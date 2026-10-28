# True Positive

True Positive is an AI security triage agent. It ingests AWS GuardDuty and
Security Hub findings, correlates related findings into incidents, risk-ranks
them, and drafts response runbooks with Meta Muse Spark 1.3. Nothing
executes without human approval.

## Disclosure

The product idea and an early skeleton are from before the Meta Global AI
Developer Hackathon. Everything in this repository was built during the
event, October 27 through November 4, 2026. No pre-hackathon code is used.

## What it does

- Reads security findings from AWS GuardDuty and Security Hub, or from
  sample data when AWS access is not available.
- Groups related findings into a single incident so an analyst sees one
  case, not a pile of disconnected alerts.
- Scores incident risk so the real threats surface first.
- Drafts a step-by-step response runbook with Muse Spark 1.3, grounded in
  the source findings.
- Stops at a human approval gate. The agent drafts; a person decides.

## Demo

The demo runs from a laptop. A keyless sample-run mode will be included so
anyone can run and verify the behavior without a Meta API key. Live mode
uses the Meta Model API with Muse Spark 1.3.

## Safety

True Positive is a triage and drafting tool. It does not remediate,
terminate, isolate, or change anything on its own. Every action in a
runbook requires explicit human approval first.

## Build log

- October 27, 2026: repository created empty. Meta Model API smoke test
  passed from the build laptop (model list and a chat completion on
  muse-spark-1.3, both HTTP 200).
- October 28, 2026: Agent loop built. Run state saved after every turn (`runs/<run_id>.json`), six tools (ingest_findings, record_fact, set_checklist, draft_runbook, request_human_input, file_report), grounding enforced by exact-quote checks in code, verification inside file_report with refusal reasons and escalation after three refusals. Proven in sample mode: honest run files in 6 turns as pending approval; an empty filing is refused three times and escalated.
 
