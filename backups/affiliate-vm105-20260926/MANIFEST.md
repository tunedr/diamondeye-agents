# VM105 affiliate-engine-01 Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source host: affiliate-engine-01 (VM105) — 192.168.1.55

## Services Running (all healthy as of 2026-09-26)
| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| resume-tool | local build | :3000 | Tool-06 AI Resume Tailor → resume.diamondeye.net |
| agent-zero-affiliate | frdel/agent-zero-run:latest | :7072 | LEGACY — abandoned per 2026-07-20 |
| ae-n8n | n8nio/n8n:latest | :5679 | Affiliate workflows |
| ae-postgres | postgres | internal | n8n database |
| ae-redis | redis | internal | session cache |

## Archived Files
- `resume-tool-docker-compose.yml` — Resume tool compose (no inline secrets — uses env_file)

## Notes
- resume-tool uses `.env` file for secrets (not archived — contains API keys)
- resume-tool source is a local build — no upstream image; source code is in VM105:/home/tunedr/resume-tool/
- resume-tool is LIVE at https://resume.diamondeye.net (NPM proxy host 15 → VM105:3000)
- One known blocker: Gumroad product URL (Branden action item — see project_tool06_resume_tailor.md in memory)

## Resume Tool Source Gap
The resume-tool container is built from local source (`build: .`). The source code itself
is NOT yet in Git. This is a coverage gap for this resource.
Recommend: `git init` in VM105:/home/tunedr/resume-tool/ and push to a private GitHub repo.
