# ICM Inventory Management Specification

## Purpose
The Librarian (de-librarian-01) maintains a live inventory of all ICM markdown files across every DiamondEye machine. This is how the system knows what documentation exists, where it lives, and whether it is current.

## Inventory File
- Location on TrueNAS: /mnt/truenas-canonical/infrastructure/icm-inventory.md
- Updated by: Librarian on a schedule (every 6 hours via n8n-librarian)
- Format: machine name, file path, last modified date, sha256 hash

## Machines to Inventory
| Machine | Path(s) |
|---------|---------|
| MGMT-XPS (192.168.1.221) | ~/AGENTS/ |
| pop-ollama (192.168.1.136) | ~/AGENTS/ and /mnt/user/appdata/agent-zero/ |
| orchestrator VM 104 (192.168.1.19) | ~/coding-agent/ and ~/AGENTS/ |
| de-librarian-01 (192.168.1.107) | ~/AGENTS/ and ~/de-knowledge/ |
| de-gateway-01 (192.168.1.108) | ~/AGENTS/ |
| Unraid (192.168.1.2) | /mnt/user/appdata/agent-zero/ |

## Inventory Workflow (n8n-librarian, every 6 hours)
1. SSH into each machine
2. Run: find ~/AGENTS -name "*.md" -exec sha256sum {} \;
3. Compare hashes to previous inventory
4. If new file: ingest into Infrastructure workspace in AnythingLLM
5. If changed file: update AnythingLLM, flag change in Telegram
6. If file missing that was previously present: Telegram alert immediately
7. Write updated inventory to TrueNAS canonical path

## Required Steps on Every New VM Deployment
Before closing any build session, Claude Code must complete ALL of the following:

1. Create ~/AGENTS/ on the new VM
2. Copy the full GLOBAL/ ICM structure from MGMT-XPS:
   scp -r /home/tunedr/AGENTS/GLOBAL/ tunedr@<vm-ip>:~/AGENTS/GLOBAL/
3. Write LOCAL/machine-config.md with machine-specific details (see template below)
4. Confirm the Librarian's next inventory run will pick it up (check n8n-librarian schedule, or note as pending if Librarian not yet operational)

## LOCAL/machine-config.md Template
```
# Machine Config — <hostname>
- Hostname: <hostname>
- Role: <role>
- Local IP: <ip>
- Tailscale IP: <ip or pending>
- Primary user: <user>
- Home directory: /home/<user>
- VM ID: <id if Proxmox VM>
- Key services: <list>
- ICM paths inventoried: ~/AGENTS/
- Last ICM sync: <date or pending>
```

## Notes
- TrueNAS NFS must be mounted on de-librarian-01 at /mnt/truenas-canonical before inventory writes can land
- TrueNAS silvering may delay this — document as pending if NFS not yet available
- Librarian workflow is blocked until AnythingLLM is deployed and n8n-librarian is configured
