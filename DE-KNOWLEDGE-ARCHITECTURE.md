# DE-KNOWLEDGE-ARCHITECTURE.md
# DiamondEye Knowledge Layer — Canonical Build Runbook
# Source: May 15 2026 Session Record + May 13 2026 V2 Architecture Doc
# Written: 2026-05-17
# Status: Ready for Claude Code on MGMT-XPS

---

## Overview

This runbook deploys the full DiamondEye knowledge layer on de-librarian-01 (VM 107, 192.168.1.107).

The Librarian is NOT a chat interface. It is the knowledge hygiene and retrieval backend for the entire DiamondEye system. It is called by the Ground Truth Gateway as a mandatory retrieval step before any operational answer is generated.

The three-layer zero-credit knowledge stack:
- Layer 1: TrueNAS NFS at 192.168.1.106 — canonical markdown files, source of truth
- Layer 2: AnythingLLM — vector/RAG query layer, serves knowledge to Agent Zero
- Layer 3: Notion — index and human dashboard only, NOT source of truth

AI inference backend: Ollama on Unraid at 192.168.1.2:11434
- NOT pop-ollama. Unraid Ollama only.
- Agent Zero model: qwen2.5:7b via Ollama (primary), Codex CLI (escalation)
- Embedding model: nomic-embed-text via Unraid Ollama
- Never calls Claude Sonnet directly

---

## VM Spec (already built — do not recreate)

- VM ID: 107
- Hostname: de-librarian-01
- IP: 192.168.1.107
- MAC: BC:24:11:87:E9:19
- RAM: 8GB (balloon=0)
- CPU: 4 cores
- Disk: 64GB
- BIOS: OVMF, q35, virtio
- OS: Ubuntu Server 24.04
- User: tunedr / Tran$4mer$

---

## Container Stack

All containers run on de-librarian-01.

Ports:
- agent-zero-librarian: 7071
- n8n-librarian: 5680
- anythingllm: 3001
- paperless-ngx: 8010
- nextcloud: 8080
- stirling-pdf: 8020
- excalidraw: 8030
- open-resume: 8040
- postgresql: internal only
- redis: internal only

---

## Docker Compose

Write to /home/tunedr/de-knowledge/docker-compose.yml

```yaml
version: "3.8"

networks:
  librarian-net:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
  paperless-data:
  paperless-media:
  paperless-export:
  paperless-consume:
  anythingllm-data:
  nextcloud-data:
  agent-zero-librarian-data:
  n8n-librarian-data:

services:

  postgresql:
    image: postgres:15
    container_name: librarian-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: paperless
      POSTGRES_USER: paperless
      POSTGRES_PASSWORD: Tran$4mer$
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - librarian-net

  redis:
    image: redis:7
    container_name: librarian-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - librarian-net

  paperless-ngx:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    container_name: paperless-ngx
    restart: unless-stopped
    depends_on:
      - postgresql
      - redis
    ports:
      - "8010:8000"
    volumes:
      - paperless-data:/usr/src/paperless/data
      - paperless-media:/usr/src/paperless/media
      - paperless-export:/usr/src/paperless/export
      - paperless-consume:/usr/src/paperless/consume
    environment:
      PAPERLESS_REDIS: redis://librarian-redis:6379
      PAPERLESS_DBHOST: librarian-postgres
      PAPERLESS_DBUSER: paperless
      PAPERLESS_DBPASS: Tran$4mer$
      PAPERLESS_DBNAME: paperless
      PAPERLESS_SECRET_KEY: diamondeye-librarian-secret-2026
      PAPERLESS_TIKA_ENABLED: 1
      PAPERLESS_TIKA_GOTENBERG_ENDPOINT: http://librarian-gotenberg:3000
      PAPERLESS_TIKA_ENDPOINT: http://librarian-tika:9998
      PAPERLESS_OCR_LANGUAGE: eng
      PAPERLESS_AI_LLM_PROVIDER: openai_compatible
      PAPERLESS_AI_OPENAI_BASE_URL: http://192.168.1.2:11434/v1
      PAPERLESS_AI_OPENAI_MODEL: qwen2.5:7b
      PAPERLESS_AI_OPENAI_KEY: ollama
    networks:
      - librarian-net

  gotenberg:
    image: gotenberg/gotenberg:8
    container_name: librarian-gotenberg
    restart: unless-stopped
    networks:
      - librarian-net

  tika:
    image: apache/tika:latest
    container_name: librarian-tika
    restart: unless-stopped
    networks:
      - librarian-net

  anythingllm:
    image: mintplexlabs/anythingllm:latest
    container_name: anythingllm
    restart: unless-stopped
    ports:
      - "3001:3001"
    volumes:
      - anythingllm-data:/app/server/storage
    environment:
      LLM_PROVIDER: ollama
      OLLAMA_BASE_PATH: http://192.168.1.2:11434
      OLLAMA_MODEL_PREF: qwen2.5:7b
      EMBEDDING_ENGINE: ollama
      OLLAMA_EMBEDDING_MODEL_PREF: nomic-embed-text
      VECTOR_DB: lancedb
      AUTH_TOKEN: diamondeye-anythingllm-2026
      STORAGE_DIR: /app/server/storage
    networks:
      - librarian-net

  agent-zero-librarian:
    image: frdel/agent-zero-run:latest
    container_name: agent-zero-librarian
    restart: unless-stopped
    ports:
      - "7071:80"
    volumes:
      - agent-zero-librarian-data:/a0
    environment:
      DEFAULT_MODEL: qwen2.5:7b
      OLLAMA_BASE_URL: http://192.168.1.2:11434
    networks:
      - librarian-net

  n8n-librarian:
    image: n8nio/n8n:latest
    container_name: n8n-librarian
    restart: unless-stopped
    ports:
      - "5680:5678"
    volumes:
      - n8n-librarian-data:/home/node/.n8n
    environment:
      N8N_BASIC_AUTH_ACTIVE: "true"
      N8N_BASIC_AUTH_USER: tunedr
      N8N_BASIC_AUTH_PASSWORD: Tran$4mer$
      WEBHOOK_URL: http://192.168.1.107:5680
    networks:
      - librarian-net

  nextcloud:
    image: nextcloud:latest
    container_name: librarian-nextcloud
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - nextcloud-data:/var/www/html
    networks:
      - librarian-net

  stirling-pdf:
    image: frooodle/s-pdf:latest
    container_name: stirling-pdf
    restart: unless-stopped
    ports:
      - "8020:8080"
    networks:
      - librarian-net

  excalidraw:
    image: excalidraw/excalidraw:latest
    container_name: excalidraw
    restart: unless-stopped
    ports:
      - "8030:80"
    networks:
      - librarian-net

  open-resume:
    image: openresume/open-resume:latest
    container_name: open-resume
    restart: unless-stopped
    ports:
      - "8040:3000"
    networks:
      - librarian-net
```

---

## NFS Mount (TrueNAS)

TrueNAS is at 192.168.1.106. Silvering may be in progress — mount read-only for verification, noauto.

```bash
sudo mkdir -p /mnt/truenas-canonical
# Verify NFS export is reachable:
showmount -e 192.168.1.106
# Add to /etc/fstab (noauto until silvering confirmed complete):
# 192.168.1.106:/mnt/truenas-canonical /mnt/truenas-canonical nfs ro,noauto,nofail 0 0
```

---

## AnythingLLM Workspace Configuration

After containers are up, configure via API:
- Auth: Bearer diamondeye-anythingllm-2026
- Ensure these workspaces exist:
  - DiamondEye-Research
  - Infrastructure
  - MediaMind
  - Publishing
  - Inspections
- Create "Infrastructure" first if the initial bootstrap only supports one workspace
- Use `LOCAL/axiom-staging/instruments/anythingllm_workspaces.py` to create missing workspaces from the AnythingLLM API.
- LLM: Ollama at 192.168.1.2:11434, model qwen2.5:7b
- Embedding: nomic-embed-text via Ollama
- Vector store: lancedb (default)

---

## Deployment Sequence

1. SSH to VM 107: `ssh tunedr@192.168.1.107`
2. System prep: `sudo apt update && sudo apt install -y curl git htop ufw nfs-common`
3. Install Docker: `curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker tunedr`
4. Create stack dir: `mkdir -p /home/tunedr/de-knowledge`
5. Write docker-compose.yml from above
6. `cd /home/tunedr/de-knowledge && docker compose up -d`
7. Wait ~5 min for all images to pull and services to start
8. `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"` — verify all 11 containers Up
9. Test AnythingLLM: `curl -s http://192.168.1.107:3001/api/ping`
10. ICM close-out: mkdir ~/AGENTS, scp GLOBAL/, write LOCAL/machine-config.md

---

## ICM Close-Out (Rule 15)

Before ending any build session on VM 107:
1. `mkdir -p ~/AGENTS` on VM 107
2. `scp -r /home/tunedr/AGENTS/GLOBAL/ tunedr@192.168.1.107:~/AGENTS/GLOBAL/`
3. Write `~/AGENTS/LOCAL/machine-config.md` with VM 107 details
4. Note Librarian inventory pickup (n8n-librarian on this same VM — not yet operational until n8n is configured)
