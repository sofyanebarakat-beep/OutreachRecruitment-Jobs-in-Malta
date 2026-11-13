#!/usr/bin/env python3
"""Publish due, approved Supabase articles through the site's safe static publisher."""
from __future__ import annotations
import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
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

def pillar(article):
    text = f"{article.get('focus_keyword','')} {article.get('title','')}".lower()
    if "study" in text or "student" in text: return "StudyInMalta"
    if "employer" in text or "hiring" in text or "recruit" in text: return "Employer"
    if "job" in text or "career" in text: return "JobsInMalta"
    return "Candidate"

def markdown(article):
    today = datetime.now(timezone.utc).date().isoformat()
    fields = {
        "title": article["title"], "slug": article["slug"], "pillar": pillar(article),
        "audience": "Outreach Recruitment readers", "primary_keyword": article["focus_keyword"],
        "seo_title": article["seo_title"], "meta_description": article["meta_description"],
        "date": today, "excerpt": article.get("excerpt") or "",
        "featured_image_url": article.get("featured_image_url") or "",
        "featured_image_alt": article.get("featured_image_alt") or "",
    }
    return "---\n" + "\n".join(f"{k}: {yaml_value(v)}" for k,v in fields.items()) + "\n---\n\n" + article["body"].strip() + "\n"

def main():
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
                request("PATCH",f"seo_articles?id=eq.{article['id']}",{"status":"published","published_at":datetime.now(timezone.utc).isoformat(),"published_url":result["canonical"],"updated_at":datetime.now(timezone.utc).isoformat()})
            else:
                request("PATCH",f"seo_articles?id=eq.{article['id']}",{"status":"failed","quality_notes":result["error"],"updated_at":datetime.now(timezone.utc).isoformat()})
    summary={"published":sum(r["ok"] for r in results),"failed":sum(not r["ok"] for r in results),"touched_paths":sorted({p for r in results if r["ok"] for p in r["touched"]})}
    print(json.dumps(summary));return 1 if summary["failed"] else 0

if __name__ == "__main__": sys.exit(main())
