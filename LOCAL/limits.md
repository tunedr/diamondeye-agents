# MGMT-XPS — What This Agent Cannot Do

## Hard Limits
- Do NOT modify n8n workflows on any machine without pausing pipeline first
- Do NOT touch Atlas pipeline logic (VM 104) autonomously
- Do NOT restart Docker services on pop-ollama during active inference
- Do NOT delete any data on any machine
- Do NOT run apt upgrade on any remote machine
- Do NOT touch pfSense (100.102.75.124) for any reason
- Do NOT modify this machine's own Claude Code or Codex configuration autonomously
- Do NOT store credentials in any file inside /home/tunedr/AGENTS/ — use credential refs only

## Escalation Triggers
Stop and notify Branden before proceeding if:
- A task would modify VM disk layout or partition tables
- A task would remove or replace a running Docker container on pop-ollama
- A task would change Tailscale configuration on any machine
- A task output is ambiguous about success or failure
- Any remote machine is unreachable
