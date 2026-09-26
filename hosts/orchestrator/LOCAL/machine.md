# Machine Identity — orchestrator (VM104)

- Hostname: orchestrator
- Role: Pipeline Orchestration Layer — Atlas n8n, Notion Bridge, Grist evidence ledger
- LAN IP: 192.168.1.19 (SSH blocked by design — Tailscale only)
- Tailscale IP: 100.108.23.97
- Primary user: tunedr
- Home directory: /home/tunedr
- VM ID: 104 (Proxmox pve-studio, 192.168.1.4)
- OS: Ubuntu 24.04.3 LTS, kernel 6.8.0-124-generic
- Disk: 38G LVM (`ubuntu--vg-ubuntu--lv`), 39% used as of 2026-06-16
- RAM: 6.2GB allocated
- CPU: 2 cores

## Access
- SSH: `ssh tunedr@100.108.23.97` (Tailscale only — LAN SSH blocked by design)
- LAN IP responds to HTTP (n8n :5679, Grist :8484) but SSH is Tailscale-only

## Role in DiamondEye Stack
This machine is the generation 2 pipeline orchestration layer. It runs:
- n8n Atlas (generation 2 pipeline) — port 5679
- Notion Bridge v2 (orchestrator-notion-bridge) — port 9102
- orchestrator-agent-runner — port 9101
- orchestrator-claude-server (no exposed port)
- Grist evidence ledger — port 8484

## Docker Compose Location
- Orchestrator stack: /root/orchestrator/docker-compose.yml (root-owned)
- Grist: standalone container (`docker start/stop grist`), data at /home/tunedr/grist-data/
- Grist restart policy: unless-stopped (set 2026-06-16)

## Hard Rules for This Machine
- NEVER modify Atlas n8n workflows without pausing the pipeline first
- NEVER reboot without explicit Branden approval (production pipeline machine)
- SSH access is Tailscale-only — do not attempt LAN SSH

## Known History
- 2026-06-16: ext4 journal abort on /dev/dm-0 caused all I/O to return EIO, taking down SSH and Grist.
  Root cause was a jbd2 error. Resolved by hard reset via `qm reset 104` on pve-studio.
  errors_count confirmed 0 after reboot. Grist was stopped (RestartPolicy=no, exited 4 weeks prior) — started manually.
- networkd-dispatcher fleet fix (50-fix-tailscale-routing) confirmed present in /etc/networkd-dispatcher/routable.d/
