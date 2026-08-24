#!/usr/bin/env python3
"""C4 with a cross-family annotator seat (review round 11): the same
attributed-store policy, but path/ground assigned by gemini-3.6-flash
instead of claude-haiku-4.5. Removes the shared-model confound (haiku =
C4 annotator seat AND judge-panel seat) behind the headline 3.1%.

  python3 c4gem.py [haiku gemini]
"""
import sys

import harness as H

H.ANNOTATOR = "google/gemini-3.6-flash"
H.POLICIES["c4g"] = (H.c4_consolidate, H.c4_render, [])


def main():
    fams = sys.argv[1:] or ["haiku", "gemini"]
    H.set_corpus("en")
    key = H.load_key()
    sessions = H.load_sessions()
    probes = H.load_probes()
    for fam in fams:
        H.run_cell(key, fam, "c4g", sessions, probes, 20, False, prefix="en-")


if __name__ == "__main__":
    main()
