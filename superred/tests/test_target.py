"""Smoke: one run through the target with a fake LLM and a fake attacker."""
import asyncio

import pytest
from superred.core.types.events import (
    ControllableInjection,
    ControllableNoInjection,
    ControllablePreCallEvent,
)

from spb_target import SPBTarget
from spb_target import target as T


@pytest.fixture
def fake_llm(monkeypatch):
    calls = []

    def call(key, model, system, user, _retries=4, temperature=None):
        calls.append((system or "") + " | " + user[:40])
        return "FAKE REPLY: " + user[:30]

    def call_json(key, model, system, user, retries=2, temperature=None):
        return {"notes": ["FAKE NOTE"], "block": "FAKE BLOCK", "annotations": []}

    H = T.load_harness()
    monkeypatch.setattr(H, "call", call)
    monkeypatch.setattr(H, "call_json", call_json)
    return calls


@pytest.mark.parametrize("policy,channel", [("c2", "guest_chat"), ("c4i4i3", "documents"), ("c2i3", "guest_chat")])
def test_one_run(fake_llm, policy, channel, tmp_path):
    t = SPBTarget(policy, "haiku", channel, api_key="x", log_dir=str(tmp_path))
    t.set_config("victim_query", "What do you do?")
    emitted = []

    async def send_event(ev):
        if isinstance(ev, ControllablePreCallEvent):
            return ControllableInjection(event=ev, controllable=ev.controllable, value="PAYLOAD")
        return ControllableNoInjection(event=ev, controllable=ev.controllable)

    asyncio.run(t.run(emitted.append, send_event))
    assert t.run_no == 1 and t.victim_answer.startswith("FAKE REPLY")
    assert (tmp_path / "runs.jsonl").exists()
    mem = t.query("memory")
    if policy.startswith("c4"):
        assert "[guest said]" in mem or "[from a document]" in mem
        assert "[my reply to a guest" in mem or "[my summary of a document]" in mem
    if t.policy.i3:
        assert any("Rule for using memory" in c for c in fake_llm)
    else:
        assert not any("Rule for using memory" in c for c in fake_llm)
    asyncio.run(t.reset_ephemeral_state())
    assert t.victim_answer == "" and t.run_no == 1  # durable memory, ephemeral answer


def test_decline_is_not_an_error(monkeypatch):
    H = T.load_harness()

    def call(*a, **k):
        raise OSError("empty completion")

    monkeypatch.setattr(H, "call", call)
    t = SPBTarget("c2", "haiku", "guest_chat", api_key="x")
    assert asyncio.run(t._llm(None, "hi")) == T.NO_REPLY
