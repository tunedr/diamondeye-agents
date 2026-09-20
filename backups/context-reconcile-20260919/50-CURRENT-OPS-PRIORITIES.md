# 50 — Current Ops Priorities

Last updated: 2026-06-12 — Smoke Test session (YELLOW verdict)

## Status
Pipeline architecture built and substantially functional. Smoke test attempt: YELLOW.
Two targeted repairs needed before full GREEN smoke test is possible.

## Active Priorities (in order)

1. **Fix agent-zero-desk SSH access** ← NEXT SESSION
   - Mount `~/.ssh:/root/.ssh:ro` volume into agent-zero-desk container (docker-compose.yml)
   - Without SSH keys, Agent Zero cannot execute any fleet SSH commands
   - Alternatively: mount SSH agent socket `/run/user/1000/keyring/ssh:/ssh-agent:ro` + `SSH_AUTH_SOCK=/ssh-agent`
   - Test: `docker exec agent-zero-desk ssh tunedr@192.168.1.107 exit` should succeed after fix

2. **Fix Agent Zero chat model for tool-use compliance** ← NEXT SESSION
   - llama3.2:latest (3.2B): cannot follow Agent Zero JSON tool format at all
   - qwen2.5:7b: follows JSON but calls wrong tool name (`code_execution` vs `code_execution_tool`)
   - Options: (a) test llama3.1:8b on Unraid, OR (b) add explicit tool name hint in A2A packet context
   - Fleet model standard (llama3.2:latest) is insufficient for Agent Zero — needs separate standard

3. **Re-run smoke test** after above two fixes
   - Same test payload: SSH to VM107, docker exec hermes-librarian head -5 /opt/data/SOUL.md
   - Should complete in under 2 minutes with SSH keys + correct model

4. **Model routing confirmation** ← DONE
   - pop-ollama 192.168.1.136:11434 confirmed reachable via LAN as of 2026-06-12
   - Agent Zero embedding: fixed (api_base=http://192.168.1.2:11434/v1, provider=openai, custom_llm_provider=openai)
   - Hermes Desk delegation: llama3.2:latest (131K context, above 64K minimum)

3. **Grist repair on VM104**
   - Port 8484 connection refused — Proxmox console access required
   - Blocked: Tailscale on VM104 may be stopped; SSH from LAN blocked by design
   - Defer until Branden can access VM104 console

4. **Librarian 1:30am cron job creation**
   - hermes-librarian on VM107 has cron_mode:auto and timezone:America/Denver
   - No cron job exists in jobs.json — first scheduled run will not happen
   - Create via hermes-librarian cron API or n8n workflow

5. **OPENAI_API_KEY provisioning**
   - Blocks GPT-4o upgrade for hermes-desk
   - Blocks GPT-4o mini upgrade for hermes-librarian
   - Both currently functional on local Ollama models

## Deferred Work (do not do in this session)

- Fix pop-ollama Tailscale port 11434 exposure (separate task — pop-ollama is reachable via LAN now)
- Restore Grist on VM104 (requires Proxmox console)
- Create Librarian cron job (separate task)
- Remediate VM107 extra personas (apollo/truthlens base_url correction)
- Change global model-routing standard permanently
- Telegram end-to-end smoke test (requires interactive Branden session)

## Standing Hold

- No new Proxmox VM changes
- No Atlas n8n workflow edits without pipeline pause
- No pfSense changes
- No docker system prune without explicit Branden approval
