"""draft_runbook: record the runbook draft. Drafting only; nothing executes."""
from __future__ import annotations


def run(state, ctx, text: str) -> dict:
    if not text.strip():
        return {"ok": False, "error": "runbook text is empty"}
    state.runbook_draft = text
    return {"ok": True, "chars": len(text)}

