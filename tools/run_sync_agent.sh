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

# 1) Open/close jobs to match the careers page, build new jobs with the
#    /job-seo-generator skill, push, and email the report at 09:00 Malta time.
echo "=== Daily Job Sync (open/close) ===" | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/daily_job_sync.py" --send-at 09:00 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}
# Exit 2 = the sync caught its own crash and already emailed an alert. Anything else
# non-zero (syntax/import error, killed) gets a plain alert from here.
if [ "$EXIT_CODE" -ne 0 ] && [ "$EXIT_CODE" -ne 2 ]; then
  python3 "$SCRIPT_DIR/send_alert.py" "⚠️ Daily job sync FAILED — $(date +%Y-%m-%d) (exit $EXIT_CODE)" \
    "$(tail -n 60 "$LOG_FILE")" 2>&1 | tee -a "$LOG_FILE"
fi

# 2) The older SEO/GSC analysis report — saved to reports/, no second email.
echo "" | tee -a "$LOG_FILE"
echo "=== SEO / GSC analysis (job_sync_agent.py, no email) ===" | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/job_sync_agent.py" --no-email 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "=== SEO Course Automation ===" | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/apply_analytics_tracking.py" 2>&1 | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/seo_course_automation.py" 2>&1 | tee -a "$LOG_FILE"
SEO_EXIT_CODE=${PIPESTATUS[0]}
echo "Finished: $(date) | Exit: $EXIT_CODE" | tee -a "$LOG_FILE"

# Keep only last 20 logs
ls -t "$LOG_DIR"/sync-*.log 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null

if [ "$SEO_EXIT_CODE" -ne 0 ]; then
  exit "$SEO_EXIT_CODE"
fi
exit "$EXIT_CODE"
