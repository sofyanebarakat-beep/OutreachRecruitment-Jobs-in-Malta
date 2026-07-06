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

# Source postings use wildly inconsistent heading text (plain, emoji-prefixed,
# synonyms) — classify any short standalone line by keyword rather than exact
# match, so the sectionizer below stays robust across formats.
RESP_KW = ["responsibilit", "key duties", "main duties", "your tasks", "key tasks",
           "what you'll do", "what you will do", "day-to-day", "day to day", "duties"]
REQ_KW = ["requirement", "looking for", "qualification", "your profile", "about you",
          "candidate profile", "who we need", "ideal candidate", "what you need",
          "skills & experience", "skills and experience"]
OFFER_KW = ["on offer", "we offer", "benefit", "perks", "package", "remuneration",
            "why join", "what you get", "compensation", "in it for you"]


def classify_heading(line: str) -> str | None:
    h = re.sub(r"^[^\w]+", "", line).strip().lower()
    if not h or len(h) > 80:
        return None
    if any(kw in h for kw in OFFER_KW):
        return "offer"
    if any(kw in h for kw in REQ_KW):
        return "requirements"
    if any(kw in h for kw in RESP_KW):
        return "responsibilities"
    return None


def sectionize(text: str) -> dict:
    """Split a scraped job description into responsibilities/requirements/offer
    bullet lists. Source markup varies (real <li> lists, <br>-separated bullet
    characters, emoji headings, or a bullet-marker-then-text-on-next-line
    pattern), so this walks line by line rather than relying on fixed
    heading strings or paragraph boundaries."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    result: dict[str, list[str]] = {"responsibilities": [], "requirements": [], "offer": []}
    current: str | None = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line in ("•", "-", "*"):
            if i + 1 < len(lines):
                content = lines[i + 1]
                if current in result and 3 < len(content) <= 300:
                    result[current].append(content)
                i += 2
                continue
            i += 1
            continue
        if line[:1] in ("•", "-", "*"):
            content = line.lstrip("•-* ").strip()
            if current in result and 3 < len(content) <= 300:
                result[current].append(content)
            i += 1
            continue
        cat = classify_heading(line)
        if cat:
            current = cat
        i += 1
    return result


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

    return sectionize(text)


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
