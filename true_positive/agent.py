"""The True Positive agent loop.

One tool call per turn. State is saved after every turn. A failed model
call pauses the run (resumable) instead of crashing it. Hitting the turn
cap without filing escalates to a human.

Tool allowlist: only the registered tools may run. A call naming any
other tool is discarded, logged in the run history with its turn, and
the loop continues; the model sees the refusal on its next turn.

Claims check: when a claims judge is supplied, a report that passes
file_report's deterministic gate is judged once more for whether each
quote supports its claim (see claims_check.py).
"""
from __future__ import annotations

from .claims_check import apply_claims_verdict
from .state import RunState
from .tools import TOOLS, ToolContext, dispatch

SYSTEM_PROMPT = (
    "You are True Positive, a security triage agent working one incident. "
    "Call exactly one tool per turn. Ground every fact with record_fact, "
    "using an exact quote from the finding. Settle every checklist item "
    "with a fact or mark it na with a reason. Draft the runbook, then "
    "file the report. Code verifies the filing, not you."
)


def run_loop(state: RunState, ctx: ToolContext, model, claims_judge=None) -> RunState:
    while state.status == "running":
        if state.turn >= state.max_turns:
            state.status = "escalated"
            state.history.append({"turn": state.turn, "event": "turn_cap_reached"})
            state.save()
            break
        try:
            call = model.next_call(state, ctx)
        except Exception as e:
            state.status = "paused"
            state.history.append({"turn": state.turn, "event": "model_error", "error": str(e)})
            state.save()
            break
        state.turn += 1
        if call["tool"] not in TOOLS:
            state.history.append({"turn": state.turn, "tool": call["tool"],
                                  "args": call.get("args", {}),
                                  "result": {"ok": False, "discarded": True,
                                             "error": f"tool not on the allowlist: {call['tool']}"}})
            state.save()
            continue
        result = dispatch(call["tool"], state, ctx, call.get("args", {}))
        if call["tool"] == "file_report" and result.get("ok") and claims_judge is not None:
            result = apply_claims_verdict(state, result, claims_judge)
        state.history.append({"turn": state.turn, "tool": call["tool"],
                              "args": call.get("args", {}), "result": result})
        state.save()
    return state
