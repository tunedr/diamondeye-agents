# DiamondEye Service Map — All Running Services
# Last verified: 2026-06-11

## pop-ollama (VM 101 — 100.91.173.40)
All services are Docker-based. No systemd service units for these.
- ollama — GPU-backed inference (RTX 2060, 6GB VRAM)
- n8n Sentinel — port 5678 — generation 1 pipeline
- postiz — port 4007 — social distribution
- agent-zero — Docker
- temporal — Docker
- trilium — Docker
- glances — Docker
- de-book-sites — Docker
- GPU constraint: RTX 2060 6GB — qwen2.5-coder:7b for fleet utility. Cannot run multiple large models simultaneously.
- Model routing: llama3.2:latest @ :11434 (chat), qwen2.5-coder:7b @ :11434 (utility/code). Updated 2026-06-05.
- ACCESS NOTE: LAN IP 192.168.1.136 REACHABLE as of 2026-06-13 (sessions 5+8). Both LAN SSH (tunedr@192.168.1.136) and Tailscale SSH (100.91.173.40) confirmed. Ollama port 11434 accessible via LAN directly from MGMT-XPS.

## orchestrator (VM 104 — 100.108.23.97)
- n8n Atlas — port 5679 — generation 2 pipeline (ACTIVE — not yet frozen as of 2026-06-11)
- Atlas orchestration — Notion Bridge v2
- Grist — port 8484 — evidence ledger (LIVE, verified 2026-06-11 via HTTP probe)
- SSH: Tailscale-only (100.108.23.97). LAN SSH blocked by design.

## Unraid (Tower — 100.120.180.114 / LAN 192.168.1.2)
- Ollama — port 11434 — fleet chat/embed models (llama3.2:latest, nomic-embed-text)
- ARR suite (Sonarr, Radarr, etc.)
- Media stack / Plex

## de-librarian-01 (VM 107 — 192.168.1.107)
- hermes-librarian — port 8642 — Hermes AI agent (Librarian profile, llama3.2 via Ollama) — RUNNING
- hermes-apollo — port 8643 — OSINT/investigation agent — RUNNING
- hermes-coder — port 8645 — code task agent — RUNNING
- hermes-truthlens — port 8644 — truth-lens agent — RUNNING
- agent-zero-librarian — port 7071 — A2A executor — RUNNING
- n8n-librarian — port 5680 — scheduled workflows — RUNNING
- anythingllm — port 3001 — RAG knowledge base — RUNNING
- paperless-ngx — port 8010 — document archive — RUNNING
- agent-zero-axiom — port 7073 — background investigations — RUNNING
- excalidraw — port 8030 — diagrams — RUNNING

## MGMT-XPS (this machine — 100.76.233.89)
- Claude Code — interactive execution (primary escalation executor)
- Agent Zero (agent-zero-desk) — port 50080 — execution orchestrator
- hermes-desk — port 8642 — Hermes AI agent (Desk profile, GPT-4o / openai-codex currently)
- hermes-librarian — local bridge instance, port mapped — RUNNING (llama3.2 via Ollama)
- hermes-researcher — RUNNING
- hermes-godmode — RUNNING
- hermes-coder — RUNNING
- openclaw-desk — port 18789 — STOPPED/RETIRED (2026-06-13 session 9). Container preserved. Rollback: docker start openclaw-desk.

## Access Path Verification Notes (verified 2026-06-13 — session 9)
- pop-ollama (100.91.173.40): Tailscale CONFIRMED. LAN 192.168.1.136 CONFIRMED (sessions 5+8 fixed asymmetric routing). Both paths valid.
- pve-studio (192.168.1.4): LAN ping and SSH live. Tailscale path broken (not installed).
- de-truenas-01 (192.168.1.106): status unknown.
- Unraid / de-gateway-01 (192.168.1.2): LAN ping CONFIRMED. SSH blocked (permission denied). Web routes :3000, :3002, :7072 respond.
- de-librarian-01 (192.168.1.107): LAN ping CONFIRMED. SSH CONFIRMED. Service ports 3001/5680/7071/8642 live.
- VM104 orchestrator (192.168.1.19): LAN ping CONFIRMED. SSH blocked (Tailscale-only). n8n :5679 and Grist :8484 HTTP confirmed.
- de-pubmachine-01 (192.168.1.48): status unknown.
- de-edge-01 (192.168.1.36): LAN ping, SSH, and web UI on 8888 confirmed (per prior session).
- affiliate-engine-01 (192.168.1.55): status unknown.
