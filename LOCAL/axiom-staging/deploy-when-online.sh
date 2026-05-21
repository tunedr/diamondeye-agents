#!/bin/bash
# AXIOM two-persona deployment script
# Run this when VM 107 (192.168.1.107) comes back online
# Written: 2026-05-20

set -e
STAGING=/home/tunedr/AGENTS/LOCAL/axiom-staging
SSH="ssh -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no tunedr@192.168.1.107"
SCP="scp -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no"

echo "=== Testing VM 107 connectivity ==="
if ! ping -c 1 -W 2 192.168.1.107 >/dev/null 2>&1; then
    echo "ERROR: VM 107 not reachable. Run this script when it comes back online."
    exit 1
fi
echo "VM 107 reachable — proceeding"

echo "=== Creating directories on VM 107 ==="
$SSH 'mkdir -p /home/tunedr/axiom/
      mkdir -p /home/tunedr/axiom-data/usr/agents/agent0/prompts
      mkdir -p /home/tunedr/axiom-data/usr/agents/agent0/instruments
      mkdir -p /home/tunedr/axiom-reports'

echo "=== Pushing docker-compose ==="
$SCP "${STAGING}/docker-compose.yml" tunedr@192.168.1.107:/home/tunedr/axiom/docker-compose.yml

echo "=== Pushing SOUL.md files ==="
$SCP "${STAGING}/prompts/agent.system.main.specifics.md" \
    tunedr@192.168.1.107:/home/tunedr/axiom-data/usr/agents/agent0/prompts/agent.system.main.specifics.md
$SCP "${STAGING}/prompts/axiom_deep.md" \
    tunedr@192.168.1.107:/home/tunedr/axiom-data/usr/agents/agent0/prompts/axiom_deep.md

echo "=== Pushing handoff skill ==="
$SCP "${STAGING}/instruments/librarian_handoff.py" \
    tunedr@192.168.1.107:/home/tunedr/axiom-data/usr/agents/agent0/instruments/librarian_handoff.py

echo "=== Restarting AXIOM container with new compose ==="
$SSH 'cd /home/tunedr/axiom &&
      docker stop agent-zero-axiom 2>/dev/null || true &&
      docker rm agent-zero-axiom 2>/dev/null || true &&
      docker compose up -d &&
      sleep 10 &&
      docker ps | grep agent-zero-axiom'

echo "=== Verifying AXIOM health ==="
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://192.168.1.107:7073 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "AXIOM: OK (HTTP $HTTP_CODE)"
else
    echo "AXIOM: WARNING — HTTP $HTTP_CODE — check logs:"
    ssh -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no tunedr@192.168.1.107 \
        'docker logs agent-zero-axiom --tail 20'
fi

echo "=== Committing on VM 107 ==="
$SSH 'cd /home/tunedr/axiom-data &&
      git init 2>/dev/null || true &&
      git add . &&
      git commit -m "feat: AXIOM two-persona — Scout (deepseek) + Deep (Codex OAuth) + VIN + Librarian handoff" 2>/dev/null &&
      git push 2>/dev/null || echo "Push blocked — GitHub PAT needed. Committed locally."'

echo ""
echo "=== AXIOM DEPLOYMENT COMPLETE ==="
echo "Next: Branden must authenticate Codex OAuth"
echo "  Open: http://192.168.1.107:7073"
echo "  Go to: Settings → Models → OpenAI → OAuth"
echo "  Authenticate with ChatGPT Plus account"
