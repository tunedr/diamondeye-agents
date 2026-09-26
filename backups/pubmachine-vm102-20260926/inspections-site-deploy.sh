#!/bin/bash
# DiamondEye Inspections — Cloudflare Pages Deploy Script
# Usage: CLOUDFLARE_API_TOKEN=<token> bash deploy.sh
# Token must be a Cloudflare API token with Cloudflare Pages:Edit permission.
# DO NOT embed the token in this file or pass it as a positional argument.
# The env-var pattern keeps the secret out of process listings and shell history.
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="inspections-site"

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  echo "ERROR: CLOUDFLARE_API_TOKEN env var is required."
  echo "Usage: CLOUDFLARE_API_TOKEN=<token> bash deploy.sh"
  exit 1
fi

echo "[deploy] site dir: $SITE_DIR"
echo "[deploy] project:  $PROJECT_NAME"
echo "[deploy] running wrangler pages deploy..."

export CLOUDFLARE_API_TOKEN
npx wrangler pages deploy "$SITE_DIR" \
  --project-name "$PROJECT_NAME" \
  --commit-dirty=true

echo "[deploy] done"
