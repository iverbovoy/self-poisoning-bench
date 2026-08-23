# Annotation rules v2.3 — itemAE phase 2 (see PLAN.md)

v2.2 → v2.3 (post-2.0 debrief, 2026-08-17): ground routes by evidence
channel, not content; the temporal test spelled out; new R-quoted for
attributed content inside tool payloads. Values are closed vocabularies —
spelling counts (`inferred`, not `infered`).

One record → one annotation. Walk the decision path top to bottom; most
columns stay empty most of the time.

## The decision path

**Step 0 — is there a claim at all?**
Greetings, acknowledgements, filler ("привет", "ок", "ну давай") carry no
propositional content. Mark `unresolvable = x`, write `phatic` in notes,
stop. This is a standard outcome, not a judgment call. (A meaningful "ок"
answering a pending tool confirmation reaches the feed as a `tool_call`
decision record anyway — the bare `user_msg` alone carries nothing.)

**Step 1 — whose picture does the claim live in? → `path`**
- `self` — the system's own picture: sensor facts, its own states, its own
  questions and actions.
- `self.user` — the picture attributed to the owner: what he wants, knows,
  plans, prefers — *as presented or read from him*.
- `self.user.self` — the system as a character inside the owner's picture:
  what he thinks/expects/believes about IT.
- Deeper than rank 2 (`self.x.y.z`) must not occur → `unresolvable`, say why.
- **The path grows only when a picture is attributed to someone.** Being
  mentioned inside the content does not add a layer: "ты считаешь меня
  параноиком" is the owner's picture of the system's picture (rank 2) whose
  content is a property claim — not rank 3.

**Step 2 — pointing at what, to justify it? → `ground`**
instrument → `observed` · someone's words → `asserted` · someone's deed →
`behavioral` · other records → `inferred` · a guess → `assumed`.
Ground names the **evidence channel, not what the content describes**. A
deed captured by an instrument is `observed` — the sensor reports it
("away", "back", "attention: left monitor" are all deeds of the owner, and
all `observed`). `behavioral` is reserved for deeds read from the
interaction itself, where no instrument stands between: cancelled a tool,
rephrased, ignored a suggestion.

**Step 3 — a point, a span, or a trait? → `temporal_kind`**
`event` (instant) · `state` (has a start, possibly an end) · `disposition`
(open-ended trait/preference, decays). The test — ask of the claim: true
**в этот момент** (at that instant, then it's over) → `event`; true **до
сих пор** (holds from a start until further notice) → `state`; true
**вообще** (no particular time attached) → `disposition`. A transition
("вернулся") is an event; the condition it opens ("отсутствует") is a
state. Boundary: **beliefs/opinions about
something → `state`** (revisable, about a matter); tastes, habits,
preferences → `disposition`. A directly asserted preference ("я предпочитаю
X") IS a disposition — R-scope forbids *inferring* dispositions from single
events, not recording asserted ones.

**Step 4 — the usually-empty columns.**
- `valid` — only when the interval is written in the record itself
  ("с 10 по 20 августа"); never reconstructed. Default: empty. Write it
  as ISO `YYYY-MM-DD/YYYY-MM-DD` (open end: leave that side empty,
  e.g. `2026-08-10/`).
- `conflict_with` — id of another record; only same path + same ground +
  both dispositions + incompatible. Events/states never conflict
  (trajectory); different ground never conflicts (diff material).
  Mark it on either record of the pair — direction carries no
  information and the checkers treat it symmetrically.
- `intent` — `tool_call` records only: `intended` (the effect was the
  point) · `foreseen` (known side effect, not the point) · `reaction`
  (no deliberation visible).

## Case rules

**R-sensor (defaults — presumptions, override only if content clearly says
otherwise):**
- detector transition/verdict ("вернулся", "лицо: You 0.41", "доступ
  выдан") → `self / observed / event`;
- perception snapshot → `self / observed / state`;
- current state ("сейчас отсутствует, с 14:02") → `self / observed / state`;
- **time-spanning aggregate** ("отсутствует 40 минут", "уходил трижды") →
  `self / inferred / state` — the instrument ends at the transition event;
  anything gluing several events is derived.

**R-vlm (D8):** VLM scene captions (`vlm_obs`) → `self / inferred`, usually
`state` — the describer is an interpreter, not a calibrated instrument, so
its output never gets `observed`; it derives from the frame-capture event
(the `frame` reference in the record), which itself is `self / observed /
event` — the camera IS an instrument. (`asserted` rejected: a stateless
model call is not a source with a picture of its own.)

**R-question:** a question's content is "wants to know X". Route by asker:
owner's question → `self.user / asserted`; the agent's own question →
`self / asserted`. Usually `event`.

**R-speech:** the owner's statements about himself — facts, preferences,
plans ("мне 37", "предпочитаю темноту") → `self.user / asserted`, however
objective they sound: self-report never promotes to `self` by itself (I1).
What he *does in the interaction* (cancels a tool, rephrases, ignores a
suggestion) → `behavioral`; the same deed reported by a sensor is
`observed` (Step 2 — evidence channel).

**R-quoted:** content carried inside a tool payload, note, or quotation
that is **explicitly attributed to someone's words** ("source: owner
said", quoted speech) routes by the original speaker, exactly as if said
directly: a stored note "владелец в Киеве — owner said" is the owner's
claim about himself → `self.user / asserted`. The wrapping action (the
remember call executed) does not reset attribution to `self` — that would
be the promotion I1 forbids, performed by the annotator.

**R-scope:** annotate what THIS record alone carries. One "make it short"
is a momentary request (event); the standing preference would be
consolidation's work, not yours. If a conclusion needs several records —
skip it.

**Honesty valve:** if the path above doesn't decide — `unresolvable = x` +
one line why. Its share is a phase-2.0 metric with a stop threshold; never
squeeze out an answer to keep it low.

## Worked examples

| Record (abridged) | path | ground | temporal | note |
|---|---|---|---|---|
| sensor: "вернулся" | self | observed | event | R-sensor |
| sensor: "отсутствует 40 мин" | self | inferred | state | aggregate |
| user: "что видишь сейчас?" | self.user | asserted | event | R-question |
| agent: "как зовут кота?" | self | asserted | event | agent's own question |
| user: "мне 37, инженер" | self.user | asserted | state | R-speech |
| user: "предпочитаю темноту" | self.user | asserted | disposition | R-speech |
| agent: "ты обычно уходишь к 15:00" | self.user | inferred | disposition | generalization |
| agent: "ты думаешь, я не запоминаю" | self.user.self | assumed | state | rank 2 |
| tool: lock_screen cancelled | self | behavioral | event | intent per case |
| user: "привет" | — | — | — | phatic → unresolvable |

## Procedure

- Practice first on the canon deck (`evals/canon.csv`), check yourself with
  `evals/canon_check.py` — disagreements with the key are rule bugs to
  discuss, not failures.
- Real sessions: go in order, ~2 min per record, trust the first reading.
  Save as CSV (Keep Current Format). Session B ≥ 2 days later, blind.
- Specific records are not discussed between sessions; rule questions are
  fine.
