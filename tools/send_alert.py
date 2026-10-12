#!/usr/bin/env python3
"""send_alert.py — stdlib-only alert email, used by run_sync_agent.sh when the
daily sync dies in a way it could not report itself (e.g. a syntax/import error).

Usage: python3 tools/send_alert.py "Subject" "body text"
"""
import html
import json
import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from pathlib import Path

cfg = json.loads((Path(__file__).resolve().parent / "sync_config.json").read_text())
subject, body = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
msg = MIMEText(f"<pre style='white-space:pre-wrap'>{html.escape(body[-6000:])}</pre>", "html", "utf-8")
msg["Subject"], msg["From"], msg["To"] = subject, cfg["smtp_user"], "sbarakat@outreachrecruitment.net"
with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=60) as s:
    s.starttls(context=ssl.create_default_context())
    s.login(cfg["smtp_user"], cfg["smtp_pass"])
    s.sendmail(cfg["smtp_user"], [msg["To"]], msg.as_string())
print("alert sent")
