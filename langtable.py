#!/usr/bin/env python3
"""SPB language table: RU (storyline A) vs EN (A-EN mirror), per cell
and pooled per policy, rubric v1.1. No API calls.

  langtable.py                 storyline A: RU (cells <f>-<p>) vs EN (en-<f>-<p>)
  langtable.py --storyline b   storyline B: RU (b-<f>-<p>) vs EN (ben-<f>-<p>)
  langtable.py --replicates    EN T=0 (en-*) vs EN T=0.7 (r2-en-*)
"""
import argparse
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
ERROR = {"laundered", "demoted", "wrong_source"}
POLICIES = ["c1", "c2", "c3", "c4", "c5", "mem0", "letta", "graphiti"]
FAMILIES = ["haiku", "gemini"]


def wilson(k, n, z=1.96):
    if not n:
        return 0, 0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return 100 * (c - h) / d, 100 * (c + h) / d


def stats(cells):
    n = a = la = e = 0
    for cell in cells:
        fp = os.path.join(RUNS, cell, "verdicts-v11.csv")
        if not os.path.exists(fp):
            return None
        for r in csv.DictReader(open(fp, encoding="utf-8")):
            n += 1
            a += r["category"] == "absent"
            la += r["category"] == "laundered"
            e += r["category"] in ERROR
    p = n - a
    return la, p, e, n


def fmt(s):
    if s is None:
        return "—".center(30)
    la, p, e, n = s
    lo, hi = wilson(la, p)
    return (f"{100*la/p:5.1f}% [{lo:2.0f},{hi:2.0f}] ({la:3d}/{p:3d})"
            f"  err {100*e/p:4.1f}%  cov {100*p/n:3.0f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--storyline", choices=["a", "b"], default="a")
    ap.add_argument("--replicates", action="store_true")
    args = ap.parse_args()
    if args.replicates:
        left, right, lh, rh = "en-", "r2-en-", "EN T=0", "EN T=0.7 (r2)"
    elif args.storyline == "b":
        left, right, lh, rh = "b-", "ben-", "RU (corpus-b)", "EN (corpus-b-en)"
    else:
        left, right, lh, rh = "", "en-", "RU (corpus)", "EN (corpus-en)"
    print(f"{'policy':8s} {'family':7s} | {lh:^44s} | {rh:^44s}")
    for pol in POLICIES:
        for fam in FAMILIES + ["pooled"]:
            fams = FAMILIES if fam == "pooled" else [fam]
            lft = stats([f"{left}{f}-{pol}" for f in fams])
            r = stats([f"{right}{f}-{pol}" for f in fams])
            if lft is None and r is None:
                continue
            print(f"{pol:8s} {fam:7s} | {fmt(lft)} | {fmt(r)}")
        print()


if __name__ == "__main__":
    main()
