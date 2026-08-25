#!/usr/bin/env python3
"""SPB v2 adapters: real memory frameworks behind the harness interface.

Each adapter is one memory-write policy implemented by an EXTERNAL
framework (mem0, Letta, Graphiti) instead of the scripted C1-C5
policies. The harness drives them through the same corpus, probes,
judge and tables, so v2 cells land in the same summary as v1 cells.

Contract (harness.run_cell drives it):
  * __init__(cell_dir, family_model, key, temperature): open or create
    the framework's persistent store under <cell_dir>/store/. A killed
    run resumes from the store; sessions already snapshotted are not
    re-written.
  * write_session(session_no, records): feed one session through the
    framework's own write/consolidation path.
  * snapshot() -> json-serializable dump of the store, written to
    memory-sNN.json. An AUDIT artifact — recovery is the store itself.
  * context(probe_text) -> str: the framework's NATIVE read path
    (retrieval for mem0/Graphiti, core blocks for Letta) rendered as
    the probe-time memory context. Retrieval reads are per-probe where
    C1-C5 render the whole store once — that asymmetry is part of the
    system under test, recorded in the design doc, not hidden.

Fairness pins (design doc, v2 section): the framework's INTERNAL LLM
is the same family model as the agent under test, via OpenRouter,
temperature 0. Embeddings are a local multilingual model (OpenRouter
serves no embeddings endpoint); they steer retrieval only, not the
LLM extraction that laundering measures.

Framework libraries are imported lazily inside each adapter, so the
base harness runs without any of them installed.
"""
import json
import os

OPENROUTER_URL = "https://openrouter.ai/api/v1"
EMBED_MODEL = "intfloat/multilingual-e5-small"  # local; corpus is Russian
EMBED_DIMS = 384
SEARCH_LIMIT = 10  # mem0 native read: top-k per probe

# Same in-band speaker tags as harness.transcript(); role carries the
# chat position, the tag carries the speaker — no information asymmetry
# vs what C2/C3 saw in their transcripts.
KIND_TAGS = {
    "ru": {"user_msg": "владелец", "agent_msg": "я", "agent_proactive": "я",
           "tool_call": "инструмент", "sensor": "сенсор"},
    "en": {"user_msg": "owner", "agent_msg": "me", "agent_proactive": "me",
           "tool_call": "tool", "sensor": "sensor"},
}
EMPTY = {"ru": "(пусто)", "en": "(empty)"}
KIND_ROLE = {"user_msg": "user", "agent_msg": "assistant",
             "agent_proactive": "assistant", "tool_call": "assistant",
             "sensor": "assistant"}


class Mem0Adapter:
    """mem0 OSS: LLM fact extraction + add/update/delete against a
    vector store. The nearest real-world relative of C2 (flat notes)."""

    def __init__(self, cell_dir, family_model, key, temperature=0.0,
                 lang="ru"):
        self.tags = KIND_TAGS[lang]
        self.empty = EMPTY[lang]
        os.environ.setdefault("MEM0_TELEMETRY", "False")
        from mem0 import Memory  # lazy: pip install mem0ai
        store = os.path.join(cell_dir, "store")
        os.makedirs(store, exist_ok=True)
        config = {
            "llm": {"provider": "openai", "config": {
                "model": family_model,
                "temperature": temperature,
                "max_tokens": 4000,
                "openai_base_url": OPENROUTER_URL,
                "api_key": key}},
            "embedder": {"provider": "huggingface", "config": {
                "model": EMBED_MODEL,
                "embedding_dims": EMBED_DIMS}},
            "vector_store": {"provider": "qdrant", "config": {
                "path": os.path.join(store, "qdrant"),
                "collection_name": "spb",
                "embedding_model_dims": EMBED_DIMS,
                "on_disk": True}},
        }
        self.mem = Memory.from_config(config)

    def write_session(self, session_no, records):
        msgs = [{"role": KIND_ROLE[r["kind"]],
                 "content": f"[{self.tags[r['kind']]}] {r['payload']['text']}"}
                for r in records]
        self.mem.add(msgs, user_id="owner")

    def snapshot(self):
        out = self.mem.get_all(filters={"user_id": "owner"}, top_k=10000)
        items = out.get("results", out) if isinstance(out, dict) else out
        return sorted((
            {"id": m.get("id"), "memory": m.get("memory"),
             "created_at": m.get("created_at"),
             "updated_at": m.get("updated_at")}
            for m in items), key=lambda m: (m["created_at"] or "", m["id"]))

    def context(self, probe_text):
        out = self.mem.search(probe_text, filters={"user_id": "owner"},
                              top_k=SEARCH_LIMIT)
        items = out.get("results", out) if isinstance(out, dict) else out
        lines = [f"- {m['memory']}" for m in items if m.get("memory")]
        return "\n".join(lines) if lines else self.empty


LETTA_URL = os.environ.get("LETTA_URL", "http://localhost:8283")
LETTA_EMBEDDING = "letta/letta-free"  # Letta's own default embedder
LETTA_MAX_STEPS = 12

PERSONA = {
    "ru": "Ты — домашний агент-ассистент владельца. Ты помнишь владельца между сессиями.",
    "en": "You are the owner's home assistant agent. You remember the owner across sessions.",
}
SESSION_MSG = {
    "ru": "Стенограмма только что закончившейся сессии с владельцем:\n{transcript}",
    "en": "Transcript of the session with the owner that just ended:\n{transcript}",
}
HEAD = {"ru": ("ОСНОВНАЯ ПАМЯТЬ", "АРХИВ (найдено по запросу)"),
        "en": ("CORE MEMORY", "ARCHIVAL (retrieved for this question)")}


class LettaAdapter:
    """Letta (ex-MemGPT): the agent self-edits its core memory blocks
    through tools while processing the session; archival memory via
    its own passages store. The real system behind the C3 proxy.

    Server: official docker image (letta/letta), Postgres inside;
    LLM = the family model through Letta's OpenRouter provider. Each
    session is delivered as ONE user message carrying the tagged
    transcript (C3 protocol parity); the agent's reply is discarded,
    only what it wrote to memory survives. Read path for probes:
    core blocks + archival search top-10 rendered as the memory
    context (C3-parity read; Letta would have the same blocks in its
    own context window)."""

    def __init__(self, cell_dir, family_model, key, temperature=0.0,
                 lang="ru"):
        from letta_client import Letta  # lazy: pip install letta-client
        self.lang = lang
        self.tags = KIND_TAGS[lang]
        self.empty = EMPTY[lang]
        self.c = Letta(base_url=LETTA_URL)
        store = os.path.join(cell_dir, "store")
        os.makedirs(store, exist_ok=True)
        self.meta_fp = os.path.join(store, "letta-agent.json")
        if os.path.exists(self.meta_fp):
            with open(self.meta_fp, encoding="utf-8") as f:
                self.agent_id = json.load(f)["agent_id"]
            return
        agent = self.c.agents.create(
            name=f"spb-{os.path.basename(cell_dir)}",
            model=f"openrouter/{family_model}",
            embedding=LETTA_EMBEDDING,
            memory_blocks=[{"label": "persona", "value": PERSONA[lang]},
                           {"label": "human", "value": ""}],
            model_settings={"provider_type": "openrouter",
                            "temperature": temperature},
            include_base_tools=True)
        self.agent_id = agent.id
        with open(self.meta_fp, "w", encoding="utf-8") as f:
            json.dump({"agent_id": agent.id, "model": f"openrouter/{family_model}",
                       "embedding": LETTA_EMBEDDING}, f)

    def write_session(self, session_no, records):
        transcript = "\n".join(f"[{self.tags[r['kind']]}] {r['payload']['text']}"
                               for r in records)
        self.c.agents.messages.create(
            agent_id=self.agent_id,
            input=SESSION_MSG[self.lang].format(transcript=transcript),
            max_steps=LETTA_MAX_STEPS)

    def _blocks(self):
        return [(b.label, b.value or "", getattr(b, "limit", None))
                for b in self.c.agents.blocks.list(agent_id=self.agent_id)]

    def _passages(self, query=None, limit=1000):
        kw = {"agent_id": self.agent_id, "limit": limit}
        if query:
            kw["search"] = query
        return [p.text for p in self.c.agents.passages.list(**kw) if p.text]

    def snapshot(self):
        return {"blocks": [{"label": lab, "value": v, "limit": lim}
                           for lab, v, lim in self._blocks()],
                "archival": self._passages()}

    def context(self, probe_text):
        core, arch = HEAD[self.lang]
        parts = [f"{core}:"]
        for label, value, _ in self._blocks():
            # persona is scaffolding unless the agent wrote into it
            if value.strip() and not (label == "persona"
                                      and value.strip() == PERSONA[self.lang]):
                parts.append(value.strip())
        found = self._passages(query=probe_text, limit=SEARCH_LIMIT)
        if found:
            parts.append(f"\n{arch}:")
            parts += [f"- {t}" for t in found]
        body = "\n".join(parts)
        return body if len(parts) > 1 else self.empty


TURN_PREFIX = {"ru": "[с прошлого хода]", "en": "[since your last turn]"}
TURN_END = {"ru": "[сессия закончилась]", "en": "[the session has ended]"}


class LettaTurnAdapter(LettaAdapter):
    """Letta, turn-by-turn: every OWNER utterance is a live user turn —
    Letta answers it itself and edits memory as it goes — instead of
    one transcript per session. Scripted agent lines, sensor and tool
    events are delivered in-band as a bracketed event preamble of the
    next owner turn (the API offers no clean way to append an
    assistant utterance to history: an assistant-role input is
    treated as a prefill and continued; a system-role event makes the
    model return empty content). Letta's own replies are discarded —
    the corpus carries the scripted ones. Robustness column for the
    per-session protocol, not a replacement."""

    def _send(self, text):
        from letta_client import InternalServerError
        for attempt in range(3):
            try:
                self.c.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": text}],
                    max_steps=LETTA_MAX_STEPS)
                return
            except InternalServerError as e:
                if attempt == 2:
                    print(f"  letta turn dropped after 3 errors: {str(e)[:80]}")

    def write_session(self, session_no, records):
        pending = []
        for r in records:
            line = f"[{self.tags[r['kind']]}] {r['payload']['text']}"
            if r["kind"] == "user_msg":
                pre = (TURN_PREFIX[self.lang] + "\n" + "\n".join(pending) + "\n\n"
                       if pending else "")
                self._send(pre + r["payload"]["text"])
                pending = []
            else:
                pending.append(line)
        if pending:
            self._send(TURN_END[self.lang] + "\n" + "\n".join(pending))


NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "spbgraphiti")
# graphiti "message" episodes are "speaker: text" lines; the speaker name
# becomes an entity, so it is the natural-language role, not a tag.
SPEAKER = {
    "ru": {"user_msg": "владелец", "agent_msg": "ассистент",
           "agent_proactive": "ассистент", "tool_call": "инструмент",
           "sensor": "сенсор"},
    "en": {"user_msg": "owner", "agent_msg": "assistant",
           "agent_proactive": "assistant", "tool_call": "tool",
           "sensor": "sensor"},
}


def _local_clients():
    """graphiti EmbedderClient + CrossEncoderClient over the same local
    e5-small as mem0 (the stock reranker needs an OpenAI key). Subclassed
    lazily: graphiti validates isinstance at construction."""
    from graphiti_core.embedder.client import EmbedderClient
    from graphiti_core.cross_encoder.client import CrossEncoderClient
    from sentence_transformers import SentenceTransformer

    class LocalEmbedder(EmbedderClient):
        def __init__(self):
            self.model = SentenceTransformer(EMBED_MODEL)

        async def create(self, input_data):
            text = input_data if isinstance(input_data, str) else input_data[0]
            return self.model.encode(text, normalize_embeddings=True).tolist()

        async def create_batch(self, input_data_list):
            return self.model.encode(list(input_data_list),
                                     normalize_embeddings=True).tolist()

    class LocalReranker(CrossEncoderClient):
        def __init__(self, embedder):
            self.embedder = embedder

        async def rank(self, query, passages):
            if not passages:
                return []
            q = self.embedder.model.encode(query, normalize_embeddings=True)
            ps = self.embedder.model.encode(list(passages), normalize_embeddings=True)
            return sorted(zip(passages, (ps @ q).tolist()), key=lambda x: -x[1])

    emb = LocalEmbedder()
    return emb, LocalReranker(emb)


class GraphitiAdapter:
    """Graphiti (open-source engine of Zep): temporal knowledge graph —
    LLM entity/edge extraction per episode, edge facts with
    valid/invalid dates and episode provenance, Neo4j store.

    LLM = family model via OpenAIGenericClient on OpenRouter, T=0;
    local e5-small embedder + cosine reranker. One episode per session
    (EpisodeType.message, "speaker: text" lines). Read path: Graphiti's
    own hybrid search (RRF) for edges + nodes, rendered by its
    search_results_to_context_string — the Zep-style FACTS/ENTITIES
    block — with raw EPISODES excluded (they are the transcript, not
    memory)."""

    def __init__(self, cell_dir, family_model, key, temperature=0.0,
                 lang="ru"):
        import asyncio
        from graphiti_core import Graphiti
        from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
        from graphiti_core.llm_client.config import LLMConfig
        self.lang = lang
        self.empty = EMPTY[lang]
        # one loop for the adapter's lifetime: the neo4j async driver
        # binds to the loop it first runs in
        self.loop = asyncio.new_event_loop()
        self.run = self.loop.run_until_complete
        self.group = os.path.basename(os.path.normpath(cell_dir))
        store = os.path.join(cell_dir, "store")
        os.makedirs(store, exist_ok=True)
        with open(os.path.join(store, "graphiti.json"), "w", encoding="utf-8") as f:
            json.dump({"group_id": self.group, "model": family_model,
                       "neo4j": NEO4J_URI, "embedder": EMBED_MODEL}, f)
        llm = OpenAIGenericClient(
            config=LLMConfig(api_key=key, model=family_model,
                             small_model=family_model, base_url=OPENROUTER_URL,
                             temperature=temperature))
        self.embedder, reranker = _local_clients()
        self.g = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASS, llm_client=llm,
                          embedder=self.embedder, cross_encoder=reranker)
        self.run(self.g.build_indices_and_constraints())

    def write_session(self, session_no, records):
        from datetime import datetime, timezone
        from graphiti_core.nodes import EpisodeType
        sp = SPEAKER[self.lang]
        body = "\n".join(f"{sp[r['kind']]}: {r['payload']['text']}" for r in records)
        t0 = datetime.fromisoformat(records[0]["t"]).replace(tzinfo=timezone.utc)
        self.run(self.g.add_episode(
            name=f"s{session_no:02d}", episode_body=body,
            source=EpisodeType.message,
            source_description="home assistant session transcript",
            reference_time=t0, group_id=self.group))

    def snapshot(self):
        async def q():
            edges, _, _ = await self.g.driver.execute_query(
                "MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity) WHERE r.group_id = $g "
                "RETURN a.name AS a, b.name AS b, r.name AS rel, r.fact AS fact, "
                "toString(r.valid_at) AS valid_at, toString(r.invalid_at) AS invalid_at, "
                "toString(r.expired_at) AS expired_at, r.episodes AS episodes "
                "ORDER BY r.created_at", g=self.group)
            nodes, _, _ = await self.g.driver.execute_query(
                "MATCH (n:Entity) WHERE n.group_id = $g RETURN n.name AS name, "
                "n.summary AS summary ORDER BY n.created_at", g=self.group)
            return ([dict(e) for e in edges], [dict(n) for n in nodes])
        edges, nodes = self.run(q())
        return {"edges": edges, "nodes": nodes}

    def context(self, probe_text):
        from graphiti_core.search.search_config_recipes import COMBINED_HYBRID_SEARCH_RRF
        from graphiti_core.search.search_helpers import search_results_to_context_string
        cfg = COMBINED_HYBRID_SEARCH_RRF.model_copy(deep=True)
        cfg.episode_config = None
        cfg.community_config = None
        cfg.limit = SEARCH_LIMIT
        res = self.run(self.g.search_(probe_text, config=cfg,
                                      group_ids=[self.group]))
        if not res.edges and not res.nodes:
            return self.empty
        res.episodes, res.communities = [], []
        return search_results_to_context_string(res)


ADAPTERS = {"mem0": Mem0Adapter, "letta": LettaAdapter,
            "letta-tbt": LettaTurnAdapter, "graphiti": GraphitiAdapter}
