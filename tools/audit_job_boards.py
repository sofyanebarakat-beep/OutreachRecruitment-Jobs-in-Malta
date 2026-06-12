#!/usr/bin/env python3
"""
Audit Outreach Recruitment job board sync.

Compares:
- https://outreach-recruitment-agency.careers-page.com/
- https://outreachrecruitment.net/jobs/
- local jobs/index.html, when available

Writes Markdown and JSON reports to reports/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
CAREERS_URL = "https://outreach-recruitment-agency.careers-page.com/"
PUBLIC_URL = "https://outreachrecruitment.net/jobs/"
LOCAL_JOBS = ROOT / "jobs" / "index.html"


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
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"[ \t]+", " ", unescape(html)).strip()


def normalize_title(title: str) -> str:
    title = unescape(title).lower()
    title = title.replace("&", " and ")
    title = re.sub(r"\([^)]*\)", " ", title)
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


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


def parse_careers_page(max_pages: int = 40) -> SourceResult:
    jobs: list[str] = []
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

    return SourceResult(
        name="Careers platform",
        url=CAREERS_URL,
        final_url=final_url,
        count=count,
        jobs=jobs,
        partial=False,
        warnings=warnings,
    )


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

    if len(jobs) < (count or 0):
        warnings.append(
            "Public website HTML appears to expose only visible/first-page jobs; missing-job comparison may be partial."
        )
    spam_markers = ["Hacklink", "Nulled", "casino", "escort", "bet", "porn"]
    found_spam = sorted({m for m in spam_markers if re.search(m, text, re.I)})
    if found_spam:
        warnings.append(
            "Suspicious footer/link text found on public site: " + ", ".join(found_spam)
        )

    return SourceResult("Public website", PUBLIC_URL, final_url, count, jobs, True, warnings)


def parse_local_jobs() -> SourceResult:
    if not LOCAL_JOBS.exists():
        return SourceResult("Local static grid", str(LOCAL_JOBS), str(LOCAL_JOBS), None, [], True, ["jobs/index.html not found."])

    html = LOCAL_JOBS.read_text(encoding="utf-8")
    count = None
    count_match = re.search(r"Showing\s+(\d+)\s+jobs?", html, re.I)
    if count_match:
        count = int(count_match.group(1))

    card_count = len(re.findall(r"<article[^>]+data-opening-job", html, re.I))
    jobs = []
    seen = set()
    card_blocks = re.findall(
        r"(<article[^>]+data-opening-job.*?</article>)",
        html,
        re.I | re.S,
    )
    for block in card_blocks:
        match = re.search(
            r'<h3[^>]*class="[^"]*\bheading-h5\b[^"]*"[^>]*>\s*(.*?)\s*</h3>',
            block,
            re.I | re.S,
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

    return SourceResult("Local static grid", str(LOCAL_JOBS), str(LOCAL_JOBS), count, jobs, False, warnings)


def missing_titles(source: SourceResult, target: SourceResult) -> list[str]:
    target_keys = target.normalized_jobs
    return [title for title in source.jobs if normalize_title(title) not in target_keys]


def write_reports(results: list[SourceResult]) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    md_path = REPORT_DIR / f"job-board-sync-report-{stamp}.md"
    json_path = REPORT_DIR / f"job-board-sync-report-{stamp}.json"

    careers = results[0]
    public = results[1]
    local = results[2]

    missing_public = missing_titles(careers, public)
    missing_local = missing_titles(careers, local)
    extra_public = missing_titles(public, careers)
    extra_local = missing_titles(local, careers)

    data = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "sources": [asdict(r) for r in results],
        "comparisons": {
            "careers_missing_from_public_scrape": missing_public,
            "careers_missing_from_local": missing_local,
            "public_scrape_not_on_careers": extra_public,
            "local_not_on_careers": extra_local,
        },
    }
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def count_label(result: SourceResult) -> str:
        return "Not found" if result.count is None else str(result.count)

    lines = [
        "# Job Board Sync Report",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "## Counts",
        "",
        "| Source | Count | Jobs scraped | Partial | URL |",
        "|---|---:|---:|---|---|",
    ]
    for result in results:
        lines.append(
            f"| {result.name} | {count_label(result)} | {len(result.jobs)} | {'Yes' if result.partial else 'No'} | {result.final_url} |"
        )

    lines.extend([
        "",
        "## Status",
        "",
    ])
    counts = [r.count for r in results if r.count is not None]
    if len(set(counts)) <= 1 and counts:
        lines.append(f"All available counts match at {counts[0]}.")
    else:
        lines.append("Counts do not match.")

    lines.extend([
        "",
        "## Missing From Public Website Scrape",
        "",
    ])
    lines.extend([f"- {title}" for title in missing_public[:100]] or ["- None found in scraped titles."])
    if len(missing_public) > 100:
        lines.append(f"- ...and {len(missing_public) - 100} more")

    lines.extend([
        "",
        "## Missing From Local Static Grid",
        "",
    ])
    lines.extend([f"- {title}" for title in missing_local[:100]] or ["- None."])
    if len(missing_local) > 100:
        lines.append(f"- ...and {len(missing_local) - 100} more")

    lines.extend([
        "",
        "## Public Website Jobs Not Found On Careers Platform",
        "",
    ])
    lines.extend([f"- {title}" for title in extra_public[:100]] or ["- None found in scraped titles."])

    lines.extend([
        "",
        "## Local Static Jobs Not Found On Careers Platform",
        "",
    ])
    lines.extend([f"- {title}" for title in extra_local[:100]] or ["- None."])

    all_warnings = [(r.name, w) for r in results for w in r.warnings]
    if all_warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend([f"- {name}: {warning}" for name, warning in all_warnings])

    lines.extend([
        "",
        "## Recommended Next Action",
        "",
        "- Treat the careers platform as source of truth unless instructed otherwise.",
        "- If local static grid differs, run `python3 tools/scrape_careers_page.py --csv-only` and review/import updates.",
        "- If the public WordPress page differs, update or repair the WordPress jobs source so it mirrors the careers platform.",
    ])

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-pages", type=int, default=40)
    args = parser.parse_args()

    results = [
        parse_careers_page(max_pages=args.max_pages),
        parse_public_site(),
        parse_local_jobs(),
    ]
    md_path, json_path = write_reports(results)

    for result in results:
        print(f"{result.name}: count={result.count} scraped={len(result.jobs)} partial={result.partial}")
        for warning in result.warnings:
            print(f"  WARNING: {warning}")
    print(f"Markdown report: {md_path}")
    print(f"JSON report: {json_path}")

    counts = [r.count for r in results if r.count is not None]
    return 1 if len(set(counts)) > 1 else 0


if __name__ == "__main__":
    sys.exit(main())
