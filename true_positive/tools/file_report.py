"""file_report: file the incident report, but only if verification passes.

Checks (all must pass):
- checklist exists and has no open items; settled items point at real facts
- checklist covers every reference kind (see coverage.py); a missing
  kind refuses the filing, naming only the kind to the model
- a runbook draft exists
- the report cites at least one fact, and every citation is a real fact
- every recorded fact still traces to an exact quote in its finding
A failed check refuses the filing with reasons. Three refusals escalate
to a human. A filed report is pending approval; nothing executes. The
filed report carries the checklist coverage percentage for the human
reviewer.
"""
from __future__ import annotations

from ..coverage import coverage_pct, missing_kinds


def _description(finding):
    return finding.description if hasattr(finding, "description") else finding["description"]


def run(state, ctx, summary: str, citations: list) -> dict:
    reasons = []
    if not state.checklist:
        reasons.append("checklist is empty")
    for it in state.checklist:
        if it["status"] == "open":
            reasons.append(f"checklist item still open: {it['item']}")
        elif it["status"] == "settled":
            f = it["fact"]
            if f is None or not (0 <= f < len(state.facts)):
                reasons.append(f"checklist item settled without a valid fact: {it['item']}")
    for kind in missing_kinds(state.checklist):
        reasons.append(f"checklist does not cover: {kind}")
    if not state.runbook_draft:
        reasons.append("no runbook draft recorded")
    if not citations:
        reasons.append("report cites no facts")
    for c in citations or []:
        if not (0 <= c < len(state.facts)):
            reasons.append(f"citation {c} is not a recorded fact")
    for i, fact in enumerate(state.facts):
        finding = ctx.findings.get(fact["finding_id"])
        if finding is None:
            reasons.append(f"fact {i} references unknown finding {fact['finding_id']}")
        elif fact["quote"] not in _description(finding):
            reasons.append(f"fact {i} quote no longer matches its finding")
    if reasons:
        state.file_attempts += 1
        if state.file_attempts >= 3:
            state.status = "escalated"
            return {"ok": False, "escalated": True, "reasons": reasons}
        return {"ok": False, "reasons": reasons}
    state.report = {"summary": summary, "citations": citations,
                    "runbook": state.runbook_draft, "status": "pending_approval",
                    "coverage_pct": coverage_pct(state.checklist)}
    state.status = "filed"
    return {"ok": True, "report_status": "pending_approval"}
