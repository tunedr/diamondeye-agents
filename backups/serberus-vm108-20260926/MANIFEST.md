# VM108 serberus-hermes Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source host: serberus-hermes (VM108) — 192.168.1.108 static / Tailscale 100.67.35.31

## Current Status
BLOCKED — per memory project_serberus_hermes.md:
- Dual-profile prep COMPLETE (2026-09-05)
- BLOCKED on: Telegram tokens + model key (Branden action items)

## Archived Files
- `serberus-config.yaml` — Hermes v0.19.0 config (minimal — only dashboard auth)

## Serberus config.yaml (minimal install)
```yaml
dashboard:
  basic_auth:
    username: Serberus
    password_hash: scrypt$16384$8$1$436rFLS7bxbubrxCGvAwQg==$A7B2zp6UqU2toNKXqi8ePuCoyQrdSjhWbQ7pW6GEfEs=
```

## Notes
- Hermes v0.19.0 installed bare-metal via PyPI
- hermes-dashboard.service: systemd user service, linger enabled, port 9124
- Domain: serberus.diamondeye.net → NPM proxy host 16 on de-edge-01 → 192.168.1.108:9124
- SSL: Cloudflare Origin Cert ID 1 (expires 2041)
- openai-codex OAuth: NOT configured (open item per 3ae6d271 runbook)
- Telegram tokens: NOT configured (blocked — Branden action)
- Model key: NOT configured (blocked)

## Recovery Notes
- pip install hermes-agent[standard], then hermes-gateway configure
- Enable hermes-dashboard.service + loginctl enable-linger tunedr
- Re-auth: hermes auth (OAuth flow)
- NPM proxy host 16 is already configured on de-edge-01
