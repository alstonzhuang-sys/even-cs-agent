#!/bin/bash
# Daily Escalation Report - Automated Cron Job

# This script should be run daily (e.g., 9:00 AM) to send escalation report to Rosen

DATE=$(date -u +%Y-%m-%d)
REPORT_FILE="/tmp/escalation_report_${DATE}.md"

echo "Generating escalation report for $DATE..."

# Generate report
cd ~/.openclaw/workspace/even-cs-agent
python3 scripts/escalation_worker.py report --date "$DATE" > "$REPORT_FILE"

# Check if there are any cases
CASE_COUNT=$(grep -c "^###" "$REPORT_FILE" || echo "0")

if [ "$CASE_COUNT" -eq 0 ]; then
    echo "No escalations today. Skipping report."
    exit 0
fi

echo "Found $CASE_COUNT escalation cases. Sending report to Rosen..."

# TODO: Send to Rosen via Feishu
# For now, just print the report
cat "$REPORT_FILE"

echo ""
echo "To send to Rosen, use:"
echo "  feishu_im_user_message --action send --receive-id ou_xxx --msg-type text --content '{\"text\":\"...\"}'"

# Cleanup
rm -f "$REPORT_FILE"
