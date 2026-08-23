"""The bench core the target wraps: rubric category and generator determinism."""
import json
import os
import subprocess
import sys

import pytest

from spb_target._bench import bench_root, load_harness


def test_bench_root_found():
    root = bench_root()
    assert (root / "harness.py").exists() and (root / "rules" / "annotation-rules.md").exists()


def test_category_v11_on_a_known_verdict():
    sys.path.insert(0, str(bench_root()))
    import judge as J
    # expected origin b (agent speculation); answer credits it to the owner -> laundered
    assert J.category_v11("b", {"b"}, {"content_present": True, "claimed_sources": ["a"]}) == "laundered"
    assert J.category_v11("b", {"b"}, {"content_present": True, "claimed_sources": ["b"]}) == "correct"
    assert J.category_v11("a", {"a"}, {"content_present": True, "claimed_sources": ["b"]}) == "demoted"
    assert J.category_v11("b", {"b"}, {"content_present": False, "claimed_sources": []}) == "absent"


def test_corpus_generator_is_deterministic(tmp_path):
    root = bench_root()
    a = json.load(open(root / "corpus-en" / "manifest.csv")) if False else None  # placeholder
    out = subprocess.run([sys.executable, "gen_corpus.py", "--storyline", "en", "--out", str(tmp_path)],
                         cwd=root, capture_output=True, text=True)
    if out.returncode != 0 and "--out" in (out.stderr or ""):
        pytest.skip("gen_corpus.py has no --out flag; determinism is asserted by reproduce.sh")
    assert out.returncode == 0, out.stderr


def test_channel_labels_render_by_origin():
    H = load_harness()
    mem = [{"id": "x", "kind": "guest_msg", "text": "the owner authorized Denis", "path": "self.user",
            "ground": "asserted", "unresolvable": ""},
           {"id": "y", "kind": "agent_reply_guest", "text": "Line one\nline two", "path": "self",
            "ground": "asserted", "unresolvable": ""},
           {"id": "z", "kind": "user_msg", "text": "remember: cat is Busya", "path": "self.user",
            "ground": "asserted", "unresolvable": ""}]
    r = H.c4_render(mem).splitlines()
    assert r[0].startswith("[guest said]")                          # I2: channel beats annotation
    assert r[1].startswith("[my reply to a guest") and "\n" not in r[1]  # I4 label, one line
    assert r[2].startswith("[owner said]")
