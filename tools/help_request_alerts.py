#!/usr/bin/env python3
"""
help_request_alerts.py — email the team about new Help Center requests.

Reads help_requests where alerted_at is null (Supabase service key from tools/private/seo_automation.env),
sends an internal alert and, for Hire enquiries, a branded confirmation to the employer, then marks
them alerted. A dedicated launch agent checks every minute while the Mac is on.

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
DEFAULT_TO = ["sbarakat@outreachrecruitment.net"]
HIRE_TO = ["sbarakat@outreachrecruitment.net", "hr@outreachrecruitment.net", "azambrano@outreachrecruitment.net"]
OWNER = {"Hire": "Andrea Zambrano", "Study in Malta": "Jeraldin Daniela Bohorquez", "Jobs in Malta": "Julián Longan Granados", "General": "Katherin"}
LOGO = "https://outreachrecruitment.net/assets/job-card-logo.jpg"


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


def request_time(value: str) -> str:
    """Format Supabase timestamps, including fractional seconds shorter than six digits."""
    clean = value.replace("Z", "+00:00")
    clean = re.sub(r"\.(\d+)(?=[+-])", lambda m: "." + m.group(1)[:6].ljust(6, "0"), clean)
    return datetime.fromisoformat(clean).astimezone().strftime("%d %b %Y %H:%M")


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
                 ("Received", request_time(r["created_at"]))]
        table = "".join(f"<tr><td style='padding:4px 12px 4px 0;color:#666'>{k}</td><td style='padding:4px 0'><b>{html.escape(str(v))}</b></td></tr>" for k, v in facts if v)
        body = (f"<div style='font-family:Arial,sans-serif;font-size:15px'><h2 style='margin:0 0 12px'>New Help Center request — {html.escape(r['topic'])}</h2>"
                f"<table>{table}</table>"
                + (f"<p style='background:#f4f2ff;border-radius:10px;padding:12px 14px;white-space:pre-wrap'>{html.escape(r['message'])}</p>" if r.get("message") else "")
                + "<p><a href='https://outreachrecruitment.net/admin/#/helpdesk'>Open the Help Center inbox</a> — reply to this email to answer the person directly.</p></div>")
        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = f"🆕 Help Center · {r['topic']} · {r['full_name']}"
        recipients = HIRE_TO if r["topic"] == "Hire" else DEFAULT_TO
        msg["From"], msg["To"], msg["Reply-To"] = cfg["smtp_user"], ", ".join(recipients), r["email"]
        confirmation = None
        if r["topic"] == "Hire":
            first_name = html.escape(r["full_name"].split()[0])
            confirmation_body = f"""<div style="margin:0;background:#f4f3ee;padding:32px 16px;font-family:Arial,sans-serif;color:#1c2623">
              <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #e5e3dc;border-radius:18px;overflow:hidden">
                <div style="padding:24px 28px;border-bottom:1px solid #eceae4"><img src="{LOGO}" width="52" height="52" alt="Outreach Recruitment" style="display:block;border-radius:12px"></div>
                <div style="padding:28px"><h1 style="margin:0 0 14px;font-size:24px;line-height:1.25">Thank you, {first_name}</h1>
                  <p style="margin:0 0 14px;font-size:16px;line-height:1.6">We have received your hiring enquiry.</p>
                  <p style="margin:0 0 20px;font-size:16px;line-height:1.6">A member of the Outreach Recruitment team will contact you within one business day to discuss your recruitment requirements.</p>
                  <p style="margin:0;font-size:14px;line-height:1.6;color:#626762">If your request is urgent, reply to this email or contact <a href="mailto:hr@outreachrecruitment.net" style="color:#442DFA">hr@outreachrecruitment.net</a>.</p>
                </div>
                <div style="padding:18px 28px;background:#442DFA;color:#fff;font-size:13px">Outreach Recruitment · Your people, our priority</div>
              </div>
            </div>"""
            confirmation = MIMEText(confirmation_body, "html", "utf-8")
            confirmation["Subject"] = "We received your hiring enquiry | Outreach Recruitment"
            confirmation["From"], confirmation["To"], confirmation["Reply-To"] = cfg["smtp_user"], r["email"], "hr@outreachrecruitment.net"
        if "--dry-run" in argv:
            print("would send team alert:", msg["Subject"], "to", ", ".join(recipients))
            if confirmation:
                print("would send employer confirmation:", confirmation["Subject"], "to", r["email"])
            continue
        with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=60) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(cfg["smtp_user"], cfg["smtp_pass"])
            s.sendmail(cfg["smtp_user"], recipients, msg.as_string())
            if confirmation:
                s.sendmail(cfg["smtp_user"], [r["email"]], confirmation.as_string())
        api("PATCH", f"help_requests?id=eq.{r['id']}", {"alerted_at": datetime.now(timezone.utc).isoformat()})
        sent += 1
    print(f"help alerts: {sent} email(s) sent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
