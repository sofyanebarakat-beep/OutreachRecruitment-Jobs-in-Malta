#!/usr/bin/env python3
"""
article_checkup.py — 30-day check-up for blog articles from Google Search Console.

For every article (blog/*.html, canonical /<slug>/) it reads the last 28 days of clicks, impressions,
CTR and average position, plus the top search query, and flags articles that need attention:
  • low-ctr      — live 30+ days, 100+ impressions, CTR under 1.5%  → rewrite the SEO title / description
  • page-two     — live 30+ days, average position 8–20             → strengthen the content / internal links
  • not-found    — live 30+ days, under 20 impressions              → check the topic, keyword and links
Writes reports/article-checkup.json, which the SEO admin (/admin/seo → Articles → 30-day check-up) shows.

Usage: python3 tools/article_checkup.py [--commit]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
OUT = ROOT / "reports" / "article-checkup.json"
SITE = "https://outreachrecruitment.net/"


def articles() -> list[dict]:
    out = []
    for p in sorted((ROOT / "blog").glob("*.html")):
        if p.name == "index.html":
            continue
        s = p.read_text(encoding="utf-8")
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', s) or re.search(r'<link href="([^"]+)" rel="canonical"', s)
        title = re.search(r'<h1 class="od-title">(.*?)</h1>', s, re.S) or re.search(r"<title>(.*?)</title>", s, re.S)
        pub = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})', s)
        seo = re.search(r"<title>(.*?)</title>", s, re.S)
        out.append({"slug": p.stem, "url": (canon.group(1) if canon else f"{SITE}{p.stem}/"),
                    "title": re.sub(r"<[^>]+>|\s+", " ", title.group(1)).strip() if title else p.stem,
                    "seo_title": re.sub(r"\s+", " ", seo.group(1)).strip() if seo else "",
                    "published": pub.group(1) if pub else None})
    return out


def query(token: str, body: dict) -> list[dict]:
    from job_sync_agent import google_api_post
    site = quote(SITE, safe="")
    status, data = google_api_post(f"https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query", token, body)
    if status != 200:
        raise RuntimeError(f"Search Console API {status}: {str(data)[:300]}")
    return data.get("rows", [])


def main(argv: list[str]) -> int:
    from seo_course_automation import google_token
    token = google_token(["https://www.googleapis.com/auth/webmasters.readonly"])
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=27)
    base = {"startDate": start.isoformat(), "endDate": end.isoformat(), "type": "web", "rowLimit": 5000}
    # Articles moved from /blog/<slug>(.html) to /<slug>/ on 2026-11-10: Google still reports many
    # impressions under the old addresses, so every address variant counts towards the article.
    def key_of(url: str) -> str:
        path = url.replace(SITE, "/").split("?")[0].split("#")[0]
        return re.sub(r"^/(blog/)?|\.html$|/$", "", path)
    pages: dict[str, dict] = {}
    for r in query(token, {**base, "dimensions": ["page"]}):
        g = pages.setdefault(key_of(r["keys"][0]), {"clicks": 0, "impressions": 0, "pos_x_impr": 0.0})
        g["clicks"] += r["clicks"]; g["impressions"] += r["impressions"]; g["pos_x_impr"] += r["position"] * r["impressions"]
    top: dict[str, dict] = {}
    for r in query(token, {**base, "dimensions": ["page", "query"], "rowLimit": 25000}):
        k = key_of(r["keys"][0])
        q = top.setdefault(k, {})
        q[r["keys"][1]] = q.get(r["keys"][1], 0) + r["impressions"]
    rows = []
    for a in articles():
        key = a["slug"]
        g = pages.get(key, {})
        clicks, impr = int(g.get("clicks", 0)), int(g.get("impressions", 0))
        ctr = clicks / impr if impr else 0.0
        pos = g["pos_x_impr"] / impr if impr else 0.0
        days = (date.today() - datetime.strptime(a["published"], "%Y-%m-%d").date()).days if a["published"] else None
        flags = []
        if days is not None and days >= 30:
            if impr >= 100 and ctr < 0.015:
                flags.append(("low-ctr", "Many people see it in Google but few click — rewrite the SEO title and meta description around the top search query."))
            if impr >= 20 and 8 <= pos <= 20:
                flags.append(("page-two", "It sits on page 2 of Google — add facts, a clearer quick answer and links from related articles to move it up."))
            if impr < 20:
                flags.append(("not-found", "Google barely shows it — check that the topic matches what people search, the keyword is in the title, and other pages link to it."))
        rows.append({**a, "days_live": days, "clicks": clicks, "impressions": impr, "ctr": round(ctr * 100, 2),
                     "position": round(pos, 1), "top_query": max(top[key], key=top[key].get) if top.get(key) else "",
                     "flags": [f for f, _ in flags], "advice": [m for _, m in flags]})
    rows.sort(key=lambda r: (-len(r["flags"]), -r["impressions"]))
    OUT.write_text(json.dumps({"generated": datetime.now().isoformat(timespec="minutes"), "period": f"{start} to {end}",
                               "articles": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    flagged = sum(1 for r in rows if r["flags"])
    print(f"article check-up: {len(rows)} articles, {flagged} flagged ({start} → {end})")
    if "--commit" in argv:
        git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        git("add", "--", str(OUT.relative_to(ROOT)))
        if git("diff", "--cached", "--quiet").returncode:
            git("commit", "-m", f"Article 30-day check-up ({date.today().isoformat()})")
            git("pull", "--no-rebase", "--no-edit", "origin", "main")
            r = git("push", "origin", "main")
            print("pushed" if r.returncode == 0 else f"push failed: {r.stderr.strip()[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
