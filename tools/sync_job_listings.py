#!/usr/bin/env python3
"""
sync_job_listings.py — make every place that lists jobs show only open jobs.

  1. Hub + homepage pages (*.html in the site root): remove <article class="opening-job-card">
     cards that link to a closed/expired job. (jobs/index.html is rebuilt by
     update_jobs_listing.py and keeps its intentional "Closed" cards.)
  2. "Similar jobs" carousels on job pages: swap cards that point to a closed/expired
     job for an open job, same category first.
  3. /jobs ItemList JSON-LD (the job list Google reads): rebuilt from the open jobs.
  4. Categories: every job gets a real category (tools/job_categories.py) — run first.
  5. Closed job pages show "Position Closed" with apply disabled; reopened pages are
     restored (tools/job_page_state.py).

Idempotent. Usage:
  python3 tools/sync_job_listings.py [--dry-run]
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
SITE = "https://outreachrecruitment.net"

ARTICLE_RE = re.compile(r'<article\b[^>]*class="[^"]*\bopening-job-card\b[^"]*"[^>]*>.*?</article>\s*', re.S)
CARD_RE = re.compile(
    r'<div class="similar-job-card">(?:(?!<div class="similar-job-card">).)*?'
    r'class="similar-job-apply".*?</a>\s*</div>', re.S)
JOB_HREF_RE = re.compile(r'href="/jobs/([a-z0-9-]+)/?"')
SKIP_ROOT_PAGES = {"home-test.html"}
# Pages that list jobs from every category: a closed card becomes the newest open job.
# On category hubs it becomes an open job of the same category, or is removed.
GENERAL_PAGES = {"index.html", "jobs-in-malta-top-15-opening-jobs.html", "opening-jobs-in-malta.html",
                 "salary-calculator-malta.html", "careers.html", "subcontracting-jobs-in-malta.html"}


def is_open(job: dict) -> bool:
    return job.get("status", "active").lower() not in ("closed", "expired")


def esc(s: str) -> str:
    return htmllib.escape(s, quote=True)


def hub_card(old: str, job: dict) -> str:
    """An open-job card in the same style (classes) as the card it replaces."""
    cls = re.search(r'class="([^"]*)"', old).group(1)
    meta = [job.get("employment_type", ""), job.get("category", "")]
    if job.get("salary"):
        meta.append(f"Salary Range: {job['salary']}")
    return (
        f'<article class="{cls}" data-opening-job="" data-featured="{str(bool(job.get("featured"))).lower()}" '
        f'data-latest="true" data-title="{esc((job["title"] + " " + job.get("location", "")).lower())}" '
        f'data-category="{esc(job.get("category", ""))}" data-location="{esc(job.get("location", "").lower())}" '
        f'data-date="{esc(job.get("date", ""))}"><a class="opening-job-link" href="/jobs/{job["slug"]}">'
        f'<div class="opening-card-day">New</div><img class="opening-job-logo" src="/assets/job-card-logo.jpg" '
        f'alt="Outreach Recruitment job logo"><h3 class="heading-h5">{esc(job["title"])}</h3>'
        f'<div class="opening-job-company">{esc(job.get("location", ""))}</div><div class="opening-job-meta">'
        + "".join(f"<span>{esc(x)}</span>" for x in meta if x) + "</div></a></article>"
    )


def clean_hubs(jobs: dict[str, dict], dry: bool) -> tuple[dict[str, dict], list[str], set[str]]:
    open_jobs = sorted((j for j in jobs.values() if is_open(j)), key=lambda j: j.get("date", ""), reverse=True)
    changed: dict[str, dict] = {}
    emptied: list[str] = []
    touched: set[str] = set()
    for path in sorted(ROOT.glob("*.html")):
        if path.name in SKIP_ROOT_PAGES:
            continue
        text = path.read_text(encoding="utf-8")
        cards = ARTICLE_RE.findall(text)
        if not cards:
            continue
        on_page = {m.group(1) for c in cards for m in [JOB_HREF_RE.search(c)] if m}
        general = path.name in GENERAL_PAGES
        stats = {"replaced": 0, "removed": 0}

        def swap(m: re.Match) -> str:
            card = m.group(0)
            slug = JOB_HREF_RE.search(card)
            if not slug or slug.group(1) not in jobs or is_open(jobs[slug.group(1)]):
                return card
            cat = jobs[slug.group(1)].get("category", "")
            pool = [j for j in open_jobs if j["slug"] not in on_page]
            pick = next((j for j in pool if j.get("category") == cat), None)
            if pick is None and general and pool:
                pick = pool[0]
            if pick is None:
                stats["removed"] += 1
                return ""
            on_page.add(pick["slug"])
            stats["replaced"] += 1
            trailing = card[len(card.rstrip()):]
            return hub_card(card, pick) + trailing

        new = ARTICLE_RE.sub(swap, text)
        if not ARTICLE_RE.findall(new) and not general:
            # A category hub with no open jobs of its own left: show the newest open jobs
            # rather than an empty grid.
            general, stats["replaced"], stats["removed"] = True, 0, 0
            on_page = {m.group(1) for c in cards for m in [JOB_HREF_RE.search(c)] if m}
            new = ARTICLE_RE.sub(swap, text)
        if new != text:
            changed[path.name] = stats
            if not ARTICLE_RE.findall(new):
                emptied.append(path.name)
            touched.add(path.name)
            if not dry:
                path.write_text(new, encoding="utf-8")
    return changed, emptied, touched


def fill_card(card: str, job: dict) -> str:
    slug, title = job["slug"], job["title"]
    card = JOB_HREF_RE.sub(f'href="/jobs/{slug}"', card)
    card = re.sub(r'aria-label="[^"]*"', f'aria-label="View {esc(title)} job details"', card, count=1)
    card = re.sub(r'(<span class="similar-job-title">)[^<]*(</span>)', rf"\g<1>{esc(title)}\g<2>", card)
    card = re.sub(r'(<span class="similar-job-tag">)[^<]*(</span>)',
                  rf"\g<1>{esc(job.get('category') or 'General')}\g<2>", card)
    fields = [job.get("location", ""), job.get("employment_type", "")]
    spans = iter(fields)
    card = re.sub(r'(<span class="similar-job-field">(?:<svg\b.*?</svg>)?)[^<]*(</span>)',
                  lambda m: f"{m.group(1)}{esc(next(spans, ''))}{m.group(2)}", card)
    return card


def fix_carousels(jobs: dict[str, dict], dry: bool) -> tuple[int, set[str]]:
    open_jobs = sorted((j for j in jobs.values() if is_open(j)), key=lambda j: j.get("date", ""), reverse=True)
    swaps, touched = 0, set()
    for path in sorted((ROOT / "jobs").rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if "similar-job-card" not in text:
            continue
        own = path.parent.name if path.name == "index.html" else path.stem
        cards = CARD_RE.findall(text)
        in_track = {m.group(1) for c in cards for m in [JOB_HREF_RE.search(c)] if m}
        own_cat = (jobs.get(own) or {}).get("category", "")
        new_text, n = text, 0
        for card in cards:
            m = JOB_HREF_RE.search(card)
            if m and m.group(1) in jobs and is_open(jobs[m.group(1)]):
                cat = jobs[m.group(1)].get("category") or "General"
                fixed = re.sub(r'(<span class="similar-job-tag">)[^<]*(</span>)', rf"\g<1>{esc(cat)}\g<2>", card)
                if fixed != card:  # keep the tag in step with the job's category
                    new_text = new_text.replace(card, fixed, 1)
                    n += 1
                continue
            if not m or m.group(1) not in jobs:
                continue
            pool = [j for j in open_jobs if j["slug"] not in in_track and j["slug"] != own]
            pick = next((j for j in pool if j.get("category") == own_cat), pool[0] if pool else None)
            if not pick:
                continue
            in_track.add(pick["slug"])
            new_text = new_text.replace(card, fill_card(card, pick), 1)
            n += 1
        if n:
            swaps += n
            touched.add(str(path.relative_to(ROOT)))
            if not dry:
                path.write_text(new_text, encoding="utf-8")
    return swaps, touched


def rebuild_itemlist(jobs: dict[str, dict], dry: bool) -> tuple[int, set[str]]:
    path = ROOT / "jobs" / "index.html"
    text = path.read_text(encoding="utf-8")
    open_jobs = sorted((j for j in jobs.values() if is_open(j)), key=lambda j: j.get("date", ""), reverse=True)
    for m in re.finditer(r'(<script[^>]+application/ld\+json[^>]*>)(.*?)(</script>)', text, re.S):
        if '"ItemList"' not in m.group(2):
            continue
        data = json.loads(m.group(2))
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "ItemList":
                item["numberOfItems"] = len(open_jobs)
                item["itemListElement"] = [
                    {"@type": "ListItem", "position": i, "url": f"{SITE}/jobs/{j['slug']}", "name": j["title"]}
                    for i, j in enumerate(open_jobs, 1)]
        new_block = m.group(1) + "\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n" + m.group(3)
        new = text[:m.start()] + new_block + text[m.end():]
        if new != text and not dry:
            path.write_text(new, encoding="utf-8")
        return len(open_jobs), ({"jobs/index.html"} if new != text else set())
    return 0, set()


def run(dry: bool = False) -> dict:
    import job_categories
    import job_page_state
    cats = job_categories.run(dry)
    jobs = {j["slug"]: j for j in json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))}
    removed, emptied, t1 = clean_hubs(jobs, dry)
    swaps, t2 = fix_carousels(jobs, dry)
    n_items, t3 = rebuild_itemlist(jobs, dry)
    states = job_page_state.sync_all() if not dry else {"closed": 0, "opened": 0, "touched": []}
    return {"hub_cards": removed, "hubs_now_empty": emptied, "carousel_swaps": swaps,
            "itemlist_items": n_items, "categorised": cats["changed"],
            "pages_marked_closed": states["closed"], "pages_reopened": states["opened"],
            "touched": sorted(t1 | t2 | t3 | set(cats["touched"]) | set(states["touched"]))}


if __name__ == "__main__":
    res = run(dry="--dry-run" in sys.argv)
    res["touched"] = f"{len(res['touched'])} file(s)"
    print(json.dumps(res, indent=2))
