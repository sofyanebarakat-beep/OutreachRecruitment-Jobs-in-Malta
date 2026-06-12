#!/bin/bash
# run_sync_agent.sh — Run the job sync agent and log output
# Registered with launchd for automated scheduling

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/reports/logs"
LOG_FILE="$LOG_DIR/sync-$(date +%Y-%m-%d-%H%M).log"

mkdir -p "$LOG_DIR"

echo "=== Job Sync Agent ===" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"

python3 "$SCRIPT_DIR/job_sync_agent.py" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}
echo "Finished: $(date) | Exit: $EXIT_CODE" | tee -a "$LOG_FILE"

# Keep only last 20 logs
ls -t "$LOG_DIR"/sync-*.log 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null

exit $EXIT_CODE
