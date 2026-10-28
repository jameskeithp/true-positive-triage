# True Positive: design

Decided in-session on October 27, 2026, the first build night of the Meta
Global AI Developer Hackathon. This document records the design; the code
in this repository implements it.

## Principles

1. Code decides, the model drafts. Risk scores and verification are plain
   code. The model writes summaries and runbook drafts.
2. Grounding is enforced, not requested. A fact enters the case record
   only with an exact quote from a source finding, and the record refuses
   a quote that is not in the source text.
3. The human gate is structural. A report files as pending approval.
   Nothing executes from this tool without a person approving it.
4. Everything is resumable. Run state is saved after every turn, so a
   failed API call leaves a paused run, not a lost one.

## Data model

Finding (one normalized alert):
- id, source (guardduty, securityhub, or sample)
- type, title, description (the source text, kept verbatim)
- severity, normalized at ingest to a 0 to 10 scale
- resource_type, resource_id, account_id, region
- first_seen, last_seen, status

Incident (one case for the analyst):
- id, the list of finding ids grouped into it
- resources involved, first_seen, last_seen
- score and score_reasons (see scoring)
- status: open, needs_input, or filed

## Correlation

- Primary grouping: same resource_id (one instance, one bucket, one IAM
  principal) in the same account.
- Secondary grouping: findings with no clear resource group by account
  and finding family (the normalized type prefix, for example
  UnauthorizedAccess or CryptoCurrency).
- A finding joins an incident only if its last_seen is within 24 hours of
  the incident's latest finding. Rules are plain and explainable on
  purpose: an analyst must be able to say why two alerts are one case.

## Scoring (deterministic, in code)

- Base: the highest severity in the incident.
- +1.0 when the incident holds 3 or more findings.
- +1.5 when any finding shows public exposure (a public resource or a
  rule open to 0.0.0.0/0).
- +2.0 when any finding shows credential abuse (root use, access key
  misuse, credential access).
- +0.5 for each additional distinct finding type beyond the first,
  up to +1.5.
- Total is capped at 10 and rounded to one decimal. Every component is
  recorded in score_reasons, so the number can always be explained.

## The agent loop

- The model picks one tool per turn. Turns are capped at 25. The final
  turn forces the report to be filed.
- After every turn, the full run state is written to runs/<run_id>.json.
- A failed API call marks the run paused. A paused run resumes from its
  saved state.
- API calls retry on transient errors, and every call logs its request
  ID, because the Model API has shown intermittent failures from some
  hosts during this event.

## Tools (one file each)

- ingest_findings: load findings from a source and normalize them.
- record_fact: add a fact to the case record. Requires the finding id
  and an exact quote from that finding's description. Refuses anything
  else.
- set_checklist: set or update the triage checklist for the incident.
- draft_runbook: draft the response runbook from recorded facts only.
- request_human_input: move the incident to needs_input and state
  exactly what evidence is missing. The run stops there.
- file_report: file the final report as pending approval. This tool
  runs the verification checks below before it accepts the report.

## Verification (inside file_report)

- Every checklist item is settled: answered by a recorded fact, or
  marked not applicable with a reason.
- Every citation in the report matches a recorded fact, and every
  recorded fact traces to a finding id and an exact quote.
- No open evidence request remains.
- If a check fails, the tool refuses the report and says why. After 3
  refusals the run escalates to a human instead of looping.

## Approval

- A filed report is pending approval. A person approves it, or rejects
  it with notes. Rejection notes return to the agent for a revised
  draft. Approval in this version approves the report only; executing
  runbook steps is a later feature and will be dry-run first.

## Run modes

- Live mode: Meta Model API, model muse-spark-1.3, key read from the
  MODEL_API_KEY environment variable. Never stored in the repo.
- Sample mode: canned model responses over the sample data in this
  repo, so anyone can run and verify the full flow with no API key.

## Out of scope for the first slice

- Live GuardDuty and Security Hub pulls (planned during the event).
- Executing runbook steps (planned, dry-run first, approval required).
