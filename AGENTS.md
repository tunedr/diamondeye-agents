# DiamondEye Agent Context — MGMT-XPS
## Identity
This machine is MGMT-XPS. Tailscale IP: 100.76.233.89.
This is the dedicated AI execution node for the DiamondEye system.
This is the ONLY machine where Claude Code and Codex run interactively.
This machine is the Atlas escalation target for tasks beyond local Ollama capability.

## Working Agreements
- Always read GLOBAL/architecture.md before starting any task
- Always read LOCAL/limits.md before touching any remote machine
- Ollama/DeepSeek first — for tasks local models can handle
- Codex CLI second — for coding and infrastructure tasks (better credit monitoring)
- Claude Code last resort only — when both Ollama and Codex cannot complete the task
- All results written to Notion before session ends
- Never modify your own infrastructure
- Never delete data
- Never run apt upgrade on any remote VM
- n8n must be paused before any pipeline surgery
- Prefer Tailscale IPs for inter-service SSH and traffic where Tailscale is verified; use documented LAN IPs for hosts without confirmed Tailscale (see GLOBAL/architecture.md for per-host status)

## Load Order
1. GLOBAL/architecture.md
2. GLOBAL/rules.md
3. GLOBAL/services.md
4. GLOBAL/notion-schema.md
5. LOCAL/identity.md
6. LOCAL/limits.md
