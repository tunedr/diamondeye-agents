# Machine Identity — de-librarian-01

- Hostname: de-librarian-01
- Role: Knowledge Layer — RAG backend, document management, OSINT execution, knowledge hygiene
- Local IP: 192.168.1.107
- Tailscale IP: pending
- Primary user: tunedr
- Home directory: /home/tunedr
- VM ID: 107 (Proxmox pve-studio)
- OS: Ubuntu Server 24.04 LTS
- Disk: 164G LVM (resized 2026-06-05 from 101G — scsi0 on local-lvm)
- RAM: 14GB allocated
- CPU: 4 cores (2 sockets x 2 cores)

## Role in DiamondEye Stack
This machine is the knowledge execution layer. It runs:
- Hermes Agent (librarian, apollo, truth-lens, coder profiles)
- AXIOM investigator (agent-zero-axiom — DO NOT TOUCH)
- Supporting services: Paperless-ngx, AnythingLLM, Nextcloud, Gotenberg, Stirling-PDF

## TrueNAS NFS Mount
- Mount point: /mnt/truenas-canonical
- NFS export: 192.168.1.106:/mnt/twelvet/canonical
- Hermes data: /mnt/truenas-canonical/hermes-data
- fstab entry: 192.168.1.106:/mnt/twelvet/canonical /mnt/truenas-canonical nfs defaults,_netdev,noatime 0 0

## Docker Compose Locations
- Knowledge stack: /home/tunedr/de-knowledge/docker-compose.yml
- Hermes: /opt/hermes/docker-compose.yml
- Managed via: cd /home/tunedr/de-knowledge && docker compose [cmd]
