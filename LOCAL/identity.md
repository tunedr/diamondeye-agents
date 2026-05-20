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
- Codex CLI (interactive, ChatGPT Plus auth)
- Agent Zero (chat/orchestration layer on port 50080)

## Context Root
- All agent context lives at: /home/tunedr/AGENTS/
- Skills: /home/tunedr/AGENTS/LOCAL/skills/
- SSH configs: /home/tunedr/AGENTS/LOCAL/ssh/
