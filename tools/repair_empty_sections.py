"""
repair_empty_sections.py
========================
Re-fetches job detail pages for any job that has empty Key Responsibilities,
Requirements, or What's on Offer sections, and patches those sections in-place.

Usage:
    python3 tools/repair_empty_sections.py
"""
from __future__ import annotations
import json
import re
import sys
import time
from html import escape
from pathlib import Path

# Re-use parsing helpers from the scraper
sys.path.insert(0, str(Path(__file__).parent))
from scrape_careers_page import fetch, strip_tags, extract_section, parse_jsonld

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "jobs"
REGISTRY = ROOT / "tools" / "jobs_registry.json"
CAREERS_BASE = "https://outreach-recruitment-agency.careers-page.com"
DELAY_SECS = 1.5


def list_items(raw: list[str]) -> str:
    return "".join(f"<li>{escape(i)}</li>" for i in raw if i.strip())


def patch_section(html: str, heading: str, new_items: str) -> str:
    pattern = rf'({re.escape(heading)}</h2><div class="w-richtext"><ul[^>]*>)(.*?)(</ul></div>)'
    return re.sub(pattern, lambda m: m.group(1) + new_items + m.group(3),
                  html, count=1, flags=re.S)


def has_empty_sections(html: str) -> bool:
    return '<ul role="list"></ul>' in html


def fetch_content(uuid: str) -> dict:
    """Fetch a careers page job and return extracted section lists."""
    url = f"{CAREERS_BASE}/jobs/{uuid}"
    try:
        html = fetch(url)
    except Exception as e:
        print(f"    ERROR: {e}")
        return {}

    ld = parse_jsonld(html)
    desc_text = ld.get("description", "")
    if desc_text:
        desc_text = strip_tags(desc_text)
    if not desc_text or len(desc_text.strip()) < 30:
        return {}

    return {
        "responsibilities": extract_section(desc_text,
            "Key Responsibilities", "Responsibilities", "Main Duties", "Duties",
            "Key Duties", "Your tasks", "Your Tasks", "The Role", "Main Tasks",
            "Key Tasks", "What you'll do", "What You'll Do"),
        "requirements": extract_section(desc_text,
            "Requirements", "What We're Looking For", "Qualifications",
            "What you need", "Job Requirements", "Who We Need",
            "The Ideal Candidate", "Skills & Experience", "Your Profile", "About You"),
        "offer": extract_section(desc_text,
            "What's on Offer", "What We Offer", "Benefits", "Package",
            "On Offer", "We Offer", "Remuneration", "Why Join", "What You Get"),
    }


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    # Collect jobs with empty sections
    to_repair = []
    for job in registry:
        slug = job["slug"]
        path = JOBS / slug / "index.html"
        if not path.exists():
            path = JOBS / f"{slug}.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        if has_empty_sections(html):
            uuid_m = re.search(r'careers-page\.com/jobs/([0-9a-f-]{36})/apply', html)
            if uuid_m:
                to_repair.append({"slug": slug, "uuid": uuid_m.group(1)})

    print(f"Found {len(to_repair)} job page(s) with empty sections.\n")

    updated = 0
    no_content = 0

    for i, item in enumerate(to_repair, 1):
        slug = item["slug"]
        uuid = item["uuid"]
        print(f"[{i}/{len(to_repair)}] {slug} … ", end="", flush=True)

        content = fetch_content(uuid)
        if not content or not any(content.values()):
            print("no content found")
            no_content += 1
            time.sleep(DELAY_SECS)
            continue

        resp_html  = list_items(content.get("responsibilities", []))
        req_html   = list_items(content.get("requirements", []))
        offer_html = list_items(content.get("offer", []))

        if not resp_html and not req_html and not offer_html:
            print("sections empty after parse")
            no_content += 1
            time.sleep(DELAY_SECS)
            continue

        # Patch both the .html and /index.html copies
        paths = [
            JOBS / slug / "index.html",
            JOBS / f"{slug}.html",
        ]
        for path in paths:
            if not path.exists():
                continue
            html = path.read_text(encoding="utf-8")
            if resp_html:
                html = patch_section(html, "Key Responsibilities", resp_html)
            if req_html:
                html = patch_section(html, "Requirements", req_html)
            if offer_html:
                html = patch_section(html, "What's on Offer", offer_html)
            path.write_text(html, encoding="utf-8")

        parts = []
        if resp_html: parts.append(f"{len(content['responsibilities'])} responsibilities")
        if req_html:  parts.append(f"{len(content['requirements'])} requirements")
        if offer_html: parts.append(f"{len(content['offer'])} offer items")
        print("OK — " + ", ".join(parts))
        updated += 1

        time.sleep(DELAY_SECS)

    print(f"\nDone. Updated: {updated}, No content: {no_content}")


if __name__ == "__main__":
    main()
