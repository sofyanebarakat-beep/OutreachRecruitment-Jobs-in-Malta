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
employer_name    Real employer name if public; leave blank to use Outreach Recruitment
confidential_employer true | false; set true if the employer must be hidden in schema
street_address   Optional exact worksite street address
postal_code      Optional worksite postal code
base_salary      Optional actual base salary from employer, numeric only
salary_min       Optional actual minimum salary, numeric only
salary_max       Optional actual maximum salary, numeric only
salary_currency  Salary currency, default EUR
salary_unit      HOUR | DAY | WEEK | MONTH | YEAR, default YEAR
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

# ── Category → live hub page (slug, display name) ───────────────────────────
CATEGORY_HUBS = {
    "Hospitality":               ("hospitality-jobs-in-malta", "Hospitality Jobs in Malta"),
    "Hospitality & Hotel Jobs":  ("hospitality-jobs-in-malta", "Hospitality Jobs in Malta"),
    "Engineering & Maintenance": ("engineering-jobs-in-malta", "Engineering Jobs in Malta"),
    "Sales":                     ("sales-jobs-in-malta", "Sales Jobs in Malta"),
    "Sales & Marketing":         ("sales-jobs-in-malta", "Sales Jobs in Malta"),
    "Marine & Shipping":         ("marine-jobs-in-malta", "Marine Jobs in Malta"),
    "Marine":                    ("marine-jobs-in-malta", "Marine Jobs in Malta"),
    "Construction":              ("construction-jobs-in-malta", "Construction Jobs in Malta"),
    "IT & Technology":           ("it-jobs-in-malta", "IT Jobs in Malta"),
    "IT":                        ("it-jobs-in-malta", "IT Jobs in Malta"),
    "Finance & Accounting":      ("finance-jobs-in-malta", "Finance Jobs in Malta"),
    "Insurance":                 ("insurance-jobs-in-malta", "Insurance Jobs in Malta"),
    "Insurance & Pension":       ("insurance-jobs-in-malta", "Insurance Jobs in Malta"),
    "Retail":                    ("retail-jobs-in-malta", "Retail Jobs in Malta"),
}
# Categories with no live hub page yet (General, Administration, Logistics,
# Healthcare, Marketing, HR & Recruitment, Management, ...) fall back
# to a 3-level breadcrumb (Home > Jobs in Malta > Title) with no hub segment.

# ── City → one-sentence neighbourhood blurb ──────────────────────────────────
NEIGHBOURHOODS = {
    "mellieħa":     "Located in Mellieħa, in the scenic north of Malta near beaches and the Mellieħa Bay resort area.",
    "st. julian's": "Located in St. Julian's, near Spinola Bay and the Paceville entertainment district.",
    "san ġiljan":   "Located in St. Julian's, near Spinola Bay and the Paceville entertainment district.",
    "sliema":       "Located in Sliema, along Malta's main seafront promenade and shopping district.",
    "valletta":     "Located in Valletta, Malta's capital and UNESCO World Heritage city.",
    "floriana":     "Located in Floriana, on the outskirts of Valletta.",
    "birkirkara":   "Located in Birkirkara, one of Malta's largest and most central residential towns.",
    "gżira":        "Located in Gżira, on the waterfront facing Manoel Island and Sliema Creek.",
    "msida":        "Located in Msida, near the University of Malta and Msida Marina.",
    "mosta":        "Located in Mosta, home to the famous Rotunda and a major central-Malta hub.",
    "naxxar":       "Located in Naxxar, a residential town close to the Malta National Aquarium.",
    "paola":        "Located in Paola, in the Cottonera / South Harbour area of Malta.",
    "żejtun":       "Located in Żejtun, in the south-east of Malta near industrial and marine sites.",
    "marsaxlokk":   "Located in Marsaxlokk, Malta's traditional fishing village in the south-east.",
    "birżebbuġa":   "Located in Birżebbuġa, near Malta Freeport in the south of the island.",
    "luqa":         "Located in Luqa, close to Malta International Airport.",
    "qormi":        "Located in Qormi, a central Malta town with a strong industrial base.",
    "hamrun":       "Located in Ħamrun, a busy commercial town close to Valletta.",
    "żebbuġ":       "Located in Żebbuġ, a residential town in central Malta.",
    "attard":       "Located in Attard, one of Malta's affluent central towns near San Anton Gardens.",
    "rabat":        "Located in Rabat, next to the ancient walled city of Mdina.",
    "st. paul's bay": "Located in St. Paul's Bay, a popular seaside town in the north of Malta.",
    "bugibba":      "Located in Bugibba, part of Malta's lively northern tourist strip.",
    "qawra":        "Located in Qawra, on the northern coast alongside Bugibba and St. Paul's Bay.",
    "san gwann":    "Located in San Ġwann, a residential and commercial town near Sliema.",
    "swieqi":       "Located in Swieqi, a residential area close to St. Julian's and Paceville.",
    "marsaskala":   "Located in Marsaskala, a coastal town in the south-east of Malta.",
    "fgura":        "Located in Fgura, in the Cottonera area of south-east Malta.",
    "santa venera": "Located in Santa Venera, a central town close to Valletta and Ħamrun.",
    "biot":         "Located in the shipyard and marine services area on Malta's Grand Harbour.",
    "gozo":         "Located in Gozo, Malta's sister island, known for its slower pace and coastal scenery.",
    "victoria":     "Located in Victoria (Rabat), the capital of Gozo.",
}


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

def generate_job_page(job: dict, other_jobs: list[dict] | None = None) -> str:
    """Clone jobs/plumber/index.html and substitute all dynamic fields."""
    other_jobs = other_jobs or []
    base_path = JOBS / "plumber" / "index.html"
    if not base_path.exists():
        raise FileNotFoundError("Base template jobs/plumber/index.html not found")

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
    # The real apply form is lazy-loaded via data-src (swapped to src by JS on
    # open) — NOT the plain src= attribute, which belongs to the unrelated GTM
    # noscript iframe higher up the page. Target the apply iframe specifically.
    html = re.sub(
        r'(<iframe class="outreach-apply-frame[^"]*"[^>]*data-src=")[^"]*(")',
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

    # ── 7a. Visible page headline (job-header-card) ──────────────────────────
    # Template drifted from <h1 class="heading-h1"> to
    # <h1 class="heading-h1 job-header-title"> — the old regex was a silent no-op
    # and every generated page kept the literal base-template title ("Plumber").
    html = re.sub(
        r'<h1 class="heading-h1 job-header-title">[^<]*</h1>',
        f'<h1 class="heading-h1 job-header-title">{html_esc(title)}</h1>',
        html, count=1
    )

    # ── 7b. h1 with aria-label (apply-panel header) ──────────────────────────
    html = re.sub(
        r'<h1 class="heading-h1" aria-label="[^"]*">[^<]*<',
        f'<h1 class="heading-h1" aria-label="{html_esc(title)}">{html_esc(title)}<',
        html, count=1
    )

    # ── 8. job-header-card meta row (category / salary / emp-type / location) ─
    # 4 <span class="job-meta-item"> chips: index 0 = category, 2 = employment
    # type, 3 = location. Index 1 ("Negotiable") is left untouched on purpose —
    # salary is out of scope and every existing rich page keeps it.
    # NOTE: this whole block was previously hardcoded from the base template
    # (e.g. "Engineering & Maintenance / Negotiable / Full-Time / Mellieħa").
    def _fix_header_meta(block_match):
        idx = [0]
        repls = {0: cat_esc, 2: html_esc(emp_type), 3: loc_esc}
        def _one(mm):
            i = idx[0]
            idx[0] += 1
            return mm.group(1) + repls.get(i, mm.group(2)) + mm.group(3)
        return re.sub(r'(</svg>)([^<]*)(</span>)', _one, block_match.group(0))
    html = re.sub(
        r'<div class="job-header-meta">.*?</div><div class="job-header-actions">',
        _fix_header_meta, html, count=1, flags=re.S
    )

    # ── 8b. Location caption (apply-panel header — right after the aria-label
    #        h1 set in step 7b) ───────────────────────────────────────────────
    html = re.sub(
        rf'(aria-label="{re.escape(html_esc(title))}">{re.escape(html_esc(title))}</h1><div class="caption blue-caption">)[^<]*(</div>)',
        rf"\g<1>{loc_esc}\2", html, count=1
    )

    # ── 9/10/11. Details-grid chips (Category / Employment Type / Work Mode) ──
    # NOTE: these previously targeted <span class="tag blue-tag/grey-tag/green-tag">,
    # which does not exist anywhere in the base template (jobs/plumber/index.html).
    # The real visible markup is the cms-details-grid's "Category" / "Employment
    # Type" / "Work Mode" cms-detail divs below — those were silently left
    # unchanged on every generated job page (visible chip stayed hardcoded from
    # the plumber template, e.g. "Hospitality", regardless of the job's actual
    # category). Fixed to target the real elements.
    html = re.sub(
        r'(<div class="caption blue-caption">Category</div><div class="text-medium">)[^<]*(</div>)',
        rf"\g<1>{cat_esc}\2", html, count=1
    )
    html = re.sub(
        r'(<div class="caption blue-caption">Employment Type</div><div class="text-medium">)[^<]*(</div>)',
        rf"\g<1>{html_esc(emp_type)}\2", html, count=1
    )
    html = re.sub(
        r'(<div class="caption blue-caption">Work Mode</div><div class="text-medium">)[^<]*(</div>)',
        rf"\g<1>{html_esc(work_mode)}\2", html, count=1
    )

    # ── 11b. Intro teaser (heading-h5 inside cms-article/stack) ─────────────
    html = re.sub(
        r'(class="stack gap-07"[^>]*><div class="heading-h5">)[^<]*(</div>)',
        rf"\g<1>{html_esc(title)} — {loc_esc}\2", html, count=1
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
        r'(How To Apply</h2><div class="w-richtext"><p>)(.*?)(</p>)',
        lambda m: m.group(1) + html_esc(closing) + m.group(3),
        html, count=1, flags=re.S
    )

    # ── 13. CTA heading (old "Ready to apply for this <em>X</em>" — harmless
    #        no-op on the current template) + base-template leftovers that the
    #        generator never touched: success-panel confirmation, saved-jobs
    #        JOB_REF, LinkedIn/WhatsApp share links, and the page CSS comment. ─
    html = re.sub(
        r"(apply for this <em>)[^<]*(</em>)",
        rf"\g<1>{html_esc(title)}\2", html, count=1
    )
    html = re.sub(
        r'(Your application for <em>)[^<]*(</em>)',
        rf"\g<1>{html_esc(title)}\2", html, count=1
    )
    html = re.sub(r'(var JOB_REF = ")[^"]*(")', rf"\g<1>{slug}\2", html, count=1)
    html = re.sub(r'(/\* )Plumber( page)', rf"\g<1>{title}\2", html, count=1)
    from urllib.parse import quote as _urlquote
    html = re.sub(
        r'(share-offsite/\?url=)[^"]*(")',
        rf'\g<1>{_urlquote(page_url, safe="")}\2', html, count=1
    )
    _wa_text = _urlquote(f"{title} role in {city}, Malta - {page_url}", safe="")
    html = re.sub(r'(wa\.me/\?text=)[^"]*(")', rf"\g<1>{_wa_text}\2", html, count=1)

    # ── 15. JobPosting JSON-LD schema ─────────────────────────────────────────
    html = re.sub(r'"title":\s*"[^"]*"', f'"title": "{title}"', html, count=1)
    html = re.sub(r'"datePosted":\s*"[^"]*"', f'"datePosted": "{date_posted}"', html, count=1)
    html = re.sub(r'"validThrough":\s*"[^"]*"', f'"validThrough": "{valid_thru}"', html, count=1)
    html = re.sub(r'"streetAddress":\s*"[^"]*"', f'"streetAddress": "{city}, Malta"', html, count=1)
    html = re.sub(r'"addressLocality":\s*"[^"]*"', f'"addressLocality": "{city}"', html, count=1)
    html = re.sub(r'"employmentType":\s*"[^"]*"', f'"employmentType": "{emp_type_schema(emp_type)}"', html, count=1)
    html = re.sub(r'"occupationalCategory":\s*"[^"]*"', f'"occupationalCategory": "{occ_category(category)}"', html, count=1)
    # NOTE: JSON-LD is not HTML, so this must use the raw category, not cat_esc
    # (html_esc(category)) — using the HTML-escaped form wrote literal "&amp;"
    # into the JSON-LD industry field for any category containing "&" (e.g.
    # "Engineering & Maintenance", "Sales & Marketing").
    html = re.sub(r'"industry":\s*"[^"]*"', f'"industry": "{category}"', html, count=1)
    html = re.sub(
        r'"url":\s*"https://outreachrecruitment\.net/jobs/[^"]*"',
        f'"url": "{page_url}"', html, count=1
    )
    # Use actual job content for JSON-LD description (full text, not thin one-liner)
    raw_about = job.get("about", "") or job.get("responsibilities", "") or ""
    if raw_about:
        import html as _html_mod
        plain = re.sub(r'<[^>]+>', ' ', raw_about)
        plain = _html_mod.unescape(plain).strip()
        plain = re.sub(r'\s+', ' ', plain)[:1500]
        schema_desc = plain
    else:
        schema_desc = f"{title} role in {city}, Malta. {category}. Apply through Outreach Recruitment Agency."
    schema_desc_json = json.dumps(schema_desc)[1:-1]
    html = re.sub(
        r'"description":\s*"[^"]*(?<!\\)"',
        lambda m: f'"description": "{schema_desc_json}"', html, count=1
    )
    # NOTE: the base template's "experienceRequirements" is an OBJECT
    # ({"@type": "OccupationalExperienceRequirements", "monthsOfExperience": 1}),
    # not a string — the old string-only regex below silently never matched,
    # so every generated job page kept the generic "monthsOfExperience": 1
    # placeholder. Match either shape and replace with a real string value.
    exp_req = f"Previous experience as a {title} or in a similar role."
    html = re.sub(
        r'"experienceRequirements":\s*(?:"[^"]*"|\{[^}]*\})',
        f'"experienceRequirements": "{exp_req}"', html, count=1
    )
    html = re.sub(r'"value":\s*"[^"]*"', f'"value": "{slug}"', html, count=1)

    # ── 16. Breadcrumb (visible nav + JSON-LD) — rebuilt from the real category ─
    hub = CATEGORY_HUBS.get(category)
    crumbs = [("Home", "/"), ("Jobs in Malta", "/jobs")]
    if hub:
        hub_slug, hub_name = hub
        crumbs.append((hub_name, f"/{hub_slug}"))
    crumbs.append((title, f"/jobs/{slug}"))

    # Visible breadcrumb — match the current template's <nav class="job-breadcrumb">
    # structure (no inline styles), as used by the correctly-migrated rich pages.
    nav_parts = []
    for i, (name, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            nav_parts.append(f'<span aria-current="page">{html_esc(name)}</span>')
        else:
            nav_parts.append(
                f'<a href="{href}">{html_esc(name)}</a><span aria-hidden="true">›</span>'
            )
    nav_html = (
        '<nav aria-label="Breadcrumb" class="job-breadcrumb">' + "".join(nav_parts) + "</nav>"
    )
    html = re.sub(
        r'<nav aria-label="Breadcrumb".*?</nav>',
        lambda m: nav_html, html, count=1, flags=re.S
    )

    bc_items = []
    for i, (name, href) in enumerate(crumbs, start=1):
        item_url = page_url if href.startswith(f"/jobs/{slug}") else f"{BASE_URL}{href}"
        bc_items.append(
            '    {\n      "@type": "ListItem",\n'
            f'      "position": {i},\n      "name": "{name}",\n      "item": "{item_url}"\n    }}'
        )
    bc_json = '"@type": "BreadcrumbList",\n  "itemListElement": [\n' + ",\n".join(bc_items) + "\n  ]\n}"
    html = re.sub(
        r'"@type":\s*"BreadcrumbList".*?\]\s*\}',
        lambda m: bc_json, html, count=1, flags=re.S
    )

    # ── 17. Neighbourhood description ────────────────────────────────────────
    neighbourhood = NEIGHBOURHOODS.get(city.lower(), f"Located in {city}, Malta.")
    html = re.sub(
        r'(<p id="neighbourhood-desc"[^>]*>)[^<]*(</p>)',
        lambda m: m.group(1) + neighbourhood + m.group(2), html, count=1
    )

    # ── 18. Similar Jobs — same category first, then same city, then latest ──
    pool = [j for j in other_jobs
            if j.get("slug") != slug and j.get("status") not in ("expired", "closed")]
    same_category = [j for j in pool if j.get("category") == category]
    same_city = [j for j in pool if j.get("location", "").split(",")[0].strip().lower() == city.lower()]
    seen_slugs: set[str] = set()
    similar: list[dict] = []
    for group in (same_category, same_city, pool):
        for j in group:
            if j["slug"] not in seen_slugs:
                seen_slugs.add(j["slug"])
                similar.append(j)
            if len(similar) >= 4:
                break
        if len(similar) >= 4:
            break

    # SVG glyphs copied verbatim from the base template's similar-job cards.
    _SIM_PIN = ('<svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">'
                '<path d="M10 18s6-5.686 6-10.5A6 6 0 0 0 4 7.5C4 12.314 10 18 10 18Z" '
                'stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"></path>'
                '<circle cx="10" cy="7.5" r="2" stroke="currentColor" stroke-width="1.3"></circle></svg>')
    _SIM_CLOCK = ('<svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">'
                  '<circle cx="10" cy="10" r="7.3" stroke="currentColor" stroke-width="1.3"></circle>'
                  '<path d="M10 5.8V10l3 2" stroke="currentColor" stroke-width="1.3" '
                  'stroke-linecap="round" stroke-linejoin="round"></path></svg>')
    _SIM_ARROW = ('<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
                  '<path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" '
                  'stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>')
    similar_cards = []
    for j in similar:
        j_slug = j["slug"]
        j_title = html_esc(j["title"])
        j_cat = html_esc(j.get("category", "General"))
        j_loc = html_esc(j.get("location", "Malta"))
        j_emp = html_esc(j.get("employment_type", "Full-Time"))
        similar_cards.append(
            f'<div class="similar-job-card"><a class="similar-job-card-link" href="/jobs/{j_slug}" '
            f'aria-label="View {j_title} job details"></a><div class="similar-job-card-top">'
            f'<img class="similar-job-logo" src="/assets/job-card-logo.jpg" alt=""/>'
            f'<span class="similar-job-tag">{j_cat}</span></div>'
            f'<span class="similar-job-title">{j_title}</span>'
            f'<span class="similar-job-fields"><span class="similar-job-field">{_SIM_PIN}{j_loc}</span>'
            f'<span class="similar-job-field">{_SIM_CLOCK}{j_emp}</span></span>'
            f'<a class="similar-job-apply" href="/jobs/{j_slug}">View Job{_SIM_ARROW}</a></div>'
        )
    similar_html = "".join(similar_cards)

    # Heading "Similar Jobs in {Category}"
    html = re.sub(
        r'(<div class="similar-jobs-head"><h2 class="heading-h4">Similar Jobs in )[^<]*(</h2>)',
        lambda m: m.group(1) + cat_esc + m.group(2), html, count=1
    )
    # Carousel track — swap the base template's hardcoded cards for job-specific
    # ones. (The old regex targeted a #similar-jobs <div style="display:grid"> that
    # no longer exists, so every generated page shipped Plumber's similar jobs.)
    if similar_cards:
        html = re.sub(
            r'(<div class="similar-jobs-track" id="similar-jobs-track">).*?'
            r'(</div></div></div></div></section></main>)',
            lambda m: m.group(1) + similar_html + m.group(2), html, count=1, flags=re.S
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

def _ping_indexnow(slugs: list[str]) -> None:
    """Submit new job URLs to IndexNow (Bing/Google instant indexing signal)."""
    import urllib.request, urllib.error
    urls = [f"{BASE_URL}/jobs/{s}" for s in slugs]
    payload = json.dumps({
        "host": "outreachrecruitment.net",
        "key": "indexnow",
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f"  IndexNow: submitted {len(urls)} URL(s) — HTTP {r.status}")
    except urllib.error.HTTPError as e:
        print(f"  IndexNow: HTTP {e.code} (non-fatal)")
    except Exception as e:
        print(f"  IndexNow: skipped ({e})")


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
                "employer_name":   row.get("employer_name", "").strip(),
                "confidential_employer": row.get("confidential_employer", "").strip(),
                "employer_url":    row.get("employer_url", "").strip(),
                "employer_logo":   row.get("employer_logo", "").strip(),
                "street_address":  row.get("street_address", "").strip(),
                "postal_code":     row.get("postal_code", "").strip(),
                "address_locality": row.get("address_locality", "").strip(),
                "address_region":  row.get("address_region", "").strip(),
                "address_country": row.get("address_country", "").strip(),
                "base_salary":     row.get("base_salary", "").strip(),
                "salary_min":      row.get("salary_min", "").strip(),
                "salary_max":      row.get("salary_max", "").strip(),
                "salary_currency": row.get("salary_currency", "").strip(),
                "salary_unit":     row.get("salary_unit", "").strip(),
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
            html = generate_job_page(job, other_jobs=registry)
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
        _ping_indexnow(added)
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
