#!/bin/bash
# Daily Escalation Report - Automated Cron Job
#
# This script generates and optionally sends the daily escalation report.
#
# Usage:
#   ./scripts/daily_report.sh              # Generate today's report
#   ./scripts/daily_report.sh 2026-03-17   # Generate report for specific date
#
# Cron setup (run daily at 9:00 AM):
#   0 9 * * * cd ~/.openclaw/workspace/even-cs-agent && ./scripts/daily_report.sh >> logs/daily_report.log 2>&1
#
# OpenClaw cron setup:
#   openclaw cron add --name "cs-daily-report" --schedule "0 9 * * *" \
#     --command "cd ~/.openclaw/workspace/even-cs-agent && ./scripts/daily_report.sh"

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Use provided date or today
DATE="${1:-$(date -u +%Y-%m-%d)}"
REPORT_FILE="/tmp/escalation_report_${DATE}.md"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Generating escalation report for $DATE..."

# Generate report
python3 scripts/escalation_worker.py report --date "$DATE" > "$REPORT_FILE"

# Check if there are any cases
CASE_COUNT=$(grep -c "^###" "$REPORT_FILE" 2>/dev/null || echo "0")

if [ "$CASE_COUNT" -eq 0 ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] No escalations for $DATE. Skipping."
    rm -f "$REPORT_FILE"
    exit 0
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Found $CASE_COUNT escalation cases."

# Read Rosen's Feishu ID from config
ROSEN_ID=$(python3 -c "
import json
from pathlib import Path
config_file = Path('config/channels.json')
if config_file.exists():
    config = json.load(open(config_file))
    print(config.get('rosen_contact', {}).get('feishu_id', ''))
" 2>/dev/null)

if [ -z "$ROSEN_ID" ] || [ "$ROSEN_ID" = "ou_xxx" ]; then
    echo "[WARN] Rosen's Feishu ID not configured. Printing report to stdout."
    cat "$REPORT_FILE"
else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Report ready for Rosen ($ROSEN_ID)."
    cat "$REPORT_FILE"
    echo ""
    echo "To send via OpenClaw:"
    echo "  feishu_im_user_message --action send --receive-id-type open_id --receive-id $ROSEN_ID --msg-type text --content '{\"text\":\"$(head -5 "$REPORT_FILE" | tr '\n' ' ')\"}'"
fi

# Cleanup
rm -f "$REPORT_FILE"

