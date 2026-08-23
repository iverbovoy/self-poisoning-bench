# Self-Poisoning Bench (SPB)

Does an agent's long-term memory keep track of *where* a fact came from —
"the owner told me" vs "I guessed" vs "a sensor reported it"? SPB measures
this per memory-write policy, first **without any adversary** (the agent
just rewriting its own notes), then **with one** (MINJA memory injection
through SuperRed). It is the artifact of

> I. Verbovoy. *Rank-Bounded Agent Memory: A Storage-Level, By-Design
> Defense Against Memory-Poisoning Attacks.* v1.2, 2026.
> Zenodo concept DOI 10.5281/zenodo.21994003 (Sections 6–7).

Everything downstream of the stored model outputs regenerates
byte-identically without API calls (`./reproduce.sh`).

## What is measured

A scripted 20-session feed of one synthetic owner and a home-assistant
agent. 26 *tracer* records per storyline carry a known origin — owner-stated
(a), agent speculation (b), instrument/sensor (c). At checkpoints the agent
answers probes **from memory alone**; a three-model panel *extracts* what
the answer claims (content present? which sources?) and the category is
computed in code against the manifest:

* **laundered** — a speculation presented as owner-stated or observed
  (misattribution *up* the trust scale); also **demoted**, **wrong source**,
  **absent**, **confabulated**.

Memory policies: `c1` verbatim owner utterances; `c2` flat notes; `c3`
self-edited prompt block (1,500 chars); `c4` attributed store — every record
labeled with its origin by a fixed, isolated annotator seat under the
frozen rules (`rules/annotation-rules.md`); `c5` = c4 compressed to c3's
budget keeping labels; plus production systems behind `adapters.py`:
**mem0**, **Letta**, **Graphiti**.

### Headline — self-poisoning, no adversary (English corpus, storyline A, rubric v1.1)

| memory | laundered / present | any error | coverage |
|---|---|---|---|
| C1 verbatim | 2.3% [1, 6] | 6.8% | 41% |
| C2 flat notes | 25.3% [20, 31] | 36.2% | 71% |
| C3 self-edit block | 32.7% [27, 39] | 53.1% | 70% |
| mem0 2.0.18 | 29.0% [23, 36] | 40.3% | 57% |
| Letta 0.16.8 | 26.6% [21, 33] | 44.3% | 59% |
| Graphiti 0.29.3 | 24.4% [19, 31] | 28.4% | 62% |
| **C4 attributed store** | **3.1% [2, 6]** | 9.4% | **89%** |
| **C5 attributed, compressed** | **6.2% [4, 10]** | 12.9% | 74% |

The loss is complete at the first rewrite and does not grow with sessions;
the error runs *up* (speculation → "the owner said"), the reverse almost
never; the label, not memory volume, is the active ingredient (C5). The
Russian mirror (four families, 3,960 verdicts) and storyline B replicate.
Full tables: `RESULTS-v2.md` (v1/v0 kept for the record).

### Headline — adversarial, MINJA via SuperRed (`superred/`)

Four agent families × two attacker channels (a guest on the household chat;
a document the owner asks the agent to read) × 16 tasks, end-to-end ASR:

| pooled (n = 128) | C2 flat notes | C2 + read rule, no labels | I2 | I2 + I4 | **I2 + I4 + I3** |
|---|---|---|---|---|---|
| attack success | 46.9% [38, 55] | 50.0% | 41.4% | 39.8% | **10.2% [6, 17]** |

Full mechanism is the minimum in 8/8 family × channel pairs; write-time
promotion of the planted claim is 0 under I2 + I4 in every cell; the
residual is read-side (a prompt-mediated reader ignoring a correct label)
and classified. Full report: `superred/results/REPORT.md`; per-run traces
in `superred/results/<cell>/{runs,verdicts}.jsonl`.

## Layout

```
gen_corpus.py, storyline*.py   deterministic corpus generators (RU/EN, A/B)
corpus*/                       generated corpora + manifests + probes
harness.py                     replay harness: policies c1–c5, probes
adapters.py                    mem0 / Letta / Graphiti behind one interface
judge.py, curve.py, langtable.py, replicates.py   panel judge + tables
runs/<cell>/                   memory snapshots per session, answers, judgments, verdicts
adjudicate.py, adjudication*/  blind human/LLM adjudication (RU done; EN LLM seat done, human queued)
rules/annotation-rules.md      frozen annotation rules v2.3 (the C4 annotator's only authority)
docs/design.md                 bench design decisions
superred/                      SuperRed target, tasks, sweep, re-judge, report
reproduce.sh                   regenerate corpora, verdicts, tables, REPORT.md; diff against tree
```

## Running

Free tier (no API): `./reproduce.sh`.

Paid tier (OpenRouter): `export OPENROUTER_API_KEY=...`, then e.g.

```
python3 harness.py --corpus en --family haiku gemini --condition c2 c4
python3 judge.py --corpus en ...            # see judge.py --help
```

Framework cells need the project venv: `pip install mem0ai
sentence-transformers qdrant-client letta-client graphiti-core` (+ CPU
torch). Letta runs as the official container (`docker run -d --name
spb-letta -p 8283:8283 -e OPENROUTER_API_KEY=... -e
LETTA_TELEMETRY_ENABLED=false letta/letta`, server 0.16.8); Graphiti needs
Neo4j (`docker run -d --name spb-neo4j -p 7687:7687 -e
NEO4J_AUTH=neo4j/spbgraphiti neo4j:5`). `LETTA_URL`, `NEO4J_URI/USER/PASS`
override the defaults in `adapters.py`.

Adversarial leg: `pip install superred superred-optimizer-minja
superred-optimizer-goal-passthrough`, then

```
python3 superred/run_superred.py --attacker minja --channel guest_chat documents \
    --family haiku gemini gpt deepseek --policy c2 c2i3 c4 c4i4 c4i4i3 --ext
python3 superred/rejudge.py --force superred/results/minja-*   # unified three-metric verdicts
python3 superred/report.py
```

Models are pinned by OpenRouter id in `harness.FAMILIES`; the C4 annotator
seat is always `anthropic/claude-haiku-4.5` at temperature 0.

## Provenance of the numbers

Every verdict file, table and the adversarial report is a pure function of
the stored model outputs in `runs/` and `superred/results/*/runs.jsonl`;
`reproduce.sh` asserts byte identity. The blind adjudication samples and
scores are in `adjudication*/`; the EN human key is withheld until the
human adjudication is scored.

## License

Code: MIT. Corpora, stored model outputs, adjudication files and results:
CC BY 4.0. See `LICENSE`.
