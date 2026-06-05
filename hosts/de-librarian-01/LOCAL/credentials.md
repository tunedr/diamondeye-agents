# Credential Locations — de-librarian-01

DO NOT store credential values in this file. Reference locations only.

## Primary Credential Source
All system credentials: /home/tunedr/CREDENTIALS.env on pop-ollama (192.168.1.136)
Read via: ssh tunedr@192.168.1.136 cat /home/tunedr/CREDENTIALS.env

## Local Credential Locations

| Credential | Location |
|---|---|
| Hermes .env (Telegram tokens, gateway config) | /mnt/truenas-canonical/hermes-data/.env |
| AnythingLLM API key | CREDENTIALS.env on pop-ollama — key: ANYTHINGLLM_PASSWORD |
| Paperless-ngx API token | CREDENTIALS.env on pop-ollama — key: PAPERLESS_AXIOM_TOKEN |
| TrueNAS admin password | CREDENTIALS.env on pop-ollama — key: TRUENAS_ADMIN_PASSWORD |
| System default password | CREDENTIALS.env on pop-ollama — key: system default password |
| Telegram librarian bot token | CREDENTIALS.env on pop-ollama — key: DE_LIBRARIAN_BOT_TOKEN |

## Service Auth Notes
- AnythingLLM: token auth on port 3001
- Paperless-ngx: API token on port 8010
- TrueNAS UI: admin login at http://192.168.1.106/ui — truenas_admin user
- Hermes gateway: open access (GATEWAY_ALLOW_ALL_USERS=true in .env)
