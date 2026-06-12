# A2A Handoff Contract — Hermes Desk to Agent Zero
# DiamondEye Three-Agent Architecture
# Written: 2026-06-12 — Autonomous Pipeline Completion Repair
# Maintained by: Hermes Librarian after evidence of working pipeline exists

## Purpose

This document defines the handoff contract between Hermes Desk and Agent Zero for the
DiamondEye three-agent autonomous pipeline. It specifies the packet format, required
fields, delivery mechanism, and receipt confirmation pattern.

The A2A bridge is the connection point that allows Hermes Desk to remain inside the
feedback loop while outside the execution loop.

## Current Implementation Status

As of 2026-06-12: SCAFFOLD ONLY — no automated bridge is wired.

Hermes Desk must manually pass the Notion runbook URL to Agent Zero via one of:
1. Direct HTTP POST to Agent Zero API at http://localhost:50080 (MGMT-XPS local)
2. Telegram message routed to Agent Zero if Telegram integration is active
3. tmux paste into Agent Zero session if interactive

Full automated A2A wiring is deferred until the smoke test confirms component readiness.

## Handoff Packet Format

Every task handed from Hermes Desk to Agent Zero must include all fields below.
Fields marked REQUIRED must be present. Fields marked OPTIONAL may be omitted if not applicable.

```json
{
  "job_id": "REQUIRED — unique ID (e.g. DE-YYYYMMDD-NNN)",
  "requesting_agent": "REQUIRED — always 'hermes-desk' for Desk-originated tasks",
  "receiving_agent": "REQUIRED — always 'agent-zero-desk' for MGMT-XPS execution",
  "runbook_url": "REQUIRED — full Notion URL of the runbook to execute",
  "goal": "REQUIRED — one sentence describing what done looks like",
  "phases_allowed": "REQUIRED — list of phase numbers allowed in this call (e.g. [1, 2, 3])",
  "allowed_tools": "REQUIRED — list of tool categories allowed (e.g. ['terminal', 'file', 'docker', 'ssh', 'notion'])",
  "forbidden_actions": "REQUIRED — list of explicitly forbidden actions (e.g. ['docker system prune', 'rm -rf', 'apt upgrade', 'pfSense'])",
  "model_route_expected": "REQUIRED — which model/endpoint Agent Zero should use (e.g. 'qwen2.5-coder:7b @ 192.168.1.136:11434')",
  "evidence_required": "REQUIRED — what proof is needed to mark the task done (e.g. 'Notion page ID, command output confirming service running')",
  "report_back_destination": "REQUIRED — Notion page ID or A2A callback URL where the execution report should be written",
  "stop_condition": "REQUIRED — exact condition that marks the task complete",
  "escalation_rule": "REQUIRED — when to escalate to Claude Code (e.g. 'two consecutive phase failures')",
  "human_approval_rule": "REQUIRED — what requires Branden approval before proceeding",
  "priority": "OPTIONAL — LOW / NORMAL / HIGH",
  "deadline": "OPTIONAL — ISO 8601 datetime",
  "context_notes": "OPTIONAL — additional context for Agent Zero"
}
```

## Example Packet (dry run)

```json
{
  "job_id": "DE-20260612-001",
  "requesting_agent": "hermes-desk",
  "receiving_agent": "agent-zero-desk",
  "runbook_url": "https://app.notion.com/p/37d6d271f21c81ee85b4d8f366696dc1",
  "goal": "Confirm all MGMT-XPS containers are running and report status to Hermes",
  "phases_allowed": [8],
  "allowed_tools": ["terminal", "docker"],
  "forbidden_actions": ["docker system prune", "rm -rf", "container restarts", "config edits"],
  "model_route_expected": "qwen2.5-coder:7b @ http://192.168.1.136:11434",
  "evidence_required": "docker ps output showing hermes-desk, agent-zero-desk, openclaw-desk all Up",
  "report_back_destination": "30e6d271-f21c-8141-b74d-f62f14ad1e6a",
  "stop_condition": "All containers confirmed running, status written to Notion",
  "escalation_rule": "Two consecutive failures on the same step escalate to Claude Code",
  "human_approval_rule": "Any container restart or config change requires Branden approval"
}
```

## Agent Zero Receipt Confirmation

When Agent Zero receives a handoff packet, it must:
1. Acknowledge receipt with job_id and timestamp
2. Fetch the runbook_url from Notion
3. Validate that the requested phases are within phases_allowed
4. Begin execution phase by phase
5. Write a Notion update after each phase
6. Return the completed structured execution report (see Agent Zero SOUL for schema) to report_back_destination

## Failure Handling

If Agent Zero cannot parse the packet or missing a REQUIRED field:
- Return error to requesting agent with the exact missing field
- Do not begin execution
- Write the failure to Notion with job_id

If a phase fails twice:
- Stop execution
- Write current state and error to Notion
- Escalate to Claude Code using the three-step invocation standard from SOUL

## Delivery Endpoint

Agent Zero API: http://localhost:50080 (MGMT-XPS local — not exposed externally)
Expected method: POST to Agent Zero chat/task endpoint
Authentication: local network only — no external exposure

Note: The exact Agent Zero API endpoint for receiving structured packets must be confirmed
during the full A2A integration task. Current implementation is scaffold/documentation only.

## Future Integration Steps (deferred from this runbook)

1. Confirm Agent Zero API endpoint path for task injection
2. Write Hermes Desk SOUL rule for packet format enforcement
3. Test with a single dry-run packet using harmless read-only task
4. Wire Hermes Desk automation to generate and POST the packet
5. Add OpenClaw scope validation hook before packet delivery
6. Connect report_back_destination to Hermes Desk incoming review flow
