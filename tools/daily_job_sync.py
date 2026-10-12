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
     /jobs/<uuid> returns 404. Unseen-but-still-200 jobs stay open.
  3. Build a fact sheet for every open ATS job (tools/ats_facts.py →
     tools/ats_snapshots/<uuid>.json): city, type, dates, salary, work mode,
     languages, experience, description. Nothing on a page is guessed.
  4. REOPEN registry jobs (closed/expired) whose UUID is open again.
     CREATE pages for brand-new jobs with the /job-seo-generator skill (headless
     `claude -p`), working from the fact sheet. Address = title, or title-city
     when the title is taken.
     UPDATE pages whose title / city / salary / type / description changed
     since yesterday's fact sheet.
  5. Every created or updated page must pass tools/verify_job_page.py (schema,
     salary, apply link, template leftovers, private data, FAQ, Chrome render).
     Failures are rolled back and listed under "Needs your attention".
  6. Rebuild /jobs, sitemaps, hubs, similar-jobs carousels and the /jobs ItemList
     (update_jobs_listing.py + sync_job_listings.py); commit + push; notify Google.
  7. ~10 min after the push, check the live site (open count, new/closed pages).
  8. Email the report (held until --send-at HH:MM). A crash emails an alert instead.

Usage:
  python3 tools/daily_job_sync.py                  # full run
  python3 tools/daily_job_sync.py --dry-run        # compare + report only, change nothing
  python3 tools/daily_job_sync.py --no-create      # no Claude page building/updating
  python3 tools/daily_job_sync.py --no-push --no-email --no-live-check
  python3 tools/daily_job_sync.py --send-at 09:00  # hold the email until 09:00
  python3 tools/daily_job_sync.py --resend         # email today's saved report again
"""
from __future__ import annotations

import fcntl
import html as htmllib
import json
import re
import shutil
import smtplib
import ssl
import subprocess
import sys
import time
import traceback
import unicodedata
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
CONFIG_PATH = ROOT / "tools" / "sync_config.json"
REPORT_DIR = ROOT / "reports" / "daily-sync"
REJECTED_DIR = REPORT_DIR / "rejected"
LOCK_PATH = ROOT / "tools" / ".daily_job_sync.lock"
RUNNER = "cloud" if __import__("os").environ.get("DAILY_SYNC_RUNNER") == "cloud" else "mac"

ATS = "https://outreach-recruitment-agency.careers-page.com"
SITE = "https://outreachrecruitment.net"
REPORT_RECIPIENT = "sbarakat@outreachrecruitment.net"

LIST_DELAY = 6           # seconds between ATS listing requests
DETAIL_DELAY = 4         # seconds between ATS /jobs/<uuid> requests
MAX_CLOSES_PER_RUN = 25  # safety brake: more than this in one day = something is wrong
MAX_CREATES_PER_RUN = 10
MAX_UPDATES_PER_RUN = 10
MAX_AUDIT_FIXES_PER_RUN = 5   # existing pages repaired per day by the daily page check
AUDIT_MAX_ATTEMPTS = 2        # after this many failed repairs a page is flagged once and left alone
AUDIT_STATE_PATH = ROOT / "tools" / "page_audit.json"
OPEN_VALID_THROUGH = "2029-12-30"
CLAUDE_TIMEOUT = 75 * 60
LIVE_FIRST_WAIT = 10 * 60
LIVE_MAX_WAIT = 25 * 60

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
# HTTP + ATS scraping
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
        except (URLError, OSError):
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
        notes.append(f"The careers page advertises {advertised} jobs but {len(found)} unique jobs were "
                     f"collected (its listing pages are not always consistent).")
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
# Registry + page helpers
# ─────────────────────────────────────────────────────────────────────────────

TOUCHED: set[str] = set()


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
    # Older jobs keep only a redirect stub at <slug>; the page itself lives at the stub's target.
    from verify_job_page import real_slug
    slug = real_slug(slug)
    return [p for p in (ROOT / "jobs" / slug / "index.html", ROOT / "jobs" / f"{slug}.html") if p.exists()]


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def set_page_valid_through(slug: str, value: str) -> None:
    for path in page_files(slug):
        TOUCHED.add(rel(path))
        text = path.read_text(encoding="utf-8")
        new = re.sub(r'("validThrough"\s*:\s*)"[^"]*"', rf'\1"{value}"', text)
        if new != text:
            path.write_text(new, encoding="utf-8")


def site_url(slug: str) -> str:
    return f"{SITE}/jobs/{slug}/"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.replace("&", " and ")).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def choose_slug(title: str, city: str, taken: set[str]) -> str:
    """Title first; when that address is taken, title-city (housekeeper-rabat), then -2, -3 …"""
    base = slugify(title)
    if base not in taken:
        return base
    c = slugify(city)
    cand = f"{base}-{c}" if c and not base.endswith(c) else base
    slug, n = cand, 2
    while slug in taken:
        slug, n = f"{cand}-{n}", n + 1
    return slug


def taken_slugs(registry: list[dict]) -> set[str]:
    taken = {j["slug"] for j in registry}
    taken |= {p.name for p in (ROOT / "jobs").iterdir() if p.is_dir()}
    taken |= {p.stem for p in (ROOT / "jobs").glob("*.html")}
    return taken


def page_salary(slug: str) -> str:
    """The salary currently in a page's JobPosting schema (the owner's figure), as 'min–max'."""
    for path in page_files(slug):
        m = re.search(r'"baseSalary"\s*:\s*\{.*?"minValue"\s*:\s*([\d.]+).*?"maxValue"\s*:\s*([\d.]+)',
                      path.read_text(encoding="utf-8"), re.S)
        if m:
            return f"{m.group(1)}–{m.group(2)}"
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Headless Claude: create / update pages with the job-seo-generator skill
# ─────────────────────────────────────────────────────────────────────────────

def claude_bin() -> str | None:
    return shutil.which("claude") or next(
        (p for p in (str(Path.home() / ".local/bin/claude"), "/opt/homebrew/bin/claude",
                     "/usr/local/bin/claude") if Path(p).exists()), None)


COMMON_RULES = f"""Rules for every page (the sync script checks all of these with tools/verify_job_page.py
and rolls the page back if any fails):
- Work ONLY from the fact sheet tools/ats_snapshots/<uuid>.json (it was read from the careers page
  minutes ago). Do not guess city, type, salary, languages or experience.
- Salary: if the fact sheet has a salary, show exactly that amount and unit (header chip, sidebar,
  offer list, FAQ, meta description) and put the same min/max in JobPosting baseSalary. If it has
  none, write "Competitive salary" and put NO baseSalary in the schema. Never write "gross" unless
  the source says so.
- Defaults (project memory feedback_job_skill_defaults): On-site unless the fact sheet says
  Hybrid/Remote, Apply online, English. Reference number and deadline stay PRIVATE: validThrough
  {OPEN_VALID_THROUGH} in the schema + registry only, never in visible text; the reference only in an
  HTML comment.
- FAQ: closed by default; FAQPage schema questions must equal the visible FAQ questions.
- The apply link MUST be the fact sheet's apply_url. No other careers-page job link on the page.
- No text left over from the template page you cloned (old title, city, slug, uuid, salary).
- Write the page to jobs/<slug>/index.html AND jobs/<slug>.html (identical).
- Do NOT git commit or push. Do NOT close, expire or edit any other job.
"""


def run_claude(prompt: str, log_path: Path) -> None:
    exe = claude_bin()
    if not exe:
        log_path.write_text("claude CLI not found — page building skipped", encoding="utf-8")
        return
    try:
        result = subprocess.run(
            [exe, "-p", prompt, "--dangerously-skip-permissions", "--max-turns", "400",
             "--output-format", "text"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=CLAUDE_TIMEOUT,
        )
        log_path.write_text(result.stdout + "\n--- stderr ---\n" + result.stderr, encoding="utf-8")
    except subprocess.TimeoutExpired:
        log_path.write_text("Claude run timed out", encoding="utf-8")


def create_prompt(jobs: list[dict]) -> str:
    lines = "\n".join(
        f"- {j['title']} — slug: {j['slug']} — fact sheet: tools/ats_snapshots/{j['uuid']}.json"
        f" — salary to show: {j['salary_label']}" for j in jobs)
    return f"""You are the unattended daily job-sync agent for this repo (Outreach Recruitment).
These jobs are OPEN on the careers page but have no page on outreachrecruitment.net yet:

{lines}

For EACH job run the /job-seo-generator skill exactly as specified in
"Jobs Skills/job-seo-generator/SKILL.md" (+ references/) and publish it:
1. Read the fact sheet. Use the slug given above exactly (do not invent another).
2. Build the page by cloning a current rich job page (jobs/head-chef-in-gozo/index.html or
   jobs/client-accountant/index.html — NOT jobs/plumber / add_jobs_from_csv.py) and regenerate every
   job-specific part: head/meta, all JSON-LD blocks, header chips, sidebar, body sections, FAQ,
   similar jobs (open jobs only), share links, apply panel/iframe, JOB_REF.
3. Add the job to tools/jobs_registry.json (slug as given, no "status" key, valid_through
   {OPEN_VALID_THROUGH}, apply_url from the fact sheet, salary only if the fact sheet has one,
   and a real "category" — one of: Construction, Customer Service, Engineering & Maintenance,
   Finance & Accounting, Hospitality, Insurance, IT & Technology, Manufacturing, Marine & Shipping,
   Retail, Sales, Logistics, Administration, HR & Recruitment, Healthcare, Wellness. Never "General").
   Use the same category on the page (header chip, sidebar, schema industry/occupationalCategory).
4. Save the 12-section package to reports/job-seo-<slug>-{date.today().isoformat()}.md.

{COMMON_RULES}
If a job cannot be built properly, skip it and say why.
End with one line per job: CREATED <uuid> <slug>  or  SKIPPED <uuid> <reason>.
"""


def update_prompt(jobs: list[dict]) -> str:
    lines = "\n".join(
        f"- {j['title']} — page: jobs/{j['slug']}/ — fact sheet: tools/ats_snapshots/{j['uuid']}.json — "
        f"{'TO FIX (daily page check)' if j.get('audit') else 'changed'}: {'; '.join(j['changes'])}"
        + (f" — KEEP the owner's salary {j['owner_salary']} (the careers page gives none)"
           if j.get("owner_salary") else "")
        for j in jobs)
    return f"""You are the unattended daily job-sync agent for this repo (Outreach Recruitment).
These OPEN job pages need updating — either the job changed on the careers page since yesterday,
or the daily page check found something on the page that does not match the careers page /
the publishing rules ("TO FIX"):

{lines}

For EACH job, update its existing page (both jobs/<slug>/index.html and jobs/<slug>.html when
present) and its tools/jobs_registry.json entry so they match the new fact sheet, following the
/job-seo-generator skill ("Jobs Skills/job-seo-generator/SKILL.md"). Change only what the change
affects (e.g. a new salary → header chip, sidebar, offer list, FAQ answer, meta description and
baseSalary; a new city → location everywhere incl. schema and meta; new description → body
sections, FAQ, schema description). Keep the slug / URL unchanged.

{COMMON_RULES}
End with one line per job: UPDATED <uuid> <slug>  or  SKIPPED <uuid> <reason>.
"""


def reject_new_page(slug: str) -> None:
    """Move a failed new page out of the site (kept for review, never published)."""
    dest = REJECTED_DIR / date.today().isoformat() / slug
    dest.mkdir(parents=True, exist_ok=True)
    for p in page_files(slug):
        shutil.move(str(p), str(dest / ("index.html" if p.name == "index.html" else p.name)))
    folder = ROOT / "jobs" / slug
    if folder.is_dir() and not any(folder.iterdir()):
        folder.rmdir()


def create_new_jobs(new_jobs: list[dict], facts: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    from verify_job_page import verify
    log(f"  /job-seo-generator (headless Claude): creating {len(new_jobs)} job(s) …")
    run_claude(create_prompt(new_jobs), REPORT_DIR / f"claude-create-{date.today().isoformat()}.log")

    registry = load_registry()
    created, failed = [], []
    for j in new_jobs:
        reg = next((x for x in registry if job_uuid(x) == j["uuid"] and is_open(x)), None)
        if not reg:
            failed.append(dict(j, reason="the page was not built (not added to the registry)"))
            if page_files(j["slug"]):
                reject_new_page(j["slug"])
            continue
        problems = verify(reg, facts.get(j["uuid"]))
        if problems:
            registry.remove(reg)
            reject_new_page(reg["slug"])
            failed.append(dict(j, slug=reg["slug"],
                               reason="failed the pre-publish check: " + "; ".join(problems[:4])))
            log(f"    ✗ {j['title']}: {problems}")
        else:
            sheet = facts.get(j["uuid"]) or {}
            if sheet.get("salary") and not reg.get("salary"):  # so the /jobs card shows it too
                reg["salary"] = j["salary_label"]
            TOUCHED.update(rel(p) for p in page_files(reg["slug"]))
            TOUCHED.update(rel(p) for p in (ROOT / "reports").glob(f"job-seo-{reg['slug']}-*.md"))
            created.append(dict(j, slug=reg["slug"], url=site_url(reg["slug"])))
            log(f"    ✓ {j['title']} → {reg['slug']}")
    save_registry(registry)
    return created, failed


def update_jobs(changed: list[dict], facts: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    from verify_job_page import verify
    log(f"  /job-seo-generator (headless Claude): updating {len(changed)} changed job(s) …")
    backup_pages = {rel(p): p.read_text(encoding="utf-8") for j in changed for p in page_files(j["slug"])}
    backup_entries = {j["uuid"]: json.dumps(next(x for x in load_registry() if job_uuid(x) == j["uuid"]))
                      for j in changed}
    run_claude(update_prompt(changed), REPORT_DIR / f"claude-update-{date.today().isoformat()}.log")

    registry = load_registry()
    updated, failed = [], []
    for j in changed:
        idx = next((i for i, x in enumerate(registry) if job_uuid(x) == j["uuid"]), None)
        reg = registry[idx] if idx is not None else json.loads(backup_entries[j["uuid"]])
        problems = verify(dict(reg, owner_salary=j.get("owner_salary", "")), facts.get(j["uuid"]))
        if problems:
            # Roll back: the page keeps yesterday's (still valid) content.
            for path_s, text in backup_pages.items():
                if path_s.startswith(f"jobs/{j['slug']}"):
                    (ROOT / path_s).write_text(text, encoding="utf-8")
            if idx is not None:
                registry[idx] = json.loads(backup_entries[j["uuid"]])
            failed.append(dict(j, reason="update failed the pre-publish check, page left as it was: "
                                         + "; ".join(problems[:4])))
            log(f"    ✗ {j['title']}: {problems}")
        else:
            TOUCHED.update(rel(p) for p in page_files(j["slug"]))
            updated.append(dict(j, url=site_url(j["slug"])))
            log(f"    ✓ {j['title']}")
    save_registry(registry)
    return updated, failed


# ─────────────────────────────────────────────────────────────────────────────
# Git
# ─────────────────────────────────────────────────────────────────────────────

def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True)


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
                 "sitemap_index.xml", "sitemap.xml", "construction-jobs-in-malta.html", "tools/ats_snapshots",
                 "reports/google_indexing_history.csv", "tools/page_audit.json", "tools/rich_results.json",
                 "tools/job_redirects.json"]


def git_commit_push(message: str, push: bool) -> tuple[str, bool]:
    # Stage only what this run touched — never sweep in other people's uncommitted edits.
    today = date.today().isoformat()
    paths = set(LISTING_FILES) | TOUCHED | {rel(p) for p in REPORT_DIR.glob(f"*{today}*") if p.is_file()}
    git("add", "--", *sorted(p for p in paths if (ROOT / p).exists()))
    if not git("diff", "--cached", "--quiet").returncode:
        return "nothing to commit", False
    commit = git("commit", "-m", message + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    if commit.returncode != 0:
        return f"commit failed: {commit.stderr.strip()[:200]}", False
    if not push:
        return "committed (push skipped)", False
    for _ in range(3):
        git("fetch", "origin", "main")
        if git("merge", "--no-edit", "origin/main").returncode != 0:
            git("merge", "--abort")
            return "committed locally — merge with origin/main had conflicts, NOT pushed", False
        if git("push", "origin", "main").returncode == 0:
            return "pushed to GitHub (main)", True
        time.sleep(20)
    return "committed locally — push failed 3 times", False


# ─────────────────────────────────────────────────────────────────────────────
# Google + live site
# ─────────────────────────────────────────────────────────────────────────────

def notify_google(r: dict) -> dict:
    """URL_UPDATED for every page whose job status/content changed (closed pages carry an
    expired validThrough, so a recrawl drops them from Google for Jobs)."""
    rows = [{"title": j["title"], "slug": j.get("slug", ""), "url": j["url"], "type": "URL_UPDATED",
             "source": f"daily_sync_{kind}"}
            for kind in ("created", "reopened", "updated", "closed") for j in r[kind] if j.get("url")]
    if not rows:
        return {"sent": 0, "ok": 0}
    try:
        from job_sync_agent import submit_google_indexing
        res = submit_google_indexing(rows)
    except Exception as e:
        return {"sent": len(rows), "ok": 0, "error": str(e)[:200]}
    ok = sum(1 for x in res if x.get("ok"))
    err = next((str(x.get("response"))[:160] for x in res if not x.get("ok")), "")
    return {"sent": len(rows), "ok": ok, "error": err, "sitemap": submit_sitemap()}


def submit_sitemap() -> str:
    """Resubmit the jobs sitemap in Search Console so Google re-reads the job list."""
    try:
        from google.auth.transport.requests import Request as GoogleRequest
        from google.oauth2 import service_account
        from job_sync_agent import google_credentials_path
        creds = service_account.Credentials.from_service_account_file(
            str(google_credentials_path()), scopes=["https://www.googleapis.com/auth/webmasters"])
        creds.refresh(GoogleRequest())
        url = (f"https://www.googleapis.com/webmasters/v3/sites/{quote(SITE + '/', safe='')}/sitemaps/"
               f"{quote(SITE + '/sitemaps/sitemap-jobs.xml', safe='')}")
        with urlopen(Request(url, method="PUT", headers={"Authorization": f"Bearer {creds.token}"}), timeout=30) as resp:
            return "submitted" if resp.status in (200, 204) else f"HTTP {resp.status}"
    except Exception as e:
        return f"not submitted ({str(e)[:80]})"


def live_open_count() -> int | None:
    status, body = fetch(f"{SITE}/jobs/?sync={int(time.time())}", retries=3)
    m = re.search(r"\+(\d+)\s+Open Positions", body) if status == 200 else None
    return int(m.group(1)) if m else None


def live_check(r: dict, pushed: bool) -> dict:
    expected = r["site_open_after"]
    if pushed:
        log(f"  waiting {LIVE_FIRST_WAIT // 60} min for GitHub Pages to deploy …")
        time.sleep(LIVE_FIRST_WAIT)
    deadline = time.time() + (LIVE_MAX_WAIT - LIVE_FIRST_WAIT if pushed else 0)
    count = live_open_count()
    while count != expected and time.time() < deadline:
        time.sleep(60)
        count = live_open_count()
    problems = []
    for j in r["created"] + r["reopened"] + r["updated"]:
        status, body = fetch(j["url"] + f"?sync={int(time.time())}", retries=3)
        if status != 200:
            problems.append(f"{j['title']}: live page answers HTTP {status}")
        elif j.get("uuid") and j["uuid"] not in body:
            problems.append(f"{j['title']}: live page is not the new version yet")
    today = date.today().isoformat()
    for j in r["closed"]:
        status, body = fetch(j["url"] + f"?sync={int(time.time())}", retries=3)
        m = re.search(r'"validThrough"\s*:\s*"([^"]+)"', body)
        if status == 200 and (not m or m.group(1)[:10] >= today):
            problems.append(f"{j['title']}: live page still looks open")
    return {"count": count, "expected": expected, "ok": count == expected and not problems,
            "problems": problems}


# ─────────────────────────────────────────────────────────────────────────────
# Report + email
# ─────────────────────────────────────────────────────────────────────────────

def esc(s: object) -> str:
    return htmllib.escape(str(s))


def job_list_html(rows: list[dict], empty: str, link_key: str = "url", extra: str = "") -> str:
    if not rows:
        return f'<p style="color:#666;margin:4px 0 12px">{empty}</p>'
    items = []
    for r in rows:
        link = r.get(link_key) or r.get("ats_url")
        label = f'<a href="{esc(link)}">{esc(r.get("title", ""))}</a>' if link else esc(r.get("title", ""))
        city = f' <span style="color:#777">— {esc(r["city"])}</span>' if r.get("city") else ""
        sal = f' <span style="color:#555">· {esc(r["salary_label"])}</span>' if r.get("salary_label") else ""
        why = (f'<br><span style="color:#b45309;font-size:13px">{esc(r[extra] if isinstance(r[extra], str) else "; ".join(r[extra]))}</span>'
               if extra and r.get(extra) else "")
        items.append(f'<li style="margin-bottom:4px">{label}{city}{sal}{why}</li>')
    return '<ul style="margin:4px 0 12px;padding-left:20px">' + "".join(items) + "</ul>"


def live_line(r: dict) -> tuple[str, str]:
    lv = r.get("live")
    if not lv:
        return "", ""
    if lv["ok"]:
        return f"Live site: {lv['count']} ✅", "#15803d"
    shown = lv["count"] if lv["count"] is not None else "?"
    return (f"Live site shows {shown}, expected {lv['expected']} ⚠️ — GitHub Pages may still be "
            f"deploying; if it is still wrong later today, the deploy failed and needs a look."), "#b45309"


def build_report(r: dict) -> tuple[str, str, str]:
    in_sync = r["site_open_after"] == r["ats_advertised"]
    badge = "✅ In sync" if in_sync else "⚠️ Not in sync"
    if r.get("dry_run"):
        badge += " (report only — nothing was changed; lists show what WOULD happen)"
    opened = len(r["created"]) + len(r["reopened"])
    subject = (f"Job sync {r['date']}: {badge.split(' (')[0]} — careers page {r['ats_advertised']} / website "
               f"{r['site_open_after']} (+{opened} opened, -{len(r['closed'])} closed"
               + (f", {len(r['updated'])} updated" if r["updated"] else "") + ")")
    color = "#15803d" if in_sync else "#b45309"
    stat = lambda n, label: (f'<td style="padding:10px 14px;border:1px solid #e5e7eb;text-align:center">'
                             f'<div style="font-size:24px;font-weight:700">{esc(n)}</div>'
                             f'<div style="font-size:12px;color:#555">{label}</div></td>')
    live_txt, live_color = live_line(r)
    attention = r["failed"] + r["held"]
    ls = r.get("listings") or {}
    hub_rep = sum(v.get("replaced", 0) for v in ls.get("hub_cards", {}).values())
    hub_rem = sum(v.get("removed", 0) for v in ls.get("hub_cards", {}).values())
    housekeeping = []
    if hub_rep or hub_rem:
        housekeeping.append(f"Hub/homepage cards for closed jobs: {hub_rep} replaced with open jobs, {hub_rem} removed")
    if ls.get("carousel_swaps"):
        housekeeping.append(f"'Similar jobs' links to closed jobs replaced: {ls['carousel_swaps']}")
    if ls.get("itemlist_items"):
        housekeeping.append(f"Google job list on /jobs (ItemList) rebuilt: {ls['itemlist_items']} open jobs")
    g = r.get("google") or {}
    if g.get("sent"):
        housekeeping.append(f"Google notified about {g['ok']}/{g['sent']} changed page(s)"
                            + (f" — error: {g['error']}" if g.get("error") and g["ok"] < g["sent"] else "")
                            + (f"; jobs sitemap {g['sitemap']}" if g.get("sitemap") else ""))
    if ls.get("pages_marked_closed") or ls.get("pages_reopened"):
        housekeeping.append(f"Job pages switched to 'Position Closed' (apply disabled): {ls.get('pages_marked_closed', 0)}"
                            f"; closed look removed from reopened pages: {ls.get('pages_reopened', 0)}")
    if ls.get("categorised"):
        housekeeping.append("Category set automatically: " + ", ".join(
            f"{c['title']} → {c['to']}" for c in ls["categorised"][:12])
            + (f" (+{len(ls['categorised']) - 12} more)" if len(ls["categorised"]) > 12 else ""))
    gc = r.get("google_check") or {}
    google_html = ""
    if gc.get("checked") or gc.get("error"):
        google_html = (f'<h3 style="margin:14px 0 4px">🔎 Google check — new jobs, 2+ days after publishing</h3>'
                       f'<p style="margin:4px 0;color:#444">{len(gc.get("ok", []))} of {gc.get("checked", 0)} checked '
                       f'are indexed and showing in Google Jobs ✅</p>'
                       + (job_list_html(gc["flagged"], "", extra="reason") if gc.get("flagged") else "")
                       + (f'<p style="color:#b45309">{esc(gc["error"])}</p>' if gc.get("error") else ""))
    sc = r.get("salary_coverage") or {}
    if sc.get("open"):
        housekeeping.insert(0, f"Salary shown on {sc['with_salary']} of {sc['open']} open jobs "
                               f"({round(100 * sc['with_salary'] / sc['open'])}%) — all salaries come from the careers page")
    if r.get("salary_synced"):
        housekeeping.append("Salary updated from the careers page: " + "; ".join(r["salary_synced"][:10])
                            + (f" (+{len(r['salary_synced']) - 10} more)" if len(r["salary_synced"]) > 10 else ""))
    if ls.get("merged"):
        housekeeping.append("Duplicate entries merged (old address now redirects): " + ", ".join(
            f"{', '.join(m['dropped'])} → {m['keep']}" for m in ls["merged"]))
    try:
        rr = json.loads((ROOT / "tools" / "rich_results.json").read_text(encoding="utf-8"))
        if (date.fromisoformat(r["date"]) - date.fromisoformat(rr["last_run"])).days <= 1:
            sm = rr.get("summary", {})
            bad = [s_ for s_, p_ in rr.get("pages", {}).items() if p_.get("indexed") and (not p_.get("job_posting") or p_.get("errors"))]
            housekeeping.insert(0, f"Monthly Google check: {sm.get('job_posting_ok', 0)} of {sm.get('checked', 0)} job pages show in "
                                   f"Google Jobs with no errors; {len(bad)} queued for repair"
                                   + (f"; {sm.get('not_indexed')} not indexed yet" if sm.get("not_indexed") else ""))
    except Exception:
        pass
    pc = r.get("page_check") or {}
    if pc.get("open_checked"):
        housekeeping.insert(0, f"Daily page check: {pc['ok']} of {pc['open_checked']} open job pages pass every check"
                               + (f"; repairing {pc['fixing_today']} today" if pc.get("fixing_today") else "")
                               + (f", {pc['queued']} queued for the next days" if pc.get("queued") else ""))
    notes = r["notes"] + r.get("salary_notes", [])
    li = lambda xs: "".join(f"<li>{esc(x)}</li>" for x in xs)
    html = f"""<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;max-width:720px;color:#111">
<h2 style="margin:0 0 4px">Daily Job Sync — {esc(r['date'])}</h2>
<p style="margin:0 0 6px;color:{color};font-weight:700">{esc(badge)}</p>
{f'<p style="margin:0 0 14px;color:{live_color};font-weight:600">{esc(live_txt)}</p>' if live_txt else ''}
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
<h3 style="margin:14px 0 4px">✏️ Updated ({len(r['updated'])})</h3>
{job_list_html(r['updated'], 'No job changed on the careers page.', extra='changes')}
<h3 style="margin:14px 0 4px">⚠️ Needs your attention ({len(attention)})</h3>
{job_list_html(attention, 'Nothing.', extra='reason')}
{google_html}
{f'<h3 style="margin:14px 0 4px">Notes</h3><ul style="padding-left:20px">{li(notes)}</ul>' if notes else ''}
{f'<h3 style="margin:14px 0 4px">Site housekeeping</h3><ul style="padding-left:20px;color:#444">{li(housekeeping)}</ul>' if housekeeping else ''}
<p style="color:#555;font-size:13px;margin-top:18px">Git: {esc(r['git'])}.<br>
Careers page: <a href="{ATS}/">{ATS}</a> · Website: <a href="{SITE}/jobs/">{SITE}/jobs/</a></p>
</div>"""
    md = [f"# Daily Job Sync — {r['date']}", "", f"**{badge}** — careers page {r['ats_advertised']}, "
          f"website {r['site_open_before']} → {r['site_open_after']}", ""]
    if live_txt:
        md += [live_txt, ""]
    for key, label in (("created", "New jobs published"), ("reopened", "Reopened"), ("closed", "Closed"),
                       ("updated", "Updated"), ("failed", "Failed"), ("held", "Held back")):
        md.append(f"## {label} ({len(r[key])})")
        md += [f"- {j.get('title')} — {j.get('url') or j.get('ats_url', '')}"
               + (f" ({j['reason']})" if j.get("reason") else "")
               + (f" ({'; '.join(j['changes'])})" if j.get("changes") else "") for j in r[key]] or ["- none"]
        md.append("")
    if notes:
        md += ["## Notes"] + [f"- {n}" for n in notes] + [""]
    if gc.get("checked"):
        md += [f"## Google check ({len(gc.get('ok', []))}/{gc['checked']} indexed + in Google Jobs)"]
        md += [f"- {x['title']} — {x['reason']}" for x in gc.get("flagged", [])] + [""]
    if housekeeping:
        md += ["## Site housekeeping"] + [f"- {h}" for h in housekeeping] + [""]
    md.append(f"Git: {r['git']}")
    return subject, html, "\n".join(md) + "\n"


def smtp_config() -> dict | None:
    """tools/sync_config.json on the Mac; SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS env vars in the cloud."""
    import os
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception:
        pass
    if os.environ.get("SMTP_PASS"):
        return {"smtp_host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
                "smtp_port": os.environ.get("SMTP_PORT", "587"),
                "smtp_user": os.environ.get("SMTP_USER", REPORT_RECIPIENT),
                "smtp_pass": os.environ["SMTP_PASS"]}
    return None


def send_email(subject: str, html_body: str) -> str:
    cfg = smtp_config()
    if not cfg:
        return "email skipped — no tools/sync_config.json and no SMTP_PASS environment variable"
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, cfg["smtp_user"], REPORT_RECIPIENT
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    err = ""
    for _ in range(3):
        try:
            with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"]), timeout=60) as s:
                s.starttls(context=ssl.create_default_context())
                s.login(cfg["smtp_user"], cfg["smtp_pass"])
                s.sendmail(cfg["smtp_user"], [REPORT_RECIPIENT], msg.as_string())
            return f"email sent to {REPORT_RECIPIENT}"
        except Exception as e:  # network blips right after wake-up are common
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


def save_report_files(r: dict) -> tuple[str, str, str]:
    subject, html_body, md = build_report(r)
    today = r["date"] + ("-dryrun" if r.get("dry_run") else "")
    (REPORT_DIR / f"{today}.md").write_text(md, encoding="utf-8")
    (REPORT_DIR / f"{today}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    (REPORT_DIR / f"{today}.html").write_text(html_body, encoding="utf-8")
    return subject, html_body, md


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main(args: list[str]) -> int:
    from ats_facts import (changes_between, is_new_role, load_snapshot, parse_job_page, salary_label,
                           save_snapshot)
    import indexing_followup
    import sync_job_listings

    dry = "--dry-run" in args
    push = not dry and "--no-push" not in args
    email = not dry and "--no-email" not in args
    create = not dry and "--no-create" not in args
    do_live = "--no-live-check" not in args
    send_at = args[args.index("--send-at") + 1] if "--send-at" in args else None

    today = date.today().isoformat()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if "--resend" in args:
        r = json.loads((REPORT_DIR / f"{today}.json").read_text(encoding="utf-8"))
        subject, html_body, _ = build_report(r)
        log("  " + send_email(subject, html_body))
        return 0

    log(f"=== Daily job sync {datetime.now():%Y-%m-%d %H:%M} {'(DRY RUN)' if dry else ''} ===")
    r: dict = {"date": today, "created": [], "reopened": [], "closed": [], "updated": [], "failed": [],
               "held": [], "notes": [], "salary_notes": [], "git": "no changes", "dry_run": dry}

    if not dry:
        err = git_preflight()
        if err:
            r["notes"].append(f"Did not change anything: {err}.")
            dry, push, create = True, False, False
            r["dry_run"] = True
            log(f"  PREFLIGHT: {err} — running report-only")

    # Tell the cloud backup (09:30) that today's run has started, so it never runs alongside us.
    if not dry and push:
        marker = REPORT_DIR / f"{today}-started.txt"
        marker.write_text(f"{datetime.now().isoformat(timespec='seconds')} {RUNNER}\n", encoding="utf-8")
        git("add", "--", rel(marker))
        git("commit", "-m", f"[Daily Sync] run started {today} ({RUNNER})\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        git("push", "origin", "main")

    # 1. Careers page listing
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
    r["site_open_before"] = len([j for j in registry if is_open(j)])
    log(f"  careers page: {len(ats)} collected / {advertised} advertised · website open: {r['site_open_before']}")
    if not ats or not advertised:
        r["site_open_after"] = r["site_open_before"]
        dry, push, create = True, False, False
        r["dry_run"] = True

    # 2. Close — only on a confirmed ATS 404
    to_check = [u for u in open_jobs if u not in ats] if ats else []
    log(f"\n[2] {len(to_check)} website job(s) not in the careers-page listing — checking each …")
    to_close = []
    for u in to_check:
        live = ats_job_is_live(u)
        j = open_jobs[u]
        log(f"  {j['title']} ({u[:8]}) → {'OPEN' if live else 'CLOSED' if live is False else 'UNKNOWN'}")
        if live is False:
            to_close.append(j)
        elif live is None:
            r["held"].append({"title": j["title"], "ats_url": f"{ATS}/jobs/{u}",
                              "reason": "careers page did not answer — left open, will retry tomorrow"})
        time.sleep(DETAIL_DELAY)
    if len(to_close) > MAX_CLOSES_PER_RUN:
        r["notes"].append(f"{len(to_close)} jobs look closed — more than the safety limit of "
                          f"{MAX_CLOSES_PER_RUN}/day, so none were closed. Please check manually.")
        r["held"] += [{"title": j["title"], "ats_url": f"{ATS}/jobs/{job_uuid(j)}",
                       "reason": "closed on the careers page, held by the daily safety limit"} for j in to_close]
        to_close = []

    # 3. Fact sheets for every open careers-page job
    log(f"\n[3] Reading {len(ats)} job pages for fact sheets …")
    facts: dict[str, dict] = {}
    for i, u in enumerate(ats, 1):
        status, body = fetch(f"{ATS}/jobs/{u}")
        if status == 200:
            facts[u] = parse_job_page(u, body)
            facts[u]["title"] = facts[u]["title"] or ats[u]["title"]
            facts[u]["city"] = facts[u]["city"] or ats[u]["city"]
        if i % 20 == 0:
            log(f"  {i}/{len(ats)}")
        time.sleep(DETAIL_DELAY)
    log(f"  {len(facts)} fact sheets read")

    # 3b. The careers page is the source of every salary: keep the registry (→ /jobs cards,
    #     page check, Google data) in step with it. A salary the careers page does not give
    #     is the owner's and is left alone.
    r["salary_synced"] = []
    for u, job in open_jobs.items():
        sal = (facts.get(u) or {}).get("salary")
        if sal and sal.get("unit_corrected"):
            r["salary_notes"].append(f"{job['title']}: the careers page lists {salary_label(dict(sal, unit=sal['unit_corrected'].split('→')[0]))}"
                                     f" — shown as {salary_label(sal)}. Please correct the unit on the careers page.")
        if sal and job.get("salary") != salary_label(sal):
            r["salary_synced"].append(f"{job['title']}: {job.get('salary') or 'none'} → {salary_label(sal)}")
            if not dry:
                job["salary"] = salary_label(sal)
    with_salary = sum(1 for u, j in open_jobs.items() if (facts.get(u) or {}).get("salary") or j.get("salary"))
    r["salary_coverage"] = {"with_salary": with_salary, "open": len(open_jobs)}

    # 4. Reopen / new / changed
    taken = taken_slugs(registry)
    new_jobs, changed = [], []
    retitled: dict[str, dict] = {}  # uuid -> old registry job, for a same-ID job that became a new role
    for u in ats:
        f = facts.get(u, {})
        prev = all_by_uuid.get(u)
        if u in open_jobs:
            old = load_snapshot(u)
            diffs = changes_between(old, f) if old and f else []
            job = open_jobs[u]
            if diffs and is_new_role(old.get("title") or job["title"], f.get("title", "")):
                # Same careers-page ID, different job: close the old page, publish a new one.
                log(f"  new role on the same ID: '{old.get('title') or job['title']}' → '{f['title']}'")
                retitled[u] = job
                to_close.append(job)
                title, city = f["title"], f.get("city") or ats[u]["city"]
                slug = choose_slug(title, city, taken)
                taken.add(slug)
                new_jobs.append({"uuid": u, "title": title, "city": city, "slug": slug,
                                 "salary_label": salary_label(f.get("salary")), "ats_url": f"{ATS}/jobs/{u}",
                                 "replaces": job["title"]})
                continue
            if diffs:
                owner = "" if f.get("salary") else (job.get("salary") or page_salary(job["slug"]))
                changed.append({"uuid": u, "title": f.get("title") or job["title"], "slug": job["slug"],
                                "city": f.get("city", ""), "changes": diffs, "owner_salary": owner})
            continue
        if prev and page_files(prev["slug"]):
            log(f"  reopen: {prev['title']} ({prev['slug']})")
            r["reopened"].append({"title": prev["title"], "slug": prev["slug"], "uuid": u,
                                  "url": site_url(prev["slug"]), "city": prev.get("location", "")})
            if not dry:
                prev.pop("status", None)
                prev["valid_through"] = OPEN_VALID_THROUGH
                prev["lastmod"] = today
                set_page_valid_through(prev["slug"], OPEN_VALID_THROUGH)
            continue
        title, city = f.get("title") or ats[u]["title"], f.get("city") or ats[u]["city"]
        slug = choose_slug(title, city, taken)
        taken.add(slug)
        sal = salary_label(f.get("salary")) if f else "Competitive salary"
        log(f"  new: {title} ({city}) → {slug} · {sal}")
        new_jobs.append({"uuid": u, "title": title, "city": city, "slug": slug, "salary_label": sal,
                         "ats_url": f"{ATS}/jobs/{u}"})
        if f and not f.get("salary"):
            r["salary_notes"].append(f"{title}: no salary given on the careers page — page says 'Competitive salary'.")
        if not f:
            r["held"].append({"title": title, "ats_url": f"{ATS}/jobs/{u}",
                              "reason": "could not read the job's careers page — will retry tomorrow"})
    new_jobs = [j for j in new_jobs if j["uuid"] in facts]
    log(f"  {len(new_jobs)} new, {len(r['reopened'])} to reopen, {len(changed)} changed")

    # 4b. Daily page check: every open page vs its fact sheet and the publishing rules.
    #     Safe problems are repaired (via the same skill-driven update + pre-publish check);
    #     a salary on the page that the careers page does not give is the owner's and is kept.
    from verify_job_page import verify
    audit_state = {}
    try:
        audit_state = json.loads(AUDIT_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    busy = {c["uuid"] for c in changed} | {j["uuid"] for j in new_jobs} | set(retitled)
    audit_ok, audit_todo, audit_given_up = 0, [], []
    for u, job in open_jobs.items():
        f = facts.get(u)
        if not f or u in busy or job in to_close:
            continue
        owner = "" if f.get("salary") else (job.get("salary") or page_salary(job["slug"]))
        problems = verify(dict(job, owner_salary=owner), f, render=False)
        from verify_job_page import real_slug as _rs
        google = (audit_state.get(job["slug"]) or audit_state.get(_rs(job["slug"])) or {}).get("google_issues", [])
        problems += [g for g in google if g not in problems]
        if not problems:
            audit_ok += 1
            audit_state.pop(job["slug"], None)
            continue
        st = audit_state.setdefault(job["slug"], {"first_seen": today, "attempts": 0})
        st["problems"] = problems
        if st["attempts"] >= AUDIT_MAX_ATTEMPTS:
            audit_given_up.append(job)
            continue
        audit_todo.append({"uuid": u, "title": job["title"], "slug": job["slug"], "city": f.get("city", ""),
                           "changes": problems, "owner_salary": owner, "audit": True})
    def severity(item: dict) -> int:  # wrong apply link / salary first, cosmetic last
        text = " ".join(item["changes"]).lower()
        if "apply link" in text or "other ats job" in text or "google" in text:
            return 0
        if "does not match the careers page" in text or "is not shown on the page" in text:
            return 1
        if "competitive salary" in text and len(item["changes"]) == 1:
            return 3
        return 2
    audit_todo.sort(key=severity)
    audit_fix = audit_todo[:MAX_AUDIT_FIXES_PER_RUN] if create else []
    changed += audit_fix
    r["page_check"] = {"open_checked": audit_ok + len(audit_todo) + len(audit_given_up), "ok": audit_ok,
                       "to_fix": len(audit_todo), "fixing_today": len(audit_fix),
                       "queued": len(audit_todo) - len(audit_fix)}
    for job in audit_given_up:  # flagged once, then left for the owner
        st = audit_state[job["slug"]]
        if not st.get("flagged"):
            st["flagged"] = today
            r["held"].append({"title": job["title"], "url": site_url(job["slug"]),
                              "reason": "page check keeps failing after automatic repair attempts: "
                                        + "; ".join(st["problems"][:3])})
    log(f"  page check: {audit_ok} ok, {len(audit_todo)} to fix ({len(audit_fix)} today)")

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    for j in to_close:
        r["closed"].append({"title": j["title"], "slug": j["slug"], "url": site_url(j["slug"]),
                            "city": j.get("location", ""),
                            **({"reason": "replaced by a new role on the same careers-page ID"}
                               if job_uuid(j) in retitled else {})})
        if not dry:
            j["status"] = "closed"
            j["lastmod"] = today
            if job_uuid(j) in retitled:  # a different job now uses this ID — never merge the two
                j["replaced_by"] = next((n["slug"] for n in new_jobs if n["uuid"] == job_uuid(j)), "")
            set_page_valid_through(j["slug"], f"{yesterday}T23:59:59")
    if not dry:
        save_registry(registry)

    # Fact sheets the skill reads (saved before Claude runs). Changed-job sheets are saved
    # only after a successful update, so a failed update is retried tomorrow.
    changed_uuids = {c["uuid"] for c in changed}
    if not dry:
        for u, f in facts.items():
            if u not in changed_uuids:
                save_snapshot(f)

    # 5. Create / update with the skill, each page verified before it can go live
    if new_jobs and create:
        overflow: list[dict] = []
        batch, overflow = new_jobs[:MAX_CREATES_PER_RUN], new_jobs[MAX_CREATES_PER_RUN:]
        created, failed = create_new_jobs(batch, facts)
        for c in created:
            if c.get("replaces"):
                c["reason"] = f"new role — replaces '{c['replaces']}' (same careers-page ID)"
        r["created"] += created
        r["failed"] += failed
        # A same-ID role change whose new page failed: put the old page back so the job stays listed.
        failed_uuids = {j["uuid"] for j in failed + overflow}
        restore = [old for u, old in retitled.items() if u in failed_uuids]
        if restore:
            reg_now = load_registry()
            for old in restore:
                for x in reg_now:
                    if x["slug"] == old["slug"]:
                        x.pop("status", None)
                        x["lastmod"] = today
                set_page_valid_through(old["slug"], OPEN_VALID_THROUGH)
                r["closed"] = [c for c in r["closed"] if c["slug"] != old["slug"]]
                r["notes"].append(f"'{old['title']}' changed into a different job on the careers page, but the "
                                  f"new page could not be built — the old page stays open for now.")
            save_registry(reg_now)
        r["held"] += [dict(j, reason="queued for tomorrow (daily creation limit)") for j in overflow]
    elif new_jobs:
        r["held"] += [dict(j, reason="new job — not created (report-only run)") for j in new_jobs]

    if changed and create:
        batch, overflow = changed[:MAX_UPDATES_PER_RUN], changed[MAX_UPDATES_PER_RUN:]
        updated, failed = update_jobs(batch, facts)
        r["updated"] += updated
        r["failed"] += failed
        for j in updated:
            if j.get("audit"):
                j["changes"] = ["page repaired — " + c for c in j["changes"]]
        for j in updated:  # failed / queued changes keep yesterday's sheet and are retried tomorrow
            save_snapshot(facts[j["uuid"]])
            if j.get("audit"):
                audit_state.pop(j["slug"], None)  # incl. google_issues — next monthly check re-verifies
        for j in failed:
            if j.get("audit") and j["slug"] in audit_state:
                audit_state[j["slug"]]["attempts"] = audit_state[j["slug"]].get("attempts", 0) + 1
        r["held"] += [dict(j, reason="change queued for tomorrow (daily update limit)") for j in overflow]
    elif changed:
        r["updated"] = [dict(j, url=site_url(j["slug"])) for j in changed] if dry else []
        if not dry:
            r["held"] += [dict(j, reason="changed on the careers page — not updated (--no-create)") for j in changed]

    # 6. Listings everywhere
    if not dry:  # idempotent — also picks up registry edits made since the last run
        subprocess.run([sys.executable, str(ROOT / "tools" / "update_jobs_listing.py")], cwd=str(ROOT))
    if not dry:
        res = sync_job_listings.run()
        TOUCHED.update(res.pop("touched"))
        r["listings"] = res
    r["site_open_after"] = len([j for j in load_registry() if is_open(j)])
    if dry:
        r["site_open_after"] = r["site_open_before"] - len(r["closed"]) + len(r["reopened"]) + len(
            [j for j in r["held"] if j.get("reason", "").startswith("new job")])
    if r["site_open_after"] != r["ats_advertised"] and r["ats_advertised"]:
        r["notes"].append(f"Website shows {r['site_open_after']} open jobs vs {r['ats_advertised']} on the "
                          f"careers page — see 'Needs your attention'.")

    if not dry:
        AUDIT_STATE_PATH.write_text(json.dumps(audit_state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Same-day re-runs keep the earlier runs' changes in the report (merged before the report
    # is first saved, so an interrupted run cannot leave an empty report behind). Only this
    # run's own changes are committed and sent to Google.
    run_changes = {k: list(r[k]) for k in ("created", "reopened", "closed", "updated")}
    first = REPORT_DIR / f"{today}-first.json"
    if not r["dry_run"]:
        if first.exists():
            prev = json.loads(first.read_text(encoding="utf-8"))
            for k in run_changes:
                seen = {j.get("url") for j in r[k]}
                r[k] = [j for j in prev.get(k, []) if j.get("url") not in seen] + r[k]
            r["site_open_before"] = prev["site_open_before"]
        else:
            first.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")

    # 7. Commit + push, Google, live check
    pushed = False
    if not dry:
        parts = [f"{len(run_changes[k])} {label}" for k, label in
                 (("created", "added"), ("reopened", "reopened"), ("closed", "closed"), ("updated", "updated"))
                 if run_changes[k]]
        save_report_files(r)
        r["git"], pushed = git_commit_push(
            f"[Daily Sync] {', '.join(parts) or 'listings + fact sheets'} — {r['site_open_after']} open "
            f"(careers page {r['ats_advertised']})", push)
        if pushed:
            r["google"] = notify_google(dict(r, **run_changes))
    if do_live and not dry:
        log("\n[7] Checking the live site …")
        r["live"] = live_check(r, pushed)
        log(f"  live: {r['live']}")

    if not dry:
        log("\n[8] Google follow-up (jobs published 2+ days ago) …")
        try:
            r["google_check"] = indexing_followup.run()
        except Exception as e:
            r["google_check"] = {"checked": 0, "ok": [], "flagged": [], "error": str(e)[:200]}
        log(f"  checked {r['google_check']['checked']}, flagged {len(r['google_check']['flagged'])}")

    subject, html_body, md = save_report_files(r)
    if not dry and push:
        # Always publish the day's report: the cloud backup looks for it on GitHub to know
        # the Mac run happened.
        paths = [rel(p) for p in REPORT_DIR.glob(f"{today}*")] + ["tools/indexing_followup.json"]
        git("add", "--", *[p for p in paths if (ROOT / p).exists()])
        if git("diff", "--cached", "--quiet").returncode:
            git("commit", "-m", f"[Daily Sync] report {today}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        for _ in range(3):
            git("fetch", "origin", "main")
            if git("merge", "--no-edit", "origin/main").returncode != 0:
                git("merge", "--abort")
                break
            if git("push", "origin", "main").returncode == 0:
                break
            time.sleep(20)
    log("\n" + md)

    # 8. Email
    if email:
        if send_at:
            wait_until(send_at)
        log("  " + send_email(subject, html_body))

    # 9. Monthly Google rich-result check (after the email, it takes ~15 min). Problem pages
    #    go into tools/page_audit.json and are repaired by the following days' page checks.
    if not dry:
        import rich_results_check
        if rich_results_check.due():
            log("\n[9] Monthly Google rich-result check …")
            try:
                rr = rich_results_check.run()
                log(f"  checked {rr['checked']}, Job Posting OK {rr['job_posting_ok']}, problems {len(rr['problems'])}")
                git("add", "--", "tools/rich_results.json", "tools/page_audit.json")
                if git("diff", "--cached", "--quiet").returncode:
                    git("commit", "-m", f"[Daily Sync] monthly Google rich-result check {today}\n\n"
                                        "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
                    git("fetch", "origin", "main")
                    if git("merge", "--no-edit", "origin/main").returncode == 0:
                        git("push", "origin", "main")
                    else:
                        git("merge", "--abort")
            except Exception as e:
                log(f"  rich-result check failed: {e}")
    return 0


def alert(exc_text: str) -> None:
    body = (f'<div style="font-family:Arial,sans-serif"><h2 style="color:#b91c1c">⚠️ Daily job sync failed</h2>'
            f"<p>The run on {datetime.now():%Y-%m-%d %H:%M} crashed before finishing. No report was produced; "
            f"jobs may not be in sync today. Details:</p><pre style='background:#f3f4f6;padding:10px;"
            f"white-space:pre-wrap;font-size:12px'>{esc(exc_text[-4000:])}</pre></div>")
    log(send_email(f"⚠️ Daily job sync FAILED — {date.today().isoformat()}", body))


if __name__ == "__main__":
    lock = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("Another daily_job_sync run is in progress — exiting.")
        sys.exit(0)
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except BaseException:
        tb = traceback.format_exc()
        log(tb)
        if "--dry-run" not in sys.argv and "--no-email" not in sys.argv:
            alert(tb)
        sys.exit(2)
