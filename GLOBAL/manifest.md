# DiamondEye GLOBAL Local Manifest
# Last updated: 2026-05-25

This manifest records the local GLOBAL/ documentation files present after the 2026-05-25 rules rewrite. No existing manifest was found under `/mnt/c/Users/brand/AGENTS` before this file was created.

| Path | Last Updated | SHA-256 |
|---|---|---|
| `rules.md` | 2026-09-19 reconcile | `63a80867980412d0710e2c0a60ce41b2ef696682f91e046b56d2c9ada12d0fa3` |
| `architecture.md` | 2026-09-19 reconcile | `81eacb06bb4ddddb0910aaab5049c8bdf6e4aaeb1c26742c6c4fc604011c6f5f` |
| `services.md` | 2026-09-19 reconcile | `54ca464f7c9b071b9a600b3d8b497cc1479e3f48f4b8db741d5578b45fac94fc` |
| `notion-schema.md` | unchanged | `6e0ffc6381e9d337929a8766a8de7db75f32bb1ee5dc7af098cae6b7ac333eb9` |
| `LOCAL/identity.md` | 2026-09-19 reconcile | `c5bd7233400679994a6229e39fe305619c4fd5da01b2856c7cf5d8522da0d09d` |

## Change Notes

### 2026-09-19 — Context reconcile (Claude Code session, goal: eliminate stale operating context)
- architecture.md: hermes-desk model corrected gpt-5.4 → gpt-5.5; Odin section added (anthropic/claude-sonnet-4-6, Level 2 commissioned); Model Change Log entries added for 2026-09-11 power outage recovery.
- services.md: hermes-desk model corrected; hermes-gateway-pilot renamed to Odin with current state (claude-sonnet-4-6, proven Notion MCP, Level 2).
- LOCAL/identity.md: Odin added to agent inventory; Codex CLI status note added (Plus lapsed 2026-09-05).
- Backups at: /home/tunedr/AGENTS/backups/context-reconcile-20260919/

### 2026-05-25 — Initial rules rewrite
- Rewrote `rules.md` into separated active, revised, pending review, and deprecated/stale sections.
- Added active VM/project isolation boundary rules from the DiamondEye VM Isolation Contract.
- Preserved all prior standing rules by status and reason.
- Marked Tailscale-only configs, Librarian live inventory, Agent Zero dual-model assumptions, TrueNAS Phase 2b gate, and localhost/Ollama endpoint wording as pending review instead of standing law.
