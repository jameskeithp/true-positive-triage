"""Claims check: layer-2 verification after the deterministic gate.

The deterministic checks in file_report prove each quote EXISTS in its
finding. They cannot prove the quote SUPPORTS the claim. When a claims
judge is wired (live mode), a separate model call judges exactly that:
one entry per recorded fact, claim plus quote, nothing else. A claim
the judge calls unsupported refuses the filing: the refused draft and
the reasons are saved beside the run file as evidence, and the refusal
counts toward the same 3-refusals-then-escalate rule. If the judge
itself errors, the filing stands but is flagged unavailable, so the
human reviewer knows the second layer never ran.
"""
from __future__ import annotations

import json
from pathlib import Path


def save_refused_draft(state, report, reasons) -> str:
    path = Path("runs") / f"{state.run_id}-refused-{state.file_attempts + 1}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(
        {"run_id": state.run_id, "incident_id": state.incident_id,
         "report": report, "refusal_reasons": reasons}, indent=2))
    return str(path)


def apply_claims_verdict(state, result, judge) -> dict:
    """Judge the just-filed report's claims. Returns the final result."""
    try:
        unsupported = judge(list(state.facts))
    except Exception as e:
        return {**result, "claims_check": f"unavailable: {e}"}
    if not unsupported:
        return {**result, "claims_check": "passed"}
    reasons = [f"claims check: claim {i} is not supported by its quote"
               for i in unsupported]
    draft_path = save_refused_draft(state, state.report, reasons)
    state.report = None
    state.file_attempts += 1
    if state.file_attempts >= 3:
        state.status = "escalated"
    else:
        state.status = "running"
    return {"ok": False, "claims_check": "failed", "reasons": reasons,
            "refused_draft": draft_path}
