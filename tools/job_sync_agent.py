#!/usr/bin/env python3
"""
job_sync_agent.py — Outreach Recruitment Job Sync Agent
========================================================
Compares all active jobs between:
  Source of Truth: https://outreach-recruitment-agency.careers-page.com/
  Website:         https://outreachrecruitment.net/jobs/

Generates HTML email report with sync score + CSV attachments.
Sends to sbarakat@outreachrecruitment.net

Usage:
  python3 tools/job_sync_agent.py               # full run + email
  python3 tools/job_sync_agent.py --no-email    # run, save report, skip email
  python3 tools/job_sync_agent.py --no-seo      # skip per-page SEO/broken-link checks
  python3 tools/job_sync_agent.py --dry-run     # no email, no SEO, print summary only

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
import sys
import time
from dataclasses import dataclass, field
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


@dataclass
class SyncReport:
    generated_at: str
    careers_count_advertised: int
    careers_count_scraped: int
    website_count: int

    missing_jobs: list[str] = field(default_factory=list)       # on careers, not website
    extra_jobs: list[str] = field(default_factory=list)         # on website, not careers
    title_mismatches: list[dict] = field(default_factory=list)  # similar but different title
    location_mismatches: list[dict] = field(default_factory=list)
    broken_links: list[dict] = field(default_factory=list)
    seo_issues: list[dict] = field(default_factory=list)
    sitemap_missing: list[str] = field(default_factory=list)

    sync_score: float = 100.0
    warnings: list[str] = field(default_factory=list)


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

    # Rule 2 — missing from website
    for norm_title, cj in careers_norm.items():
        if norm_title not in website_norm:
            report.missing_jobs.append(cj.title)

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


def build_html_email(report: SyncReport) -> str:
    date_str = report.generated_at[:10]
    score = report.sync_score

    if score == 100:
        score_color = SCORE_COLOR["excellent"]
        score_label = "✅ Fully Synced"
        alert_box = "<div style='background:#e8f5e9;border:2px solid #2e7d32;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#2e7d32'>✅ All Jobs Synced — No action required.</b></div>"
    elif score >= 90:
        score_color = SCORE_COLOR["good"]
        score_label = "Minor Issues"
        alert_box = "<div style='background:#fff9c4;border:2px solid #f9a825;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#e65100'>⚠️ Minor differences detected — review recommended.</b></div>"
    elif score >= 75:
        score_color = SCORE_COLOR["warning"]
        score_label = "Needs Attention"
        alert_box = "<div style='background:#fff3e0;border:2px solid #ef6c00;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#bf360c'>⚠️ Sync issues detected — action needed.</b></div>"
    else:
        score_color = SCORE_COLOR["critical"]
        score_label = "Critical"
        alert_box = "<div style='background:#ffebee;border:2px solid #c62828;padding:15px;border-radius:8px;margin:20px 0'><b style='color:#b71c1c'>🚨 Action Required — Significant differences between Careers Page and Website.</b></div>"

    # Build actions list
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

    actions_html = "".join(f"<li>{a}</li>" for a in actions)

    seo_rows_html = ""
    for item in report.seo_issues[:30]:
        issues_str = "; ".join(item["issues"])
        item_url = item["url"]
        item_title = item["title"]
        seo_rows_html += f"<tr><td><a href='{item_url}'>{item_title}</a></td><td>{issues_str}</td></tr>"

    if not report.seo_issues and report.website_count > 0 and len(report.broken_links) == 0:
        seo_section_html = "<p style='color:#888'>SEO check skipped (run without --no-seo for full check)</p>"
    elif report.seo_issues:
        seo_section_html = (
            f"<table border='1' cellpadding='5' style='border-collapse:collapse;font-size:13px'>"
            f"<tr><th>Job Title</th><th>Issues</th></tr>"
            f"{seo_rows_html}"
            f"</table>"
        )
    else:
        seo_section_html = "<p style='color:#888'>None</p>"

    sitemap_html = _rows(report.sitemap_missing)

    warnings_html = ""
    if report.warnings:
        wlist = "".join(f"<li>{w}</li>" for w in report.warnings)
        warnings_html = f"<h3 style='color:#e65100'>⚠️ Warnings</h3><ul>{wlist}</ul>"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; }}
  h1 {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; }}
  h2 {{ color: #283593; margin-top: 30px; border-left: 4px solid #3f51b5; padding-left: 10px; }}
  h3 {{ color: #37474f; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  th {{ background: #1a237e; color: white; padding: 8px; text-align: left; }}
  td {{ padding: 6px 8px; border-bottom: 1px solid #e0e0e0; }}
  tr:nth-child(even) {{ background: #f5f5f5; }}
  .score {{ font-size: 48px; font-weight: bold; color: {score_color}; }}
  .stat {{ display: inline-block; margin: 10px 20px 10px 0; }}
  .stat-num {{ font-size: 28px; font-weight: bold; color: #1a237e; }}
  .stat-label {{ font-size: 12px; color: #666; display: block; }}
  ul li {{ margin: 4px 0; }}
  a {{ color: #1565c0; }}
  .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #888; }}
</style>
</head>
<body>

<h1>📋 Job Sync Report — Outreach Recruitment</h1>
<p style="color:#666">Generated: {report.generated_at} | Report for: {date_str}</p>

{alert_box}

<h2>📊 Summary</h2>
<div class="stat"><span class="stat-num">{report.careers_count_advertised or report.careers_count_scraped}</span><span class="stat-label">Careers Page Jobs</span></div>
<div class="stat"><span class="stat-num">{report.website_count}</span><span class="stat-label">Website Jobs</span></div>
<div class="stat"><span class="stat-num">{len(report.missing_jobs)}</span><span class="stat-label">Missing from Website</span></div>
<div class="stat"><span class="stat-num">{len(report.extra_jobs)}</span><span class="stat-label">Extra on Website</span></div>
<div class="stat"><span class="stat-num">{len(report.broken_links)}</span><span class="stat-label">Broken Pages</span></div>
<div class="stat"><span class="stat-num">{len(report.seo_issues)}</span><span class="stat-label">SEO Issues</span></div>

<p><span class="score">{score}%</span>&nbsp;&nbsp;<span style="font-size:20px;color:{score_color}">{score_label}</span></p>

<h2>✅ Actions Required</h2>
<ol>{actions_html}</ol>

<h2>➕ Jobs to Add ({len(report.missing_jobs)})</h2>
<p><em>On careers page but missing from website</em></p>
{_rows(report.missing_jobs)}

<h2>🗑️ Jobs to Remove ({len(report.extra_jobs)})</h2>
<p><em>On website but no longer active on careers page</em></p>
{_rows(report.extra_jobs)}

<h2>📝 Possible Title Differences ({len(report.title_mismatches)})</h2>
<p><em>Jobs with similar but non-matching titles between platforms</em></p>
{_mismatch_table(report.title_mismatches, [
    ("careers_title", "Careers Page Title"),
    ("website_title", "Website Title"),
    ("similarity", "Match %"),
    ("website_url", "URL"),
])}

<h2>📍 Location Differences ({len(report.location_mismatches)})</h2>
{_mismatch_table(report.location_mismatches, [
    ("title", "Job Title"),
    ("registry_location", "Registry Location"),
    ("website_location", "Website Card Location"),
    ("url", "URL"),
])}

<h2>🔗 Broken Pages ({len(report.broken_links)})</h2>
{_mismatch_table(report.broken_links, [
    ("title", "Job Title"),
    ("url", "URL"),
    ("status", "HTTP Status"),
])}

<h2>🔍 SEO Issues ({len(report.seo_issues)})</h2>
{seo_section_html}

<h2>🗺️ Sitemap Issues ({len(report.sitemap_missing)})</h2>
<p><em>Job pages missing from sitemap_index.xml</em></p>
{sitemap_html}

{warnings_html}

<h2>📎 CSV Attachments</h2>
<p>The following CSV files are attached to this email:</p>
<ul>
  <li>missing_jobs.csv — {len(report.missing_jobs)} jobs</li>
  <li>extra_jobs.csv — {len(report.extra_jobs)} jobs</li>
  <li>title_mismatches.csv — {len(report.title_mismatches)} entries</li>
  <li>location_mismatches.csv — {len(report.location_mismatches)} entries</li>
  <li>broken_links.csv — {len(report.broken_links)} pages</li>
  <li>seo_issues.csv — {len(report.seo_issues)} issues</li>
</ul>

<div class="footer">
  <p>Outreach Recruitment — Job Sync Agent | Run every 2 days at 08:00 Malta Time</p>
  <p>Source: <a href="https://outreach-recruitment-agency.careers-page.com/">Careers Platform</a> |
     Website: <a href="https://outreachrecruitment.net/jobs/">outreachrecruitment.net/jobs</a></p>
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
        print(f"  Configure SMTP in: {CONFIG_PATH}")

    return 0 if report.sync_score == 100.0 else 1


if __name__ == "__main__":
    sys.exit(main())
