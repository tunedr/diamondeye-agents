# DiamondEye Architecture — Full VM and Machine Inventory

## Proxmox Host
- Host: pve-studio
- Local IP: 192.168.1.4
- Tailscale: 100.99.40.111
- Boot drive: Samsung 1TB SSD
- Storage VG: vmdata (sda 1.82TB + sdb 931GB + sdc 931GB = 3.51TB thin pool)
- NOTE: Both NVMes (pve-dead VG and fastvg) are thermally failing — do not use

## VM Inventory
| VM ID | Name | Role | Tailscale IP |
|-------|------|------|--------------|
| 100 | ha-control | Home Assistant | — |
| 101 | pop-ollama | GPU inference, Sentinel pipeline, Docker host | 100.91.173.40 |
| 102 | de-pubmachine-01 | Publishing machine | — |
| 103 | de-edge-01 | Edge node | — |
| 104 | orchestrator | Atlas AI orchestration, n8n port 5679 | 100.108.23.97 | LAN: 192.168.1.19 (static) |
| 105 | affiliate-engine-01 | TrendForge affiliate engine | — |

## Other Machines
| Machine | Role | Tailscale IP | Local IP |
|---------|------|--------------|----------|
| MGMT-XPS (this machine) | Interactive AI execution node, Atlas escalation target | 100.76.233.89 | — |
| Unraid (Tower) | Storage, secondary compute | 100.120.180.114 | 192.168.1.2 |
| TrueNAS | Primary storage backbone (Phase 2b pending) | 100.76.34.69 | — |
| pfSense | Network firewall | 100.102.75.124 | DO NOT TOUCH |

## SSH Access
- pop-ollama: tunedr@100.91.173.40
- pve-studio: root@100.99.40.111
- orchestrator: root@100.108.23.97
- Unraid: root@100.120.180.114
- TrueNAS: admin@100.76.34.69
- SSH host map: LOCAL/ssh/hosts.md
- SSH key location: /home/tunedr/.ssh/

## Pipeline Architecture
- Sentinel = Sentinel pipeline on pop-ollama, n8n port 5678 (generation 1, still active)
- Atlas = Orchestration pipeline on VM 104, n8n port 5679 (generation 2)
- Notion = Single source of truth for all task state
