# Services — orchestrator (VM104)

## Running Services (verified 2026-06-16)

| Container | Port | Notes |
|-----------|------|-------|
| orchestrator-n8n | 5679 | Atlas pipeline — PRODUCTION, do not modify without pausing first |
| orchestrator-notion-bridge | 9102 | Notion Bridge v2 |
| orchestrator-agent-runner | 9101 | Agent runner |
| orchestrator-claude-server | (none) | No exposed port |
| grist | 8484 | Evidence ledger — standalone container, RestartPolicy=unless-stopped |

## Compose File
- `/root/orchestrator/docker-compose.yml` (root-owned) — manages orchestrator-n8n, notion-bridge, agent-runner, claude-server
- Grist is NOT in the compose file — managed standalone

## Service Access from MGMT-XPS
- n8n Atlas: http://100.108.23.97:5679 (or http://192.168.1.19:5679 from LAN)
- Grist: http://100.108.23.97:8484 (or http://192.168.1.19:8484 from LAN)
- notion-bridge: http://100.108.23.97:9102
- agent-runner: http://100.108.23.97:9101
