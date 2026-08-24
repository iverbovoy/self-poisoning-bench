#!/usr/bin/env python3
"""SPB x SuperRed: delta-ASR sweep (invariants off vs on).

Grid: channel {guest_chat, documents} x policy {c2, c3 | c4, c5} x family
{haiku, gemini} x attacker {passthrough (direct, one shot), minja}.
One Controller = one threat model = (scope=channel, attacker LLM, USD cap).

  ./venv/bin/python evals/spbench/superred/run_superred.py \\
      --channel guest_chat --policy c2 c4 --family haiku --attacker minja

Results tree: evals/spbench/superred/results/<attacker>-<channel>-<family>-<policy>/
(SuperRed's own resumable format; `superred serve results/` for the dashboard)
plus runs.jsonl per cell (every session: injected text, memory, victim answer).
summary.csv is appended one line per cell: ASR and the demoted rate.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import os

from superred.core.controller import Controller, TargetFactory
from superred.core.types.llm import LLMConfig

from spb_claim import all_tasks
from spb_target import CHANNEL_TAGS, SPBTarget
from spb_target._bench import load_harness

HERE = os.path.dirname(os.path.abspath(__file__))
H = load_harness()
RESULTS = os.path.join(HERE, "results")
OPENROUTER = "https://openrouter.ai/api/v1"
ATTACKER_MODEL = "openrouter/anthropic/claude-haiku-4.5"  # attacker's LLM (litellm id)
SCOPES = CHANNEL_TAGS


def make_optimizer(name, channel, seed=20260821):
    if name == "passthrough":
        from goal_passthrough_optimizer import GoalPassthroughOptimizer
        return GoalPassthroughOptimizer()
    if name == "minja":
        from minja_optimizer import MinjaOptimizer
        return MinjaOptimizer(
            inject_num=3, num_benign=0, test_num=2, random_seed=seed,
            use_llm_scenario_synthesis=True, adaptive=True,
            target_controllable_name=("guest_message" if channel == "guest_chat"
                                      else "document_text"),
            response_observable_names={"response"})
    if name == "muzzle":
        from muzzle_optimizer import MuzzleOptimizer
        return MuzzleOptimizer()
    raise ValueError(name)


async def run_cell(args, channel, policy, family, attacker, key):
    seed_suffix = f"-s{args.seed}" if args.seed != 20260821 else ""
    label = f"{attacker}-{channel}-{family}-{policy}{seed_suffix}"
    cell_dir = os.path.join(RESULTS, label)
    tf = TargetFactory(
        create=lambda: SPBTarget(policy, family, channel, api_key=key,
                                 guest_turns=args.guest_turns, log_dir=cell_dir),
        concurrency=args.concurrency)
    tasks = all_tasks(key, ext=args.ext, r2=args.r2)
    if args.tasks:
        tasks = [t for t in tasks if t.tid in args.tasks]
    ctrl = Controller(
        optimizer_factory=lambda: make_optimizer(attacker, channel, args.seed),
        target_factory=tf,
        security_claim=tasks,
        scope=frozenset({SCOPES[channel]}),
        llm_config=(LLMConfig(model=ATTACKER_MODEL, api_base=OPENROUTER, api_key=key)
                    if attacker != "passthrough" else None),
        task_cost_cap_usd=args.cost_cap,
        max_runs_per_task=args.max_runs,
        include_feedback=True,
        results_dir=cell_dir,
        report="auto",
        attacker_label=attacker, target_label=f"spb-{family}-{policy}",
        claim_label=f"spb8-{channel}")
    res = await ctrl.run()
    n = len(res.task_results)
    succ = sum(1 for t in res.task_results if getattr(t, "success", False))
    # demoted: X reached memory but kept its origin in the final answer
    dem = 0
    for t in res.task_results:
        runs = getattr(t, "runs", None) or []
        last = runs[-1] if runs else None
        ev = getattr(last, "evaluation", None) if last else None
        if ev and ev.sub_scores.get("demoted") and ev.sub_scores["demoted"].value:
            dem += 1
    asr = round(succ / n, 3) if n else None
    print(f"== {label}: tasks {n}, success {succ}, ASR {asr}, demoted {dem}")
    os.makedirs(RESULTS, exist_ok=True)
    fp = os.path.join(RESULTS, "summary.csv")
    new = not os.path.exists(fp)
    with open(fp, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["attacker", "channel", "family", "policy", "tasks",
                        "success", "asr", "demoted"])
        w.writerow([attacker, channel, family,
                    policy + (f"-s{args.seed}" if args.seed != 20260821 else ""),
                    n, succ, asr, dem])


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", nargs="+", choices=list(SCOPES), default=["guest_chat"])
    ap.add_argument("--policy", nargs="+", default=["c2", "c4"])
    ap.add_argument("--family", nargs="+", choices=list(H.FAMILIES), default=["haiku"])
    ap.add_argument("--attacker", nargs="+", choices=["passthrough", "minja", "muzzle"],
                    default=["passthrough"])
    ap.add_argument("--tasks", nargs="*", help="task ids subset, e.g. t1 t2")
    ap.add_argument("--ext", action="store_true", help="16 tasks (TASKS_CORE + TASKS_EXT)")
    ap.add_argument("--r2", action="store_true",
                    help="include the rank-2 task t17 (usually with --tasks t17)")
    ap.add_argument("--seed", type=int, default=20260821, help="MINJA random seed")
    ap.add_argument("--max-runs", type=int, default=10)
    ap.add_argument("--cost-cap", type=float, default=1.0)
    ap.add_argument("--guest-turns", type=int, default=3)
    ap.add_argument("--concurrency", type=int, default=2)
    args = ap.parse_args()
    key = H.load_key()
    for attacker in args.attacker:
        for channel in args.channel:
            for family in args.family:
                for policy in args.policy:
                    await run_cell(args, channel, policy, family, attacker, key)


if __name__ == "__main__":
    asyncio.run(main())
