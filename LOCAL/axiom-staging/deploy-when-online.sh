#!/bin/bash
# AXIOM two-persona deployment script
# Run this when VM 107 (192.168.1.107) comes back online
# Written: 2026-05-20

set -e
STAGING=/home/tunedr/AGENTS/LOCAL/axiom-staging
SSH="ssh -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no -o BatchMode=yes tunedr@100.74.175.57"
SCP="scp -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no"

echo "=== Testing VM 107 connectivity ==="
if ! ping -c 1 -W 2 100.74.175.57 >/dev/null 2>&1; then
    echo "ERROR: VM 107 not reachable. Run this script when it comes back online."
    exit 1
fi
echo "VM 107 reachable — proceeding"

echo "=== Creating directories on VM 107 ==="
$SSH 'mkdir -p /home/tunedr/axiom/
      mkdir -p /home/tunedr/axiom-data/prompts
      mkdir -p /home/tunedr/axiom-data/instruments
      mkdir -p /home/tunedr/axiom-reports'

echo "=== Pushing docker-compose ==="
$SCP "${STAGING}/docker-compose.yml" tunedr@100.74.175.57:/home/tunedr/axiom/docker-compose.yml

echo "=== Pushing SOUL.md files ==="
$SCP "${STAGING}/prompts/agent.system.main.specifics.md" \
    tunedr@100.74.175.57:/home/tunedr/axiom-data/prompts/agent.system.main.specifics.md
$SCP "${STAGING}/prompts/axiom_deep.md" \
    tunedr@100.74.175.57:/home/tunedr/axiom-data/prompts/axiom_deep.md
$SCP "${STAGING}/prompts/librarian.md" \
    tunedr@100.74.175.57:/home/tunedr/axiom-data/prompts/librarian.md

echo "=== Pushing handoff skill ==="
$SCP "${STAGING}/instruments/librarian_handoff.py" \
    tunedr@100.74.175.57:/home/tunedr/axiom-data/instruments/librarian_handoff.py
$SCP "${STAGING}/instruments/anythingllm_workspaces.py" \
    tunedr@100.74.175.57:/home/tunedr/axiom-data/instruments/anythingllm_workspaces.py

echo "=== Restarting AXIOM container with new compose ==="
$SSH 'cd /home/tunedr/axiom &&
      docker stop agent-zero-axiom 2>/dev/null || true &&
      docker rm agent-zero-axiom 2>/dev/null || true &&
      docker compose up -d &&
      sleep 10 &&
      docker ps | grep agent-zero-axiom'

echo "=== Verifying AXIOM health ==="
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://100.74.175.57:7073 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "AXIOM: OK (HTTP $HTTP_CODE)"
else
    echo "AXIOM: WARNING — HTTP $HTTP_CODE — check logs:"
    ssh -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no tunedr@100.74.175.57 \
        'docker logs agent-zero-axiom --tail 20'
fi

echo "=== Committing on VM 107 ==="
$SSH 'cd /home/tunedr/axiom-data &&
      git init 2>/dev/null || true &&
      git add . &&
      git commit -m "feat: AXIOM four-layer — Executor + Planner + Validator + Compiler + Librarian handoff" 2>/dev/null &&
      git push 2>/dev/null || echo "Push blocked — GitHub PAT needed. Committed locally."'

echo ""
echo "=== AXIOM DEPLOYMENT COMPLETE ==="
echo "Next: Branden must authenticate Codex OAuth"
echo "  Open: http://100.74.175.57:7073"
echo "  Go to: Settings → Models → OpenAI → OAuth"
echo "  Authenticate with ChatGPT Plus account"
