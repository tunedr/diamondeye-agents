# 40 — Model Routing Doctrine

## Global Fleet Standard (June 5 2026 — Locked by Branden)

| Role | Model | Endpoint |
|---|---|---|
| CHAT | llama3.2:latest | http://192.168.1.2:11434 (Unraid) |
| UTILITY / CODER | qwen2.5-coder:7b | http://192.168.1.136:11434 (pop-ollama) |
| EMBED | nomic-embed-text:latest | http://192.168.1.2:11434 (Unraid) |

This standard is locked. No agent changes it without explicit Branden approval.

## MGMT-XPS Routing Status (updated 2026-06-12)

pop-ollama (192.168.1.136:11434): REACHABLE as of 2026-06-12.
- Was unreachable from MGMT-XPS on 2026-06-11 (transient outage — root cause unknown).
- Reachability confirmed: HTTP 200, qwen2.5-coder:7b present.
- Agent Zero usr/.env UTILITY_MODEL_BASE_URL=http://192.168.1.136:11434 is correct.

Unraid (192.168.1.2:11434): REACHABLE — qwen2.5:7b, llama3.2, nomic-embed confirmed.
- Approved fallback for UTILITY if pop-ollama becomes unreachable again.
- Hermes Desk delegation currently uses Unraid qwen2.5:7b (Phase 4 2026-06-11 change).

## Executor Assignment

| Task Type | Executor |
|---|---|
| Orchestration, reasoning, task intake, runbook creation | GPT / Hermes Desk |
| Complex code/config repair, multi-file edits, diagnostic chains | Claude Code (this session) |
| Atomic execution — SSH, Docker, scripts | Agent Zero → qwen2.5-coder subagents |
| Embeddings / semantic search | nomic-embed-text @ Unraid |

## Escalation Path

1. Local Ollama (qwen2.5-coder at pop-ollama, or Unraid fallback) — routine low-cost execution
2. Claude Code via tmux — complex repair, multi-context work, escalation after 2 failures
3. Claude API — only for revenue tools and hard escalations (not internal pipeline)

## Fallback Policy

If pop-ollama (192.168.1.136:11434) becomes unreachable from MGMT-XPS:
- Approved fallback: qwen2.5:7b @ http://192.168.1.2:11434 (Unraid)
- Document as fallback routing, not a permanent fleet-standard change
- Any permanent fleet-standard change requires Branden decision
- Update DIAMONDEYE-STATE.md to reflect outage status

## Credit Outage Protocol

If GPT/Hermes Desk credits are exhausted:
- Acknowledge the outage explicitly
- Log task or idea into scratch/inbox.md for Desk pickup later
- Do not substitute Claude Code for Hermes Desk decision-making

## Claude Code Model Selection

| Job Type | Model |
|---|---|
| Config edits, file writes, simple scripts | Haiku |
| Multi-phase runbooks, moderate complexity | Sonnet (default) |
| Deep debugging, novel architecture | Opus (exception only) |
