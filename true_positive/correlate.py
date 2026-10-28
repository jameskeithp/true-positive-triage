from datetime import datetime, timedelta

from .models import Incident

WINDOW = timedelta(hours=24)


def _ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _family(finding_type):
    head = finding_type.split(":")[0]
    return head.split("/")[0]


def _key(finding):
    if finding.resource_id:
        return (finding.account_id, "resource", finding.resource_id)
    return (finding.account_id, "family", _family(finding.type))


def correlate(findings):
    incidents = []
    by_key = {}
    for finding in sorted(findings, key=lambda f: _ts(f.last_seen)):
        key = _key(finding)
        target = None
        for candidate in by_key.get(key, []):
            if _ts(finding.last_seen) - _ts(candidate.last_seen) <= WINDOW:
                target = candidate
                break
        if target is None:
            target = Incident(
                id="INC-%03d" % (len(incidents) + 1),
                account_id=finding.account_id,
            )
            incidents.append(target)
            by_key.setdefault(key, []).append(target)
        target.finding_ids.append(finding.id)
        if finding.resource_id and finding.resource_id not in target.resources:
            target.resources.append(finding.resource_id)
        if not target.first_seen or finding.first_seen < target.first_seen:
            target.first_seen = finding.first_seen
        if finding.last_seen > target.last_seen:
            target.last_seen = finding.last_seen
    return incidents
