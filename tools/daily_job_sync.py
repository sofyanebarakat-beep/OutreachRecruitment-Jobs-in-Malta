#!/usr/bin/env python3
"""
daily_job_sync.py — keep outreachrecruitment.net/jobs/ identical to the ATS.

Source of truth: https://outreach-recruitment-agency.careers-page.com/
Website:         tools/jobs_registry.json  →  https://outreachrecruitment.net/jobs/

Every run:
  1. Scrape every open ATS job (listing pages, 2 passes, then per-city filter
     pages if anything is still missing). Jobs are matched by ATS UUID — the UUID
     in each registry job's apply_url — never by title (titles repeat).
  2. CLOSE  site jobs whose UUID is gone from the ATS *and* whose ATS page
     /jobs/<uuid> returns 404. A job that is merely unseen in the listing
     (rate-limit, unstable pagination) but still answers 200 stays open.
  3. REOPEN registry jobs (closed/expired) whose UUID is open again on the ATS.
  4. CREATE pages for brand-new ATS jobs with the /job-seo-generator skill
     (headless `claude -p`, spec in "Jobs Skills/job-seo-generator/").
  5. Rebuild /jobs listing + sitemap, verify, commit + push to main.
  6. Email the report (optionally held until --send-at HH:MM local time).

Usage:
  python3 tools/daily_job_sync.py                  # full run
  python3 tools/daily_job_sync.py --dry-run        # compare + report only, change nothing
  python3 tools/daily_job_sync.py --no-create      # open/close only, list new jobs
  python3 tools/daily_job_sync.py --no-push --no-email
  python3 tools/daily_job_sync.py --send-at 09:00  # hold the email until 09:00
"""
from __future__ import annotations

import html as htmllib
import json
import re
import shutil
import smtplib
import ssl
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
CONFIG_PATH = ROOT / "tools" / "sync_config.json"
REPORT_DIR = ROOT / "reports" / "daily-sync"
SKILL_DIR = ROOT / "Jobs Skills" / "job-seo-generator"

ATS = "https://outreach-recruitment-agency.careers-page.com"
SITE = "https://outreachrecruitment.net"
REPORT_RECIPIENT = "sbarakat@outreachrecruitment.net"

LIST_DELAY = 6          # seconds between ATS listing requests
DETAIL_DELAY = 4        # seconds between ATS /jobs/<uuid> checks
MAX_CLOSES_PER_RUN = 25  # safety brake: more than this in one day = something is wrong
MAX_CREATES_PER_RUN = 10
OPEN_VALID_THROUGH = "2029-12-30"
CLAUDE_TIMEOUT = 75 * 60

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
CARD_RE = re.compile(r"<a\b[^>]*\bdata-job-id=\"[^\"]+\"[^>]*>", re.S)
ATTR_RE = re.compile(r'data-job-(id|title|city)="([^"]*)"')
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP
# ─────────────────────────────────────────────────────────────────────────────

def fetch(url: str, retries: int = 6) -> tuple[int, str]:
    """GET with 429/network backoff. Returns (status, body); 404 is a valid answer."""
    for attempt in range(1, retries + 1):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=30) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except HTTPError as e:
            if e.code == 404:
                return 404, ""
            if attempt == retries:
                return e.code, ""
            wait = 30 * attempt if e.code == 429 else 5 * attempt
        except (URLError, OSError) as e:
            if attempt == retries:
                return 0, ""
            wait = 10 * attempt
        log(f"    retry {attempt}/{retries - 1} in {wait}s ({url})")
        time.sleep(wait)
    return 0, ""


def parse_cards(page_html: str) -> dict[str, dict]:
    jobs: dict[str, dict] = {}
    for tag in CARD_RE.findall(page_html):
        attrs = dict(ATTR_RE.findall(tag))
        uid = attrs.get("id", "")
        if UUID_RE.fullmatch(uid):  # a card repeats its id on several tags — merge them
            job = jobs.setdefault(uid, {"uuid": uid, "title": "", "city": ""})
            for key in ("title", "city"):
                job[key] = job[key] or htmllib.unescape(attrs.get(key, "")).strip()
    return jobs


def scrape_listing(base_url: str, found: dict[str, dict]) -> tuple[int, str]:
    """Walk ?page=N for one listing URL. Returns (advertised_count, first_page_html)."""
    sep = "&" if "?" in base_url else "?"
    advertised, first_html, page, last = 0, "", 1, 1
    while page <= max(last, 1) and page <= 40:
        status, body = fetch(base_url if page == 1 else f"{base_url}{sep}page={page}")
        if status != 200:
            raise RuntimeError(f"ATS listing returned HTTP {status} for page {page}")
        if page == 1:
            first_html = body
            m = re.search(r"(\d+)\s+Open\s+Positions", body, re.I)
            advertised = int(m.group(1)) if m else 0
        last = max([last] + [int(n) for n in re.findall(r"[?&]page=(\d+)", body)])
        cards = parse_cards(body)
        if not cards:
            break
        for uid, job in cards.items():
            prev = found.get(uid, {})
            found[uid] = {k: job[k] or prev.get(k, "") for k in job}
        page += 1
        time.sleep(LIST_DELAY)
    return advertised, first_html


def scrape_ats() -> tuple[dict[str, dict], int, list[str]]:
    notes: list[str] = []
    found: dict[str, dict] = {}
    advertised, first_html = scrape_listing(f"{ATS}/", found)
    log(f"  pass 1: {len(found)} / {advertised} advertised")
    if len(found) < advertised:
        scrape_listing(f"{ATS}/", found)
        log(f"  pass 2: {len(found)} / {advertised}")
    if len(found) < advertised:
        cities = sorted(set(htmllib.unescape(c) for c in
                            re.findall(r'name="cities"\s+value="([^"]*)"', first_html)))
        log(f"  city-filter pass over {len(cities)} cities …")
        for city in cities:
            scrape_listing(f"{ATS}/?cities={quote(city)}", found)
        log(f"  after city pass: {len(found)} / {advertised}")
    if advertised and len(found) != advertised:
        notes.append(f"ATS advertises {advertised} but {len(found)} unique jobs were collected "
                     f"(the ATS listing pages are not always consistent).")
    return found, advertised, notes


def ats_job_is_live(uid: str) -> bool | None:
    """True = open (200), False = closed (404 / 'no longer available'), None = unknown."""
    status, body = fetch(f"{ATS}/jobs/{uid}")
    if status == 404 or (status == 200 and "no longer available" in body.lower()):
        return False
    if status == 200:
        return True
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Registry + page edits
# ─────────────────────────────────────────────────────────────────────────────

def is_open(job: dict) -> bool:
    return job.get("status", "active").lower() not in ("closed", "expired")


def job_uuid(job: dict) -> str:
    m = UUID_RE.search(job.get("apply_url", ""))
    return m.group(0) if m else ""


def load_registry() -> list[dict]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(jobs: list[dict]) -> None:
    REGISTRY_PATH.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def page_files(slug: str) -> list[Path]:
    # GitHub Pages serves jobs/<slug>.html over jobs/<slug>/index.html — keep both in step.
    return [p for p in (ROOT / "jobs" / slug / "index.html", ROOT / "jobs" / f"{slug}.html") if p.exists()]


def set_page_valid_through(slug: str, value: str) -> None:
    for path in page_files(slug):
        TOUCHED.add(str(path.relative_to(ROOT)))
        text = path.read_text(encoding="utf-8")
        new = re.sub(r'("validThrough"\s*:\s*)"[^"]*"', rf'\1"{value}"', text)
        if new != text:
            path.write_text(new, encoding="utf-8")


TOUCHED: set[str] = set()


def site_url(slug: str) -> str:
    return f"{SITE}/jobs/{slug}/"


# ─────────────────────────────────────────────────────────────────────────────
# New jobs via the /job-seo-generator skill (headless Claude Code)
# ─────────────────────────────────────────────────────────────────────────────

def claude_bin() -> str | None:
    return shutil.which("claude") or next(
        (p for p in (str(Path.home() / ".local/bin/claude"), "/opt/homebrew/bin/claude",
                     "/usr/local/bin/claude") if Path(p).exists()), None)


def create_jobs_prompt(new_jobs: list[dict]) -> str:
    lines = "\n".join(f"- {j['title']} ({j['city'] or 'city: see ATS page'}) — {ATS}/jobs/{j['uuid']}"
                      for j in new_jobs)
    return f"""You are the unattended daily job-sync agent for this repo (Outreach Recruitment).
These jobs are OPEN on the ATS (careers-page.com) but have no page on outreachrecruitment.net:

{lines}

For EACH job, run the /job-seo-generator skill exactly as specified in
"Jobs Skills/job-seo-generator/SKILL.md" (+ its references/) and publish it on the site:
1. Fetch the ATS job page (and its ld+json) to get the real description, city, employment
   type and salary. Never invent a salary — if the source has none, write "Competitive salary".
2. Apply the saved defaults from your project memory (feedback_job_skill_defaults): Full-time
   unless the source says otherwise, On-site, Apply online, reference number and deadline kept
   PRIVATE (validThrough {OPEN_VALID_THROUGH} in schema + registry only, never visible text),
   FAQ closed by default, schema FAQ == visible FAQ.
3. Build the page by cloning a current rich job page (e.g. jobs/head-chef-in-gozo/index.html or
   jobs/client-accountant/index.html — NOT jobs/plumber via add_jobs_from_csv.py) and regenerate
   every job-specific part (head/meta, all JSON-LD blocks, header chips, sidebar, body sections,
   FAQ, similar jobs, share links, apply panel/iframe, JOB_REF). Write BOTH jobs/<slug>/index.html
   and jobs/<slug>.html with identical content.
4. The apply_url MUST be {ATS}/jobs/<that job's uuid>/apply — double-check every job's uuid.
5. Add the job to tools/jobs_registry.json (no "status" key = open; valid_through {OPEN_VALID_THROUGH}),
   then run: python3 tools/update_jobs_listing.py
6. Check there are no leaks from the template page (old title, city, slug, uuid, salary) and no
   private data (reference number, deadline, 2029) in visible text.
7. Save the 12-section package to reports/job-seo-<slug>-{date.today().isoformat()}.md.

Rules: do NOT git commit or push (the sync script verifies and pushes). Do NOT close, expire or
edit any other job. If a job cannot be built properly, skip it and say why.
End with one line per job: CREATED <uuid> <slug>  or  SKIPPED <uuid> <reason>.
"""


def create_new_jobs(new_jobs: list[dict], log_path: Path) -> tuple[list[dict], list[dict]]:
    """Returns (created, failed). Success is verified from the registry, not Claude's words."""
    exe = claude_bin()
    if not exe:
        return [], [dict(j, reason="claude CLI not found") for j in new_jobs]
    log(f"  running /job-seo-generator via headless Claude for {len(new_jobs)} job(s) …")
    try:
        result = subprocess.run(
            [exe, "-p", create_jobs_prompt(new_jobs), "--dangerously-skip-permissions",
             "--max-turns", "400", "--output-format", "text"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=CLAUDE_TIMEOUT,
        )
        log_path.write_text(result.stdout + "\n--- stderr ---\n" + result.stderr, encoding="utf-8")
    except subprocess.TimeoutExpired:
        log_path.write_text("Claude run timed out", encoding="utf-8")

    registry = load_registry()
    by_uuid = {job_uuid(j): j for j in registry if is_open(j)}
    created, failed = [], []
    for j in new_jobs:
        reg = by_uuid.get(j["uuid"])
        if not reg:
            failed.append(dict(j, reason="not added to registry"))
            continue
        pages = page_files(reg["slug"])
        problems = []
        if len(pages) < 2:
            problems.append("missing jobs/<slug>/index.html or jobs/<slug>.html")
        for p in pages:
            text = p.read_text(encoding="utf-8")
            if j["uuid"] not in text:
                problems.append(f"{p.name} does not contain the ATS uuid")
        if problems:
            # Keep a half-built page off the live listing: drop it from the registry.
            registry.remove(reg)
            failed.append(dict(j, slug=reg["slug"], reason="; ".join(problems) + " — not published"))
        else:
            TOUCHED.update(str(p.relative_to(ROOT)) for p in pages)
            TOUCHED.update(str(p.relative_to(ROOT))
                           for p in (ROOT / "reports").glob(f"job-seo-{reg['slug']}-*.md"))
            created.append(dict(j, slug=reg["slug"], url=site_url(reg["slug"])))
    save_registry(registry)
    subprocess.run([sys.executable, str(ROOT / "tools" / "update_jobs_listing.py")], cwd=str(ROOT))
    return created, failed


# ─────────────────────────────────────────────────────────────────────────────
# Git
# ─────────────────────────────────────────────────────────────────────────────

def git(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True, check=check)


def git_preflight() -> str | None:
    """Make sure we start from an up-to-date main. Returns an error string or None."""
    branch = git("branch", "--show-current").stdout.strip()
    if branch != "main":
        return f"repo is on branch '{branch}', not main"
    if git("status", "--porcelain", "--", "tools/jobs_registry.json").stdout.strip():
        return "tools/jobs_registry.json has uncommitted changes from someone else"
    git("fetch", "origin", "main")
    pull = git("pull", "--ff-only", "origin", "main")
    if pull.returncode != 0:
        return f"git pull --ff-only failed: {pull.stderr.strip()[:200]}"
    return None


LISTING_FILES = ["tools/jobs_registry.json", "jobs/index.html", "index.html", "sitemaps/sitemap-jobs.xml",
                 "sitemap_index.xml", "sitemap.xml"]


def git_commit_push(message: str, push: bool, touched: set[str]) -> str:
    # Stage only what this run touched — never sweep in other people's uncommitted edits.
    paths = set(LISTING_FILES) | touched | {"reports/daily-sync"}
    git("add", "--", *sorted(p for p in paths if (ROOT / p).exists()))
    if not git("diff", "--cached", "--quiet").returncode:
        return "nothing to commit"
    commit = git("commit", "-m", message + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    if commit.returncode != 0:
        return f"commit failed: {commit.stderr.strip()[:200]}"
    if not push:
        return "committed (push skipped)"
    for _ in range(3):
        git("fetch", "origin", "main")
        merge = git("merge", "--no-edit", "origin/main")
        if merge.returncode != 0:
            git("merge", "--abort")
            return "committed locally — merge with origin/main had conflicts, NOT pushed"
        if git("push", "origin", "main").returncode == 0:
            return "pushed to GitHub (main)"
        time.sleep(20)
    return "committed locally — push failed 3 times"


# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────

def esc(s: object) -> str:
    return htmllib.escape(str(s))


def job_list_html(rows: list[dict], empty: str, link_key: str = "url", extra: str = "") -> str:
    if not rows:
        return f'<p style="color:#666;margin:4px 0 12px">{empty}</p>'
    items = []
    for r in rows:
        title = esc(r.get("title", ""))
        link = r.get(link_key)
        label = f'<a href="{esc(link)}">{title}</a>' if link else title
        city = f' <span style="color:#777">— {esc(r["city"])}</span>' if r.get("city") else ""
        why = f' <span style="color:#b45309">({esc(r[extra])})</span>' if extra and r.get(extra) else ""
        items.append(f"<li>{label}{city}{why}</li>")
    return '<ul style="margin:4px 0 12px;padding-left:20px">' + "".join(items) + "</ul>"


def build_report(r: dict) -> tuple[str, str, str]:
    in_sync = r["site_open_after"] == r["ats_advertised"]
    badge = "✅ In sync" if in_sync else "⚠️ Not in sync"
    if r.get("dry_run"):
        badge += " (report only — nothing was changed; lists show what WOULD happen)"
    subject = (f"Job sync {r['date']}: {badge} — ATS {r['ats_advertised']} / website "
               f"{r['site_open_after']} (+{len(r['created']) + len(r['reopened'])} opened, "
               f"-{len(r['closed'])} closed)")
    color = "#15803d" if in_sync else "#b45309"
    stat = lambda n, label: (f'<td style="padding:10px 14px;border:1px solid #e5e7eb;text-align:center">'
                             f'<div style="font-size:24px;font-weight:700">{esc(n)}</div>'
                             f'<div style="font-size:12px;color:#555">{label}</div></td>')
    notes = "".join(f"<li>{esc(n)}</li>" for n in r["notes"])
    html = f"""<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;max-width:720px;color:#111">
<h2 style="margin:0 0 4px">Daily Job Sync — {esc(r['date'])}</h2>
<p style="margin:0 0 14px;color:{color};font-weight:700">{badge}</p>
<table style="border-collapse:collapse;margin-bottom:16px"><tr>
{stat(r['ats_advertised'], 'Open on careers page')}
{stat(r['site_open_before'], 'Website before')}
{stat(r['site_open_after'], 'Website now')}
</tr></table>
<h3 style="margin:14px 0 4px">🆕 New jobs published ({len(r['created'])})</h3>
{job_list_html(r['created'], 'None today.')}
<h3 style="margin:14px 0 4px">♻️ Reopened ({len(r['reopened'])})</h3>
{job_list_html(r['reopened'], 'None today.')}
<h3 style="margin:14px 0 4px">🔒 Closed ({len(r['closed'])})</h3>
{job_list_html(r['closed'], 'None today.')}
<h3 style="margin:14px 0 4px">⚠️ Needs your attention ({len(r['failed']) + len(r['held'])})</h3>
{job_list_html(r['failed'] + r['held'], 'Nothing.', link_key='ats_url', extra='reason')}
{f'<h3 style="margin:14px 0 4px">Notes</h3><ul style="padding-left:20px">{notes}</ul>' if notes else ''}
<p style="color:#555;font-size:13px;margin-top:18px">Git: {esc(r['git'])}.
{'Changes are in GitHub/Lovable — if the live site does not show them, click <b>Publish → Update</b>.' if 'pushed' in r['git'] else ''}<br>
Careers page: <a href="{ATS}/">{ATS}</a> · Website: <a href="{SITE}/jobs/">{SITE}/jobs/</a></p>
</div>"""
    md = [f"# Daily Job Sync — {r['date']}", "", f"**{badge}** — ATS {r['ats_advertised']}, "
          f"website {r['site_open_before']} → {r['site_open_after']}", ""]
    for key, label in (("created", "New jobs published"), ("reopened", "Reopened"), ("closed", "Closed"),
                       ("failed", "Failed to create"), ("held", "Held back (safety)")):
        md.append(f"## {label} ({len(r[key])})")
        md += [f"- {j.get('title')} — {j.get('url') or j.get('ats_url', '')}"
               + (f" ({j['reason']})" if j.get("reason") else "") for j in r[key]] or ["- none"]
        md.append("")
    if r["notes"]:
        md += ["## Notes"] + [f"- {n}" for n in r["notes"]] + [""]
    md.append(f"Git: {r['git']}")
    return subject, html, "\n".join(md) + "\n"


def send_email(subject: str, html_body: str) -> str:
    try:
        cfg = json.loads(CONFIG_PATH.read_text())
    except Exception:
        return "email skipped — tools/sync_config.json missing"
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, cfg["smtp_user"], REPORT_RECIPIENT
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    for attempt in range(3):
        try:
            with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=60) as s:
                s.starttls(context=ssl.create_default_context())
                s.login(cfg["smtp_user"], cfg["smtp_pass"])
                s.sendmail(cfg["smtp_user"], [REPORT_RECIPIENT], msg.as_string())
            return f"email sent to {REPORT_RECIPIENT}"
        except Exception as e:  # network blips at wake-up are common
            err = str(e)
            time.sleep(60)
    return f"email FAILED: {err[:200]}"


def wait_until(hhmm: str) -> None:
    h, m = map(int, hhmm.split(":"))
    target = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
    secs = (target - datetime.now()).total_seconds()
    if secs > 0:
        log(f"  holding the report until {hhmm} ({int(secs // 60)} min) …")
        time.sleep(secs)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    args = sys.argv[1:]
    dry = "--dry-run" in args
    push = not dry and "--no-push" not in args
    email = not dry and "--no-email" not in args
    create = not dry and "--no-create" not in args
    send_at = args[args.index("--send-at") + 1] if "--send-at" in args else None

    today = date.today().isoformat()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    log(f"=== Daily job sync {datetime.now():%Y-%m-%d %H:%M} {'(DRY RUN)' if dry else ''} ===")

    r: dict = {"date": today, "created": [], "reopened": [], "closed": [], "failed": [],
               "held": [], "notes": [], "git": "no changes"}

    r["dry_run"] = dry
    if not dry:
        err = git_preflight()
        if err:
            r["notes"].append(f"Did not change anything: {err}.")
            dry, push, create = True, False, False
            r["dry_run"] = True
            log(f"  PREFLIGHT: {err} — running report-only")

    # 1. ATS
    log("\n[1] Scraping careers page …")
    try:
        ats, advertised, notes = scrape_ats()
    except Exception as e:
        ats, advertised, notes = {}, 0, []
        r["notes"].append(f"Could not read the careers page ({e}). No jobs were opened or closed.")
    r["notes"] += notes
    r["ats_advertised"] = advertised

    registry = load_registry()
    open_jobs = {job_uuid(j): j for j in registry if is_open(j) and job_uuid(j)}
    all_by_uuid: dict[str, dict] = {}
    for j in registry:  # prefer the most recently touched entry when a uuid repeats
        u = job_uuid(j)
        if u and (u not in all_by_uuid or j.get("lastmod", "") >= all_by_uuid[u].get("lastmod", "")):
            all_by_uuid[u] = j
    r["site_open_before"] = sum(1 for j in registry if is_open(j))
    log(f"  ATS: {len(ats)} collected / {advertised} advertised · website open: {r['site_open_before']}")

    if not ats or not advertised:
        r["site_open_after"] = r["site_open_before"]
        dry, push, create = True, False, False
        r["dry_run"] = True

    # 2. Close — only on a confirmed ATS 404
    to_check = [u for u in open_jobs if u not in ats] if ats else []
    log(f"\n[2] {len(to_check)} website job(s) not in the ATS listing — checking each ATS page …")
    to_close = []
    for u in to_check:
        live = ats_job_is_live(u)
        j = open_jobs[u]
        log(f"  {j['title']} ({u[:8]}) → {'OPEN' if live else 'CLOSED' if live is False else 'UNKNOWN'}")
        if live is False:
            to_close.append(j)
        elif live is None:
            r["held"].append({"title": j["title"], "ats_url": f"{ATS}/jobs/{u}",
                              "reason": "ATS page did not answer — left open, will retry tomorrow"})
        time.sleep(DETAIL_DELAY)

    if len(to_close) > MAX_CLOSES_PER_RUN:
        r["notes"].append(f"{len(to_close)} jobs look closed — more than the safety limit of "
                          f"{MAX_CLOSES_PER_RUN}/day, so none were closed. Please check manually.")
        r["held"] += [{"title": j["title"], "ats_url": f"{ATS}/jobs/{job_uuid(j)}",
                       "reason": "closed on ATS, held by safety limit"} for j in to_close]
        to_close = []

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    for j in to_close:
        r["closed"].append({"title": j["title"], "url": site_url(j["slug"]), "city": j.get("location", "")})
        if not dry:
            j["status"] = "closed"
            j["lastmod"] = today
            set_page_valid_through(j["slug"], f"{yesterday}T23:59:59")

    # 3. Reopen / new
    new_uuids = [u for u in ats if u not in open_jobs]
    new_jobs = []
    log(f"\n[3] {len(new_uuids)} ATS job(s) not open on the website")
    for u in new_uuids:
        prev = all_by_uuid.get(u)
        if prev and page_files(prev["slug"]):
            log(f"  reopen: {prev['title']} ({prev['slug']})")
            r["reopened"].append({"title": prev["title"], "url": site_url(prev["slug"]),
                                  "city": prev.get("location", "")})
            if not dry:
                prev.pop("status", None)
                prev["valid_through"] = OPEN_VALID_THROUGH
                prev["lastmod"] = today
                set_page_valid_through(prev["slug"], OPEN_VALID_THROUGH)
        else:
            log(f"  new: {ats[u]['title']} ({ats[u]['city']})")
            new_jobs.append(dict(ats[u], ats_url=f"{ATS}/jobs/{u}"))

    if not dry and (r["closed"] or r["reopened"]):
        save_registry(registry)
        subprocess.run([sys.executable, str(ROOT / "tools" / "update_jobs_listing.py")], cwd=str(ROOT))

    # 4. New jobs via the skill
    if new_jobs and create:
        batch, overflow = new_jobs[:MAX_CREATES_PER_RUN], new_jobs[MAX_CREATES_PER_RUN:]
        created, failed = create_new_jobs(batch, REPORT_DIR / f"claude-{today}.log")
        r["created"] += created
        r["failed"] += failed
        r["held"] += [dict(j, reason="queued for tomorrow (daily creation limit)") for j in overflow]
    elif new_jobs:
        r["held"] += [dict(j, reason="new job — not created (report-only run)") for j in new_jobs]

    # 5. Recount, commit, push
    r["site_open_after"] = sum(1 for j in load_registry() if is_open(j))
    if r["site_open_after"] != r["ats_advertised"] and r["ats_advertised"]:
        r["notes"].append(f"Website shows {r['site_open_after']} open jobs vs {r['ats_advertised']} on the "
                          f"careers page — see 'Needs your attention' above.")

    subject, html_body, md = build_report(r)
    (REPORT_DIR / f"{today}.md").write_text(md, encoding="utf-8")
    (REPORT_DIR / f"{today}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    (REPORT_DIR / f"{today}.html").write_text(html_body, encoding="utf-8")

    if not dry and (r["closed"] or r["reopened"] or r["created"]):
        parts = [f"{len(r[k])} {label}" for k, label in
                 (("created", "added"), ("reopened", "reopened"), ("closed", "closed")) if r[k]]
        r["git"] = git_commit_push(f"[Daily Sync] {', '.join(parts)} — {r['site_open_after']} open "
                                   f"(ATS {r['ats_advertised']})", push, TOUCHED)
        subject, html_body, md = build_report(r)
        (REPORT_DIR / f"{today}.md").write_text(md, encoding="utf-8")
        (REPORT_DIR / f"{today}.html").write_text(html_body, encoding="utf-8")
    # A second run on the same day keeps the first run's changes in the report.
    first = REPORT_DIR / f"{today}-first.json"
    if not r["dry_run"]:
        if first.exists():
            prev = json.loads(first.read_text(encoding="utf-8"))
            for k in ("created", "reopened", "closed"):
                r[k] = prev[k] + r[k]
            r["site_open_before"] = prev["site_open_before"]
            subject, html_body, md = build_report(r)
            (REPORT_DIR / f"{today}.md").write_text(md, encoding="utf-8")
            (REPORT_DIR / f"{today}.html").write_text(html_body, encoding="utf-8")
        else:
            first.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    log("\n" + md)

    # 6. Email
    if email:
        if send_at:
            wait_until(send_at)
        log("  " + send_email(subject, html_body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
