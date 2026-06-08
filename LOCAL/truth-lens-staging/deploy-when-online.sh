#!/bin/bash
# Truth Lens deployment helper
# Generated for VM 108 (de-gateway-01 / 192.168.1.2)

set -e

STAGING=/home/tunedr/AGENTS/LOCAL/truth-lens-staging
TARGET_HOST=192.168.1.2
SSH="ssh -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no -o BatchMode=yes tunedr@${TARGET_HOST}"
SCP="scp -i ~/.ssh/diamondeye_key -o StrictHostKeyChecking=no"

echo "=== Testing VM 108 connectivity ==="
if ! ping -c 1 -W 2 "${TARGET_HOST}" >/dev/null 2>&1; then
    echo "ERROR: VM 108 not reachable. Run this script when it comes back online."
    exit 1
fi

echo "=== Creating target directories ==="
$SSH 'mkdir -p /home/tunedr/truth-lens-data/prompts
      mkdir -p /home/tunedr/truth-lens-data/openwebui
      mkdir -p /home/tunedr/truth-lens-data/docs'

echo "=== Pushing Truth Lens pipe ==="
$SCP "${STAGING}/openwebui/truth_lens_pipe.py" \
    tunedr@${TARGET_HOST}:/home/tunedr/truth-lens-data/openwebui/truth_lens_pipe.py

echo "=== Pushing Truth Lens persona prompt ==="
$SCP "${STAGING}/prompts/agent.system.main.specifics.md" \
    tunedr@${TARGET_HOST}:/home/tunedr/truth-lens-data/prompts/agent.system.main.specifics.md

echo "=== Truth Lens deployment bundle staged ==="
echo "Next manual actions:"
echo "  1. Copy /home/tunedr/truth-lens-data/prompts/agent.system.main.specifics.md to /a0/prompts/agent.system.main.specifics.md"
echo "  2. Install truth_lens_pipe.py in the OpenWebUI custom pipe directory"
echo "  3. Set truth-lens-pipe as the default model for truth.diamondeye.net"
echo "  4. Configure NPM proxy and Cloudflare DNS for truth.diamondeye.net"

