# Credential Locations — MGMT-XPS
# This file points to where credentials live. It does NOT store credentials.

## This Machine
- Claude Code auth: managed by claude CLI (run `claude` to re-auth if needed)
- Codex CLI auth: managed by codex CLI (run `codex` to re-auth if needed)
- SSH keys: /home/tunedr/.ssh/

## Remote Credential Store
- Primary credentials file: /home/tunedr/CREDENTIALS.env on pop-ollama (100.91.173.40)
- To read: ssh tunedr@100.91.173.40 cat /home/tunedr/CREDENTIALS.env
- Notion API key: in CREDENTIALS.env as NOTION_API_KEY
- Anthropic API key: in CREDENTIALS.env as ANTHROPIC_API_KEY

## SSH Key Setup (if not already done)
- Run: ssh-keygen -t ed25519 -C "mgmt-xps-agent"
- Copy to each machine: ssh-copy-id tunedr@100.91.173.40
- Copy to each machine: ssh-copy-id root@100.99.40.111
- Copy to each machine: ssh-copy-id root@100.108.23.97
