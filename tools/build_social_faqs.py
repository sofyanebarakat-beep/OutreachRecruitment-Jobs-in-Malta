#!/usr/bin/env python3
"""
build_social_faqs.py — collect the site's FAQ questions for Admin › Social Media › FAQ posts.

Reads every FAQPage JSON-LD block on the site and writes admin/faq-posts.json:
  general: questions that appear on 2+ pages (agency / study / hiring questions), with a source page
  jobs:    questions from OPEN job pages only (closed jobs are skipped), with the job's address
Run by tools/daily_job_sync.py every morning, so job questions follow the open jobs.

Usage: python3 tools/build_social_faqs.py
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "admin" / "faq-posts.json"
REGISTRY = ROOT / "tools" / "jobs_registry.json"
JSONLD_RE = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', re.S | re.I)
SKIP_DIRS = {".git", "admin", "reports", "node_modules", "tools", "components"}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    rel = rel[:-len("/index.html")] if rel.endswith("/index.html") else rel[:-5] if rel.endswith(".html") else rel
    return "/" + rel if rel != "index" else "/"


def faqs(path: Path) -> list[tuple[str, str]]:
    out = []
    for block in JSONLD_RE.findall(path.read_text(encoding="utf-8", errors="replace")):
        try:
            data = json.loads(block)
        except Exception:
            continue
        for item in data if isinstance(data, list) else data.get("@graph", [data]):
            if isinstance(item, dict) and item.get("@type") == "FAQPage":
                for q in item.get("mainEntity", []) or []:
                    a = q.get("acceptedAnswer") or {}
                    qq, aa = clean(q.get("name", "")), clean(a.get("text", "") if isinstance(a, dict) else "")
                    if qq and aa:
                        out.append((qq, aa))
    return out


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    open_jobs = {j["slug"]: j for j in registry if j.get("status", "").lower() not in ("closed", "expired")}

    count: Counter = Counter()
    answer: dict[str, str] = {}
    sources: dict[str, list[str]] = defaultdict(list)
    job_faqs = []
    for path in sorted(ROOT.rglob("*.html")):
        parts = path.relative_to(ROOT).parts
        # Skip tooling / working folders (e.g. "STUDY IN MALTA SKILLS") — only real site pages.
        if parts[0] in SKIP_DIRS or any(" " in p or p[:1].isupper() for p in parts[:-1]) or path.stat().st_size < 5000:
            continue
        slug = (parts[1][:-5] if parts[1].endswith(".html") else parts[1]) if parts[0] == "jobs" and len(parts) > 1 else None
        for q, a in faqs(path):
            count[q] += 1
            answer.setdefault(q, a)
            sources[q].append(page_url(path))
            if slug and slug in open_jobs:
                job_faqs.append({"q": q, "a": a, "slug": slug, "title": open_jobs[slug]["title"]})

    def topic_link(q: str, srcs: list[str]) -> str:
        ql = q.lower()
        if re.search(r"\bstud(y|ying|ent)|course|school|universit", ql):
            return "/study-in-malta-complete-guide"
        if re.search(r"\bhire|hiring|my business|source|employer|recruit for", ql):
            return "/employers"
        if re.search(r"contact|different question", ql):
            return "/contact-us"
        return next((s for s in srcs if not s.startswith("/jobs") and s not in ("/", "/index")), "/jobs")

    general = []
    for q, n in count.most_common():
        if n < 2:
            continue
        general.append({"q": q, "a": answer[q], "url": topic_link(q, sources[q]), "pages": n})
    common = {q for q, n in count.items() if n >= 20}  # agency questions repeated on every job page

    seen, jobs_out = set(), []
    for f in job_faqs:  # one entry per (job, question); only job-specific questions
        key = (f["slug"], f["q"].lower())
        if f["q"] in common:
            continue
        if key not in seen:
            seen.add(key)
            jobs_out.append(f)

    OUT.write_text(json.dumps({"general": general, "jobs": jobs_out}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"faq-posts.json: {len(general)} general question(s), {len(jobs_out)} question(s) from open job pages")


if __name__ == "__main__":
    main()
