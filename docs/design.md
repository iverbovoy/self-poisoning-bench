# Self-Poisoning Bench (SPB) — design v0

Working name; de-branded naming decision deferred (same policy as the
preprint). Adopted 2026-08-20 as a parallel workstream under a hard
frame; all six framing decisions below were made by Ivan explicitly,
one by one.

## Problem and claim under test

Agent long-term memory degrades **without an adversary**: the agent
reads its own past output as fact, attribution of origin ("user said"
vs "I inferred") is lost across write→consolidate→recall cycles, and
laundered content eventually enters answers and decisions as ground
truth. The benchmark measures this loss per memory-write policy.
(Originally framed as degradation *as a function of session count*;
v1 data showed the loss is complete at the first write — see
Metrics, "Retired".)

This is the empirical leg the rank-bounded-memory preprint currently
lacks, and the C0 experiment ("run 20 sessions, get a curve or a
reason to retract the hypothesis") gets its harness here.

## Prior art and the exact gap (verified against primary sources 2026-08-20)

- **TMA-NM** (arXiv:2606.24322, Louck, 23 Jun 2026): origin-bound
  authority, non-malleable IFC, machine-checked; names agent
  self-summarization as an origin-laundering channel. **Adversarial**
  threat model; guarantees cover action authorization and explicitly
  leave non-consequential answer distortion out of scope. Its lattice
  is a linear integrity scale (untrusted ⊏ agent ⊏ trusted) — rank-2
  attribution (`self.user.self`), a user-model layer, and the
  normative layer are not expressible in it. Delta paragraph queued
  for preprint v1.1 (queue order, experiment-paced — Ivan's call).
- **BeliefMem** (arXiv:2605.05583): names the adversary-free
  self-reinforcing-error problem, treats it as uncertainty about the
  world (probabilistic beliefs, noisy-OR). Does not distinguish
  memory source. Different disease, similar symptom.
- **Provenance semirings** (Green et al. 2007) + security semiring:
  the meet-over-support math is prior art — cite, never claim.
- Practice (from the prior-art scan, to re-verify in code before any
  public table): Zep has strong episode provenance but no source
  *type* and no prompt delivery of it; mem0 has tenancy metadata, not
  provenance; Letta self-edited core blocks are the canonical
  laundering pattern (agent writes into its own system prompt,
  unlabeled).

**Free niche SPB occupies**: measuring epistemic degradation of
persistent memory without an adversary — the attribution-error curve
over sessions and laundering depth. Nobody measures this (TMA-NM
measures ASR; BeliefMem measures task accuracy).

## Design decisions (all adopted 2026-08-20)

1. **Workstream frame — hard**: design doc → generator → in-house
   conditions → first full curve. NO external framework integrations
   (mem0/Zep/Letta) until the first curve exists; they are SPB v2,
   mirroring the 2.2b pattern. 2.2a remains the gate for building the
   memory model; SPB gates nothing and is gated by nothing.
2. **TMA-NM preprint delta**: joins v1.1 queue item 4 (related-work
   deltas), published experiment-paced with the rest — no rush
   release.
3. **`attribute` is built now, in SILENT mode**: behind a flag at the
   IO boundary, haiku seat, derived records with provenance (rules
   version, model) beside the pre-schema raw feed. Labels are shown
   to NO ONE (no UI, not Ivan) until comparison time — preserves 2.1
   blindness and prevents Ivan calibrating on model readings.
   Rationale for building: live rank-2 cases accumulate labeled; 2.1
   numbers become a by-product; the write point already exists
   (phase 0 put the writer where attribute belongs).
4. **Judge = full panel, majority vote** (opus-5, haiku-4.5,
   gemini-3.6-flash — same seats as D4), 2/3 verdicts.
   Inter-judge agreement is reported as a free by-product. Mandatory
   layer on top: Ivan adjudicates a random probe sample blind;
   judge–human agreement with Wilson CI goes into the paper. Judge
   validation section = the phase-2 apparatus (pooled path accuracy
   94–99% vs adjudicated keys, human 87–89%).
5. **Seed corpus = hybrid, numbers never mixed** (2.1 discipline):
   - *Primary, publishable*: synthetic multi-session feed built by
     the canon-deck method — this same artifact closes preprint v1.1
     queue item 5 (public s21-equivalent). Composition is a
     controlled knob: per session, a set ratio of user assertions /
     tool observations / agent speculations.
   - *Secondary, private*: replay of the live kinectctl raw feed —
     same metrics, second column, transferability check.
6. **Agent under test = two families**: one Claude tier + one
   non-Claude (gemini-flash), identical harness and sessions.
   Cross-family divergence is itself a result. The live kinectagent
   stack is not used for the synthetic curve; its natural place is
   the private refeed column (decide later).

## Conditions (memory-write policies, in-house)

| # | policy | writes to memory | models |
|---|---|---|---|
| C1 | verbatim-user-only | user utterances copied verbatim, nothing else | the "may not reproduce" control |
| C2 | flat notes | agent-phrased notes, explicit recall (our live notes.jsonl baseline) | current kinectagent practice |
| C3 | self-edit blocks | agent edits a persistent block injected into its own system prompt | Letta pattern; canonical laundering |
| C4 | attributed store | itemAE schema: every record carries path/ground; projection renders labels into the prompt | the defense |

C4 uses the frozen v2.3 rules via the attribute annotator; the
projection format (how labels render into the prompt) is part of the
condition and must be specified before runs — it is the point-(C)
invariant under test.

## Protocol

- k sessions replayed per (condition × agent-family); each session
  ends with the condition's consolidation step writing memory; next
  session starts from that memory plus the new session script.
- k = 20 for the first curve (C0's number); probes fire at fixed
  checkpoints (e.g. k = 1, 3, 5, 10, 15, 20).
- Probe types:
  1. **Attribution probes**: "did I tell you X, or did you conclude
     it?" — keyed to seeded records with known origin.
  2. **Twin probes** (shared with 2.2a): semantically-near pairs
     differing only in path/ground.
  3. **Decision probes** (N2-flavored): tasks where acting on
     laundered content produces a detectably different action than
     acting on labeled content.
- Seeded speculation tracers: the synthetic sessions plant agent
  speculations with unique factual content so their reappearance as
  "fact" is mechanically detectable in later answers.

## Metrics

1. **Laundering rate** — share of content-present answers that
   present agent speculation as owner-stated or observed fact, per
   condition per family, pooled over checkpoints. Judge: panel
   majority (extraction-based), human-validated (blind
   adjudication, `evals/spbench/adjudicate.py`).
2. **Coverage** and **any-error** alongside, so a policy cannot win
   by forgetting.
3. **Hedging decay** — survival of epistemic hedges across
   derivation chains. Measured, not yet written up.

**Retired 2026-08-21 — W_t (laundering depth) and the session-index
curve as headline.** v1.1 data, all cells pooled: laundering in C2/C3 is at its
maximum at k=1 and does not grow (C2 46%→26%, C3 42%→34% over
k=1..20; C4 4–6% throughout)
and a chained speculation launders as completely as its parent at
generation one. The label is destroyed by the FIRST agent rewrite;
W_t≈1 everywhere and there is no depth to measure. The claim under
test is therefore restated: **write-time attribution collapse**, not
accumulation. "No growth after k=1" is stated only at the power of
the data (one seed + replicates); the per-checkpoint table stays in
the report as evidence, not as the headline.

No metric is ever an optimization target (§10 discipline).

## Threats to validity, answered in-design

- *Judge circularity* (our schema is both defense C4 and ruler):
  panel majority + Ivan's blind spot-adjudication with reported
  agreement; judging uses rules-as-rubric, the defense uses
  attribute-at-write — different roles of the same spec, stated
  openly.
- *Synthetic realism*: private live-refeed column, same metrics,
  never mixed.
- *Single-model artifact*: two families by design.
- *Constructed-to-leak corpus*: composition ratios published with the
  generator; C1 control shows what happens when agent output is
  simply never written.

## Relation to the rest of the program

- 2.2a (does perspective indexing SELECT better than cosine) is
  untouched and remains the gate for project/consolidate/graph.
- SPB feeds preprint v1.2 (empirics + TMA-NM delta + public
  artifact). The architecture paper keeps 2.2a/2.2b.
- Ivan's C0 commitment = the first run of this harness.

## Build order (Claude-side, fits Ivan's corpus-accumulation window)

1. Session generator (canon-deck method, composition knobs) +
   tracer-seeding. Doubles as v1.1 artifact item 5.
2. Replay harness: condition runners C1–C4, checkpointing, probe
   injection.
3. Judge pipeline: panel majority over probe transcripts (reuses
   panel.py machinery), Ivan-audit sampler.
4. First curve: 2 families × 4 conditions × k=20.
5. (separate track) silent `attribute` at the kinectview IO boundary.

Everything lands in `evals/spbench/` (code + synthetic corpus) and
runs under the one-experiment-one-branch rule.

## SPB v2 — real frameworks (ADOPTED 2026-08-22)

The v1 frame ("no external framework integrations before the first
full curve") is satisfied; v2 replaces the C2/C3 proxies with real
systems behind one adapter interface (`evals/spbench/adapters.py`).
Order, cheapest/most-predictable first, each step publishable alone:

1. **mem0** (OSS): LLM fact extraction + vector store — the nearest
   real relative of C2. Hours of integration; also validates that the
   proxy methodology transfers to a real system.
2. **Letta**: real core-memory self-edit block — directly validates
   the "Letta-style proxy" claim behind C3 (defense of v1, not just a
   new column).
3. **Graphiti** (open-source Zep engine, self-hosted + Neo4j; hosted
   Zep rejected — irreproducible, data leaves the machine): the only
   one with an open outcome — episode-provenance edges MAY preserve
   attribution. Either result publishes.

**Pre-registered predictions (written 2026-08-22, BEFORE any v2
run):** mem0 launders at C2 level (~30%); Letta at C3 level (~33%);
Graphiti — no prediction, genuinely open (mechanism exists, default
prompts may not use it).

**Fairness pins:** framework-internal LLM = the same family model as
the agent under test (OpenRouter, T=0); grid 2 families (haiku,
gemini) × frameworks × 2 storylines; judge panel, rubric v1.1 and
probes identical to v1 (rescore under later rubrics alongside, as
v1.0→v1.1). Embeddings: local `multilingual-e5-small` (OpenRouter
has no embeddings endpoint) — steers retrieval only, not the
extraction that laundering measures.

**Recorded asymmetries (by design, disclosed):** (a) read path is the
framework's NATIVE retrieval (mem0: search top-10 per probe) where
C1–C5 render the whole store — the read path is part of the system
under test; (b) session records enter as chat messages with the same
in-band speaker tags as the C2/C3 transcripts (roles: owner=user,
everything else=assistant) — no information asymmetry at write time.

Cells: `runs/<family>-<framework>`; judge.py/curve.py are
cell-name-agnostic, v2 rows land in the same tables.

**Letta mechanics (2026-08-22):** official container (letta/letta
0.16.8), LLM = family model through Letta's own OpenRouter provider,
T=0 via model_settings; embeddings `letta/letta-free` (Letta's
default hosted embedder — synthetic corpus, nothing private leaves
the machine). One agent per cell with the stock persona/human blocks
and base memory tools, **as-shipped block limit (100,000 chars)** —
the real system is measured as shipped, not budget-matched to C3's
1,500; C5 already showed volume is not the active ingredient, and a
budget-matched Letta cell is a follow-up, not a prerequisite. Each
session is delivered as ONE user message carrying the tagged
transcript (C3 protocol parity; the agent's chat reply is discarded,
only its memory writes survive). Read path: core blocks + archival
search top-10 rendered as the probe's memory context — a C3-parity
read (Letta would hold the same blocks in its own context window).

**Graphiti mechanics (2026-08-22):** graphiti-core 0.29.3 on Neo4j
5.26 (container), LLM = family model via OpenAIGenericClient on
OpenRouter, T=0; local e5-small embedder and a cosine reranker in
place of the stock OpenAI reranker (needs an OpenAI key). One
`message` episode per session with "speaker: text" lines (speaker =
owner/assistant/tool/sensor — in graphiti the speaker becomes an
entity, so it is a role name, not a tag). Read path: graphiti's own
hybrid RRF search for edges + nodes rendered by its
`search_results_to_context_string` — the Zep-style FACTS (with
valid/invalid dates) + ENTITIES block — with raw EPISODES excluded:
they are the transcript itself, not memory. Observed at smoke: facts
keep the speaker as subject ("The owner requested…", "The assistant
will…") — attribution may survive structurally; no prediction.

## Language: English primary (Ivan, 2026-08-22)

The RU corpus was a validity threat the mem0 run made concrete:
framework-internal prompts are English, so a RU corpus inserts a
translation step (an extra rewrite) between source and memory, and
RU probes against EN-normalized memories make retrieval cross-lingual
(mem0 haiku coverage 49% is partly that). Decision: **English is the
base going forward; Russian stays as the released v1 record and a
language-robustness column.** Numbers across languages are never
mixed.

Mechanics: `storyline_en.py` is a 1:1 mirror of storyline A — same
tracer ids/types/origins/seed sessions; proper nouns transliterated,
not translated (Busya, Oleg, Zhyto, Morena, Lviv, Veltra), so the
pair differs in language alone; markers re-chosen as distinctive
English substrings with the same lexical-split discipline; manifest
ground truth carries over, NO re-annotation and no new human labor.
The harness prompt set (C2/C3/C5, probe system, speaker tags, C4
labels) switches with `--corpus en`; the judge templates are shared,
with the answer-language note parametrized. Cells: `en-*`. Ivan's
blind adjudication validated the judge on RU and stays RU-scoped; an
EN spot-adjudication is optional later if EN becomes the paper's
headline table.

**Pre-registered expectations (written BEFORE any en-* run):**
(1) direction stays b->a; (2) C2/C4 laundering on EN ≈ RU within CIs
— the collapse is structural, not linguistic; (3) mem0 coverage
RISES on EN (the cross-lingual retrieval penalty disappears),
laundering rate stays in the same band; (4) C4/C5 stay at the bottom
on EN as on RU.
