# Odin (MGMT-XPS Hermes PA) Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source: MGMT-XPS — /home/tunedr/.hermes/

## Archived Files (all safe — no inline secrets)
- `odin-config.yaml` — Hermes v0.21.3 config (provider model names, gateway tuning, MCP config)
  API keys are loaded from environment/OAuth — NOT in config.yaml
- `odin-SOUL.md` — Agent identity, voice, governing doctrines, authorization envelope
- `odin-AGENTS.md` — Working context and collaborator profile

## What Was Excluded
- `auth.json` — EXCLUDED: Contains OAuth tokens (openai-codex, Notion, etc.)
- `hermes-webui.env` — EXCLUDED: May contain API keys
- `mcp-tokens/` — EXCLUDED: OAuth token cache
- `vault/` — EXCLUDED: Secrets vault
- `*.db`, `*.db-wal`, `*.db-shm` — EXCLUDED: Runtime state DBs
- All `*.bak`, `*.pre-*` backup files — EXCLUDED: Redundant historical state
- `sessions/`, `memories/`, `logs/` — EXCLUDED: Runtime/session data

## Service Status (as of 2026-09-26)
- hermes-gateway.service: RUNNING — Telegram @diamondeye_gateway_bot, PID 3955957
- hermes-serve.service: RUNNING — :9119
- hermes-dashboard.service: RUNNING — :9120 (public: mgmt-xps.turtle-sunfish.ts.net:9120)
- hermes-webui.service: RUNNING — :9121 (Hermex/iPhone, HUMAN IPHONE GATE pending)

## Model Configuration
- Primary: openai-codex/gpt-5.5 (ChatGPT subscription OAuth, migrated 2026-09-20)
- Rollback: anthropic/claude-sonnet-4-6 (backup at /home/tunedr/.hermes/odin-phase-c-backup-20260921T003520Z/)
- Level 2 commissioned: 2026-09-19 (forensic 3dc6d271)
- OpenAI migration forensic: 3e26d271-f21c-81b2-8b95-c325760f20b6

## Recovery Notes
- To rebuild Odin from scratch: install hermes-agent, copy config.yaml, re-auth (hermes auth)
- SOUL.md and AGENTS.md restore identity/context after a fresh install
- OAuth tokens cannot be backed up — will require re-auth via `hermes auth`
