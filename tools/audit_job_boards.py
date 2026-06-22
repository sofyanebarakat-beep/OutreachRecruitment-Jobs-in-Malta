#!/usr/bin/env python3
"""
audit_job_boards.py — Enhanced Job Board Sync Report

Compares:
- https://outreach-recruitment-agency.careers-page.com/
- https://outreachrecruitment.net/jobs/
- local jobs/index.html

Enhancements over the basic version:
- Slug pre-generated for every "Jobs to Add" prompt
- Jobs expiring soon flagged (posted > 60 days ago on careers platform)
- Missing category page alert at report level
- Reference numbers auto-incremented from highest in existing pages
- Category page auto-detected per job
- Close prompt slugs derived automatically from job titles

Usage:
    python3 tools/audit_job_boards.py
    python3 tools/audit_job_boards.py --max-pages 40
    python3 tools/audit_job_boards.py --no-details   # skip fetching full job descriptions
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, date, timedelta
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT         = Path(__file__).resolve().parents[1]
REPORT_DIR   = ROOT / "reports"
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
CAREERS_URL  = "https://outreach-recruitment-agency.careers-page.com/"
PUBLIC_URL   = "https://outreachrecruitment.net/jobs/"
LOCAL_JOBS   = ROOT / "jobs" / "index.html"
DELAY        = 1.0   # seconds between detail-page fetches

# ── Category page map (slug → local filename) ────────────────────────────────
CATEGORY_PAGES = {
    "Marine":       "marine-jobs-in-malta.html",
    "Engineering":  "engineering-jobs-in-malta.html",
    "Hospitality":  "hospitality-jobs-in-malta.html",
    "IT":           "it-jobs-in-malta.html",
}

# Keywords used to infer category from job title (checked in order)
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("IT",          ["developer", "software", "it support", "systems analyst", "infrastructure",
                     "cloud", "azure", "devops", "sharepoint", "drupal", "netsuite"]),
    ("Marine",      ["marine", "maritime", "shipyard", "diver", "diving", "vessel", "hull",
                     "yacht", "naval", "tank cleaner", "pipe fitter", "welder / burner",
                     "welder/burner", "plate shop", "marine carpenter", "marine turner",
                     "commercial diver", "ship"]),
    ("Engineering", ["engineer", "technician", "electrician", "mechanic", "hvac",
                     "structural", "quantity", "plumber", "welder", "maintenance",
                     "plant tech", "electronic"]),
    ("Hospitality", ["chef", "waiter", "waitress", "bartender", "housekeeper",
                     "receptionist", "f&b", "food", "beverage", "hotel", "restaurant",
                     "kitchen", "barista", "runner", "steward", "sommelier",
                     "commis", "pastry", "sous chef", "head chef"]),
]


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helper
# ─────────────────────────────────────────────────────────────────────────────

def fetch(url: str, timeout: int = 25, retries: int = 4) -> tuple[str, str]:
    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(req, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                return body, response.geturl()
        except HTTPError as exc:
            last_error = exc
            if exc.code == 429 and attempt < retries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            raise
        except URLError as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise last_error or RuntimeError(f"Could not fetch {url}")


def strip_tags(html: str) -> str:
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    html = re.sub(r"</(?:h[1-6]|p|div|li)>", "\n", html, flags=re.I)
    html = re.sub(r"<li[^>]*>", "• ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"[ \t]+", " ", unescape(html))
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def normalize_title(title: str) -> str:
    title = unescape(title).lower()
    title = title.replace("&", " and ")
    title = re.sub(r"\([^)]*\)", " ", title)
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def slugify(title: str) -> str:
    """Convert a job title to a URL-safe folder slug."""
    slug = unescape(title).lower()
    slug = re.sub(r"[&/\\]", " ", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug


def title_abbrev(title: str, length: int = 3) -> str:
    """Generate a short uppercase abbreviation from a job title for reference numbers."""
    words = re.sub(r"[^a-zA-Z0-9\s]", " ", title).split()
    stop = {"a", "an", "the", "of", "in", "for", "and", "or", "to", "with"}
    significant = [w for w in words if w.lower() not in stop and len(w) > 1]
    if not significant:
        significant = words
    abbrev = "".join(w[0].upper() for w in significant[:length])
    return abbrev.ljust(length, "X")[:length]


# ─────────────────────────────────────────────────────────────────────────────
# Reference number tracking
# ─────────────────────────────────────────────────────────────────────────────

def next_ref_number() -> int:
    """Scan all job pages and registry to find the highest OR-XXX-YYYY-NNN and return max+1."""
    pattern = re.compile(r"OR-[A-Z]{3}-\d{4}-(\d+)")
    highest = 0
    # Scan job HTML files
    for html_file in (ROOT / "jobs").rglob("*.html"):
        try:
            text = html_file.read_text(encoding="utf-8", errors="ignore")
            for m in pattern.finditer(text):
                n = int(m.group(1))
                if n > highest:
                    highest = n
        except Exception:
            pass
    return highest + 1


# ─────────────────────────────────────────────────────────────────────────────
# Category detection
# ─────────────────────────────────────────────────────────────────────────────

def infer_category(title: str) -> str:
    """Return the best-matching category name, or 'General' if no match."""
    tl = title.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in tl for kw in keywords):
            return category
    return "General"


def category_page_for(category: str) -> tuple[str | None, str | None]:
    """Return (filename, path) for the category page, or (None, None) if no page exists."""
    filename = CATEGORY_PAGES.get(category)
    if not filename:
        return None, None
    path = ROOT / filename
    return (filename, str(path)) if path.exists() else (None, None)


# ─────────────────────────────────────────────────────────────────────────────
# Careers platform scraping  (listing + detail pages)
# ─────────────────────────────────────────────────────────────────────────────

UUID_RE = re.compile(
    r'href="/jobs/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"',
    re.I,
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr = dict(attrs)
        href = attr.get("href")
        if href:
            self._href = href
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            text = re.sub(r"\s+", " ", " ".join(self._text)).strip()
            self.links.append((self._href, text))
            self._href = None
            self._text = []


@dataclass
class CareerJob:
    title: str
    uuid: str


@dataclass
class SourceResult:
    name: str
    url: str
    final_url: str
    count: int | None
    jobs: list[str]
    partial: bool
    warnings: list[str]

    @property
    def normalized_jobs(self) -> set[str]:
        return {normalize_title(j) for j in self.jobs if normalize_title(j)}


def parse_careers_page(max_pages: int = 40) -> tuple[SourceResult, dict[str, str]]:
    """Returns (SourceResult, uuid_map) where uuid_map is {normalized_title: uuid}."""
    jobs: list[str] = []
    uuid_map: dict[str, str] = {}
    seen: set[str] = set()
    count: int | None = None
    final_url = CAREERS_URL
    warnings: list[str] = []

    for page in range(1, max_pages + 1):
        url = CAREERS_URL if page == 1 else f"{CAREERS_URL}?page={page}"
        try:
            html, final_url = fetch(url)
        except URLError as exc:
            warnings.append(f"Could not fetch careers page {page}: {exc}")
            break

        if page == 1:
            count_match = re.search(r"(\d+)\s+Open Positions", strip_tags(html), re.I)
            if count_match:
                count = int(count_match.group(1))

        # Collect UUIDs per job
        uuid_set = {m.group(1) for m in UUID_RE.finditer(html)}

        parser = LinkParser()
        parser.feed(html)
        page_jobs = []
        for href, text in parser.links:
            if not re.search(r"/jobs/[0-9a-f-]{36}(?:$|/|\?)", href, re.I):
                continue
            if not text or text.lower() in {"refer", "apply now"}:
                continue
            key = normalize_title(text)
            if key and key not in seen:
                seen.add(key)
                jobs.append(text)
                page_jobs.append(text)
                # Map title → UUID (extract from href)
                uuid_m = re.search(r"/jobs/([0-9a-f-]{36})", href, re.I)
                if uuid_m:
                    uuid_map[key] = uuid_m.group(1)

        if not page_jobs:
            break

        pages = [int(p) for p in re.findall(r"page=(\d+)", html)]
        max_seen_page = max(pages) if pages else page
        if page >= max_seen_page:
            break

        time.sleep(2.0)

    if count is not None and len(jobs) != count:
        warnings.append(
            f"Careers count is {count}, but scraper collected {len(jobs)} titles."
        )

    return (
        SourceResult(
            name="Careers platform",
            url=CAREERS_URL,
            final_url=final_url,
            count=count,
            jobs=jobs,
            partial=False,
            warnings=warnings,
        ),
        uuid_map,
    )


def fetch_job_detail(uuid: str, title: str) -> dict:
    """Fetch a careers platform job page and return location, description, apply_url, date_posted."""
    url = f"https://outreach-recruitment-agency.careers-page.com/jobs/{uuid}"
    result = {
        "uuid": uuid,
        "apply_url": f"{url}/apply",
        "location": "Malta",
        "description": "",
        "date_posted": None,
    }
    try:
        html, _ = fetch(url)
    except Exception as e:
        print(f"    WARNING: could not fetch detail for {title}: {e}")
        return result

    # Extract from JSON-LD JobPosting schema
    json_lds = re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I
    )
    for block in json_lds:
        try:
            j = json.loads(block)
            if not isinstance(j, dict) or j.get("@type") != "JobPosting":
                continue
            # Location
            loc = j.get("jobLocation", {}).get("address", {})
            city = loc.get("addressLocality", "")
            country = loc.get("addressCountry", "")
            if city:
                result["location"] = f"{city}, {country}" if country else city
            # Description
            desc_html = j.get("description", "")
            if desc_html:
                result["description"] = strip_tags(desc_html)
            # Date posted
            dp = j.get("datePosted", "")
            if dp:
                result["date_posted"] = dp[:10]
            # Apply URL from schema
            app_url = j.get("applicationUrl") or j.get("apply_url")
            if app_url:
                result["apply_url"] = app_url
            break
        except Exception:
            continue

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Parse public site and local grid (unchanged logic)
# ─────────────────────────────────────────────────────────────────────────────

def parse_public_site() -> SourceResult:
    warnings: list[str] = []
    try:
        html, final_url = fetch(PUBLIC_URL)
    except URLError as exc:
        return SourceResult("Public website", PUBLIC_URL, PUBLIC_URL, None, [], True, [str(exc)])

    text = strip_tags(html)
    count = None
    count_match = re.search(r"(\d+)\s+Job Listings", text, re.I)
    if count_match:
        count = int(count_match.group(1))

    jobs = []
    seen = set()
    for title in re.findall(r"<h3[^>]*>\s*(.*?)\s*</h3>", html, re.I | re.S):
        clean = strip_tags(title)
        if not clean:
            continue
        key = normalize_title(clean)
        if key and key not in seen:
            seen.add(key)
            jobs.append(clean)

    spam_markers = ["Hacklink", "Nulled", "casino", "escort", "bet", "porn"]
    found_spam = sorted({m for m in spam_markers if re.search(m, text, re.I)})
    if found_spam:
        warnings.append("Suspicious footer/link text found on public site: " + ", ".join(found_spam))

    return SourceResult("Public website", PUBLIC_URL, final_url, count, jobs, True, warnings)


def parse_local_jobs() -> SourceResult:
    if not LOCAL_JOBS.exists():
        return SourceResult(
            "Local static grid", str(LOCAL_JOBS), str(LOCAL_JOBS), None, [], True,
            ["jobs/index.html not found."]
        )

    html = LOCAL_JOBS.read_text(encoding="utf-8")
    count = None
    count_match = re.search(r"Showing\s+(\d+)\s+jobs?", html, re.I)
    if count_match:
        count = int(count_match.group(1))

    card_count = len(re.findall(r"<article[^>]+data-opening-job", html, re.I))
    jobs = []
    seen = set()
    card_blocks = re.findall(
        r"(<article[^>]+data-opening-job.*?</article>)", html, re.I | re.S
    )
    for block in card_blocks:
        match = re.search(
            r'<h3[^>]*class="[^"]*\bheading-h5\b[^"]*"[^>]*>\s*(.*?)\s*</h3>',
            block, re.I | re.S,
        )
        if not match:
            continue
        title = match.group(1)
        clean = strip_tags(title)
        key = normalize_title(clean)
        if key and key not in seen:
            seen.add(key)
            jobs.append(clean)

    warnings = []
    if count is not None and card_count != count:
        warnings.append(f"Local count is {count}, but found {card_count} job card elements.")
    if card_count and len(jobs) != card_count:
        warnings.append(f"Found {card_count} local job cards, but extracted {len(jobs)} unique titles.")

    return SourceResult(
        "Local static grid", str(LOCAL_JOBS), str(LOCAL_JOBS), count, jobs, False, warnings
    )


def missing_titles(source: SourceResult, target: SourceResult) -> list[str]:
    target_keys = target.normalized_jobs
    return [title for title in source.jobs if normalize_title(title) not in target_keys]


# ─────────────────────────────────────────────────────────────────────────────
# Prompt builders
# ─────────────────────────────────────────────────────────────────────────────

def build_add_prompt(
    title: str,
    detail: dict,
    ref_number: str,
    slug: str,
    category: str,
    cat_page: str | None,
) -> str:
    location = detail.get("location", "Malta")
    apply_url = detail.get("apply_url", "")
    description = detail.get("description", "")

    # Category page step
    if cat_page:
        cat_step = f"4. Category page exists → add job card to {cat_page}"
    else:
        cat_step = f"4. No matching category page for {category} — skip category page step, note in report"

    return f"""Add a new job using the job-seo-generator skill.

Job title: {title}
Category: {category}
Location city: {location}
Salary range: Not disclosed
Apply URL: {apply_url}
Folder: jobs/{slug}/

Job description:
{description}

Defaults (apply silently):
- Employment type: Full-time
- Reference number: {ref_number}
- Application method: Apply online
- Remote status: On-site
- Language: English
- Salary: always in baseSalary JSON-LD only, never visible on page — show "Competitive" instead

Publishing steps (all mandatory — do not skip any):
1. Create jobs/{slug}/index.html — full job detail page with JobPosting schema + BreadcrumbList schema
2. Set apply URL in #job-apply-panel, How To Apply body section, and applicationUrl schema field
3. Add job card first in opening-jobs-grid → jobs/index.html
{cat_step}
5. Increment open-position count in jobs/index.html (read current count, do not guess)
6. Update sitemaps/sitemap-jobs.xml — add new job URL + update /jobs lastmod to today
7. Update ItemList JSON-LD in jobs/index.html — insert new job as position 1
8. Update freshness text in jobs/index.html → "Browse N+ current job vacancies in Malta — updated {datetime.now().strftime('%B %Y')}"
9. Add visible internal link in job detail page → "Browse all Jobs in Malta" → /jobs

Generate all 12 sections of the SEO package."""


def build_close_prompt(jobs_to_close: list[str]) -> str:
    slug_lines = "\n".join(
        f"- {title} → slug: {slugify(title)}"
        for title in jobs_to_close
    )
    slugs_arg = " ".join(slugify(t) for t in jobs_to_close)
    return f"""Close the following jobs using the expire-job skill.

Jobs to close (these positions are no longer accepting applications):
{slug_lines}

Steps (all mandatory — do not skip any):
1. Run: python3 tools/expire_job.py {slugs_arg}
2. Verify tools/jobs_registry.json shows status: "expired" for all {len(jobs_to_close)} slugs
3. On each job detail page (jobs/[slug]/index.html):
   a. Remove the entire #job-apply-panel section
   b. Remove all elements with [data-job-apply-trigger] (Apply Now buttons)
   c. Remove the .job-mobile-apply-cta sticky bar
   d. In the cms-article How To Apply section, replace the apply link and button with:
      "This position is no longer accepting applications. Browse our current open vacancies →"
      linking to /jobs/
   e. Confirm the JobPosting schema validThrough is set to a past date
4. In jobs/index.html: mark each closed job card with a "Position Closed" badge — do NOT remove the cards from the grid
5. Update sitemaps/sitemap-jobs.xml — set <lastmod> for each closed job URL to today"""


# ─────────────────────────────────────────────────────────────────────────────
# Expiry checks
# ─────────────────────────────────────────────────────────────────────────────

def check_expiring_soon(days: int = 60) -> list[dict]:
    """
    Return registry jobs with date older than `days` ago that are not yet expired.
    These are jobs that have been sitting on the site a long time and may close soon.
    """
    if not REGISTRY_PATH.exists():
        return []
    cutoff = date.today() - timedelta(days=days)
    results = []
    for job in json.loads(REGISTRY_PATH.read_text(encoding="utf-8")):
        if job.get("status") == "expired":
            continue
        d_str = job.get("date", "")
        if not d_str:
            continue
        try:
            posted = date.fromisoformat(d_str)
        except ValueError:
            continue
        if posted <= cutoff:
            results.append({
                "title": job.get("title", job["slug"]),
                "slug": job["slug"],
                "date": d_str,
                "days_old": (date.today() - posted).days,
            })
    results.sort(key=lambda x: x["days_old"], reverse=True)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Missing category page alerts
# ─────────────────────────────────────────────────────────────────────────────

def find_missing_category_pages(titles: list[str]) -> list[dict]:
    """
    For each title in the list, infer its category and check whether the
    corresponding category page exists on the site. Return those without a page.
    """
    missing = []
    seen_cats: set[str] = set()
    for title in titles:
        cat = infer_category(title)
        if cat in seen_cats:
            continue
        cat_filename, _ = category_page_for(cat)
        if cat_filename is None and cat not in ("General",):
            seen_cats.add(cat)
            missing.append({"category": cat, "example_job": title})
    return missing


# ─────────────────────────────────────────────────────────────────────────────
# Report writer
# ─────────────────────────────────────────────────────────────────────────────

def write_reports(
    results: list[SourceResult],
    uuid_map: dict[str, str],
    fetch_details: bool = True,
) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(exist_ok=True)
    today = datetime.now()
    stamp = today.strftime("%Y-%m-%d")
    md_path   = REPORT_DIR / f"job-board-sync-report-{stamp}.md"
    json_path = REPORT_DIR / f"job-board-sync-report-{stamp}.json"

    careers, public, local = results
    missing_local  = missing_titles(careers, local)   # Jobs to Add
    extra_local    = missing_titles(local, careers)   # Jobs to Close

    # ── Ref number counter ──────────────────────────────────────────────────
    next_ref = next_ref_number()

    # ── Expiring soon ───────────────────────────────────────────────────────
    expiring = check_expiring_soon(days=60)

    # ── Missing category page alert (for jobs to add) ───────────────────────
    missing_cat_pages = find_missing_category_pages(missing_local)

    # ── Fetch details for each job to add ───────────────────────────────────
    job_details: dict[str, dict] = {}
    if fetch_details and missing_local:
        print(f"\n  Fetching details for {len(missing_local)} job(s) to add …")
        for title in missing_local:
            uuid = uuid_map.get(normalize_title(title), "")
            if not uuid:
                print(f"    WARNING: no UUID found for '{title}' — skipping detail fetch")
                job_details[title] = {"apply_url": "", "location": "Malta", "description": ""}
                continue
            print(f"    {title} …", end=" ", flush=True)
            detail = fetch_job_detail(uuid, title)
            job_details[title] = detail
            print(f"OK ({detail['location']})")
            time.sleep(DELAY)

    # ── Build prompts ────────────────────────────────────────────────────────
    add_prompts: list[dict] = []
    for i, title in enumerate(missing_local):
        detail  = job_details.get(title, {"apply_url": "", "location": "Malta", "description": ""})
        slug    = slugify(title)
        cat     = infer_category(title)
        cat_filename, _ = category_page_for(cat)
        abbrev  = title_abbrev(title)
        ref_num = f"OR-{abbrev}-{today.year}-{next_ref + i:03d}"
        prompt  = build_add_prompt(title, detail, ref_num, slug, cat, cat_filename)
        add_prompts.append({
            "title":    title,
            "slug":     slug,
            "category": cat,
            "ref":      ref_num,
            "location": detail.get("location", "Malta"),
            "apply_url": detail.get("apply_url", ""),
            "date_posted": detail.get("date_posted"),
            "prompt":   prompt,
        })

    # ── Status header numbers ────────────────────────────────────────────────
    n_add   = len(missing_local)
    n_close = len(extra_local)
    n_warn  = len(expiring) + len(missing_cat_pages)

    # ── Write Markdown ───────────────────────────────────────────────────────
    lines: list[str] = [
        "# Job Sync Report — Outreach Recruitment",
        "",
        f"Generated: {today.strftime('%Y-%m-%d')}",
        "",
        f"→ **{n_add} to add** · **{n_close} to close** · **{n_warn} alert(s)**",
        "",
        "---",
    ]

    # ── Alerts section ───────────────────────────────────────────────────────
    if expiring or missing_cat_pages:
        lines += ["", "## Alerts", ""]
        if expiring:
            lines.append(
                f"**Jobs expiring soon** — {len(expiring)} active job(s) posted more than "
                f"60 days ago. Confirm they are still open on the careers platform before adding."
            )
            lines.append("")
            lines.append("| Job | Days Live | Date Posted |")
            lines.append("|---|---:|---|")
            for e in expiring:
                lines.append(f"| {e['title']} | {e['days_old']} | {e['date']} |")
            lines.append("")
        if missing_cat_pages:
            lines.append(
                f"**Missing category pages** — {len(missing_cat_pages)} category/ies needed "
                f"by jobs to add have no matching page on the site:"
            )
            for mc in missing_cat_pages:
                lines.append(f"- **{mc['category']}** (e.g. *{mc['example_job']}*) — no category page found")
            lines.append("")

    # ── Jobs to Add ─────────────────────────────────────────────────────────
    lines += ["", f"## Jobs to Add", "", f"{n_add} job(s) on the careers platform not yet on the static website.", ""]

    if not add_prompts:
        lines.append("- None")
    else:
        for i, p in enumerate(add_prompts, 1):
            lines += [
                "---",
                "",
                f"### {i}. {p['title']}",
                "",
                p["prompt"],
                "",
            ]

    # ── Jobs to Close ────────────────────────────────────────────────────────
    lines += [
        "---",
        "",
        "## Jobs to Close",
        "",
        f"{n_close} job(s) on the static website no longer found on the careers platform.",
        "Keep pages live but disable all application functionality.",
        "",
    ]

    if not extra_local:
        lines.append("- None")
    else:
        lines += [build_close_prompt(extra_local), ""]

    # ── Write files ──────────────────────────────────────────────────────────
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data = {
        "generated_at": today.isoformat(timespec="seconds"),
        "jobs_to_add": [
            {"title": p["title"], "slug": p["slug"], "ref": p["ref"],
             "location": p["location"], "apply_url": p["apply_url"],
             "date_posted": p["date_posted"]}
            for p in add_prompts
        ],
        "jobs_to_close": extra_local,
        "expiring_soon": expiring,
        "missing_category_pages": missing_cat_pages,
    }
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return md_path, json_path


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Outreach Recruitment job board sync report")
    parser.add_argument("--max-pages", type=int, default=40, help="Max careers listing pages to scrape")
    parser.add_argument("--no-details", action="store_true", help="Skip fetching full job descriptions")
    args = parser.parse_args()

    print("Scraping careers platform …")
    careers_result, uuid_map = parse_careers_page(max_pages=args.max_pages)

    print("Scraping public website …")
    public_result = parse_public_site()

    print("Reading local static grid …")
    local_result = parse_local_jobs()

    results = [careers_result, public_result, local_result]

    md_path, json_path = write_reports(
        results, uuid_map, fetch_details=not args.no_details
    )

    print(f"\nCareers platform: count={careers_result.count} scraped={len(careers_result.jobs)}")
    print(f"Public website:   scraped={len(public_result.jobs)} (partial)")
    print(f"Local static:     count={local_result.count} scraped={len(local_result.jobs)}")
    for result in results:
        for warning in result.warnings:
            print(f"  WARNING ({result.name}): {warning}")
    print(f"\nReport: {md_path}")
    print(f"JSON:   {json_path}")

    missing_local  = missing_titles(careers_result, local_result)
    extra_local    = missing_titles(local_result, careers_result)
    expiring       = check_expiring_soon(days=60)
    missing_cats   = find_missing_category_pages(missing_local)

    print(f"\n→ {len(missing_local)} to add · {len(extra_local)} to close · "
          f"{len(expiring)} expiring soon · {len(missing_cats)} missing category page(s)")

    counts = [r.count for r in results if r.count is not None]
    return 1 if len(set(counts)) > 1 else 0


if __name__ == "__main__":
    sys.exit(main())
