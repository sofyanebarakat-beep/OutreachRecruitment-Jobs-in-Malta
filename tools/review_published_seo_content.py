#!/usr/bin/env python3
"""Complete due 7/30/60-day article reviews from imported Search Console data."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from urllib.parse import quote
from tools.publish_scheduled_seo_articles import request

def main():
    now=quote(datetime.now(timezone.utc).isoformat())
    reviews=request("GET",f"seo_content_reviews?select=*&status=eq.pending&due_at=lte.{now}") or []
    completed=0
    for review in reviews:
        articles=request("GET",f"seo_articles?select=published_url&id=eq.{review['article_id']}") or []
        if not articles or not articles[0].get("published_url"): continue
        url=quote(articles[0]["published_url"],safe="")
        pages=request("GET",f"seo_pages?select=clicks,impressions,ctr,position&url=eq.{url}&limit=1") or []
        metric=pages[0] if pages else {}
        impressions=int(metric.get("impressions") or 0);position=float(metric.get("position") or 0)
        recommendation=("Improve the title and meta description to lift CTR." if impressions>=100 and float(metric.get("ctr") or 0)<2 else "Add internal links and expand useful sections." if position>10 else "Performance is healthy; preserve the page and monitor.")
        request("PATCH",f"seo_content_reviews?id=eq.{review['id']}",{**metric,"status":"complete","recommendation":recommendation,"updated_at":datetime.now(timezone.utc).isoformat()});completed+=1
    print(json.dumps({"due":len(reviews),"completed":completed}))
if __name__=="__main__": main()
