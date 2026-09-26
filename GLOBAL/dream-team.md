# DiamondEye Dream Team Architecture
# Last verified: 2026-06-20
# Authority: Branden Womack. All three agents read this file for cross-boundary routing decisions.

## The Three Agents

| Agent | Role | Machine | Primary Model | Contact |
|-------|------|---------|---------------|---------|
| XPs_pa | Executive conduit / chief of staff | MGMT-XPS (native) | gpt-5.4 (Codex OAuth) | Telegram @Xps_pa_diamondeye_bot |
| Desk | Builder VP / operations orchestrator | MGMT-XPS (Docker) | llama3.2 → routes Cline | http://localhost:8642/v1/chat/completions |
| Librarian | Truth VP / evidence librarian | VM107 de-librarian-01 | llama3.2 (standard) / gpt-5.4 (Guru) | http://127.0.0.1:8647 (standard) / http://127.0.0.1:8648 (Guru) |

---

## Ownership Zones

### XPs_pa owns
- Branden's daily priorities and what to tackle first
- Task triage and executive judgment calls
- Revenue-first alignment and decision authority
- Routing work to Desk or Librarian — it sends tasks, it does not execute them
- Guru escalation when it needs gpt-5.5 reasoning (financial decisions, irreversible actions, low confidence)

XPs_pa does NOT execute infra changes, write to fleet configs, or self-verify facts.

### Desk owns
- Execution routing for all builder tasks
- Cline task dispatch (direct path: Desk → cline-api.py on pop-ollama:8766 → cline-executor-desk.py → Cline binary using qwen2.5-coder:7b)
- Fleet build, config repair, multi-file edits via Cline
- Notion writebacks for every Cline run (forensic page under Master Hub)
- [SUPERSEDED 2026-06-22] Agent Zero dispatch for AXIOM, publishing, and affiliate tasks (agent-zero-desk port 50080) — Agent Zero is abandoned for ALL active workflows per architecture.md. No new workflow should route through A0.
- Notion MCP tools (22 tools active as of 2026-06-13)

Desk does NOT make priority decisions, self-authorize high-risk changes, or self-certify disputed facts.

### Librarian owns
- Evidence management, confidence labeling, source trails
- ICM fleet health (GLOBAL/ file propagation and drift detection — target: 6-hour sweep)
- Doctrine truth — answering "what does X say" from SOUL.md and ICM sources
- Audit queues and stale/disputed fact flags
- Guru escalation for the four judgment-call trigger types (see below)

Librarian does NOT approve actions, execute fleet changes, or remediate problems it finds.

---

## The Trust Boundary

```
XPs_pa decides  →  Desk executes  →  Librarian verifies
```

None of the three closes the loop alone:
- XPs_pa alone can choose, but must not be the sole verifier of whether a decision is factually sound.
- Desk alone can act, but must not self-authorize disputed facts or override priority calls.
- Librarian alone can judge evidence, but cannot approve, execute, or remediate.

Claude Code is the out-of-band escalation executor — invoked only when Desk's Cline path returns `explicit_failure=true` and the desk-escalation-watcher.service triggers a tmux session. Claude Code is never in the normal operation loop.

---

## Routing Rules

### XPs_pa → Desk
Send when: Branden has approved a builder task (infra, code, config, fleet change).
How: HTTP POST to `http://localhost:8642/v1/chat/completions` with Desk API key, or via hermes-desk Telegram.

### XPs_pa → Librarian (standard tier — llama3.2)
Send when: simple classification, ICM lookup, known-answer question, routing triage.
How: HTTP POST to `http://127.0.0.1:8647/v1/chat/completions` + `Authorization: Bearer <HERMES_LIBRARIAN_API_KEY>`.
Always inject a system context message — stateless API does not auto-load SOUL.md.

### XPs_pa → Librarian-Guru (gpt-5.4 — use for real truth questions)
Send when: fact-checking, doctrine questions, contradicting docs, ambiguous evidence, any of the four escalation triggers.
How: HTTP POST to `http://127.0.0.1:8648/v1/chat/completions` + `Authorization: Bearer <HERMES_LIBRARIAN_GURU_API_KEY>`.
Both keys are in `/home/tunedr/CREDENTIALS.env` on MGMT-XPS.

### Desk → Cline (execution)
Normal execution path: Desk routes to `cline-api.py` on pop-ollama (100.91.173.40:8766, X-API-KEY: desk-cline-2026).
Cline uses qwen2.5-coder:7b via cline-ollama-proxy on pop-ollama:11435.
Every Cline run writes a forensic Notion page under Master Hub (30e6d271-f21c-8141-b74d-f62f14ad1e6a).

### Desk → Claude Code (escalation only)
Triggers when: Cline returns `explicit_failure=true`.
Mechanism: Desk writes `escalate_XXXX.sh` to `/opt/data/escalations/` → desk-escalation-watcher.service (MGMT-XPS systemd) picks it up in <5s → Claude Code tmux session created.
Claude Code operates from runbook URL sent in the third message of the /goal invocation standard.

---

## Librarian-Guru Escalation Triggers (SOUL.md v1.1.0)

Escalate from standard Librarian (llama3.2) to Guru (gpt-5.4) only when one of these four is true:

1. **Unverifiable claim blocking a decision**: A claim has no corroborating evidence and a downstream decision depends on which confidence label is correct.
2. **Contradicting documents**: Two sources directly contradict each other with no clear supersession path that Librarian can determine from timestamps or source type.
3. **Archived item with uncertain relevance**: An archived/dropped item might be relevant to an active blocking problem but whether the connection is real cannot be determined by pattern-matching.
4. **Ambiguous scan result**: A scheduled scan returns neither a clean pass nor a clean fail and pattern-matching cannot categorize it.

Routine work that NEVER escalates: inventory scans, propagation, templated writebacks, known-answer lookups, clean pass/fail results.

---

## Live Endpoints (verified 2026-06-20)

| Service | Endpoint | Auth | Notes |
|---------|----------|------|-------|
| XPs_pa | HERMES_HOME=/home/tunedr/xps-pa-data hermes | Telegram bot | Systemd hermes-gateway.service (user, linger) |
| Desk API | http://localhost:8642/v1/chat/completions | API_SERVER_KEY in hermes-desk-data/.env | Also port 9124 web dashboard |
| Librarian standard | http://127.0.0.1:8647/v1/chat/completions | HERMES_LIBRARIAN_API_KEY | librarian-tunnel.service on MGMT-XPS |
| Librarian Guru | http://127.0.0.1:8648/v1/chat/completions | HERMES_LIBRARIAN_GURU_API_KEY | librarian-guru-tunnel.service on MGMT-XPS |
| Cline API | http://100.91.173.40:8766/run | X-API-KEY: desk-cline-2026 | pop-ollama, cline-api.service (user systemd) |
| [SUPERSEDED 2026-06-22] Agent Zero Desk | http://localhost:50080 | AGENT_ZERO_DESK_API_KEY | Abandoned for all active workflows — legacy container only, see architecture.md |

SSH alias for VM107: `ssh librarian` (resolves to tunedr@192.168.1.107, ~/.ssh/id_ed25519).

---

## What Remains Unbuilt (as of 2026-06-20)

- [DONE 2026-06-20] Librarian Notion MCP: @notionhq/notion-mcp-server@2.2.1 installed, mcp_servers.notion block in config.yaml, process confirmed running (PID 156 at restart), Notion API read/write verified. Caveat: llama3.2 (standard tier) does not reliably invoke MCP tools autonomously — direct API calls or Guru-tier MCP are more reliable paths.
- Cron sweep: n8n-librarian (VM107:5680) is running but no workflows exist for the 6-hour ICM sweep. BLOCKED — n8n changes require separate authorization.
- Librarian Tailscale: interface present on VM107 but unauthenticated — LAN-only access. Requires interactive `sudo tailscale up` by Branden.
- Dream Team cross-agent session handoff protocol: not formalized — agents currently communicate only via HTTP or Telegram, not a shared session state.
- Guru-tier Notion MCP (hermes-librarian-guru): not configured — gpt-5.4 would invoke tools reliably but hermes-librarian-guru has no mcp_servers block yet.
