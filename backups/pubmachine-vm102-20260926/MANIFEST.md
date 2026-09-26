# VM102 de-pubmachine-01 Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source host: de-pubmachine-01 (VM102) — 192.168.1.48

## Services Running (all healthy as of 2026-09-26)
| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| inspections-web | nginx:alpine | :8081 | DiamondEye Inspections static site → diamondeye.net |
| shlink | shlinkio/shlink:stable | :8080 | Link shortener → go.diamondeye.net |
| n8n | n8nio/n8n:latest | :5678 | Publishing workflows |
| agent-zero-publishing | frdel/agent-zero-run:latest | :7071 | LEGACY — abandoned per 2026-07-20 |
| pub-postgres | postgres:16 | internal | Shlink database |
| pub-n8n-postgres | postgres:16 | internal | n8n database |

## Archived Files
- `docker-compose.sanitized.yml` — Main compose (sanitized, secrets redacted)
- `publishing-agent-docker-compose.sanitized.yml` — Agent Zero compose (sanitized, LEGACY)
- `inspections-site-index.html` — DiamondEye Inspections static site HTML
- `inspections-site-deploy.sh` — Cloudflare Pages deploy script (no secrets inline)
- `inspections-site-redirects` — _redirects file for Cloudflare Pages

## Secrets Gap
The live `/srv/pubmachine/docker-compose.yml` stores secrets inline:
- PostgreSQL passwords (same password used for both shlink and n8n DBs)
- n8n encryption key (required to decrypt existing n8n credentials)
These should be migrated to an env_file or Vault. Actual values are in CREDENTIALS.env on pop-ollama.

## Docker Compose Location on VM102
- Main: `/srv/pubmachine/docker-compose.yml`
- Publishing agent: `/srv/pubmachine/agents/publishing/docker-compose.yml`

## Inspections Site Notes
- Static site served from `/home/tunedr/inspections-site` on VM102
- Also deployed to Cloudflare Pages (project: inspections-site) via wrangler
- Deploy script requires `CLOUDFLARE_API_TOKEN` env var — not stored in script
- Source of truth for deploy: the static files in this backup
