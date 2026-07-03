"""
repair_empty_sections.py
========================
Re-fetches job detail pages for any job that originally had empty Key
Responsibilities, Requirements, or What's on Offer sections (per the last
git commit), and patches those sections in-place with real content scraped
from the live careers-page.com listing — both the visible <ul role="list">
markup and the mirrored JobPosting JSON-LD "description" field.

The careers-page.com template no longer embeds JSON-LD, so content is
scraped directly from the description div in the rendered HTML.

Usage:
    python3 tools/repair_empty_sections.py            # write changes
    python3 tools/repair_empty_sections.py --dry-run  # report only
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
import time
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scrape_careers_page import fetch, strip_tags

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "jobs"
REGISTRY = ROOT / "tools" / "jobs_registry.json"
CAREERS_BASE = "https://outreach-recruitment-agency.careers-page.com"
DELAY_SECS = 1.5

HEADINGS = {
    "responsibilities": "Key Responsibilities",
    "requirements": "Requirements",
    "offer": "What's on Offer",
}
JSONLD_VARIANTS = {
    "responsibilities": ["Key Responsibilities"],
    "requirements": ["Requirements"],
    "offer": ["What's on Offer", "What&#x27;s on Offer"],
}

# Section-heading fragments that sometimes bleed into a scraped bullet list
# (source pages nest headings inside <ul><li> markup) — drop these as items.
HEADING_NOISE = {
    "key responsibilities", "responsibilities", "requirements",
    "what we're looking for", "what were looking for", "qualifications",
    "what's on offer", "what we offer", "benefits", "the ideal candidate",
    "your profile", "about you",
}


def git_show(rel_path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel_path}"],
        cwd=str(ROOT), capture_output=True, text=True
    )
    return result.stdout if result.returncode == 0 else None


def section_empty(html: str, heading: str) -> bool:
    m = re.search(
        rf'<h2 class="heading-h4">{re.escape(heading)}</h2><div class="w-richtext"><ul[^>]*>(.*?)</ul></div>',
        html, re.S
    )
    return bool(m) and len(m.group(1).strip()) == 0


def extract_uuid(html: str) -> str | None:
    m = re.search(r'careers-page\.com/jobs/([0-9a-f-]{36})/apply', html)
    return m.group(1) if m else None


def extract_section(text: str, heading: str) -> list[str]:
    all_headings = list(HEADINGS.values()) + [
        "What We're Looking For", "Qualifications", "Benefits",
        "What We Offer", "Skills & Experience", "Your Profile",
    ]
    stop_alts = "|".join(re.escape(h) for h in all_headings)
    stop_pat = rf"(?:\n\n?(?:{stop_alts})\s*:?|\Z)"
    pattern = rf"(?<!\w){re.escape(heading)}\s*:?\s*\n(.*?){stop_pat}"
    m = re.search(pattern, text, re.S | re.I)
    if not m:
        return []
    block = m.group(1)
    items = [l.lstrip("•- ").strip() for l in block.splitlines() if l.strip() and l.strip() not in ("•", "-")]
    items = [i for i in items if 5 < len(i) <= 300 and i.lower().rstrip(":") not in HEADING_NOISE]
    return items


def fetch_content(uuid: str) -> dict:
    url = f"{CAREERS_BASE}/jobs/{uuid}"
    try:
        html = fetch(url)
    except Exception as e:
        print(f"    ERROR: {e}")
        return {}

    m = re.search(
        r'<div class="text-heading-color mt-4 font-paragraph description">(.*?)<div class="job-description-buttom',
        html, re.S
    )
    if not m:
        return {}
    text = strip_tags(m.group(1))
    if len(text.strip()) < 30:
        return {}

    return {key: extract_section(text, heading) for key, heading in HEADINGS.items()}


def li_html(items: list[str]) -> str:
    return "".join(f"<li>{escape(i, quote=False)}</li>" for i in items)


def li_json(items: list[str]) -> str:
    return "".join(f"<li>{json.dumps(i)[1:-1]}</li>" for i in items)


def patch_visible(html: str, heading: str, new_items_html: str) -> tuple[str, bool]:
    pattern = rf'(<h2 class="heading-h4">{re.escape(heading)}</h2><div class="w-richtext"><ul role="list">)(.*?)(</ul></div>)'
    new_html, n = re.subn(pattern, lambda m: m.group(1) + new_items_html + m.group(3), html, count=1, flags=re.S)
    return new_html, n > 0


def patch_jsonld(html: str, key: str, new_items_json: str) -> tuple[str, bool]:
    for variant in JSONLD_VARIANTS[key]:
        pattern = rf'({re.escape(variant)}:?</p><ul>)(.*?)(</ul>)'
        new_html, n = re.subn(pattern, lambda m: m.group(1) + new_items_json + m.group(3), html, count=1, flags=re.S)
        if n > 0:
            return new_html, True
    return html, False


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    # Collect jobs to repair, keyed by uuid, from the pre-fix HEAD commit.
    by_uuid: dict[str, list[dict]] = {}
    for job in registry:
        slug = job["slug"]
        for rel in (f"jobs/{slug}/index.html", f"jobs/{slug}.html"):
            path = ROOT / rel
            if not path.exists():
                continue
            baseline = git_show(rel)
            if baseline is None:
                continue
            needed = [key for key, heading in HEADINGS.items() if section_empty(baseline, heading)]
            if not needed:
                continue
            uuid = extract_uuid(baseline) or extract_uuid(path.read_text(encoding="utf-8"))
            if not uuid:
                print(f"  SKIP {rel} — no uuid found")
                continue
            by_uuid.setdefault(uuid, []).append({"slug": slug, "rel": rel, "needed": needed})

    total_files = sum(len(v) for v in by_uuid.values())
    print(f"Found {len(by_uuid)} unique job posting(s) / {total_files} file(s) needing repair.\n")

    updated_files = 0
    no_content_uuids = []

    for i, (uuid, files) in enumerate(by_uuid.items(), 1):
        slugs = ", ".join(f["slug"] for f in files)
        print(f"[{i}/{len(by_uuid)}] {uuid} ({slugs}) … ", end="", flush=True)

        content = fetch_content(uuid)
        available = {k: v for k, v in content.items() if v}
        if not available:
            print("no real content found on source")
            no_content_uuids.append(uuid)
            time.sleep(DELAY_SECS)
            continue

        parts = [f"{len(v)} {k}" for k, v in available.items()]
        print("OK — " + ", ".join(parts))

        for f in files:
            path = ROOT / f["rel"]
            html = path.read_text(encoding="utf-8")
            changed = False
            for key in f["needed"]:
                items = available.get(key)
                if not items:
                    continue
                heading = HEADINGS[key]
                html, ok1 = patch_visible(html, heading, li_html(items))
                html, ok2 = patch_jsonld(html, key, li_json(items))
                changed = changed or ok1 or ok2
            if changed and not dry_run:
                path.write_text(html, encoding="utf-8")
                updated_files += 1
            elif changed:
                updated_files += 1

        time.sleep(DELAY_SECS)

    print(f"\nDone. Files updated: {updated_files}. Postings with no source content: {len(no_content_uuids)}")
    if no_content_uuids:
        print("No-content UUIDs:")
        for u in no_content_uuids:
            print(f"  {u}")


if __name__ == "__main__":
    main()
