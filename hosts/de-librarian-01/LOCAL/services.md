# Services — de-librarian-01

Last verified: 2026-06-05

## Hermes Agent (NEW — replaces agent-zero-librarian and n8n-librarian)

| Container | Port | Image | Status | Touch? |
|---|---|---|---|---|
| hermes | 8642:8642 | nousresearch/hermes-agent:latest | UP | ACTIVE — primary executor |

Hermes profiles: librarian, apollo, truth-lens, coder
Gateway data: /mnt/truenas-canonical/hermes-data (TrueNAS NFS)
Compose: /opt/hermes/docker-compose.yml
Network: de-knowledge_librarian-net

## Knowledge Stack (do not modify without explicit task)

| Container | Port | Image | Status | Touch? |
|---|---|---|---|---|
| agent-zero-axiom | 7073:80 | local image 189168e18236 | UP | DO NOT TOUCH |
| agent-zero-librarian | 7071:80 | frdel/agent-zero-run:latest | UP | REPLACE pending Hermes stability |
| librarian-gotenberg | 3000 | gotenberg/gotenberg:8 | UP | DO NOT TOUCH |
| openclaw-axiom-openclaw-gateway-1 | 7074, 18790 | ghcr.io/openclaw/openclaw:latest | UP | DO NOT TOUCH |
| anythingllm | 3001 | mintplexlabs/anythingllm:latest | UP | DO NOT TOUCH |
| paperless-ngx | 8010:8000 | ghcr.io/paperless-ngx/paperless-ngx:latest | UP | DO NOT TOUCH |
| librarian-nextcloud | 8080:80 | nextcloud:latest | UP | DO NOT TOUCH |
| stirling-pdf | 8020:8080 | frooodle/s-pdf:latest | UP | DO NOT TOUCH |
| librarian-postgres | 5432 | postgres:15 | UP | DO NOT TOUCH |
| librarian-redis | 6379 | redis:7 | UP | DO NOT TOUCH |
| excalidraw | 8030:80 | excalidraw/excalidraw:latest | UP | DO NOT TOUCH |
| librarian-tika | 9998 | apache/tika:latest | UP | DO NOT TOUCH |
| n8n-librarian | 5680:5678 | n8nio/n8n:latest | UP | REPLACE with Hermes cron (pending) |

## Docker Network
- Shared network: de-knowledge_librarian-net
- All VM 107 containers on this network communicate by container name

## SearXNG
- Internal process (not in container table): localhost:55510
- Used by Apollo and Truth Lens for web search
