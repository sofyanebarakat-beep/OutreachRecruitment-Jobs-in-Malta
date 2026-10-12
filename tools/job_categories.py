#!/usr/bin/env python3
"""
job_categories.py — give every job a real category, automatically.

Categories match the site's hub pages (construction, customer service, engineering,
finance, hospitality, insurance, IT, manufacturing, marine, retail, sales …).
A job keeps the category it already has unless it is empty, "General", or a duplicate
spelling ("Marine" → "Marine & Shipping"). Then the category is worked out from the job
title (and the description as a fallback) and written to the registry AND the job page:
schema industry/occupationalCategory, header chip, sidebar "Category" row, the
"Similar Jobs in …" heading and the meta descriptions.

Usage:
  python3 tools/job_categories.py [--dry-run]     # categorise + update pages
  python3 tools/job_categories.py "Job title"     # show the category for a title
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
SNAPSHOT_DIR = ROOT / "tools" / "ats_snapshots"

ALIASES = {
    "marine": "Marine & Shipping", "it": "IT & Technology", "transport": "Logistics",
    "engineering": "Engineering & Maintenance", "finance": "Finance & Accounting",
    "accounting": "Finance & Accounting", "hr": "HR & Recruitment", "customer care": "Customer Service",
}
UNSET = {"", "general", "other", "none", "n/a"}

# Most specific first. Matched against the title, then (fallback) the description.
RULES: list[tuple[str, str]] = [
    ("Insurance", r"insurance|underwrit|claims|broker"),
    ("Customer Service", r"customer (?:service|care|contact|support|operations|experience)|contact cent|call cent|"
                         r"assistance (?:coordinator|operations)|client service"),
    ("IT & Technology", r"developer|software|\bit\b|first line support|helpdesk|help desk|product owner|devops|"
                        r"data (?:analyst|engineer|scien)|systems? (?:admin|analyst|engineer)|network|cyber|"
                        r"drupal|\.net|sharepoint|netsuite|itsm|programmer|ai research|qa tester"),
    ("Wellness", r"\bspa\b|beauty|nail|massage|therapist|hair|aesthetic"),
    ("Healthcare", r"nurse|carer|care worker|health(?:care)?\b|doctor|pharmac|medical|dental"),
    ("Marine & Shipping", r"marine|ship|yacht|vessel|diver|deckhand|seafar|crew|maritime|boat"),
    ("Hospitality", r"chef|cook|kitchen|waiter|waitress|bartender|bar attend|barista|housekeep|room attend|"
                    r"hotel|porter|restaurant|front office|commis|pizza|deli|sous|dishwash|runner|f&b|butler|"
                    r"concierge|food (?:and|&) beverage|salumeria|hospitality|steward|catering|banquet"),
    ("Construction", r"builder|shutter|mason|gypsum|plaster|carpent|tiler|construction|estimator|quantity|"
                     r"draught|site (?:manager|engineer)|crane|scaffold|steel fixer|painter|aluminium|aluminum|"
                     r"structural|joiner|labourer|civil"),
    ("Manufacturing", r"production|operator|bottling|factory|assembler|packer|manufactur|cnc|machin|"
                      r"turner|plate shop|fabricat|welder"),
    ("Engineering & Maintenance", r"engineer|technician|electric|maintenance|mechanic|hvac|plumb|fitter|"
                                  r"automotive|refrigerat|facility|fleet"),
    ("Logistics", r"driver|delivery|warehouse|storekeep|logistic|forklift|transport|courier|purchasing|"
                  r"procurement|supply chain|dispatch|washer"),
    ("Retail", r"retail|shop|cashier|store|counter|merchandis|parts personnel|luxury"),
    ("Sales", r"sales|business development|account manager|marketing|media buyer|social media|"
              r"commercial executive"),
    ("Finance & Accounting", r"account|audit|tax|financ|payroll|bookkeep|payment|credit|treasur|"
                             r"controller|cfo"),
    ("HR & Recruitment", r"\bhr\b|human resources|recruit|talent"),
    ("Administration", r"admin|office|secretar|receptionist|coordinator|clerk|data entry|assistant|"
                       r"executive|supervisor|manager|officer|qhse|hsse|health and safety"),
]


def canonical(category: str) -> str:
    c = (category or "").strip()
    return ALIASES.get(c.lower(), c)


def categorize(title: str, description: str = "") -> str:
    t = title.lower()
    for cat, pattern in RULES[:-1]:
        if re.search(pattern, t):
            return cat
    # Only generic words in the title ("Supervisor", "Officer"): let the description decide.
    d = description.lower()
    best, hits = "Administration", 0
    for cat, pattern in RULES[:-1]:
        n = len(re.findall(pattern, d))
        if n > hits:
            best, hits = cat, n
    return best


def choose(job: dict, description: str = "") -> str:
    """Keep a real existing category; otherwise work it out."""
    current = canonical(job.get("category", ""))
    if current.lower() not in UNSET:
        return current
    return categorize(job.get("title", ""), description)


def page_files(slug: str) -> list[Path]:
    sys.path.insert(0, str(ROOT / "tools"))
    from verify_job_page import real_pages  # follows old redirect stubs to the real page
    return real_pages(slug)


def update_page(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    o, n = re.escape(old), new
    o_html = re.escape(htmllib.escape(old))
    out = text
    out = re.sub(rf'("(?:industry|occupationalCategory)"\s*:\s*)"{o}"', rf'\1"{n}"', out)
    out = re.sub(rf'(<div class="caption blue-caption">Category</div><div class="text-medium">){o_html}(</div>)',
                 rf"\g<1>{htmllib.escape(n)}\g<2>", out)
    out = re.sub(rf'(</svg>){o_html}(</span>)', rf"\g<1>{htmllib.escape(n)}\g<2>", out, count=1)  # header chip
    out = re.sub(rf"(Similar Jobs in ){o_html}(<)", rf"\g<1>{htmllib.escape(n)}\g<2>", out)
    out = re.sub(rf"(\. ){o_html}( role\.)", rf"\g<1>{htmllib.escape(n)}\g<2>", out)
    if out != text:
        path.write_text(out, encoding="utf-8")
        return True
    return False


def run(dry: bool = False) -> dict:
    """Categorise every job in the registry and its pages. Returns {changed: [...], touched: [...]}."""
    jobs = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    changed, touched = [], []
    for job in jobs:
        old = job.get("category", "") or ""
        desc = ""
        m = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", job.get("apply_url", ""))
        if m and (SNAPSHOT_DIR / f"{m.group(0)}.json").exists():
            desc = json.loads((SNAPSHOT_DIR / f"{m.group(0)}.json").read_text()).get("description_text", "")
        new = choose(job, desc)
        if new == old:
            continue
        changed.append({"slug": job["slug"], "title": job["title"], "from": old or "(none)", "to": new})
        if dry:
            continue
        job["category"] = new
        for f in page_files(job["slug"]):
            if old and update_page(f, old, new):
                touched.append(str(f.relative_to(ROOT)))
    if changed and not dry:
        REGISTRY_PATH.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"changed": changed, "touched": touched}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        print(categorize(" ".join(args)))
    else:
        res = run(dry="--dry-run" in sys.argv)
        for c in res["changed"]:
            print(f"  {c['title']}: {c['from']} → {c['to']}")
        print(f"{len(res['changed'])} job(s) recategorised, {len(res['touched'])} page file(s) updated")
