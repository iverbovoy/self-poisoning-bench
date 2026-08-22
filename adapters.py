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


ADAPTERS = {"mem0": Mem0Adapter}
