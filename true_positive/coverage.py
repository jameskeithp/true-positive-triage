"""Checklist coverage: the reference kinds a complete triage answers.

Coverage is measured in code at exactly two checkpoints (set_checklist
and file_report). The percentage is for the human reviewer; feedback
to the model names only the missing kinds, never the percentage.
"""
from __future__ import annotations

KINDS = (
    "affected_resource",
    "severity_rationale",
    "public_exposure",
    "credential_abuse",
    "timeline",
    "containment",
    "remediation",
    "verification",
    "evidence_gaps",
)


def covered_kinds(checklist) -> set:
    return {it.get("kind") for it in checklist
            if it.get("status") in ("settled", "na") and it.get("kind")}


def missing_kinds(checklist) -> list:
    covered = covered_kinds(checklist)
    return [k for k in KINDS if k not in covered]


def coverage_pct(checklist) -> int:
    return round(100 * len(covered_kinds(checklist)) / len(KINDS))
