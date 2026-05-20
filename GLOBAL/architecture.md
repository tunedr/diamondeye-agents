# DiamondEye Architecture — Ground Truth
# Last verified: 2026-05-20

## Proxmox Host
- pve-studio: 192.168.1.4 (LAN only — no Tailscale installed)

## Virtual Machines
| VM  | Hostname            | LAN IP        | Tailscale       | Key Services |
|-----|---------------------|---------------|-----------------|--------------|
| 100 | ha-control          | DHCP          | —               | Home Assistant OS |
| 101 | pop-ollama          | 192.168.1.136 | 100.91.173.40   | Ollama :11434, Postiz :4007, A0 :7070 |
| 102 | de-pubmachine-01    | 192.168.1.48  | —               | A0 Publishing :7071 |
| 103 | de-edge-01          | 192.168.1.36  | turtle-sunfish  | Dashboard :8888 |
| 104 | orchestrator        | 192.168.1.19  | 100.108.23.97   | Atlas n8n :5679 |
| 105 | affiliate-engine-01 | 192.168.1.55  | —               | A0 Affiliate :7072, n8n :5679 |
| 106 | de-truenas-01       | 192.168.1.106 | —               | TrueNAS SCALE, 12TB |
| 107 | de-librarian-01     | 192.168.1.107 | pending         | A0 Librarian :7071, AnythingLLM :3001, n8n :5680 |
| 108 | de-gateway-01       | 192.168.1.108 | pending         | A0 Gateway :7072, OpenWebUI :3000, Uptime Kuma :3002, n8n :5680 |

## Physical Machines
| Host      | LAN IP        | Tailscale       | Role |
|-----------|---------------|-----------------|------|
| Unraid    | 192.168.1.2   | 100.120.180.114 | A0 MediaMind :50080, Ollama :11434, Plex, ARR |
| MGMT-XPS  | 192.168.1.221 | 100.76.233.89   | Desk — Claude Code, Codex, A0 :50080, OpenClaw :3000 |
| Laptop    | Tailscale TBD | TBD             | WSL — Claude Code, Codex, A0 :50080, OpenClaw :3000 |

## Ollama Instances
| Host       | IP                  | Purpose |
|------------|---------------------|---------|
| pop-ollama | 192.168.1.136:11434 | CHAT model (deepseek-r1) for all fleet agents |
| Unraid     | 192.168.1.2:11434   | UTILITY (qwen2.5) + EMBED (nomic-embed) for all fleet agents; ALL tiers for MediaMind |

## Fleet Model Routing — ALL Agent Zero instances except MediaMind
  CHAT:    deepseek-r1:latest      @ http://192.168.1.136:11434
  UTILITY: qwen2.5:7b              @ http://192.168.1.2:11434
  EMBED:   nomic-embed-text:latest @ http://192.168.1.2:11434

## OpenClaw Model Routing — ALL OpenClaw instances
  Chat:     Codex OAuth (ChatGPT Plus, gpt-4o)
  Executor: Codex CLI
  Embed:    nomic-embed-text @ http://192.168.1.2:11434

## Agent Zero A2A Fleet
| Instance             | IP            | Port  | Role |
|----------------------|---------------|-------|------|
| agent-zero-gateway   | 192.168.1.108 | 7072  | A2A Controller |
| agent-zero (general) | 192.168.1.136 | 7070  | General executor |
| agent-zero-librarian | 192.168.1.107 | 7071  | ICM, Notion, research |
| agent-zero-publishing| 192.168.1.48  | 7071  | Books, Postiz, social |
| agent-zero-affiliate | 192.168.1.55  | 7072  | Campaigns, affiliate |
| agent-zero-desk      | 192.168.1.221 | 50080 | Interactive — MGMT-XPS |
| agent-zero-laptop    | Tailscale TBD | 50080 | Portable — update after laptop runbook |
| agent-zero (MM)      | 192.168.1.2   | 50080 | MediaMind — DO NOT MODIFY |

## Credentials
  Location: /home/tunedr/CREDENTIALS.env on pop-ollama (192.168.1.136)
  Read: ssh tunedr@192.168.1.136 cat /home/tunedr/CREDENTIALS.env

## Hard Rules
  - Never touch pfSense: 100.102.75.124
  - Never run docker system prune autonomously
  - Never delete data on any machine
  - Never modify Atlas n8n without pausing pipeline first
  - Always write task results to Notion before session ends
