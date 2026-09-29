"""
update_construction_hub.py
==========================
Regenerates construction-jobs-in-malta.html from tools/jobs_registry.json:
featured jobs, grouped job cards, live count + "updated" date, salary table
(only salaries actually published on the job pages), jobs-by-location,
FAQ (visible + FAQPage schema), ItemList / Breadcrumb schema, title and meta.

Called automatically at the end of update_jobs_listing.py; can also be run
on its own:  python3 tools/update_construction_hub.py
Idempotent: everything between <main class="main"> and </main> is rebuilt.
"""
from __future__ import annotations
import json
import re
from collections import OrderedDict
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tools" / "jobs_registry.json"
HUB = ROOT / "construction-jobs-in-malta.html"
BASE = "https://outreachrecruitment.net"
HUB_URL = f"{BASE}/construction-jobs-in-malta"
OG_IMAGE = f"{BASE}/assets/jobs-malta-construction.png"

# Shown on top in highlighted boxes, in this order (only while open).
FEATURED = ["wood-painting-finishing-specialist", "skilled-carpenters", "gypsum-installers"]

# A job belongs on this hub if its category is Construction, or its title
# matches a construction trade (maritime/shipyard and mechanic roles excluded).
TRADE_RE = re.compile(
    r"construct|foreman|carpent|joiner|shutter|steel fix|labourer|civil works|surveyor|gypsum|drywall|"
    r"plaster|mason|tiler|tile layer|scaffold|alumin|site coordinator|site manager|wood paint|"
    r"heavy machine|builder|excavat|crane|paver", re.I)
EXCLUDE_SLUGS = {"labourer-mechanic"}
EXCLUDE_CATEGORIES = {"Marine & Shipping", "Marine"}

GROUPS = [
    ("Trades, Finishing &amp; Labour", None),
    ("Site Supervision &amp; Project Management", re.compile(r"foreman|coordinator|project manager|site manager|supervisor", re.I)),
    ("Quantity Surveying, Quality &amp; Engineering", re.compile(r"surveyor|\bqa\b|quality|engineer|laborator", re.I)),
]

GUIDES = [
    ("/blog/construction-worker-salary-malta", "Construction worker salary in Malta 2026"),
    ("/blog/construction-jobs-malta-non-eu-workers", "How to get a construction job in Malta as a non-EU worker"),
    ("/blog/site-foreman-jobs-malta", "Site foreman jobs in Malta: duties, pay and how to get hired"),
    ("/blog/construction-engineering-jobs-malta-overview", "Construction and engineering jobs in Malta: an overview"),
]

ARROW = ('<svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M5 12H19M19 12L12 5M19 12L12 19" '
         'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--_⚡️-icons---icon-stroke)"></path></svg>')
PIN = ('<svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M10 18s6-5.686 6-10.5A6 6 0 0 0 4 7.5C4 12.314 10 18 10 18Z" '
       'stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"></path><circle cx="10" cy="7.5" r="2" stroke="currentColor" stroke-width="1.5"></circle></svg>')
PLUS = ('<svg fill="none" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M3.33203 8L12.6654 8" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
        'stroke-width="var(--_⚡️-icons---icon-stroke)"></path><path d="M8 3.33325V12.6666" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
        'stroke-width="var(--_⚡️-icons---icon-stroke)"></path></svg>')
MINUS = ('<svg fill="none" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M8 3.33325V12.6666" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
         'stroke-width="var(--_⚡️-icons---icon-stroke)"></path></svg>')

STYLE = """<style id="construction-hub-style">
#top15-dark-frame .ch-count{color:rgba(255,255,255,.75);font-size:1rem;margin-top:.75rem}
.ch-block{margin-top:56px}
.ch-block-title{color:#fff;font-size:1.35rem;font-weight:600;margin:0 0 20px;text-align:left}
.ch-featured-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.ch-feat-card{position:relative;border-radius:22px;background:linear-gradient(135deg,#FFD166 0%,#FF9F1C 55%,#FF7A00 100%);color:#1a1a1a;box-shadow:0 18px 40px rgba(255,138,0,.28);transition:transform .2s ease,box-shadow .2s ease}
.ch-feat-card:hover{transform:translateY(-4px);box-shadow:0 24px 48px rgba(255,138,0,.38)}
.ch-feat-link{display:flex;flex-direction:column;gap:14px;height:100%;padding:26px 24px 24px;color:inherit;text-decoration:none}
.ch-feat-top{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.ch-feat-badge{background:#1a1a1a;color:#FFD166;font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:.3rem .8rem;border-radius:999px}
.ch-feat-cat{font-size:.8rem;font-weight:600;opacity:.8}
.ch-feat-title{font-size:1.35rem;line-height:1.25;font-weight:700;margin:0;color:#1a1a1a}
.ch-feat-meta{display:flex;flex-wrap:wrap;gap:10px 16px;font-size:.9rem;font-weight:500}
.ch-feat-meta span{display:inline-flex;align-items:center;gap:5px}
.ch-feat-meta svg{width:16px;height:16px}
.ch-feat-salary{align-self:flex-start;background:#fff;color:#1a1a1a;font-weight:700;font-size:1rem;padding:.45rem .9rem;border-radius:12px}
.ch-feat-cta{margin-top:auto;display:inline-flex;align-items:center;gap:8px;align-self:flex-start;background:#1a1a1a;color:#fff;font-weight:600;font-size:.95rem;padding:.7rem 1.2rem;border-radius:999px}
.ch-feat-cta svg{width:16px;height:16px}
.ch-grid{display:grid;gap:16px}
.ch-salary-tag{color:#1f7a3f;font-weight:600}
.ch-content{max-width:860px;margin:0 auto}
.ch-content h2{margin:0 0 18px}
.ch-content h3{font-size:1.3rem;font-weight:600;margin:36px 0 12px}
.ch-content p,.ch-content li{font-size:1.02rem;line-height:1.7}
.ch-content ul{padding-left:1.2rem}
.ch-content a{color:#442DFA;text-decoration:underline}
.ch-table-wrap{overflow-x:auto;margin:18px 0}
.ch-table{width:100%;border-collapse:collapse;min-width:480px;font-size:.98rem}
.ch-table th,.ch-table td{text-align:left;padding:12px 14px;border-bottom:1px solid #e3e3e3}
.ch-table th{background:#f4f2ff;font-weight:600}
.ch-table td a{color:#442DFA}
.ch-locations{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin-top:16px}
.ch-location{border:1px solid #e3e3e3;border-radius:14px;padding:14px 16px}
.ch-location strong{display:block;margin-bottom:6px}
.ch-location a{display:block;font-size:.95rem;line-height:1.6}
@media (max-width:991px){.ch-featured-grid{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.ch-featured-grid{grid-template-columns:1fr}.ch-feat-title{font-size:1.2rem}}
</style>"""

FAQ_STYLE = ('<style id="faq-accordion-fix">.faq-list .faq-item-bottom{display:grid !important;grid-template-rows:0fr;height:auto !important;min-height:0 !important;'
             'opacity:0 !important;overflow:hidden;transition:grid-template-rows .3s ease,opacity .3s ease;}.faq-list .faq-item.is-open .faq-item-bottom{grid-template-rows:1fr;'
             'opacity:1 !important;}.faq-list .faq-item-text-wrapper{min-height:0;overflow:hidden;transition:padding .3s ease;}.faq-list .faq-item:not(.is-open) '
             '.faq-item-text-wrapper{padding-top:0 !important;padding-bottom:0 !important;}.faq-list .faq-item-top{cursor:pointer;}.faq-list .icon.small.plus{opacity:1 !important;}'
             '.faq-list .icon.small.minus{opacity:0 !important;}.faq-list .faq-item.is-open .icon.small.plus{opacity:0 !important;}.faq-list .faq-item.is-open .icon.small.minus'
             '{opacity:1 !important;}</style>')
FAQ_SCRIPT = ('<script id="faq-accordion-js">(function(){var items=document.querySelectorAll(".faq-list .faq-item");if(!items.length)return;function setOpen(item,open)'
              '{item.classList.toggle("is-open",open);item.classList.toggle("or-open",open);var top=item.querySelector(".faq-item-top");if(top)top.setAttribute("aria-expanded",'
              'open?"true":"false");}function toggle(item){var willOpen=!item.classList.contains("is-open");items.forEach(function(other){if(other!==item)setOpen(other,false);});'
              'setOpen(item,willOpen);}items.forEach(function(item){var top=item.querySelector(".faq-item-top");var bottom=item.querySelector(".faq-item-bottom");if(!top||!bottom||'
              'item.getAttribute("data-faq-ready"))return;item.setAttribute("data-faq-ready","1");bottom.removeAttribute("style");top.setAttribute("role","button");'
              'top.setAttribute("tabindex","0");setOpen(item,false);top.addEventListener("click",function(e){e.preventDefault();toggle(item);});top.addEventListener("keydown",'
              'function(e){if(e.key==="Enter"||e.key===" "){e.preventDefault();toggle(item);}});});})();</script>')


# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────

def page_path(slug: str) -> Path | None:
    folder, flat = ROOT / "jobs" / slug / "index.html", ROOT / "jobs" / f"{slug}.html"
    for p in (flat, folder):  # GitHub Pages serves the flat file first
        if p.exists() and p.stat().st_size > 5000:
            return p
    return None


def page_salary(slug: str) -> str | None:
    """Salary exactly as published in the job page header chip; None if negotiable/undisclosed."""
    p = page_path(slug)
    if not p:
        return None
    chips = re.findall(r'<span class="job-meta-item">(.*?)</span>', p.read_text(encoding="utf-8"), re.S)
    if len(chips) < 2:
        return None
    text = re.sub(r"<svg.*?</svg>|<[^>]+>", "", chips[1], flags=re.S).strip()
    return text if "€" in text else None


def construction_jobs(jobs: list[dict], today: str) -> list[dict]:
    out = []
    for j in jobs:
        if j.get("status", "active").lower() in ("expired", "closed") or j.get("valid_through", "9999-12-31") < today:
            continue
        if j["slug"] in EXCLUDE_SLUGS or j["category"] in EXCLUDE_CATEGORIES:
            continue
        if j["category"] == "Construction" or TRADE_RE.search(j["title"]) or j["slug"] in FEATURED:
            if page_path(j["slug"]):
                j = dict(j, salary=page_salary(j["slug"]))
                out.append(j)
    out.sort(key=lambda j: j.get("date", ""), reverse=True)
    return out


def group_of(job: dict) -> int:
    for i, (_, rx) in enumerate(GROUPS):
        if rx and rx.search(job["title"]):
            return i
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# HTML
# ─────────────────────────────────────────────────────────────────────────────

def e(s: str) -> str:
    return escape(s, quote=True)


def featured_card(j: dict) -> str:
    salary = f'<div class="ch-feat-salary">{e(j["salary"])}</div>' if j.get("salary") else ""
    return (f'<article class="ch-feat-card"><a class="ch-feat-link" href="/jobs/{j["slug"]}/" aria-label="{e(j["title"])} job in {e(j["location"])}">'
            f'<div class="ch-feat-top"><span class="ch-feat-badge">★ Featured</span><span class="ch-feat-cat">Construction</span></div>'
            f'<h3 class="ch-feat-title">{e(j["title"])}</h3>'
            f'<div class="ch-feat-meta"><span>{PIN}{e(j["location"])}</span><span>{e(j.get("employment_type", "Full-Time"))}</span><span>{e(j.get("work_mode", "On-Site"))}</span></div>'
            f'{salary}<span class="ch-feat-cta">Apply Now {ARROW}</span></a></article>')


def job_card(j: dict) -> str:
    salary = f'<span class="ch-salary-tag">{e(j["salary"])}</span>' if j.get("salary") else ""
    return (f'<article class="opening-job-card opening-job-card--centered" data-opening-job="" data-category="Construction" '
            f'data-location="{e(j["location"].lower())}" data-date="{e(j.get("date", ""))}">'
            f'<a class="opening-job-link" href="/jobs/{j["slug"]}/"><img class="opening-job-logo" src="/assets/job-card-logo.jpg" alt="Outreach Recruitment job logo"/>'
            f'<h4 class="heading-h5">{e(j["title"])}</h4><div class="opening-job-company">{e(j["location"])}</div>'
            f'<div class="opening-job-meta"><span>{e(j.get("employment_type", "Full-Time"))}</span>{salary}</div></a></article>')


def faq_items(jobs: list[dict]) -> list[tuple[str, str]]:
    paid = [j for j in jobs if j.get("salary")]
    if paid:
        examples = "; ".join(f'{j["title"]} {j["salary"]}' for j in paid[:5])
        pay = (f"Pay depends on the trade, experience and overtime. Salaries published in our current construction vacancies include: {examples}. "
               "Roles without a published figure are negotiable, and our team shares the range during screening.")
    else:
        pay = "Pay depends on the trade, experience and overtime. Our team shares the salary range for each role during screening."
    return [
        ("How much do construction workers earn in Malta?", pay),
        ("Can non-EU citizens apply for construction jobs in Malta?",
         "Yes, for many roles. Candidates from outside the EU need an employer-sponsored single permit processed through Identità, which takes longer than hiring an EU citizen. "
         "Each job lists a Target Location — for example \"Residents in Malta & Europeans\" or \"EU & Latin America nationals\" — so check it before applying."),
        ("What certificates do I need to work in construction in Malta?",
         "For most trades, proven hands-on experience is the main requirement. Some roles also need specific licences — for example plant and heavy machine operators or drivers — "
         "and Malta's Building and Construction Authority (BCA) runs a skills card scheme for construction workers. Every job description lists exactly what the employer asks for."),
        ("Is accommodation provided with construction jobs in Malta?",
         "It depends on the employer. Where accommodation or transport is included, it is stated in the job description; otherwise our team can confirm it for you during screening."),
        ("What are the working hours on Maltese construction sites?",
         "A standard full-time week is 40 hours, usually with early morning starts. Average weekly hours including overtime are capped at 48 unless you individually agree to work more. "
         "In summer, expect earlier starts and regular breaks to manage the heat."),
        ("Do I need to speak Maltese to work in construction?",
         "No. English is widely used on construction sites in Malta, and most listings ask for basic or good English for communication and safety instructions."),
        ("How long does it take to get hired?",
         "Our team aims to respond to every application within 3–5 business days. Candidates already living in Malta or holding EU citizenship can often start within a few weeks; "
         "non-EU hires take longer because the work permit must be approved first."),
        ("How do I apply for a construction job through Outreach Recruitment?",
         "Choose a job on this page, open it and click Apply Now. Complete the short online form with your experience and CV, and our recruitment team will contact you if your profile matches."),
    ]


def faq_html(items: list[tuple[str, str]]) -> str:
    out = ""
    for q, a in items:
        out += (f'<div class="faq-item"><div class="faq-item-top"><h3 class="text-large strong">{e(q)}</h3><div class="faq-button"><div class="button-circle small">'
                f'<div class="icon small plus w-embed">{PLUS}</div><div class="icon small minus w-embed">{MINUS}</div></div></div></div>'
                f'<div class="faq-item-bottom"><div class="faq-item-text-wrapper"><p class="text-medium">{e(a)}</p></div></div></div>')
    return out


def main_html(jobs: list[dict], today_d: date) -> str:
    n = len(jobs)
    updated = today_d.strftime("%-d %B %Y")
    month = today_d.strftime("%B %Y")
    by_slug = {j["slug"]: j for j in jobs}
    featured = [by_slug[s] for s in FEATURED if s in by_slug]
    rest = [j for j in jobs if j["slug"] not in FEATURED]
    groups: list[list[dict]] = [[] for _ in GROUPS]
    for j in rest:
        groups[group_of(j)].append(j)

    hero = (f'<section class="section hero-2"><div class="hero-frame"><div class="hero-split">'
            f'<div class="hero-media split" data-gsap-scroll="fade" id="w-node-b0a5431f-9eb8-4807-e875-e457476bb0f5-top15"><div class="w-dyn-list"><div class="w-dyn-items" role="list">'
            f'<div class="w-dyn-item" role="listitem"><div class="case-study-compact-card-media"><img alt="Construction worker in a hi-vis vest holding a yellow hard hat at a building site — construction jobs in Malta" '
            f'class="media-fill" sizes="100vw" src="{BASE}/assets/jobs-malta-construction.webp" fetchpriority="high"/><div class="case-study-related-overlay"></div></div></div></div></div></div>'
            f'<div class="w-layout-vflex hero-header home-2" id="w-node-c55a7aff-99b5-9e54-34ab-d0f45aff49ae-top15"><div class="w-layout-vflex text center narrow" data-gsap-scroll="text">'
            f'<h1 class="heading-h1">Construction Jobs in Malta</h1>'
            f'<div class="text-medium">Browse {n} open construction jobs in Malta — carpenters, gypsum installers, wood finishers, labourers, steel fixers, site foremen and quantity surveyors. '
            f'Salaries shown where published. Apply online through Outreach Recruitment.</div></div>'
            f'<div class="w-layout-vflex buttons" data-gsap-scroll="fade"><a class="button-primary animated w-inline-block" href="#top-jobs"><div class="button-label">View Construction Jobs</div>'
            f'<div class="button-rail"><div class="button-circle small accent"><div class="icon small w-embed">{ARROW}</div></div></div>'
            f'<div class="icon-button"><div class="icon small w-embed">{ARROW}</div></div></a></div></div></div></div></section>')

    blocks = ""
    if featured:
        blocks += (f'<div class="ch-block"><h3 class="ch-block-title">Featured Construction Jobs</h3><div class="ch-featured-grid">'
                   + "".join(featured_card(j) for j in featured) + '</div></div>')
    for (title, _), items in zip(GROUPS, groups):
        if items:
            blocks += (f'<div class="ch-block"><h3 class="ch-block-title">{title}</h3><div class="opening-jobs-centered-grid ch-grid">'
                       + "".join(job_card(j) for j in items) + '</div></div>')

    jobs_section = (f'<div id="top15-dark-frame" class="frame" style="background-color:#2C2D2D !important;"><section class="section padding-top-large" id="top-jobs">'
                    f'<div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content"><div class="w-layout-vflex section-header center">'
                    f'<div class="w-layout-vflex text center" data-gsap-scroll="text"><h2 class="heading-h2">Open Construction Jobs in Malta</h2>'
                    f'<p class="ch-count"><strong>{n} open construction jobs</strong> – updated {updated}</p></div></div>'
                    f'{blocks}'
                    f'<div style="display:flex;justify-content:center;margin:48px 0 56px;"><a class="button-primary animated w-inline-block" href="/jobs/">'
                    f'<div class="button-label">Browse all jobs in Malta</div><div class="button-rail"><div class="button-circle small accent"><div class="icon small w-embed">{ARROW}</div></div></div>'
                    f'<div class="icon-button"><div class="icon small w-embed">{ARROW}</div></div></a></div>'
                    f'</div></div></section></div>')

    paid = [j for j in jobs if j.get("salary")]
    rows = "".join(f'<tr><td><a href="/jobs/{j["slug"]}/">{e(j["title"])}</a></td><td>{e(j["location"])}</td><td>{e(j["salary"])}</td></tr>' for j in paid)
    table = (f'<div class="ch-table-wrap"><table class="ch-table"><thead><tr><th>Role</th><th>Location</th><th>Published pay</th></tr></thead><tbody>{rows}</tbody></table></div>'
             if paid else "")

    locs: "OrderedDict[str, list[dict]]" = OrderedDict()
    for j in sorted(jobs, key=lambda j: j["location"]):
        locs.setdefault(j["location"], []).append(j)
    loc_html = "".join(
        f'<div class="ch-location"><strong>{e(loc)}</strong>' + "".join(f'<a href="/jobs/{j["slug"]}/">{e(j["title"])}</a>' for j in items) + '</div>'
        for loc, items in locs.items())
    guides = "".join(f'<li><a href="{u}">{e(t)}</a></li>' for u, t in GUIDES if (ROOT / (u.lstrip("/") + ".html")).exists())

    content = f"""<section class="section padding-top-large" id="construction-guide"><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content"><div class="ch-content w-richtext">
<h2 class="heading-h2">Construction Jobs in Malta in {month}</h2>
<p>Malta's construction industry is one of the island's busiest employers of skilled trades. Apartment blocks, hotels, offices, renovations and public infrastructure keep demand high for carpenters, gypsum and drywall installers, wood finishers, steel fixers, shutterers, labourers and site supervisors — as well as for quantity surveyors and quality managers who keep projects on budget and to standard.</p>
<p>Outreach Recruitment works directly with Malta-based construction and finishing companies. Every vacancy on this page is an open role with a full job description, and the salary is shown wherever the employer has published it. There are currently <strong>{n} open construction jobs</strong> listed; you can apply online in a few minutes and our team will contact you if your profile matches.</p>
<h3>Construction roles in demand</h3>
<ul>
<li><strong>Trades and finishing:</strong> carpenters and joiners, gypsum and drywall installers, wood painters and finishers, plasterers and aluminium installers.</li>
<li><strong>Structural and site work:</strong> steel fixers, steel shutterers, builders, general labourers and heavy machine operators.</li>
<li><strong>Site supervision:</strong> construction site foremen, site coordinators and construction project managers.</li>
<li><strong>Technical and commercial:</strong> quantity surveyors, QA managers and construction materials laboratory staff.</li>
</ul>
<h3>Construction salaries in Malta</h3>
<p>The table below lists every salary currently published in our construction vacancies. Pay depends on the trade, your experience and whether overtime is included. Trades are often paid by the hour, while supervisory and technical roles are usually quoted as a monthly or yearly salary. Roles not listed here are marked negotiable, and our team shares the range during screening.</p>
{table}
<p>To estimate your take-home pay after tax and social security, use our <a href="/salary-calculator-malta">Malta salary calculator</a>.</p>
<h3>Working hours and site conditions</h3>
<p>A standard full-time week in Malta is 40 hours, and average weekly working time including overtime is capped at 48 hours unless you individually agree to work more. Sites usually start early in the morning, and some projects run shifts around deliveries and concrete pours.</p>
<p>Maltese summers are hot and humid. Employers must manage heat stress as part of their health and safety duties, so in July and August expect earlier starts, access to water and shade, and heavier outdoor tasks moved to cooler hours. Always follow your site's safety plan and wear the protective equipment provided.</p>
<h3>Certificates, skills cards and safety</h3>
<p>For most trades, proven hands-on experience matters more than formal qualifications, although certificates and trade training help your application. Malta's Building and Construction Authority (BCA) runs a skills card scheme for construction workers, and some roles need specific licences — for example plant and heavy machine operators or drivers. On every site you will receive a safety induction and must wear personal protective equipment such as a hard hat, safety boots and a hi-vis vest. Each job description lists exactly what the employer asks for.</p>
<h3>EU and non-EU candidates</h3>
<p>EU, EEA and Swiss citizens can work in Malta without a work permit and register as residents once employed. Candidates from outside the EU need an employer-sponsored single permit processed through Identità, which takes longer, so employers state a <em>Target Location</em> on each listing — for example "Residents in Malta &amp; Europeans" or "EU &amp; Latin America nationals". Check it before applying, and if you already live in Malta with a valid permit, mention it in your application.</p>
<h3>Construction jobs by location</h3>
<p>Construction work in Malta is spread across the island. These are the towns where our open construction vacancies are based:</p>
<div class="ch-locations">{loc_html}</div>
<h3>Guides for construction job seekers</h3>
<ul>{guides}</ul>
<p>Looking for related work? Browse <a href="/engineering-jobs-in-malta">engineering jobs in Malta</a>, <a href="/manufacturing-jobs-in-malta">manufacturing and industrial jobs</a> or <a href="/subcontracting-jobs-in-malta">subcontracting jobs in Malta</a>.</p>
</div></div></div></section>"""

    faq = (f'<section class="section padding-top-large" id="faq"><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content">'
           f'<div class="w-layout-vflex section-header center"><div class="w-layout-vflex text center" data-gsap-scroll="text">'
           f'<h2 class="heading-h2">Construction Jobs in Malta: <em>FAQ</em></h2></div></div>'
           f'<div class="faq-list" data-gsap-scroll="stagger">{faq_html(faq_items(jobs))}</div></div></div></section>')

    return '<main class="main">' + hero + jobs_section + content + faq + '</main>'


# ─────────────────────────────────────────────────────────────────────────────
# Head + schema
# ─────────────────────────────────────────────────────────────────────────────

def ld(obj: dict) -> str:
    return "\n" + json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/") + "\n"


def update_head(s: str, jobs: list[dict], today_d: date) -> str:
    n = len(jobs)
    title = f"Construction Jobs in Malta – Hiring Now ({today_d.strftime('%B %Y')})"
    desc = ("Apply for construction jobs in Malta: carpenters, gypsum installers, labourers, steel fixers, site foremen, "
            "quantity surveyors and more. Updated weekly. Apply online today.")

    def sub_meta(s, attr, name, value):
        pat = re.compile(rf'<meta content="[^"]*" {attr}="{re.escape(name)}"/>')
        tag = f'<meta content="{e(value)}" {attr}="{name}"/>'
        if pat.search(s):
            return pat.sub(lambda m: tag, s, count=1)
        return s.replace('<meta content="width=device-width', tag + '<meta content="width=device-width', 1)

    s = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", s, count=1, flags=re.S)
    for attr, name, val in [("name", "description", desc), ("property", "og:title", title), ("property", "og:description", desc),
                            ("property", "og:image", OG_IMAGE), ("name", "twitter:title", title), ("name", "twitter:description", desc),
                            ("name", "twitter:image", OG_IMAGE)]:
        s = sub_meta(s, attr, name, val)
    s = s.replace('data-wf-page="hospitality-jobs-in-malta"', 'data-wf-page="construction-jobs-in-malta"')

    webpage = {
        "@context": "https://schema.org", "@type": "CollectionPage", "name": title,
        "description": desc, "url": HUB_URL, "inLanguage": "en", "dateModified": today_d.isoformat(),
        "about": {"@type": "Organization", "name": "Outreach Recruitment", "url": BASE,
                  "description": "Outreach Recruitment is a Malta-based recruitment agency placing carpenters, gypsum installers, labourers, steel fixers, "
                                 "site foremen, quantity surveyors and other construction professionals with employers across Malta.",
                  "areaServed": "Malta", "serviceType": "Recruitment Agency"},
        "mainEntity": {"@type": "ItemList", "name": "Open Construction Jobs in Malta", "numberOfItems": n,
                       "description": "Current construction vacancies in Malta placed through Outreach Recruitment.",
                       "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": j["title"], "url": f'{BASE}/jobs/{j["slug"]}/'}
                                           for i, j in enumerate(ordered(jobs))]},
    }
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": "Jobs in Malta", "item": f"{BASE}/jobs"},
        {"@type": "ListItem", "position": 3, "name": "Construction Jobs in Malta", "item": HUB_URL}]}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items(jobs)]}
    wanted = {"CollectionPage": webpage, "WebPage": webpage, "BreadcrumbList": crumbs, "FAQPage": faq}

    head_end = s.index("</head>")
    head, rest = s[:head_end], s[head_end:]
    seen = set()

    def repl(m):
        try:
            t = json.loads(m.group(2)).get("@type")
        except ValueError:
            return m.group(0)
        if t in wanted:
            key = "page" if t in ("CollectionPage", "WebPage") else t
            seen.add(key)
            return m.group(1) + ld(wanted[t]) + m.group(3)
        return m.group(0)

    head = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', repl, head, flags=re.S)
    for key, obj in [("page", webpage), ("BreadcrumbList", crumbs), ("FAQPage", faq)]:
        if key not in seen:
            head += f'<script type="application/ld+json">{ld(obj)}</script>'
    for block in (STYLE, FAQ_STYLE):
        bid = re.search(r'id="([^"]+)"', block).group(1)
        head = re.sub(rf'<style id="{bid}">.*?</style>', '', head, flags=re.S) + block
    return head + rest


def ordered(jobs: list[dict]) -> list[dict]:
    feat = [j for s in FEATURED for j in jobs if j["slug"] == s]
    rest = [j for j in jobs if j["slug"] not in FEATURED]
    return feat + [j for g in range(len(GROUPS)) for j in rest if group_of(j) == g]


def main() -> None:
    today_d = date.today()
    jobs = construction_jobs(json.loads(REGISTRY.read_text(encoding="utf-8")), today_d.isoformat())
    s = HUB.read_text(encoding="utf-8")
    a, b = s.index('<main class="main">'), s.index("</main>") + len("</main>")
    s = s[:a] + main_html(jobs, today_d) + s[b:]
    s = update_head(s, jobs, today_d)
    s = re.sub(r'<script id="faq-accordion-js">.*?</script>', '', s, flags=re.S)
    s = s.replace("</body>", FAQ_SCRIPT + "</body>", 1)
    HUB.write_text(s, encoding="utf-8")
    paid = sum(1 for j in jobs if j.get("salary"))
    print(f"  construction-jobs-in-malta.html — {len(jobs)} construction job(s), {paid} with published salary")


if __name__ == "__main__":
    main()
