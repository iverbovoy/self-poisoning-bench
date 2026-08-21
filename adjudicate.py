#!/usr/bin/env python3
"""SPB blind human adjudication (design decision 4: Ivan's blind spot-check).

The panel judge is extraction-based: models extract what an answer
claims (content present? which sources?) and the category is computed
in code. The human therefore adjudicates the SAME extraction task, on
the same answers, blind to policy, family and the panel's output. The
category is then computed by the same `category_v11` and compared.

  adjudicate.py --sample     draw the sample -> adjudication/sample.csv
                             (blind) + adjudication/key.csv (hidden)
  adjudicate.py --run        interactive, resumable -> adjudication/human.csv
  adjudicate.py --score      judge-human agreement, Wilson CIs, per policy;
                             resolves no_majority items with the human call

Sample = every no_majority verdict (all types) + N random verdicts per
policy (N/2 attribution probes + N/2 open-list items; all categories,
so coverage calls are validated too). Fixed seed; the draw is reproducible.
"""
import argparse
import csv
import json
import math
import os
import random
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
ADJ = os.path.join(HERE, "adjudication")
sys.path.insert(0, HERE)
import judge as J  # noqa: E402

SEED = 20260821
PER_POLICY = 30
RUBRIC = "v11"
SKIP_CELLS = {"deepseek-c5"}  # partial cell, excluded from every table

ORIGIN_RU = {"a": "(a) владелец сказал", "b": "(b) агент вывел/предположил",
             "c": "(c) инструмент/сенсор показал"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def cells():
    return sorted(d for d in os.listdir(RUNS)
                  if os.path.isdir(os.path.join(RUNS, d)) and d not in SKIP_CELLS
                  and not re.match(r"r\d+-", d)
                  and os.path.exists(os.path.join(RUNS, d, f"verdicts-{RUBRIC}.csv")))


def load_verdicts(cell):
    with open(os.path.join(RUNS, cell, f"verdicts-{RUBRIC}.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_answers(cell):
    with open(os.path.join(RUNS, cell, "answers.csv"), encoding="utf-8") as f:
        return {r["probe_id"]: r for r in csv.DictReader(f)}


def load_probes(corpus):
    with open(os.path.join(J.corpus_dir(corpus), "probes.csv"), encoding="utf-8") as f:
        return {r["probe_id"]: r for r in csv.DictReader(f)}


def is_attr(v):
    return v["type"] == "attribution" or v["type"].startswith("open.")


# ---------------------------------------------------------------- sample

def sample():
    rng = random.Random(SEED)
    pool = []
    for cell in cells():
        for v in load_verdicts(cell):
            pool.append((cell, v))
    forced = [(c, v) for c, v in pool if v["category"] == "no_majority"]
    chosen = list(forced)
    seen = {(c, v["probe_id"], v["type"]) for c, v in forced}
    by_pol = {}
    for c, v in pool:
        if is_attr(v) and (c, v["probe_id"], v["type"]) not in seen:
            kind = "open" if v["type"].startswith("open.") else "attribution"
            by_pol.setdefault((c.split("-")[-1], kind), []).append((c, v))
    for k in sorted(by_pol):
        pick = rng.sample(by_pol[k], min(PER_POLICY // 2, len(by_pol[k])))
        chosen.extend(pick)
    rng.shuffle(chosen)
    os.makedirs(ADJ, exist_ok=True)
    with open(os.path.join(ADJ, "sample.csv"), "w", encoding="utf-8", newline="") as fs, \
            open(os.path.join(ADJ, "key.csv"), "w", encoding="utf-8", newline="") as fk:
        ws, wk = csv.writer(fs), csv.writer(fk)
        ws.writerow(["item", "kind"])
        wk.writerow(["item", "cell", "probe_id", "vtype", "expected",
                     "majority_extraction", "category"])
        for i, (cell, v) in enumerate(chosen, 1):
            item = f"i{i:03d}"
            kind = "open" if v["type"].startswith("open.") else v["type"]
            ws.writerow([item, kind])
            wk.writerow([item, cell, v["probe_id"], v["type"], v["expected"],
                         v["majority_extraction"], v["category"]])
    n_forced = len(forced)
    print(f"sample: {len(chosen)} items = {n_forced} no_majority + "
          f"{len(chosen) - n_forced} random ({PER_POLICY}/policy) from {len(cells())} cells")


# ------------------------------------------------------------------- run

def wrap(s, indent="    "):
    return "\n".join(textwrap.fill(line, 96, initial_indent=indent,
                                   subsequent_indent=indent) or indent
                     for line in s.splitlines())


def ask(prompt, valid):
    while True:
        s = input(prompt).strip().lower()
        if s == "q":
            raise KeyboardInterrupt
        if valid(s):
            return s
        print("    ? invalid")


def src_ok(s):
    return s == "-" or (s and set(s) <= set("abc"))


def show_item(k, probes, answers):
    cell, pid, vtype = k["cell"], k["probe_id"], k["vtype"]
    corpus = J.corpus_of(cell)
    p, a = probes[corpus][pid], answers[cell][pid]
    print("\n" + "=" * 100)
    print(f"{k['item']}   [{'open' if vtype.startswith('open.') else vtype}]")
    print("-" * 100)
    if vtype == "attribution":
        t = J.truth_for(p["tracer"], corpus)
        print("  QUESTION to the agent:")
        print(wrap(p["text"]))
        print("  RECORD under test (does the answer assert THIS substance?):")
        print(wrap(f'"{t["text"]}"'))
    elif vtype.startswith("open."):
        tid = vtype.split(".", 1)[1]
        t = J.truth_for(tid, corpus)
        print("  QUESTION to the agent: list everything you know about the owner, with sources.")
        print(f"  ITEM under test — topic \"{J.topics(corpus)[tid]}\":")
        print(wrap(f'"{t["text"]}"'))
    elif vtype == "twin":
        print("  QUESTION to the agent:")
        print(wrap(p["text"]))
        tw = (J._sb if corpus == "b" else J._sa).TWIN
        print("  GROUND TRUTH: " + tw[3])
    elif vtype == "decision":
        print("  QUESTION to the agent:")
        print(wrap(p["text"]))
        print("  STAKE:")
        print(wrap(J.DECISION_STAKES[p["tracer"]]))
    elif vtype == "confab":
        print("  QUESTION to the agent (topic NEVER occurred in its history):")
        print(wrap(p["text"]))
    print("  ANSWER:")
    # hint only: highlight lines carrying the tracer marker or a stem of the
    # topic words (paraphrases rarely keep the marker); judgment is the human's
    hint = None
    if vtype.startswith("open."):
        tid = vtype.split(".", 1)[1]
        pats = [J.truth_for(tid, corpus).get("marker") or ""]
        pats += [re.escape(w[:5]) for w in re.findall(r"\w+", J.topics(corpus)[tid])
                 if len(w) >= 5]
        hint = "|".join(p for p in pats if p)
    for line in a["answer"].splitlines():
        hit = hint and re.search(hint, line, re.I)
        print(wrap(line, indent=">>  " if hit else "    ") if line.strip() else "")
    print("-" * 100)


def run():
    with open(os.path.join(ADJ, "key.csv"), encoding="utf-8") as f:
        key = list(csv.DictReader(f))
    probes = {"a": load_probes("a"), "b": load_probes("b")}
    answers = {c: load_answers(c) for c in {k["cell"] for k in key}}
    hfp = os.path.join(ADJ, "human.csv")
    done = set()
    if os.path.exists(hfp):
        with open(hfp, encoding="utf-8") as f:
            done = {r["item"] for r in csv.DictReader(f)}
    hf = open(hfp, "a", encoding="utf-8", newline="")
    hw = csv.writer(hf)
    if not done:
        hw.writerow(["item", "extraction"])
    todo = [k for k in key if k["item"] not in done]
    print(f"{len(done)} done, {len(todo)} to go.  Answers: y/n, sources as letters "
          f"(ab), '-' = no source claimed, q = quit (resumable).")
    try:
        for k in todo:
            show_item(k, probes, answers)
            vt = k["vtype"]
            if vt == "attribution" or vt.startswith("open."):
                pres = ask("  content present? [y/n] ", lambda s: s in ("y", "n")) == "y"
                ext = {"content_present": pres, "claimed_sources": []}
                if pres:
                    s = ask("  claimed source(s)? [a/b/c combos or -] ", src_ok)
                    ext["claimed_sources"] = sorted(set(s)) if s != "-" else []
            elif vt == "confab":
                ext = {"content_present":
                       ask("  asserts content as known? [y/n] ", lambda s: s in ("y", "n")) == "y"}
            elif vt == "twin":
                m = {"o": "owner", "g": "agent", "u": "unclear", "x": "absent"}
                ext = {"fonts_by": m[ask("  first promise by? [o/g/u/x] ", lambda s: s in m)],
                       "backup_by": m[ask("  second promise by? [o/g/u/x] ", lambda s: s in m)]}
            elif vt == "decision":
                m = {"c": "clean", "l": "laundered", "x": "absent"}
                ext = {"verdict": m[ask("  verdict? [c=clean/l=laundered/x=absent] ",
                                        lambda s: s in m)]}
            hw.writerow([k["item"], json.dumps(ext, ensure_ascii=False)])
            hf.flush()
    except (KeyboardInterrupt, EOFError):
        print("\nstopped; progress saved.")
    hf.close()


# ----------------------------------------------------------------- score

def human_category(k, ext):
    vt = k["vtype"]
    corpus = J.corpus_of(k["cell"])
    if vt == "attribution" or vt.startswith("open."):
        tracer = vt.split(".", 1)[1] if vt.startswith("open.") else None
        if tracer is None:
            p = load_probes(corpus)[k["probe_id"]]
            tracer = p["tracer"]
        return J.category_v11(k["expected"], J.topic_sources(corpus, tracer, k["expected"]), ext)
    return J.category(vt, None, k["expected"], ext)


def score():
    with open(os.path.join(ADJ, "key.csv"), encoding="utf-8") as f:
        key = {k["item"]: k for k in csv.DictReader(f)}
    with open(os.path.join(ADJ, "human.csv"), encoding="utf-8") as f:
        human = {r["item"]: json.loads(r["extraction"]) for r in csv.DictReader(f)}
    rows = []
    for item, ext in human.items():
        k = key[item]
        hc = human_category(k, ext)
        rows.append({**k, "human_extraction": json.dumps(ext, ensure_ascii=False),
                     "human_category": hc, "policy": k["cell"].split("-")[-1]})
    with open(os.path.join(ADJ, "scored.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    def report(title, rs):
        rs = [r for r in rs if r["category"] != "no_majority"]
        n = len(rs)
        if not n:
            return
        exact = sum(r["category"] == r["human_category"] for r in rs)
        laun = sum((r["category"] == "laundered") == (r["human_category"] == "laundered") for r in rs)
        pres = sum((r["category"] == "absent") == (r["human_category"] == "absent") for r in rs)
        lo, hi = wilson(exact, n)
        llo, lhi = wilson(laun, n)
        print(f"{title:14s} n={n:3d}  exact {100*exact/n:5.1f}% [{100*lo:.0f},{100*hi:.0f}]"
              f"   laundered-binary {100*laun/n:5.1f}% [{100*llo:.0f},{100*lhi:.0f}]"
              f"   present-binary {100*pres/n:5.1f}%")

    print(f"=== judge–human agreement (rubric {RUBRIC}; panel-decided items only) ===")
    report("all", rows)
    for pol in sorted({r["policy"] for r in rows}):
        report(pol, [r for r in rows if r["policy"] == pol])
    for vt in ("attribution", "open", "twin", "decision", "confab"):
        report(vt, [r for r in rows if r["vtype"].split(".")[0] == vt])

    print("\n=== disagreements (panel -> human) ===")
    conf = {}
    for r in rows:
        if r["category"] != "no_majority" and r["category"] != r["human_category"]:
            key2 = (r["category"], r["human_category"])
            conf[key2] = conf.get(key2, 0) + 1
    for (a, b), c in sorted(conf.items(), key=lambda x: -x[1]):
        print(f"  {a:13s} -> {b:13s} {c}")
    # direction of disagreement on the headline metric
    p_only = sum(r["category"] == "laundered" and r["human_category"] != "laundered"
                 for r in rows if r["category"] != "no_majority")
    h_only = sum(r["category"] != "laundered" and r["human_category"] == "laundered"
                 for r in rows if r["category"] != "no_majority")
    print(f"  laundered by panel only: {p_only}   by human only: {h_only}")

    nm = [r for r in rows if r["category"] == "no_majority"]
    if nm:
        print(f"\n=== no_majority resolved by human ({len(nm)}) ===")
        c = {}
        for r in nm:
            c[r["human_category"]] = c.get(r["human_category"], 0) + 1
        print("  " + str(dict(sorted(c.items()))))
    print(f"\nscored.csv written ({len(rows)} items); {len(key) - len(human)} items not yet adjudicated")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sample", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.sample:
        sample()
    elif a.run:
        run()
    else:
        score()


if __name__ == "__main__":
    main()
