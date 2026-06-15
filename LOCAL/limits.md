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

## Pre-Authorized Operations (no per-instance approval needed)
Last updated: 2026-06-15 Session 20 — scoped explicitly, do NOT generalize beyond these boundaries.

### GitHub Repo Creation
- Creating NEW PRIVATE repos under github.com/tunedr for DiamondEye agent code/config/data is PRE-AUTHORIZED.
- Boundaries: private only, tunedr account only, DiamondEye-related only. NOT public repos. NOT other orgs.
- Credential required: GitHub fine-grained PAT with "Administration: write" for tunedr account repos.
  - Token location (once provisioned): set GH_TOKEN in /home/tunedr/CREDENTIALS.env and run `gh auth login --with-token <<< "$GH_TOKEN"`.
  - As of 2026-06-15: NO PAT exists. diamondeye-agents was created manually by Branden; SSH push access is via id_ed25519. gh CLI is installed (2.45.0) but not authenticated. The gap is missing credential, NOT missing authorization.
- SSH key (id_ed25519) grants git push/pull to EXISTING repos only. It does NOT grant GitHub REST API access for repo creation.

### Docker Container Restarts on MGMT-XPS
- Restarting these specific containers when config/doctrine changes require it is PRE-AUTHORIZED:
  - agent-zero-desk
  - hermes-desk
  - hermes-librarian (on VM107 — via SSH + docker restart, not local)
- tunedr is in the docker group — `docker restart <name>` works without sudo on MGMT-XPS.
- NOT included: production/customer-facing containers; pop-ollama containers during active inference; any container not listed above.

## Escalation Triggers
Stop and notify Branden before proceeding if:
- A task would modify VM disk layout or partition tables
- A task would remove or replace a running Docker container on pop-ollama
- A task would change Tailscale configuration on any machine
- A task output is ambiguous about success or failure
- Any remote machine is unreachable
- A GitHub repo creation is needed but GH_TOKEN is not in CREDENTIALS.env (credential gap, not auth gap)
