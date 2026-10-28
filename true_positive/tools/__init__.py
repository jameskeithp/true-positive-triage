"""Tool registry: one module per tool, one call per turn."""
from __future__ import annotations

from dataclasses import dataclass, field

from . import record_fact, set_checklist, ingest_findings, draft_runbook, request_human_input, file_report


@dataclass
class ToolContext:
    findings: dict = field(default_factory=dict)   # finding_id -> Finding (or dict)


TOOLS = {
    "record_fact": record_fact.run,
    "set_checklist": set_checklist.run,
    "ingest_findings": ingest_findings.run,
    "draft_runbook": draft_runbook.run,
    "request_human_input": request_human_input.run,
    "file_report": file_report.run,    
}


def dispatch(name: str, state, ctx: ToolContext, args: dict) -> dict:
    fn = TOOLS.get(name)
    if fn is None:
        return {"ok": False, "error": f"unknown tool: {name}"}
    try:
        return fn(state, ctx, **args)
    except TypeError as e:
        return {"ok": False, "error": f"bad arguments for {name}: {e}"}

