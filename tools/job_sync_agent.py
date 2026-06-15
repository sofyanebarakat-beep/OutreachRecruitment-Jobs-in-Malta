#!/usr/bin/env python3
"""
job_sync_agent.py — Outreach Recruitment Job Sync Agent
========================================================
GOAL: Keep outreachrecruitment.net/jobs/ 100% in sync with the careers page.

Compares all active jobs between:
  Source of Truth: https://outreach-recruitment-agency.careers-page.com/
  Website:         https://outreachrecruitment.net/jobs/

Usage:
  python3 tools/job_sync_agent.py               # full run + email
  python3 tools/job_sync_agent.py --auto-fix    # auto-add missing + expire extra + push
  python3 tools/job_sync_agent.py --no-email    # run, save report, skip email
  python3 tools/job_sync_agent.py --no-seo      # skip per-page SEO/broken-link checks
  python3 tools/job_sync_agent.py --dry-run     # no email, no SEO, no sitemap, print only

Email config — set in tools/sync_config.json or as environment variables:
  SMTP_HOST  SMTP_PORT  SMTP_USER  SMTP_PASS
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import smtplib
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import date as date_type
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
CONFIG_PATH = ROOT / "tools" / "sync_config.json"

CAREERS_URL = "https://outreach-recruitment-agency.careers-page.com/"
PUBLIC_JOBS_URL = "https://outreachrecruitment.net/jobs/"
PUBLIC_BASE = "https://outreachrecruitment.net"
SITEMAP_INDEX = "https://outreachrecruitment.net/sitemap_index.xml"
GSC_SITE_URL = "https://outreachrecruitment.net/"
GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"

REPORT_RECIPIENT = "sbarakat@outreachrecruitment.net"
DELAY = 0.8  # seconds between requests

STATE_PATH = ROOT / "tools" / "sync_state.json"
DASHBOARD_PATH = ROOT / "sync-dashboard.html"
GOOGLE_INDEXING_LOG_PATH = REPORT_DIR / "google_indexing_history.csv"
AUTO_CLOSE_THRESHOLD = 3   # consecutive checks before auto-closing an extra job
DUPLICATE_THRESHOLD = 0.72  # similarity score to flag potential duplicate titles


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CareersJob:
    title: str
    uuid: str
    url: str


@dataclass
class WebsiteJob:
    title: str
    slug: str
    url: str
    location: str = ""
    employment_type: str = ""
    category: str = ""
    # Populated during SEO check
    status: int = 0
    meta_title: str = ""
    meta_description: str = ""
    canonical: str = ""
    is_indexable: bool = True
    schema_issues: list[str] = field(default_factory=list)


@dataclass
class SyncReport:
    generated_at: str
    careers_count_advertised: int
    careers_count_scraped: int
    website_count: int

    missing_jobs: list[str] = field(default_factory=list)       # titles only (for display)
    missing_jobs_detail: list[dict] = field(default_factory=list)  # {title, uuid, careers_url}
    extra_jobs: list[str] = field(default_factory=list)         # on website, not careers
    title_mismatches: list[dict] = field(default_factory=list)  # similar but different title
    location_mismatches: list[dict] = field(default_factory=list)
    broken_links: list[dict] = field(default_factory=list)
    seo_issues: list[dict] = field(default_factory=list)
    sitemap_missing: list[str] = field(default_factory=list)

    sync_score: float = 100.0
    previous_score: float | None = None
    warnings: list[str] = field(default_factory=list)

    # Populated by auto_fix()
    auto_fixed_added: list[str] = field(default_factory=list)
    auto_fixed_removed: list[str] = field(default_factory=list)
    auto_fixed_added_jobs: list[dict] = field(default_factory=list)    # {title, slug, url}
    auto_fixed_removed_jobs: list[dict] = field(default_factory=list)  # {title, slug, url}

    # Ready-to-paste Claude prompts for each missing job
    missing_prompts: list[str] = field(default_factory=list)

    # New feature fields
    duplicates: list[dict] = field(default_factory=list)
    schema_issues: list[dict] = field(default_factory=list)
    auto_closed_this_run: list[str] = field(default_factory=list)
    auto_closed_jobs: list[dict] = field(default_factory=list)  # {title, slug, url}
    indexing_submissions: list[dict] = field(default_factory=list)
    ranking_readiness: list[dict] = field(default_factory=list)
    priority_jobs: list[dict] = field(default_factory=list)
    keyword_issues: list[dict] = field(default_factory=list)
    internal_link_issues: list[dict] = field(default_factory=list)
    content_quality_issues: list[dict] = field(default_factory=list)
    category_ranking: list[dict] = field(default_factory=list)
    schema_eligibility: list[dict] = field(default_factory=list)
    ranking_action_plan: list[str] = field(default_factory=list)
    gsc_url_inspection: list[dict] = field(default_factory=list)
    gsc_search_performance: list[dict] = field(default_factory=list)
    gsc_indexing_problems: list[dict] = field(default_factory=list)
    gsc_canonical_conflicts: list[dict] = field(default_factory=list)
    gsc_not_indexed_jobs: list[dict] = field(default_factory=list)
    gsc_zero_impression_jobs: list[dict] = field(default_factory=list)
    gsc_ranking_opportunities: list[dict] = field(default_factory=list)
    gsc_query_match_issues: list[dict] = field(default_factory=list)
    gsc_rich_result_issues: list[dict] = field(default_factory=list)
    gsc_action_plan: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url: str, timeout: int = 25, retries: int = 4) -> tuple[str, int]:
    """Return (body, status_code). Raises on network error."""
    req = Request(url, headers=HEADERS)
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace"), resp.status
        except HTTPError as exc:
            if exc.code == 404:
                return "", 404
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


def fetch_head(url: str, timeout: int = 15) -> int:
    """Return HTTP status code using HEAD request."""
    try:
        req = Request(url, method="HEAD", headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            return resp.status
    except HTTPError as exc:
        return exc.code
    except URLError:
        return 0


def strip_tags(html: str) -> str:
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"[ \t]+", " ", unescape(html)).strip()


def normalize_title(title: str) -> str:
    title = unescape(title).lower()
    title = title.replace("&", " and ")
    title = re.sub(r"\([^)]*\)", " ", title)
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Scrape careers page (all listing pages)
# ─────────────────────────────────────────────────────────────────────────────

UUID_RE = re.compile(
    r'/jobs/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
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


def scrape_careers_page(max_pages: int = 50) -> tuple[list[CareersJob], int]:
    """
    Scrape all job titles from careers-page.com listing pages.
    Returns (jobs_list, advertised_count).
    """
    jobs: list[CareersJob] = []
    seen_uuids: set[str] = set()
    advertised_count = 0

    page = 1
    while page <= max_pages:
        url = CAREERS_URL if page == 1 else f"{CAREERS_URL}?page={page}"
        print(f"  [Careers] page {page} — {url}")
        try:
            html, _ = fetch(url)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            break

        if page == 1:
            m = re.search(r"(\d+)\s+Open\s+Positions", html, re.I)
            if m:
                advertised_count = int(m.group(1))

        parser = LinkParser()
        parser.feed(html)

        new_on_page = 0
        for href, text in parser.links:
            m = UUID_RE.search(href)
            if not m:
                continue
            uuid = m.group(1)
            if not text or normalize_title(text) in {"refer", "apply now", "apply"}:
                continue
            if uuid not in seen_uuids:
                seen_uuids.add(uuid)
                full_url = f"https://outreach-recruitment-agency.careers-page.com/jobs/{uuid}"
                jobs.append(CareersJob(title=text.strip(), uuid=uuid, url=full_url))
                new_on_page += 1

        if new_on_page == 0:
            break  # no new jobs = we're past the last page

        # Detect max page from pagination links
        page_nums = [int(p) for p in re.findall(r"page=(\d+)", html)]
        max_seen = max(page_nums) if page_nums else page
        if page >= max_seen and new_on_page < 10:
            # We might be on the last page; try one more to confirm
            page += 1
            continue

        page += 1
        time.sleep(DELAY)

    return jobs, advertised_count


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Scrape public website job cards
# ─────────────────────────────────────────────────────────────────────────────

JOB_CARD_RE = re.compile(
    r'<article[^>]+data-opening-job[^>]*>(.*?)</article>',
    re.I | re.S,
)
TITLE_RE = re.compile(r'<h3[^>]*class="[^"]*heading-h5[^"]*"[^>]*>\s*(.*?)\s*</h3>', re.I | re.S)
LOCATION_RE = re.compile(r'<div[^>]*class="[^"]*opening-job-company[^"]*"[^>]*>\s*(.*?)\s*</div>', re.I | re.S)
LINK_RE = re.compile(r'<a[^>]+href="(/jobs/[^"]+)"', re.I)
META_SPANS_RE = re.compile(r'<div[^>]*class="[^"]*opening-job-meta[^"]*"[^>]*>(.*?)</div>', re.I | re.S)
SPAN_RE = re.compile(r'<span[^>]*>(.*?)</span>', re.I | re.S)
DATA_ATTR_RE = re.compile(r'data-(\w+)="([^"]*)"')


def scrape_public_website() -> list[WebsiteJob]:
    """Extract all job cards from outreachrecruitment.net/jobs/."""
    print(f"  [Website] Fetching {PUBLIC_JOBS_URL}")
    html, status = fetch(PUBLIC_JOBS_URL)
    if status != 200:
        print(f"  ERROR: Website returned {status}")
        return []

    jobs: list[WebsiteJob] = []
    seen_slugs: set[str] = set()

    for card_match in JOB_CARD_RE.finditer(html):
        card_html = card_match.group(0)

        # Title
        tm = TITLE_RE.search(card_html)
        if not tm:
            continue
        title = strip_tags(tm.group(1)).strip()
        if not title:
            continue

        # URL / slug
        lm = LINK_RE.search(card_html)
        rel_url = lm.group(1) if lm else ""
        # Normalize: strip /jobs/ prefix and slashes to get just the slug
        slug = rel_url.strip("/").replace("jobs/", "")
        full_url = f"{PUBLIC_BASE}/jobs/{slug}" if slug else ""

        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        # Location
        loc_m = LOCATION_RE.search(card_html)
        location = strip_tags(loc_m.group(1)).strip() if loc_m else ""

        # Employment type + category from meta spans
        employment_type = ""
        category = ""
        meta_m = META_SPANS_RE.search(card_html)
        if meta_m:
            spans = SPAN_RE.findall(meta_m.group(1))
            if spans:
                employment_type = strip_tags(spans[0]).strip()
            if len(spans) > 1:
                category = strip_tags(spans[1]).strip()

        # Fallback: data attributes on article
        if not location or not employment_type:
            attrs = dict(DATA_ATTR_RE.findall(card_html))
            if not location and "location" in attrs:
                location = attrs["location"].title()
            if not employment_type and "title" in attrs:
                # employment type isn't stored as data-attr, skip
                pass

        jobs.append(WebsiteJob(
            title=title,
            slug=slug,
            url=full_url,
            location=location,
            employment_type=employment_type,
            category=category,
        ))

    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Per-page SEO + broken link check
# ─────────────────────────────────────────────────────────────────────────────

META_TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)
META_DESC_RE = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']', re.I)
META_DESC_RE2 = re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']', re.I)
CANONICAL_RE = re.compile(
    r'<link\b[^>]*\bhref=["\']([^"\']*)["\'][^>]*\brel=["\']canonical["\']'
    r'|<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']*)["\']',
    re.I,
)
NOINDEX_RE = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', re.I)
JSONLD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
REQUIRED_SCHEMA_FIELDS = ["title", "description", "datePosted", "hiringOrganization", "jobLocation"]
RECOMMENDED_SCHEMA_FIELDS = ["validThrough", "employmentType", "identifier"]


def validate_job_schema(html: str) -> tuple[dict | None, list[str]]:
    """Extract and validate JSON-LD JobPosting schema. Returns (schema_dict, issues_list)."""
    schema_m = JSONLD_RE.search(html)
    if not schema_m:
        return None, ["No JSON-LD schema found"]
    try:
        schema = json.loads(schema_m.group(1))
    except Exception:
        return None, ["Malformed JSON in JSON-LD block"]

    if schema.get("@type") not in ("JobPosting", ["JobPosting"]):
        return schema, [f"@type is '{schema.get('@type')}', expected JobPosting"]

    issues: list[str] = []
    for f in REQUIRED_SCHEMA_FIELDS:
        if not schema.get(f):
            issues.append(f"Missing required: {f}")
    for f in RECOMMENDED_SCHEMA_FIELDS:
        if not schema.get(f):
            issues.append(f"Missing recommended: {f}")

    dp = schema.get("datePosted", "")
    if dp:
        try:
            datetime.fromisoformat(dp)
        except Exception:
            issues.append(f"Invalid datePosted: {dp!r}")

    vt = schema.get("validThrough", "")
    if vt:
        try:
            if datetime.fromisoformat(vt) < datetime.now():
                issues.append(f"validThrough expired: {vt[:10]}")
        except Exception:
            issues.append(f"Invalid validThrough: {vt!r}")

    org = schema.get("hiringOrganization", {})
    if isinstance(org, dict) and not org.get("name"):
        issues.append("hiringOrganization missing 'name'")

    loc = schema.get("jobLocation", {})
    if isinstance(loc, dict):
        addr = loc.get("address", {})
        if isinstance(addr, dict) and not addr.get("addressLocality"):
            issues.append("jobLocation.address missing addressLocality")

    return schema, issues


def check_job_page_seo(job: WebsiteJob) -> None:
    """Fetch job page and populate status, meta_title, meta_description, canonical, is_indexable."""
    if not job.url:
        job.status = 0
        return
    try:
        html, status = fetch(job.url)
        job.status = status
        if status != 200:
            return

        tm = META_TITLE_RE.search(html)
        job.meta_title = strip_tags(tm.group(1)).strip() if tm else ""

        dm = META_DESC_RE.search(html) or META_DESC_RE2.search(html)
        job.meta_description = dm.group(1).strip() if dm else ""

        cm = CANONICAL_RE.search(html)
        job.canonical = (cm.group(1) or cm.group(2)).strip() if cm else ""

        job.is_indexable = not bool(NOINDEX_RE.search(html))

        # Validate JSON-LD structured data
        _, job.schema_issues = validate_job_schema(html)

    except Exception as exc:
        job.status = 0
        print(f"    WARN: {job.url} — {exc}")


def run_seo_checks(website_jobs: list[WebsiteJob]) -> None:
    """Check all job pages. Updates jobs in-place."""
    total = len(website_jobs)
    print(f"\n[SEO] Checking {total} job pages …")
    for i, job in enumerate(website_jobs, 1):
        print(f"  [{i}/{total}] {job.slug}", end=" … ", flush=True)
        check_job_page_seo(job)
        status_str = str(job.status) if job.status else "ERR"
        issues = []
        if job.status != 200:
            issues.append(f"HTTP {status_str}")
        else:
            if not job.meta_title:
                issues.append("no meta title")
            if not job.meta_description:
                issues.append("no meta desc")
            if not job.canonical:
                issues.append("no canonical")
            if not job.is_indexable:
                issues.append("noindex")
        print("OK" if not issues else " | ".join(issues))
        time.sleep(DELAY)


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Sitemap check
# ─────────────────────────────────────────────────────────────────────────────

def fetch_sitemap_urls() -> set[str]:
    """Fetch all job URLs from the sitemap index + child sitemaps."""
    urls: set[str] = set()
    try:
        index_html, _ = fetch(SITEMAP_INDEX)
        child_sitemaps = re.findall(r"<loc>\s*(https://[^\s<]+)\s*</loc>", index_html, re.I)
        for sm_url in child_sitemaps:
            try:
                sm_html, _ = fetch(sm_url)
                locs = re.findall(r"<loc>\s*(https://[^\s<]+)\s*</loc>", sm_html, re.I)
                for loc in locs:
                    if "/jobs/" in loc:
                        urls.add(loc.rstrip("/"))  # normalize: no trailing slash
            except Exception:
                pass
            time.sleep(0.3)

        # Also check the main sitemap.xml
        main_sm, _ = fetch(f"{PUBLIC_BASE}/sitemap.xml")
        locs = re.findall(r"<loc>\s*(https://[^\s<]+)\s*</loc>", main_sm, re.I)
        for loc in locs:
            if "/jobs/" in loc:
                urls.add(loc.rstrip("/"))

    except Exception as exc:
        print(f"  WARN: Could not fetch sitemap: {exc}")

    return urls


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Comparison logic
# ─────────────────────────────────────────────────────────────────────────────

SIMILARITY_THRESHOLD = 0.75  # flag as potential mismatch if > this but not exact


def build_report(
    careers_jobs: list[CareersJob],
    careers_count_advertised: int,
    website_jobs: list[WebsiteJob],
    sitemap_urls: set[str],
    skip_seo: bool = False,
) -> SyncReport:
    report = SyncReport(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        careers_count_advertised=careers_count_advertised,
        careers_count_scraped=len(careers_jobs),
        website_count=len(website_jobs),
    )

    careers_norm = {normalize_title(j.title): j for j in careers_jobs}
    website_norm = {normalize_title(j.title): j for j in website_jobs}

    # Rule 1 — count mismatch (informational, captured in report fields)

    # Load previous score for trend
    report.previous_score = load_previous_score()

    # Rule 2 — missing from website
    for norm_title, cj in careers_norm.items():
        if norm_title not in website_norm:
            report.missing_jobs.append(cj.title)
            report.missing_jobs_detail.append({
                "title": cj.title,
                "uuid": cj.uuid,
                "careers_url": cj.url,
            })

    # Rule 3 — extra on website (closed jobs still visible)
    for norm_title, wj in website_norm.items():
        if norm_title not in careers_norm:
            report.extra_jobs.append(wj.title)

    # Rule 4 — title mismatches (similar but not exact)
    careers_unmatched = [cj for cj in careers_jobs if normalize_title(cj.title) not in website_norm]
    website_unmatched = [wj for wj in website_jobs if normalize_title(wj.title) not in careers_norm]

    used_website: set[str] = set()
    for cj in careers_unmatched:
        best_score = 0.0
        best_wj = None
        for wj in website_unmatched:
            if wj.slug in used_website:
                continue
            score = title_similarity(cj.title, wj.title)
            if score > best_score:
                best_score = score
                best_wj = wj
        if best_wj and best_score >= SIMILARITY_THRESHOLD:
            used_website.add(best_wj.slug)
            report.title_mismatches.append({
                "careers_title": cj.title,
                "website_title": best_wj.title,
                "similarity": round(best_score, 2),
                "website_url": best_wj.url,
            })

    # Rule 5 — location mismatches (compare registry vs website cards)
    if REGISTRY_PATH.exists():
        registry = {j["slug"]: j for j in json.loads(REGISTRY_PATH.read_text())}
        for wj in website_jobs:
            reg = registry.get(wj.slug)
            if reg and wj.location:
                reg_loc = reg.get("location", "").strip().lower()
                web_loc = wj.location.strip().lower()
                if reg_loc and web_loc and reg_loc != web_loc:
                    report.location_mismatches.append({
                        "title": wj.title,
                        "registry_location": reg.get("location", ""),
                        "website_location": wj.location,
                        "url": wj.url,
                    })

    if not skip_seo:
        # Rule 7 — broken links
        for wj in website_jobs:
            if wj.status == 404 or wj.status == 0:
                report.broken_links.append({
                    "title": wj.title,
                    "url": wj.url,
                    "status": wj.status,
                })

        # Rule 8 — SEO issues
        for wj in website_jobs:
            if wj.status != 200:
                continue
            issues = []
            if not wj.meta_title:
                issues.append("Missing meta title")
            elif len(wj.meta_title) < 30:
                issues.append(f"Meta title too short ({len(wj.meta_title)} chars)")
            elif len(wj.meta_title) > 65:
                issues.append(f"Meta title too long ({len(wj.meta_title)} chars)")
            if not wj.meta_description:
                issues.append("Missing meta description")
            elif len(wj.meta_description) < 70:
                issues.append(f"Meta description too short ({len(wj.meta_description)} chars)")
            elif len(wj.meta_description) > 160:
                issues.append(f"Meta description too long ({len(wj.meta_description)} chars)")
            if not wj.canonical:
                issues.append("Missing canonical URL")
            if not wj.is_indexable:
                issues.append("Page set to noindex")
            if issues:
                report.seo_issues.append({
                    "title": wj.title,
                    "url": wj.url,
                    "issues": issues,
                })

    # Rule 9 — sitemap missing (compare without trailing slash)
    if sitemap_urls:
        for wj in website_jobs:
            normalized_url = wj.url.rstrip("/")
            if normalized_url not in sitemap_urls:
                report.sitemap_missing.append(wj.url)

    # Rule 10 — duplicate title detection within website jobs
    report.duplicates = detect_duplicates(website_jobs)

    # Rule 11 — schema issues (collected per-job during SEO check)
    if not skip_seo:
        for wj in website_jobs:
            if wj.schema_issues and wj.status == 200:
                report.schema_issues.append({
                    "title": wj.title,
                    "url": wj.url,
                    "issues": wj.schema_issues,
                })

    # Ranking analysis — separate from sync score
    apply_ranking_analysis(report, website_jobs)

    # Sync score
    total_penalties = 0
    weight_missing = 5
    weight_extra = 3
    weight_broken = 10
    weight_seo = 1
    weight_sitemap = 0.5

    total_jobs = max(careers_count_advertised, len(website_jobs), 1)
    penalties = (
        len(report.missing_jobs) * weight_missing
        + len(report.extra_jobs) * weight_extra
        + len(report.broken_links) * weight_broken
        + len(report.seo_issues) * weight_seo
        + len(report.sitemap_missing) * weight_sitemap
    )
    max_possible = total_jobs * max(weight_missing, weight_broken)
    score = max(0.0, 100.0 - (penalties / max_possible * 100))
    report.sync_score = round(score, 1)

    if careers_count_advertised and len(careers_jobs) < careers_count_advertised:
        report.warnings.append(
            f"Careers page advertises {careers_count_advertised} jobs but scraper collected "
            f"{len(careers_jobs)} — pagination may have been incomplete."
        )

    return report


# ─────────────────────────────────────────────────────────────────────────────
# CSV generation
# ─────────────────────────────────────────────────────────────────────────────

def make_csv(rows: list[dict], fieldnames: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def append_csv_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    """Append rows to a CSV file, creating it with headers when needed."""
    if not rows:
        return
    path.parent.mkdir(exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        if needs_header:
            writer.writeheader()
        writer.writerows(rows)


def submit_google_indexing(changes: list[dict], dry_run: bool = False) -> list[dict]:
    """
    Submit changed job URLs to Google Indexing API.

    changes rows use: {title, slug, url, type, source}
    type must be URL_UPDATED or URL_DELETED.
    """
    if not changes:
        return []

    stamp = datetime.now().isoformat(timespec="seconds")
    results: list[dict] = []

    if dry_run:
        for change in changes:
            results.append({
                "date": stamp,
                "title": change.get("title", ""),
                "slug": change.get("slug", ""),
                "url": change["url"],
                "type": change["type"],
                "source": change.get("source", ""),
                "status": "DRY_RUN",
                "ok": True,
                "response": "Skipped live Google submission during dry run.",
            })
        return results

    try:
        from google_indexing_api import load_access_token, publish
    except Exception as exc:
        message = f"Could not import google_indexing_api helper: {exc}"
        for change in changes:
            results.append({
                "date": stamp,
                "title": change.get("title", ""),
                "slug": change.get("slug", ""),
                "url": change["url"],
                "type": change["type"],
                "source": change.get("source", ""),
                "status": "ERROR",
                "ok": False,
                "response": message,
            })
        return results

    try:
        token = load_access_token()
    except BaseException as exc:
        message = f"Could not get Google access token: {exc}"
        for change in changes:
            results.append({
                "date": stamp,
                "title": change.get("title", ""),
                "slug": change.get("slug", ""),
                "url": change["url"],
                "type": change["type"],
                "source": change.get("source", ""),
                "status": "ERROR",
                "ok": False,
                "response": message,
            })
        return results

    for change in changes:
        try:
            status, response = publish(token, change["url"], change["type"])
        except Exception as exc:
            status, response = "ERROR", str(exc)
        ok = isinstance(status, int) and 200 <= status < 300
        results.append({
            "date": stamp,
            "title": change.get("title", ""),
            "slug": change.get("slug", ""),
            "url": change["url"],
            "type": change["type"],
            "source": change.get("source", ""),
            "status": status,
            "ok": ok,
            "response": response[:500],
        })
        time.sleep(0.2)

    append_csv_rows(
        GOOGLE_INDEXING_LOG_PATH,
        results,
        ["date", "title", "slug", "url", "type", "source", "status", "ok", "response"],
    )
    return results


def indexing_changes_from_report(report: SyncReport) -> list[dict]:
    changes: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(job: dict, notification_type: str, source: str) -> None:
        url = job.get("url")
        slug = job.get("slug", "")
        if not url and slug:
            url = f"{PUBLIC_BASE}/jobs/{slug}"
        if not url:
            return
        key = (url, notification_type)
        if key in seen:
            return
        seen.add(key)
        changes.append({
            "title": job.get("title", ""),
            "slug": slug,
            "url": url,
            "type": notification_type,
            "source": source,
        })

    for job in report.auto_fixed_added_jobs:
        add(job, "URL_UPDATED", "auto_fix_added")
    for job in report.auto_fixed_removed_jobs:
        add(job, "URL_DELETED", "auto_fix_removed")
    for job in report.auto_closed_jobs:
        add(job, "URL_DELETED", "auto_close")

    return changes


def google_credentials_path() -> Path | None:
    try:
        from google_indexing_api import default_credentials_path
        return default_credentials_path()
    except BaseException:
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        return Path(credentials_path) if credentials_path else None


def gsc_access_token() -> str:
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request as GoogleRequest
    except ImportError as exc:
        raise RuntimeError("Missing dependency: google-auth. Install with `python3 -m pip install google-auth`.") from exc

    credentials_path = google_credentials_path()
    if credentials_path is None:
        raise RuntimeError("No Google service account JSON found. Put one JSON file in tools/private/.")

    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=[GSC_SCOPE],
    )
    credentials.refresh(GoogleRequest())
    return credentials.token


def google_api_post(url: str, token: str, payload: dict, timeout: int = 30) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
            return response.status, json.loads(text) if text else {}
    except HTTPError as exc:
        text = exc.read().decode("utf-8")
        try:
            data = json.loads(text)
        except Exception:
            data = {"error": {"message": text[:500]}}
        return exc.code, data


def inspect_gsc_url(token: str, url: str) -> tuple[int, dict]:
    return google_api_post(
        "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
        token,
        {
            "inspectionUrl": url,
            "siteUrl": GSC_SITE_URL,
            "languageCode": "en-US",
        },
    )


def query_gsc_performance(token: str, url: str, days: int = 28) -> tuple[int, dict]:
    end = (date_type.today() - timedelta(days=2)).isoformat()
    start = (date_type.today() - timedelta(days=days + 2)).isoformat()
    site = quote(GSC_SITE_URL, safe="")
    return google_api_post(
        f"https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query",
        token,
        {
            "startDate": start,
            "endDate": end,
            "dimensions": ["page", "query"],
            "type": "web",
            "dimensionFilterGroups": [{
                "groupType": "and",
                "filters": [{
                    "dimension": "page",
                    "operator": "equals",
                    "expression": url,
                }],
            }],
            "rowLimit": 10,
            "aggregationType": "auto",
        },
    )


def parse_gsc_inspection(job: WebsiteJob, status: int, data: dict) -> dict:
    error = data.get("error", {}) if isinstance(data, dict) else {}
    result = data.get("inspectionResult", {}) if isinstance(data, dict) else {}
    index = result.get("indexStatusResult", {}) or {}
    rich = result.get("richResultsResult", {}) or {}

    user_canonical = index.get("userCanonical", "")
    google_canonical = index.get("googleCanonical", "")
    verdict = index.get("verdict", "")
    coverage = index.get("coverageState", "")
    indexing_state = index.get("indexingState", "")
    page_fetch_state = index.get("pageFetchState", "")
    robots_txt_state = index.get("robotsTxtState", "")
    last_crawl = index.get("lastCrawlTime", "")
    sitemap = "; ".join(index.get("sitemap", []) or [])
    rich_verdict = rich.get("verdict", "")
    rich_items = rich.get("detectedItems", []) or []
    rich_item_types = ", ".join(sorted({str(item.get("richResultType", "")) for item in rich_items if item.get("richResultType")}))

    indexed = verdict in {"PASS"} or "indexed" in coverage.lower()
    canonical_match = bool(user_canonical and google_canonical and user_canonical.rstrip("/") == google_canonical.rstrip("/"))

    return {
        "title": job.title,
        "slug": job.slug,
        "url": job.url,
        "status": status,
        "ok": 200 <= status < 300,
        "indexed": indexed,
        "verdict": verdict,
        "coverage_state": coverage,
        "indexing_state": indexing_state,
        "page_fetch_state": page_fetch_state,
        "robots_txt_state": robots_txt_state,
        "last_crawl_time": last_crawl,
        "user_canonical": user_canonical,
        "google_canonical": google_canonical,
        "canonical_match": canonical_match,
        "sitemap": sitemap,
        "rich_results_verdict": rich_verdict,
        "rich_result_types": rich_item_types,
        "error": error.get("message", ""),
    }


def parse_gsc_performance(job: WebsiteJob, status: int, data: dict, target_keyword: str) -> dict:
    rows = data.get("rows", []) if isinstance(data, dict) else []
    clicks = sum(float(row.get("clicks", 0)) for row in rows)
    impressions = sum(float(row.get("impressions", 0)) for row in rows)
    weighted_position = sum(float(row.get("position", 0)) * float(row.get("impressions", 0)) for row in rows)
    avg_position = round(weighted_position / impressions, 1) if impressions else 0
    ctr = round(clicks / impressions, 4) if impressions else 0
    top_query = rows[0]["keys"][1] if rows and len(rows[0].get("keys", [])) > 1 else ""
    queries = [row["keys"][1] for row in rows if len(row.get("keys", [])) > 1]
    target_parts = [part for part in re.split(r"\W+", target_keyword.lower()) if len(part) > 2]
    query_blob = " ".join(queries).lower()
    target_query_visible = bool(target_parts and all(part in query_blob for part in target_parts[:3]))

    return {
        "title": job.title,
        "slug": job.slug,
        "url": job.url,
        "status": status,
        "ok": 200 <= status < 300,
        "clicks": int(clicks),
        "impressions": int(impressions),
        "ctr": ctr,
        "position": avg_position,
        "top_query": top_query,
        "target_keyword": target_keyword,
        "target_query_visible": target_query_visible,
        "queries": "; ".join(queries[:10]),
        "error": (data.get("error", {}) if isinstance(data, dict) else {}).get("message", ""),
    }


def apply_gsc_analysis(report: SyncReport, website_jobs: list[WebsiteJob], limit: int | None = None) -> None:
    jobs = website_jobs[:limit] if limit else website_jobs
    if not jobs:
        return

    print(f"\n[GSC] Checking {len(jobs)} job URL(s) with Search Console …")
    try:
        token = gsc_access_token()
    except Exception as exc:
        message = f"Google Search Console API skipped: {exc}"
        report.warnings.append(message)
        print(f"  WARN: {message}")
        return

    ranking_by_url = {row["url"].rstrip("/"): row for row in report.ranking_readiness}

    for i, job in enumerate(jobs, 1):
        print(f"  [{i}/{len(jobs)}] {job.slug}", end=" … ", flush=True)
        target_keyword = ranking_by_url.get(job.url.rstrip("/"), {}).get("target_keyword", keyword_targets(job.title)[0])

        inspect_status, inspect_data = inspect_gsc_url(token, job.url)
        inspection = parse_gsc_inspection(job, inspect_status, inspect_data)
        report.gsc_url_inspection.append(inspection)

        perf_status, perf_data = query_gsc_performance(token, job.url)
        performance = parse_gsc_performance(job, perf_status, perf_data, target_keyword)
        report.gsc_search_performance.append(performance)

        problems: list[str] = []
        if not inspection["ok"]:
            problems.append(f"URL Inspection API error: {inspection['error'] or inspection['status']}")
        if inspection["ok"] and not inspection["indexed"]:
            problems.append(inspection["coverage_state"] or inspection["verdict"] or "Not indexed")
            report.gsc_not_indexed_jobs.append(inspection)
        if inspection["ok"] and inspection["user_canonical"] and inspection["google_canonical"] and not inspection["canonical_match"]:
            problems.append("Google-selected canonical differs from user canonical")
            report.gsc_canonical_conflicts.append(inspection)
        if inspection["ok"] and inspection["robots_txt_state"] and inspection["robots_txt_state"] not in {"ALLOWED", "ROBOTS_TXT_STATE_UNSPECIFIED"}:
            problems.append(f"Robots.txt state: {inspection['robots_txt_state']}")
        if inspection["ok"] and inspection["page_fetch_state"] and inspection["page_fetch_state"] not in {"SUCCESSFUL", "PAGE_FETCH_STATE_UNSPECIFIED"}:
            problems.append(f"Page fetch state: {inspection['page_fetch_state']}")
        if inspection["ok"] and inspection["rich_results_verdict"] and inspection["rich_results_verdict"] not in {"PASS", "VERDICT_UNSPECIFIED"}:
            problems.append(f"Rich results verdict: {inspection['rich_results_verdict']}")
            report.gsc_rich_result_issues.append(inspection)
        if inspection["indexed"] and performance["ok"] and performance["impressions"] == 0:
            problems.append("Indexed page has zero impressions in selected GSC window")
            report.gsc_zero_impression_jobs.append(performance)
        if performance["ok"] and performance["position"] and performance["position"] > 20:
            problems.append(f"Average position worse than 20 ({performance['position']})")
            report.gsc_ranking_opportunities.append(performance)
        if performance["ok"] and performance["impressions"] > 0 and not performance["target_query_visible"]:
            problems.append("Target keyword not visible in top Search Console queries")
            report.gsc_query_match_issues.append(performance)

        if problems:
            report.gsc_indexing_problems.append({
                "title": job.title,
                "url": job.url,
                "problems": problems,
            })

        print("OK" if not problems else f"{len(problems)} issue(s)")
        time.sleep(0.2)

    action_counts = [
        (len(report.gsc_not_indexed_jobs), "job URL(s) not indexed or not passing URL Inspection"),
        (len(report.gsc_canonical_conflicts), "job URL(s) where Google selected a different canonical"),
        (len(report.gsc_zero_impression_jobs), "job URL(s) with zero Search Console impressions"),
        (len(report.gsc_ranking_opportunities), "job URL(s) ranking worse than average position 20"),
        (len(report.gsc_query_match_issues), "job URL(s) missing target keyword visibility in top queries"),
        (len(report.gsc_rich_result_issues), "job URL(s) with rich result issues"),
    ]
    report.gsc_action_plan = [
        f"Fix {count} {label}"
        for count, label in action_counts
        if count
    ] or ["No GSC indexing or performance problems detected in checked URLs."]


def local_job_html(slug: str) -> str:
    candidates = [
        ROOT / "jobs" / slug / "index.html",
        ROOT / "jobs" / f"{slug}.html",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def category_link_sources(slug: str) -> list[str]:
    sources: list[str] = []
    needles = [f"/jobs/{slug}", f"https://outreachrecruitment.net/jobs/{slug}"]
    for path in sorted(ROOT.glob("*jobs-in-malta.html")):
        if path.name == "jobs-in-malta-top-15-opening-jobs.html":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(needle in text for needle in needles):
            sources.append(path.name)
    return sources


def last_indexing_status_by_url() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    if not GOOGLE_INDEXING_LOG_PATH.exists():
        return rows
    try:
        with GOOGLE_INDEXING_LOG_PATH.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                url = row.get("url", "")
                if url:
                    rows[url.rstrip("/")] = row
    except Exception:
        return {}
    return rows


def keyword_targets(title: str) -> tuple[str, str]:
    clean_title = re.sub(r"\s+", " ", title).strip()
    return f"{clean_title} jobs in Malta", f"{clean_title} job in Malta"


def schema_has_salary(schema: dict | None) -> bool:
    if not isinstance(schema, dict):
        return False
    return bool(schema.get("baseSalary"))


def apply_ranking_analysis(report: SyncReport, website_jobs: list[WebsiteJob]) -> None:
    """Build ranking-readiness, keyword, linking, content, schema, and category sections."""
    duplicate_slugs: set[str] = set()
    for item in report.duplicates:
        for key in ("url_a", "url_b"):
            slug = item.get(key, "").rstrip("/").split("/")[-1]
            if slug:
                duplicate_slugs.add(slug)

    sitemap_missing = {url.rstrip("/") for url in report.sitemap_missing}
    schema_issue_by_url = {item["url"].rstrip("/"): item["issues"] for item in report.schema_issues}
    indexing_by_url = last_indexing_status_by_url()
    category_rows: dict[str, dict] = {}

    for job in website_jobs:
        html = local_job_html(job.slug)
        text = strip_tags(html)
        text_l = re.sub(r"\s+", " ", text).lower()
        word_count = len(re.findall(r"\b\w+\b", text))

        meta_title = job.meta_title
        if not meta_title and html:
            tm = META_TITLE_RE.search(html)
            meta_title = strip_tags(tm.group(1)).strip() if tm else ""

        meta_description = job.meta_description
        if not meta_description and html:
            dm = META_DESC_RE.search(html) or META_DESC_RE2.search(html)
            meta_description = dm.group(1).strip() if dm else ""

        canonical = job.canonical
        if not canonical and html:
            cm = CANONICAL_RE.search(html)
            canonical = (cm.group(1) or cm.group(2)).strip() if cm else ""

        is_indexable = job.is_indexable and not bool(NOINDEX_RE.search(html))
        schema, local_schema_issues = validate_job_schema(html) if html else (None, ["No local job HTML found"])
        schema_issues = schema_issue_by_url.get(job.url.rstrip("/"), local_schema_issues)
        category_sources = category_link_sources(job.slug)
        last_indexing = indexing_by_url.get(job.url.rstrip("/"))
        primary_kw, secondary_kw = keyword_targets(job.title)
        haystack = " ".join([meta_title, meta_description, text]).lower()

        issues: list[str] = []
        keyword_gaps: list[str] = []
        content_gaps: list[str] = []
        link_gaps: list[str] = []
        score = 100

        status_ok = job.status in (0, 200) and bool(html or job.status == 200)
        if not status_ok:
            score -= 25
            issues.append(f"Page status not confirmed as 200 ({job.status or 'unknown'})")

        if not meta_title:
            score -= 12
            issues.append("Missing meta title")
        else:
            title_l = meta_title.lower()
            if job.title.lower() not in title_l:
                score -= 6
                keyword_gaps.append("Meta title does not include exact job title")
            if "malta" not in title_l:
                score -= 6
                keyword_gaps.append("Meta title missing Malta")
            if "job" not in title_l:
                score -= 4
                keyword_gaps.append("Meta title missing job/jobs intent")

        if not meta_description:
            score -= 10
            issues.append("Missing meta description")
        else:
            desc_l = meta_description.lower()
            if job.title.lower() not in desc_l:
                score -= 4
                keyword_gaps.append("Meta description does not include exact job title")
            if "malta" not in desc_l:
                score -= 4
                keyword_gaps.append("Meta description missing Malta")
            if "apply" not in desc_l:
                score -= 3
                keyword_gaps.append("Meta description missing apply CTA")

        if primary_kw.lower() not in haystack and secondary_kw.lower() not in haystack:
            score -= 5
            keyword_gaps.append(f"Target phrase missing: {primary_kw}")

        expected_canonical = f"{PUBLIC_BASE}/jobs/{job.slug}"
        if not canonical:
            score -= 8
            issues.append("Missing canonical")
        elif canonical.rstrip("/") != expected_canonical:
            score -= 6
            issues.append("Canonical does not match clean job URL")

        if not is_indexable:
            score -= 20
            issues.append("Page is noindex")

        if schema_issues:
            score -= min(18, 6 + len(schema_issues) * 3)
            issues.append("JobPosting schema needs fixes")

        if job.url.rstrip("/") in sitemap_missing:
            score -= 8
            issues.append("Missing from sitemap")

        if not category_sources:
            score -= 10
            link_gaps.append("Not linked from a category jobs page")

        if job.slug in duplicate_slugs:
            score -= 10
            issues.append("Possible duplicate/cannibalization risk")

        if word_count < 250:
            score -= 12
            content_gaps.append(f"Job content is very short ({word_count} words)")
        elif word_count < 450:
            score -= 6
            content_gaps.append(f"Job content could be deeper ({word_count} words)")

        required_sections = {
            "responsibilities": "Missing responsibilities section",
            "requirements": "Missing requirements section",
            "what's on offer": "Missing offer/benefits section",
            "apply": "Missing strong apply CTA",
        }
        for needle, label in required_sections.items():
            if needle not in text_l:
                score -= 4
                content_gaps.append(label)

        if not schema_has_salary(schema):
            score -= 2
            content_gaps.append("Salary/baseSalary missing or not specific")

        score = max(0, min(100, score))
        all_issues = issues + keyword_gaps + link_gaps + content_gaps
        category = job.category or "Uncategorized"
        row = {
            "title": job.title,
            "slug": job.slug,
            "url": job.url,
            "category": category,
            "score": score,
            "priority": "High" if score < 70 else "Medium" if score < 85 else "Low",
            "target_keyword": primary_kw,
            "word_count": word_count,
            "category_links": len(category_sources),
            "category_sources": ", ".join(category_sources),
            "schema_eligible": not bool(schema_issues),
            "last_indexing_status": (last_indexing or {}).get("status", "Not recorded"),
            "last_indexing_date": (last_indexing or {}).get("date", ""),
            "issues": all_issues[:10],
        }
        report.ranking_readiness.append(row)

        bucket = category_rows.setdefault(category, {"category": category, "jobs": 0, "score_total": 0, "weak_jobs": 0})
        bucket["jobs"] += 1
        bucket["score_total"] += score
        if score < 85:
            bucket["weak_jobs"] += 1

        if keyword_gaps:
            report.keyword_issues.append({
                "title": job.title,
                "url": job.url,
                "target_keyword": primary_kw,
                "issues": keyword_gaps,
            })
        if link_gaps:
            report.internal_link_issues.append({
                "title": job.title,
                "url": job.url,
                "issues": link_gaps,
            })
        if content_gaps:
            report.content_quality_issues.append({
                "title": job.title,
                "url": job.url,
                "word_count": word_count,
                "issues": content_gaps,
            })
        report.schema_eligibility.append({
            "title": job.title,
            "url": job.url,
            "eligible": not bool(schema_issues),
            "issues": schema_issues,
        })

    report.ranking_readiness.sort(key=lambda item: (item["score"], item["title"]))
    report.priority_jobs = report.ranking_readiness[:15]
    report.category_ranking = [
        {
            "category": row["category"],
            "jobs": row["jobs"],
            "average_score": round(row["score_total"] / max(row["jobs"], 1), 1),
            "weak_jobs": row["weak_jobs"],
        }
        for row in category_rows.values()
    ]
    report.category_ranking.sort(key=lambda item: (item["average_score"], item["category"]))

    action_counts = [
        (len([j for j in report.ranking_readiness if j["score"] < 70]), "high-priority job page(s) below 70/100"),
        (len(report.keyword_issues), "job page(s) with keyword targeting gaps"),
        (len(report.internal_link_issues), "job page(s) missing category-page internal links"),
        (len(report.content_quality_issues), "job page(s) needing deeper content"),
        (len([s for s in report.schema_eligibility if not s["eligible"]]), "job page(s) not fully eligible for JobPosting rich results"),
        (len(report.duplicates), "possible duplicate/cannibalization pair(s) to review"),
    ]
    report.ranking_action_plan = [
        f"Fix {count} {label}"
        for count, label in action_counts
        if count
    ] or ["All tracked ranking checks look strong this run."]


def build_csvs(report: SyncReport, website_jobs: list[WebsiteJob]) -> dict[str, str]:
    csvs: dict[str, str] = {}

    csvs["missing_jobs.csv"] = make_csv(
        [{"title": t} for t in report.missing_jobs],
        ["title"],
    )
    csvs["extra_jobs.csv"] = make_csv(
        [{"title": t} for t in report.extra_jobs],
        ["title"],
    )
    csvs["title_mismatches.csv"] = make_csv(
        report.title_mismatches,
        ["careers_title", "website_title", "similarity", "website_url"],
    )
    csvs["location_mismatches.csv"] = make_csv(
        report.location_mismatches,
        ["title", "registry_location", "website_location", "url"],
    )
    csvs["broken_links.csv"] = make_csv(
        report.broken_links,
        ["title", "url", "status"],
    )

    seo_flat = []
    for item in report.seo_issues:
        for issue in item["issues"]:
            seo_flat.append({
                "title": item["title"],
                "url": item["url"],
                "issue": issue,
            })
    csvs["seo_issues.csv"] = make_csv(seo_flat, ["title", "url", "issue"])

    csvs["duplicates.csv"] = make_csv(
        report.duplicates,
        ["title_a", "url_a", "title_b", "url_b", "similarity"],
    )
    csvs["google_indexing_submissions.csv"] = make_csv(
        report.indexing_submissions,
        ["date", "title", "slug", "url", "type", "source", "status", "ok", "response"],
    )
    ranking_rows = []
    for item in report.ranking_readiness:
        row = dict(item)
        row["issues"] = "; ".join(item.get("issues", []))
        ranking_rows.append(row)
    csvs["ranking_readiness.csv"] = make_csv(
        ranking_rows,
        [
            "title", "slug", "url", "category", "score", "priority",
            "target_keyword", "word_count", "category_links", "category_sources",
            "schema_eligible", "last_indexing_status", "last_indexing_date", "issues",
        ],
    )
    keyword_rows = []
    for item in report.keyword_issues:
        for issue in item["issues"]:
            keyword_rows.append({
                "title": item["title"],
                "url": item["url"],
                "target_keyword": item["target_keyword"],
                "issue": issue,
            })
    csvs["keyword_issues.csv"] = make_csv(keyword_rows, ["title", "url", "target_keyword", "issue"])
    content_rows = []
    for item in report.content_quality_issues:
        for issue in item["issues"]:
            content_rows.append({
                "title": item["title"],
                "url": item["url"],
                "word_count": item["word_count"],
                "issue": issue,
            })
    csvs["content_quality_issues.csv"] = make_csv(content_rows, ["title", "url", "word_count", "issue"])
    link_rows = []
    for item in report.internal_link_issues:
        for issue in item["issues"]:
            link_rows.append({"title": item["title"], "url": item["url"], "issue": issue})
    csvs["internal_link_issues.csv"] = make_csv(link_rows, ["title", "url", "issue"])
    schema_rows = []
    for item in report.schema_eligibility:
        if item["eligible"]:
            schema_rows.append({"title": item["title"], "url": item["url"], "eligible": True, "issue": ""})
        else:
            for issue in item["issues"]:
                schema_rows.append({"title": item["title"], "url": item["url"], "eligible": False, "issue": issue})
    csvs["schema_eligibility.csv"] = make_csv(schema_rows, ["title", "url", "eligible", "issue"])
    csvs["category_ranking.csv"] = make_csv(
        report.category_ranking,
        ["category", "jobs", "average_score", "weak_jobs"],
    )
    csvs["gsc_url_inspection.csv"] = make_csv(
        report.gsc_url_inspection,
        [
            "title", "slug", "url", "status", "ok", "indexed", "verdict", "coverage_state",
            "indexing_state", "page_fetch_state", "robots_txt_state", "last_crawl_time",
            "user_canonical", "google_canonical", "canonical_match", "sitemap",
            "rich_results_verdict", "rich_result_types", "error",
        ],
    )
    csvs["gsc_search_performance.csv"] = make_csv(
        report.gsc_search_performance,
        [
            "title", "slug", "url", "status", "ok", "clicks", "impressions", "ctr",
            "position", "top_query", "target_keyword", "target_query_visible", "queries", "error",
        ],
    )
    gsc_problem_rows = []
    for item in report.gsc_indexing_problems:
        for problem in item["problems"]:
            gsc_problem_rows.append({"title": item["title"], "url": item["url"], "problem": problem})
    csvs["gsc_indexing_problems.csv"] = make_csv(gsc_problem_rows, ["title", "url", "problem"])

    return csvs


# ─────────────────────────────────────────────────────────────────────────────
# Previous score (trend)
# ─────────────────────────────────────────────────────────────────────────────

def load_previous_score() -> float | None:
    """Load sync score from the most recent past report JSON."""
    today = datetime.now().strftime("%Y-%m-%d")
    reports = sorted(REPORT_DIR.glob("sync-report-*.json"), reverse=True)
    for path in reports:
        if today not in path.name:  # skip today's report
            try:
                return float(json.loads(path.read_text()).get("sync_score", 0))
            except Exception:
                pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Sync state — auto-close tracking
# ─────────────────────────────────────────────────────────────────────────────

def load_sync_state() -> dict:
    """Load persistent state for consecutive-absence tracking."""
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {"consecutive_extra": {}, "last_run": ""}


def save_sync_state(state: dict) -> None:
    state["last_run"] = datetime.now().strftime("%Y-%m-%d")
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def update_auto_close_state(extra_job_titles: list[str], state: dict) -> list[str]:
    """
    Increment consecutive-absence counter for each extra job.
    Reset counters for jobs no longer extra.
    Return titles that have hit AUTO_CLOSE_THRESHOLD.
    """
    consecutive = state.get("consecutive_extra", {})
    for title in extra_job_titles:
        consecutive[title] = consecutive.get(title, 0) + 1
    for title in list(consecutive.keys()):
        if title not in extra_job_titles:
            del consecutive[title]
    state["consecutive_extra"] = consecutive
    return [t for t, count in consecutive.items() if count >= AUTO_CLOSE_THRESHOLD]


def close_job_in_registry(title: str) -> str | None:
    """Mark a job as 'closed' in jobs_registry.json. Returns the closed slug when updated."""
    if not REGISTRY_PATH.exists():
        return None
    registry = json.loads(REGISTRY_PATH.read_text())
    closed_slug = None
    for job in registry:
        if title_similarity(job["title"], title) >= 0.75 and job.get("status") not in ("closed", "expired"):
            job["status"] = "closed"
            closed_slug = job["slug"]
    if closed_slug:
        REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    return closed_slug


# ─────────────────────────────────────────────────────────────────────────────
# Duplicate detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_duplicates(website_jobs: list[WebsiteJob]) -> list[dict]:
    """Find job cards on the website with suspiciously similar titles."""
    duplicates: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for i, job_a in enumerate(website_jobs):
        for j, job_b in enumerate(website_jobs):
            if i >= j or (i, j) in seen:
                continue
            seen.add((i, j))
            score = title_similarity(job_a.title, job_b.title)
            if DUPLICATE_THRESHOLD <= score < 1.0:
                duplicates.append({
                    "title_a": job_a.title,
                    "url_a": job_a.url,
                    "title_b": job_b.title,
                    "url_b": job_b.url,
                    "similarity": round(score, 2),
                })
    return sorted(duplicates, key=lambda x: x["similarity"], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# Urgent 404 email alert
# ─────────────────────────────────────────────────────────────────────────────

def send_urgent_404_alert(broken_links: list[dict]) -> bool:
    """Send an immediate separate email when 404s are found — don't wait for next run."""
    config = load_smtp_config()
    if {"smtp_host", "smtp_port", "smtp_user", "smtp_pass"} - set(config.keys()):
        return False

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = "".join(
        f"<tr><td>{item['title']}</td>"
        f"<td><a href='{item['url']}'>{item['url']}</a></td>"
        f"<td style='color:#c62828;font-weight:bold'>{item['status'] or 'ERR'}</td></tr>"
        for item in broken_links
    )
    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>body{{font-family:Arial,sans-serif;color:#333;max-width:700px;margin:0 auto;padding:20px}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th{{background:#b71c1c;color:white;padding:8px 10px;text-align:left}}
td{{padding:7px 10px;border-bottom:1px solid #eee}}</style>
</head><body>
<div style="background:#ffebee;border:3px solid #c62828;border-radius:10px;padding:20px;margin-bottom:20px">
  <h1 style="color:#b71c1c;margin:0">🚨 URGENT: {len(broken_links)} Broken Job Page(s)</h1>
  <p style="margin:8px 0;font-size:14px;color:#555">Detected: {date_str} Malta Time</p>
</div>
<p><b>Candidates and Google cannot reach these pages.</b> Fix immediately.</p>
<table>
<tr><th>Job Title</th><th>URL</th><th>Status</th></tr>
{rows}
</table>
<h2 style="color:#283593;margin-top:24px">🛠 How to Fix</h2>
<ol style="font-size:14px">
  <li>Check the slug in <code>tools/jobs_registry.json</code></li>
  <li>If job is filled: <code>python3 tools/expire_job.py SLUG</code></li>
  <li>Regenerate: <code>python3 tools/update_jobs_listing.py</code></li>
  <li>Deploy: <code>git add -A && git commit -m "Fix broken page" && git push origin main</code></li>
</ol>
<p style="font-size:12px;color:#999;border-top:1px solid #eee;padding-top:12px;margin-top:24px">
  Outreach Recruitment — Job Sync Agent — Urgent 404 Alert<br>
  <a href="https://outreachrecruitment.net/jobs/">outreachrecruitment.net/jobs</a>
</p>
</body></html>"""

    subject = f"🚨 URGENT: {len(broken_links)} Broken Job Page(s) — Outreach Recruitment — {date_str}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config["smtp_user"]
    msg["To"] = REPORT_RECIPIENT
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        port = int(config["smtp_port"])
        if port == 465:
            import ssl
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(config["smtp_host"], port, context=ctx) as server:
                server.login(config["smtp_user"], config["smtp_pass"])
                server.sendmail(config["smtp_user"], REPORT_RECIPIENT, msg.as_string())
        else:
            with smtplib.SMTP(config["smtp_host"], port) as server:
                server.ehlo()
                server.starttls()
                server.login(config["smtp_user"], config["smtp_pass"])
                server.sendmail(config["smtp_user"], REPORT_RECIPIENT, msg.as_string())
        print(f"  ⚠️  Urgent 404 alert sent to {REPORT_RECIPIENT}")
        return True
    except Exception as exc:
        print(f"  ERROR sending 404 alert: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Live dashboard page
# ─────────────────────────────────────────────────────────────────────────────

def generate_dashboard(report: SyncReport, state: dict) -> None:
    """Write sync-dashboard.html to project root (noindex, updated every run)."""
    score = report.sync_score
    if score == 100:
        score_color, score_label = "#2e7d32", "Fully Synced"
        status_bg, status_border = "#e8f5e9", "#2e7d32"
    elif score >= 95:
        score_color, score_label = "#558b2f", "Almost There"
        status_bg, status_border = "#f1f8e9", "#558b2f"
    elif score >= 85:
        score_color, score_label = "#f9a825", "Needs Attention"
        status_bg, status_border = "#fff3e0", "#ef6c00"
    else:
        score_color, score_label = "#c62828", "Action Required"
        status_bg, status_border = "#ffebee", "#c62828"

    def _tbl_rows_2(rows_data: list, empty_msg: str = "✅ None", cols: int = 2) -> str:
        if not rows_data:
            return f"<tr><td colspan='{cols}' style='color:#2e7d32'>{empty_msg}</td></tr>"
        return "".join(rows_data)

    missing_rows = [
        f"<tr><td>{jd['title']}</td>"
        f"<td><a href='{jd['careers_url']}' target='_blank'>View on Careers ↗</a></td></tr>"
        for jd in report.missing_jobs_detail
    ]
    extra_rows = [
        f"<tr><td>{t}</td><td style='color:#e65100'>Not on careers page</td></tr>"
        for t in report.extra_jobs
    ]
    broken_rows = [
        f"<tr><td>{bl['title']}</td>"
        f"<td><a href='{bl['url']}' target='_blank'>{bl['url']}</a></td>"
        f"<td style='color:#c62828;font-weight:bold'>{bl['status'] or 'ERR'}</td></tr>"
        for bl in report.broken_links
    ]
    dup_rows = []
    for d in report.duplicates:
        ua, ub = d["url_a"], d["url_b"]
        ta, tb = d["title_a"], d["title_b"]
        pct = int(d["similarity"] * 100)
        dup_rows.append(
            f"<tr><td><a href='{ua}' target='_blank'>{ta}</a></td>"
            f"<td><a href='{ub}' target='_blank'>{tb}</a></td>"
            f"<td>{pct}%</td></tr>"
        )
    schema_rows = [
        f"<tr><td><a href='{si['url']}' target='_blank'>{si['title']}</a></td>"
        f"<td style='color:#c62828'>{'; '.join(si['issues'][:3])}</td></tr>"
        for si in report.schema_issues[:25]
    ]
    consecutive = state.get("consecutive_extra", {})
    tracking_rows = []
    for title, count in consecutive.items():
        warn = count >= AUTO_CLOSE_THRESHOLD - 1
        status_td = (
            "<span style='color:#c62828;font-weight:bold'>⚠️ Next run: auto-close</span>"
            if warn else "Monitoring"
        )
        tracking_rows.append(
            f"<tr><td>{title}</td><td>{count}/{AUTO_CLOSE_THRESHOLD}</td>"
            f"<td>{status_td}</td></tr>"
        )
    auto_closed_rows = [
        f"<tr><td>{t}</td><td style='color:#ff6d00'>Marked closed this run</td></tr>"
        for t in report.auto_closed_this_run
    ]

    def stat(val: int, label: str, ok_is_zero: bool = True) -> str:
        cls = "ok" if (val == 0) == ok_is_zero else "warn"
        return (
            f"<div class='stat'><div class='stat-val {cls}'>{val}</div>"
            f"<div class='stat-lbl'>{label}</div></div>"
        )

    careers_count = report.careers_count_advertised or report.careers_count_scraped
    website_ok = len(report.missing_jobs) == 0 and len(report.extra_jobs) == 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Job Sync Dashboard — Outreach Recruitment</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;background:#f0f2f5;color:#1a1a2e}}
.header{{background:linear-gradient(135deg,#1a237e 0%,#283593 100%);color:white;padding:28px 32px}}
.header h1{{font-size:24px;font-weight:800}}
.header p{{font-size:13px;opacity:.75;margin-top:4px}}
.noindex-pill{{display:inline-block;background:rgba(255,255,255,.18);border-radius:4px;padding:2px 10px;font-size:11px;margin-top:8px}}
.content{{max-width:1100px;margin:24px auto;padding:0 16px}}
.card{{background:white;border-radius:12px;padding:22px 26px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
.card h2{{font-size:16px;font-weight:700;color:#283593;border-left:4px solid #3f51b5;padding-left:10px;margin-bottom:14px}}
.score-ring{{text-align:center;padding:20px 0}}
.score-num{{font-size:72px;font-weight:900;color:{score_color};line-height:1}}
.score-lbl{{font-size:20px;font-weight:600;color:{score_color};margin-top:6px}}
.progress{{background:#e0e0e0;border-radius:10px;height:20px;margin:16px 0;overflow:hidden}}
.progress-fill{{background:{score_color};width:{score}%;height:100%;border-radius:10px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(115px,1fr));gap:12px;margin:16px 0}}
.stat{{background:#f5f7ff;border-radius:10px;padding:14px 12px;text-align:center}}
.stat-val{{font-size:30px;font-weight:800;color:#1a237e}}
.stat-val.ok{{color:#2e7d32}}
.stat-val.warn{{color:#c62828}}
.stat-lbl{{font-size:11px;color:#666;margin-top:4px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:#1a237e;color:white;padding:8px 10px;text-align:left;font-size:12px;font-weight:600}}
td{{padding:8px 10px;border-bottom:1px solid #f0f0f0}}
tr:hover td{{background:#fafafa}}
a{{color:#1565c0;text-decoration:none}}
a:hover{{text-decoration:underline}}
.status-bar{{background:{status_bg};border:2px solid {status_border};border-radius:8px;padding:12px 18px;margin-bottom:16px}}
.status-bar b{{color:{score_color};font-size:16px}}
.meta{{font-size:12px;color:#888;margin-bottom:12px}}
.footer{{text-align:center;font-size:12px;color:#999;padding:24px 0}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 Job Sync Dashboard</h1>
  <p>Outreach Recruitment &nbsp;·&nbsp; Last updated: {now_str} &nbsp;·&nbsp; <a href="https://outreachrecruitment.net/jobs/" style="color:rgba(255,255,255,.8)">View Live Jobs ↗</a></p>
  <div class="noindex-pill">🔒 noindex — internal use only</div>
</div>
<div class="content">

<div class="card">
  <div class="status-bar"><b>{score_label}</b> — Sync Score {score}% as of {report.generated_at[:16]}</div>
  <div class="score-ring"><div class="score-num">{score}%</div><div class="score-lbl">{score_label}</div></div>
  <div class="progress"><div class="progress-fill"></div></div>
  <div class="stats">
    {stat(careers_count, "Careers Page", ok_is_zero=False)}
    {stat(report.website_count, "Website Jobs", ok_is_zero=False)}
    {stat(len(report.missing_jobs), "Missing")}
    {stat(len(report.extra_jobs), "Extra")}
    {stat(len(report.broken_links), "Broken")}
    {stat(len(report.seo_issues), "SEO Issues")}
    {stat(len(report.duplicates), "Duplicates")}
    {stat(len(report.schema_issues), "Schema Issues")}
  </div>
</div>

<div class="card">
  <h2>➕ Missing Jobs ({len(report.missing_jobs)})</h2>
  <p class="meta">On careers page but not on website</p>
  <table><tr><th>Job Title</th><th>Action</th></tr>
  {_tbl_rows_2(missing_rows, "✅ All careers jobs are on the website")}</table>
</div>

<div class="card">
  <h2>🗑️ Extra Jobs ({len(report.extra_jobs)})</h2>
  <p class="meta">On website but no longer on careers page</p>
  <table><tr><th>Job Title</th><th>Status</th></tr>
  {_tbl_rows_2(extra_rows, "✅ No extra jobs")}</table>
</div>

<div class="card">
  <h2>🔗 Broken Pages ({len(report.broken_links)})</h2>
  <p class="meta">Job pages returning HTTP errors — candidates cannot access these</p>
  <table><tr><th>Job Title</th><th>URL</th><th>Status</th></tr>
  {_tbl_rows_2(broken_rows, "✅ No broken pages", cols=3)}</table>
</div>

<div class="card">
  <h2>🔍 Duplicate Suspects ({len(report.duplicates)})</h2>
  <p class="meta">Jobs with very similar titles — possible duplicates (≥{int(DUPLICATE_THRESHOLD*100)}% match)</p>
  <table><tr><th>Job A</th><th>Job B</th><th>Similarity</th></tr>
  {_tbl_rows_2(dup_rows, "✅ No duplicates detected", cols=3)}</table>
</div>

<div class="card">
  <h2>📋 Schema Issues ({len(report.schema_issues)})</h2>
  <p class="meta">JSON-LD structured data problems — missing fields affect Google Jobs indexing</p>
  <table><tr><th>Job Title</th><th>Issues</th></tr>
  {_tbl_rows_2(schema_rows, "✅ All schemas pass validation")}</table>
</div>

<div class="card">
  <h2>⏳ Auto-Close Tracking ({len(consecutive)})</h2>
  <p class="meta">Jobs absent from careers page — auto-closes at {AUTO_CLOSE_THRESHOLD} consecutive checks</p>
  <table><tr><th>Job Title</th><th>Absence Count</th><th>Status</th></tr>
  {_tbl_rows_2(tracking_rows, "No jobs being tracked", cols=3)}</table>
</div>

<div class="card">
  <h2>🔒 Auto-Closed This Run ({len(report.auto_closed_this_run)})</h2>
  <p class="meta">Jobs automatically marked closed after {AUTO_CLOSE_THRESHOLD}+ consecutive absences from careers page</p>
  <table><tr><th>Job Title</th><th>Action</th></tr>
  {_tbl_rows_2(auto_closed_rows, "None auto-closed this run")}</table>
</div>

</div>
<div class="footer">
  <p>Outreach Recruitment — Job Sync Dashboard &nbsp;·&nbsp; Updated every 2 days at 08:00 Malta Time</p>
  <p style="margin-top:4px"><a href="https://outreachrecruitment.net/jobs/">outreachrecruitment.net/jobs</a> &nbsp;|&nbsp; <a href="https://outreach-recruitment-agency.careers-page.com/">Careers Platform</a></p>
  <p style="margin-top:8px;font-size:11px">⚠️ This page is excluded from search engines (noindex, nofollow). Do not share the URL publicly.</p>
</div>
</body></html>"""

    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    print(f"  Dashboard: {DASHBOARD_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
# Auto-fix — fetch missing job details from careers page
# ─────────────────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def _format_description(raw_html: str) -> str:
    """Convert HTML job description to clean plain-text with bullet formatting."""
    text = re.sub(r"<br\s*/?>", "\n", raw_html, flags=re.I)
    text = re.sub(r"<li[^>]*>", "\n- ", text, flags=re.I)
    text = re.sub(r"</li>", "", text, flags=re.I)
    text = re.sub(r"<(?:h[1-6]|p|div|section)[^>]*>", "\n\n", text, flags=re.I)
    text = re.sub(r"</(?:h[1-6]|p|div|section)>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_job_detail(uuid: str, title: str) -> dict:
    """Fetch full job details from careers page for prompt generation."""
    url = f"https://outreach-recruitment-agency.careers-page.com/jobs/{uuid}"
    try:
        html, _ = fetch(url)
    except Exception:
        return {}

    ld: dict = {}
    schema_m = re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I)
    if schema_m:
        try:
            ld = json.loads(schema_m.group(1))
        except Exception:
            pass

    # Location — city only (no ", Malta" suffix)
    city = "Malta"
    loc_data = ld.get("jobLocation", {})
    if isinstance(loc_data, dict):
        raw_city = loc_data.get("address", {}).get("addressLocality", "").strip()
        if raw_city:
            city = re.sub(r",?\s*Malta\s*$", "", raw_city, flags=re.I).strip()

    # Employment type
    et_map = {"FULL_TIME": "Full-Time", "PART_TIME": "Part-Time",
              "CONTRACTOR": "Subcontracting", "TEMPORARY": "Part-Time"}
    emp_type = et_map.get(ld.get("employmentType", "FULL_TIME"), "Full-Time")

    # Work mode
    work_mode = "On-Site"
    if ld.get("jobLocationType") == "TELECOMMUTE":
        work_mode = "Remote"
    elif re.search(r"\bhybrid\b", title, re.I):
        work_mode = "Hybrid"

    # Category
    category = ld.get("occupationalCategory", "").strip() or _guess_category(title)

    # Full description — preserve structure
    raw_desc = ld.get("description", "")
    full_description = _format_description(raw_desc) if raw_desc else ""

    return {
        "city":            city,
        "location":        f"{city}, Malta" if city != "Malta" else "Malta",
        "employment_type": emp_type,
        "work_mode":       work_mode,
        "category":        category,
        "about":           full_description[:900],
        "description":     full_description,
        "apply_url":       f"https://outreach-recruitment-agency.careers-page.com/jobs/{uuid}/apply",
    }


def _guess_category(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["chef", "waiter", "cook", "bartend", "restaurant", "sommelier", "hotel"]):
        return "Hospitality"
    if any(k in t for k in ["developer", "software", "it ", "network", "data", "cyber", "devops"]):
        return "IT & Technology"
    if any(k in t for k in ["account", "finance", "audit", "tax", "payable", "bookkeep", "payroll"]):
        return "Finance & Accounting"
    if any(k in t for k in ["nurse", "doctor", "health", "medical", "pharmacy", "therapist"]):
        return "Healthcare"
    if any(k in t for k in ["admin", "coordinator", "specialist", "assistant", "secretary", "reception"]):
        return "Administration"
    if any(k in t for k in ["plumb", "weld", "electric", "engine", "mechanic", "techni", "fabricat"]):
        return "Engineering & Maintenance"
    if any(k in t for k in ["marine", "ship", "vessel", "maritime"]):
        return "Maritime"
    if any(k in t for k in ["sales", "business develop", "account manag"]):
        return "Sales"
    if any(k in t for k in ["hr ", "human resource", "recruit", "talent"]):
        return "HR & Recruitment"
    return "General"


def _guess_industry_sector(category: str, title: str, description: str) -> tuple[str, str]:
    """Return (industry, sector) from category and description context."""
    cat = category.lower()
    desc = description.lower()
    t = title.lower()

    if "finance" in cat or "accounting" in cat:
        if any(k in desc for k in ["hotel", "hospitality", "resort"]):
            return "Hospitality", "Finance & Accounting"
        if any(k in desc for k in ["insurance", "healthcare", "claims"]):
            return "Healthcare & Insurance", "Finance & Administration"
        return "Finance & Business Services", "Finance & Accounting"
    if "it" in cat or "technology" in cat:
        return "Technology", "IT & Software Development"
    if "healthcare" in cat or "medical" in cat:
        return "Healthcare & Insurance", "Healthcare Administration"
    if "hospitality" in cat:
        return "Hospitality & Tourism", "Hotel & Food & Beverage Operations"
    if "admin" in cat:
        if any(k in desc for k in ["insurance", "healthcare", "claims", "medical"]):
            return "Healthcare & Insurance", "Administration & Operations"
        if any(k in desc for k in ["hotel", "hospitality"]):
            return "Hospitality", "Administration"
        return "Business Services", "Administration & Operations"
    if "engineering" in cat or "maintenance" in cat:
        return "Engineering & Technical Services", "Maintenance & Engineering"
    if "maritime" in cat or "marine" in t:
        return "Maritime & Shipping", "Marine Engineering"
    if "hr" in cat or "recruitment" in cat:
        return "Human Resources", "HR & Talent Acquisition"
    if "sales" in cat:
        return "Sales & Commercial", "Sales & Business Development"
    if "logistics" in cat:
        return "Logistics & Supply Chain", "Operations & Logistics"
    if "retail" in cat:
        return "Retail", "Retail Operations"
    return "Business Services", "General"


def _guess_region(city: str) -> str:
    """Map Maltese city to region."""
    city_lower = city.lower()
    north = ["mellieħa", "mellieha", "st paul", "naxxar", "mosta", "rabat", "mdina", "attard", "lija", "balzan"]
    south = ["żurrieq", "zurrieq", "birżebbuġa", "birzebbuga", "safi", "tarxien", "żejtun", "zejtun", "ghaxaq", "siggiewi"]
    harbour = ["valletta", "floriana", "msida", "gżira", "gzira", "sliema", "st julian", "ta' xbiex", "ta xbiex", "pietà", "pieta", "hamrun", "qormi"]
    central = ["birkirkara", "swieqi", "san gwann", "iklin", "santa venera"]
    paola = ["paola", "tarxien", "luqa", "gudja", "mqabba"]

    for k in north:
        if k in city_lower:
            return "Northern Malta"
    for k in south:
        if k in city_lower:
            return "Southern Malta"
    for k in paola:
        if k in city_lower:
            return "South Eastern Malta"
    for k in harbour:
        if k in city_lower:
            return "Southern Harbour Region"
    for k in central:
        if k in city_lower:
            return "Central Malta"
    return "Malta"


def _generate_ref_number(category: str) -> str:
    """Generate OR-ABBR-YEAR-NUM reference number."""
    import random
    year = datetime.now().year
    cat = category.lower()
    if "finance" in cat or "accounting" in cat:
        abbr = "FIN"
    elif "it" in cat or "technology" in cat:
        abbr = "IT"
    elif "healthcare" in cat or "medical" in cat:
        abbr = "MED"
    elif "hospitality" in cat:
        abbr = "HOSP"
    elif "admin" in cat:
        abbr = "ADMIN"
    elif "engineering" in cat or "maintenance" in cat:
        abbr = "ENG"
    elif "maritime" in cat or "marine" in cat:
        abbr = "MAR"
    elif "hr" in cat or "recruitment" in cat:
        abbr = "HR"
    elif "sales" in cat:
        abbr = "SALES"
    elif "logistics" in cat:
        abbr = "LOG"
    else:
        abbr = "GEN"
    return f"OR-{abbr}-{year}-{random.randint(100, 999)}"


def generate_job_prompt(detail: dict) -> str:
    """Build the complete job-seo-generator prompt for a missing job."""
    today = datetime.now().strftime("%Y-%m-%d")
    return (
        f"Use job-seo-generator to create a complete Google Jobs-ready, SEO-optimized,\n"
        f"AI-search-friendly job package. Apply all skill rules including SERP competitor\n"
        f"analysis, semantic SEO/entities, job category mapping, candidate keyword\n"
        f"questions, freshness/update rules, conversion optimization, duplicate content\n"
        f"prevention, and structured data safety rules.\n\n"
        f"Generate all sections from the job-output-template.md.\n\n"
        f"After generating all sections, also:\n"
        f"- Add the new job card to jobs/index.html in the opening-jobs-grid as the first card\n"
        f"- Increase the open positions count by 1 in all counter labels\n"
        f"- Read the current count from the file before incrementing — do not hard-code a number\n\n"
        f"---\n\n"
        f"Job title: {detail['title']}\n"
        f"Location city: {detail['city']}\n"
        f"Location region: {detail['region']}\n"
        f"Country: Malta\n"
        f"Employment type: {detail['employment_type']}\n"
        f"Salary range: Not specified\n"
        f"Salary currency: EUR\n"
        f"Date posted: {today}\n"
        f"Expiry date / valid through: {datetime.now().year}-12-31\n"
        f"Reference number: {detail['ref_number']}\n"
        f"Application URL: {detail['apply_url']}\n"
        f"Application method: Apply online\n"
        f"Remote status: {detail['work_mode']}\n"
        f"Industry: {detail['industry']}\n"
        f"Sector: {detail['sector']}\n\n"
        f"Job description:\n{detail['description']}\n\n"
        f"Label: Job Target\n"
        f"Value: Residents in Malta & Europeans"
    )


def auto_fix(report: SyncReport) -> None:
    """
    Auto-add jobs missing from website, auto-expire jobs no longer on careers page.
    Commits and pushes changes to GitHub when done.
    """
    today = date_type.today().isoformat()

    # ── Add missing jobs ──────────────────────────────────────────────────────
    if report.missing_jobs_detail:
        print(f"\n  [Auto-Fix] Fetching details for {len(report.missing_jobs_detail)} missing job(s) …")
        csv_rows = []
        existing_slugs: set[str] = set()
        if REGISTRY_PATH.exists():
            existing_slugs = {j["slug"] for j in json.loads(REGISTRY_PATH.read_text())}

        for jd in report.missing_jobs_detail:
            print(f"    {jd['title']} …", end=" ", flush=True)
            details = fetch_job_detail(jd["uuid"], jd["title"])
            if not details:
                print("FAILED — skipping")
                continue

            slug = _slugify(jd["title"])
            counter = 2
            base = slug
            while slug in existing_slugs:
                slug = f"{base}-{counter}"
                counter += 1
            existing_slugs.add(slug)

            csv_rows.append({
                "title":           jd["title"],
                "slug":            slug,
                "category":        "",
                "location":        details["location"],
                "employment_type": details["employment_type"],
                "work_mode":       details["work_mode"],
                "apply_url":       details["apply_url"],
                "about":           details["about"],
                "responsibilities": "",
                "requirements":    "",
                "offer":           "",
                "closing":         "",
                "keywords":        "",
                "date":            today,
                "valid_through":   "2026-12-31",
                "featured":        "true",
            })
            print(f"OK ({details['location']}, {details['employment_type']})")
            time.sleep(DELAY)

        if csv_rows:
            tmp_csv = ROOT / "tools" / "_autofix_import.csv"
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)
            tmp_csv.write_text(buf.getvalue(), encoding="utf-8")

            print(f"\n    Running add_jobs_from_csv.py …")
            result = subprocess.run(
                ["python3", str(ROOT / "tools" / "add_jobs_from_csv.py"), str(tmp_csv)],
                cwd=str(ROOT), capture_output=True, text=True,
            )
            tmp_csv.unlink(missing_ok=True)
            if result.returncode == 0:
                report.auto_fixed_added = [r["title"] for r in csv_rows]
                report.auto_fixed_added_jobs = [
                    {
                        "title": r["title"],
                        "slug": r["slug"],
                        "url": f"{PUBLIC_BASE}/jobs/{r['slug']}",
                    }
                    for r in csv_rows
                ]
                print(f"    Added {len(report.auto_fixed_added)} job(s) ✓")
            else:
                print(f"    ERROR: {result.stderr[:400]}")

    # ── Expire extra jobs ─────────────────────────────────────────────────────
    if report.extra_jobs and REGISTRY_PATH.exists():
        print(f"\n  [Auto-Fix] Expiring {len(report.extra_jobs)} extra job(s) …")
        registry = json.loads(REGISTRY_PATH.read_text())
        active_jobs = [j for j in registry if j.get("status") != "expired"]

        for extra_title in report.extra_jobs:
            best_slug, best_score = None, 0.0
            for job in active_jobs:
                score = title_similarity(extra_title, job["title"])
                if score > best_score:
                    best_score = score
                    best_slug = job["slug"]

            if best_slug and best_score >= 0.7:
                print(f"    Expiring: {extra_title} ({best_slug}) …", end=" ", flush=True)
                result = subprocess.run(
                    ["python3", str(ROOT / "tools" / "expire_job.py"), best_slug],
                    cwd=str(ROOT), capture_output=True, text=True,
                )
                if result.returncode == 0:
                    report.auto_fixed_removed.append(extra_title)
                    report.auto_fixed_removed_jobs.append({
                        "title": extra_title,
                        "slug": best_slug,
                        "url": f"{PUBLIC_BASE}/jobs/{best_slug}",
                    })
                    print("OK ✓")
                else:
                    print(f"ERROR: {result.stderr[:100]}")
            else:
                print(f"    Could not match '{extra_title}' in registry — skipping")

    # ── Git commit + push ─────────────────────────────────────────────────────
    if report.auto_fixed_added or report.auto_fixed_removed:
        parts = []
        if report.auto_fixed_added:
            parts.append(f"add {len(report.auto_fixed_added)} job(s)")
        if report.auto_fixed_removed:
            parts.append(f"expire {len(report.auto_fixed_removed)} job(s)")
        commit_msg = f"[Auto-Sync] {'; '.join(parts)}"

        print(f"\n  [Auto-Fix] Committing and pushing …")
        subprocess.run(["git", "add", "-A"], cwd=str(ROOT), capture_output=True)
        commit = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        if commit.returncode == 0:
            push = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=str(ROOT), capture_output=True, text=True,
            )
            status = "Pushed to GitHub ✓" if push.returncode == 0 else f"Push failed: {push.stderr[:100]}"
            print(f"  {status}")
        else:
            print(f"  Commit failed: {commit.stderr[:200]}")


# ─────────────────────────────────────────────────────────────────────────────
# HTML email body
# ─────────────────────────────────────────────────────────────────────────────

def _rows(items: list[str], limit: int = 50) -> str:
    shown = items[:limit]
    html = "".join(f"<li>{unescape(s)}</li>" for s in shown)
    if len(items) > limit:
        html += f"<li><em>…and {len(items) - limit} more (see CSV attachment)</em></li>"
    return f"<ul>{html}</ul>" if html else "<p style='color:#888'>None</p>"


def _mismatch_table(rows: list[dict], cols: list[tuple[str, str]]) -> str:
    if not rows:
        return "<p style='color:#888'>None</p>"
    headers = "".join(f"<th>{label}</th>" for _, label in cols)
    body = ""
    for row in rows[:50]:
        cells = "".join(f"<td>{row.get(key, '')}</td>" for key, _ in cols)
        body += f"<tr>{cells}</tr>"
    return f"<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px'><tr>{headers}</tr>{body}</table>"


def _build_indexing_section(submissions: list[dict]) -> str:
    if not submissions:
        return "<p style='color:#2e7d32'>No changed job URLs needed Google submission this run.</p>"

    rows = ""
    for item in submissions[:50]:
        ok = item.get("ok")
        status_color = "#2e7d32" if ok else "#c62828"
        rows += (
            f"<tr>"
            f"<td><a href='{item.get('url', '')}'>{item.get('title') or item.get('slug') or item.get('url', '')}</a></td>"
            f"<td>{item.get('type', '')}</td>"
            f"<td>{item.get('source', '')}</td>"
            f"<td style='color:{status_color};font-weight:700'>{item.get('status', '')}</td>"
            f"</tr>"
        )

    return (
        f"<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
        f"<tr><th>Job URL</th><th>Notification</th><th>Source</th><th>Status</th></tr>"
        f"{rows}</table>"
    )


def _build_ranking_table(rows: list[dict], limit: int = 15) -> str:
    if not rows:
        return "<p style='color:#2e7d32'>No ranking issues detected.</p>"
    body = ""
    for item in rows[:limit]:
        color = "#c62828" if item["score"] < 70 else "#e65100" if item["score"] < 85 else "#2e7d32"
        issue_text = "; ".join(item.get("issues", [])[:3])
        body += (
            f"<tr>"
            f"<td><a href='{item['url']}'>{item['title']}</a></td>"
            f"<td>{item.get('category', '')}</td>"
            f"<td style='color:{color};font-weight:800'>{item['score']}/100</td>"
            f"<td>{item.get('target_keyword', '')}</td>"
            f"<td>{issue_text}</td>"
            f"</tr>"
        )
    return (
        "<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
        "<tr><th>Job</th><th>Category</th><th>Score</th><th>Target Keyword</th><th>Top Fixes</th></tr>"
        f"{body}</table>"
    )


def _build_category_ranking_table(rows: list[dict]) -> str:
    if not rows:
        return "<p style='color:#888'>No category ranking data available.</p>"
    body = ""
    for item in rows:
        color = "#c62828" if item["average_score"] < 70 else "#e65100" if item["average_score"] < 85 else "#2e7d32"
        body += (
            f"<tr><td>{item['category']}</td><td>{item['jobs']}</td>"
            f"<td style='color:{color};font-weight:800'>{item['average_score']}/100</td>"
            f"<td>{item['weak_jobs']}</td></tr>"
        )
    return (
        "<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
        "<tr><th>Category</th><th>Jobs</th><th>Average Score</th><th>Weak Jobs</th></tr>"
        f"{body}</table>"
    )


def _build_issue_summary_table(rows: list[dict], empty: str, limit: int = 20) -> str:
    if not rows:
        return f"<p style='color:#2e7d32'>{empty}</p>"
    body = ""
    for item in rows[:limit]:
        issues = "; ".join(item.get("issues", [])[:4])
        extra = ""
        if "target_keyword" in item:
            extra = f"<br><span style='color:#666;font-size:12px'>{item['target_keyword']}</span>"
        if "word_count" in item:
            extra = f"<br><span style='color:#666;font-size:12px'>{item['word_count']} words</span>"
        body += f"<tr><td><a href='{item['url']}'>{item['title']}</a>{extra}</td><td>{issues}</td></tr>"
    return (
        "<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
        "<tr><th>Job</th><th>Issues</th></tr>"
        f"{body}</table>"
    )


def _build_gsc_problem_table(rows: list[dict], empty: str, limit: int = 25) -> str:
    if not rows:
        return f"<p style='color:#2e7d32'>{empty}</p>"
    body = ""
    for item in rows[:limit]:
        problems = "; ".join(item.get("problems", [])[:4]) if "problems" in item else (
            item.get("coverage_state") or item.get("top_query") or item.get("rich_results_verdict") or ""
        )
        body += f"<tr><td><a href='{item['url']}'>{item['title']}</a></td><td>{problems}</td></tr>"
    return (
        "<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
        "<tr><th>Job</th><th>Google Signal</th></tr>"
        f"{body}</table>"
    )


def _build_gsc_performance_table(rows: list[dict], empty: str, limit: int = 25) -> str:
    if not rows:
        return f"<p style='color:#2e7d32'>{empty}</p>"
    body = ""
    for item in rows[:limit]:
        body += (
            f"<tr><td><a href='{item['url']}'>{item['title']}</a></td>"
            f"<td>{item.get('impressions', 0)}</td><td>{item.get('clicks', 0)}</td>"
            f"<td>{item.get('position', 0)}</td><td>{item.get('top_query', '')}</td></tr>"
        )
    return (
        "<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
        "<tr><th>Job</th><th>Impr.</th><th>Clicks</th><th>Avg Pos.</th><th>Top Query</th></tr>"
        f"{body}</table>"
    )


SCORE_COLOR = {
    "excellent": "#2e7d32",
    "good": "#558b2f",
    "warning": "#f9a825",
    "critical": "#c62828",
}


def _build_prompts_section(prompts: list[str]) -> str:
    if not prompts:
        return ""
    cards = ""
    for i, prompt in enumerate(prompts, 1):
        # Extract title from prompt for the header
        title_m = re.search(r"^Job title:\s*(.+)$", prompt, re.M)
        title = title_m.group(1).strip() if title_m else f"Job {i}"
        escaped = prompt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cards += (
            f'<div style="margin-bottom:24px;border:1px solid #bbdefb;border-radius:8px;overflow:hidden">'
            f'<div style="background:#1565c0;color:white;padding:10px 16px;font-weight:700;font-size:14px">'
            f'📋 Prompt {i} — {title}</div>'
            f'<pre style="margin:0;padding:16px;background:#1e1e2e;color:#cdd6f4;font-size:12px;'
            f'line-height:1.6;overflow-x:auto;white-space:pre-wrap;word-break:break-word;font-family:monospace">'
            f'{escaped}</pre>'
            f'</div>'
        )
    return (
        f'<div class="card">'
        f'<h2>📋 Claude Prompts — Ready to Paste ({len(prompts)})</h2>'
        f'<p style="color:#555;margin-top:-4px;font-size:13px">'
        f'Copy each prompt below and paste it directly into Claude to generate the full job page.</p>'
        f'{cards}'
        f'</div>'
    )


def _build_schema_section(schema_issues: list[dict]) -> str:
    if not schema_issues:
        return "<p style='color:#2e7d32'>✅ All structured data schemas pass validation</p>"
    rows = ""
    for item in schema_issues[:30]:
        issue_str = "; ".join(item["issues"][:4])
        rows += f"<tr><td><a href='{item['url']}'>{item['title']}</a></td><td style='color:#c62828'>{issue_str}</td></tr>"
    return (
        f"<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
        f"<tr><th>Job Title</th><th>Issues</th></tr>{rows}</table>"
    )


def _progress_bar(score: float, color: str) -> str:
    filled = int(score)
    empty = 100 - filled
    return (
        f"<div style='background:#e0e0e0;border-radius:8px;height:18px;width:100%;max-width:500px;margin:8px 0'>"
        f"<div style='background:{color};width:{filled}%;height:18px;border-radius:8px;transition:width 0.3s'></div>"
        f"</div>"
    )


def _trend_badge(current: float, previous: float | None) -> str:
    if previous is None:
        return "<span style='color:#888;font-size:13px'>First run</span>"
    diff = round(current - previous, 1)
    if diff > 0:
        return f"<span style='color:#2e7d32;font-size:14px'>▲ +{diff}% vs last run ({previous}%)</span>"
    elif diff < 0:
        return f"<span style='color:#c62828;font-size:14px'>▼ {diff}% vs last run ({previous}%)</span>"
    else:
        return f"<span style='color:#555;font-size:13px'>= No change vs last run ({previous}%)</span>"


def build_html_email(report: SyncReport) -> str:
    date_str = report.generated_at[:10]
    score = report.sync_score
    careers_count = report.careers_count_advertised or report.careers_count_scraped
    indexing_total = len(report.indexing_submissions)
    indexing_success = sum(1 for item in report.indexing_submissions if item.get("ok"))
    indexing_failed = indexing_total - indexing_success
    avg_ranking_score = (
        round(sum(item["score"] for item in report.ranking_readiness) / len(report.ranking_readiness), 1)
        if report.ranking_readiness else 0
    )
    high_priority_rank_jobs = len([item for item in report.ranking_readiness if item["score"] < 70])
    gsc_checked = len(report.gsc_url_inspection)
    gsc_problem_count = len(report.gsc_indexing_problems)
    gsc_checked = len(report.gsc_url_inspection)
    gsc_problem_count = len(report.gsc_indexing_problems)

    if score == 100:
        score_color = SCORE_COLOR["excellent"]
        score_label = "✅ Fully Synced"
        alert_box = "<div style='background:#e8f5e9;border:2px solid #2e7d32;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#2e7d32;font-size:16px'>✅ All Jobs Synced — Website perfectly mirrors the careers page.</b></div>"
    elif score >= 95:
        score_color = SCORE_COLOR["good"]
        score_label = "Almost There"
        alert_box = "<div style='background:#f1f8e9;border:2px solid #558b2f;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#33691e;font-size:16px'>🟡 Almost perfect — small differences to fix.</b></div>"
    elif score >= 85:
        score_color = SCORE_COLOR["warning"]
        score_label = "Needs Attention"
        alert_box = "<div style='background:#fff3e0;border:2px solid #ef6c00;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#bf360c;font-size:16px'>⚠️ Sync issues detected — action needed.</b></div>"
    else:
        score_color = SCORE_COLOR["critical"]
        score_label = "Action Required"
        alert_box = "<div style='background:#ffebee;border:2px solid #c62828;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#b71c1c;font-size:16px'>🚨 Significant differences — website is out of sync!</b></div>"

    # Goal gap
    total_issues = len(report.missing_jobs) + len(report.extra_jobs) + len(report.broken_links)
    if score == 100:
        goal_text = "🎯 Goal achieved — website is 100% in sync with the careers page!"
        goal_color = "#2e7d32"
    else:
        gap_items = []
        if report.missing_jobs:
            gap_items.append(f"{len(report.missing_jobs)} job(s) to add")
        if report.extra_jobs:
            gap_items.append(f"{len(report.extra_jobs)} job(s) to remove")
        if report.broken_links:
            gap_items.append(f"{len(report.broken_links)} broken page(s)")
        if report.seo_issues:
            gap_items.append(f"{len(report.seo_issues)} SEO issue(s)")
        if report.sitemap_missing:
            gap_items.append(f"{len(report.sitemap_missing)} sitemap entry(ies) missing")
        goal_text = f"🎯 To reach 100%: fix {' + '.join(gap_items)}"
        goal_color = "#e65100"

    # Auto-fix summary
    auto_fix_html = ""
    if report.auto_fixed_added or report.auto_fixed_removed:
        items = []
        if report.auto_fixed_added:
            items.append(f"<li>✅ Auto-added {len(report.auto_fixed_added)} job(s): "
                         + ", ".join(f"<b>{t}</b>" for t in report.auto_fixed_added) + "</li>")
        if report.auto_fixed_removed:
            items.append(f"<li>🗑️ Auto-expired {len(report.auto_fixed_removed)} job(s): "
                         + ", ".join(f"<b>{t}</b>" for t in report.auto_fixed_removed) + "</li>")
        auto_fix_html = (
            f"<div style='background:#e3f2fd;border:2px solid #1565c0;padding:15px;border-radius:8px;margin:20px 0'>"
            f"<b style='color:#0d47a1'>🤖 Auto-Fix Applied:</b><ul style='margin:8px 0'>{''.join(items)}</ul>"
            f"<p style='margin:4px 0;font-size:13px;color:#555'>Changes committed and pushed to GitHub automatically.</p>"
            f"</div>"
        )

    # Quick fix commands (only if there are issues and no auto-fix ran)
    quick_fix_html = ""
    if not (report.auto_fixed_added or report.auto_fixed_removed) and (report.missing_jobs or report.extra_jobs):
        cmds = []
        if report.missing_jobs:
            cmds.append("# Add missing jobs automatically:<br>python3 tools/job_sync_agent.py --auto-fix --no-seo")
        if report.extra_jobs:
            slugs = " ".join(_slugify(t) for t in report.extra_jobs[:5])
            cmds.append(f"# Or expire extra jobs manually:<br>python3 tools/expire_job.py {slugs}")
        cmd_html = "<br><br>".join(f"<code style='background:#263238;color:#80cbc4;padding:10px;display:block;border-radius:4px;font-size:13px'>{c}</code>" for c in cmds)
        quick_fix_html = (
            f"<h2>⚡ Quick Fix Commands</h2>"
            f"<p>Run these in Terminal from the project folder:</p>"
            f"{cmd_html}"
        )

    # Actions list
    actions = []
    if report.missing_jobs:
        actions.append(f"Add <b>{len(report.missing_jobs)}</b> missing job(s) to website")
    if report.extra_jobs:
        actions.append(f"Remove <b>{len(report.extra_jobs)}</b> closed job(s) from website")
    if report.title_mismatches:
        actions.append(f"Review <b>{len(report.title_mismatches)}</b> possible title mismatch(es)")
    if report.location_mismatches:
        actions.append(f"Verify <b>{len(report.location_mismatches)}</b> location discrepancy(ies)")
    if report.broken_links:
        actions.append(f"Fix <b>{len(report.broken_links)}</b> broken page(s)")
    if report.seo_issues:
        actions.append(f"Fix <b>{len(report.seo_issues)}</b> SEO issue(s)")
    if report.sitemap_missing:
        actions.append(f"Update sitemap — <b>{len(report.sitemap_missing)}</b> page(s) missing")
    if report.duplicates:
        actions.append(f"Review <b>{len(report.duplicates)}</b> possible duplicate job(s)")
    if report.schema_issues:
        actions.append(f"Fix <b>{len(report.schema_issues)}</b> structured data schema issue(s)")
    if report.auto_closed_this_run:
        actions.append(f"<b>{len(report.auto_closed_this_run)}</b> job(s) auto-closed this run — verify and push")
    if indexing_failed:
        actions.append(f"Review <b>{indexing_failed}</b> failed Google Indexing API submission(s)")
    if high_priority_rank_jobs:
        actions.append(f"Improve <b>{high_priority_rank_jobs}</b> high-priority ranking page(s) below 70/100")
    if not actions:
        actions = ["No action required — everything is in sync! 🎉"]
    actions_html = "".join(f"<li style='margin:6px 0'>{a}</li>" for a in actions)

    # Missing jobs table with careers page links
    missing_html = ""
    if report.missing_jobs_detail:
        rows = ""
        for jd in report.missing_jobs_detail:
            rows += f"<tr><td>{jd['title']}</td><td><a href='{jd['careers_url']}' style='color:#1565c0'>View on Careers Page ↗</a></td></tr>"
        missing_html = (
            f"<table border='1' cellpadding='6' style='border-collapse:collapse;font-size:13px;width:100%'>"
            f"<tr><th>Job Title</th><th>Careers Page Link</th></tr>{rows}</table>"
        )
    else:
        missing_html = "<p style='color:#2e7d32'>✅ None — all careers page jobs are on the website</p>"

    # SEO section
    seo_rows_html = ""
    for item in report.seo_issues[:30]:
        issues_str = "; ".join(item["issues"])
        item_url = item["url"]
        item_title = item["title"]
        seo_rows_html += f"<tr><td><a href='{item_url}'>{item_title}</a></td><td style='color:#c62828'>{issues_str}</td></tr>"

    if not report.seo_issues and report.website_count > 0 and len(report.broken_links) == 0:
        seo_section_html = "<p style='color:#888'>SEO check skipped — run <code>python3 tools/job_sync_agent.py</code> for full check.</p>"
    elif report.seo_issues:
        seo_section_html = (
            f"<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px;width:100%'>"
            f"<tr><th>Job Title</th><th>Issues</th></tr>{seo_rows_html}</table>"
        )
    else:
        seo_section_html = "<p style='color:#2e7d32'>✅ No SEO issues found</p>"

    sitemap_html = _rows(report.sitemap_missing) if report.sitemap_missing else "<p style='color:#2e7d32'>✅ All job pages are in the sitemap</p>"

    warnings_html = ""
    if report.warnings:
        wlist = "".join(f"<li>{w}</li>" for w in report.warnings)
        warnings_html = f"<h3 style='color:#e65100'>⚠️ Warnings</h3><ul>{wlist}</ul>"

    count_diff = report.website_count - careers_count
    count_diff_str = f"+{count_diff}" if count_diff > 0 else str(count_diff)
    count_diff_color = "#2e7d32" if count_diff == 0 else "#c62828"

    # Auto-closed section (built outside f-string to avoid backslash in expression)
    if report.auto_closed_this_run:
        _ac_items = "".join(f"<li><b>{t}</b> — set to status: closed in registry</li>" for t in report.auto_closed_this_run)
        _ac_cmd = "python3 tools/update_jobs_listing.py &amp;&amp; git add -A &amp;&amp; git commit -m 'Auto-close filled jobs' &amp;&amp; git push origin main"
        auto_closed_section_html = (
            f"<div class='card'><h2>🔒 Auto-Closed This Run ({len(report.auto_closed_this_run)})</h2>"
            f"<p style='color:#555;margin-top:-4px;font-size:13px'>Jobs absent from careers page for {AUTO_CLOSE_THRESHOLD}+ consecutive checks — automatically marked closed on website</p>"
            f"<ul>{_ac_items}</ul>"
            f"<p style='font-size:13px;color:#666'>Run <code>{_ac_cmd}</code> to deploy.</p></div>"
        )
    else:
        auto_closed_section_html = ""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background: #fafafa; }}
  .card {{ background: white; border-radius: 10px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
  h1 {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; margin-top: 0; }}
  h2 {{ color: #283593; margin-top: 0; border-left: 4px solid #3f51b5; padding-left: 10px; }}
  h3 {{ color: #37474f; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  th {{ background: #1a237e; color: white; padding: 8px 10px; text-align: left; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #e8e8e8; }}
  tr:nth-child(even) td {{ background: #f9f9f9; }}
  .score-big {{ font-size: 52px; font-weight: 900; color: {score_color}; line-height: 1; }}
  .score-label {{ font-size: 18px; color: {score_color}; font-weight: bold; margin-left: 8px; }}
  .stat-grid {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 16px 0; }}
  .stat {{ background: #f5f7ff; border-radius: 8px; padding: 14px 18px; min-width: 110px; text-align: center; }}
  .stat-num {{ font-size: 28px; font-weight: 800; color: #1a237e; display: block; }}
  .stat-num.red {{ color: #c62828; }}
  .stat-num.green {{ color: #2e7d32; }}
  .stat-label {{ font-size: 11px; color: #666; display: block; margin-top: 2px; }}
  ul li {{ margin: 5px 0; }}
  a {{ color: #1565c0; }}
  code {{ font-family: monospace; }}
  .footer {{ margin-top: 30px; padding-top: 16px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #999; }}
  .goal-box {{ background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%); border-left: 5px solid {score_color}; padding: 14px 18px; border-radius: 0 8px 8px 0; margin: 16px 0; }}
</style>
</head>
<body>

<div class="card">
<h1>📋 Job Sync Report — Outreach Recruitment</h1>
<p style="color:#666;margin-top:-8px">Generated: {report.generated_at} &nbsp;|&nbsp; <a href="https://outreachrecruitment.net/jobs/">outreachrecruitment.net/jobs</a> &nbsp;|&nbsp; <a href="https://outreachrecruitment.net/sync-dashboard.html" style="color:#1565c0;font-weight:bold">📊 Live Dashboard ↗</a></p>

{alert_box}
{auto_fix_html}

<div class="goal-box">
  <p style="margin:0;font-size:15px;color:{goal_color}"><b>{goal_text}</b></p>
  {_progress_bar(score, score_color)}
  <div style="display:flex;justify-content:space-between;font-size:12px;color:#888;max-width:500px">
    <span>0%</span><span>50%</span><span>100% Goal</span>
  </div>
  <p style="margin:8px 0 0">{_trend_badge(score, report.previous_score)}</p>
</div>
</div>

<div class="card">
<h2>📊 Summary</h2>
<div class="stat-grid">
  <div class="stat"><span class="stat-num">{careers_count}</span><span class="stat-label">Careers Page Jobs</span></div>
  <div class="stat"><span class="stat-num {'red' if count_diff != 0 else 'green'}">{report.website_count}</span><span class="stat-label">Website Jobs</span></div>
  <div class="stat"><span class="stat-num {'red' if count_diff != 0 else 'green'}" style="font-size:20px">{count_diff_str}</span><span class="stat-label">Count Difference</span></div>
  <div class="stat"><span class="stat-num {'red' if report.missing_jobs else 'green'}">{len(report.missing_jobs)}</span><span class="stat-label">Missing</span></div>
  <div class="stat"><span class="stat-num {'red' if report.extra_jobs else 'green'}">{len(report.extra_jobs)}</span><span class="stat-label">Extra</span></div>
  <div class="stat"><span class="stat-num {'red' if report.broken_links else 'green'}">{len(report.broken_links)}</span><span class="stat-label">Broken Pages</span></div>
  <div class="stat"><span class="stat-num {'red' if report.seo_issues else 'green'}">{len(report.seo_issues)}</span><span class="stat-label">SEO Issues</span></div>
  <div class="stat"><span class="stat-num {'red' if report.sitemap_missing else 'green'}">{len(report.sitemap_missing)}</span><span class="stat-label">Sitemap Missing</span></div>
  <div class="stat"><span class="stat-num {'red' if report.duplicates else 'green'}">{len(report.duplicates)}</span><span class="stat-label">Duplicates</span></div>
  <div class="stat"><span class="stat-num {'red' if report.schema_issues else 'green'}">{len(report.schema_issues)}</span><span class="stat-label">Schema Issues</span></div>
  <div class="stat"><span class="stat-num {'red' if indexing_failed else 'green'}">{indexing_total}</span><span class="stat-label">Google Submitted</span></div>
  <div class="stat"><span class="stat-num {'red' if avg_ranking_score < 70 else 'green' if avg_ranking_score >= 85 else ''}">{avg_ranking_score}</span><span class="stat-label">Avg Ranking Score</span></div>
  <div class="stat"><span class="stat-num {'red' if high_priority_rank_jobs else 'green'}">{high_priority_rank_jobs}</span><span class="stat-label">Ranking Priority</span></div>
  <div class="stat"><span class="stat-num {'red' if gsc_problem_count else 'green'}">{gsc_problem_count}</span><span class="stat-label">GSC Problems</span></div>
  <div class="stat"><span class="stat-num">{gsc_checked}</span><span class="stat-label">GSC Checked</span></div>
</div>
<p style="font-size:13px;color:#666;margin:4px 0">
  <b>Sync Score:</b> <span style="font-size:22px;font-weight:900;color:{score_color}">{score}%</span>
  <span class="score-label">{score_label}</span>
</p>
</div>

<div class="card">
<h2>✅ Actions Required</h2>
<ol style="margin:0;padding-left:20px">{actions_html}</ol>
</div>

<div class="card">
<h2>🏆 Ranking Action Plan</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Prioritized SEO work to help every job page rank for job-title searches in Malta</p>
{_rows(report.ranking_action_plan)}
</div>

<div class="card">
<h2>🔎 Google Search Console Action Plan</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Google-side indexing, canonical, rich result, and search performance blockers from the Search Console API</p>
{_rows(report.gsc_action_plan or ["GSC was not run for this report. Use a normal run or add --with-gsc to dry-run."])}
</div>

<div class="card">
<h2>🚫 Jobs Not Indexed by Google ({len(report.gsc_not_indexed_jobs)})</h2>
{_build_gsc_problem_table(report.gsc_not_indexed_jobs, "No not-indexed jobs found in checked URLs")}
</div>

<div class="card">
<h2>🧭 Canonical Conflicts ({len(report.gsc_canonical_conflicts)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Google-selected canonical differs from the page's declared canonical</p>
{_build_gsc_problem_table(report.gsc_canonical_conflicts, "No Google canonical conflicts found")}
</div>

<div class="card">
<h2>📉 Indexed but Zero Impressions ({len(report.gsc_zero_impression_jobs)})</h2>
{_build_gsc_performance_table(report.gsc_zero_impression_jobs, "No zero-impression jobs found in checked URLs")}
</div>

<div class="card">
<h2>📍 Ranking Opportunities: Position Worse Than 20 ({len(report.gsc_ranking_opportunities)})</h2>
{_build_gsc_performance_table(report.gsc_ranking_opportunities, "No checked jobs are ranking worse than average position 20")}
</div>

<div class="card">
<h2>🔤 Query Match Gaps ({len(report.gsc_query_match_issues)})</h2>
{_build_gsc_performance_table(report.gsc_query_match_issues, "Target keywords are visible in top queries for checked jobs")}
</div>

<div class="card">
<h2>⭐ GSC Rich Results Issues ({len(report.gsc_rich_result_issues)})</h2>
{_build_gsc_problem_table(report.gsc_rich_result_issues, "No rich result issues found in checked URLs")}
</div>

<div class="card">
<h2>📈 Top Jobs Needing Ranking Work ({len(report.priority_jobs)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Lowest ranking-readiness scores across metadata, schema, content, links, duplicates, sitemap, and indexing history</p>
{_build_ranking_table(report.priority_jobs)}
</div>

<div class="card">
<h2>🧭 Category Ranking Report</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Average ranking readiness by job category</p>
{_build_category_ranking_table(report.category_ranking)}
</div>

<div class="card">
<h2>🎯 Keyword Target Gaps ({len(report.keyword_issues)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Checks target phrases like “Job Title jobs in Malta”, “Job Title job in Malta”, and apply-intent copy</p>
{_build_issue_summary_table(report.keyword_issues, "No keyword targeting gaps detected")}
</div>

<div class="card">
<h2>🔗 Internal Link Coverage ({len(report.internal_link_issues)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Flags jobs not linked from category hub pages such as hospitality, construction, finance, IT, sales, insurance, or marine</p>
{_build_issue_summary_table(report.internal_link_issues, "Every job has category-page link coverage")}
</div>

<div class="card">
<h2>✍️ Content Quality Checks ({len(report.content_quality_issues)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Checks depth, responsibilities, requirements, offer/benefits, salary/baseSalary, and apply CTA</p>
{_build_issue_summary_table(report.content_quality_issues, "No content quality gaps detected")}
</div>

<div class="card">
<h2>⭐ JobPosting Rich Results Eligibility</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Schema eligibility for Google Jobs rich result consideration</p>
{_build_issue_summary_table([item for item in report.schema_eligibility if not item["eligible"]], "All checked jobs are eligible by tracked schema rules")}
</div>

{quick_fix_html}

<div class="card">
<h2>➕ Jobs to Add ({len(report.missing_jobs)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">On careers page but <b>missing</b> from website — run <code>--auto-fix</code> to add automatically</p>
{missing_html}
</div>

{_build_prompts_section(report.missing_prompts)}

<div class="card">
<h2>🗑️ Jobs to Remove ({len(report.extra_jobs)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">On website but <b>no longer active</b> on careers page</p>
{_rows(report.extra_jobs) if report.extra_jobs else "<p style='color:#2e7d32'>✅ No extra jobs</p>"}
</div>

<div class="card">
<h2>📝 Title Differences ({len(report.title_mismatches)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Similar but non-matching titles between platforms</p>
{_mismatch_table(report.title_mismatches, [
    ("careers_title", "Careers Page Title"),
    ("website_title", "Website Title"),
    ("similarity", "Match %"),
    ("website_url", "URL"),
]) if report.title_mismatches else "<p style='color:#2e7d32'>✅ All titles match</p>"}
</div>

<div class="card">
<h2>🔗 Broken Pages ({len(report.broken_links)})</h2>
{_mismatch_table(report.broken_links, [
    ("title", "Job Title"),
    ("url", "URL"),
    ("status", "HTTP Status"),
]) if report.broken_links else "<p style='color:#2e7d32'>✅ No broken pages</p>"}
</div>

<div class="card">
<h2>🔍 SEO Issues ({len(report.seo_issues)})</h2>
{seo_section_html}
</div>

<div class="card">
<h2>🗺️ Sitemap Issues ({len(report.sitemap_missing)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Job pages not listed in sitemap — Google may not index them</p>
{sitemap_html}
</div>

{f'<div class="card">{warnings_html}</div>' if report.warnings else ""}

<div class="card">
<h2>🔍 Duplicate Suspects ({len(report.duplicates)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Jobs with very similar titles on the website — may confuse candidates or Google</p>
{_mismatch_table(report.duplicates, [
    ("title_a", "Job A"),
    ("title_b", "Job B"),
    ("similarity", "Match"),
    ("url_a", "URL A"),
]) if report.duplicates else "<p style='color:#2e7d32'>✅ No duplicates detected</p>"}
</div>

<div class="card">
<h2>📋 Schema Issues ({len(report.schema_issues)})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">JSON-LD structured data problems — missing fields affect how Google Jobs displays these listings</p>
{_build_schema_section(report.schema_issues)}
</div>

{auto_closed_section_html}

<div class="card">
<h2>📡 Google Indexing API ({indexing_total})</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Changed job URLs submitted through the connected Search Console service account. Successful: <b style="color:#2e7d32">{indexing_success}</b>; failed: <b style="color:#c62828">{indexing_failed}</b>.</p>
{_build_indexing_section(report.indexing_submissions)}
</div>

<div class="card">
<h2>💡 SEO Action Plan</h2>
<p style="color:#555;margin-top:-4px;font-size:13px">Concrete steps to improve search visibility and Google Jobs indexing</p>
<table border="1" cellpadding="7" style="border-collapse:collapse;font-size:13px;width:100%">
<tr><th style="width:30px">#</th><th>Action</th><th>Priority</th><th>Impact</th></tr>
<tr><td>1</td><td><b>Canonical tags</b> — Each job page must have exactly ONE <code>&lt;link rel="canonical"&gt;</code> pointing to its own URL. Duplicate or mismatched canonicals split authority and confuse Google.<br><code style="font-size:11px;color:#555">Fix: run <b>python3 tools/fix_canonical.py</b> then push.</code></td><td style="color:#c62828">🔴 High</td><td>Google ranking, de-duplication</td></tr>
<tr><td>2</td><td><b>Meta description length</b> — Keep between 120–155 characters. Too short wastes SERP space; too long gets cut. Descriptions should include the job title, city, and a call-to-action keyword like "Apply now".</td><td style="color:#e65100">🟠 Medium</td><td>Click-through rate</td></tr>
<tr><td>3</td><td><b>Meta title format</b> — Ideal pattern: <em>Job Title in City, Malta | Outreach Recruitment</em> (max 60 chars). Verify every page follows this pattern.</td><td style="color:#e65100">🟠 Medium</td><td>SERP visibility</td></tr>
<tr><td>4</td><td><b>JSON-LD schema</b> — All pages need <code>validThrough</code>, <code>employmentType</code>, and <code>identifier</code> fields filled. Missing fields reduce Google Jobs eligibility. Run <code>python3 tools/fix_jobposting_schema.py</code> if needed.</td><td style="color:#e65100">🟠 Medium</td><td>Google Jobs listings</td></tr>
<tr><td>5</td><td><b>Sitemap freshness + Indexing API</b> — Whenever jobs are added, updated, closed, or removed, regenerate <code>sitemaps/sitemap-jobs.xml</code> and submit changed URLs through the connected Search Console bot. This report now records those Google API submissions.</td><td style="color:#2e7d32">🟢 Low</td><td>Indexing speed</td></tr>
<tr><td>6</td><td><b>Duplicate job titles</b> — {len(report.duplicates)} duplicate suspects found this run (e.g. "Bartender" vs "Bartenders"). Merge or differentiate these pages — two near-identical pages compete against each other in Google.</td><td style="color:#2e7d32">🟢 Low</td><td>Keyword cannibalization</td></tr>
<tr><td>7</td><td><b>Internal linking</b> — Add links from category hub pages (e.g. hospitality-jobs-in-malta.html) to individual job pages. This distributes PageRank to new job pages faster.</td><td style="color:#2e7d32">🟢 Low</td><td>Crawl budget, authority</td></tr>
</table>
</div>

<div class="card">
<h2>📎 CSV Attachments</h2>
<ul style="margin:0">
  <li>missing_jobs.csv — {len(report.missing_jobs)} jobs to add</li>
  <li>extra_jobs.csv — {len(report.extra_jobs)} jobs to remove</li>
  <li>title_mismatches.csv — {len(report.title_mismatches)} entries</li>
  <li>broken_links.csv — {len(report.broken_links)} pages</li>
  <li>seo_issues.csv — {len(report.seo_issues)} issues</li>
  <li>duplicates.csv — {len(report.duplicates)} duplicate suspects</li>
  <li>google_indexing_submissions.csv — {len(report.indexing_submissions)} submissions this run</li>
  <li>ranking_readiness.csv — {len(report.ranking_readiness)} job ranking scores</li>
  <li>keyword_issues.csv — {len(report.keyword_issues)} jobs with keyword gaps</li>
  <li>internal_link_issues.csv — {len(report.internal_link_issues)} jobs missing category links</li>
  <li>content_quality_issues.csv — {len(report.content_quality_issues)} jobs needing content work</li>
  <li>schema_eligibility.csv — {len(report.schema_eligibility)} rich result checks</li>
  <li>category_ranking.csv — {len(report.category_ranking)} category summaries</li>
  <li>gsc_url_inspection.csv — {len(report.gsc_url_inspection)} URL Inspection checks</li>
  <li>gsc_search_performance.csv — {len(report.gsc_search_performance)} Search Analytics rows</li>
  <li>gsc_indexing_problems.csv — {len(report.gsc_indexing_problems)} Google-side problem groups</li>
</ul>
</div>

<div class="footer">
  <p>Outreach Recruitment — Job Sync Agent | Runs every day at 08:00 Malta Time</p>
  <p>
    Careers Platform: <a href="https://outreach-recruitment-agency.careers-page.com/">outreach-recruitment-agency.careers-page.com</a> &nbsp;|&nbsp;
    Website: <a href="https://outreachrecruitment.net/jobs/">outreachrecruitment.net/jobs</a> &nbsp;|&nbsp;
    <a href="https://outreachrecruitment.net/sync-dashboard.html">📊 Live Dashboard</a>
  </p>
</div>

</body>
</html>"""
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Markdown report (local save)
# ─────────────────────────────────────────────────────────────────────────────

def build_markdown_report(report: SyncReport) -> str:
    score = report.sync_score
    status = "Fully Synced" if score == 100 else "Needs Attention" if score >= 75 else "Critical"
    indexing_total = len(report.indexing_submissions)
    indexing_success = sum(1 for item in report.indexing_submissions if item.get("ok"))
    indexing_failed = indexing_total - indexing_success
    avg_ranking_score = (
        round(sum(item["score"] for item in report.ranking_readiness) / len(report.ranking_readiness), 1)
        if report.ranking_readiness else 0
    )
    high_priority_rank_jobs = len([item for item in report.ranking_readiness if item["score"] < 70])
    gsc_checked = len(report.gsc_url_inspection)
    gsc_problem_count = len(report.gsc_indexing_problems)
    lines = [
        f"# Job Sync Report — {report.generated_at[:10]}",
        "",
        f"Generated: {report.generated_at}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        "|---|---|",
        f"| Careers Page Jobs | {report.careers_count_advertised or report.careers_count_scraped} |",
        f"| Careers Jobs Scraped | {report.careers_count_scraped} |",
        f"| Website Jobs | {report.website_count} |",
        f"| **Sync Score** | **{score}% — {status}** |",
        f"| Missing from Website | {len(report.missing_jobs)} |",
        f"| Extra on Website | {len(report.extra_jobs)} |",
        f"| Title Mismatches | {len(report.title_mismatches)} |",
        f"| Location Mismatches | {len(report.location_mismatches)} |",
        f"| Broken Links | {len(report.broken_links)} |",
        f"| SEO Issues | {len(report.seo_issues)} |",
        f"| Sitemap Missing | {len(report.sitemap_missing)} |",
        f"| Possible Duplicates | {len(report.duplicates)} |",
        f"| Schema Issues | {len(report.schema_issues)} |",
        f"| Google Indexing Submitted | {indexing_total} |",
        f"| Google Indexing Successful | {indexing_success} |",
        f"| Google Indexing Failed | {indexing_failed} |",
        f"| Average Ranking Readiness | {avg_ranking_score}/100 |",
        f"| High-Priority Ranking Jobs | {high_priority_rank_jobs} |",
        f"| GSC URLs Checked | {gsc_checked} |",
        f"| GSC Problem Groups | {gsc_problem_count} |",
        "",
        "## Jobs to Add (Missing from Website)",
        "",
    ]
    lines.extend([f"- {t}" for t in report.missing_jobs] or ["- None"])

    lines.extend(["", "## Jobs to Remove (Extra on Website)", ""])
    lines.extend([f"- {t}" for t in report.extra_jobs] or ["- None"])

    lines.extend(["", "## Title Differences", ""])
    if report.title_mismatches:
        lines.append("| Careers Title | Website Title | Similarity |")
        lines.append("|---|---|---|")
        for m in report.title_mismatches:
            lines.append(f"| {m['careers_title']} | {m['website_title']} | {m['similarity']} |")
    else:
        lines.append("- None")

    lines.extend(["", "## Location Differences", ""])
    if report.location_mismatches:
        for m in report.location_mismatches:
            lines.append(f"- **{m['title']}**: registry=`{m['registry_location']}` vs website=`{m['website_location']}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Broken Links", ""])
    lines.extend([f"- [{m['title']}]({m['url']}) — HTTP {m['status']}" for m in report.broken_links] or ["- None"])

    lines.extend(["", "## SEO Issues", ""])
    if report.seo_issues:
        for item in report.seo_issues:
            lines.append(f"- **{item['title']}** (`{item['url']}`): {'; '.join(item['issues'])}")
    else:
        lines.append("- None (or check skipped)")

    lines.extend(["", "## Sitemap Issues", ""])
    lines.extend([f"- {url}" for url in report.sitemap_missing] or ["- None"])

    lines.extend(["", "## Possible Duplicate Jobs", ""])
    if report.duplicates:
        lines.append("| Job A | Job B | Similarity |")
        lines.append("|---|---|---|")
        for item in report.duplicates:
            lines.append(
                f"| [{item['title_a']}]({item['url_a']}) | "
                f"[{item['title_b']}]({item['url_b']}) | {item['similarity']} |"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Google Indexing API", ""])
    if report.indexing_submissions:
        lines.append("| URL | Type | Source | Status |")
        lines.append("|---|---|---|---|")
        for item in report.indexing_submissions:
            lines.append(
                f"| [{item.get('title') or item.get('slug') or item['url']}]({item['url']}) | "
                f"{item['type']} | {item.get('source', '')} | {item['status']} |"
            )
    else:
        lines.append("- No changed job URLs needed Google submission this run.")

    lines.extend(["", "## Ranking Action Plan", ""])
    lines.extend([f"{i+1}. {item}" for i, item in enumerate(report.ranking_action_plan)] or ["- None"])

    lines.extend(["", "## Google Search Console Action Plan", ""])
    lines.extend([f"{i+1}. {item}" for i, item in enumerate(report.gsc_action_plan)] or ["- GSC was not run for this report."])

    lines.extend(["", "## Jobs Not Indexed by Google", ""])
    if report.gsc_not_indexed_jobs:
        for item in report.gsc_not_indexed_jobs[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})**: {item.get('coverage_state') or item.get('verdict')}")
    else:
        lines.append("- None found in checked URLs")

    lines.extend(["", "## Canonical Conflicts", ""])
    if report.gsc_canonical_conflicts:
        for item in report.gsc_canonical_conflicts[:30]:
            lines.append(
                f"- **[{item['title']}]({item['url']})**: user `{item.get('user_canonical')}` vs Google `{item.get('google_canonical')}`"
            )
    else:
        lines.append("- None found")

    lines.extend(["", "## Indexed but Zero Impressions", ""])
    if report.gsc_zero_impression_jobs:
        for item in report.gsc_zero_impression_jobs[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})**: target `{item['target_keyword']}`")
    else:
        lines.append("- None found in checked URLs")

    lines.extend(["", "## Ranking Opportunities from GSC", ""])
    if report.gsc_ranking_opportunities:
        for item in report.gsc_ranking_opportunities[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})**: avg position {item['position']}, top query `{item['top_query']}`")
    else:
        lines.append("- None found in checked URLs")

    lines.extend(["", "## Query Match Gaps from GSC", ""])
    if report.gsc_query_match_issues:
        for item in report.gsc_query_match_issues[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})**: target `{item['target_keyword']}`, top query `{item['top_query']}`")
    else:
        lines.append("- None found in checked URLs")

    lines.extend(["", "## Top Jobs Needing Ranking Work", ""])
    if report.priority_jobs:
        lines.append("| Job | Category | Score | Target Keyword | Top Fixes |")
        lines.append("|---|---|---|---|---|")
        for item in report.priority_jobs:
            lines.append(
                f"| [{item['title']}]({item['url']}) | {item['category']} | {item['score']}/100 | "
                f"{item['target_keyword']} | {'; '.join(item.get('issues', [])[:3])} |"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Category Ranking Report", ""])
    if report.category_ranking:
        lines.append("| Category | Jobs | Average Score | Weak Jobs |")
        lines.append("|---|---|---|---|")
        for item in report.category_ranking:
            lines.append(f"| {item['category']} | {item['jobs']} | {item['average_score']}/100 | {item['weak_jobs']} |")
    else:
        lines.append("- None")

    lines.extend(["", "## Keyword Target Gaps", ""])
    if report.keyword_issues:
        for item in report.keyword_issues[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})** — target `{item['target_keyword']}`: {'; '.join(item['issues'])}")
    else:
        lines.append("- None")

    lines.extend(["", "## Internal Link Coverage", ""])
    if report.internal_link_issues:
        for item in report.internal_link_issues[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})**: {'; '.join(item['issues'])}")
    else:
        lines.append("- All jobs have category-page link coverage")

    lines.extend(["", "## Content Quality Checks", ""])
    if report.content_quality_issues:
        for item in report.content_quality_issues[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})** — {item['word_count']} words: {'; '.join(item['issues'])}")
    else:
        lines.append("- None")

    lines.extend(["", "## JobPosting Rich Results Eligibility", ""])
    ineligible = [item for item in report.schema_eligibility if not item["eligible"]]
    if ineligible:
        for item in ineligible[:30]:
            lines.append(f"- **[{item['title']}]({item['url']})**: {'; '.join(item['issues'])}")
    else:
        lines.append("- All checked jobs are eligible by tracked schema rules")

    if report.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend([f"- {w}" for w in report.warnings])

    lines.extend(["", "## Actions Required", ""])
    actions = []
    if report.missing_jobs:
        actions.append(f"Add {len(report.missing_jobs)} missing job(s) to website")
    if report.extra_jobs:
        actions.append(f"Remove {len(report.extra_jobs)} closed job(s) from website")
    if report.title_mismatches:
        actions.append(f"Review {len(report.title_mismatches)} possible title mismatch(es)")
    if report.location_mismatches:
        actions.append(f"Verify {len(report.location_mismatches)} location discrepancy(ies)")
    if report.broken_links:
        actions.append(f"Fix {len(report.broken_links)} broken page(s)")
    if report.seo_issues:
        actions.append(f"Fix {len(report.seo_issues)} SEO issue(s)")
    if report.sitemap_missing:
        actions.append(f"Update sitemap — {len(report.sitemap_missing)} page(s) missing")
    if report.duplicates:
        actions.append(f"Review {len(report.duplicates)} possible duplicate job(s)")
    if report.schema_issues:
        actions.append(f"Fix {len(report.schema_issues)} structured data schema issue(s)")
    if indexing_failed:
        actions.append(f"Review {indexing_failed} failed Google Indexing API submission(s)")
    if high_priority_rank_jobs:
        actions.append(f"Improve {high_priority_rank_jobs} high-priority ranking page(s) below 70/100")
    if not actions:
        actions = ["No action required — everything is in sync!"]
    lines.extend([f"{i+1}. {a}" for i, a in enumerate(actions)])

    return "\n".join(lines) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# Email sending
# ─────────────────────────────────────────────────────────────────────────────

def load_smtp_config() -> dict:
    config = {}
    if CONFIG_PATH.exists():
        try:
            config = json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    # Environment variables override
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS"):
        val = os.environ.get(key)
        if val:
            config[key.lower()] = val
    return config


def send_email(report: SyncReport, html_body: str, csvs: dict[str, str]) -> bool:
    config = load_smtp_config()
    required = {"smtp_host", "smtp_port", "smtp_user", "smtp_pass"}
    missing_keys = required - set(config.keys())
    if missing_keys:
        print(f"  SKIP: Missing SMTP config: {missing_keys}")
        print(f"  Set these in {CONFIG_PATH} or as environment variables.")
        return False

    date_str = report.generated_at[:10]
    score = report.sync_score
    status = "✅ All Synced" if score == 100 else f"⚠️ {score}% — Action Required"
    subject = f"Job Sync Report — Outreach Recruitment — {date_str} — {status}"

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = config["smtp_user"]
    msg["To"] = REPORT_RECIPIENT

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)

    for filename, content in csvs.items():
        part = MIMEApplication(content.encode("utf-8"), Name=filename)
        part["Content-Disposition"] = f'attachment; filename="{filename}"'
        msg.attach(part)

    try:
        port = int(config["smtp_port"])
        if port == 465:
            import ssl
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(config["smtp_host"], port, context=ctx) as server:
                server.login(config["smtp_user"], config["smtp_pass"])
                server.sendmail(config["smtp_user"], REPORT_RECIPIENT, msg.as_string())
        else:
            with smtplib.SMTP(config["smtp_host"], port) as server:
                server.ehlo()
                server.starttls()
                server.login(config["smtp_user"], config["smtp_pass"])
                server.sendmail(config["smtp_user"], REPORT_RECIPIENT, msg.as_string())
        print(f"  Email sent to {REPORT_RECIPIENT}")
        return True
    except Exception as exc:
        print(f"  ERROR sending email: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Save reports
# ─────────────────────────────────────────────────────────────────────────────

def save_reports(report: SyncReport, md: str, csvs: dict[str, str]) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(exist_ok=True)
    stamp = report.generated_at[:10]
    md_path = REPORT_DIR / f"sync-report-{stamp}.md"
    json_path = REPORT_DIR / f"sync-report-{stamp}.json"

    md_path.write_text(md, encoding="utf-8")

    data = {
        "generated_at": report.generated_at,
        "careers_count_advertised": report.careers_count_advertised,
        "careers_count_scraped": report.careers_count_scraped,
        "website_count": report.website_count,
        "sync_score": report.sync_score,
        "missing_jobs": report.missing_jobs,
        "extra_jobs": report.extra_jobs,
        "title_mismatches": report.title_mismatches,
        "location_mismatches": report.location_mismatches,
        "broken_links": report.broken_links,
        "seo_issues": report.seo_issues,
        "sitemap_missing": report.sitemap_missing,
        "warnings": report.warnings,
        "duplicates": report.duplicates,
        "schema_issues": report.schema_issues,
        "auto_closed_this_run": report.auto_closed_this_run,
        "auto_closed_jobs": report.auto_closed_jobs,
        "auto_fixed_added_jobs": report.auto_fixed_added_jobs,
        "auto_fixed_removed_jobs": report.auto_fixed_removed_jobs,
        "indexing_submissions": report.indexing_submissions,
        "ranking_readiness": report.ranking_readiness,
        "priority_jobs": report.priority_jobs,
        "keyword_issues": report.keyword_issues,
        "internal_link_issues": report.internal_link_issues,
        "content_quality_issues": report.content_quality_issues,
        "category_ranking": report.category_ranking,
        "schema_eligibility": report.schema_eligibility,
        "ranking_action_plan": report.ranking_action_plan,
        "gsc_url_inspection": report.gsc_url_inspection,
        "gsc_search_performance": report.gsc_search_performance,
        "gsc_indexing_problems": report.gsc_indexing_problems,
        "gsc_canonical_conflicts": report.gsc_canonical_conflicts,
        "gsc_not_indexed_jobs": report.gsc_not_indexed_jobs,
        "gsc_zero_impression_jobs": report.gsc_zero_impression_jobs,
        "gsc_ranking_opportunities": report.gsc_ranking_opportunities,
        "gsc_query_match_issues": report.gsc_query_match_issues,
        "gsc_rich_result_issues": report.gsc_rich_result_issues,
        "gsc_action_plan": report.gsc_action_plan,
    }
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save CSVs too
    for filename, content in csvs.items():
        (REPORT_DIR / filename).write_text(content, encoding="utf-8")

    return md_path, json_path


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(report: SyncReport) -> None:
    print("\n" + "=" * 60)
    print(f"  SYNC SCORE: {report.sync_score}%")
    print("=" * 60)
    print(f"  Careers page: {report.careers_count_advertised} advertised, {report.careers_count_scraped} scraped")
    print(f"  Website:      {report.website_count} jobs")
    print(f"  Missing jobs: {len(report.missing_jobs)}")
    if report.missing_jobs:
        for t in report.missing_jobs[:10]:
            print(f"    + {t}")
        if len(report.missing_jobs) > 10:
            print(f"    … and {len(report.missing_jobs) - 10} more")
    print(f"  Extra jobs:   {len(report.extra_jobs)}")
    if report.extra_jobs:
        for t in report.extra_jobs[:10]:
            print(f"    - {t}")
    print(f"  Title diffs:  {len(report.title_mismatches)}")
    print(f"  Location diffs: {len(report.location_mismatches)}")
    print(f"  Broken links: {len(report.broken_links)}")
    print(f"  SEO issues:   {len(report.seo_issues)}")
    print(f"  Sitemap missing: {len(report.sitemap_missing)}")
    if report.warnings:
        print(f"\n  WARNINGS:")
        for w in report.warnings:
            print(f"    ! {w}")
    print("=" * 60)


def main() -> int:
    args = sys.argv[1:]
    no_email = "--no-email" in args or "--dry-run" in args
    no_seo   = "--no-seo"   in args or "--dry-run" in args
    dry_run  = "--dry-run"  in args
    do_fix   = "--auto-fix" in args
    with_gsc = "--with-gsc" in args
    no_gsc = "--no-gsc" in args
    gsc_limit = None
    for i, arg in enumerate(args):
        if arg.startswith("--gsc-limit="):
            gsc_limit = int(arg.split("=", 1)[1])
        elif arg == "--gsc-limit" and i + 1 < len(args):
            gsc_limit = int(args[i + 1])

    print("=" * 60)
    print("  Outreach Recruitment — Job Sync Agent")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Load persistent state for auto-close tracking
    sync_state = load_sync_state()
    print(f"\n  State loaded — tracking {len(sync_state.get('consecutive_extra', {}))} job(s) for auto-close")

    # Step 1: Scrape careers page
    print("\n[1/5] Scraping careers page …")
    careers_jobs, careers_count = scrape_careers_page()
    print(f"  Collected {len(careers_jobs)} jobs (advertised: {careers_count})")

    # Step 2: Scrape public website
    print("\n[2/5] Scraping public website …")
    website_jobs = scrape_public_website()
    print(f"  Found {len(website_jobs)} job cards")

    # Step 3: SEO + broken link checks (includes schema validation)
    if not no_seo:
        run_seo_checks(website_jobs)
    else:
        print("\n[3/5] SEO checks skipped (--no-seo / --dry-run)")

    # Step 4: Sitemap check
    print("\n[4/5] Checking sitemap …")
    if not dry_run:
        sitemap_urls = fetch_sitemap_urls()
        print(f"  Found {len(sitemap_urls)} job URLs in sitemap")
    else:
        sitemap_urls = set()
        print("  Sitemap check skipped (--dry-run)")

    # Step 5: Build report (duplicates + schema issues included)
    print("\n[5/5] Building report …")
    report = build_report(careers_jobs, careers_count, website_jobs, sitemap_urls, skip_seo=no_seo)

    print_summary(report)
    if report.duplicates:
        print(f"\n  Duplicate suspects: {len(report.duplicates)}")
        for d in report.duplicates[:5]:
            print(f"    '{d['title_a']}' ≈ '{d['title_b']}' ({int(d['similarity']*100)}%)")
    if report.schema_issues:
        print(f"\n  Schema issues: {len(report.schema_issues)} job(s)")

    # Step 5b: Urgent 404 alert — send immediately, don't wait for scheduled report
    if report.broken_links and not no_email:
        print(f"\n  🚨 {len(report.broken_links)} broken page(s) — sending urgent 404 alert …")
        send_urgent_404_alert(report.broken_links)

    # Step 5c: Auto-close check — update state, close jobs that hit threshold
    if not dry_run:
        jobs_to_close = update_auto_close_state(report.extra_jobs, sync_state)
        if jobs_to_close:
            print(f"\n  [Auto-Close] {len(jobs_to_close)} job(s) hit {AUTO_CLOSE_THRESHOLD}-check threshold:")
            for title in jobs_to_close:
                print(f"    Closing: {title} …", end=" ", flush=True)
                closed_slug = close_job_in_registry(title)
                if closed_slug:
                    report.auto_closed_this_run.append(title)
                    report.auto_closed_jobs.append({
                        "title": title,
                        "slug": closed_slug,
                        "url": f"{PUBLIC_BASE}/jobs/{closed_slug}",
                    })
                    print("updated in registry ✓")
                else:
                    print("not found in registry")
            if report.auto_closed_this_run:
                print(f"  Run python3 tools/update_jobs_listing.py && git add -A && git commit -m 'Auto-close filled jobs' && git push origin main")
        save_sync_state(sync_state)
        print(f"  State saved — tracking {len(sync_state.get('consecutive_extra', {}))} extra job(s)")

    # Step 5d: Fetch full details + generate prompts for missing jobs
    if report.missing_jobs_detail and not dry_run:
        print(f"\n  Fetching details for {len(report.missing_jobs_detail)} missing job(s) …")
        for jd in report.missing_jobs_detail:
            print(f"    {jd['title']} …", end=" ", flush=True)
            detail = fetch_job_detail(jd["uuid"], jd["title"])
            if detail:
                industry, sector = _guess_industry_sector(
                    detail["category"], jd["title"], detail["description"]
                )
                prompt_data = {
                    "title":           jd["title"],
                    "city":            detail["city"],
                    "region":          _guess_region(detail["city"]),
                    "employment_type": detail["employment_type"],
                    "work_mode":       detail["work_mode"],
                    "apply_url":       detail["apply_url"],
                    "industry":        industry,
                    "sector":          sector,
                    "description":     detail["description"],
                    "ref_number":      _generate_ref_number(detail["category"]),
                }
                report.missing_prompts.append(generate_job_prompt(prompt_data))
                print("OK")
            else:
                print("FAILED")
            time.sleep(DELAY)

    # Step 6 (optional): Auto-fix
    if do_fix and (report.missing_jobs or report.extra_jobs):
        print("\n[Auto-Fix] Starting …")
        auto_fix(report)
        print("\n  Re-scanning after auto-fix …")
        website_jobs2 = scrape_public_website()
        report2 = build_report(careers_jobs, careers_count, website_jobs2, sitemap_urls, skip_seo=True)
        report2.auto_fixed_added = report.auto_fixed_added
        report2.auto_fixed_removed = report.auto_fixed_removed
        report2.auto_fixed_added_jobs = report.auto_fixed_added_jobs
        report2.auto_fixed_removed_jobs = report.auto_fixed_removed_jobs
        report2.previous_score = report.sync_score
        report2.auto_closed_this_run = report.auto_closed_this_run
        report2.auto_closed_jobs = report.auto_closed_jobs
        report = report2
        print_summary(report)
    elif do_fix:
        print("\n[Auto-Fix] Nothing to fix — already in sync!")

    gsc_jobs = website_jobs2 if do_fix and (report.auto_fixed_added or report.auto_fixed_removed) and "website_jobs2" in locals() else website_jobs
    if not no_gsc and (not dry_run or with_gsc):
        apply_gsc_analysis(report, gsc_jobs, limit=gsc_limit)
    elif dry_run and not with_gsc:
        report.gsc_action_plan = ["GSC skipped during dry run. Run with --with-gsc to test Search Console API."]
        print("\n[GSC] Skipped during dry run. Add --with-gsc to test Search Console API.")
    elif no_gsc:
        report.gsc_action_plan = ["GSC skipped by --no-gsc."]
        print("\n[GSC] Skipped by --no-gsc.")

    indexing_changes = indexing_changes_from_report(report)
    if indexing_changes:
        print(f"\n[Google Indexing] Submitting {len(indexing_changes)} changed URL(s) …")
        report.indexing_submissions = submit_google_indexing(indexing_changes, dry_run=dry_run)
        ok_count = sum(1 for row in report.indexing_submissions if row.get("ok"))
        fail_count = len(report.indexing_submissions) - ok_count
        print(f"  Google Indexing: {ok_count} successful, {fail_count} failed")
    else:
        print("\n[Google Indexing] No changed job URLs to submit.")

    # Generate HTML + CSVs
    html_body = build_html_email(report)
    md_body = build_markdown_report(report)
    csvs = build_csvs(report, website_jobs)

    # Save locally
    md_path, json_path = save_reports(report, md_body, csvs)
    print(f"\n  Markdown report: {md_path}")
    print(f"  JSON report:     {json_path}")
    print(f"  CSVs saved to:   {REPORT_DIR}/")

    # Save HTML preview
    html_path = REPORT_DIR / f"sync-report-{report.generated_at[:10]}.html"
    html_path.write_text(html_body, encoding="utf-8")
    print(f"  HTML preview:    {html_path}")

    # Send email
    if not no_email:
        print(f"\n  Sending email to {REPORT_RECIPIENT} …")
        send_email(report, html_body, csvs)
    else:
        print(f"\n  Email skipped. To send manually, remove --no-email / --dry-run flag.")

    return 0 if report.sync_score == 100.0 else 1


if __name__ == "__main__":
    sys.exit(main())
