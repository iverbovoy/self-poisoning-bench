#!/usr/bin/env python3
"""SPB curve aggregation: verdicts.csv per cell -> the headline tables.

No API calls. Reads runs/<cell>/verdicts.csv produced by judge.py.

Tables:
  1. Attribution-error curve: per cell, per checkpoint — share of
     non-correct among content-present verdicts (laundered + demoted +
     wrong_source), plus the laundering share alone. `absent` counts in
     coverage, not in error (a policy that never stored the content is
     not lying about its origin — that is the C1 case by construction).
  2. Age-resolved laundering: error by memory age (checkpoint - seed
     session), pooled over checkpoints — the W_t proxy for v0.
  3. Category totals per cell.
Output: prints tables + writes runs/summary.csv (long format).
"""
import csv
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")

ERROR_CATS = {"laundered", "demoted", "wrong_source"}


def load():
    data = {}
    for cell in sorted(os.listdir(RUNS)):
        fp = os.path.join(RUNS, cell, "verdicts.csv")
        if os.path.isdir(os.path.join(RUNS, cell)) and os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                data[cell] = list(csv.DictReader(f))
    return data


def attribution_rows(rows):
    return [r for r in rows
            if r["type"] == "attribution" or r["type"].startswith("open.")]


def stat(rows):
    present = [r for r in rows if r["category"] not in
               ("absent", "no_majority")]
    err = [r for r in present if r["category"] in ERROR_CATS]
    laun = [r for r in present if r["category"] == "laundered"]
    return len(rows), len(present), len(err), len(laun)


def main():
    data = load()
    out = []
    print("=== attribution error by checkpoint (err%/laundered% of present; n) ===")
    cells = sorted(data)
    cps = sorted({int(r["checkpoint"]) for rows in data.values()
                  for r in attribution_rows(rows)})
    print(f"{'cell':12s}" + "".join(f"{cp:>16d}" for cp in cps))
    for cell in cells:
        rows = attribution_rows(data[cell])
        line = f"{cell:12s}"
        for cp in cps:
            sub = [r for r in rows if int(r["checkpoint"]) == cp]
            n, p, e, l = stat(sub)
            cellstr = f"{100*e/p:.0f}/{100*l/p:.0f}% n={p}" if p else "—"
            line += f"{cellstr:>16s}"
            out.append([cell, "checkpoint", cp, p, e, l])
        print(line)

    print("\n=== attribution error by memory age (pooled) ===")
    ages = sorted({int(r["age"]) for rows in data.values()
                   for r in attribution_rows(rows) if r["age"] != ""})
    print(f"{'cell':12s}" + "".join(f"{a:>14d}" for a in ages))
    for cell in cells:
        rows = attribution_rows(data[cell])
        line = f"{cell:12s}"
        for a in ages:
            sub = [r for r in rows if r["age"] != "" and int(r["age"]) == a]
            n, p, e, l = stat(sub)
            line += f"{(f'{100*e/p:.0f}% n={p}' if p else '—'):>14s}"
            out.append([cell, "age", a, p, e, l])
        print(line)

    print("\n=== category totals ===")
    for cell in cells:
        cats = defaultdict(int)
        for r in data[cell]:
            cats[r["category"]] += 1
        print(f"{cell:12s} {dict(sorted(cats.items()))}")

    print("\n=== twins + decisions ===")
    for cell in cells:
        for r in data[cell]:
            if r["type"] in ("twin", "decision"):
                print(f"{cell:12s} {r['type']:8s} cp={r['checkpoint']:>2s} "
                      f"-> {r['category']}")

    with open(os.path.join(RUNS, "summary.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "axis", "value", "present", "errors", "laundered"])
        w.writerows(out)


if __name__ == "__main__":
    main()
