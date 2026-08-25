#!/usr/bin/env python3
"""SPB inference statistics: clustered and paired, over tracer clusters.

Single source for every interval and paired figure quoted in Section 6
of the preprint (v1.2). No API calls; reads runs/<cell>/verdicts-v11.csv.

  stats.py                     EN storyline A grid (en-<fam>-<policy>)
  stats.py --prefix "" --families haiku gemini gpt deepseek   RU mirror

Outputs, per policy pooled over families:
  * laundered/present with a cluster-bootstrap 95% CI (percentile,
    resampling the tracer clusters with replacement, B=10000, seed 0).
    The unit of observation is tracer x checkpoint x family; the same
    tracer is measured up to twelve times, so per-observation Wilson
    intervals would overstate precision (langtable.py prints those).
  * per-tracer summary: tracers asserted, tracers laundered at least once.

Paired block, C4 against each unlabeled policy (same corpus, same
tracers, same judge -- the rows are not independent witnesses, so the
paired view is the correct form):
  * mean per-tracer paired difference (policy minus C4), over tracers
    asserted under both, with a paired cluster-bootstrap 95% CI;
  * McNemar-style direction: tracers laundered at least once under the
    policy while clean under C4, and the reverse.
Common-tracer block: the same table restricted to tracers asserted
under every compared policy, where coverage differences cannot bias
the denominator.

Cluster = tracer id; twin-probe rows (tracer "tA+tB") are assigned to
the first component, so every verdict row lands in exactly one
cluster. The cluster list is the union of merged tracer ids observed
in the loaded verdicts (the 26 registry tracers on storyline A;
storyline B adds its three confab probes as their own clusters).
"""
import argparse
import csv
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
UNLABELED = ["c2", "c3", "mem0", "letta", "graphiti"]
# c4x/c5x: stripped-label controls; c4g: annotator seat moved to gemini;
# letta-tbt: turn-by-turn Letta protocol
POLICIES = ["c1"] + UNLABELED + ["letta-tbt", "c4", "c4x", "c4g", "c5", "c5x"]
B = 10000
SEED = 0


def load_probemap(corpus_dir):
    fp = os.path.join(HERE, corpus_dir, "probes.csv")
    return {r["probe_id"]: r["tracer"] for r in csv.DictReader(open(fp, encoding="utf-8"))}


def tracer_of(row, probemap):
    t = row["type"]
    tr = t.split(".", 1)[1] if t.startswith("open.") else probemap.get(row["probe_id"], "")
    return tr.split("+")[0]  # twin rows cluster with their first component


def load_policy(prefix, families, policy, probemap):
    """-> {tracer: [(laundered, present), ...]} or None if a cell is missing."""
    per = defaultdict(list)
    for fam in families:
        fp = os.path.join(RUNS, f"{prefix}{fam}-{policy}", "verdicts-v11.csv")
        if not os.path.exists(fp):
            return None
        for r in csv.DictReader(open(fp, encoding="utf-8")):
            tr = tracer_of(r, probemap)
            if not tr:
                continue
            per[tr].append((r["category"] == "laundered", r["category"] != "absent"))
    return per


def rate(per, tracers=None):
    ts = per.keys() if tracers is None else tracers
    la = sum(o[0] for t in ts for o in per.get(t, ()))
    p = sum(o[1] for t in ts for o in per.get(t, ()))
    return la, p


def boot_ci(rng, draw):
    """Percentile 95% CI over B evaluations of draw(resampled tracer list)."""
    vals = sorted(v for v in (draw(rng) for _ in range(B)) if v is not None)
    if not vals:
        return None, None
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals))]


def cluster_ci(per, clusters):
    rng = random.Random(SEED)

    def draw(rng):
        pick = [clusters[rng.randrange(len(clusters))] for _ in clusters]
        la = sum(o[0] for t in pick for o in per.get(t, ()))
        p = sum(o[1] for t in pick for o in per.get(t, ()))
        return 100 * la / p if p else None

    return boot_ci(rng, draw)


def tracer_rate(per, t):
    la = sum(o[0] for o in per[t])
    p = sum(o[1] for o in per[t])
    return 100 * la / p if p else None


def paired(per_x, per_c4):
    """Tracers asserted under both; mean per-tracer diff + CI + direction."""
    both = sorted(t for t in per_x if t in per_c4
                  and tracer_rate(per_x, t) is not None
                  and tracer_rate(per_c4, t) is not None)
    diffs = {t: tracer_rate(per_x, t) - tracer_rate(per_c4, t) for t in both}
    mean = sum(diffs.values()) / len(both)
    rng = random.Random(SEED)

    def draw(rng):
        pick = [both[rng.randrange(len(both))] for _ in both]
        return sum(diffs[t] for t in pick) / len(pick)

    lo, hi = boot_ci(rng, draw)
    x_only = sum(1 for t in both
                 if any(o[0] for o in per_x[t]) and not any(o[0] for o in per_c4[t]))
    c4_only = sum(1 for t in both
                  if any(o[0] for o in per_c4[t]) and not any(o[0] for o in per_x[t]))
    return len(both), mean, lo, hi, x_only, c4_only


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="en-")
    ap.add_argument("--corpus", default="corpus-en")
    ap.add_argument("--families", nargs="+", default=["haiku", "gemini"])
    args = ap.parse_args()
    probemap = load_probemap(args.corpus)
    data = {}
    for pol in POLICIES:
        per = load_policy(args.prefix, args.families, pol, probemap)
        if per is not None:
            data[pol] = per
    clusters = sorted({t for per in data.values() for t in per})

    print(f"clusters: {len(clusters)} observed tracers; B={B}, seed={SEED}\n")
    print(f"{'policy':9s} {'laundered/present':>18s} {'cluster 95% CI':>16s}"
          f" {'asserted':>9s} {'laundered>=1':>13s}")
    for pol in POLICIES:
        if pol not in data:
            continue
        la, p = rate(data[pol])
        lo, hi = cluster_ci(data[pol], clusters)
        nt = sum(1 for t in data[pol] if any(o[1] for o in data[pol][t]))
        lt = sum(1 for t in data[pol] if any(o[0] for o in data[pol][t]))
        print(f"{pol:9s} {la:4d}/{p:4d} = {100*la/p:5.1f}% [{lo:5.1f},{hi:5.1f}]"
              f" {nt:9d} {lt:13d}")

    if "c4" in data:
        print("\npaired against c4 (tracers asserted under both):")
        print(f"{'policy':9s} {'n':>3s} {'mean diff':>10s} {'paired 95% CI':>16s}"
              f" {'pol-only':>9s} {'c4-only':>8s}")
        tot_x = tot_c4 = 0
        for pol in UNLABELED:
            if pol not in data:
                continue
            n, mean, lo, hi, x_only, c4_only = paired(data[pol], data["c4"])
            tot_x += x_only
            tot_c4 += c4_only
            print(f"{pol:9s} {n:3d} {mean:+9.1f}pp [{lo:6.1f},{hi:6.1f}]"
                  f" {x_only:9d} {c4_only:8d}")
        print(f"direction pooled over comparisons: {tot_c4} (c4-only) vs {tot_x} (policy-only)")

        compared = [p for p in UNLABELED + ["c4", "c5"] if p in data]
        common = sorted(set.intersection(*(
            {t for t in data[p] if any(o[1] for o in data[p][t])} for p in compared)))
        print(f"\ncommon tracers across {'/'.join(compared)}: {len(common)}")
        for pol in compared:
            la, p = rate(data[pol], common)
            print(f"{pol:9s} {la:4d}/{p:4d} = {100*la/p:5.1f}%")


if __name__ == "__main__":
    main()
