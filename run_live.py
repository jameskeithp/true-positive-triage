import json
from true_positive.state import RunState, new_run_id
from true_positive.tools import ToolContext
from true_positive.agent import run_loop
from true_positive.live_model import LiveModel

INCIDENT_FINDINGS = ("gd-2001", "gd-2002")
items = json.load(open("data/sample_findings.json"))
items = items["findings"] if isinstance(items, dict) else items
ctx = ToolContext(findings={f["id"]: f for f in items if f["id"] in INCIDENT_FINDINGS})
state = RunState(run_id=new_run_id(), mode="live", incident_id="INC-002")
model = LiveModel()
state = run_loop(state, ctx, model, claims_judge=model.judge_claims)
print("STATUS:", state.status)
print("TURNS:", state.turn)
if state.report:
    print("COVERAGE:", state.report.get("coverage_pct"))
    print("REPORT STATUS:", state.report.get("status"))
