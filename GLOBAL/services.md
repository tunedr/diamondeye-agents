# DiamondEye Service Map — All Running Services

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
- GPU constraint: RTX 2060 6GB — DeepSeek 7B Q4 fits barely. Cannot run DeepSeek + Whisper simultaneously.

## orchestrator (VM 104 — 100.108.23.97)
- n8n Atlas — port 5679 — generation 2 pipeline
- Atlas orchestration — Notion Bridge v2
- Primary executor: Ollama/DeepSeek (default), Claude API (escalation only)

## Unraid (Tower — 100.120.180.114)
- Ollama — port 11434 — secondary inference
- ARR suite (Sonarr, Radarr, etc.)
- Media stack

## MGMT-XPS (this machine — 100.76.233.89)
- Claude Code — interactive execution
- Codex CLI — interactive execution
- Agent Zero — chat/orchestration layer on port 50080

## Access Path Verification Notes
- pop-ollama (100.91.173.40 / 192.168.1.136): reachable by ping on both Tailscale and LAN; SSH on Tailscale succeeds; LAN SSH currently hits host-key verification in batch mode; Ollama, n8n Sentinel, Agent Zero, Postiz, Temporal, Trilium, Glances, and de-book-sites are live.
- pve-studio (100.99.40.111 / 192.168.1.4): Tailscale ping and SSH timed out, but LAN ping, LAN SSH, and the Proxmox UI on 8006 are live.
- de-truenas-01 / TrueNAS reference (100.76.34.69 / 192.168.1.106): Tailscale ping and SSH timed out, but LAN ping, LAN SSH refusal, and the web UI redirect to /ui are live.
- de-gateway-01 (100.120.42.102 / 192.168.1.2): reachable by ping on both Tailscale and LAN; SSH on both paths fails with permission denied; web routes on 3000, 3002, and 7072 respond.
- de-librarian-01 (192.168.1.107): LAN ping, SSH, and service ports 3001 / 5680 / 7071 are live; no Tailscale path is documented.
- de-pubmachine-01 (192.168.1.48): LAN ping failed and SSH returned no route to host in this verification.
- de-edge-01 (192.168.1.36): LAN ping, SSH, and web UI on 8888 are live.
- affiliate-engine-01 (192.168.1.55): LAN ping failed and SSH returned no route to host in this verification.
