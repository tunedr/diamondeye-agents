---
name: check-status
description: Check the status of all DiamondEye machines and services. Use when asked for a system health check or status report.
---
## Goal
SSH into each machine and report: uptime, disk usage, Docker container status, and any obvious errors.

## Steps
1. SSH to pop-ollama (100.91.173.40) — run: uptime && df -h && docker ps
2. SSH to pve-studio (100.99.40.111) — run: uptime && df -h && pvesm status
3. SSH to orchestrator (100.108.23.97) — run: uptime && df -h && docker ps
4. Compile results into a status table
5. Write summary to Notion Active Session State page
