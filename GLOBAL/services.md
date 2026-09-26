# DiamondEye Service Map — All Running Services
# Last verified: 2026-08-10 (IP conflict resolution — session 3b86d271-f21c-8127-b4f9-fb0ce4cde1ac)
# Fleet Reference DB (2026-07-25): f80b61810eca46a08466bf3174926d99

## pop-ollama (VM 101 — 100.91.173.40 / LAN 192.168.1.136)
SSH: tunedr@192.168.1.136 (LAN) or tunedr@100.91.173.40 (Tailscale) — both confirmed.
Docker containers (all RUNNING):
- ollama — :11434 — GPU-backed inference (RTX 2060, 6GB VRAM). Models: qwen2.5-coder:7b, llama3.2, gemma3, deepseek-r1, phi3:3.8b, llama3:8b, deepseek-coder:6.7b, mistral, nomic-embed-text
- n8n Sentinel — :5678 — generation 1 pipeline (Sentinel)
- postiz-proxy (nginx) — :4007 — social distribution frontend
- postiz — internal — social distribution app
- agent-zero — :7070 — legacy container (preserved)
- temporal — :7233-7235 — workflow engine
- temporal-postgres, postiz-redis, postiz-postgres — internal
- trilium — :8080 — notes (up 7 min as of 2026-08-06 — recently restarted)
- glances — :61208 — monitoring
- de-book-sites — :8090/:8091 — nginx book sites
- tdarr-node-popollama — internal — media transcoding node
Bare-metal processes:
- cline-api.py — :8766 — Cline HTTP API (active since Jul 14; still runs but NOT wired to Desk as of 2026-07-20)
- cline-ollama-proxy.py — 127.0.0.1:11435 — Ollama proxy for Cline (active since Jun 22)
- cline hub daemon — 127.0.0.1:25463 — Cline background daemon
Systemd: coding-agent.service (Autonomous Coding Agent Runner) — RUNNING (NOT in services.md previously)
GPU constraint: RTX 2060 6GB — cannot run multiple large models simultaneously.

## orchestrator (VM 104 — 100.108.23.97 / LAN 192.168.1.19)
SSH: Tailscale-only (tunedr@100.108.23.97). LAN SSH blocked by design.
Nginx systemd service running. Docker containers (all RUNNING unless noted):
- atlas-v2 — :8080 — Atlas v2 agent (up 3 weeks as of 2026-08-06; NOT in prior services.md)
- orchestrator-n8n — :5679 — generation 2 pipeline / Atlas n8n (ACTIVE)
- orchestrator-notion-bridge — :9102 (mapped from 9101) — Notion Bridge v2
- orchestrator-agent-runner — :9101 (mapped from 9100) — Agent Runner
- orchestrator-claude-server — no external port — Claude server process
- grist — :8484 — evidence ledger (RESTORED 2026-06-21; forensic: 3876d271-f21c-814f-85ae-fdff4dfc519a)
- orchestrator-n8n-new — EXITED (exited 2 months ago — stale container, do not restart without task card)

## Unraid (Tower — 100.120.180.114 / LAN 192.168.1.2)
SSH: root@192.168.1.2 confirmed. Docker containers (RUNNING):
- ollama — :11434 — fleet chat/embed models. Models: nomic-embed-text, llama3.1:8b, llama3.2:latest, qwen2.5:7b, deepseek-r1, catsarethebest/llama3.2-4oClaude
- openwebui — :3010 (NOT :3000 — port 3000 is arr-dashboard)
- openclaw-gateway — :7075 (NOT :7074 as in prior docs)
- agent-zero (MediaMind) — :50080
- uptime-kuma — :3002
- n8n-gateway — :5680
- SearXNG — :8081
- MCP-Searxng — :3333
- kasm — :3322
- HELFINANCE — :3210 (has its own Tailscale node: 100.105.140.24, hostname 'helfinance')
- arr-dashboard — :3000
- tg-poller-mediamind — internal
- binhex-plexpass, binhex-sonarr (:8989), binhex-radarr (:7878), binhex-sabnzbdvpn (:8080)
- bazarr (:6767), tdarr (:8264-8266), tdarr_node, recyclarr
- Ombi (:5000), Huntarr (:9705), requestrr (:4545)
- binhex-delugevpn, binhex-prowlarr (:9696), binhex-flaresolverr (:8191), binhex-krusader (:6080)
- n8n — :5678
CREATED (not running): Maintainerr, Configarr, plex-utills

## de-librarian-01 (VM 107 — 100.74.175.56 / LAN 192.168.1.107)
SSH: tunedr@192.168.1.107 (LAN) — confirmed. Tailscale: 100.74.175.56 — ONLINE.
⚠️ ALL 5 HERMES CONTAINERS EXITED — confirmed 2026-07-25 and 2026-08-06.
hermes-librarian (:8642), hermes-librarian-guru (:8646), hermes-apollo (:8643), hermes-coder (:8645), hermes-truthlens (:8644): NOT PRESENT in docker ps.
Tunnel services on MGMT-XPS (librarian-tunnel.service, librarian-guru-tunnel.service): DISABLED.
Branden decision needed: intentionally removed or needs rebuild?

Docker containers RUNNING:
- n8n-librarian — :5680 (mapped from 5678) — scheduled workflows (up 7 weeks)
- agent-zero-axiom — :7073 — AXIOM (up 7 weeks)
- agent-zero-librarian — :7071 — legacy container (up 8 weeks; abandoned for active workflows)
- librarian-gotenberg — :3000 — PDF generation (up 2 months)
- openclaw-axiom-openclaw-gateway-1 — :7074/:18790 — OpenClaw gateway (up 2 months, healthy)
- anythingllm — :3001 — RAG knowledge base (up 2 months, healthy)
- paperless-ngx — :8010 — document archive (up 2 months, healthy)
- librarian-nextcloud — :8080 — Nextcloud (up 2 months; NOT in prior docs)
- stirling-pdf — :8020 — PDF tools (up 2 months, healthy; NOT in prior docs)
- librarian-postgres, librarian-redis, librarian-tika — internal
- excalidraw — :8030 — diagrams (up 2 months, healthy)

## MGMT-XPS (this machine — 100.76.233.89 / LAN 192.168.1.221)
Docker containers RUNNING (verified 2026-08-06):
- hermes-desk — :8642 (API), :9125→9124 (dashboard) — Branden's primary PA. Docker uid 10000. HERMES_HOME=/opt/data. Model: gpt-5.5/openai-codex (updated 2026-09-11 power outage recovery; was gpt-5.4 pre-2026-09-05). Fallbacks: gemini, groq, cerebras, openrouter. Cline NOT in Desk's execution path (excluded 2026-07-20).
- anythingllm-desk — 127.0.0.1:3002→3001 — local RAG for guru-routing. Wired to Groq llama-3.3-70b-versatile. Fleet workspace verified end-to-end. Up 12 days (healthy).
- honcho — host network :8000 — memory/peer coordination for hermes-desk. Up 26h (started 2026-08-05 after Honcho fix — prior dummy key caused 9-min delay).
- honcho-postgres — :5433→5432 — Honcho database. Up 2 weeks.
- agent-zero-desk — :50080→80 — legacy container (up 2 weeks; NOT active authority; preserved).
Docker containers EXITED:
- hermes-librarian, hermes-researcher, hermes-godmode, hermes-coder — all EXITED
- openclaw-desk — EXITED (retired 2026-06-13; container preserved for rollback)
Systemd services:
- desk-escalation-watcher.service (system) — ACTIVE/RUNNING since 2026-07-21. Watches /home/tunedr/desk-escalations/ for escalate_*.sh files → opens tmux session with claude CLI.
- a0-escalation-watcher.service (system) — ACTIVE/RUNNING since 2026-07-21.
- openclaw-gateway.service (user) — RETIRED 2026-09-07. Service unit deleted, npm package uninstalled (331 packages removed), /home/tunedr/.openclaw/ removed (815MB freed). Port 18789 no longer in use. Rollback archive: /home/tunedr/archives/openclaw-retired-20260907-032255/ (SHA256: 4fbec81dd7b62fdb708847b53801ffc275945598fd6ba5727b63fd54aff885d6). Forensic: 3d46d271-f21c-81ad-b2ff-c93473a7959b.
- hermes-dashboard.service (system) — STOPPED + DISABLED 2026-09-07. Was crash-looping; ExecStart pointed at non-existent path. Disabled prior to xps_pa archival.
- Odin (hermes-gateway, bare-metal, user tunedr) — LIVE; Level 2 Commissioned 2026-09-19. Hermes Agent v0.21.3 (2026.9.14) bce20d0b at HERMES_HOME=~/.hermes/. Model: openai-codex/gpt-5.5 (ChatGPT subscription OAuth; migrated 2026-09-20; no automatic Anthropic fallback; rollback = restore backup config). Services: hermes-gateway.service (Telegram @diamondeye_gateway_bot, PID 3955957, restarted 2026-09-20), hermes-serve.service (:9119, PID 3962906), hermes-dashboard.service (:9120, PID 3962909, public_url mgmt-xps.turtle-sunfish.ts.net:9120), hermes-webui.service (:9121, PID 1802003, Hermex/iPhone frontend, tailnet-only, HUMAN IPHONE GATE pending). cua-driver 0.23.2 (AT-SPI/X11 PASS). Notion MCP OAuth proven read+write 2026-09-12. ntn v0.18.1 installed. post_turn_capture hook active since 2026-09-12. Level 2 forensic: 3dc6d271-f21c-8145-8ac9-f90869350891. Migration forensic: 3e26d271-f21c-81b2-8b95-c325760f20b6. Initial pilot forensic: 3d46d271-f21c-81ad-b2ff-c93473a7959b.
xps_pa (ARCHIVED 2026-09-07):
- Profile data moved from /home/tunedr/hermes/profiles/xps_pa/ to /home/tunedr/Downloads/hermes-xps-pa-archive-20260907-032040/hermes-xps-pa-home/. SHA256 manifest on file.
- HERMES_HOME was /home/tunedr/hermes (NOT /home/tunedr/.hermes). Both paths now cleared.
- hermes-gateway.service (user) — was DEAD since 2026-07-16. hermes-dashboard.service disabled 2026-09-07.
- Telegram @Xps_pa_diamondeye_bot: token preserved in archive. Not actively served.
Claude Code — interactive escalation executor (tmux session hermes-claude, --dangerously-skip-permissions)

## ha-control (VM 100 — LAN 192.168.1.100 static)
- Home Assistant OS — web UI :8123 (HTTP 200 confirmed 2026-08-10 post-fix)
- No SSH, no Tailscale
- QEMU guest agent: RUNNING — qm guest exec 100 from pve-studio WORKS (confirmed 2026-08-10)
- HA CLI: /usr/bin/ha available via guest exec
- Current addressing: STATIC 192.168.1.100/24 via ha network update (2026-08-10 22:36 UTC)
- Target addressing: DHCP via pfSense reservation bc:24:11:79:43:dd → .100 (PENDING — Branden)
- Once pfSense reservation exists: run qm guest exec 100 -- /usr/bin/ha network update enp6s18 --ipv4-method auto to revert to DHCP
- IP conflict with VM108 RESOLVED 2026-08-10 (session 3b86d271-f21c-8127-b4f9-fb0ce4cde1ac)

## de-pubmachine-01 (VM 102 — LAN 192.168.1.48)
SSH: tunedr@192.168.1.48 — confirmed. No Tailscale. Docker containers RUNNING (all up ~2 weeks):
- inspections-web — :8081 — DiamondEye Inspections web (NOT in prior docs)
- agent-zero-publishing — :7071 — publishing lane (legacy; still running)
- shlink — :8080 — link shortener (NOT in prior docs)
- n8n — :5678 — workflow automation
- pub-postgres, pub-n8n-postgres — internal

## de-edge-01 (VM 103 — 100.99.172.65 / LAN 192.168.1.36)
SSH: tunedr@192.168.1.36 (LAN) — confirmed. Tailscale: 100.99.172.65 (hostname de-edge-01, NOT turtle-sunfish).
Systemd services: nginx.service, ddclient.service (DDNS), tailscaled.service — all RUNNING.
Docker containers RUNNING:
- dashboard-frontend — :8888
- dashboard-backend — :8889
- npm / Nginx Proxy Manager — :80/:81/:443
NPM proxy hosts: resume.diamondeye.net (host 15→VM105:3000), serberus.diamondeye.net (host 16→VM108:9124)

## affiliate-engine-01 (VM 105 — LAN 192.168.1.55)
SSH: tunedr@192.168.1.55 (diamondeye_key) — confirmed. No Tailscale. Docker containers RUNNING:
- resume-tool — :3000 — Tool-06 AI Resume Tailor (up 13 days as of 2026-07-25)
- agent-zero-affiliate — :7072 — affiliate lane (legacy)
- ae-n8n — :5679 — n8n affiliate workflows
- ae-postgres, ae-redis — internal

## de-truenas-01 (VM 106 — LAN 192.168.1.106)
No Tailscale. SSH: returns "Permission denied (publickey)" — SSH key not provisioned on MGMT-XPS for this host.
Web UI: HTTP/HTTPS :80/:443 respond (302 redirect confirmed 2026-07-25).
HTTPS API: 401 Unauthorized (no TrueNAS API token available in fleet sessions).
Proxmox: VM106 RUNNING, 8192MB RAM, 32GB disk. Internal services UNKNOWN.

## serberus-hermes (VM 108 — 100.67.35.31 / LAN 192.168.1.108 static)
ADDED 2026-08-01. SSH: confirmed. Tailscale: 100.67.35.31 (enrolled as serberus-hermes).
- Hermes v0.19.0 — bare-metal install (via PyPI)
- hermes-dashboard.service — systemd user service (linger enabled), port 9124 (0.0.0.0). Active since 19:14:52 UTC 2026-08-10.
- Auth gate: basic auth, username Serberus, scrypt hash
- Domain: serberus.diamondeye.net → NPM proxy host 16 on de-edge-01 → 192.168.1.108:9124
- SSL: Cloudflare Origin Cert ID 1 (expires 2041). External HTTPS LIVE — HTTP 200 confirmed 2026-08-10 22:37 UTC.
- Addressing: guest-level static 192.168.1.108/24 via Netplan (confirmed; no DHCP). IP conflict with VM100 RESOLVED 2026-08-10.
- Open items: pfSense DHCP reservation bc:24:11:c2:78:75 → .108 (Branden, optional); openai-codex OAuth config
- Runbook: 3ae6d271-f21c-8174-a522-f2aa6a75ea2d. Conflict resolution: 3b86d271-f21c-8127-b4f9-fb0ce4cde1ac

## Access Path Verification Notes (verified 2026-08-06 — Agent Registry session)
- pop-ollama (192.168.1.136 / 100.91.173.40): LAN + Tailscale SSH CONFIRMED. Ollama :11434 CONFIRMED.
- pve-studio (192.168.1.4): LAN SSH CONFIRMED. Tailscale 100.99.40.111 enrolled but OFFLINE (83+ days).
- de-truenas-01 (192.168.1.106): Web reachable. SSH: permission denied (no key). Status PARTIAL.
- Unraid (192.168.1.2 / 100.120.180.114): SSH root CONFIRMED. Tailscale ONLINE.
- de-librarian-01 (192.168.1.107 / 100.74.175.56): LAN + Tailscale CONFIRMED. SSH CONFIRMED.
- VM104 orchestrator (100.108.23.97): Tailscale SSH CONFIRMED. LAN SSH blocked by design.
- de-pubmachine-01 (192.168.1.48): SSH CONFIRMED (diamondeye_key). No Tailscale.
- de-edge-01 (192.168.1.36 / 100.99.172.65): SSH CONFIRMED. NPM web UI CONFIRMED.
- affiliate-engine-01 (192.168.1.55): SSH CONFIRMED (diamondeye_key). No Tailscale.
- ha-control (192.168.1.108 DHCP): Web :8123 CONFIRMED. No SSH/Tailscale.
- serberus-hermes (192.168.1.108 DHCP / 100.67.35.31): SSH CONFIRMED. Dashboard :9124 CONFIRMED. External HTTPS CONFIRMED.
