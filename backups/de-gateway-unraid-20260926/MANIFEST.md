# Unraid de-gateway Stack Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source host: Unraid (Tower) — 192.168.1.2
# Source path: /mnt/user/appdata/de-gateway/

## Archived Files
- `docker-compose.yml` — de-gateway stack compose (SAFE: uses env_file, no inline secrets)

## What Was Excluded
- `/mnt/user/appdata/de-gateway/.env` — EXCLUDED: Contains WEBUI_SECRET_KEY and any other live secrets
  Only key found: WEBUI_SECRET_KEY (openwebui secret)

## Services in Stack
| Container | Port | Purpose |
|-----------|------|---------|
| openclaw-gateway | :7075 | OpenClaw gateway (external Telegram routing) |
| agent-zero-master-router | :7072 | LEGACY Agent Zero router |
| n8n-gateway | :5680 | n8n for gateway workflows |
| uptime-kuma | :3002 | Uptime monitoring |
| openwebui | :3010 | Open WebUI (Ollama frontend) |

## Recovery Notes
- Stack is at /mnt/user/appdata/de-gateway/ on Unraid
- Restore: copy compose + .env (from CREDENTIALS.env on pop-ollama), then `docker compose up -d`
- openclaw-gateway uses Unraid's local openclaw data volume for state
- n8n-gateway uses a named volume `n8n-data` (workflow data)
