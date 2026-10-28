from dataclasses import dataclass, field


@dataclass
class Finding:
    id: str
    source: str
    type: str
    title: str
    description: str
    severity: float
    resource_type: str
    resource_id: str
    account_id: str
    region: str
    first_seen: str
    last_seen: str
    status: str = "ACTIVE"


@dataclass
class Incident:
    id: str
    finding_ids: list = field(default_factory=list)
    resources: list = field(default_factory=list)
    account_id: str = ""
    first_seen: str = ""
    last_seen: str = ""
    score: float = 0.0
    score_reasons: list = field(default_factory=list)
    status: str = "open"
