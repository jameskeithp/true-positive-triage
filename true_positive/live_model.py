"""LiveModel: the muse-spark-1.3 driver for the agent loop.

Same next_call(state, ctx) interface as SampleModel. Each call sends
the system prompt, the tool contract, the incident findings, and the
full run state, because Chat Completions does not carry reasoning
across turns for external keys; the app persists its own state.

API rules baked in (proven in the Oct 27 smoke test): budget output
generously via max_completion_tokens, set reasoning_effort low for
routine turns, never send logprobs. The key comes from the MODEL_API_KEY
environment variable or the repo .env file; it is never printed.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from .agent import SYSTEM_PROMPT
from .coverage import KINDS

API_URL = "https://api.meta.ai/v1/chat/completions"
MODEL = "muse-spark-1.3"

TOOL_CONTRACT = (
    "Tools (call exactly one per reply):\n"
    '- ingest_findings: {"incident_id": str, "finding_ids": [str]}\n'
    '- record_fact: {"claim": str, "finding_id": str, "quote": str} '
    "(quote must be an exact substring of that finding's description)\n"
    '- set_checklist: {"items": [{"item": str, "kind": str, '
    '"status": "settled"|"na"|"open", "fact": int|null, "reason": str|null}]} '
    f"(kind must be one of: {', '.join(KINDS)}; settled needs a fact index, na needs a reason)\n"
    '- draft_runbook: {"text": str}\n'
    '- request_human_input: {"question": str}\n'
    '- file_report: {"summary": str, "citations": [int]}\n'
    'Reply with ONLY one JSON object: {"tool": name, "args": {...}}. No other text.'
)


def _load_key(explicit=None) -> str:
    if explicit:
        return explicit
    if os.environ.get("MODEL_API_KEY"):
        return os.environ["MODEL_API_KEY"]
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("MODEL_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("MODEL_API_KEY not found in environment or repo .env")


class LiveModel:
    def __init__(self, api_key=None):
        self._key = _load_key(api_key)

    def _chat(self, prompt: str) -> str:
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": 8192,
            "reasoning_effort": "low",
        }
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode(),
            method="POST",
            headers={"Authorization": f"Bearer {self._key}",
                     "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.load(response)
        return result["choices"][0]["message"].get("content") or ""

    @staticmethod
    def _parse_call(text: str) -> dict:
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            obj = json.loads(cleaned)
        except json.JSONDecodeError:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start < 0 or end <= start:
                raise
            obj = json.loads(cleaned[start:end + 1])
        if "tool" not in obj:
            raise ValueError("reply JSON has no tool field")
        obj.setdefault("args", {})
        return obj

    def _state_prompt(self, state, ctx) -> str:
        findings = {fid: (f if isinstance(f, dict) else vars(f))
                    for fid, f in ctx.findings.items()}
        parts = [
            SYSTEM_PROMPT,
            TOOL_CONTRACT,
            f"Incident: {state.incident_id}. Turn: {state.turn + 1} of {state.max_turns}.",
            "Findings on record (quote from these descriptions exactly):",
            json.dumps(findings, indent=2, default=str),
            "Facts recorded so far (index, claim, finding, quote):",
            json.dumps(state.facts, indent=2, default=str),
            f"Checklist: {json.dumps(state.checklist, default=str)}",
            f"Runbook drafted: {bool(state.runbook_draft)}. File attempts refused so far: {state.file_attempts}.",
        ]
        if state.history:
            parts.append("Recent history (your last calls and their results; refusals and "
                         "discards included, act on them):")
            parts.append(json.dumps(state.history[-3:], indent=2, default=str))
        return "\n\n".join(parts)

    def next_call(self, state, ctx) -> dict:
        prompt = self._state_prompt(state, ctx)
        text = self._chat(prompt)
        try:
            return self._parse_call(text)
        except Exception:
            retry = (prompt + "\n\nYour previous reply could not be parsed as a tool call. "
                     "Reply with ONLY the JSON object, nothing else.")
            return self._parse_call(self._chat(retry))

    def judge_claims(self, facts) -> list:
        listing = [{"index": i, "claim": f["claim"], "quote": f["quote"]}
                   for i, f in enumerate(facts)]
        prompt = (
            "You are a strict verification judge. For each entry, decide whether the "
            "quote actually supports the claim. Do not use outside knowledge. "
            'Reply with ONLY one JSON object: {"unsupported": [indexes]}. '
            "An empty list means every claim is supported.\n\n"
            + json.dumps(listing, indent=2)
        )
        text = self._chat(prompt).strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            obj = json.loads(text[start:end + 1])
        if "unsupported" not in obj and isinstance(obj.get("args"), dict):
            obj = obj["args"]
        return [int(i) for i in obj.get("unsupported", [])]
