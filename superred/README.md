# superred-spb

The Self-Poisoning Bench home-assistant agent as a [superred](https://superred.simonsure.com)
**Target** (`spb_target`) and its memory-injection tasks with three-metric grading as a
**Claim** (`spb_claim`). Specification: `system_specification.md`. Paper: Section 7 of
*Rank-Bounded Agent Memory* (doi:10.5281/zenodo.21994003).

```bash
pip install -e superred            # from a clone of self-poisoning-bench
export OPENROUTER_API_KEY=...
python3 superred/run_superred.py --attacker minja --channel guest_chat documents \
    --family haiku gemini gpt deepseek --policy c2 c2i3 c4 c4i4 c4i4i3 --ext
python3 superred/rejudge.py --force superred/results/minja-*   # unified verdicts
python3 superred/report.py                                       # results/REPORT.md
```

```python
from spb_target import SPBTarget, GUEST_CHAT_TAG
from spb_claim import all_tasks
```

The target wraps the bench core one directory up (`harness.py`, corpora, the fixed
annotator seat); it is located automatically from a clone or via `SPB_BENCH_ROOT`.
