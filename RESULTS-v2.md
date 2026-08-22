# SPB v2 results — real frameworks (in progress)

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

## Next

Letta (validates the C3 proxy directly), then Graphiti (open
outcome). Storyline B for framework cells after both land.
