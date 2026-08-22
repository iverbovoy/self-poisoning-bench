#!/usr/bin/env python3
"""SPB language table: RU (storyline A) vs EN (A-EN mirror), per cell
and pooled per policy, rubric v1.1. No API calls.

  langtable.py            prints the table; rows = policies incl. v2 frameworks
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
ERROR = {"laundered", "demoted", "wrong_source"}
POLICIES = ["c1", "c2", "c3", "c4", "c5", "mem0", "letta"]
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
    n = a = l = e = 0
    for cell in cells:
        fp = os.path.join(RUNS, cell, "verdicts-v11.csv")
        if not os.path.exists(fp):
            return None
        for r in csv.DictReader(open(fp, encoding="utf-8")):
            n += 1
            a += r["category"] == "absent"
            l += r["category"] == "laundered"
            e += r["category"] in ERROR
    p = n - a
    return l, p, e, n


def fmt(s):
    if s is None:
        return "—".center(30)
    l, p, e, n = s
    lo, hi = wilson(l, p)
    return (f"{100*l/p:5.1f}% [{lo:2.0f},{hi:2.0f}] ({l:3d}/{p:3d})"
            f"  err {100*e/p:4.1f}%  cov {100*p/n:3.0f}%")


def main():
    print(f"{'policy':8s} {'family':7s} | {'RU (corpus)':^44s} | {'EN (corpus-en)':^44s}")
    for pol in POLICIES:
        for fam in FAMILIES + ["pooled"]:
            fams = FAMILIES if fam == "pooled" else [fam]
            ru = stats([f"{f}-{pol}" for f in fams])
            en = stats([f"en-{f}-{pol}" for f in fams])
            if ru is None and en is None:
                continue
            print(f"{pol:8s} {fam:7s} | {fmt(ru)} | {fmt(en)}")
        print()


if __name__ == "__main__":
    main()
