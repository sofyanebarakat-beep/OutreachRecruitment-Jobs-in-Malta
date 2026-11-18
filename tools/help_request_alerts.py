#!/usr/bin/env python3
"""
help_request_alerts.py — email the team about new Help Center requests.

Reads help_requests where alerted_at is null (Supabase service key from tools/private/seo_automation.env),
sends one email per new request (subject shows the topic and name, Reply-To is the person), then marks
them alerted. Runs every hour from tools/run_sync_agent.sh (07:00–20:00 while the Mac is on).

Usage: python3 tools/help_request_alerts.py [--dry-run]
"""
from __future__ import annotations

import html
import json
import re
import smtplib
import ssl
import sys
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
TO = ["sbarakat@outreachrecruitment.net"]
OWNER = {"Hire": "Andrea Zambrano", "Study in Malta": "Jeraldin Daniela Bohorquez", "Jobs in Malta": "Julián Longan Granados", "General": "Katherin"}


def env() -> dict:
    out = {}
    for line in (ROOT / "tools" / "private" / "seo_automation.env").read_text().splitlines():
        m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out


def api(method: str, path: str, body=None):
    e = env()
    req = Request(e["SUPABASE_URL"].rstrip("/") + "/rest/v1/" + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                  headers={"apikey": e["SUPABASE_SERVICE_ROLE_KEY"], "Authorization": f"Bearer {e['SUPABASE_SERVICE_ROLE_KEY']}",
                           "Content-Type": "application/json", "Prefer": "return=minimal"})
    with urlopen(req, timeout=40) as r:
        raw = r.read()
        return json.loads(raw) if raw else None


def main(argv: list[str]) -> int:
    try:
        rows = api("GET", "help_requests?select=*&alerted_at=is.null&order=created_at.asc&limit=50") or []
    except Exception as exc:  # table/column missing (migration not run) or offline: nothing to do
        print(f"help alerts: skipped ({exc})")
        return 0
    if not rows:
        print("help alerts: no new requests")
        return 0
    cfg = json.loads((ROOT / "tools" / "sync_config.json").read_text())
    sent = 0
    for r in rows:
        d = r.get("details") or {}
        facts = [("Topic", r["topic"]), ("Name", r["full_name"]), ("Email", r["email"]), ("Phone", r.get("phone")), ("Company", r.get("company")),
                 ("Current location", r.get("current_location")), ("Nationality", r.get("nationality")), ("Job", r.get("job_title")),
                 ("Wants to study", d.get("study_level")), ("Start", d.get("start_when")), ("Suggested owner", OWNER.get(r["topic"])),
                 ("Received", datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).astimezone().strftime("%d %b %Y %H:%M"))]
        table = "".join(f"<tr><td style='padding:4px 12px 4px 0;color:#666'>{k}</td><td style='padding:4px 0'><b>{html.escape(str(v))}</b></td></tr>" for k, v in facts if v)
        body = (f"<div style='font-family:Arial,sans-serif;font-size:15px'><h2 style='margin:0 0 12px'>New Help Center request — {html.escape(r['topic'])}</h2>"
                f"<table>{table}</table>"
                + (f"<p style='background:#f4f2ff;border-radius:10px;padding:12px 14px;white-space:pre-wrap'>{html.escape(r['message'])}</p>" if r.get("message") else "")
                + "<p><a href='https://outreachrecruitment.net/admin/#/helpdesk'>Open the Help Center inbox</a> — reply to this email to answer the person directly.</p></div>")
        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = f"🆕 Help Center · {r['topic']} · {r['full_name']}"
        msg["From"], msg["To"], msg["Reply-To"] = cfg["smtp_user"], ", ".join(TO), r["email"]
        if "--dry-run" in argv:
            print("would send:", msg["Subject"])
            continue
        with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=60) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(cfg["smtp_user"], cfg["smtp_pass"])
            s.sendmail(cfg["smtp_user"], TO, msg.as_string())
        api("PATCH", f"help_requests?id=eq.{r['id']}", {"alerted_at": datetime.now(timezone.utc).isoformat()})
        sent += 1
    print(f"help alerts: {sent} email(s) sent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
