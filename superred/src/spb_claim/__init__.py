"""superred Claim for the Self-Poisoning Bench: memory-injection tasks and
three-metric grading (end-to-end ASR, storage promotion, read-side violation)."""
from spb_claim.claim import SPBTask, all_tasks, judge_run, verdict_record
from spb_claim.judge import ANSWER_PROMPT, JUDGE_MODEL, MEMORY_PROMPT, label_of, memory_attribution
from spb_claim.metrics import Verdict, wilson
from spb_claim.tasks import BY_ID, BY_QUERY, TASKS, TASKS_CORE, TASKS_EXT, TaskSpec

__all__ = ["SPBTask", "all_tasks", "judge_run", "verdict_record", "TaskSpec", "TASKS",
           "TASKS_CORE", "TASKS_EXT", "BY_ID", "BY_QUERY", "Verdict", "wilson", "label_of",
           "memory_attribution", "JUDGE_MODEL", "ANSWER_PROMPT", "MEMORY_PROMPT"]
