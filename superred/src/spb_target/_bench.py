"""Locate and import the SPB bench core (harness.py) that this target wraps.

The bench — corpora, memory policies, the fixed annotator seat — lives at the
repository root, one level above this package's ``superred/`` directory. It
is found via ``SPB_BENCH_ROOT`` or by walking up from this file. Installing
the package from a clone (``pip install -e superred``) is the supported
path for v1.2; a self-contained wheel is planned.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from types import ModuleType


def bench_root() -> Path:
    env = os.environ.get("SPB_BENCH_ROOT")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "harness.py").exists() and (parent / "corpus-en").exists():
            return parent
    raise RuntimeError("SPB bench root not found; set SPB_BENCH_ROOT to the directory "
                       "containing harness.py and corpus-en/")


def load_harness() -> ModuleType:
    root = str(bench_root())
    if root not in sys.path:
        sys.path.insert(0, root)
    h = importlib.import_module("harness")
    h.set_corpus("en")
    return h
