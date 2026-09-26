# hermes-desk Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source: MGMT-XPS — /home/tunedr/hermes-desk/

## Archived Files
- `docker-compose.sanitized.yml` — hermes-desk compose (sanitized, all API keys redacted)

## What Was Excluded
- `/home/tunedr/hermes-desk/docker-compose.yml` — EXCLUDED: Contains live API keys inline
- `/home/tunedr/hermes-desk-data/` — EXCLUDED: Runtime data (Docker uid 10000, contains sessions/memory)

## Secrets Gap
Live docker-compose.yml stores all API keys inline (not in env files):
- GEMINI_API_KEY / GOOGLE_API_KEY
- GROQ_API_KEY
- CEREBRAS_API_KEY
- OPENROUTER_API_KEY
- OLLAMA_CLOUD_API_KEY
- API_SERVER_KEY (hermes API auth key)
Actual values are accessible via: ssh pop-ollama, cat /home/tunedr/CREDENTIALS.env

## Service Status (as of 2026-09-26)
- Container: hermes-desk (RUNNING, up — image: nousresearch/hermes-agent:latest)
- API: :8642 (bound 0.0.0.0)
- Dashboard: :9124 (mapped to :9125 on host)
- Model: gpt-5.5 via openai-codex OAuth
- Role: autonomous executor and portfolio manager (NOT the PA front-door)

## Recovery Notes
- Restore secrets from CREDENTIALS.env on pop-ollama
- Copy sanitized compose, fill in <REDACTED:*> values, then: docker compose up -d
- Data volume /home/tunedr/hermes-desk-data/ persists sessions/memory across restarts
