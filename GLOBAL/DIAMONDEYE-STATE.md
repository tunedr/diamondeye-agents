# DIAMONDEYE-STATE.md
# Living fleet state document — owned by Librarian once operational.
# Updated on schedule (target: every 2 hours when Librarian is running).
# Any AI reading this: treat all fields as verified unless marked [UNVERIFIED].
# Do not modify this file manually. Do not guess at field values.
# Last updated: 2026-05-26 (notion-bridge git fix — Claude Code session)

---

## SECTION 1: FLEET HEALTH
# Format: Machine | LAN IP | Tailscale IP | Reachable | Last Verified
# Reachable = YES / NO / UNKNOWN

| Machine | LAN IP | Tailscale IP | Reachable | Last Verified |
|---|---|---|---|---|
| pve-studio (Proxmox host) | 192.168.1.4 | 100.99.40.111 (path broken) | YES (LAN only) | 2026-05-27 |
| VM101 pop-ollama | 192.168.1.136 | 100.91.173.40 | YES | 2026-05-27 |
| VM102 de-pubmachine-01 | 192.168.1.48 | [UNVERIFIED] | UNKNOWN | 2026-05-25 |
| VM103 de-edge-01 | 192.168.1.36 | [UNVERIFIED] | UNKNOWN | never |
| VM104 orchestrator | 192.168.1.19 | 100.108.23.97 | YES | 2026-05-27 |
| VM105 affiliate-engine-01 | 192.168.1.55 | [UNVERIFIED] | UNKNOWN | 2026-05-25 |
| VM106 de-truenas-01 | 192.168.1.106 | [UNVERIFIED] | UNKNOWN | 2026-05-25 |
| VM107 de-librarian-01 | 192.168.1.107 | [UNVERIFIED] | YES (LAN) | 2026-05-23 |
| VM108 de-gateway-01 | 192.168.1.108 | 100.120.42.102 | YES (Tailscale) | 2026-05-27 |
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
| Ollama (Docker, GPU) | VM101 | 11434 | HEALTHY | 2026-05-27 |
| coding-agent | VM101 | 9100 | HEALTHY | 2026-05-27 |
| claude-server | VM101 | 9099 | UP (credits_paused=true) | 2026-05-27 |
| agent-zero | VM101 | 7070 | HEALTHY | 2026-05-27 |
| n8n Sentinel | VM101 | 5678 | UP (scanner inactive by design) | 2026-05-27 |
| notion-bridge | VM104 | 9101 internal (ext 9102) | HEALTHY (git installed 2026-05-26) | 2026-05-26 |
| n8n Atlas | VM104 | 5679 | HEALTHY | 2026-05-27 |
| Atlas Task Scanner | VM104 | n8n workflow Iyts70flbCG4sKub | ACTIVE (re-enabled 2026-05-27) | 2026-05-27 |
| Atlas Dead Man Monitor | VM104 | n8n workflow | ACTIVE | 2026-05-27 |
| Atlas Completion Handler | VM104 | n8n workflow | ACTIVE | 2026-05-27 |
| agent-zero-librarian | VM107 | 7071 | UNKNOWN | 2026-05-23 |
| AnythingLLM | VM107 | 3001 | UNKNOWN | 2026-05-23 |
| Grist | VM104 | 8484 | RUNNING (undocumented) | 2026-05-20 |
| Ollama (Unraid, CPU) | Unraid | 11434 | [UNVERIFIED] | never |
| Home Assistant | VM100 | 8123 | UP (web reachable) | 2026-05-26 |

---

## SECTION 3: OPEN BLOCKERS
# Human-gated items only. Things that cannot proceed without Branden action.

1. VM102 and VM105 — SSH never confirmed. DHCP reservations fixed (2026-05-25) but services on these VMs have not been verified.
2. VM100 ha-control — pfSense reservation corrected to .100 (2026-05-25) but HA OS is not confirmed at that IP (no SSH addon installed). Verify via Proxmox console or install HA SSH addon.
3. Codex OAuth on MGMT-XPS — expired as of 2026-05-23. Needs interactive reauth in Codex before Codex can write to Notion.
4. watchdog.py on VM101 — stopped. Do not restart until inode retention guard is implemented and approved.
5. DIAMONDEYE-STATE.md Librarian automation — this document is manually seeded. Librarian scheduled sync not yet wired.
6. pve-studio Tailscale path broken — Tailscale peer exists (100.99.40.111) but path non-functional. LAN only for now.
7. VM101 QEMU guest agent — not responding. qm guest exec does not work. Use Tailscale SSH (tunedr@100.91.173.40) only.
8. Atlas Dead Man Monitor n8n expressions broken — IF node uses {{ .body || }} (should be {{ $json.body }}), Telegram chatId uses {{ .TELEGRAM_CHAT_ID }} (should be {{ $env.TELEGRAM_CHAT_ID }}). Needs 2-field fix in n8n UI at http://192.168.1.19:5679.
9. [RESOLVED 2026-05-26] notion-bridge git blocker — FIXED. git 2.47.3 installed via apt in docker-compose.yml command; container rebuilt. Atlas task dispatches should no longer fail with FileNotFoundError.
10. VM106 de-truenas-01 — IPv4 status unknown. DHCP reservation set to .106 (2026-05-25) but VM has no ARP presence. Needs console investigation.

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
