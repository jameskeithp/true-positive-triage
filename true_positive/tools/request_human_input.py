"""request_human_input: pause the run and ask the human. A first-class state."""
from __future__ import annotations


def run(state, ctx, question: str) -> dict:
    state.status = "needs_input"
    return {"ok": True, "question": question}

