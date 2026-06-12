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
from datetime import datetime
from difflib import SequenceMatcher
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
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

REPORT_RECIPIENT = "sbarakat@outreachrecruitment.net"
DELAY = 0.8  # seconds between requests

STATE_PATH = ROOT / "tools" / "sync_state.json"
DASHBOARD_PATH = ROOT / "sync-dashboard.html"
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

    # Ready-to-paste Claude prompts for each missing job
    missing_prompts: list[str] = field(default_factory=list)

    # New feature fields
    duplicates: list[dict] = field(default_factory=list)
    schema_issues: list[dict] = field(default_factory=list)
    auto_closed_this_run: list[str] = field(default_factory=list)


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
CANONICAL_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']*)["\']', re.I)
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
        job.canonical = cm.group(1).strip() if cm else ""

        job.is_indexable = not bool(NOINDEX_RE.search(html))

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
<p style="color:#666;margin-top:-8px">Generated: {report.generated_at} &nbsp;|&nbsp; <a href="https://outreachrecruitment.net/jobs/">outreachrecruitment.net/jobs</a></p>

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
<h2>📎 CSV Attachments</h2>
<ul style="margin:0">
  <li>missing_jobs.csv — {len(report.missing_jobs)} jobs to add</li>
  <li>extra_jobs.csv — {len(report.extra_jobs)} jobs to remove</li>
  <li>title_mismatches.csv — {len(report.title_mismatches)} entries</li>
  <li>broken_links.csv — {len(report.broken_links)} pages</li>
  <li>seo_issues.csv — {len(report.seo_issues)} issues</li>
</ul>
</div>

<div class="footer">
  <p>Outreach Recruitment — Job Sync Agent | Runs every 2 days at 08:00 Malta Time</p>
  <p>
    Careers Platform: <a href="https://outreach-recruitment-agency.careers-page.com/">outreach-recruitment-agency.careers-page.com</a> &nbsp;|&nbsp;
    Website: <a href="https://outreachrecruitment.net/jobs/">outreachrecruitment.net/jobs</a>
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

    print("=" * 60)
    print("  Outreach Recruitment — Job Sync Agent")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: Scrape careers page
    print("\n[1/5] Scraping careers page …")
    careers_jobs, careers_count = scrape_careers_page()
    print(f"  Collected {len(careers_jobs)} jobs (advertised: {careers_count})")

    # Step 2: Scrape public website
    print("\n[2/5] Scraping public website …")
    website_jobs = scrape_public_website()
    print(f"  Found {len(website_jobs)} job cards")

    # Step 3: SEO + broken link checks
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

    # Step 5: Build report
    print("\n[5/5] Building report …")
    report = build_report(careers_jobs, careers_count, website_jobs, sitemap_urls, skip_seo=no_seo)

    print_summary(report)

    # Step 5b: Fetch full details + generate prompts for missing jobs
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
        report2.previous_score = report.sync_score
        report = report2
        print_summary(report)
    elif do_fix:
        print("\n[Auto-Fix] Nothing to fix — already in sync!")

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
