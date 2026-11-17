#!/usr/bin/env python3
"""Publish due, approved Supabase articles through the site's safe static publisher."""
from __future__ import annotations
import importlib.util
import base64
import json
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = ROOT / "SEO Emp and Candidates" / "automation" / "publish_article.py"

def request(method: str, path: str, body=None):
    base, key = os.environ["SUPABASE_URL"].rstrip("/"), os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    data = json.dumps(body).encode() if body is not None else None
    req = Request(base + "/rest/v1/" + path, data=data, method=method, headers={"apikey":key,"Authorization":f"Bearer {key}","Content-Type":"application/json","Prefer":"return=representation"})
    with urlopen(req, timeout=45) as response:
        raw = response.read()
        return json.loads(raw) if raw else None

def yaml_value(value):
    return json.dumps(str(value or ""), ensure_ascii=False)

CATEGORY_PILLAR = {"Jobs in Malta": "JobsInMalta", "Study in Malta": "StudyInMalta",
                   "Employers": "Employer", "Candidates": "Candidate"}

def pillar(article):
    # The category chosen in the dashboard decides where the article is filed.
    if article.get("category") in CATEGORY_PILLAR: return CATEGORY_PILLAR[article["category"]]
    text = f"{article.get('focus_keyword','')} {article.get('title','')}".lower()
    if "study" in text or "student" in text: return "StudyInMalta"
    if "employer" in text or "hiring" in text or "recruit" in text: return "Employer"
    if "job" in text or "career" in text: return "JobsInMalta"
    return "Candidate"

def markdown(article):
    today = datetime.now(timezone.utc).date().isoformat()
    # Republishing an already-published article keeps its original date and records today as "updated".
    first = (article.get("published_at") or "")[:10] or today
    fields = {
        "title": article["title"], "slug": article["slug"], "pillar": pillar(article),
        "audience": "Outreach Recruitment readers", "primary_keyword": article["focus_keyword"],
        "seo_title": article["seo_title"], "meta_description": article["meta_description"],
        "date": first, "updated": today, "excerpt": article.get("excerpt") or "",
        "featured_image_url": article.get("featured_image_url") or "",
        "featured_image_alt": article.get("featured_image_alt") or "",
        "author_name": article.get("author_name") or "Outreach Recruitment",
        "reviewed_by": next((r.get("by","") for r in (article.get("validation_results") or []) if isinstance(r, dict) and r.get("type")=="human_review"), ""),
        "reviewed_at": next((r.get("at","") for r in (article.get("validation_results") or []) if isinstance(r, dict) and r.get("type")=="human_review"), ""),
        "section_images_b64": base64.urlsafe_b64encode(json.dumps(article.get("section_images") or []).encode()).decode(),
    }
    body = article["body"]
    # AI-generated bodies sometimes store line breaks as the two characters "\n".
    if "\\n" in body and body.count("\\n") >= body.count("\n"):
        body = body.replace("\\r\\n", "\n").replace("\\n", "\n").replace('\\"', '"')
    return "---\n" + "\n".join(f"{k}: {yaml_value(v)}" for k,v in fields.items()) + "\n---\n\n" + body.strip() + "\n"

def rebuild_news_pages():
    """Re-render /news-updates and the category pages (/news-updates/jobs-in-malta/) from blog/."""
    import subprocess
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "build_news_page.py")], cwd=ROOT, capture_output=True, text=True)
    if run.returncode:
        print("warning: build_news_page.py failed: " + (run.stderr or run.stdout)[-500:], file=sys.stderr); return []
    return ["news-updates.html"] + sorted(str(p.relative_to(ROOT)) for p in (ROOT / "news-updates").glob("*/index.html"))

def take_offline():
    """Articles the admin marked "Take offline" (status=rejected while still having a published_url):
    replace the page with a redirect to the chosen related article and remove it from the blog page,
    sitemap and News & Updates. Returns the touched paths."""
    import re
    rows = request("GET", "seo_articles?select=id,slug,canonical_url,title&status=eq.rejected&published_url=not.is.null") or []
    touched = set()
    for a in rows:
        slug = a.get("slug") or ""
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            continue
        target = (a.get("canonical_url") or "").replace("https://outreachrecruitment.net", "") or "/news-updates"
        if not target.startswith("/") or target.strip("/") == slug:
            target = "/news-updates"
        stub = (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8"/>\n<title>Redirecting… | Outreach Recruitment</title>\n'
                f'<link rel="canonical" href="https://outreachrecruitment.net{target}"/>\n<meta http-equiv="refresh" content="0; url={target}"/>\n'
                f'<meta name="robots" content="noindex,follow"/>\n</head>\n<body>\n<p>This article has moved. If you are not redirected automatically, '
                f'<a href="{target}">continue here</a>.</p>\n</body>\n</html>\n')
        for rel in (f"blog/{slug}.html",):
            if (ROOT / rel).exists():
                (ROOT / rel).unlink(); touched.add(rel)
        for rel in (f"{slug}/index.html", f"{slug}.html"):
            if (ROOT / rel).exists() or rel.endswith("/index.html"):
                (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
                (ROOT / rel).write_text(stub); touched.add(rel)
        idx = ROOT / "blog" / "index.html"
        t = idx.read_text()
        t2 = re.sub(rf'<article class="article-card[^"]*"[^>]*>(?:(?!</article>).)*?href="/{re.escape(slug)}/".*?</article>', "", t, flags=re.S)
        if t2 != t:
            idx.write_text(t2); touched.add("blog/index.html")
        for sm in ("sitemaps/sitemap-blog.xml", "sitemaps/sitemap-pages.xml"):
            x = (ROOT / sm).read_text()
            x2 = re.sub(rf"\s*<url>\s*<loc>https://outreachrecruitment\.net/{re.escape(slug)}/?</loc>.*?</url>", "", x, flags=re.S)
            if x2 != x:
                (ROOT / sm).write_text(x2); touched.add(sm)
        now = datetime.now(timezone.utc)
        request("PATCH", f"seo_articles?id=eq.{a['id']}", {"published_url": None, "updated_at": now.isoformat(),
                "quality_notes": f"Taken offline on {now.date().isoformat()}; /{slug}/ redirects to {target}"})
    return sorted(touched)

def main():
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("::warning::SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY repository secrets are not set; nothing to publish.", file=sys.stderr)
        print(json.dumps({"published":0,"failed":0,"touched_paths":[]})); return 0
    now = quote(datetime.now(timezone.utc).isoformat())
    query = f"seo_articles?select=*&status=in.(approved,scheduled)&or=(scheduled_at.is.null,scheduled_at.lte.{now})&order=scheduled_at.asc.nullsfirst"
    articles = request("GET", query) or []
    spec = importlib.util.spec_from_file_location("outreach_publisher", PUBLISHER)
    publisher = importlib.util.module_from_spec(spec); spec.loader.exec_module(publisher)
    results=[]
    with tempfile.TemporaryDirectory(prefix="outreach-seo-") as tmp:
        for article in articles:
            problems=[]
            for field in ("title","slug","focus_keyword","seo_title","meta_description","body","featured_image_url","featured_image_alt","service_id"):
                if not article.get(field): problems.append(field)
            if problems:
                results.append({"id":article["id"],"ok":False,"error":"Missing: "+", ".join(problems)});continue
            draft=Path(tmp)/f"{article['slug']}.md";draft.write_text(markdown(article))
            result=publisher.publish_one(draft);result["id"]=article["id"];results.append(result)
            if result["ok"]:
                published_at=datetime.now(timezone.utc)
                request("PATCH",f"seo_articles?id=eq.{article['id']}",{"status":"published","published_at":article.get("published_at") or published_at.isoformat(),"published_url":result["canonical"],"updated_at":published_at.isoformat()})
                for days,period in ((7,"7d"),(30,"30d"),(60,"60d")):
                    try: request("POST","seo_content_reviews?on_conflict=article_id,review_period",{"article_id":article["id"],"review_period":period,"due_at":(published_at+timedelta(days=days)).isoformat(),"status":"pending"})
                    except Exception: pass
                try: request("POST","seo_automation_logs",{"job_name":"Google indexing request prepared","status":"success","message":result["canonical"],"article_id":article["id"],"ended_at":published_at.isoformat()})
                except Exception: pass
            else:
                request("PATCH",f"seo_articles?id=eq.{article['id']}",{"status":"failed","quality_notes":result["error"],"updated_at":datetime.now(timezone.utc).isoformat()})
    touched={p for r in results if r["ok"] for p in r["touched"]}
    try: touched.update(take_offline())
    except Exception as exc: print(f"warning: take-offline step failed: {exc}", file=sys.stderr)
    if touched: touched.update(rebuild_news_pages())
    summary={"published":sum(r["ok"] for r in results),"failed":sum(not r["ok"] for r in results),"touched_paths":sorted(touched)}
    print(json.dumps(summary));return 1 if summary["failed"] else 0

if __name__ == "__main__": sys.exit(main())
