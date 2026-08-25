#!/usr/bin/env python3
"""Bounded model check of the rank-axis invariants (paper Section 4).

Finite model of the schema. One content atom phi enters through a foreign
channel (a guest). Records are (content, kind, layer) with kind
'belief' | 'event' and layer from a small alphabet; the utterance event
"[self] observed: the guest uttered phi" is a rank-0 EVENT record whose
quoted payload is phi and whose speaker is the guest.

The ordinary loop is five operation families; `promote` is deliberately
absent (the check asks what is reachable WITHOUT it):

  write       - route the incoming utterance: the event record is always
                a legitimate rank-0 record; the content routes by channel
                with I2 on, to the agent's own layer with I2 off
  consolidate - rewrite a record; a belief stays a belief at its layer
                (I1 on) or may move down-rank (I1 off); an event stays an
                event - asserting its CONTENT is de-quotation, below
  dequote     - assert the quoted content of an event record; lands at
                the speaker's layer with I2' on, at the event's own
                layer (rank 0) with I2' off
  infer       - derive a belief about phi from stored premises; a belief
                premise contributes its own rank; an event premise
                contributes the speaker's rank with I2' on, its record
                rank (0) with I2' off; the conclusion takes the max
                premise rank with I4 on, rank 0 with I4 off
  reply       - the agent's own text generated from a record; inherits
                the source rank with I4 on (the implemented site),
                rank 0 with I4 off

Violation: a reachable state holds (phi, belief, self) - the foreign
claim as the agent's own rank-0 belief. The norm door is out of reach
by construction here: it consumes utterance events on the identified
OWNER channel only, and the guest's event is not on it; it emits
intentions, never beliefs, so it adds no belief states.

Exhaustive breadth-first search over reachable record sets (finite atom
set, so it terminates). Expected: no violation with all four invariants
on; a concrete counterexample trace for each invariant dropped alone
(I1 off: consolidation down-ranks the guest belief; I2 off: content
routed straight to rank 0; I2' off: de-quotation from the event
record; I4 off: a reply/inference from the event lands at rank 0).

  python3 formal_check.py
"""
from itertools import combinations

PHI = "phi"
LAYERS = ("self", "self.guest", "self.user", "self.user.self")
RANK = {"self": 0, "self.guest": 1, "self.user": 1, "self.user.self": 2}
SPEAKER_LAYER = "self.guest"     # the guest is the speaker of the event


def layer_of_rank(r):
    return next(lay for lay in LAYERS if RANK[lay] == r)


def effective_rank(rec, inv):
    """Rank a premise contributes when its CONTENT is asserted."""
    content, kind, layer = rec
    if kind == "event":
        return RANK[SPEAKER_LAYER] if inv["I2p"] else RANK[layer]
    return RANK[layer]


def step(state, inv):
    out = set()
    # write
    out.add((PHI, "event", "self"))
    out.add((PHI, "belief", "self.guest" if inv["I2"] else "self"))
    for rec in state:
        content, kind, layer = rec
        if kind == "belief":
            # consolidate a belief
            if inv["I1"]:
                out.add((content, "belief", layer))
            else:
                for lay in LAYERS:
                    if RANK[lay] <= RANK[layer]:
                        out.add((content, "belief", lay))
        else:
            # consolidate an event: stays an event at its layer
            out.add((content, "event", layer))
            # dequote its content
            out.add((content, "belief",
                     SPEAKER_LAYER if inv["I2p"] else layer))
        # reply generated from this record, asserting its content
        r = effective_rank(rec, inv) if inv["I4"] else 0
        out.add((content, "belief", layer_of_rank(r)))
    # infer over any 1-2 premises that carry phi
    prem = [r for r in state if r[0] == PHI]
    for n in (1, 2):
        for sub in combinations(prem, n):
            if not sub:
                continue
            r = (max(effective_rank(p, inv) for p in sub)
                 if inv["I4"] else 0)
            out.add((PHI, "belief", layer_of_rank(r)))
    return out


def violated(state):
    return (PHI, "belief", "self") in state


def search(inv, max_depth=6):
    state = frozenset()
    seen = {state}
    frontier = [(state, [])]
    for _ in range(max_depth):
        nxt = []
        for st, trace in frontier:
            for rec in step(st, inv):
                st2 = frozenset(st | {rec})
                if st2 in seen:
                    continue
                seen.add(st2)
                tr2 = trace + [rec]
                if violated(st2):
                    return tr2
                nxt.append((st2, tr2))
        frontier = nxt
    return None


def main():
    base = {"I1": True, "I2": True, "I2p": True, "I4": True}
    cex = search(base)
    print("all ON            :",
          "no violating state reachable" if cex is None
          else f"VIOLATION {cex}")
    assert cex is None
    for drop in ("I2", "I2p", "I4"):
        inv = dict(base)
        inv[drop] = False
        cex = search(inv)
        assert cex is not None, drop
        print(f"{drop:4s} dropped      : counterexample  " + " -> ".join(
            f"({c},{k},{lay})" for c, k, lay in cex))
    inv = dict(base)
    inv["I1"] = False
    cex1 = search(inv)
    assert cex1 is not None
    print("I1   dropped      : counterexample  " + " -> ".join(
        f"({c},{k},{lay})" for c, k, lay in cex1))
    print("\nresult: (phi, belief, rank 0) unreachable under "
          "I1+I2+I2'+I4 without `promote`; dropping any one invariant "
          "yields a concrete laundering trace.")


if __name__ == "__main__":
    main()
