# DIAMONDEYE-STATE.md
# Living fleet state document — owned by Librarian once operational.
# Updated on schedule (target: every 2 hours when Librarian is running).
# Any AI reading this: treat all fields as verified unless marked [UNVERIFIED].
# Do not modify this file manually. Do not guess at field values.
# Last updated: 2026-06-12 (Pipeline repair — SSH mount + tool compliance resolved — Claude Code session 6)
# Architecture: Three-Agent Architecture (Hermes Desk → Agent Zero → Claude Code). Atlas/V2 superseded.

---

## SECTION 1: FLEET HEALTH
# Format: Machine | LAN IP | Tailscale IP | Reachable | Last Verified
# Reachable = YES / NO / UNKNOWN

| Machine | LAN IP | Tailscale IP | Reachable | Last Verified |
|---|---|---|---|---|
| pve-studio (Proxmox host) | 192.168.1.4 | 100.99.40.111 (path broken) | YES (LAN only) | 2026-05-27 |
| VM101 pop-ollama | 192.168.1.136 | 100.91.173.40 | YES (LAN + Tailscale — accept-routes=false applied 2026-06-12, see session 5 Notion record) | 2026-06-12 |
| VM102 de-pubmachine-01 | 192.168.1.48 | [UNVERIFIED] | UNKNOWN | 2026-05-25 |
| VM103 de-edge-01 | 192.168.1.36 | [UNVERIFIED] | UNKNOWN | never |
| VM104 orchestrator | 192.168.1.19 | 100.108.23.97 | YES (LAN ping; SSH Tailscale-only) | 2026-06-11 |
| VM105 affiliate-engine-01 | 192.168.1.55 | [UNVERIFIED] | UNKNOWN | 2026-05-25 |
| VM106 de-truenas-01 | 192.168.1.106 | [UNVERIFIED] | UNKNOWN | 2026-05-25 |
| VM107 de-librarian-01 | 192.168.1.107 | [UNVERIFIED] | YES (LAN ping + SSH confirmed) | 2026-06-11 |
| VM108 de-gateway-01 | 192.168.1.2 | 100.120.42.102 | YES (Tailscale) | 2026-05-27 |
| VM100 ha-control | 192.168.1.100 | [UNVERIFIED] | UNKNOWN | 2026-05-25 |
| MGMT-XPS | 192.168.1.221 | 100.76.233.89 | YES | 2026-05-27 |
| Unraid | 192.168.1.2 | 100.120.180.114 | YES (LAN) | 2026-05-23 |
| pfSense | 192.168.1.1 | 100.102.75.124 | YES | 2026-05-27 |

---

## SECTION 2: SERVICE STATUS
# Format: Service | Machine | Port | Status | Last Verified
# Status = HEALTHY / DEGRADED / DOWN / UNKNOWN

| Service | Machine | Port | Status | Last Verified |
|---|---|---|---|---|
| Ollama (Docker, GPU) | VM101 | 11434 | HEALTHY (generate tested 2026-06-12) | 2026-06-12 |
| coding-agent | VM101 | 9100 | HEALTHY | 2026-05-27 |
| claude-server | VM101 | 9099 | UP (credits_paused=true) | 2026-05-27 |
| agent-zero | VM101 | 7070 | HEALTHY | 2026-05-27 |
| n8n Sentinel | VM101 | 5678 | UP (scanner inactive by design) | 2026-05-27 |
| notion-bridge | VM104 | 9101 internal (ext 9102) | HEALTHY (git installed 2026-05-26) | 2026-05-26 |
| n8n Atlas | VM104 | 5679 | HEALTHY | 2026-05-27 |
| Atlas Task Scanner | VM104 | n8n workflow Iyts70flbCG4sKub | ACTIVE (re-enabled 2026-05-27) | 2026-05-27 |
| Atlas Dead Man Monitor | VM104 | n8n workflow | ACTIVE | 2026-05-27 |
| Atlas Completion Handler | VM104 | n8n workflow | ACTIVE | 2026-05-27 |
| agent-zero-librarian | VM107 | 7071 | RUNNING (Up 2+ days) | 2026-06-11 |
| AnythingLLM | VM107 | 3001 | RUNNING (Up 4+ days, healthy) | 2026-06-11 |
| hermes-librarian | VM107 | 8642 | RUNNING (Up 20 hours) | 2026-06-11 |
| hermes-apollo | VM107 | 8643 | RUNNING (Up 20 hours) | 2026-06-11 |
| hermes-coder | VM107 | 8645 | RUNNING (Up 20 hours) | 2026-06-11 |
| hermes-truthlens | VM107 | 8644 | RUNNING (Up 20 hours) | 2026-06-11 |
| n8n-librarian | VM107 | 5680 | RUNNING (Up 4+ days) | 2026-06-11 |
| Grist | VM104 | 8484 | LIVE (HTTP probe confirmed) | 2026-06-11 |
| n8n Atlas | VM104 | 5679 | HEALTHY — NOT YET FROZEN | 2026-06-11 |
| Ollama (Unraid, CPU) | Unraid | 11434 | [UNVERIFIED] | never |
| hermes-desk | MGMT-XPS | 8642 | RUNNING — API server ACTIVE on 0.0.0.0:8642 | 2026-06-12 |
| agent-zero-desk | MGMT-XPS | 50080 | RUNNING (Up 3 days) | 2026-06-11 |
| openclaw-desk | MGMT-XPS | 18789 | RUNNING/healthy (Up 3 days) | 2026-06-11 |
| Home Assistant | VM100 | 8123 | UP (web reachable) | 2026-05-26 |

---

## SECTION 3: OPEN BLOCKERS
# Human-gated items only. Things that cannot proceed without Branden action.

1. VM102 and VM105 — SSH never confirmed. DHCP reservations fixed (2026-05-25) but services on these VMs have not been verified.
2. VM100 ha-control — pfSense reservation corrected to .100 (2026-05-25) but HA OS is not confirmed at that IP (no SSH addon installed). Verify via Proxmox console or install HA SSH addon.
3. Codex OAuth on MGMT-XPS — expired as of 2026-05-23. Needs interactive reauth. NOTE: Three-Agent architecture removes Codex from hermes-desk (Phase 4) — this blocker may become moot.
4. watchdog.py on VM101 — STOPPED AND DISABLED (2026-06-12, session 4). watchdog.service disabled in user systemd (symlink removed). Do not restart until inode retention guard is implemented and Branden approves. Root cause of stop: watchdog.py was consuming 7.2 GiB RAM + exhausting 23 GiB swap, causing VM101 SSH/ICMP failures. Session record: Notion 37d6d271-f21c-810f-9c84-fe15c79701b9.
5. DIAMONDEYE-STATE.md Librarian automation — this document is manually seeded. Librarian scheduled sync not yet wired.
6. pve-studio Tailscale path broken — Tailscale peer exists (100.99.40.111) but path non-functional. LAN only for now.
7. [RESOLVED 2026-06-12] VM101 QEMU guest agent — was unresponsive during OOM condition in session 4. Confirmed functional after memory recovery: used successfully in sessions 4 and 5 for nftables dump and tcpdump. Both access paths now valid: qm guest exec via Proxmox SSH (root@192.168.1.4) AND Tailscale SSH (tunedr@100.91.173.40) AND LAN SSH (tunedr@192.168.1.136).
8. Atlas Dead Man Monitor n8n expressions broken — IF node uses {{ .body || }} (should be {{ $json.body }}), Telegram chatId uses {{ .TELEGRAM_CHAT_ID }} (should be {{ $env.TELEGRAM_CHAT_ID }}). Needs 2-field fix in n8n UI at http://192.168.1.19:5679.
9. [RESOLVED 2026-05-26] notion-bridge git blocker — FIXED. git 2.47.3 installed via apt.
10. VM106 de-truenas-01 — IPv4 status unknown. DHCP reservation set to .106 (2026-05-25) but VM has no ARP presence. Needs console investigation.
11. [RESOLVED 2026-06-12] pop-ollama LAN fully reachable — Root cause identified and fixed in session 5. MGMT-XPS and VM101 were accepting pfSense's Tailscale-advertised 192.168.1.0/24 subnet route (table 52, priority 5270), causing return traffic to hairpin through pfSense. pfSense stateful firewall dropped asymmetric replies. Fix: `tailscale set --accept-routes=false` on both hosts. LAN ping (0% loss, 0.3ms), LAN SSH, Tailscale SSH, and Ollama TCP/11434 all verified passing. Session 5 Notion record: 37d6d271-f21c-8120-9f29-dab60b497aa9.
12. [RESOLVED 2026-06-11] Three-Agent Architecture Build — COMPLETE. All phases executed. Open items: OPENAI_API_KEY needed for GPT-4o/GPT-4o-mini upgrades; Grist down on VM104 (needs Proxmox console access); Librarian 1:30am cron job not yet created; full Telegram smoke test pending. Final session record: Notion 37d6d271-f21c-812e-ab5b-cf5417d69c5c.
13. Grist down on VM104 — port 8484 connection refused as of 2026-06-11 (was LIVE earlier same day). VM104 SSH inaccessible (LAN port 22 blocked by design; Tailscale SSH resets — may indicate Tailscale stopped on VM104). Use Proxmox console to investigate. Blocker task: Notion 37d6d271-f21c-814b-acba-dc81d5a5b543.
14. Librarian 1:30am cron job not created — hermes-librarian on VM107 has cron_mode:auto and timezone:America/Denver configured but no jobs in jobs.json. Must create the maintenance cron job before first scheduled run.
15. OpenAI API key missing — OPENAI_API_KEY not in CREDENTIALS.env on VM101 or MGMT-XPS. Blocks GPT-4o upgrade for hermes-desk and GPT-4o mini upgrade for hermes-librarian. Both currently using Unraid local models (functional but not at target).
16. [RESOLVED 2026-06-12] agent-zero-desk SSH keys — Fixed in session 6. Container was started manually (not Compose). Bind-mount failed due to UID mismatch (host UID 1000 vs container root). Solution: named Docker volume `agent-zero-desk-ssh` populated with root-owned key copies via busybox helper. SSH verified: VM101 LAN, VM101 Tailscale, VM107 LAN all pass. Runbook: 37d6d271-f21c-81a8-80b5-d10aed50dea6.
17. [RESOLVED 2026-06-12] Agent Zero tool-name compliance — Root cause: context contamination in long sessions, not a model limitation. qwen2.5:7b correctly emits `code_execution_tool` in clean context (verified via direct Ollama API test). Agent Zero retry/nudge mechanisms handle transient drift. No model change required. Runbook: 37d6d271-f21c-81a8-80b5-d10aed50dea6.
18. [RESOLVED 2026-06-12] MGMT-XPS ↔ VM101 LAN block — Root cause: pfSense-advertised 192.168.1.0/24 subnet route in Tailscale table 52 on both hosts caused asymmetric routing (forward via LAN enp3s0→enp6s18, return via Tailscale→pfSense). pfSense stateful firewall dropped orphaned replies. Fix: `tailscale set --accept-routes=false` on MGMT-XPS (local sudo) and VM101 (via Proxmox QEMU agent). Fully verified. Session 5 Notion record: 37d6d271-f21c-8120-9f29-dab60b497aa9. Doctrine: see standing rule 13.

---

## SECTION 4: AUTH TOKEN STATUS
# Format: Service | Machine | Status | Last Verified
# Do not store secret values here — reference credential locations only.
# All secrets stored in: /home/tunedr/diamondeye/CREDENTIALS.env (VM101) synced to ~/CREDENTIALS.env (MGMT-XPS)

| Service | Machine | Status | Last Verified |
|---|---|---|---|
| Claude Code OAuth | MGMT-XPS | ACTIVE (running since May 21) | 2026-05-27 |
| Codex OAuth | MGMT-XPS | EXPIRED — needs reauth | 2026-05-23 |
| Claude Code OAuth | Laptop WSL | [UNVERIFIED] | unknown |
| Codex OAuth | Laptop WSL | [UNVERIFIED] | unknown |
| Notion API (n8n bot, CREDENTIALS.env NOTION_TOKEN) | VM104 | ACTIVE | 2026-05-27 |
| Notion API (claude-code bot) | MGMT-XPS | ACTIVE | 2026-05-23 |
| Telegram (@De_atlas_bot) | VM104 n8n | ACTIVE | 2026-05-27 |
| Telegram (VM101 monitoring) | VM101 | ACTIVE | 2026-05-27 |

---

## SECTION 5: STANDING RULES
# These cannot be violated. No exceptions. No AI overrides these.
# See GLOBAL/rules.md for the full authoritative rule set with rationale.
# This section is a quick-reference summary only.

1. VM ISOLATION — every session targets only explicitly named VMs. Do not make changes to other machines unless listed in the prompt.
2. NO PIPELINE FIXING PIPELINE — infrastructure repair tasks do not go into the Atlas Notion Tasks DB. Route to human-gated XPS lane.
3. NO GUESSING ON CREDENTIALS — if a credential name, endpoint URL, or IP is not in this document or CREDENTIALS.env, stop and ask.
4. WRITEBACK REQUIRED — no session closes without a Notion session record. No exceptions.
5. NO WATCHDOG RESTART — watchdog.py on VM101 must not restart until inode retention guard is implemented and Branden approves.
6. ATLAS SCANNER STATE — re-enabled 2026-05-27. Monitor first jobs carefully. If scanner causes issues, pause via n8n API before any other action.
7. READ THIS FILE FIRST — any AI starting a session must read DIAMONDEYE-STATE.md before taking any action.
8. SWAPFILE ACTIVE ON VM101 — /swapfile (8 GiB) is active and fstab-persistent. Do not remove or modify.
9. OLLAMA MEMORY GUARD ACTIVE — KEEP_ALIVE=5m, MAX_LOADED_MODELS=1, NUM_PARALLEL=1. Do not change without authorization.
10. NO STALE IP ASSUMPTIONS — always verify IPs from this document. Do not use IPs from memory or old session records.
11. SECRETS NOT IN DOCS — credential values must never appear in documentation. Reference the CREDENTIALS.env path only.
12. GLOBAL/ IS GIT-OWNED — changes to GLOBAL/ files must be committed and pushed. Librarian propagates; do not scp manually.
13. ACCEPT-ROUTES OFF ON LAN-CONNECTED HOSTS — any host with a native LAN interface (MGMT-XPS, all VMs) must have `tailscale set --accept-routes=false`. Accepting pfSense's 192.168.1.0/24 subnet route puts it in Tailscale table 52 (priority 5270 > main table 32766), which overrides native LAN routing and causes asymmetric pfSense hairpin. pfSense drops the orphaned return traffic. Remote Tailscale nodes without physical LAN access may accept this route. Verify with: `ip route show table 52 | grep 192.168.1` — must return nothing. Root cause record: Notion 37d6d271-f21c-8120-9f29-dab60b497aa9.
