#!/usr/bin/env python3
"""C4' control cell (review round 8, 2026-08-24): the exact C4 memory —
snapshots copied byte-identically from en-<family>-c4 — rendered with the
source labels STRIPPED at answer time. Separates the label itself from every
other effect of the annotation pipeline (Result 3 control). The annotator is
never called: run_cell loads the copied snapshots; only probe answering is new.

  python3 c4prime.py [haiku gemini]
"""
import os
import shutil
import sys

import harness as H


def c4x_render(memory):
    lines = []
    for m in memory:
        if m["unresolvable"]:
            continue
        if m.get("kind") in H.CHANNEL_LABEL:
            lines.append(" ".join(m["text"].split()))
            continue
        lines.append(m["text"])
    return "\n".join(lines) if lines else H.EMPTY


H.POLICIES["c4x"] = (H.c4_consolidate, c4x_render, [])


def main():
    fams = sys.argv[1:] or ["haiku", "gemini"]
    H.set_corpus("en")
    key = H.load_key()
    sessions = H.load_sessions()
    probes = H.load_probes()
    for fam in fams:
        src = os.path.join(H.RUNS, f"en-{fam}-c4")
        dst = os.path.join(H.RUNS, f"en-{fam}-c4x")
        os.makedirs(dst, exist_ok=True)
        for fn in sorted(os.listdir(src)):
            if fn.startswith("memory-s") and \
                    not os.path.exists(os.path.join(dst, fn)):
                shutil.copy(os.path.join(src, fn), os.path.join(dst, fn))
        H.run_cell(key, fam, "c4x", sessions, probes, 20, False, prefix="en-")


if __name__ == "__main__":
    main()
