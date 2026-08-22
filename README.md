# Self-Poisoning Bench (SPB) v1

Does an agent's long-term memory lose track of *where* a fact came
from — "the owner told me" vs "I guessed" — without any adversary,
just by the agent rewriting its own notes? SPB measures this per
memory-write policy on a synthetic 20-session feed with seeded
tracers of known origin.

Design: `../../itemae/selfpoison-bench-design.md`. Results:
`RESULTS-v1.md` (headline + addenda: rubric v1.1, C5 control, cold
reproduction, seed replicates, blind human adjudication).
`RESULTS-v0.md` is the pilot (superseded, kept for the record).
`RESULTS-v2.md` — real frameworks (mem0, then Letta/Graphiti) behind
the adapter interface (`adapters.py`); those cells need the project
venv (`pip install mem0ai sentence-transformers qdrant-client` +
CPU torch), not plain python3.

## Headline (rubric v1.1, 24 cells + C5, 4 agent families)

| policy | what it writes | laundered / present | coverage |
|---|---|---|---|
| C1 verbatim-user | owner utterances verbatim, nothing else | 3.0% [2,5] | 43% |
| C2 flat notes | agent-phrased notes | **30.3% [27,34]** | 66% |
| C3 self-edit block | Letta-style block in its own system prompt | **33.4% [30,37]** | 71% |
| C4 attributed store | every record labeled with origin (itemAE rules v2.3) | **4.9% [4,7]** | 87% |
| C5 attributed + compressed | C4 labels, compressed by the family model to C3's 1500-char budget | **2.6% [1,5]** | 66% |

"Laundered" = agent speculation presented as owner-stated or
observed fact. The loss is complete at the first rewrite (k=1) and
does not grow with sessions; C5 shows the label, not the memory
volume, is the active ingredient. Seed replicates reproduce within
2 points; a blind human adjudication agrees with the panel on the
laundered/not call 85% [72,93] (C4: 100%) and disagrees only in the
direction of *more* laundering than the panel counts.

## Layout

```
storyline.py, storyline_b.py   the two scripted 20-session storylines (A: designer, B: teacher)
gen_corpus.py                  deterministic generator -> corpus/, corpus-b/ (sessions, manifest, tracers, probes)
harness.py                     replay: consolidation policies C1-C5, checkpoint probes -> runs/<cell>/
judge.py                       panel judge (extraction-based, majority of 3) -> judgments, verdicts
curve.py                       pooled tables, per-checkpoint curve -> runs/summary-<rubric>.csv
replicates.py                  T=0 vs T=0.7 seed-replicate comparison
adjudicate.py                  blind human adjudication: --sample / --run / --score
adjudication/                  human.csv (Ivan's blind extractions), key.csv, scored.csv
runs/<family>-<cond>/          memory-sNN.json snapshots, answers.csv, judgments*.csv, verdicts*.csv
runs/b-*                       storyline B cells; runs/r2-*  seed replicates (T=0.7)
reproduce.sh                   free-tier reproduction: corpora, verdicts, tables must regenerate identically
```

Cell naming: `[r2-][b-]<family>-c<1-5>`. `deepseek-c5` is partial
(4 verdicts; the reasoning model exhausts its budget on the
compression prompt) and is excluded from every table.

## Pinned configuration (all runs 2026-08-20 .. 2026-08-22, via OpenRouter)

| role | model id |
|---|---|
| agent families | `anthropic/claude-haiku-4.5`, `google/gemini-3.6-flash`, `openai/gpt-5.6-terra`, `deepseek/deepseek-v4-flash` |
| C4/C5 annotator (fixed seat) | `anthropic/claude-haiku-4.5`, rules `itemae/annotation-rules.md` v2.3, temperature 0 |
| judge panel | `anthropic/claude-opus-5`, `anthropic/claude-haiku-4.5`, `google/gemini-3.6-flash`; majority 2/3 |

Temperature 0 for all main cells; `r2-*` replicates at 0.7 for
family calls (annotator stays at 0). `max_tokens` 4000; deepseek
gets `reasoning.max_tokens` 1500 / `max_tokens` 8000. Checkpoints
k = 1, 3, 5, 10, 15, 20. C3/C5 block budget 1500 chars. Corpus
clock starts 2026-09-01. Generator has no randomness; the
adjudication sample seed is 20260821.

Model ids are OpenRouter aliases — they may resolve to newer
snapshots later; the stored `answers.csv` and `judgments*.csv` are
the record of what the models said on those dates.

## Reproduce

Free (no API calls) — everything downstream of the stored model
outputs must regenerate byte-identically:

```
./reproduce.sh
```

Paid — rerun a cell from scratch (≈$0.3 agent + ≈$0.8 judging per
cell, 2026-08 prices; needs `OPENROUTER_API_KEY` in `../../agent.env`):

```
python3 harness.py --family haiku --condition c2            # -> runs/haiku-c2/
python3 judge.py --cells haiku-c2 --rubric v11              # -> verdicts-v11.csv
python3 harness.py --family haiku --condition c2 --tag r3- --temperature 0.7   # another replicate
python3 replicates.py
```

Both scripts are resumable (per-session snapshots; per (probe, judge)
judgments).

## Judge and rubric

Judges do not grade — they *extract*: is the record's substance
asserted in the answer, and which sources does the answer claim
(a = owner said, b = agent inferred, c = instrument showed). The
category (`correct / laundered / demoted / wrong_source / absent /
confabulated`) is computed in code from extraction vs ground truth
(`judge.category_v11`). Rubric v1.0 (`verdicts.csv`) used a single
claimed source; v1.1 (`verdicts-v11.csv`, reported) uses source
sets and per-tracer legitimate-source sets (`TOPIC_SOURCES`).
Both are stored; RESULTS reports both.

The human adjudication runs the same extraction task blind to
cell and panel output; agreement is computed on categories.

## Known limitations (reported, not fixed in v1)

- Synthetic corpus, two storylines, authored by us; C3 is a
  Letta-style proxy, not Letta. Real mem0/Zep/Letta are SPB v2.
- Storyline B owner *confirmations* of agent speculations are not
  modeled as legitimate co-sources; C4 on B shows 12–14 laundered
  under v1.1 partly for this reason (rubric v1.2 queue).
- The presence rubric ("retold with loss" vs "adjacent fact") is
  where the human and the panel diverge; the panel is the stricter
  reader, so reported error rates are lower bounds.
- Judge panel shares a family with two agents; mitigations: gemini
  seat, extraction-based prompts, human adjudication, cross-family
  consistency.
- One human adjudicator, 100 items, first ~20 discussed during
  calibration (disclosed in RESULTS).
