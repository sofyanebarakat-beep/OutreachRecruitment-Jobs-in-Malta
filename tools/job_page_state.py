#!/usr/bin/env python3
"""
job_page_state.py — show a job page as CLOSED (or open again).

A closed job keeps every detail on its page, but:
  - the job title reads "<Title> — Position Closed" (h1 + <title>)
  - a banner under the header says applications are closed, with a link to open jobs
  - every Apply button is greyed out, unclickable and reads "Applications Closed"
  - the embedded apply form never loads (iframe data-src is parked)
  - the JobPosting validThrough stays in the past (set by the sync), so Google drops it

Every change is wrapped in "job-closed" markers, so mark_open() restores the page exactly.

Usage:
  python3 tools/job_page_state.py close <slug> [...]
  python3 tools/job_page_state.py open <slug> [...]
  python3 tools/job_page_state.py sync          # make every page match the registry status
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"

TITLE_TAG = '<span class="job-closed-tag"><!-- job-closed:h1 --> — Position Closed<!-- /job-closed:h1 --></span>'
TITLE_PREFIX = "Closed – "
NEW_BADGE = '<span class="job-badge job-badge-new">New</span>'
CLOSED_BADGE = '<!-- job-closed:badge --><span class="job-badge job-badge-closed">Closed</span><!-- /job-closed:badge -->'

STYLE_SCRIPT = """<!-- job-closed:head -->
<style id="job-closed-style">
.job-closed-banner{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:16px 0 8px;padding:14px 18px;
  border-radius:12px;background:#fef2f2;border:1px solid #fecaca;color:#991b1b;font-weight:600;line-height:1.4}
.job-closed-banner a{color:#991b1b;text-decoration:underline;font-weight:700}
.job-closed-tag{color:#b91c1c;white-space:nowrap}
.job-badge-closed{background:#fee2e2;color:#b91c1c}
.job-closed-banner+.job-header-badges{margin-top:4px}
[data-job-closed-disabled]{pointer-events:none!important;cursor:not-allowed!important;opacity:.45!important;
  filter:grayscale(1)!important}
</style>
<script id="job-closed-script">
document.addEventListener('DOMContentLoaded',function(){
  var sel='a[data-job-apply-trigger-closed],a[href="#how-to-apply"],a[href="#job-apply-panel"],a[href*="careers-page.com/jobs/"][href*="/apply"]';
  document.querySelectorAll(sel).forEach(function(a){
    a.setAttribute('data-job-closed-disabled','');a.setAttribute('aria-disabled','true');a.setAttribute('tabindex','-1');
    a.removeAttribute('href');
    var w=document.createTreeWalker(a,NodeFilter.SHOW_TEXT,null);var n;
    while((n=w.nextNode())){if(/apply/i.test(n.nodeValue)){n.nodeValue=n.nodeValue.replace(/apply( now)?( online)?/i,'Applications Closed');}}
    a.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();},true);
  });
});
</script>
<!-- /job-closed:head -->"""

BANNER = ('<!-- job-closed:banner --><div class="job-closed-banner" role="status" data-job-closed>'
          '<span>🔒 This position is closed — applications are no longer accepted.</span>'
          '<a href="/jobs/">Browse open jobs in Malta →</a></div><!-- /job-closed:banner -->')


def pages(slug: str) -> list[Path]:
    out = []
    for f in (ROOT / "jobs" / f"{slug}.html", ROOT / "jobs" / slug / "index.html"):
        if f.exists():
            text = f.read_text(encoding="utf-8", errors="replace")
            if len(text) > 5000 and 'http-equiv="refresh"' not in text[:3000].lower():
                out.append(f)
    return out


def is_marked(text: str) -> bool:
    return "<!-- job-closed:head -->" in text


def close_html(text: str) -> str:
    if is_marked(text):
        return text
    # Title: first h1 on the page (the job header) + <title>
    text = re.sub(r"(<h1\b[^>]*>)(.*?)(</h1>)", lambda m: m.group(1) + m.group(2) + TITLE_TAG + m.group(3),
                  text, count=1, flags=re.S)
    text = re.sub(r"<title>", f"<title>{TITLE_PREFIX}", text, count=1)
    # Banner full-width at the top of the header card (above the badges); older pages
    # without the badges row get it straight after the title.
    if '<div class="job-header-badges">' in text:
        text = text.replace('<div class="job-header-badges">', BANNER + '<div class="job-header-badges">', 1)
    else:
        text = text.replace("</h1>", "</h1>" + BANNER, 1)
    text = text.replace(NEW_BADGE, CLOSED_BADGE, 1)
    # Never load the apply form; park the trigger attribute
    text = text.replace('data-src="', 'data-job-closed-src="')
    text = text.replace("data-job-apply-trigger", "data-job-apply-trigger-closed")
    text = text.replace("</head>", STYLE_SCRIPT + "\n</head>", 1)
    return text


def open_html(text: str) -> str:
    if not is_marked(text):
        return text
    text = re.sub(r"<!-- job-closed:head -->.*?<!-- /job-closed:head -->\n?", "", text, flags=re.S)
    text = re.sub(r"<!-- job-closed:banner -->.*?<!-- /job-closed:banner -->", "", text, flags=re.S)
    text = text.replace(TITLE_TAG, "")
    text = text.replace(CLOSED_BADGE, NEW_BADGE)
    text = text.replace(f"<title>{TITLE_PREFIX}", "<title>", 1)
    text = text.replace("data-job-closed-src=\"", 'data-src="')
    text = text.replace("data-job-apply-trigger-closed", "data-job-apply-trigger")
    return text


def set_state(slug: str, closed: bool) -> list[str]:
    changed = []
    for f in pages(slug):
        text = f.read_text(encoding="utf-8")
        new = close_html(text) if closed else open_html(text)
        if new != text:
            f.write_text(new, encoding="utf-8")
            changed.append(str(f.relative_to(ROOT)))
    return changed


def sync_all() -> dict:
    """Make every job page match its registry status. Returns {closed: n, opened: n, touched: [...]}"""
    jobs = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    status_by_slug: dict[str, bool] = {}
    for j in jobs:  # a slug that is open anywhere in the registry counts as open
        closed = j.get("status", "").lower() in ("closed", "expired")
        status_by_slug[j["slug"]] = status_by_slug.get(j["slug"], True) and closed
    res = {"closed": 0, "opened": 0, "touched": []}
    for slug, closed in status_by_slug.items():
        t = set_state(slug, closed)
        if t:
            res["closed" if closed else "opened"] += 1
            res["touched"] += t
    return res


if __name__ == "__main__":
    cmd, slugs = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
    if cmd in ("close", "open"):
        for s in slugs:
            print(s, set_state(s, cmd == "close") or "no change")
    elif cmd == "sync":
        r = sync_all()
        print(f"closed {r['closed']} page(s), reopened {r['opened']}, files touched {len(r['touched'])}")
    else:
        print(__doc__)
