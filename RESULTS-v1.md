# SPB v1 results — 4 families x 4 policies x 2 storylines (2026-08-20/21)

24 cells, 3,960 panel-majority verdicts (no_majority 1.3%).
Families: claude-haiku-4.5, gemini-3.6-flash, gpt-5.6-terra,
deepseek-v4-flash. Storyline A (designer) all four families; storyline
B (teacher; new tracer classes) haiku + gemini. C4 annotator fixed
(haiku, rules v2.3) in every cell.

## Pooled by policy (attribution + open-list verdicts; Wilson 95%)

| policy | laundered / present | any-error | coverage |
|---|---|---|---|
| C1 verbatim-user | **2.3%** [1,4] (9/389) | 4.6% | 42% |
| C2 flat notes | **30.7%** [27,34] (187/610) | 50.7% | 65% |
| C3 self-edit block | **32.1%** [29,36] (216/673) | 49.6% | 72% |
| C4 attributed | **2.0%** [1,3] (16/803) | 21.2%* | **86%** |

CIs for C2/C3 vs C4 do not overlap: a ~15x reduction in laundering
with the highest coverage of all policies. (*C4 any-error is inflated
by scoring strictness — see caveat 1.)

## Per-cell laundered counts (of 156 attribution/open verdicts)

| family / storyline | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| haiku A | 2 | 39 | 49 | 3 |
| gemini A | 4 | 18 | 21 | 0 |
| gpt A | 0 | 16 | 21 | 3 |
| deepseek A | 1 | 41 | 43 | 0 |
| haiku B | 1 | 43 | 47 | 6 |
| gemini B | 1 | 30 | 35 | 4 |

Every rephrasing cell leaks (16-49); every attributed cell is at 0-6.
Storyline B replicates A for both families.

## Findings beyond v0

1. **Direction asymmetry is universal.** Across all four families the
   dominant error in C2/C3 is b->a (agent speculation presented as
   owner-stated): haiku 167/245, gemini 104/230 (+93 dropped sources),
   gpt 37/59, deepseek 80/109. Demotion (a->b) is essentially absent
   (2 cases total). Memory lies UP the trust scale, almost never down.
2. **Three failure surfaces, one disease.** haiku and deepseek
   confidently misattribute; gemini drops sourcing (->none); gpt writes
   sparse memory (C2 coverage 50%) and still misattributes a third of
   what it keeps. No consolidation style is safe.
3. **Chained speculation (b05 -> b10) is already saturated at generation
   one.** In C2/C3 the derived speculation launders as completely as its
   parent (e.g. b-haiku-c2: parent 9/10 laundered, child 6/6). W_t
   beyond the first hop adds nothing because the first write already
   destroyed the label — consistent with the v0 write-time finding. C4
   keeps both generations correct.
4. **Confabulation is family-specific.** Never-seeded topics: haiku
   invents 1/36, gemini 8/36 — and gemini's self-edit block (C3)
   fabricates on 4/9 probes. C4: 1/36 for gemini, 0 for haiku.
5. **Rebuke replicates.** b14 (owner: "ерунда") is absent in 5 of 6
   C2/C3 cells — pushback prevents storage, as with A's t13. The one
   exception (b-haiku-c3) stored it with CORRECT attribution.
6. **Third-party report routes correctly.** b13 ("завуч говорит...") is
   attributed to the owner's report in 7/8 cells — supports the
   canon2#10 ruling (reporter keeps it).
7. **Corrections mostly stick.** b15->b17 schedule change: decision
   probe correct in 7/8 cells; only b-haiku-c2 still treated Tuesday as
   busy per the superseded schedule (laundered). C3 evicts the stale
   schedule entirely (absent), C4 keeps old and new labeled.
8. **Decisions replicate the v0 split on B:** vegetarian constraint and
   moved olympiad date correct in all 8 B cells.

## Caveats

1. **C4 `wrong_source` on B (35-38% any-error) is mostly scoring
   strictness, not attribution loss**: (a) "mixed" answers where the
   C4 store genuinely holds several labeled records on the topic (the
   owner's request AND the agent's generalization) — the agent names
   both, the rubric accepts one; (b) tracer b08 (reminder tool call):
   manifest says `observed`, the v2.3 annotator routes the payload to
   the owner (`self.user/asserted`) — a manifest-vs-rules dispute, and
   the rules are arguably right. Rubric was pre-registered and is NOT
   rescored; queued for SPB v1.1: accept "mixed" when >1 true-origin
   record exists on the topic; align manifest origin of tool payloads
   with R-quoted.
2. Still synthetic; C3 is a Letta-style proxy; storyline B only on two
   families; one seed (temperature 0 — replication came from the
   second storyline, not reruns).
3. Judge panel shares a family with two agents (haiku, and opus with
   haiku); gemini seat and the cross-family consistency of results
   mitigate; Ivan's blind spot-adjudication of the 50 no_majority +
   a random sample is the next protocol step.

## Next

Ivan adjudication sample; SPB v1.1 rubric fixes (then rescore, report
both); gpt/deepseek on storyline B; live-refeed column; SPB v2 with
real mem0/Zep/Letta; hedge-decay write-up.

---

## Addendum 2026-08-21 — rubric v1.1 (complete) and the C5 control

Completeness audit added after an incident: the first v1.1 pass was
partially lost to an OpenRouter 402 and an earlier interim table was
computed on incomplete cells. All numbers below are from judgments
verified complete (every cell within 3 calls of answers x 3 judges).

### Pooled, both rubrics (24 cells + C5 on three families)

| policy | v1.0 laundered | v1.1 laundered | v1.1 any-error | coverage |
|---|---|---|---|---|
| C1 | 2.3% | 3.0% [2,5] | 5.3% | 43% |
| C2 | 30.7% | 30.3% [27,34] | 50.0% | 66% |
| C3 | 32.1% | 33.4% [30,37] | 48.4% | 71% |
| C4 | 2.0% | 4.9% [4,7] | 13.4% | 87% |
| C5 | 3.2% | 2.6% [1,5] | 5.5% | 66% |

Rubric v1.1 (list-valued sources, legitimate-origin sets, tool-payload
ambiguity {c,a}) moves C4 laundering up (unsupported co-sources now
count) and C4 any-error down (legitimate mixed answers accepted);
C2/C3 are unchanged. The gap narrows from ~15x to ~6-7x and stays
disjoint at 95%. The result is robust to the rubric.

### C5: labels, not volume

C5 = C4 annotation + the FAMILY model compresses the labeled store to
the C3 budget (1500 chars) with an instruction to keep every [label].
Memory at s20: C3 1.1-1.6K chars, C5 1.2-1.5K, C4 8.5K.

| family (A) | C3 laundered | C4 | C5 |
|---|---|---|---|
| haiku | 48 | 5 | 3 |
| gemini | 19 | 2 | 2 |
| gpt | 22 | 6 | 3 |

Same budget, same compressor, same agent — laundering drops 6-16x when
the compressor must preserve source labels. Coverage equals C3's.
The "C4 just remembers more" objection is closed: the label is the
active ingredient; a structural label survives compression that
destroys every lexical hedge. deepseek-c5 could not be run: the
reasoning model exhausts its completion budget thinking about the
compression prompt even with a reasoning cap — recorded, not hidden.

### Known limitation surfaced by v1.1 on storyline B

C4 on B shows 12-14 laundered under v1.1 (vs 1-6 on A). Storyline B's
owner CONFIRMS several speculations ("есть такое", "угадал") — a
confirmed speculation is partly owner-asserted, so "you confirmed it"
co-sources are arguably legitimate; TOPIC_SOURCES does not yet encode
confirmations. Queue for v1.2: treat explicit owner confirmation as a
legitimate co-source. Storyline A's owner replies were non-committal,
so A is unaffected.
