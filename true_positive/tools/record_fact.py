"""record_fact: add a grounded fact to the case record.

Design rule (DESIGN.md): a fact enters the record only with a finding
ID and an exact quote from that finding's description. Anything else
is refused.
"""
from __future__ import annotations


def _description(finding):
    return finding.description if hasattr(finding, "description") else finding["description"]


def run(state, ctx, claim: str, finding_id: str, quote: str) -> dict:
    if finding_id not in ctx.findings:
        return {"ok": False, "error": f"unknown finding_id: {finding_id}"}
    if not claim.strip():
        return {"ok": False, "error": "claim is empty"}
    if quote not in _description(ctx.findings[finding_id]):
        return {"ok": False, "error": "quote is not an exact quote from that finding's description"}
    fact = {"claim": claim, "finding_id": finding_id, "quote": quote}
    state.facts.append(fact)
    return {"ok": True, "fact_index": len(state.facts) - 1}

