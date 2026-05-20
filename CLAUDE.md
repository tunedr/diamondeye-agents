# DiamondEye Agent Context — MGMT-XPS
## Identity
This machine is MGMT-XPS. Tailscale IP: 100.76.233.89.
This is the dedicated AI execution node for the DiamondEye system.
This is the ONLY machine where Claude Code and Codex run interactively.
This machine is the Atlas escalation target for tasks beyond local Ollama capability.

## Load Order
Read the following files before taking any action:
1. GLOBAL/architecture.md — full VM inventory and system layout
2. GLOBAL/rules.md — standing rules that cannot be overridden
3. GLOBAL/services.md — all running services across the stack
4. GLOBAL/notion-schema.md — Notion page IDs and field names
5. LOCAL/identity.md — this machine's specific role and constraints
6. LOCAL/limits.md — what this agent is NOT allowed to do

## Escalation Rule
Ollama/DeepSeek first. Codex CLI second. Claude Code only as last resort.
Codex has better credit monitoring — always try Codex before escalating to Claude Code.
Never burn Claude credits on tasks that Ollama or Codex can handle.

## Output Rule
All task results go to Notion before the session ends. No exceptions.
