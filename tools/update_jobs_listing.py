"""
update_jobs_listing.py
======================
Regenerates index.html (homepage) and jobs/index.html (job board)
from tools/jobs_registry.json.

HOW TO USE
----------
- To add jobs in bulk:  python3 tools/add_jobs_from_csv.py your_file.csv
  (that script updates the registry AND calls this script automatically)

- To remove a filled job:
  1. Delete its entry from tools/jobs_registry.json
  2. Run: python3 tools/update_jobs_listing.py
  3. Commit and push

HOMEPAGE_LIMIT
--------------
Set how many jobs appear on the homepage scroll-track.
The jobs page always shows every job.
"""
from __future__ import annotations
import json
import re
from html import escape
from pathlib import Path
from datetime import date

ROOT     = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tools" / "jobs_registry.json"

# How many recent jobs to show on the homepage (0 = show all)
HOMEPAGE_LIMIT = 10


# ─────────────────────────────────────────────────────────────────────────────
# Load registry
# ─────────────────────────────────────────────────────────────────────────────

def load_jobs() -> list[dict]:
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Registry not found: {REGISTRY}")
    jobs = json.loads(REGISTRY.read_text(encoding="utf-8"))
    # Ensure category has HTML-escaped version for display
    for j in jobs:
        j.setdefault("category_html", escape(j["category"], quote=False))
        j.setdefault("location_html", escape(j["location"], quote=False))
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# HTML builders
# ─────────────────────────────────────────────────────────────────────────────

ARROW_SVG = (
    '<svg fill="none" height="100%" viewBox="0 0 24 24" width="100%" '
    'xmlns="http://www.w3.org/2000/svg"><path d="M5 12H19M19 12L12 5M19 12L12 19" '
    'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
    'stroke-width="var(--_⚡️-icons---icon-stroke)"></path></svg>'
)
BUTTON_CIRCLE = (
    '<div class="button-circle w-variant-e60b93da-b1c9-73e7-16f0-c65a304e3ef0" '
    'data-wf--button-secondary-circle--variant="small">'
    '<div class="icon w-variant-e60b93da-b1c9-73e7-16f0-c65a304e3ef0 w-embed">'
    + ARROW_SVG + '</div></div>'
)


def homepage_row(job: dict, num: int) -> str:
    return (
        '<div class="w-dyn-item" role="listitem">'
        f'<a class="job-offer w-inline-block" href="/jobs/{job["slug"]}">'
        '<div class="w-layout-hflex row gap-04">'
        f'<span class="or-num">{str(num).zfill(2)}</span>'
        f'<div class="text-large strong">{job["category_html"]}</div>'
        f'<div class="tag darker or-tag">{job["category_html"]}</div>'
        '<span class="tag or-new">New</span>'
        f'<div class="text-large muted">{job["location_html"]}</div>'
        '</div>' + BUTTON_CIRCLE + '</a></div>'
    )


def jobs_page_card(job: dict) -> str:
    cat   = job["category"]
    title = escape(job["title"])
    # data-title includes both title words and keywords so search works on both
    search_data = escape(
        (job["title"] + " " + job.get("keywords", "")).lower().strip(),
        quote=True
    )
    return (
        f'<article class="opening-job-card" data-opening-job '
        f'data-featured="{"true" if job.get("featured") else "false"}" '
        f'data-latest="true" '
        f'data-title="{search_data}" '
        f'data-category="{escape(cat, quote=True)}" '
        f'data-location="{escape(job["location_slug"], quote=True)}" '
        f'data-date="{job["date"]}">'
        f'<a class="opening-job-link" href="/jobs/{job["slug"]}/">'
        '<div class="opening-card-day">New</div>'
        '<img class="opening-job-logo" src="/assets/job-card-logo.jpg" '
        'alt="Outreach Recruitment job logo"/>'
        f'<h3 class="heading-h5">{title}</h3>'
        f'<div class="opening-job-company">{job["location_html"]}</div>'
        '<div class="opening-job-meta">'
        f'<span>{escape(job["employment_type"])}</span>'
        f'<span>{escape(cat)}</span>'
        '</div></a></article>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Page updaters
# ─────────────────────────────────────────────────────────────────────────────

def update_homepage(all_jobs: list[dict]) -> None:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")

    # Most recent first; limit for homepage
    jobs = sorted(all_jobs, key=lambda j: j["date"], reverse=True)
    display = jobs[:HOMEPAGE_LIMIT] if HOMEPAGE_LIMIT else jobs
    n_display = len(display)
    n_total   = len(all_jobs)

    # Scroll track
    track_html = "".join(homepage_row(j, i + 1) for i, j in enumerate(display))
    html = re.sub(
        r'(<div class="or-scroll-track" role="list">)(.*?)(</div></div></div>)',
        lambda m: m.group(1) + track_html + m.group(3),
        html, count=1, flags=re.S,
    )

    # Counter number (show total, not limited)
    html = re.sub(
        r'(<span class="heading-h4 or-counter-num">)\d+(</span>)',
        rf'\g<1>{n_total}\2', html, count=1,
    )

    # Counter label
    label = "open position now" if n_total == 1 else "open positions now"
    html = re.sub(
        r'(<span class="text-small muted">)open positions? now(</span>)',
        rf'\g<1>{label}\2', html, count=1,
    )

    path.write_text(html, encoding="utf-8")
    print(f"  index.html — {n_total} total, showing {n_display} on homepage")


def update_jobs_page(all_jobs: list[dict]) -> None:
    path = ROOT / "jobs" / "index.html"
    html = path.read_text(encoding="utf-8")
    n        = len(all_jobs)
    featured = sum(1 for j in all_jobs if j.get("featured"))

    # Job cards (newest first)
    jobs_sorted = sorted(all_jobs, key=lambda j: j["date"], reverse=True)
    cards_html = "".join(jobs_page_card(j) for j in jobs_sorted)

    # Replace grid contents using div-depth matching (regex fails — first </div>
    # is inside a card, not the grid's own closing tag)
    GRID_OPEN = '<div class="opening-jobs-grid" id="opening-jobs-grid">'
    start_idx = html.find(GRID_OPEN)
    if start_idx >= 0:
        content_start = start_idx + len(GRID_OPEN)
        depth, i = 1, content_start
        end_idx = content_start
        while i < len(html) and depth > 0:
            next_open  = html.find("<div",  i)
            next_close = html.find("</div>", i)
            if next_close < 0:
                break
            if 0 <= next_open < next_close:
                depth += 1
                i = next_open + 4
            else:
                depth -= 1
                if depth == 0:
                    end_idx = next_close
                i = next_close + 6
        html = html[:content_start] + cards_html + html[end_idx:]
    else:
        print("  WARNING: opening-jobs-grid div not found")

    # Counters
    word = "job" if n == 1 else "jobs"
    html = re.sub(
        r'(<div class="opening-results-summary"[^>]*>)Showing \d+ jobs?(</div>)',
        rf'\g<1>Showing {n} {word}\2', html, count=1,
    )
    role_word = "role" if n == 1 else "roles"
    html = re.sub(
        r'(<div class="opening-board-count">)\d+ roles? available(</div>)',
        rf'\g<1>{n} {role_word} available\2', html, count=1,
    )

    # Tab counts
    html = re.sub(r'(data-opening-tab="featured"[^>]*>Featured <span>)\d+(</span>)',
                  rf'\g<1>{featured}\2', html, count=1)
    html = re.sub(r'(data-opening-tab="latest"[^>]*>Latest <span>)\d+(</span>)',
                  rf'\g<1>{n}\2', html, count=1)
    html = re.sub(r'(data-opening-tab="all"[^>]*>Open positions <span>)\d+(</span>)',
                  rf'\g<1>{n}\2', html, count=1)

    # Category filter
    cats = sorted({j["category"] for j in all_jobs})
    cat_opts = '<option value="">Choose...</option>' + "".join(
        f'<option value="{escape(c, quote=True)}">{escape(c)}</option>' for c in cats
    )
    html = re.sub(
        r'(<select class="text-field opening-filter-input" id="opening-category">).*?(</select>)',
        rf'\g<1>{cat_opts}\2', html, count=1, flags=re.S,
    )

    # Location filter — unique cities
    cities = sorted({j["location_slug"].split(",")[0].strip().title() for j in all_jobs})
    loc_opts = '<option value="">Choose...</option>' + "".join(
        f'<option value="{c.lower()}">{c}, Malta</option>' for c in cities
    )
    html = re.sub(
        r'(<select class="text-field opening-filter-input" id="opening-location">).*?(</select>)',
        rf'\g<1>{loc_opts}\2', html, count=1, flags=re.S,
    )

    path.write_text(html, encoding="utf-8")
    print(f"  jobs/index.html — {n} job(s), {featured} featured, {len(cats)} categories")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    jobs = load_jobs()
    today = date.today().isoformat()
    print(f"Updating listings ({today}) — {len(jobs)} job(s) in registry")
    update_homepage(jobs)
    update_jobs_page(jobs)
    print("\nDone. Run: git add -A && git commit -m 'Update job listings' && git push origin main")


if __name__ == "__main__":
    main()
