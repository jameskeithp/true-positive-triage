import json

from .models import Finding


def normalize_severity(source, raw):
    sev = float(raw)
    if source == "securityhub" and sev > 10:
        sev = sev / 10.0
    return round(max(0.0, min(10.0, sev)), 1)


def load_findings(path):
    with open(path) as handle:
        items = json.load(handle)
    findings = []
    for item in items:
        findings.append(Finding(
            id=item["id"],
            source=item["source"],
            type=item["type"],
            title=item["title"],
            description=item["description"],
            severity=normalize_severity(item["source"], item["severity"]),
            resource_type=item.get("resource_type", ""),
            resource_id=item.get("resource_id", ""),
            account_id=item.get("account_id", ""),
            region=item.get("region", ""),
            first_seen=item["first_seen"],
            last_seen=item["last_seen"],
            status=item.get("status", "ACTIVE"),
        ))
    return findings
