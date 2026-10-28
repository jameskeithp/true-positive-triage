"""SampleModel: a scripted model for sample mode.

Plays a fixed, honest triage of INC-002 (the two correlated GuardDuty
findings) so the full loop runs end to end with no API key. Quotes are
read from the findings themselves, never hard-coded.
"""
from __future__ import annotations


class SampleModel:
    def __init__(self, incident_id="INC-002", finding_ids=("gd-2001", "gd-2002")):
        self.incident_id = incident_id
        self.finding_ids = list(finding_ids)
        self.step = 0

    def next_call(self, state, ctx):
        self.step += 1
        if self.step == 1:
            return {"tool": "ingest_findings",
                    "args": {"incident_id": self.incident_id, "finding_ids": self.finding_ids}}
        if self.step in (2, 3):
            fid = self.finding_ids[self.step - 2]
            f = ctx.findings[fid]
            desc = f["description"] if isinstance(f, dict) else f.description
            return {"tool": "record_fact",
                    "args": {"claim": f"Evidence from {fid}", "finding_id": fid, "quote": desc[:80]}}
        if self.step == 4:
            return {"tool": "set_checklist", "args": {"items": [
                {"item": "Primary finding evidenced", "status": "settled", "fact": 0},
                {"item": "Correlated finding evidenced", "status": "settled", "fact": 1},
            ]}}
        if self.step == 5:
            return {"tool": "draft_runbook", "args": {"text":
                    "1. Isolate the affected resource.\n"
                    "2. Revoke the abused credentials.\n"
                    "3. Review access logs for the incident window.\n"
                    "4. Confirm no second resource is affected."}}
        return {"tool": "file_report", "args": {
            "summary": "Correlated credential abuse incident, evidenced by two findings.",
            "citations": [0, 1]}}

