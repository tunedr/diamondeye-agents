# MGMT-XPS — Local Machine Identity

## Machine Facts
- Hostname: MGMT-XPS
- OS: PopOS (Ubuntu-based)
- Primary user: tunedr
- Home directory: /home/tunedr
- Tailscale IP: 100.76.233.89
- Role: Dedicated interactive AI execution node

## Role in DiamondEye Stack
- This is the ONLY machine where Claude Code and Codex run interactively
- This machine is the Atlas escalation target for hard tasks
- Atlas sends task payloads here when local Ollama cannot handle the job
- This machine has SSH reach to all other DiamondEye machines via Tailscale

## Agents Running Here
- Claude Code (interactive, Claude Pro/Max auth)
- Odin — Hermes v0.21.3 bare-metal PA; model: openai-codex/gpt-5.5 (migrated 2026-09-20, forensic 3e26d271-f21c-81b2); rollback: anthropic/claude-sonnet-4-6 (backup at odin-phase-c-backup-20260921T003520Z); hermes-gateway.service (Telegram, PID 3955957), hermes-serve :9119, hermes-dashboard :9120, hermes-webui :9121 (Hermex, HUMAN IPHONE GATE pending); Level 2 CONTINUITY READY (2026-09-19, forensic 3dc6d271)
- hermes-desk Docker — model: gpt-5.5/openai-codex (autonomous portfolio manager; NOT the PA front-door)
- Codex CLI — NOTE: ChatGPT Plus subscription lapsed 2026-09-05; repair needs Branden renewal + gpt-4o swap. hermes-desk uses Codex OAuth (gpt-5.5) independently via Docker env. Codex CLI interactive escalation path status: unverified as of 2026-09-05.
- Agent Zero (legacy container on port 50080 — abandoned for active workflows)

## Context Root
- All agent context lives at: /home/tunedr/AGENTS/
- Skills: /home/tunedr/AGENTS/LOCAL/skills/
- SSH configs: /home/tunedr/AGENTS/LOCAL/ssh/
