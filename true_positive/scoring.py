PUBLIC_HINTS = ["0.0.0.0/0", "public", "anonymous", "unrestricted"]
CREDENTIAL_HINTS = ["credential", "root", "access key", "exfiltration"]


def _matches(finding, hints):
    text = (finding.type + " " + finding.description).lower()
    return any(hint in text for hint in hints)


def score_incident(incident, findings_by_id):
    findings = [findings_by_id[fid] for fid in incident.finding_ids]
    reasons = []
    base = max(f.severity for f in findings)
    score = base
    reasons.append("base severity %.1f (highest in incident)" % base)
    if len(findings) >= 3:
        score += 1.0
        reasons.append("+1.0 three or more findings in one incident")
    public = [f for f in findings if _matches(f, PUBLIC_HINTS)]
    if public:
        score += 1.5
        reasons.append("+1.5 public exposure (%s)" % public[0].id)
    cred = [f for f in findings if _matches(f, CREDENTIAL_HINTS)]
    if cred:
        score += 2.0
        reasons.append("+2.0 credential abuse (%s)" % cred[0].id)
    extra = min(len({f.type for f in findings}) - 1, 3)
    if extra > 0:
        bonus = 0.5 * extra
        score += bonus
        reasons.append("+%.1f %d additional distinct finding type(s)" % (bonus, extra))
    if score > 10:
        reasons.append("capped at 10.0")
    incident.score = round(min(score, 10.0), 1)
    incident.score_reasons = reasons
    return incident
