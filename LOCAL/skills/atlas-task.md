---
name: atlas-task
description: Parse and execute a task card received from Atlas. Use when Atlas sends a task payload to this machine.
---
## Goal
Read an Atlas task payload, execute the task with full context already loaded, and return the result.

## Steps
1. Read the task card: extract Action, Target Machine, Success Criteria
2. Confirm target machine is reachable via Tailscale
3. Execute the task using appropriate tool (Claude Code or Codex CLI)
4. Verify success against the stated criteria
5. Write result to Notion task card and update status to Done or Blocked
6. Notify via Telegram if configured
