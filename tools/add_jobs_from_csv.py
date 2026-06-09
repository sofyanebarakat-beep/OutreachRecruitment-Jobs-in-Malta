"""
add_jobs_from_csv.py
====================
Add jobs in bulk from a CSV file.

QUICK START
-----------
1. Fill in  tools/jobs_template.csv  (open in Google Sheets or Excel)
2. Save as CSV and place in the tools/ folder
3. Run:
       python3 tools/add_jobs_from_csv.py tools/jobs_template.csv
4. Review output, then:
       git add -A && git commit -m "Add bulk jobs" && git push origin main

COLUMN GUIDE  (see jobs_template.csv for examples)
----------------------------------------------------
title            Job title exactly as it should appear on the page
slug             URL slug e.g. "software-engineer"  (auto-generated if blank)
category         e.g. Hospitality / IT / Engineering & Maintenance / Retail / Finance
location         Display text  e.g. "Valletta, Malta"
employment_type  Full-Time | Part-Time | Subcontracting  (default: Full-Time)
work_mode        On-Site | Remote | Hybrid  (default: On-Site)
apply_url        Full apply link from careers-page.com
about            About the role paragraph(s). Separate paragraphs with  ||
responsibilities Pipe-separated list items  e.g.  "Do this|Do that|Do the other"
requirements     Pipe-separated list items
offer            Pipe-separated list items  (leave blank for generic defaults)
closing          Closing "How to Apply" sentence  (leave blank for generic)
keywords         Extra search keywords (space-separated; title/location auto-added)
date             Date posted  YYYY-MM-DD  (default: today)
valid_through    Expiry date  YYYY-MM-DD  (default: one year from today)
featured         true | false  (default: true)
"""
from __future__ import annotations
import csv
import json
import re
import sys
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[1]
TOOLS  = ROOT / "tools"
JOBS   = ROOT / "jobs"
REGISTRY = TOOLS / "jobs_registry.json"
SITEMAP  = ROOT / "sitemaps" / "sitemap-jobs.xml"
BASE_URL = "https://outreachrecruitment.net"

# ── How many jobs to show on the homepage scroll-track ──────────────────────
HOMEPAGE_LIMIT = 10   # show the 10 most recent; set 0 for unlimited


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def html_esc(text: str) -> str:
    return escape(text, quote=True)


def list_items(raw: str) -> str:
    """Convert pipe-separated string to <li> HTML."""
    items = [i.strip() for i in raw.split("|") if i.strip()]
    return "".join(f"<li>{html_esc(i)}</li>" for i in items)


def paragraphs(raw: str) -> str:
    """Convert  ||  paragraph breaks to <br/><br/> within a single <p>."""
    parts = [p.strip() for p in raw.split("||") if p.strip()]
    return "<br/><br/>".join(html_esc(p) for p in parts)


def emp_type_schema(emp: str) -> str:
    mapping = {
        "full-time": "FULL_TIME",
        "part-time": "PART_TIME",
        "subcontracting": "CONTRACTOR",
        "contract": "CONTRACTOR",
        "temporary": "TEMPORARY",
        "internship": "INTERN",
    }
    return mapping.get(emp.lower(), "FULL_TIME")


def occ_category(category: str) -> str:
    mapping = {
        "hospitality": "Food Service Workers",
        "retail": "Retail Sales Workers",
        "engineering & maintenance": "Installation, Maintenance, and Repair Workers",
        "it": "Computer and Mathematical Occupations",
        "it & technology": "Computer and Mathematical Occupations",
        "finance": "Business and Financial Operations Occupations",
        "healthcare": "Healthcare Support Occupations",
        "education": "Educational Instruction and Library Occupations",
        "logistics": "Transportation and Material Moving Occupations",
        "construction": "Construction and Extraction Occupations",
        "administration": "Office and Administrative Support Occupations",
        "marketing": "Arts, Design, Entertainment, Sports, and Media Occupations",
        "sales": "Sales and Related Occupations",
    }
    return mapping.get(category.lower(), category)


def auto_keywords(job: dict) -> str:
    base = f"{job['title'].lower()} {job['category'].lower()} {job['location_slug']}"
    extra = job.get("keywords", "")
    return f"{base} {extra}".strip()


# ─────────────────────────────────────────────────────────────────────────────
# HTML page generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_job_page(job: dict) -> str:
    """Clone jobs/plumber.html and substitute all dynamic fields."""
    base_path = JOBS / "plumber.html"
    if not base_path.exists():
        raise FileNotFoundError("Base template jobs/plumber.html not found")

    html = base_path.read_text(encoding="utf-8")

    slug        = job["slug"]
    title       = job["title"]
    category    = job["category"]              # plain text (may have &)
    cat_esc     = html_esc(category)           # HTML-safe
    location    = job["location"]
    loc_esc     = html_esc(location)
    city        = location.split(",")[0].strip()
    emp_type    = job["employment_type"]
    work_mode   = job["work_mode"]
    apply_url   = job["apply_url"]
    date_posted = job["date"]
    valid_thru  = job["valid_through"]
    page_url    = f"{BASE_URL}/jobs/{slug}"

    title_full  = f"{title} Job in {city}, Malta | Outreach Recruitment"
    meta_desc   = (
        f"Apply for a {title} job in {city}, Malta through Outreach Recruitment Agency. "
        f"{category} role. EU nationality or Malta residency required."
    )

    # ── 1. <title> tag ────────────────────────────────────────────────────────
    html = re.sub(r"<title>[^<]+</title>", f"<title>{html_esc(title_full)}</title>", html, count=1)

    # ── 2. meta description ───────────────────────────────────────────────────
    html = re.sub(
        r'(<meta content=")[^"]*(" name="description"/>)',
        rf"\g<1>{html_esc(meta_desc)}\2", html, count=1
    )

    # ── 3. og:title + twitter:title ───────────────────────────────────────────
    html = re.sub(
        r'(<meta content=")[^"]*(" property="og:title"/>)',
        rf"\g<1>{html_esc(title_full)}\2", html, count=1
    )
    html = re.sub(
        r'(<meta content=")[^"]*(" name="twitter:title"/>)',
        rf"\g<1>{html_esc(title_full)}\2", html, count=1
    )

    # ── 4. og:description + twitter:description ───────────────────────────────
    html = re.sub(
        r'(<meta content=")[^"]*(" property="og:description"/>)',
        rf"\g<1>{html_esc(meta_desc)}\2", html, count=1
    )
    html = re.sub(
        r'(<meta content=")[^"]*(" name="twitter:description"/>)',
        rf"\g<1>{html_esc(meta_desc)}\2", html, count=1
    )

    # ── 5. og:url + canonical ─────────────────────────────────────────────────
    html = re.sub(
        r'(<link href=")[^"]*(" rel="canonical"/>)',
        rf"\g<1>{page_url}\2", html, count=1
    )
    html = re.sub(
        r'(<meta content=")[^"]*(" property="og:url"/>)',
        rf"\g<1>{page_url}\2", html, count=1
    )

    # ── 6. Apply iframe src + title ───────────────────────────────────────────
    html = re.sub(
        r'(<iframe[^>]* src=")[^"]*(")',
        rf"\g<1>{apply_url}\2", html, count=1
    )
    html = re.sub(
        r'(title="Apply for )[^"]*(")',
        rf"\g<1>{html_esc(title)}\2", html, count=1
    )
    html = re.sub(
        r'(aria-label="Apply now for )[^"]*(")',
        rf"\g<1>{html_esc(title)}\2", html, count=1
    )
    html = re.sub(
        r'(aria-label="Apply for )[^"]*(")',
        rf"\g<1>{html_esc(title)}\2", html, count=1
    )

    # ── 7. h1 text + aria-label ───────────────────────────────────────────────
    html = re.sub(
        r'<h1 class="heading-h1" aria-label="[^"]*">[^<]*<',
        f'<h1 class="heading-h1" aria-label="{html_esc(title)}">{html_esc(title)}<',
        html, count=1
    )

    # ── 8. Location caption ───────────────────────────────────────────────────
    html = re.sub(
        r'(class="caption blue-caption">)[^<]*(</div>)',
        rf"\g<1>{loc_esc}\2", html, count=1
    )

    # ── 9. Department tag ─────────────────────────────────────────────────────
    html = re.sub(
        r'(<span class="tag blue-tag">)[^<]*(</span>)',
        rf"\g<1>{cat_esc}\2", html, count=1
    )

    # ── 10. Employment type tag ───────────────────────────────────────────────
    html = re.sub(
        r'(<span class="tag grey-tag">)[^<]*(</span>)',
        rf"\g<1>{html_esc(emp_type)}\2", html, count=1
    )

    # ── 11. Work mode tag ────────────────────────────────────────────────────
    html = re.sub(
        r'(<span class="tag green-tag">)[^<]*(</span>)',
        rf"\g<1>{html_esc(work_mode)}\2", html, count=1
    )

    # ── 12. Content sections ─────────────────────────────────────────────────
    about_html = job.get("about", "")
    resp_html  = list_items(job.get("responsibilities", ""))
    req_html   = list_items(job.get("requirements", ""))
    offer_html = list_items(job.get("offer", "Stable employment.|Supportive working environment.|Competitive remuneration package."))
    closing    = job.get("closing", "") or (
        f"If you are interested in this {title} role, we would love to hear from you. "
        f"Apply today through Outreach Recruitment."
    )

    html = re.sub(
        r"(About the Role</h2><div class=\"w-richtext\"><p>)(.*?)(</p></div>)",
        lambda m: m.group(1) + about_html + m.group(3),
        html, count=1, flags=re.S
    )
    html = re.sub(
        r'(Key Responsibilities</h2><div class="w-richtext"><ul[^>]*>)(.*?)(</ul></div>)',
        lambda m: m.group(1) + resp_html + m.group(3),
        html, count=1, flags=re.S
    )
    html = re.sub(
        r'(Requirements</h2><div class="w-richtext"><ul[^>]*>)(.*?)(</ul></div>)',
        lambda m: m.group(1) + req_html + m.group(3),
        html, count=1, flags=re.S
    )
    html = re.sub(
        r'(What\'s on Offer</h2><div class="w-richtext"><ul[^>]*>)(.*?)(</ul></div>)',
        lambda m: m.group(1) + offer_html + m.group(3),
        html, count=1, flags=re.S
    )
    html = re.sub(
        r'(How to Apply</h2><div class="w-richtext"><p>)(.*?)(</p></div>)',
        lambda m: m.group(1) + html_esc(closing) + m.group(3),
        html, count=1, flags=re.S
    )

    # ── 13. CTA heading ──────────────────────────────────────────────────────
    html = re.sub(
        r"(apply for this <em>)[^<]*(</em>)",
        rf"\g<1>{html_esc(title)}\2", html, count=1
    )

    # ── 14. "vacancy in CITY" text ────────────────────────────────────────────
    html = re.sub(
        r"(vacancy in )[^,<]+",
        rf"\g<1>{html_esc(city)}", html, count=1
    )

    # ── 15. JobPosting JSON-LD schema ─────────────────────────────────────────
    html = re.sub(r'"title":\s*"[^"]*"', f'"title": "{title}"', html, count=1)
    html = re.sub(r'"datePosted":\s*"[^"]*"', f'"datePosted": "{date_posted}"', html, count=1)
    html = re.sub(r'"validThrough":\s*"[^"]*"', f'"validThrough": "{valid_thru}"', html, count=1)
    html = re.sub(r'"addressLocality":\s*"[^"]*"', f'"addressLocality": "{city}"', html, count=1)
    html = re.sub(r'"employmentType":\s*"[^"]*"', f'"employmentType": "{emp_type_schema(emp_type)}"', html, count=1)
    html = re.sub(r'"occupationalCategory":\s*"[^"]*"', f'"occupationalCategory": "{occ_category(category)}"', html, count=1)
    html = re.sub(
        r'"url":\s*"https://outreachrecruitment\.net/jobs/[^"]*"',
        f'"url": "{page_url}"', html, count=1
    )
    schema_desc = f"{title} role in {city}, Malta. {category}. Apply through Outreach Recruitment Agency."
    html = re.sub(r'"description":\s*"[^"]*"', f'"description": "{schema_desc}"', html, count=1)

    # ── 16. Breadcrumb schema ─────────────────────────────────────────────────
    html = re.sub(
        r'(\{"@type":\s*"ListItem",\s*"position":\s*3,\s*"name":\s*")[^"]*(",\s*"item":\s*")[^"]*(")',
        rf'\g<1>{title}\g<2>{page_url}\3', html, count=1
    )

    return html


# ─────────────────────────────────────────────────────────────────────────────
# Registry helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_registry() -> list[dict]:
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return []


def save_registry(jobs: list[dict]) -> None:
    REGISTRY.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")


def registry_slugs(jobs: list[dict]) -> set[str]:
    return {j["slug"] for j in jobs}


# ─────────────────────────────────────────────────────────────────────────────
# Sitemap update
# ─────────────────────────────────────────────────────────────────────────────

def rebuild_sitemap(jobs: list[dict]) -> None:
    today = date.today().isoformat()
    entries = [
        '  <url>\n'
        f'    <loc>{BASE_URL}/jobs</loc>\n'
        f'    <lastmod>{today}</lastmod>\n'
        '    <changefreq>daily</changefreq>\n'
        '    <priority>0.9</priority>\n'
        '  </url>\n'
    ]
    for job in jobs:
        entries.append(
            '  <url>\n'
            f'    <loc>{BASE_URL}/jobs/{job["slug"]}</loc>\n'
            f'    <lastmod>{job["date"]}</lastmod>\n'
            '    <changefreq>weekly</changefreq>\n'
            '    <priority>0.8</priority>\n'
            '  </url>\n'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n'
        '  <!-- Job listing index -->\n'
        + "".join(entries) +
        '\n</urlset>\n'
    )
    SITEMAP.write_text(xml, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# CSV parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_csv(csv_path: Path) -> list[dict]:
    today = date.today().isoformat()
    one_year = (date.today() + timedelta(days=365)).isoformat()
    jobs = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            title = row.get("title", "").strip()
            if not title:
                print(f"  Row {i}: missing title, skipped")
                continue
            slug = slugify(row.get("slug", "") or title)
            job = {
                "slug":            slug,
                "title":           title,
                "category":        row.get("category", "").strip() or "General",
                "location":        row.get("location", "Malta").strip(),
                "location_slug":   row.get("location", "malta").lower().strip(),
                "employment_type": row.get("employment_type", "Full-Time").strip() or "Full-Time",
                "work_mode":       row.get("work_mode", "On-Site").strip() or "On-Site",
                "apply_url":       row.get("apply_url", "").strip(),
                "about":           paragraphs(row.get("about", "")),
                "responsibilities": row.get("responsibilities", ""),
                "requirements":    row.get("requirements", ""),
                "offer":           row.get("offer", ""),
                "closing":         row.get("closing", ""),
                "keywords":        row.get("keywords", ""),
                "date":            row.get("date", today).strip() or today,
                "valid_through":   row.get("valid_through", one_year).strip() or one_year,
                "featured":        row.get("featured", "true").strip().lower() != "false",
            }
            job["keywords"] = auto_keywords(job)
            jobs.append(job)
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main(csv_path: str) -> None:
    path = Path(csv_path)
    if not path.exists():
        print(f"ERROR: CSV file not found: {csv_path}")
        sys.exit(1)

    print(f"Reading {path.name} …")
    new_jobs = parse_csv(path)
    if not new_jobs:
        print("No valid rows found in CSV.")
        sys.exit(0)

    registry = load_registry()
    existing = registry_slugs(registry)

    added = []
    skipped = []

    for job in new_jobs:
        slug = job["slug"]
        if slug in existing:
            skipped.append(slug)
            print(f"  SKIP (exists): {slug}")
            continue

        # Generate HTML
        try:
            html = generate_job_page(job)
        except Exception as e:
            print(f"  ERROR generating {slug}: {e}")
            continue

        # Write jobs/SLUG.html
        page_path = JOBS / f"{slug}.html"
        page_path.write_text(html, encoding="utf-8")

        # Write jobs/SLUG/index.html  (trailing-slash fix)
        dir_path = JOBS / slug
        dir_path.mkdir(exist_ok=True)
        (dir_path / "index.html").write_text(html, encoding="utf-8")

        # Add to registry (only metadata, not content)
        registry_entry = {k: job[k] for k in
            ["slug","title","category","location","location_slug",
             "employment_type","work_mode","date","valid_through",
             "apply_url","keywords","featured"]}
        registry.append(registry_entry)
        existing.add(slug)
        added.append(slug)
        print(f"  CREATED: /jobs/{slug}/  ({job['title']})")

    if added:
        save_registry(registry)
        rebuild_sitemap(registry)
        print(f"\nCreated {len(added)} job page(s). Sitemap updated.")
        print("Running update_jobs_listing.py …")
        import subprocess
        subprocess.run(
            ["python3", str(TOOLS / "update_jobs_listing.py")],
            check=True
        )
    else:
        print("No new jobs added.")

    if skipped:
        print(f"\nSkipped {len(skipped)} already-existing: {', '.join(skipped)}")

    if added:
        print("\nNext step:")
        print('  git add -A && git commit -m "Add jobs from CSV" && git push origin main')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/add_jobs_from_csv.py tools/jobs_template.csv")
        sys.exit(1)
    main(sys.argv[1])
