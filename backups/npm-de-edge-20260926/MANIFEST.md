# NPM/de-edge-01 Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source host: de-edge-01 (VM103) — 192.168.1.36

## What Was Exported (Safe)
- `proxy_hosts/*.conf` — All 16 nginx proxy host config files
  These contain: domain names, backend LAN IPs/ports, SSL cert paths, and nginx directives.
  They do NOT contain private keys or passwords.

## What Was Excluded (Secrets)
- `/srv/npm/data/keys.json` — EXCLUDED: Contains RSA private key (NPM signing key). Store in Bitwarden/vault.
- `/srv/npm/data/custom_ssl/npm-1/privkey.pem` — EXCLUDED: Cloudflare Origin Certificate private key. Regenerate from Cloudflare dashboard if needed (free, 15-year certs).
- `/srv/npm/data/custom_ssl/npm-1/fullchain.pem` — EXCLUDED: Certificate chain (can regenerate alongside privkey).
- `/srv/npm/data/database.sqlite` — EXCLUDED: NPM state DB; may contain hashed access-list credentials.
- `/srv/npm/letsencrypt/` — EXCLUDED: Let's Encrypt private keys (not used — all hosts use custom SSL).

## Proxy Host Inventory (16 hosts, all using Cloudflare Origin Cert npm-1)
| Host # | Domain(s) | Backend | Notes |
|--------|-----------|---------|-------|
| 1 | n8n.diamondeye.net | 192.168.1.136:5678 | Sentinel n8n (pop-ollama) |
| 2 | go.diamondeye.net | 192.168.1.35:8080 | Shlink (note: shlink container is on VM102 :8080, LAN IP may be old) |
| 3 | ombi.diamondeye.net | 192.168.1.2:5000 | Ombi (Unraid) |
| 4 | arr.diamondeye.net | 192.168.1.2:3000 | arr-dashboard (Unraid) |
| 5 | audiobookshelf.diamondeye.net | 192.168.1.2:13378 | Audiobookshelf (Unraid) |
| 6 | book1.diamondeye.net | 192.168.1.136:8090 | Book site 1 (pop-ollama) |
| 7 | book2.diamondeye.net | 192.168.1.136:8091 | Book site 2 (pop-ollama) |
| 8 | youtube.diamondeye.net | 192.168.1.136:4007 | Postiz (pop-ollama) |
| 9 | diamondeye.net, www.diamondeye.net | 192.168.1.48:8081 | inspections-web (VM102) |
| 10 | tiktok.diamondeye.net | 192.168.1.136:4007 | Postiz (pop-ollama) |
| 11 | librarian.diamondeye.net | 192.168.1.107:3001 | AnythingLLM (VM107) |
| 12 | investigator.diamondeye.net | 192.168.1.108:3000 | VM108 (purpose unclear) |
| 13 | truth.diamondeye.net | 192.168.1.108:3000 | VM108 (purpose unclear) |
| 14 | openclaw.diamondeye.net | 192.168.1.221:18789 | MGMT-XPS OpenClaw — RETIRED 2026-09-07 |
| 15 | resume.diamondeye.net | 192.168.1.55:3000 | Resume Tool (VM105) |
| 16 | serberus.diamondeye.net | 192.168.1.108:9124 | Serberus Hermes (VM108) |

## SSL Certificate
- All 16 hosts use: `custom_ssl/npm-1` (Cloudflare Origin Certificate)
- Type: Custom SSL (not Let's Encrypt)
- Expiry: 2041 (per architecture docs)
- Recovery: Regenerate from Cloudflare dashboard → SSL/TLS → Origin Server → Create Certificate

## Recovery Notes
- To rebuild NPM: `docker run -d --name npm -p 80:80 -p 81:81 -p 443:443 jc21/nginx-proxy-manager:latest`
- Restore data bind: mount `/srv/npm/data` and `/srv/npm/letsencrypt`
- Re-add proxy hosts from conf files or use NPM UI
- Provision new Cloudflare Origin Certificate and load into custom_ssl/npm-1
