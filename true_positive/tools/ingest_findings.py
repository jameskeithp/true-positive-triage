"""ingest_findings: load an incident's findings into the tool context.

Sample mode reads data/sample_findings.json. The incident (id and
finding_ids) comes from the existing pipeline output in main.py.
Live AWS sources wire in here later without changing the loop.
"""
from __future__ import annotations

import json


def run(state, ctx, incident_id: str, finding_ids: list, source: str = "sample",
        path: str = "data/sample_findings.json") -> dict:
    if source != "sample":
        return {"ok": False, "error": f"source not wired yet: {source}"}
    data = json.load(open(path))
    items = data["findings"] if isinstance(data, dict) else data
    by_id = {f["id"]: f for f in items}
    missing = [fid for fid in finding_ids if fid not in by_id]
    if missing:
        return {"ok": False, "error": f"findings not found: {missing}"}
    for fid in finding_ids:
        ctx.findings[fid] = by_id[fid]
    state.incident_id = incident_id
    return {"ok": True, "incident_id": incident_id, "findings": finding_ids}

