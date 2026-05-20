---
name: notion-write
description: Write structured output to a Notion page. Use when a task result needs to be logged to Notion.
---
## Goal
Write task results to the correct Notion page with proper formatting.

## Rules
- Always include: Current Status, Next Action, Blocked/Decision Needed at top
- Wait 400ms between consecutive API calls
- On HTTP 429: wait 10 seconds before retry
- Use hyphenated UUID format for all page IDs
- Never overwrite existing content — append to it
