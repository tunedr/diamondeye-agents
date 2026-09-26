# DiamondEye Git/Resource Coverage Matrix
# Date: 2026-09-26
# Session: 3e76d271-f21c-81fa-8e12-ccf1ae50247e (runbook)
# Forensic: 3e26d271-f21c-8158-8874-e837b8964ebd
# Exclusions per Branden: VM106, VM110

## Status Legend
- GIT-PUSHED: in diamondeye-agents git repo, pushed to GitHub
- BUNDLE: git bundle or export artifact in AGENTS repo (pushed)
- SANITIZED-ARCHIVE: secrets-redacted copy in AGENTS repo (pushed)
- RAW-ARCHIVE: no-secret file archived as-is in AGENTS repo (pushed)
- LIVE-GIT: local git repo on source host (not pushed to GitHub)
- GAP: coverage gap documented, action needed
- EXCLUDED: excluded per Branden or out of scope
- BLOCKED: explicit blocker documented

## MGMT-XPS (Management Machine)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| AGENTS/ context (ICM files, this repo) | GIT-PUSHED | root of diamondeye-agents | HEAD: c5cbd25 |
| Odin config.yaml | RAW-ARCHIVE | backups/odin-mgmt-xps-20260926/ | No inline secrets — config only |
| Odin SOUL.md | RAW-ARCHIVE | backups/odin-mgmt-xps-20260926/ | Identity/doctrine |
| Odin AGENTS.md | RAW-ARCHIVE | backups/odin-mgmt-xps-20260926/ | Working context |
| Odin auth.json / OAuth tokens | EXCLUDED | — | Cannot backup OAuth tokens — re-auth required |
| hermes-desk docker-compose.yml | SANITIZED-ARCHIVE | backups/hermes-desk-20260926/ | Live API keys redacted |
| hermes-desk-data/ volume | EXCLUDED | — | Runtime state — too large, uid 10000 |
| honcho startup config | SANITIZED-ARCHIVE | backups/honcho-mgmt-xps-20260926/ | No compose file; startup cmd documented |
| honcho-postgres data | EXCLUDED | — | Runtime DB — not archivable |

## orchestrator (VM104)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| atlas-v2 source code | LIVE-GIT + BUNDLE | backups/atlas-v2-20260926/ | Commit d32da07; bundle SHA256: 7c561185... |
| orchestrator n8n workflows | BUNDLE | backups/orchestrator-n8n-20260926/ | 3 workflows; SHA256: b7841f62...; NOT workflow data/credentials |

## de-edge-01 (VM103)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| NPM proxy_host nginx configs (16) | RAW-ARCHIVE | backups/npm-de-edge-20260926/proxy_hosts/ | All 16 hosts |
| NPM keys.json | EXCLUDED | — | RSA private key — do not commit |
| NPM custom SSL private key | EXCLUDED | — | Cloudflare Origin Cert privkey — regenerate from CF dashboard |
| NPM database.sqlite | EXCLUDED | — | State DB — may contain hashed credentials |

## de-pubmachine-01 (VM102)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| Main docker-compose.yml | SANITIZED-ARCHIVE | backups/pubmachine-vm102-20260926/ | DB passwords + n8n encryption key redacted |
| Publishing agent docker-compose.yml | SANITIZED-ARCHIVE | backups/pubmachine-vm102-20260926/ | A0 auth password redacted; LEGACY container |
| inspections-site static files | RAW-ARCHIVE | backups/pubmachine-vm102-20260926/ | index.html, _redirects, deploy.sh |
| inspections-site source (future deploy) | GAP | — | Also deployed to Cloudflare Pages (project: inspections-site) |
| n8n workflows (VM102 pub instance) | GAP | — | Publishing n8n workflows not yet exported |

## affiliate-engine-01 (VM105)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| resume-tool docker-compose.yml | RAW-ARCHIVE | backups/affiliate-vm105-20260926/ | Safe — uses env_file |
| resume-tool .env | EXCLUDED | — | Contains API keys |
| resume-tool source code | GAP | — | Local build; source not in git; recommend: git init + push to GitHub |
| ae-n8n workflows (affiliate) | GAP | — | Not exported |

## Unraid (Tower)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| de-gateway docker-compose.yml | RAW-ARCHIVE | backups/de-gateway-unraid-20260926/ | Safe — uses env_file |
| de-gateway .env | EXCLUDED | — | Contains WEBUI_SECRET_KEY |
| de-gateway openclaw data | EXCLUDED | — | Runtime state; too large |
| n8n-gateway (Unraid) workflows | GAP | — | Not exported |

## serberus-hermes (VM108)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| Hermes config.yaml | RAW-ARCHIVE | backups/serberus-vm108-20260926/ | Minimal — only dashboard auth hash |
| Serberus install | BLOCKED | — | Blocked on Telegram tokens + model key (Branden action) |

## pop-ollama (VM101)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| Sentinel n8n workflows | GAP | — | Not exported; low priority (gen-1 pipeline) |
| Postiz config | GAP | — | Social distribution — not exported |
| Cline API + proxy scripts | GAP | — | bare-metal scripts; not in git |

## de-librarian-01 (VM107)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| All Hermes containers | EXCLUDED | — | ALL EXITED — decision pending Branden |
| n8n-librarian workflows | GAP | — | Not exported; low priority |
| paperless-ngx data | EXCLUDED | — | Document archive — too large for git |
| AnythingLLM data | EXCLUDED | — | Knowledge base — too large for git |

## ha-control (VM100)

| Resource | Status | Location in AGENTS repo | Notes |
|----------|--------|------------------------|-------|
| Home Assistant config | EXCLUDED | — | HA has built-in backup/snapshot; too large for git |

## Excluded Hosts (per Branden)

| Host | Status | Reason |
|------|--------|--------|
| de-truenas-01 (VM106) | EXCLUDED | Branden-owned exception — SSH key missing, no API token |
| VM110 | EXCLUDED | Branden-owned exception — explicit exclusion from scope |

## Summary

| Category | Count |
|----------|-------|
| GIT-PUSHED (live repo) | 1 |
| BUNDLE/EXPORT in AGENTS repo | 2 |
| RAW-ARCHIVE in AGENTS repo | 8 |
| SANITIZED-ARCHIVE in AGENTS repo | 3 |
| LIVE-GIT (not pushed to GitHub) | 1 |
| GAP (documented, needs future action) | 7 |
| EXCLUDED (justified) | 10 |
| BLOCKED (external blocker) | 1 |

## Key Gaps for Future Sessions
1. resume-tool source code (VM105) — git init + private GitHub repo
2. VM102 n8n publishing workflows — export JSON + archive
3. VM105 ae-n8n affiliate workflows — export JSON + archive
4. Unraid n8n-gateway workflows — export JSON + archive
5. VM101 Sentinel n8n workflows — export JSON + archive
6. honcho docker-compose.yml — create proper compose file
7. Postiz config (VM101) — assess if business-critical enough to export
