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
 
- October 29, 2026: Verification hardened and the live driver written. Tool allowlist in the loop: a call naming an unregistered tool is discarded and logged in the run history, and the run still completes. Checklist coverage: nine reference kinds a complete triage must answer, measured in code at set_checklist and file_report; a filing that misses a kind is refused naming only the kind, and the filed report carries the coverage percentage for the human reviewer. Claims check: after the deterministic gate, a separate model call judges whether each recorded quote supports its claim; an unsupported claim refuses the filing and the refused draft is saved beside the run file. LiveModel (muse-spark-1.3) written with the full run state carried in every prompt and proven end to end with the network call stubbed: files in 6 turns at 100 percent coverage with the claims check passing. The first real live run awaits a working Meta Model API key: key creation in the Meta console is currently failing, reported to the organizers, and a reply is being watched for.
