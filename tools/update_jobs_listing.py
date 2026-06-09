"""
update_jobs_listing.py
======================
Single source of truth for all live job postings.

HOW TO USE
----------
1. Add a new job to the JOBS list below.
2. Run:  python3 tools/update_jobs_listing.py
3. Commit and push — both index.html and jobs/index.html update automatically.

REMOVING A FILLED JOB
---------------------
Delete its entry from JOBS, then run the script again.
"""
from __future__ import annotations
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]

# ──────────────────────────────────────────────────────────────────────────────
# JOB DEFINITIONS  ←  Edit this list only
# ──────────────────────────────────────────────────────────────────────────────
JOBS = [
    {
        "slug":            "shop-assistant",
        "title":           "Shop Assistant",
        "category":        "Retail",
        "location":        "Safi &amp; Tarxien, Malta",
        "location_slug":   "safi tarxien, malta",
        "employment_type": "Full-Time",
        "work_mode":       "On-Site",
        "date":            "2026-06-08",
        "keywords":        "shop assistant retail supermarket convenience customer service",
        "featured":        True,
    },
    {
        "slug":            "plumber",
        "title":           "Plumber",
        "category":        "Engineering &amp; Maintenance",
        "location":        "Mellieħa, Malta",
        "location_slug":   "mellieha, malta",
        "employment_type": "Full-Time",
        "work_mode":       "On-Site",
        "date":            "2026-06-09",
        "keywords":        "plumber plumbing engineering maintenance hospitality hotel facilities",
        "featured":        True,
    },
    {
        "slug":            "welder",
        "title":           "Welder",
        "category":        "Engineering &amp; Maintenance",
        "location":        "Mellieħa, Malta",
        "location_slug":   "mellieha, malta",
        "employment_type": "Full-Time",
        "work_mode":       "On-Site",
        "date":            "2026-06-09",
        "keywords":        "welder welding fabrication metal engineering maintenance mig tig arc hospitality hotel",
        "featured":        True,
    },
    # ── Add new jobs below ────────────────────────────────────────────────────
    # {
    #     "slug":            "job-slug",          # must match jobs/JOB-SLUG.html
    #     "title":           "Job Title",
    #     "category":        "Category",          # e.g. Hospitality, IT, Finance
    #     "location":        "City, Malta",
    #     "location_slug":   "city malta",        # lowercase, spaces only
    #     "employment_type": "Full-Time",          # Full-Time | Part-Time | Contract
    #     "work_mode":       "On-Site",            # On-Site | Remote | Hybrid
    #     "date":            "YYYY-MM-DD",
    #     "keywords":        "search keywords here",
    #     "featured":        True,
    # },
]
# ──────────────────────────────────────────────────────────────────────────────


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
    + ARROW_SVG +
    '</div></div>'
)


def ordinal(n: int) -> str:
    return str(n).zfill(2)


def homepage_job_row(job: dict, num: int) -> str:
    """Single row for the or-scroll-track on index.html."""
    return (
        '<div class="w-dyn-item" role="listitem">'
        f'<a class="job-offer w-inline-block" href="/jobs/{job["slug"]}">'
        '<div class="w-layout-hflex row gap-04">'
        f'<span class="or-num">{ordinal(num)}</span>'
        f'<div class="text-large strong">{job["title"]}</div>'
        f'<div class="tag darker or-tag">{job["category"]}</div>'
        '<span class="tag or-new">New</span>'
        f'<div class="text-large muted">{job["location"]}</div>'
        '</div>'
        + BUTTON_CIRCLE +
        '</a></div>'
    )


def jobs_page_card(job: dict) -> str:
    """Full card for opening-jobs-grid on jobs/index.html."""
    cat_plain = job["category"].replace("&amp;", "&")
    return (
        f'<article class="opening-job-card" data-opening-job '
        f'data-featured="{"true" if job["featured"] else "false"}" '
        f'data-latest="true" '
        f'data-title="{job["keywords"]}" '
        f'data-category="{cat_plain}" '
        f'data-location="{job["location_slug"]}" '
        f'data-date="{job["date"]}">'
        f'<a class="opening-job-link" href="/jobs/{job["slug"]}/">'
        '<div class="opening-card-day">New</div>'
        '<img class="opening-job-logo" src="/assets/job-card-logo.jpg" '
        'alt="Outreach Recruitment job logo"/>'
        f'<h3 class="heading-h5">{job["title"]}</h3>'
        '<div class="opening-job-company">Outreach Recruitment</div>'
        f'<div class="opening-job-location">{job["location"]}</div>'
        '<div class="opening-job-meta">'
        f'<span>{job["employment_type"]}</span>'
        f'<span>{cat_plain}</span>'
        '</div>'
        '</a></article>'
    )


def update_homepage(jobs: list[dict]) -> None:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    n = len(jobs)

    # ── 1. Replace the scroll-track job list ─────────────────────────────────
    track_content = "".join(homepage_job_row(j, i + 1) for i, j in enumerate(jobs))
    html = re.sub(
        r'(<div class="or-scroll-track" role="list">)(.*?)(</div></div></div>)',
        lambda m: m.group(1) + track_content + m.group(3),
        html, count=1, flags=re.S,
    )

    # ── 2. Update counter number ──────────────────────────────────────────────
    html = re.sub(
        r'(<span class="heading-h4 or-counter-num">)\d+(</span>)',
        rf'\g<1>{n}\2',
        html, count=1,
    )

    # ── 3. Update counter label (singular / plural) ───────────────────────────
    label = "open position now" if n == 1 else "open positions now"
    html = re.sub(
        r'(<span class="text-small muted">)open positions? now(</span>)',
        rf'\g<1>{label}\2',
        html, count=1,
    )

    path.write_text(html, encoding="utf-8")
    print(f"  index.html — {n} job(s) updated")


def update_jobs_page(jobs: list[dict]) -> None:
    path = ROOT / "jobs" / "index.html"
    html = path.read_text(encoding="utf-8")
    n = len(jobs)
    featured = sum(1 for j in jobs if j.get("featured"))

    # ── 1. Replace job cards ──────────────────────────────────────────────────
    cards_html = "".join(jobs_page_card(j) for j in jobs)
    html = re.sub(
        r'(<div class="opening-jobs-grid" id="opening-jobs-grid">)(.*?)(</div>)',
        lambda m: m.group(1) + cards_html + m.group(3),
        html, count=1, flags=re.S,
    )

    # ── 2. Update results summary ──────────────────────────────────────────────
    word = "job" if n == 1 else "jobs"
    html = re.sub(
        r'(<div class="opening-results-summary"[^>]*>)Showing \d+ jobs?(</div>)',
        rf'\g<1>Showing {n} {word}\2',
        html, count=1,
    )

    # ── 3. Update board count ──────────────────────────────────────────────────
    role_word = "role" if n == 1 else "roles"
    html = re.sub(
        r'(<div class="opening-board-count">)\d+ roles? available(</div>)',
        rf'\g<1>{n} {role_word} available\2',
        html, count=1,
    )

    # ── 4. Update tab counts ───────────────────────────────────────────────────
    html = re.sub(
        r'(data-opening-tab="featured"[^>]*>Featured <span>)\d+(</span>)',
        rf'\g<1>{featured}\2', html, count=1,
    )
    html = re.sub(
        r'(data-opening-tab="latest"[^>]*>Latest <span>)\d+(</span>)',
        rf'\g<1>{n}\2', html, count=1,
    )
    html = re.sub(
        r'(data-opening-tab="all"[^>]*>Open positions <span>)\d+(</span>)',
        rf'\g<1>{n}\2', html, count=1,
    )

    # ── 5. Rebuild category filter options ────────────────────────────────────
    cats = sorted({j["category"].replace("&amp;", "&") for j in jobs})
    options = '<option value="">Choose...</option>' + "".join(
        f'<option value="{c}">{c}</option>' for c in cats
    )
    html = re.sub(
        r'(<select class="text-field opening-filter-input" id="opening-category">).*?(</select>)',
        rf'\g<1>{options}\2',
        html, count=1, flags=re.S,
    )

    # ── 6. Rebuild location filter options ────────────────────────────────────
    locs = sorted({j["location_slug"].split(",")[0].strip().title() for j in jobs})
    loc_options = '<option value="">Choose...</option>' + "".join(
        f'<option value="{l.lower()}">{l}, Malta</option>' for l in locs
    )
    html = re.sub(
        r'(<select class="text-field opening-filter-input" id="opening-location">).*?(</select>)',
        rf'\g<1>{loc_options}\2',
        html, count=1, flags=re.S,
    )

    path.write_text(html, encoding="utf-8")
    print(f"  jobs/index.html — {n} job(s), {featured} featured updated")


def main() -> None:
    today = date.today().isoformat()
    print(f"Updating job listings ({today}) — {len(JOBS)} job(s):")
    for j in JOBS:
        print(f"  • {j['title']} — {j['location'].replace('&amp;', '&')} [{j['category'].replace('&amp;', '&')}]")
    print()
    update_homepage(JOBS)
    update_jobs_page(JOBS)
    print("\nDone. Run: git add -A && git commit -m 'Update job listings'")


if __name__ == "__main__":
    main()
