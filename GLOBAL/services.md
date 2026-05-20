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
