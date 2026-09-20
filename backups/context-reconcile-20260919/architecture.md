# DiamondEye Architecture — Ground Truth
# Last verified: 2026-08-10 (IP conflict resolution session 3b86d271-f21c-8127-b4f9-fb0ce4cde1ac)
# Fleet Reference DB (live-verified 2026-07-25): f80b61810eca46a08466bf3174926d99
# Active workflow doctrine update: 2026-07-20
# Agent Zero is abandoned for active workflows. Legacy Agent Zero containers/ports may still
# exist in inventory, but no new workflow should depend on them.
# Cline CLI is EXCLUDED from Hermes Desk as of 2026-07-20 (Branden's explicit decision).
# Active authority chain: Hermes Desk decomposes work → writes finished plans to Notion task DB
# → Atlas v2 executes independently → Claude Code escalation only.

## Proxmox Host
- pve-studio: 192.168.1.4 — Tailscale 100.99.40.111 (enrolled but OFFLINE 83+ days as of 2026-07-25; LAN only in practice)

## Virtual Machines
| VM  | Hostname            | LAN IP          | Tailscale       | Key Services |
|-----|---------------------|-----------------|-----------------|--------------|
| 100 | ha-control          | 192.168.1.100 (static via ha network update 2026-08-10; pfSense DHCP reservation PENDING — Branden) | — | Home Assistant OS :8123 |
| 101 | pop-ollama          | 192.168.1.136   | 100.91.173.40   | Ollama :11434, Postiz :4007, A0 :7070, Cline API :8766 |
| 102 | de-pubmachine-01    | 192.168.1.48    | —               | A0 Publishing :7071, inspections-web :8081, shlink :8080 |
| 103 | de-edge-01          | 192.168.1.36    | 100.99.172.65   | Dashboard :8888/:8889, NPM :80/:81/:443 |
| 104 | orchestrator        | 192.168.1.19    | 100.108.23.97   | Atlas n8n :5679, atlas-v2 :8080, Grist :8484 |
| 105 | affiliate-engine-01 | 192.168.1.55    | —               | A0 Affiliate :7072, n8n :5679, resume-tool :3000 |
| 106 | de-truenas-01       | 192.168.1.106   | —               | TrueNAS SCALE, 12TB (SSH key missing — web UI only) |
| 107 | de-librarian-01     | 192.168.1.107   | 100.74.175.56   | AnythingLLM :3001, paperless-ngx :8010, n8n :5680, AXIOM :7073, nextcloud :8080, stirling-pdf :8020, excalidraw :8030 — NOTE: all 5 Hermes containers EXITED (confirmed 2026-08-06) |
| 108 | serberus-hermes     | 192.168.1.108 (guest-level static Netplan — CONFIRMED; IP conflict with VM100 RESOLVED 2026-08-10; pfSense reservation PENDING — Branden) | 100.67.35.31 | Hermes v0.19.0 bare-metal :9124, domain: serberus.diamondeye.net — ADDED 2026-08-01 |

## Physical Machines
| Host      | LAN IP        | Tailscale       | Role |
|-----------|---------------|-----------------|------|
| Unraid    | 192.168.1.2   | 100.120.180.114 | Ollama :11434, openwebui :3010, gateway stack (openclaw-gateway :7075, uptime-kuma :3002, n8n-gateway :5680), ARR suite, Plex, HELFINANCE :3210 |
| MGMT-XPS  | 192.168.1.221 | 100.76.233.89   | hermes-desk :8642 (Docker, gpt-5.4), anythingllm-desk :3002, honcho :8000, Claude Code, Codex, legacy agent-zero-desk :50080 |
| Laptop    | Tailscale TBD | TBD             | WSL — Claude Code, Codex (inactive/unverified) |

## Fleet Inventory
| Stack | Host | Location | Services |
|-------|------|----------|----------|
| de-gateway | Unraid | `/mnt/user/appdata/de-gateway/` | openclaw-gateway :7075, agent-zero-master-router :7072, uptime-kuma :3002, openwebui :3010, n8n-gateway :5680, SearXNG :8081 |
| serberus-hermes | VM108 | bare-metal /home/tunedr/ | Hermes v0.19.0 dashboard :9124 (systemd user service), domain serberus.diamondeye.net, NPM proxy host 16 on de-edge-01 |

## Ollama Instances
| Host       | IP                  | Purpose |
|------------|---------------------|---------|
| pop-ollama | 192.168.1.136:11434 | CODING model (qwen2.5-coder:7b) for fleet agents |
| Unraid     | 192.168.1.2:11434   | CHAT (llama3.2) + EMBED (nomic-embed) for fleet agents; ALL tiers for MediaMind |

## Fleet Model Routing — Hermes baseline (historical Agent Zero artifacts may still match these models)
  CHAT:    llama3.2:latest         @ http://192.168.1.2:11434
  UTILITY: qwen2.5-coder:7b       @ http://192.168.1.136:11434
  EMBED:   nomic-embed-text:latest @ http://192.168.1.2:11434

## Hermes Profile Routing — VM 107
  ⚠️ ALL 5 HERMES CONTAINERS EXITED — confirmed 2026-07-25 and 2026-08-06 (Agent Registry session).
  hermes-librarian, hermes-librarian-guru, hermes-apollo, hermes-coder, hermes-truthlens: NOT RUNNING.
  Tunnel services librarian-tunnel.service and librarian-guru-tunnel.service on MGMT-XPS: DISABLED.
  Branden needs to confirm: intentionally removed or need rebuild? (flagged in Agent Registry session 3b46d271)

  Historical (pre-EXITED) profile config — preserved for rebuild reference:
  librarian:       llama3.2:latest   @ http://192.168.1.2:11434/v1    (port 8642)
  librarian-guru:  gpt-5.4           @ openai-codex OAuth              (port 8646) — escalation tier only; compose: /home/tunedr/hermes-guru/docker-compose.yml
  apollo:          llama3.2:latest   @ http://192.168.1.2:11434/v1    (port 8643)
  truth-lens:      llama3.2:latest   @ http://192.168.1.2:11434/v1    (port 8644)
  coder:           qwen2.5-coder:7b  @ http://192.168.1.136:11434/v1  (port 8645, context_length: 65536, ollama_num_ctx: 65536)

## Model Change Log
  2026-09-08: MGMT-XPS Hermes pilot model updated from llama3.2:latest (custom/Ollama) to openrouter/google/gemini-2.5-flash.
  Primary: google/gemini-2.5-flash via OpenRouter (OPENROUTER_API_KEY from hermes-desk, reuse noted).
  Fallback: gemini-2.5-flash via direct Gemini API (GEMINI_API_KEY from hermes-desk, free-tier, 5 req/min limit).
  All 3 acceptance tests (chat, tool-use, reasoning) PASS for both primary and fallback.
  config.yaml backup: ~/.hermes/config.yaml.pre-phase3-20260907T202225Z.
  Telegram gateway live (tmux hermes-pilot, @diamondeye_gateway_bot, polling mode, HERMES_HOME=~/.hermes/).
  python-telegram-bot 22.8 installed. Desktop (Electron) killed; headless gateway running.
  Step 6 (roundtrip proof) PARTIAL — awaiting Branden's Telegram reply.
  Forensic: 3d56d271-f21c-81c1-8a6a-ec90adc86ab7.

  2026-09-07: MGMT-XPS OpenClaw gateway RETIRED. Replaced by Hermes Agent v0.21.0 pilot.
  Model: llama3.2:latest @ pop-ollama (192.168.1.136:11434/v1). Provider type: custom (Ollama-compatible).
  OpenClaw rollback archive: /home/tunedr/archives/openclaw-retired-20260907-032255/.
  Forensic: 3d46d271-f21c-81ad-b2ff-c93473a7959b.

  2026-09-04: Gateway primary + compaction model migrated from Kimi/gpt-oss → Claude Sonnet 4.6 via claude-cli OAuth.
  Root cause fixed: gpt-oss:20b (65K window) compacting Kimi (131K) sessions at ~111K tokens → truncated artifacts
  (Class K compaction mismatch). Fix: anthropic/claude-sonnet-4-6 (200K) for both primary and compaction.
  Auth: claude-cli backend uses Claude Code OAuth session (claude auth status --json → loggedIn=true,
  authMethod=claude.ai, subscriptionType=pro). CLAUDE_CLI_CLEAR_ENV strips all Anthropic API key env vars.
  No API key. No metered fallback. Proven: openclaw agent exec returned provider=claude-cli, model=claude-sonnet-4-6
  in 12.3s. Telegram round-trip pending Branden physical action.
  Config: ~/.openclaw/openclaw.json | Backup: .../openclaw.json.pre-claude-migration-20260904T063802Z
  Forensic: 3d16d271-f21c-8137-b26b-dc3e1dbcccc9.

  2026-09-03: OpenClaw gateway upgraded 2026.7.2-beta.7 → 2026.8.2 (0965053) on MGMT-XPS.
  Root cause: memory leak (1.7GB peak) → SQLite contention → event loop blocking (32–39s) → frozen
  Telegram offset (90586475). 2026.8.2 includes durable spool-based Telegram ingress + SQLite safety.
  Migrations applied: retired 6 shared-state tables, removed gateway.tailscale.resetOnExit config.
  Repairs: Tailscale route ownership conflict (stale 443 route cleared), skill YAML frontmatter added
  (name/description now required in 2026.8.2). Queue watcher idempotency fix deployed.
  Post-upgrade: Telegram routing restored, Kimi routing confirmed, browser relay confirmed, VM101
  artifact access confirmed. Forensic: 3d06d271-f21c-81fb-8dc4-e846a12b2f61.

  2026-08-15: OpenClaw gateway upgraded 2026.7.1-2 → 2026.7.2-beta.7 (dabe191) on MGMT-XPS.
  Locking race (EmbeddedAttemptSessionTakeoverError) fixed upstream — createEmbeddedAttemptSessionLockController
  rewritten with noOpLock + serializeLifecycle; file fingerprint check removed. Prior A1 workaround
  (tools.experimental.planTool: false) corrected and removed. update_plan enabled by default.
  Publisher schema expanded from 4 to 17 required fields. LC-01–LC-04 commissioning PASS.
  Correction runbook: 3bd6d271-f21c-8192-af9a-d10bc36a6b57.

  2026-08-01: VM108 serberus-hermes stood up (new Hermes instance, bare-metal, Hermes v0.19.0,
  port 9124 dashboard, domain serberus.diamondeye.net, Tailscale 100.67.35.31).
  openai-codex OAuth not yet configured on this host (open item per standup record 3af6d271).

  2026-07-20: Cline CLI EXCLUDED from Hermes Desk path (Branden's explicit decision).
  Desk no longer routes execution to cline-api.py. Desk writes finished plans to Notion task DB;
  Atlas v2 executes independently. Prior SOUL.md Cline Direct Invocation Protocol superseded.

  2026-07-17: xps_pa ABANDONED for active PA/orchestration work. hermes-desk (Docker) is now
  Branden's primary PA. xps_pa crash-looping (exit-code=1) as of 2026-07-16 — data preserved at
  /home/tunedr/hermes/profiles/xps_pa/, no active service running it. Deliberately not decommissioned.

  2026-06-18: Added hermes-librarian-guru profile on VM107 port 8646 (gpt-5.4 via Codex OAuth).
  Reason: Librarian mandate includes claim auditing and judgment calls that llama3.2 cannot reliably resolve. Guru is escalation-only; routine scanning stays on llama3.2.
  Escalation triggers documented in /mnt/truenas-canonical/hermes-librarian/SOUL.md v1.1.0.
  Authorized by Branden via runbook 3836d271-f21c-81ff-aeb1-e48880d3049f.

  2026-06-05: Changed from deepseek-r1/qwen2.5 to llama3.2/qwen2.5-coder.
  Reason: deepseek-r1 does not support tools API (required by Hermes Agent).
  qwen2.5:7b context window (32K) below Hermes minimum (64K).
  llama3.2:latest (131K ctx, tools supported) and qwen2.5-coder:7b (32K ctx, tools supported)
  are the new fleet standard. Authorized by Branden on 2026-06-05.

## OpenClaw Model Routing — HISTORICAL (MGMT-XPS instance RETIRED 2026-09-07)
  MGMT-XPS openclaw-gateway.service retired. Replaced by Hermes Agent v0.21.0 pilot.
  de-gateway (Unraid :7075) still active — this section applies to that instance only.
  Chat:     Codex OAuth (ChatGPT Plus, gpt-4o)
  Executor: Codex CLI
  Embed:    nomic-embed-text @ http://192.168.1.2:11434

## MGMT-XPS Hermes Gateway/PA Pilot — LIVE 2026-09-07
  Hermes Agent v0.21.0 (2026.8.31, 693641aa). HERMES_HOME=~/.hermes/ (stock default).
  Model: llama3.2:latest @ pop-ollama (192.168.1.136:11434/v1, provider=custom).
  Desktop: Electron 40.10.2, DISPLAY=:1, COSMIC/Wayland+X11. cua-driver 0.23.2.
  Notion skill (ntn v0.18.1) + Notion MCP (OAuth pending). 60 bundled skills.
  Forensic: 3d46d271-f21c-81ad-b2ff-c93473a7959b.

## Historical Agent Zero Inventory — Abandoned for Active Workflows
| Instance             | IP            | Port  | Role |
|----------------------|---------------|-------|------|
| agent-zero-gateway   | 192.168.1.2 | 7072  | Historical A2A controller |
| agent-zero (general) | 192.168.1.136 | 7070  | Historical executor |
| agent-zero-librarian | 192.168.1.107 | 7071  | Historical Librarian lane |
| agent-zero-publishing| 192.168.1.48  | 7071  | Historical publishing lane |
| agent-zero-affiliate | 192.168.1.55  | 7072  | Historical affiliate lane |
| agent-zero-desk      | 192.168.1.221 | 50080 | Legacy Desk container — not active authority |
| agent-zero-laptop    | Tailscale TBD | 50080 | Historical laptop lane |
| agent-zero (MM)      | 192.168.1.2   | 50080 | Historical MediaMind lane |

## Autonomous Pipeline Flow Map
- Intake: Notion tasks, projects, and session records enter the queue through scanner-visible databases and manual intake pages.
- Scanner: n8n pollers and trigger workflows pull ready work from Notion and adjacent sources.
- Router: Atlas v2 (orchestrator VM104 :8080) / Notion Bridge / classification logic assigns work to the correct executor path.
- Executor: Hermes Desk decomposes bounded work and writes finished plans to Notion task DB. Atlas v2 executes tasks independently. Claude Code is escalation-only. Cline CLI is NOT in Desk's execution path (excluded 2026-07-20).
- Validator: a separate worker confirms outcomes when the task touches pipeline state or infra state.
- Reporter: results are written back to Notion, the worklog, and any configured Telegram reporting path.
- Escalation: desk-escalation-watcher.service on MGMT-XPS picks up escalate_*.sh files written by Desk → opens tmux session with claude CLI. Agent Zero NOT in escalation path.
- Guardrail: any task that diagnoses, modifies, or validates the pipeline itself must be routed out of band from the affected path.

## Credentials
  Location: /home/tunedr/CREDENTIALS.env on pop-ollama (192.168.1.136)
  Read: ssh tunedr@192.168.1.136 cat /home/tunedr/CREDENTIALS.env

## Hard Rules
  - Never touch pfSense: 100.102.75.124
  - Never run docker system prune autonomously
  - Never delete data on any machine
  - Never modify Atlas n8n without pausing pipeline first
  - Always write task results to Notion before session ends
