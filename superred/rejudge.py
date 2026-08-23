#!/usr/bin/env python3
"""Fill or redo verdicts.jsonl for SuperRed cells from runs.jsonl, with the
claim's own judge (spb_claim.judge_run). Idempotent; --force re-judges
every run. Transport hiccups are retried per item; a run that still fails
is written with judge_error=true and counts as non-success.

  python3 rejudge.py [--force] results/minja-guest_chat-haiku-c4i4i3 [...]
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from spb_claim import BY_QUERY, Verdict, judge_run, verdict_record
from spb_target._bench import load_harness


def main(argv: list[str]) -> None:
    force = "--force" in argv
    dirs = [d for d in argv if d != "--force"]
    H = load_harness()
    key = H.load_key()
    for d in dirs:
        rp, vp = os.path.join(d, "runs.jsonl"), os.path.join(d, "verdicts.jsonl")
        if not os.path.exists(rp):
            continue
        if force and os.path.exists(vp):
            os.remove(vp)
        done: set[tuple[str, int]] = set()
        if os.path.exists(vp):
            for line in open(vp, encoding="utf-8"):
                v = json.loads(line)
                done.add((v["task"], v["run"]))
        todo = []
        for line in open(rp, encoding="utf-8"):
            r = json.loads(line)
            spec = BY_QUERY.get(r["victim_query"])  # runs.jsonl carries no task id (v1.2)
            if spec and (spec.tid, r["run"]) not in done:
                todo.append((r, spec))
                done.add((spec.tid, r["run"]))

        def judge(item):
            r, spec = item
            for attempt in range(3):
                try:
                    v, quotes = judge_run(H, key, spec, r["victim_answer"], r["memory"])
                    return verdict_record(spec, r["run"], v, quotes, r["victim_answer"],
                                          rejudged=True)
                except Exception as e:  # noqa: BLE001 — transport (chunked-read ValueError etc.)
                    print(f"  judge retry {attempt + 1}: {type(e).__name__}: {e}"[:160])
            v = Verdict(False, "none", False, "none")
            return verdict_record(spec, r["run"], v, {"answer_quote": "", "memory_quote": ""},
                                  r["victim_answer"], rejudged=True, judge_error=True)

        added = 0
        with open(vp, "a", encoding="utf-8") as out, ThreadPoolExecutor(8) as ex:
            for rec in ex.map(judge, todo):
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                added += 1
        print(f"{os.path.basename(d)}: +{added} verdicts")


if __name__ == "__main__":
    main(sys.argv[1:])
