#!/bin/bash
# /home/tunedr/AGENTS/bin/propagate-icm.sh
# Librarian ICM propagation — push canonical GLOBAL/ to all fleet machines
# Runs on VM107 de-librarian-01. Cron: every 6 hours.

set -euo pipefail

CANONICAL_GLOBAL="/home/tunedr/AGENTS/GLOBAL"
PUSH_LOG="/home/tunedr/AGENTS/LOCAL/push-log.md"
SSH_KEY="/home/tunedr/.ssh/id_ed25519"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DRY_RUN="${1:-}"

# Telegram config — read from env or CREDENTIALS.env
if [[ -f /home/tunedr/CREDENTIALS.env ]]; then
    source /home/tunedr/CREDENTIALS.env 2>/dev/null || true
fi
TG_TOKEN="${TELEGRAM_TOKEN_LIBRARIAN:-${LIBRARIAN_BOT_TOKEN:-}}"
TG_CHAT="${TELEGRAM_CHAT_ID:-${LIBRARIAN_CHAT_ID:-}}"

tg_send() {
    local msg="$1"
    if [[ -n "${TG_TOKEN:-}" && -n "${TG_CHAT:-}" ]]; then
        curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
            -d "chat_id=${TG_CHAT}" \
            -d "text=${msg}" \
            --max-time 10 >/dev/null 2>&1 || true
    fi
}

log() {
    echo "[$(date -u +%H:%M:%SZ)] $*"
}

# Target machines: name|ssh_target|remote_agents_path|ssh_key_flag
TARGETS=(
    "pop-ollama|tunedr@192.168.1.136|/home/tunedr/AGENTS|-i ${SSH_KEY}"
    "orchestrator|root@100.108.23.97|/root/AGENTS|-i /home/tunedr/.ssh/diamondeye_key"
    "de-gateway-01|tunedr@192.168.1.2|/home/tunedr/AGENTS|-i ${SSH_KEY}"
    "de-edge-01|tunedr@192.168.1.36|/home/tunedr/AGENTS|-i ${SSH_KEY}"
    "unraid|root@192.168.1.2|/mnt/user/appdata/agents|-i ${SSH_KEY}"
)

REACHED=()
FAILED=()
TOTAL_CHANGED=0

# Pull latest from git first
log "Pulling latest GLOBAL/ from git..."
if git -C "$(dirname "${CANONICAL_GLOBAL}")" pull --ff-only 2>&1; then
    log "Git pull OK"
else
    log "Git pull failed or no remote — continuing with local version"
fi

RSYNC_FLAGS="-avz --delete --exclude='*.bak*' --exclude='.git'"
if [[ "${DRY_RUN}" == "--dry-run" ]]; then
    log "DRY RUN MODE — no changes will be written"
    RSYNC_FLAGS="${RSYNC_FLAGS} --dry-run"
fi

for target_spec in "${TARGETS[@]}"; do
    IFS='|' read -r name ssh_target remote_path key_flag <<< "${target_spec}"

    log "--- ${name} (${ssh_target}) ---"

    # Test SSH connectivity
    if ! ssh ${key_flag} -o ConnectTimeout=8 -o StrictHostKeyChecking=no \
            -o BatchMode=yes "${ssh_target}" "echo ok" >/dev/null 2>&1; then
        log "UNREACHABLE: ${name}"
        FAILED+=("${name}")
        continue
    fi

    # Ensure GLOBAL/ directory exists on target
    ssh ${key_flag} -o StrictHostKeyChecking=no "${ssh_target}" \
        "mkdir -p ${remote_path}/GLOBAL/librarian ${remote_path}/LOCAL" 2>/dev/null || true

    # Rsync GLOBAL/ to target
    rsync_out=$(rsync ${RSYNC_FLAGS} \
        -e "ssh ${key_flag} -o StrictHostKeyChecking=no" \
        "${CANONICAL_GLOBAL}/" \
        "${ssh_target}:${remote_path}/GLOBAL/" 2>&1) || {
        log "RSYNC FAILED: ${name}"
        FAILED+=("${name}")
        continue
    }

    changed=$(echo "${rsync_out}" | grep -c "^>" 2>/dev/null) || changed=0
    TOTAL_CHANGED=$((TOTAL_CHANGED + changed))
    log "OK: ${name} — ${changed} file(s) changed"
    REACHED+=("${name}")
done

REACHED_STR="${REACHED[*]:-none}"
FAILED_STR="${FAILED[*]:-none}"

# Write push log
mkdir -p "$(dirname ${PUSH_LOG})"
{
    echo ""
    echo "## Push Run — ${TIMESTAMP}"
    echo "- Mode: ${DRY_RUN:-live}"
    echo "- Reached: ${REACHED_STR}"
    echo "- Failed: ${FAILED_STR}"
    echo "- Files changed: ${TOTAL_CHANGED}"
} >> "${PUSH_LOG}"

log "=== DONE: reached=[${REACHED_STR}] failed=[${FAILED_STR}] changed=${TOTAL_CHANGED} ==="

if [[ "${DRY_RUN}" != "--dry-run" ]]; then
    if [[ ${#FAILED[@]} -eq 0 ]]; then
        tg_send "✅ Librarian ICM sync complete ${TIMESTAMP} — Reached: ${REACHED_STR} — Files changed: ${TOTAL_CHANGED}"
        exit 0
    elif [[ ${#REACHED[@]} -gt 0 ]]; then
        tg_send "⚠️ Librarian ICM partial sync ${TIMESTAMP} — Reached: ${REACHED_STR} — Failed: ${FAILED_STR}"
        exit 1
    else
        tg_send "🚨 Librarian ICM sync FAILED ${TIMESTAMP} — All targets unreachable: ${FAILED_STR}"
        exit 2
    fi
fi
