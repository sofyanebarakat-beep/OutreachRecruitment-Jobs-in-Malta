#!/usr/bin/env python3
"""
build_job_page.py — build a full-quality job page (job-seo-generator spec) from a JSON spec.

Clones the rich template page jobs/crane-installer/index.html, regenerates every job-specific part
(head/meta, JobPosting / BreadcrumbList / FAQPage / ImageObject JSON-LD, header badges + chips,
sidebar, all body sections, FAQ, similar-jobs carousel, share links, apply panel, JOB_REF),
checks for template leftovers, and writes BOTH jobs/<slug>/index.html and jobs/<slug>.html.
With --publish it also adds the registry entry and saves the careers-page fact sheet.

Usage:
  python3 tools/build_job_page.py spec.json [--publish]

Spec (JSON): uuid, slug, title, city, city_full, ref, date_posted, meta_desc, category,
  hub_url, hub_name, image, job_type ("Direct Job" | "Subcontracting"), employment_types (list),
  employment_label, target_location, applicant_country (or null), salary ({min,max,unit,label} or null),
  occupational_category, industry, experience, education, qualifications, work_hours,
  about[], responsibilities[], requirements[], offer[], skills[], preferred[], languages[],
  contract (or null), company, location_text, howto, extra_links [[href, text]], faq [[q, a]],
  keywords, registry_location
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import sync_job_listings as SJL  # noqa: E402

SITE = "https://outreachrecruitment.net"
ATS = "https://outreach-recruitment-agency.careers-page.com"
TEMPLATE = ROOT / "jobs" / "crane-installer" / "index.html"
T_TITLE, T_SLUG, T_CITY, T_REF = "Crane Installer", "crane-installer", "Mqabba", "OR-CRIN-2026-001"
E = html.escape


def build(spec: dict) -> str:
    sp = spec
    title, slug, city, city_full = sp["title"], sp["slug"], sp["city"], sp["city_full"]
    url = f"{SITE}/jobs/{slug}"
    today = date.today().isoformat()
    sal = sp.get("salary")
    sal_label = sal["label"] if sal else "Competitive salary"
    meta_title = f"{title} Job in {city}, Malta | Outreach"
    if len(f"{meta_title} Recruitment") <= 60:
        meta_title += " Recruitment"
    assert len(meta_title) <= 60, f"meta title {len(meta_title)} > 60"
    assert 120 <= len(sp["meta_desc"]) <= 155, f"meta description {len(sp['meta_desc'])} not 120–155"

    s = TEMPLATE.read_text(encoding="utf-8")
    old_uuid = re.search(r"careers-page\.com/jobs/([0-9a-f-]{36})/apply", s).group(1)

    # head
    s = re.sub(r"<title>.*?</title>", f"<title>{E(meta_title)}</title>", s, count=1, flags=re.S)
    def meta(attr, name, value):
        nonlocal s
        s = re.sub(rf'<meta content="[^"]*" {attr}="{re.escape(name)}"/>', f'<meta content="{E(value)}" {attr}="{name}"/>', s)
    for a, n in (("name", "description"), ("property", "og:description"), ("name", "twitter:description")):
        meta(a, n, sp["meta_desc"])
    for a, n in (("property", "og:title"), ("name", "twitter:title")):
        meta(a, n, meta_title)
    meta("property", "og:url", url)
    img = f"{SITE}/assets/{sp['image']}"
    meta("property", "og:image", img); meta("name", "twitter:image", img)
    s = re.sub(r'(<link[^>]+rel="canonical"[^>]+href=")[^"]*(")', rf"\g<1>{url}\g<2>", s)
    s = re.sub(r'(<link[^>]+href=")[^"]*("[^>]+rel="canonical")', rf"\g<1>{url}\g<2>", s)

    p = lambda t: f"<p>{E(t)}</p>"
    ul = lambda items: '<ul role="list">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"
    desc_html = ("".join(p(x) for x in sp["about"]) + "<h3>Key Responsibilities</h3>" + ul(sp["responsibilities"])
                 + "<h3>Requirements</h3>" + ul(sp["requirements"]) + "<h3>What’s on Offer</h3>" + ul(sp["offer"]))

    blocks = []
    for m in re.finditer(r'(<script type="application/ld\+json">)(.*?)(</script>)', s, re.S):
        d = json.loads(m.group(2))
        t = d.get("@type")
        if t == "JobPosting":
            d.update({
                "title": title, "description": desc_html, "datePosted": sp["date_posted"], "dateModified": today,
                "validThrough": "2029-12-30", "url": url,
                "employmentType": sp["employment_types"][0] if len(sp["employment_types"]) == 1 else sp["employment_types"],
                "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "streetAddress": city_full,
                                "addressLocality": city, "addressRegion": "Malta", "postalCode": "0000", "addressCountry": "MT"}},
                "identifier": {"@type": "PropertyValue", "name": "Outreach Recruitment Ltd", "value": slug},
                "occupationalCategory": sp["occupational_category"], "industry": sp["industry"],
                "experienceRequirements": sp["experience"], "qualifications": sp["qualifications"],
                "responsibilities": "; ".join(sp["responsibilities"]), "skills": ", ".join(sp["skills"]),
                "jobBenefits": "; ".join(sp["offer"]), "workHours": sp["work_hours"],
            })
            if sp.get("education"):
                d["educationRequirements"] = sp["education"]
            else:
                d.pop("educationRequirements", None)
            if sp.get("applicant_country"):
                d["applicantLocationRequirements"] = {"@type": "Country", "name": sp["applicant_country"]}
            else:
                d.pop("applicantLocationRequirements", None)
            if sal:
                d["baseSalary"] = {"@type": "MonetaryAmount", "currency": "EUR", "value": {
                    "@type": "QuantitativeValue", "minValue": sal["min"], "maxValue": sal["max"], "unitText": sal["unit"]}}
            else:
                d.pop("baseSalary", None)
        elif t == "BreadcrumbList":
            d["itemListElement"] = [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Jobs in Malta", "item": f"{SITE}/jobs"},
                {"@type": "ListItem", "position": 3, "name": sp["hub_name"], "item": SITE + sp["hub_url"]},
                {"@type": "ListItem", "position": 4, "name": title, "item": url}]
        elif t == "FAQPage":
            d["mainEntity"] = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in sp["faq"]]
        elif t == "ImageObject":
            d.update({"url": img, "caption": f"{title} job opportunity in {city_full} — Outreach Recruitment"})
        blocks.append((m.group(0), m.group(1) + json.dumps(d, indent=2, ensure_ascii=False) + m.group(3)))
    for old, new in blocks:
        s = s.replace(old, new, 1)

    # breadcrumb + header
    s = s.replace('<a href="/construction-jobs-in-malta">Construction Jobs in Malta</a>', f'<a href="{sp["hub_url"]}">{E(sp["hub_name"])}</a>', 1)
    s = s.replace(f'<span aria-current="page">{T_TITLE}</span>', f'<span aria-current="page">{E(title)}</span>')
    if sp["job_type"] != "Direct Job":
        s = s.replace('<span class="job-badge job-badge-type">Direct Job</span>', f'<span class="job-badge job-badge-type">{E(sp["job_type"])}</span>', 1)
    s = re.sub(rf'(<h1 class="heading-h1 job-header-title">){T_TITLE}(</h1>)', rf"\g<1>{E(title)}\g<2>", s)
    hs = s.index('<div class="job-header-meta">'); he = s.index('<div class="job-header-actions">', hs)
    hm = (s[hs:he].replace("</svg>Competitive salary</span>", f"</svg>{E(sal_label)}</span>")
          .replace("</svg>Construction</span>", f"</svg>{E(sp['category'])}</span>")
          .replace(f"</svg>{T_CITY}, Malta</span>", f"</svg>{E(city_full)}</span>"))
    s = s[:hs] + hm + s[he:]

    def side(label, value):
        nonlocal s
        s = re.sub(rf'(<div class="caption blue-caption">{re.escape(label)}</div><div class="text-medium">)[^<]*(</div>)',
                   lambda m: m.group(1) + E(value) + m.group(2), s, count=1)
    side("Category", sp["category"]); side("Employment Type", sp["employment_label"]); side("Salary", sal_label)
    side("Work Mode", "On-Site"); side("Job Type", sp["job_type"] + (" Contract" if sp["job_type"] == "Subcontracting" else ""))
    side("Target Location", sp["target_location"])

    # article
    def section(t, inner, alt=False, sid=None):
        cls = "stack gap-07 job-section-alt" if alt else "stack gap-07"
        return f'<div class="{cls}" data-gsap-scroll="stagger"{f" id={chr(34)}{sid}{chr(34)}" if sid else ""}><h2 class="heading-h4">{E(t)}</h2><div class="w-richtext">{inner}</div></div>'
    a0 = s.index('<div class="cms-article">') + len('<div class="cms-article">')
    a1 = s.index('<div class="stack gap-07" data-gsap-scroll="stagger"><div class="job-share-row">')
    buttons = re.search(r'<div class="buttons".*?</a></div>', s[a0:a1], re.S).group(0)
    links = " · ".join(f'<a href="{h}">{E(t)}</a>' for h, t in sp.get("extra_links", []))
    parts = [f'<div class="stack gap-07" data-gsap-scroll="fade"><div class="heading-h5">{E(title)} — {E(city_full)}</div></div>',
             f"<!-- Internal reference (private, not displayed): {sp['ref']} -->",
             section("About the Role", "".join(p(x) for x in sp["about"]), sid="about-role"),
             section("Key Responsibilities", ul(sp["responsibilities"]), sid="key-responsibilities"),
             section("Requirements", ul(sp["requirements"]), alt=True, sid="requirements"),
             section("What’s on Offer", ul(sp["offer"]), alt=True, sid="whats-on-offer"),
             section("Skills Required", ul(sp["skills"]))]
    if sp.get("preferred"):
        parts.append(section("Preferred Qualifications", ul(sp["preferred"]), alt=True))
    if sp.get("languages"):
        parts.append(section("Languages Required", ul(sp["languages"])))
    if sp.get("contract"):
        parts.append(section("Contract Type", p(sp["contract"]), alt=True))
    parts += [section("About the Company", p(sp["company"])),
              section("Location", f'<p id="neighbourhood-desc">{E(sp["location_text"])}</p>', alt=True),
              section("About Outreach Recruitment", p("Outreach Recruitment Ltd is a Malta-based recruitment agency connecting employers with qualified local and international talent across hospitality, retail, finance, technology, healthcare, construction, engineering, maritime, and other industries.")),
              f'<div class="stack gap-07" data-gsap-scroll="stagger" id="how-to-apply"><h2 class="heading-h4">How To Apply</h2><div class="w-richtext">{p(sp["howto"])}'
              + (f"<p>Browse more roles: {links}</p>" if links else "") + f"{buttons}</div></div>"]
    s = s[:a0] + "".join(parts) + s[a1:]

    # FAQ
    f0 = s.index('<div class="faq-list"'); f0e = s.index(">", f0) + 1
    items = re.findall(r'<div class="faq-item">.*?</p></div></div></div>', s[f0:], re.S)
    tpl = items[0]
    new_items = "".join(
        re.sub(r'(<h3 class="text-large strong">).*?(</h3>)', lambda m, q=q: m.group(1) + E(q) + m.group(2),
               re.sub(r'(<p class="text-medium">).*?(</p>)', lambda m, a=a: m.group(1) + E(a) + m.group(2), tpl, flags=re.S), flags=re.S)
        for q, a in sp["faq"])
    last = s.index(items[-1], f0) + len(items[-1])
    s = s[:f0e] + new_items + s[last:]

    # leftovers outside structured parts
    s = s.replace(old_uuid, sp["uuid"]).replace(T_REF, sp["ref"])
    s = s.replace("Crane%20Installer%20role%20in%20Mqabba%2C%20Malta", quote(f"{title} role in {city_full}"))
    s = s.replace(T_SLUG, slug).replace(T_TITLE, title).replace(f"{T_CITY}, Malta", city_full).replace(T_CITY, city)

    # similar jobs: open jobs of the same category
    reg = json.loads((ROOT / "tools" / "jobs_registry.json").read_text(encoding="utf-8"))
    pool = [j for j in sorted(reg, key=lambda j: j.get("date", ""), reverse=True)
            if j.get("category") == sp["category"] and j.get("status", "") not in ("closed", "expired")
            and j["slug"] != slug and "Malta" in j.get("location", "")]
    for card, job in zip(SJL.CARD_RE.findall(s), pool):
        s = s.replace(card, SJL.fill_card(card, job), 1)
    s = re.sub(r"Similar Jobs in [^<]+<", f"Similar Jobs in {E(sp['category'])}<", s)

    core = s[s.index("<head"):s.index("<nav")] + s[s.index("<main"):s.index("</main>")]
    leaks = [b for b in ("Crane", "crane", T_CITY, "tower", "CRIN", old_uuid, "jobs-malta-construction",
                         "Construction Jobs in Malta") if b in core and b.lower() not in json.dumps(sp).lower()]
    if leaks:
        raise SystemExit(f"Template leftovers found: {leaks}")
    return s


def publish(sp: dict) -> None:
    from ats_facts import parse_job_page, save_snapshot
    from daily_job_sync import fetch
    status, body = fetch(f"{ATS}/jobs/{sp['uuid']}")
    if status == 200:
        save_snapshot(parse_job_page(sp["uuid"], body))
    path = ROOT / "tools" / "jobs_registry.json"
    reg = json.loads(path.read_text(encoding="utf-8"))
    reg = [j for j in reg if sp["uuid"] not in j.get("apply_url", "") or j.get("status") in ("closed", "expired")]
    entry = {"slug": sp["slug"], "title": sp["title"], "category": sp["category"],
             "location": sp.get("registry_location", sp["city_full"]), "location_slug": sp.get("registry_location", sp["city_full"]).lower(),
             "employment_type": "Full-Time" if "FULL_TIME" in sp["employment_types"] else "Part-Time", "work_mode": "On-Site",
             "date": sp["date_posted"], "valid_through": "2029-12-30",
             "apply_url": f"{ATS}/jobs/{sp['uuid']}/apply", "keywords": sp.get("keywords", ""), "featured": True,
             "lastmod": date.today().isoformat()}
    if sp.get("salary"):
        entry["salary"] = sp["salary"]["label"]
    if sp["job_type"] == "Subcontracting":
        entry["job_type"] = "Subcontracting"
    reg.insert(0, entry)
    path.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    page = build(spec)
    (ROOT / "jobs" / spec["slug"]).mkdir(exist_ok=True)
    (ROOT / "jobs" / spec["slug"] / "index.html").write_text(page, encoding="utf-8")
    (ROOT / "jobs" / f"{spec['slug']}.html").write_text(page, encoding="utf-8")
    print(f"built jobs/{spec['slug']}/ ({len(page):,} bytes)")
    if "--publish" in sys.argv:
        publish(spec)
        print("registry entry + fact sheet saved")
