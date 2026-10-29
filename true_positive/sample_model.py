"""SampleModel: a scripted model for sample mode.

Plays a fixed, honest triage of INC-002 (the two correlated GuardDuty
findings) so the full loop runs end to end with no API key. Quotes are
read from the findings themselves, never hard-coded. The checklist
covers all nine reference kinds (coverage.py): kinds the findings
evidence are settled with facts; the rest are na with honest reasons.
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
                {"item": "Affected resource and account identified", "kind": "affected_resource",
                 "status": "settled", "fact": 0},
                {"item": "Credential abuse checked", "kind": "credential_abuse",
                 "status": "settled", "fact": 0},
                {"item": "Public exposure checked", "kind": "public_exposure",
                 "status": "settled", "fact": 0},
                {"item": "Severity and score rationale", "kind": "severity_rationale",
                 "status": "na",
                 "reason": "Score is computed by deterministic code from the finding severities and carried with the incident."},
                {"item": "Timeline", "kind": "timeline",
                 "status": "na",
                 "reason": "First and last seen are carried on each finding at ingest (Oct 27: gd-2001 09:12-09:58Z, gd-2002 10:20-10:21Z)."},
                {"item": "Containment step drafted", "kind": "containment",
                 "status": "na", "reason": "Covered by runbook step 1: isolate the affected resource."},
                {"item": "Remediation step drafted", "kind": "remediation",
                 "status": "na", "reason": "Covered by runbook step 2: revoke the abused credentials."},
                {"item": "Verification step drafted", "kind": "verification",
                 "status": "na", "reason": "Covered by runbook step 4: confirm no second resource is affected."},
                {"item": "Evidence gaps", "kind": "evidence_gaps",
                 "status": "na", "reason": "None. Both findings are recorded as facts with exact quotes."},
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
