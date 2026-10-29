"""set_checklist: replace the verification checklist for the incident.

Each item: {"item": str, "kind": <coverage kind or None>,
"status": "open" | "settled" | "na",
"fact": <index into state.facts or None>, "reason": str or None}
An item is settled only by pointing at a recorded fact; it is na only
with a reason. Items carry a coverage kind (see coverage.py); the
result names any kinds still missing. file_report enforces coverage.
"""
from __future__ import annotations

from ..coverage import KINDS, missing_kinds

STATUSES = ("open", "settled", "na")


def run(state, ctx, items: list) -> dict:
    cleaned = []
    for it in items:
        status = it.get("status", "open")
        if status not in STATUSES:
            return {"ok": False, "error": f"bad status: {status}"}
        kind = it.get("kind")
        if kind is not None and kind not in KINDS:
            return {"ok": False, "error": f"unknown checklist kind: {kind}"}
        fact = it.get("fact")
        if status == "settled" and (fact is None or not (0 <= fact < len(state.facts))):
            return {"ok": False, "error": "settled item must point at a recorded fact index"}
        if status == "na" and not (it.get("reason") or "").strip():
            return {"ok": False, "error": "na item must carry a reason"}
        cleaned.append({"item": it["item"], "kind": kind, "status": status,
                        "fact": fact, "reason": it.get("reason")})
    state.checklist = cleaned
    return {"ok": True, "items": len(cleaned), "missing_kinds": missing_kinds(cleaned)}
