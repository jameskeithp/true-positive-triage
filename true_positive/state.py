"""Run state for the True Positive agent loop.

State is saved to runs/<run_id>.json after every turn so a run can be
paused (for example on a failed API call) and resumed exactly where it
stopped.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path

RUNS_DIR = Path("runs")


def new_run_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]


@dataclass
class RunState:
    run_id: str
    mode: str                      # "live" or "sample"
    incident_id: str | None = None
    turn: int = 0
    max_turns: int = 25
    status: str = "running"        # running | paused | needs_input | filed | escalated
    facts: list = field(default_factory=list)        # recorded facts (finding_id + quote)
    checklist: list = field(default_factory=list)    # checklist items and their state
    runbook_draft: str | None = None
    report: dict | None = None
    messages: list = field(default_factory=list)     # model conversation
    history: list = field(default_factory=list)      # tool calls and results, one per turn
    file_attempts: int = 0

    def save(self) -> Path:
        RUNS_DIR.mkdir(exist_ok=True)
        path = RUNS_DIR / f"{self.run_id}.json"
        path.write_text(json.dumps(asdict(self), indent=2))
        return path

    @classmethod
    def load(cls, run_id: str) -> "RunState":
        data = json.loads((RUNS_DIR / f"{run_id}.json").read_text())
        return cls(**data)

