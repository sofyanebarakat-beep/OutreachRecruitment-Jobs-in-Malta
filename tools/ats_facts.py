#!/usr/bin/env python3
"""
ats_facts.py — read one careers-page job and turn it into a fact sheet.

The fact sheet is the single source the job-seo-generator works from, so
nothing on a job page is guessed: city, employment type, dates and salary come
from the ATS JobPosting JSON-LD, and salary / work mode / languages /
experience are also read from the description text.

Fact sheets are saved as tools/ats_snapshots/<uuid>.json; yesterday's copy is
what the daily sync compares against to spot changed jobs.

Usage:
  python3 tools/ats_facts.py <uuid> [<uuid> ...]    # print fact sheets
"""
from __future__ import annotations

import hashlib
import html as htmllib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "tools" / "ats_snapshots"
ATS = "https://outreach-recruitment-agency.careers-page.com"

JSONLD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)

LANGUAGES = ["English", "Maltese", "Italian", "German", "French", "Spanish", "Portuguese", "Dutch",
             "Swedish", "Norwegian", "Danish", "Finnish", "Polish", "Russian", "Arabic", "Greek",
             "Turkish", "Hebrew", "Chinese", "Mandarin", "Japanese", "Korean", "Hindi", "Romanian",
             "Hungarian", "Czech", "Serbian", "Croatian", "Bulgarian", "Ukrainian", "Filipino", "Tagalog"]

UNIT_WORDS = [
    ("HOUR", r"per\s*hour|an\s*hour|/\s*h(?:ou)?r\b|p/?h\b|hourly|ph\b"),
    ("DAY", r"per\s*day|/\s*day|daily"),
    ("WEEK", r"per\s*week|/\s*week|weekly"),
    ("MONTH", r"per\s*month|a\s*month|/\s*month|monthly|p\.?m\.?\b|/\s*mo\b"),
    ("YEAR", r"per\s*(?:annum|year)|a\s*year|/\s*y(?:ea)?r\b|annual(?:ly)?|yearly|p\.?a\.?\b"),
]
NUM = r"(\d{1,3}(?:[,.\s]\d{3})+|\d+(?:\.\d+)?)\s*([kK])?"
CURRENCY = r"(?:€|EUR\b|euros?\b)"
RANGE_RE = re.compile(
    rf"(?:{CURRENCY}\s*)?{NUM}\s*(?:{CURRENCY}\s*)?(?:-|–|—|to|and)\s*(?:{CURRENCY}\s*)?{NUM}\s*(?:{CURRENCY})?", re.I)
SINGLE_RE = re.compile(rf"{CURRENCY}\s*{NUM}|{NUM}\s*{CURRENCY}", re.I)


def _num(raw: str, k: str | None) -> float:
    raw = raw.strip()
    if re.fullmatch(r"\d{1,3}(?:[,.\s]\d{3})+", raw):
        raw = re.sub(r"[,.\s]", "", raw)
    value = float(raw)
    return value * 1000 if k else value


def _unit_near(text: str) -> str | None:
    for unit, pattern in UNIT_WORDS:
        if re.search(pattern, text, re.I):
            return unit
    return None


def _guess_unit(value: float) -> str:
    return "HOUR" if value < 100 else "MONTH" if value < 10000 else "YEAR"


def salary_from_text(text: str) -> dict | None:
    """Find a € salary written in the description. Returns None when there is none."""
    candidates = []
    for m in RANGE_RE.finditer(text):
        if not re.search(CURRENCY, m.group(0), re.I) and not re.search(
                r"salary|pay|wage|rate|€", text[max(0, m.start() - 60):m.start()], re.I):
            continue
        lo, hi = _num(m.group(1), m.group(2)), _num(m.group(3), m.group(4))
        if not (5 <= lo <= hi <= 500000):
            continue
        candidates.append((m, lo, hi))
    if not candidates:
        for m in SINGLE_RE.finditer(text):
            raw, k = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
            v = _num(raw, k)
            if 5 <= v <= 500000:
                candidates.append((m, v, v))
    if not candidates:
        return None
    m, lo, hi = candidates[0]
    around = text[m.start(): m.end() + 40]
    unit = _unit_near(around) or _unit_near(text[max(0, m.start() - 60): m.end() + 60]) or _guess_unit(hi)
    return {"min": lo, "max": hi, "currency": "EUR", "unit": unit,
            "text": re.sub(r"\s+", " ", text[max(0, m.start() - 30): m.end() + 30]).strip(),
            "source": "description"}


def salary_from_schema(posting: dict) -> dict | None:
    base = posting.get("baseSalary")
    if not isinstance(base, dict):
        return None
    value = base.get("value", {})
    if isinstance(value, (int, float, str)):
        value = {"value": value}
    lo = value.get("minValue", value.get("value"))
    hi = value.get("maxValue", lo)
    try:
        lo, hi = float(lo), float(hi)
    except (TypeError, ValueError):
        return None
    if lo <= 0:
        return None
    return {"min": lo, "max": hi, "currency": base.get("currency", "EUR"),
            "unit": (value.get("unitText") or _guess_unit(hi)).upper(), "text": "", "source": "ats_schema"}


def html_to_text(fragment: str) -> str:
    fragment = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", fragment, flags=re.I)
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"[ \t\xa0]+", " ", re.sub(r"\n\s*\n+", "\n", text)).strip()


def work_mode(title: str, text: str) -> str:
    blob = f"{title}\n{text}".lower()
    if "fully remote" in blob or re.search(r"\bremote (?:role|position|work)\b", blob):
        return "Remote"
    if "hybrid" in blob:
        return "Hybrid"
    return "On-site"


def languages(text: str) -> list[str]:
    found = []
    for lang in LANGUAGES:
        for m in re.finditer(rf"\b{lang}\b", text):
            ctx = text[max(0, m.start() - 90): m.end() + 90].lower()
            if re.search(r"speak|fluen|language|proficien|native|written|spoken|knowledge of|command of", ctx):
                found.append(lang)
                break
    return found


def experience(text: str) -> str:
    m = re.search(r"(\d+)\s*\+?\s*(?:-|–|to)?\s*(\d+)?\s*\+?\s*years?['’]?\s*(?:of\s+)?(?:[\w-]+\s+){0,4}?experience",
                  text, re.I)
    if m:
        return m.group(0).strip()
    m = re.search(r"[^.\n]*\bexperience\b[^.\n]*", text, re.I)
    return m.group(0).strip()[:200] if m else ""


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_job_page(uuid: str, page_html: str) -> dict:
    posting: dict = {}
    for block in JSONLD_RE.findall(page_html):
        try:
            data = json.loads(block)
        except Exception:
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                posting = item
    desc_html = posting.get("description", "")
    text = html_to_text(htmllib.unescape(desc_html)) if desc_html else ""
    address = (posting.get("jobLocation") or {}).get("address", {}) if isinstance(
        posting.get("jobLocation"), dict) else {}
    title = htmllib.unescape(posting.get("title", "")).strip()
    salary = salary_from_schema(posting) or salary_from_text(text)
    etype = posting.get("employmentType", "")
    etype = etype[0] if isinstance(etype, list) and etype else etype
    return {
        "uuid": uuid,
        "title": title,
        "city": htmllib.unescape(address.get("addressLocality", "")).strip(),
        "region": address.get("addressRegion", ""),
        "country": address.get("addressCountry", "Malta") or "Malta",
        "employment_type": {"FULL_TIME": "Full-time", "PART_TIME": "Part-time", "CONTRACTOR": "Contract",
                            "TEMPORARY": "Temporary", "INTERN": "Internship"}.get(str(etype), "Full-time"),
        "date_posted": str(posting.get("datePosted", ""))[:10],
        "salary": salary,
        "salary_note": "" if salary else "No salary given on the careers page — page must say 'Competitive salary'.",
        "work_mode": work_mode(title, text),
        "languages": languages(text),
        "experience": experience(text),
        "description_text": text,
        "description_html": desc_html,
        "description_hash": hashlib.sha256(normalize(text).encode()).hexdigest()[:16],
        "ats_url": f"{ATS}/jobs/{uuid}",
        "apply_url": f"{ATS}/jobs/{uuid}/apply",
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
    }


def salary_label(salary: dict | None) -> str:
    if not salary:
        return "Competitive salary"
    unit = {"HOUR": "per hour", "DAY": "per day", "WEEK": "per week", "MONTH": "per month",
            "YEAR": "per year"}.get(salary["unit"], "")
    fmt = lambda v: f"€{v:,.2f}".replace(".00", "") if v < 100 else f"€{v:,.0f}"
    amount = fmt(salary["min"]) if salary["min"] == salary["max"] else f"{fmt(salary['min'])}–{fmt(salary['max'])}"
    return f"{amount} {unit}".strip()


def snapshot_path(uuid: str) -> Path:
    return SNAPSHOT_DIR / f"{uuid}.json"


def load_snapshot(uuid: str) -> dict | None:
    try:
        return json.loads(snapshot_path(uuid).read_text(encoding="utf-8"))
    except Exception:
        return None


def save_snapshot(facts: dict) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = snapshot_path(facts["uuid"])
    path.write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def changes_between(old: dict, new: dict) -> list[str]:
    """Human-readable list of meaningful differences (title, city, salary, description)."""
    out = []
    if normalize(old.get("title", "")) != normalize(new.get("title", "")):
        out.append(f"title: '{old.get('title')}' → '{new.get('title')}'")
    if normalize(old.get("city", "")) != normalize(new.get("city", "")):
        out.append(f"city: '{old.get('city')}' → '{new.get('city')}'")
    if salary_label(old.get("salary")) != salary_label(new.get("salary")):
        out.append(f"salary: {salary_label(old.get('salary'))} → {salary_label(new.get('salary'))}")
    if old.get("employment_type") != new.get("employment_type"):
        out.append(f"employment type: {old.get('employment_type')} → {new.get('employment_type')}")
    if old.get("description_hash") != new.get("description_hash"):
        out.append("job description text changed")
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from daily_job_sync import fetch  # noqa: E402
    for uid in sys.argv[1:]:
        status, body = fetch(f"{ATS}/jobs/{uid}")
        if status != 200:
            print(f"{uid}: HTTP {status}")
            continue
        facts = parse_job_page(uid, body)
        facts.pop("description_html")
        facts["description_text"] = facts["description_text"][:300] + " …"
        print(json.dumps(dict(facts, salary_label=salary_label(facts["salary"])), indent=2, ensure_ascii=False))
