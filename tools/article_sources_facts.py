#!/usr/bin/env python3
"""
article_sources_facts.py — GEO / AI-search signals for every blog article.

1. "Sources" list at the end of each article: 2–3 official, relevant sources (Identità, Jobsplus, NSO,
   Eurostat, EURES, MFHEA …) chosen by topic, plus a matching `citation` list in the BlogPosting schema.
   Only verified URLs are used: deep links were checked (HTTP 200); government sites behind Cloudflare
   (NSO, DIER, CfR, MFHEA, MFSA, BCA, MDIA, Council of Europe) are linked by their home page only.
2. "By the numbers" box after the quick answer: 2–3 one-sentence facts from our own live job data
   (tools/jobs_registry.json) — open jobs, the biggest category, published salary ranges, new jobs —
   dated, so AI answers can quote an exact, current figure.

Idempotent: re-running replaces both blocks. Then the shared blog layout is re-applied
(tools/apply_blog_template.py), which also refreshes the /<slug>/index.html copies.

Usage:
  python3 tools/article_sources_facts.py            # sources + facts for all articles
  python3 tools/article_sources_facts.py --facts    # refresh only the numbers (weekly)
  python3 tools/article_sources_facts.py --missing  # only articles without a Sources list yet (daily)
  add --commit to commit and push exactly the files it changed (used by tools/run_sync_agent.sh)
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
TODAY = date.today()
E = lambda s: html.escape(str(s), quote=True)

S = {
    "permit": ("Identità — Single Permit for non-EU nationals", "https://identita.gov.mt/expatriates-unit-main-page/noneu-nationals/employment-related-permits/single-permit/", "official work and residence permit rules for third-country nationals"),
    "identita": ("Identità (Government of Malta)", "https://identita.gov.mt/", "identity documents, residence and work permits in Malta"),
    "visa": ("Identità — Central Visa Unit", "https://identita.gov.mt/central-visa-unit-applicable-fees-and-applications-applicable-fees/", "visa applications and fees, including study visas"),
    "jobsplus": ("Jobsplus", "https://jobsplus.gov.mt/", "Malta's public employment service for job seekers and employers"),
    "eures": ("EURES — Living and working in Malta", "https://eures.europa.eu/living-and-working/living-and-working-conditions-europe/living-and-working-conditions-malta_en", "the European Commission's guide to the Maltese labour market"),
    "eurostat": ("Eurostat — Labour market statistics", "https://ec.europa.eu/eurostat/web/labour-market", "official EU employment and wage data, including Malta"),
    "nso": ("National Statistics Office Malta (NSO)", "https://nso.gov.mt/", "official Maltese labour-market and population statistics"),
    "dier": ("Department for Industrial and Employment Relations (DIER)", "https://dier.gov.mt/", "Malta's employment law, minimum wage and working conditions"),
    "cfr": ("Commissioner for Revenue (CfR)", "https://cfr.gov.mt/", "income tax and social security rates in Malta"),
    "mfhea": ("Malta Further and Higher Education Authority (MFHEA)", "https://mfhea.mt/", "accredited institutions and recognition of qualifications"),
    "um": ("University of Malta", "https://www.um.edu.mt/", "Malta's public university and its courses"),
    "mcast": ("MCAST", "https://mcast.edu.mt/", "Malta College of Arts, Science and Technology"),
    "its": ("Institute of Tourism Studies (ITS)", "https://its.edu.mt/", "Malta's hospitality and tourism training institute"),
    "mta": ("Malta Tourism Authority", "https://www.mta.com.mt/", "Malta's tourism sector authority"),
    "bca": ("Building and Construction Authority (BCA)", "https://bca.gov.mt/", "construction licensing and skills cards in Malta"),
    "ohsa": ("Occupational Health and Safety Authority (OHSA)", "https://ohsa.mt/", "workplace health and safety rules in Malta"),
    "mfsa": ("Malta Financial Services Authority (MFSA)", "https://www.mfsa.mt/", "regulator of Malta's financial and insurance sector"),
    "mdia": ("Malta Digital Innovation Authority (MDIA)", "https://mdia.gov.mt/", "Malta's authority for technology and digital innovation"),
    "europass": ("Europass — Create your CV", "https://europass.europa.eu/en/create-europass-cv", "the EU's free CV builder and skills profile"),
    "cefr": ("Council of Europe — CEFR language levels", "https://www.coe.int/en/web/common-european-framework-reference-languages", "the A1–C2 scale employers use for language requirements"),
}

# (keywords in slug/title, sources) — first match wins, in order.
RULES = [
    (("study", "student", "pre-departure"), ["mfhea", "um", "visa"]),
    (("budget", "third-country", "non-eu", "work-permit", "permit"), ["permit", "jobsplus", "eures"]),
    (("moving-to-malta", "documents"), ["permit", "eures", "jobsplus"]),
    (("salary", "pay"), ["nso", "dier", "cfr"]),
    (("hospitality", "hotel", "chef", "tourism"), ["mta", "its", "jobsplus"]),
    (("construction", "foreman", "engineering"), ["bca", "ohsa", "jobsplus"]),
    (("call-centre", "customer-service", "language", "centre-appels", "call-center"), ["cefr", "jobsplus", "eures"]),
    (("finance", "audit", "accounting", "insurance"), ["mfsa", "jobsplus", "nso"]),
    (("it-jobs", "tech"), ["mdia", "eurostat", "jobsplus"]),
    (("cv", "interview", "references", "follow-up"), ["europass", "jobsplus", "eures"]),
    (("temporary", "permanent", "employer", "hire", "hiring", "recruitment", "drop-off", "job-descriptions",
      "structured", "decision", "team", "roles"), ["dier", "jobsplus", "eurostat"]),
    (("industries", "jobs-in-malta", "jobs-malta", "new-jobs"), ["jobsplus", "eures", "nso"]),
]
DEFAULT = ["jobsplus", "eures", "eurostat"]

# Article topic -> job categories in the registry, for the "By the numbers" facts.
TOPIC_CATS = [
    (("hospitality", "hotel", "chef"), ["Hospitality"]),
    (("construction", "foreman"), ["Construction"]),
    (("engineering",), ["Engineering & Maintenance"]),
    (("call-centre", "customer-service", "language", "centre-appels", "call-center"), ["Customer Service"]),
    (("finance", "audit", "accounting"), ["Finance & Accounting", "Administration"]),
    (("insurance",), ["Insurance"]),
    (("it-jobs",), ["IT & Technology"]),
]

LABEL = {"en": ("Sources", "By the numbers"), "fr": ("Sources", "En chiffres"), "it": ("Fonti", "In cifre")}


def pick(rules, key, default):
    for words, value in rules:
        if any(w in key for w in words):
            return value
    return default


def yearly(salary: str) -> list[float]:
    nums = [float(n.replace(",", "")) for n in re.findall(r"€\s?([\d,]+(?:\.\d+)?)", salary)]
    if "month" in salary:
        nums = [n * 12 for n in nums]
    elif "hour" in salary:
        return []
    return nums


def money(n: float) -> str:
    return f"€{round(n / 100) * 100:,.0f}"


def job_stats() -> dict:
    reg = json.loads((ROOT / "tools" / "jobs_registry.json").read_text(encoding="utf-8"))
    jobs = [j for j in reg if j.get("status") not in ("closed", "expired")]
    by_cat: dict[str, list[dict]] = {}
    for j in jobs:
        by_cat.setdefault(j.get("category") or "Other", []).append(j)
    top = max(by_cat.items(), key=lambda kv: len(kv[1]))
    since = (TODAY - timedelta(days=14)).isoformat()
    return {"jobs": jobs, "by_cat": by_cat, "top": (top[0], len(top[1])),
            "new14": sum(1 for j in jobs if j.get("date", "") >= since),
            "salaried": [j for j in jobs if j.get("salary") and yearly(j["salary"])]}


def facts_for(key: str, st: dict) -> list[str]:
    when = f"{TODAY.day} {TODAY:%B %Y}"
    n = len(st["jobs"])
    out = [f"As of {when}, Outreach Recruitment lists {n} open jobs in Malta; the largest category is "
           f"{st['top'][0]} with {st['top'][1]} roles."]
    cats = pick(TOPIC_CATS, key, [])
    pool = [j for c in cats for j in st["by_cat"].get(c, [])]
    if pool:
        towns: dict[str, list] = {}
        for j in pool:
            t = j.get("location", "").replace(", Malta", "").strip()
            if t and t != "Malta":
                k = re.sub(r"[^a-zżċġħ]", "", t.lower().replace("'s", ""))  # "St. Julian's" == "St Julian"
                towns.setdefault(k, [t, 0])[1] += 1
        names = [v[0] for v in sorted(towns.values(), key=lambda v: -v[1])[:3]]
        where = " and ".join(names) if len(names) < 3 else f"{names[0]}, {names[1]} and {names[2]}"
        out.append(f"{len(pool)} of these are {' and '.join(cats).lower()} roles" + (f", mostly in {where}." if where else "."))
        paid = [v for j in pool if j.get("salary") for v in yearly(j["salary"])]
        if len(paid) >= 2:
            out.append(f"Where employers publish pay, our {cats[0].lower()} roles range from {money(min(paid))} to "
                       f"{money(max(paid))} a year (gross).")
            return out
    paid = [v for j in st["salaried"] for v in yearly(j["salary"])]
    if pool and st["new14"]:
        out.append(f"{st['new14']} new jobs were added in the last 14 days.")
    elif paid:
        out.append(f"{len(st['salaried'])} of our open roles publish a salary, ranging from {money(min(paid))} to "
                   f"{money(max(paid))} a year (gross); {st['new14']} new jobs were added in the last 14 days.")
    return out


def odbody_bounds(s: str) -> tuple[int, int]:
    """(start of #odBody inner HTML, index of its closing </article>)."""
    i = s.index('id="odBody">') + len('id="odBody">')
    depth, pos = 1, i
    for m in re.finditer(r"<article\b|</article>", s[i:]):
        depth += 1 if m.group() != "</article>" else -1
        if depth == 0:
            return i, i + m.start()
        pos = m.end()
    raise ValueError("unbalanced #odBody")


def sources_html(keys: list[str], lang: str) -> str:
    title = LABEL.get(lang, LABEL["en"])[0]
    items = "".join(f'<li><a href="{E(S[k][1])}" target="_blank" rel="noopener">{E(S[k][0])}</a> — {E(S[k][2])}</li>' for k in keys)
    return f'<section class="or-sources" data-or-sources><h2>{title}</h2><ul>{items}</ul></section>'


def facts_html(facts: list[str], lang: str) -> str:
    title = LABEL.get(lang, LABEL["en"])[1]
    items = "".join(f"<li>{E(f)}</li>" for f in facts)
    return (f'<div class="or-facts" data-or-facts><strong>{title}</strong><ul>{items}</ul>'
            f'<small>Source: Outreach Recruitment live job listings, updated {TODAY.day} {TODAY:%B %Y}.</small></div>')


def add_citations(s: str, keys: list[str], touch: bool) -> str:
    def fix(m):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            return m.group(0)
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else []
        hit = False
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") in ("BlogPosting", "Article", "NewsArticle"):
                node["citation"] = [{"@type": "CreativeWork", "name": S[k][0], "url": S[k][1]} for k in keys]
                if touch:
                    node["dateModified"] = f"{TODAY.isoformat()}T00:00:00Z"
                hit = True
        return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>' if hit else m.group(0)
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix, s, flags=re.S)


def process(path: Path, st: dict, facts_only: bool) -> bool:
    s = path.read_text(encoding="utf-8")
    if 'id="odBody"' not in s:
        return False
    lang = (re.search(r'<html[^>]*\blang="(\w+)"', s) or [None, "en"])[1]
    title = re.search(r"<title>(.*?)</title>", s, re.S)
    key = (path.stem + " " + (title.group(1) if title else "")).lower().replace(" ", "-")
    old = s
    # facts box: replace, or insert right after the quick-answer section (else at the top of the body).
    # English articles only — the facts are written in English.
    s = re.sub(r'<div class="or-facts" data-or-facts(?:="")?>.*?</div>', "", s, flags=re.S)
    box = facts_html(facts_for(key, st), lang) if lang == "en" else ""
    a, b = odbody_bounds(s)
    body = s[a:b]
    m = re.search(r'<div class="answer-box">.*?</div>\s*</section>', body, re.S)
    body = body[:m.end()] + box + body[m.end():] if m else box + body
    if not facts_only:
        keys = pick(RULES, key, DEFAULT)
        body = re.sub(r'<section class="or-sources" data-or-sources(?:="")?>.*?</section>', "", body, flags=re.S)
        # Articles written with their own "Sources" section (admin "Fix it for me") keep that one.
        if not re.search(r"<h2[^>]*>\s*(?:Sources|Fonti)\b", body):
            body = body.rstrip() + sources_html(keys, lang)
    s = s[:a] + body + s[b:]
    if not facts_only:
        s = add_citations(s, pick(RULES, key, DEFAULT), touch=True)
    if s != old:
        path.write_text(s, encoding="utf-8")
        return True
    return False


def main(argv: list[str]) -> None:
    facts_only = "--facts" in argv
    st = job_stats()
    files = [p for p in sorted(BLOG.glob("*.html")) if p.name != "index.html"]
    # Some slugs are also served from a root-level <slug>.html copy; keep those in step.
    files += [ROOT / p.name for p in files if (ROOT / p.name).exists()]
    if "--missing" in argv:
        files = [p for p in files if "data-or-sources" not in p.read_text(encoding="utf-8")]
    changed = [p for p in files if process(p, st, facts_only)]
    print(f"{len(changed)}/{len(files)} articles updated ({'facts' if facts_only else 'sources + facts'}); "
          f"{len(st['jobs'])} open jobs, top: {st['top'][0]}")
    if changed:
        sys.path.insert(0, str(ROOT / "tools"))
        import apply_blog_template as t
        t.main([str(p) for p in changed])
    if changed and "--commit" in argv:
        paths = sorted({str(p.relative_to(ROOT)) for p in changed} | {f"{p.stem}/index.html" for p in changed if (ROOT / p.stem / "index.html").exists()})
        git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        git("add", "--", *paths)
        if git("diff", "--cached", "--quiet").returncode:
            git("commit", "-m", f"Articles: {'refresh By the numbers facts' if facts_only else 'add Sources + By the numbers'} ({TODAY.isoformat()})")
            git("pull", "--no-rebase", "--no-edit", "origin", "main")
            r = git("push", "origin", "main")
            print("pushed" if r.returncode == 0 else f"push failed: {r.stderr.strip()[:300]}")


if __name__ == "__main__":
    main(sys.argv[1:])
