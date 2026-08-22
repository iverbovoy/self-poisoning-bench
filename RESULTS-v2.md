# SPB v2 results — real frameworks

Dated addenda keep the numbers as computed at the time; the closing
table and the robustness section at the end are current (post judge
fix, 2026-08-22).

v2 replaces the C2/C3 *proxies* with real memory systems behind one
adapter interface (`adapters.py`; design: SPB v2 section of
`../../itemae/selfpoison-bench-design.md`). Same corpus (storyline A),
probes, judge panel and rubric v1.1 as v1; cells land in the same
`runs/summary-v11.csv`. Predictions were pre-registered in the design
doc BEFORE any run: mem0 ≈ C2 (~30%), Letta ≈ C3 (~33%), Graphiti
open.

## mem0 (2026-08-22) — mem0ai 2.0.18, OSS

Pinned: internal LLM = the family model via OpenRouter, T=0;
embedder `intfloat/multilingual-e5-small` (local); qdrant on-disk per
cell; native read path = `search(probe, top_k=10)` per probe (v1
policies render the whole store — the read path is part of the system
under test). Sessions enter as chat messages with the same in-band
speaker tags C2/C3 saw.

| cell (A, v1.1 rubric) | laundered / present | any-error | coverage |
|---|---|---|---|
| haiku-mem0 | 17.7% [11,28] (14/79) | 27.8% | 49% |
| gemini-mem0 | 27.4% [20,37] (29/106) | 46.2% | 65% |
| **pooled mem0** | **23.2% [18,30]** (43/185) | 38.4% | 57% |
| pooled C2 (v1, proxy) | 30.3% [27,34] | 50.0% | 66% |
| pooled C4 (v1) | 4.9% [4,7] | 13.4% | 87% |
| pooled C5 (v1) | 2.6% [1,5] | 5.5% | 66% |

**Prediction check.** Confirmed in band: mem0 launders at the level
of the unattributed-notes proxies (within the per-family C2 range
16.7–36.6%), ~5x pooled C4 and ~9x C5; CIs vs C4/C5 disjoint, per
family and pooled. Not confirmed in per-family ordering: haiku-mem0
(17.7%) is BELOW haiku-c2 (36.6%) — the gpt-c2 pattern (sparse
memory, 49% coverage, still misattributes a fifth of what it keeps);
gemini-mem0 (27.4%) is ABOVE gemini-c2 (16.7%).

**Findings.**

1. **Direction is b→a, as everywhere.** All 14 haiku and 28/29 gemini
   laundered verdicts present agent speculation as owner-stated.
   Write-time collapse replicates on a real system: the k=1
   checkpoint is already at the pooled level, no growth with k.
2. **A second channel: c→a.** mem0's user-centric extraction prompt
   normalizes records to English "User has/prefers/did ..." facts.
   Beyond laundering speculation, it rewrites SENSOR/TOOL events as
   owner facts (9 of 20 gemini `wrong_source` are c→a) and strips
   the in-band speaker tags it was given. The origin label is
   destroyed by the framework's own extraction step — before any
   consolidation pressure exists.
3. **Coverage cost without a safety gain.** mem0's extraction is the
   sparsest writer measured so far (haiku 49%) yet still launders
   what it keeps — forgetting is not a defense (v1 finding 2,
   replicated on a real system).

**Caveats.** One framework so far; single seed at T=0 (internal LLM
and probes; mem0's pipeline itself is not seeded by us); retrieval
read path makes `absent` partly a retrieval property, so coverage is
not directly comparable to whole-store policies (recorded in-design);
judge family overlap as in v1 (mitigations unchanged: gemini seat,
cross-family consistency, human adjudication of the v1 protocol).

## Addendum 2026-08-22 — English primary corpus + Letta

English is the base corpus from here (design doc, "Language"):
`corpus-en` is a 1:1 mirror of storyline A (same records, origins,
tracers; proper nouns transliterated), harness prompts/tags switch
with `--corpus en`, cells `en-*`. Full EN grid: C1–C5 × {haiku,
gemini} + mem0 + Letta. `langtable.py` prints the table below.

### Language effect (pooled over haiku+gemini, rubric v1.1)

| policy | RU laundered | EN laundered | RU cov | EN cov |
|---|---|---|---|---|
| C1 verbatim | 4.3% [2,9] | 2.3% [1,6] | 43% | 41% |
| C2 flat notes | 26.5% [21,33] | 24.5% [19,30] | 70% | 71% |
| C3 self-edit | 30.0% [24,36] | 31.7% [26,38] | 71% | 70% |
| C4 attributed | 2.5% [1,5] | 3.1% [2,6] | 85% | 90% |
| C5 attr+compressed | 2.2% [1,5] | 5.8% [3,9] | 69% | 75% |
| mem0 | 23.2% [18,30] | 28.3% [22,35] | 57% | 58% |

**Pre-registered expectations, checked.** (1) Direction b→a: holds
on EN (see per-cell verdicts). (2) C2/C4 EN ≈ RU within CIs: **yes**
— every policy's EN rate lies inside its RU interval; the collapse
is structural, not linguistic. Per-family rates do move with
language (haiku-c2 36.6→20.9, gemini-c2 16.7→28.4) — family-level
numbers are language-sensitive, policy-level conclusions are not.
(3) mem0 coverage rises on EN: **no** — 57→58% pooled (haiku 49→56,
gemini 65→60). The cross-lingual-retrieval explanation for mem0's low
coverage is refuted; mem0 simply extracts sparsely, in either
language. (4) C4/C5 stay at the bottom: yes (3.1% / 5.8% vs 24–32%).

### Letta (EN, letta/letta 0.16.8 container, as-shipped)

| cell | laundered / present | any-error | coverage | human block @s20 |
|---|---|---|---|---|
| en-haiku-letta | 20.5% [13,30] (17/83) | 22.9% | 51% | 1,508 chars |
| en-gemini-letta | 29.1% [21,38] (32/110) | 57.3% | 68% | 1,104 chars |
| **pooled Letta** | **25.4% [20,32]** (49/193) | 42.5% | 60% | |
| EN C3 proxy | 31.7% [26,38] | 51.5% | 70% | ≤1,500 (budget) |
| EN C4 | 3.1% [2,6] | 9.0% | 90% | |

**Prediction check: confirmed in band.** Letta launders at the C3
level (CIs overlap; point estimate 6 points lower, coverage 10 points
lower — it writes less). The C3 proxy is validated: real Letta, given
a 100,000-char block limit and stock tools, **self-converged to a
1.1–1.5K-char human block** — the proxy's 1,500-char budget was not an
artificial constraint but where the self-edit policy lands on its
own. Archival memory was never used (0 passages in both cells).
Speculations are stored as flat profile facts ("Prefers calls
scheduled for the afternoon", "Prefers curtains drawn") — the
origin is gone at the first write, as in every unlabeled policy.

### Three real systems vs the labeled store (EN, pooled)

mem0 28.3% · Letta 25.4% · C3 proxy 31.7% · C2 proxy 24.5% — one
band, 24–32%. C4 3.1% [2,6], C5 5.8% [3,9]: 4–9x lower, CIs disjoint
from every unlabeled row. The proxies were faithful; the real
frameworks do not do better.

**Caveats.** Single seed (T=0); the gemini judge seat returns
malformed JSON on the longest open-list probe (p087, and p059 in two
cells) in 8 EN cells — those items carry a 2-judge majority, 3–5
`no_majority` per cell are excluded as before; Letta's "one
transcript message per session" is the C3-parity protocol, not
Letta's turn-by-turn deployment shape (a turn-by-turn replay is a
follow-up); RU rows for Letta not run (EN is primary now).

## Addendum 2026-08-22 — Graphiti (EN, graphiti-core 0.29.3 + Neo4j 5.26)

The one framework with a structural provenance mechanism: speakers
become graph entities, edges carry facts with valid/invalid dates and
episode references. Read path = graphiti's own hybrid search rendered
as its Zep-style FACTS/ENTITIES block (raw episodes excluded). No
prediction was registered.

| cell | laundered / present | any-error | coverage | graph @s20 |
|---|---|---|---|---|
| en-haiku-graphiti | 23.0% [16,32] (23/100) | 28.0% | 62% | 32 edges / 19 nodes |
| en-gemini-graphiti | 24.3% [17,33] (25/103) | 26.2% | 64% | |
| **pooled Graphiti** | **23.6% [18,30]** (48/203) | 27.1% | 63% | |

**Outcome: the structure does not save it.** Laundering sits in the
same band as every other unlabeled system. What the graph does buy
is the lowest any-error among them (27% vs 34–52%): with the speaker
as an entity, a/c confusions mostly disappear (`wrong_source` 2–4
per cell). What it does not buy is b→a: a speculation extracted as a
fact about the owner becomes "the owner's preferred work
environment" regardless of who said it. Two graph-specific channels:
(1) **b→c** — 5 (haiku) and 4 (gemini) speculations were attributed
to the SENSOR, e.g. "sensor observes that the cat wakes owner around
six": the entity *mentioned* in the speculation becomes the fact's
subject, so the graph assigns provenance to whoever is named, not
to who spoke; (2) the superseded-deadline decision probe (t17) is
laundered in BOTH cells — the temporal graph let the invalidated
12th resurface (n=1 per cell; a pointer, not a rate). Extraction is
sparse (32 edges for 175 records), coverage 63%.

### SPB v2 closing table (EN, storyline A, pooled haiku+gemini, rubric v1.1)

Numbers after the judge fix of 2026-08-22 (gemini reasoning cap; every
probe now carries a full 3-judge panel).

| system | laundered / present | any-error | coverage |
|---|---|---|---|
| C1 verbatim | 2.3% [1,6] | 6.8% | 41% |
| C2 flat-notes proxy | 25.3% [20,31] | 36.2% | 71% |
| C3 self-edit proxy | 32.7% [27,39] | 53.1% | 70% |
| mem0 2.0.18 | 29.0% [23,36] | 40.3% | 57% |
| Letta 0.16.8 | 26.6% [21,33] | 44.3% | 59% |
| Graphiti 0.29.3 | 24.4% [19,31] | 28.4% | 62% |
| **C4 attributed store** | **3.1% [2,6]** | 9.4% | **89%** |
| **C5 attributed + compressed** | **6.2% [4,10]** | 12.9% | 74% |

Five unlabeled memories — two proxies, three real frameworks spanning
notes, self-edit blocks and a temporal knowledge graph — land in one
band, 24.4–32.7%; the labeled store is 4–9x below, CIs disjoint from
every row above it, with the highest coverage. The pre-registered
predictions for mem0 and Letta held in band; Graphiti, left open,
joined the band. No consolidation architecture among those tested
preserves origin without an explicit per-record label.

### Robustness (2026-08-22, later) — storyline B on EN, seed replicates, judge fix

**Judge fix.** gemini-3.6-flash is a reasoning model: on the 26-item
open-list probe its reasoning consumed 3,840 of 4,000 completion
tokens and the JSON was truncated (10 EN probes judged by two seats).
`reasoning.max_tokens` 2,000 / `max_tokens` 8,000 for google models
(the deepseek recipe); the gaps were filled, every probe now has the
full panel; rates moved by at most 1.3 points.

**Storyline B on EN (`corpus-b-en`, 1:1 mirror of B: chain,
correction, third-party report, rebuke, never-seeded topics), pooled
haiku+gemini:**

| system | B-RU (v1) | B-EN laundered | any-error | coverage |
|---|---|---|---|---|
| C1 | 2.9% [1,7] | 3.3% [2,7] | 12.2% | 53% |
| C2 | 30.4% [25,36] | 29.2% [24,35] | 45.5% | 77% |
| C3 | 31.1% [26,37] | 23.7% [19,29] | 44.4% | 78% |
| mem0 | — | 27.3% [22,33] | 41.2% | 70% |
| Letta | — | 31.7% [26,38] | 43.5% | 72% |
| Graphiti | — | 29.4% [24,35] | 39.4% | 82% |
| **C4** | 8.7% [6,12] | **5.2% [3,8]** | 13.6% | 90% |
| **C5** | — | **11.0% [8,15]** | 22.8% | 80% |

The band replicates on the second storyline (23.7–31.7%) and on the
real frameworks; C4/C5 stay below it with disjoint CIs. C5 is higher
on B than on A (11.0 vs 6.2): storyline B's owner *confirms* several
speculations ("there is that", "good guess"), and the rubric does not
yet credit owner confirmation as a legitimate co-source (v1 known
limitation; rubric v1.2 queue) — the compressed store, which merges
lines, pays for it most. Language effect on B: every EN rate inside
its RU interval except C3 (31.1→23.7, intervals touching).

**Seed replicates, frameworks (T=0.7 for the framework-internal LLM
and the probes), EN storyline A:**

| system | T=0 | T=0.7 |
|---|---|---|
| mem0 | 29.0% [23,36] | 30.7% [25,38] |
| Letta | 26.6% [21,33] | 25.3% [19,32] |
| Graphiti | 24.4% [19,31] | 22.8% [18,29] |

Pooled rates replicate within 2 points for all three; per-family
swings reach 7 points (letta-haiku 20.5→27.4, letta-gemini 31.2→23.8)
with overlapping intervals. Cost of the 22 robustness cells incl.
judging: ≈$15.

**Caveats (v2, cumulative).** Single human adjudicator
on the RU protocol only (an EN spot-adjudication is queued); one
transcript = one episode/message for all frameworks (C3-parity
protocol, not turn-by-turn deployment — Letta turn-by-turn replay
queued); frameworks measured as shipped with local embedders where the
stock one needs a key; two agent families on EN (four on RU).

## Next

Preprint v1.2 takes the closing table and the robustness addendum.
Queued: EN spot-adjudication (Ivan); rubric v1.2 (owner confirmation
as co-source), rescored alongside; Letta turn-by-turn replay.
