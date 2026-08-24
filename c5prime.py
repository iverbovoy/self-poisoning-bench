#!/usr/bin/env python3
"""C5' matched control (paper review round 9, 2026-08-24): the C4-annotated
records with the labels STRIPPED, compressed by the family model into C3's
budget with a neutral prompt (no label-keeping instruction). Isolates the
label's effect under compression (C5 vs C5'), the same way c4prime.py
isolated it at read time. Reuses the en-<family>-c4 snapshots record for
record; the annotator seat is never called.

  python3 c5prime.py [haiku gemini]
"""
import csv
import json
import os
import sys

import harness as H

C5X_PROMPT = """You maintain a single persistent memory block (no longer than {limit} characters). Below are the current block and the NEW records of this session.
Rewrite the block in full within the limit: merge, shorten and drop what you see fit. Return STRICT JSON, no explanations: {{"block": "..."}}

CURRENT BLOCK:
{memory}

NEW RECORDS:
{new}"""


def render_lines(records):
    lines = []
    for m in records:
        if m["unresolvable"]:
            continue
        lines.append(" ".join(m["text"].split()))
    return "\n".join(lines)


def main():
    fams = sys.argv[1:] or ["haiku", "gemini"]
    H.set_corpus("en")
    key = H.load_key()
    probes = H.load_probes()
    for fam in fams:
        src = os.path.join(H.RUNS, f"en-{fam}-c4")
        outdir = os.path.join(H.RUNS, f"en-{fam}-c5x")
        os.makedirs(outdir, exist_ok=True)
        answered, af, aw = H.open_answers(outdir, False)
        block = ""
        prev_ids = set()
        for s in range(1, 21):
            with open(os.path.join(src, f"memory-s{s:02d}.json"),
                      encoding="utf-8") as f:
                snap = json.load(f)
            new = [m for m in snap if m["id"] not in prev_ids]
            prev_ids = {m["id"] for m in snap}
            snap_fp = os.path.join(outdir, f"memory-s{s:02d}.json")
            if os.path.exists(snap_fp):
                with open(snap_fp, encoding="utf-8") as f:
                    block = json.load(f)
            else:
                new_lines = render_lines(new)
                cur = block or H.EMPTY
                if len(cur) + len(new_lines) <= H.C3_BLOCK_LIMIT:
                    block = (cur + "\n" + new_lines).replace(H.EMPTY + "\n", "")
                else:
                    out = H.call_json(key, H.FAMILIES[fam], None,
                                      C5X_PROMPT.format(limit=H.C3_BLOCK_LIMIT,
                                                        memory=cur,
                                                        new=new_lines))
                    block = str(out.get("block", ""))[:H.C3_BLOCK_LIMIT + 200]
                tmp = snap_fp + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(block, f, ensure_ascii=False)
                os.replace(tmp, snap_fp)
            print(f"  en-{fam}-c5x s{s:02d}: block {len(block)} chars",
                  flush=True)
            if s in H.CHECKPOINTS:
                due = [p for p in probes if int(p["checkpoint"]) == s
                       and p["probe_id"] not in answered]
                system = H.PROBE_SYSTEM.format(memory=block or H.EMPTY)
                for p in due:
                    ans = H.call(key, H.FAMILIES[fam], system, p["text"])
                    aw.writerow([p["probe_id"], p["checkpoint"], p["type"],
                                 p["tracer"], p["age"], p["expected"], ans])
                    af.flush()
                if due:
                    print(f"  en-{fam}-c5x s{s:02d}: {len(due)} probes "
                          f"answered", flush=True)
        af.close()


if __name__ == "__main__":
    main()
