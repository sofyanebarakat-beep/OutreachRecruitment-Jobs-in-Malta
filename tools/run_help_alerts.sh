#!/bin/bash
# Poll new Help Center enquiries and send team/employer email notifications.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec /usr/bin/python3 "$SCRIPT_DIR/help_request_alerts.py"
