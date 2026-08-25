#!/usr/bin/env python3
"""Seed-replicate comparison: runs/<cell> (T=0) vs runs/r<k>-<cell> (T=0.7).

Prints laundered/present and any-error/present with Wilson 95% CIs per
cell and replicate, plus the per-checkpoint laundering so the
"no growth after k=1" statement can be read off at the data's power.

  replicates.py            all cells that have at least one r*- twin
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
sys.path.insert(0, HERE)
from adjudicate import wilson  # noqa: E402

RUBRIC = "v11"
ERR = {"laundered", "demoted", "wrong_source"}
CKPTS = [1, 3, 5, 10, 15, 20]


def rows(cell):
    fp = os.path.join(RUNS, cell, f"verdicts-{RUBRIC}.csv")
    if not os.path.exists(fp):
        return None
    with open(fp, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)
                if r["type"] == "attribution" or r["type"].startswith("open.")]


def stat(rs):
    present = [r for r in rs if r["category"] not in ("absent", "no_majority")]
    laun = sum(r["category"] == "laundered" for r in present)
    err = sum(r["category"] in ERR for r in present)
    return len(rs), len(present), laun, err


def fmt(rs):
    n, p, la, e = stat(rs)
    lo, hi = wilson(la, p)
    return (f"laundered {100*la/max(p,1):5.1f}% [{100*lo:2.0f},{100*hi:2.0f}] ({la:3d}/{p:3d})"
            f"  any-err {100*e/max(p,1):5.1f}%  coverage {100*p/max(n,1):3.0f}%")


def main():
    cells = sorted(d for d in os.listdir(RUNS) if re.match(r"r\d+-", d) and os.path.isdir(os.path.join(RUNS, d)))
    if not cells:
        sys.exit("no replicate cells")
    for rc in cells:
        base = re.sub(r"^r\d+-", "", rc)
        a, b = rows(base), rows(rc)
        if a is None or b is None:
            print(f"{rc}: not judged yet")
            continue
        print(f"== {base}")
        print(f"   T=0   {fmt(a)}")
        print(f"   {rc[:2]}    {fmt(b)}")
        line = []
        for k in CKPTS:
            _, pa, la, _ = stat([r for r in a if int(r["checkpoint"]) == k])
            _, pb, lb, _ = stat([r for r in b if int(r["checkpoint"]) == k])
            line.append(f"k{k}:{la}/{pa}|{lb}/{pb}")
        print("   per checkpoint (T=0|rep): " + "  ".join(line))


if __name__ == "__main__":
    main()
