#!/usr/bin/env python3
"""Daily SEO course automation: GSC, GA4, audits, experiments and opportunities.

Writes a local JSON report on every run. When SUPABASE_SERVICE_ROLE_KEY is set,
it also upserts the protected admin tables. Designed for the existing launchd job.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "seo-automation-latest.json"
STATE = ROOT / "tools" / "private" / "seo-automation-state.json"
SITE_URL = "https://outreachrecruitment.net/"
DEFAULT_CREDS = ROOT / "tools" / "private" / "search-console-bot.json"
GA4_ID = "G-FK09PDN6TK"
EXCLUDED = {".git", "admin", "reports", "components", "images", "SEO Emp and Candidates", "STUDY IN MALTA SKILLS"}
SECTOR_SLUGS = {
    "Hospitality": "hospitality-jobs-in-malta", "Engineering & Maintenance": "engineering-jobs-in-malta",
    "Engineering": "engineering-jobs-in-malta", "Finance & Accounting": "finance-jobs-in-malta",
    "Finance": "finance-jobs-in-malta", "IT & Technology": "it-jobs-in-malta", "IT": "it-jobs-in-malta",
    "Construction": "construction-jobs-in-malta", "Sales": "sales-jobs-in-malta",
    "Retail": "retail-jobs-in-malta", "Maritime": "marine-jobs-in-malta",
    "Manufacturing": "manufacturing-jobs-in-malta", "Insurance": "insurance-jobs-in-malta",
}


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def request_json(url: str, *, method="GET", headers=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(url, method=method, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urlopen(req, timeout=60) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except HTTPError as exc:
        raw = exc.read()
        payload = json.loads(raw) if raw else {"message": str(exc)}
        return exc.code, payload


def google_token(scopes: list[str]) -> str:
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request as GoogleRequest
    except ImportError as exc:
        raise RuntimeError("google-auth is required: python3 -m pip install google-auth") from exc
    configured = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", str(DEFAULT_CREDS))
    path = Path(configured)
    if not path.is_absolute():
        path = ROOT / path
    credentials = service_account.Credentials.from_service_account_file(path, scopes=scopes)
    credentials.refresh(GoogleRequest())
    return credentials.token


def gsc_query(token: str, start: str, end: str, dimensions: list[str], limit=25000) -> list[dict]:
    site = quote(SITE_URL, safe="")
    status, payload = request_json(
        f"https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query",
        method="POST", headers={"Authorization": f"Bearer {token}"},
        body={"startDate": start, "endDate": end, "dimensions": dimensions, "rowLimit": limit,
              "dataState": "final", "type": "web"},
    )
    if status != 200:
        raise RuntimeError(f"Search Console API {status}: {payload.get('error', {}).get('message', payload)}")
    return payload.get("rows", [])


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=[]; self.in_title=False; self.in_h1=False; self.h1=[]; self.meta=[]; self.canon=[]; self.images=[]; self.links=[]; self.schemas=[]; self._script=False; self._buf=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); tag=tag.lower()
        if tag=="title": self.in_title=True
        elif tag=="h1": self.h1.append(""); self.in_h1=True
        elif tag=="meta" and a.get("name","").lower()=="description": self.meta.append(a.get("content", "").strip())
        elif tag=="link" and "canonical" in a.get("rel","").lower(): self.canon.append(a.get("href", ""))
        elif tag=="img": self.images.append((a.get("src", ""), a.get("alt")))
        elif tag=="a" and a.get("href"): self.links.append(a["href"])
        elif tag=="script" and a.get("type","").lower()=="application/ld+json": self._script=True; self._buf=[]
    def handle_endtag(self, tag):
        if tag.lower()=="title": self.in_title=False
        elif tag.lower()=="h1": self.in_h1=False
        elif tag.lower()=="script" and self._script: self.schemas.append("".join(self._buf)); self._script=False
    def handle_data(self, data):
        if self.in_title: self.title.append(data)
        if self.in_h1 and self.h1: self.h1[-1]+=data
        if self._script: self._buf.append(data)


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html": return SITE_URL
    if rel.endswith("/index.html"): rel = rel[:-10]
    elif rel.endswith(".html"): rel = rel[:-5]
    return SITE_URL.rstrip("/") + "/" + rel


def public_html():
    for p in ROOT.rglob("*.html"):
        rel=p.relative_to(ROOT)
        if any(part in EXCLUDED for part in rel.parts) or p.stat().st_size < 5000: continue
        yield p


def audit_site() -> tuple[list[dict], dict[str, dict], dict[str, int]]:
    pages={}; titles=defaultdict(list); metas=defaultdict(list); incoming=Counter(); issues=[]
    for path in public_html():
        parser=PageParser()
        try: parser.feed(path.read_text(errors="replace"))
        except Exception: continue
        url=page_url(path); title=unescape(" ".join(parser.title)).strip(); h1=[unescape(x).strip() for x in parser.h1 if x.strip()]; meta=parser.meta[0] if parser.meta else ""
        pages[url]={"path":str(path.relative_to(ROOT)),"title":title,"h1":h1,"meta":meta,"canonical":parser.canon,"schemas":parser.schemas,"links":parser.links}
        if title: titles[title.lower()].append(url)
        if meta: metas[meta.lower()].append(url)
        for href in parser.links:
            if href.startswith("/"): incoming[SITE_URL.rstrip("/")+href.split("#")[0].rstrip("/")]+=1
        def add(kind, severity, detail): issues.append({"source_key":f"audit:{kind}:{url}","issue":detail,"severity":severity,"url":url,"owner":"SEO automation","status":"open","validation":f"Automated audit {date.today()}"})
        if not title: add("missing-title","High","Missing page title")
        if len(h1)!=1: add("h1-count","High" if not h1 else "Medium",f"Expected one H1; found {len(h1)}")
        if not meta: add("missing-meta","Medium","Missing meta description")
        if not parser.canon: add("missing-canonical","High","Missing canonical link")
        for src,alt in parser.images:
            if alt is None or not alt.strip(): add("missing-alt:"+src[:80],"Low",f"Image missing alt text: {src}")
        if "/jobs/" in url:
            valid=False
            for raw in parser.schemas:
                try:
                    obj=json.loads(raw)
                    nodes=obj.get("@graph",[]) if isinstance(obj,dict) else []
                    nodes=nodes+[obj] if isinstance(obj,dict) else nodes
                    if any(isinstance(n,dict) and n.get("@type")=="JobPosting" for n in nodes): valid=True
                except Exception: pass
            if not valid: add("jobposting","Critical","Missing or invalid JobPosting JSON-LD")
    for value, urls in titles.items():
        if len(urls)>1:
            for url in urls: issues.append({"source_key":f"audit:duplicate-title:{url}","issue":"Duplicate title: "+pages[url]["title"],"severity":"Medium","url":url,"owner":"SEO automation","status":"open","validation":f"Matches {len(urls)} pages; audit {date.today()}"})
    for value, urls in metas.items():
        if len(urls)>1:
            for url in urls: issues.append({"source_key":f"audit:duplicate-meta:{url}","issue":"Duplicate meta description","severity":"Low","url":url,"owner":"SEO automation","status":"open","validation":f"Matches {len(urls)} pages; audit {date.today()}"})
    for url in pages:
        if url != SITE_URL and incoming[url.rstrip("/")] == 0:
            issues.append({"source_key":f"audit:orphan:{url}","issue":"Orphan page: no internal links found","severity":"Medium","url":url,"owner":"SEO automation","status":"open","validation":f"Link graph audit {date.today()}"})
    # Duplicate .html and folder URLs are a common source of canonical/indexing ambiguity.
    for path in ROOT.glob("*.html"):
        folder=ROOT/path.stem/"index.html"
        if folder.exists():
            url=page_url(path); issues.append({"source_key":f"audit:duplicate-route:{url}","issue":"Both .html and folder versions exist","severity":"High","url":url,"owner":"SEO automation","status":"open","validation":f"Duplicate route audit {date.today()}"})
    robots=(ROOT/"robots.txt").read_text(errors="ignore") if (ROOT/"robots.txt").exists() else ""
    if "Sitemap:" not in robots:
        issues.append({"source_key":"audit:robots-sitemap","issue":"robots.txt does not declare a sitemap","severity":"High","url":SITE_URL+"robots.txt","owner":"SEO automation","status":"open","validation":f"Robots audit {date.today()}"})
    sitemap_text="\n".join(p.read_text(errors="ignore") for p in [ROOT/"sitemap.xml",*sorted((ROOT/"sitemaps").glob("*.xml"))] if p.exists())
    registry=json.loads((ROOT/"tools/jobs_registry.json").read_text())
    for job in registry:
        job_url=SITE_URL.rstrip("/")+"/jobs/"+job["slug"]
        if job.get("status") in ("closed","expired") and job_url in sitemap_text:
            issues.append({"source_key":f"audit:closed-in-sitemap:{job_url}","issue":"Closed job is still present in sitemap","severity":"High","url":job_url,"owner":"SEO automation","status":"open","validation":f"Sitemap audit {date.today()}"})
        sector_url=SITE_URL.rstrip("/")+"/"+SECTOR_SLUGS.get(job.get("category"),"")
        sector_page=pages.get(sector_url)
        if sector_page and job.get("status","open") not in ("closed","expired"):
            targets={x.rstrip("/") for x in sector_page["links"] if x.startswith("http")}
            targets|={SITE_URL.rstrip("/")+x.rstrip("/") for x in sector_page["links"] if x.startswith("/")}
            if job_url.rstrip("/") not in targets:
                issues.append({"source_key":f"audit:sector-link:{job_url}","issue":"Sector page does not link to this open job","severity":"Low","url":job_url,"owner":"SEO automation","status":"open","validation":f"Cluster link audit {date.today()}"})
    return issues,pages,incoming


class Supabase:
    def __init__(self):
        self.url=os.environ.get("SUPABASE_URL","").rstrip("/"); self.key=os.environ.get("SUPABASE_SERVICE_ROLE_KEY","")
        self.enabled=bool(self.url and self.key)
        self.headers={"apikey":self.key,"Authorization":f"Bearer {self.key}"}
    def get(self, table, query=""):
        if not self.enabled: return []
        status,data=request_json(f"{self.url}/rest/v1/{table}?{query}",headers=self.headers)
        if status!=200: raise RuntimeError(f"Supabase read {table} {status}: {data}")
        return data
    def upsert(self, table, rows, conflict):
        if not self.enabled or not rows: return
        status,data=request_json(f"{self.url}/rest/v1/{table}?on_conflict={quote(conflict)}",method="POST",
            headers={**self.headers,"Prefer":"resolution=merge-duplicates,return=minimal"},body=rows)
        if status not in (200,201,204): raise RuntimeError(f"Supabase upsert {table} {status}: {data}")
    def patch(self, table, query, row):
        if not self.enabled: return
        status,data=request_json(f"{self.url}/rest/v1/{table}?{query}",method="PATCH",headers={**self.headers,"Prefer":"return=minimal"},body=row)
        if status not in (200,204): raise RuntimeError(f"Supabase update {table} {status}: {data}")


def pull_gsc() -> dict:
    token=google_token(["https://www.googleapis.com/auth/webmasters.readonly"])
    end=date.today()-timedelta(days=2); start=end-timedelta(days=6); month=end-timedelta(days=27)
    daily=[]
    for row in gsc_query(token,str(start),str(end),["date"]):
        daily.append({"date":row["keys"][0],"clicks":round(row.get("clicks",0)),"impressions":round(row.get("impressions",0)),"ctr":round(row.get("ctr",0)*100,4),"avg_position":round(row.get("position",0),2),"source":"gsc"})
    queries=[]
    for row in gsc_query(token,str(month),str(end),["query"],1000):
        q=row["keys"][0]; queries.append({"source_key":"gsc:"+q,"keyword":q,"volume":round(row.get("impressions",0)),"current_position":round(row.get("position",0),2),"notes":f"GSC 28d through {end}"})
    pages=[]
    for row in gsc_query(token,str(month),str(end),["page"],2000):
        u=row["keys"][0]; pages.append({"source_key":"gsc:"+u,"url":u,"clicks":round(row.get("clicks",0)),"impressions":round(row.get("impressions",0)),"ctr":round(row.get("ctr",0)*100,4),"position":round(row.get("position",0),2),"notes":f"GSC 28d through {end}"})
    return {"daily":daily,"queries":queries,"pages":pages,"through":str(end)}


def ga4_report(property_id: str, dimensions, metrics, start="7daysAgo", end="2daysAgo", dimension_filter=None):
    token=google_token(["https://www.googleapis.com/auth/analytics.readonly"])
    body={"dateRanges":[{"startDate":start,"endDate":end}],"dimensions":[{"name":x} for x in dimensions],"metrics":[{"name":x} for x in metrics],"limit":"100000"}
    if dimension_filter: body["dimensionFilter"]=dimension_filter
    status,data=request_json(f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport",method="POST",headers={"Authorization":f"Bearer {token}"},body=body)
    if status!=200: raise RuntimeError(f"GA4 Data API {status}: {data.get('error',{}).get('message',data)}")
    return data


def pull_ga4(property_id: str) -> dict[str, dict]:
    filt={"filter":{"fieldName":"sessionDefaultChannelGroup","stringFilter":{"matchType":"EXACT","value":"Organic Search"}}}
    data=ga4_report(property_id,["date","eventName"],["activeUsers","eventCount"],dimension_filter=filt)
    out=defaultdict(lambda:{"organic_users":0,"applications":0,"employer_leads":0,"ai_referrals":0})
    for row in data.get("rows",[]):
        day,event=[x["value"] for x in row["dimensionValues"]]; users,count=[int(float(x["value"])) for x in row["metricValues"]]
        key=f"{day[:4]}-{day[4:6]}-{day[6:]}"; out[key]["organic_users"]=max(out[key]["organic_users"],users)
        if event=="apply_click": out[key]["applications"]+=count
        if event=="employer_lead_submit": out[key]["employer_leads"]+=count
    ai_filter={"filter":{"fieldName":"sessionSource","stringFilter":{"matchType":"FULL_REGEXP","value":".*(chatgpt|perplexity|gemini|copilot|claude).*","caseSensitive":False}}}
    ai=ga4_report(property_id,["date"],["sessions"],dimension_filter=ai_filter)
    for row in ai.get("rows",[]):
        day=row["dimensionValues"][0]["value"]; key=f"{day[:4]}-{day[4:6]}-{day[6:]}"; out[key]["ai_referrals"]+=int(float(row["metricValues"][0]["value"]))
    return dict(out)


def sectors(gsc_pages: list[dict]) -> list[dict]:
    registry=json.loads((ROOT/"tools/jobs_registry.json").read_text()); counts=Counter(); locations=Counter()
    for job in registry:
        if job.get("status","open") in ("closed","expired"): continue
        counts[job.get("category") or "General"]+=1; locations[job.get("location") or "Unknown"]+=1
    perf={x["url"].rstrip("/"):(x["impressions"],x["position"]) for x in gsc_pages}; rows=[]
    for sector,count in counts.most_common():
        slug=SECTOR_SLUGS.get(sector); path=(ROOT/f"{slug}.html") if slug else None; path2=(ROOT/slug/"index.html") if slug else None
        exists=bool(slug and ((path and path.exists()) or (path2 and path2.exists()))); url=SITE_URL.rstrip("/")+"/"+slug if slug else ""
        impressions,position=perf.get(url.rstrip("/"),(0,None))
        rows.append({"sector":sector,"open_jobs":count,"sector_page_exists":exists,"url":url,"impressions":impressions,"avg_position":position,"updated_at":datetime.now().isoformat()})
    return rows


def changed_experiments(gsc_pages: list[dict], since: str | None) -> tuple[list[dict],str]:
    latest=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
    if not since:
        probe=subprocess.run(["git","rev-list","-1","--before=90 days ago","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
        since=probe or latest
    log=subprocess.run(["git","log","--max-count=50","--format=%H%x09%cs%x09%s","--name-only",f"{since}..HEAD"],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    perf={x["url"].rstrip("/"):x for x in gsc_pages}; rows=[]; current=None
    for line in log.splitlines():
        if re.match(r"^[0-9a-f]{40}\t",line):
            sha,day,msg=line.split("\t",2); current=(sha,day,msg); continue
        if not current or not re.search(r"seo|title|h1|schema|faq|content|canonical|internal link|job",current[2],re.I): continue
        if not line.endswith((".html","/index.html")) or line.startswith(("admin/","reports/")): continue
        path=ROOT/line
        url=page_url(path) if path.exists() else SITE_URL.rstrip("/")+"/"+line.removesuffix("/index.html").removesuffix(".html")
        p=perf.get(url.rstrip("/"),{}); sha,day,msg=current
        reviews=[str(date.fromisoformat(day)+timedelta(days=n)) for n in (7,30,60,90)]
        rows.append({"source_key":f"git:{sha}:{url}","change":msg,"hypothesis":"Measure whether this committed page change improves organic visibility.","page":url,"start_date":day,"review_date":reviews[0],"before_data":json.dumps({k:p.get(k) for k in ("clicks","impressions","ctr","position")}),"review_schedule":reviews,"status":"monitoring","commit_sha":sha})
    return rows[:500],latest


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--no-audit",action="store_true"); parser.add_argument("--local-only",action="store_true"); args=parser.parse_args()
    load_env(ROOT/"tools/private/seo_automation.env")
    result={"generated_at":datetime.now().astimezone().isoformat(),"checks":{},"warnings":[]}
    gsc=pull_gsc(); result["checks"]["gsc"]={"ok":True,"through":gsc["through"],"days":len(gsc["daily"]),"queries":len(gsc["queries"]),"pages":len(gsc["pages"])}
    ga={}; property_id=os.environ.get("GA4_PROPERTY_ID","")
    if property_id:
        try: ga=pull_ga4(property_id); result["checks"]["ga4"]={"ok":True,"days":len(ga),"property_id":property_id}
        except Exception as exc: result["checks"]["ga4"]={"ok":False,"error":str(exc)}; result["warnings"].append(str(exc))
    else: result["checks"]["ga4"]={"ok":False,"error":"GA4_PROPERTY_ID is not configured"}
    for row in gsc["daily"]: row.update(ga.get(row["date"],{}))
    audit=[]
    if not args.no_audit:
        audit,_,_=audit_site(); result["checks"]["audit"]={"ok":True,"issues":len(audit)}
    sector_rows=sectors(gsc["pages"]); result["checks"]["sectors"]={"ok":True,"rows":len(sector_rows)}
    state={}
    if STATE.exists():
        try: state=json.loads(STATE.read_text())
        except Exception: pass
    experiments,latest=changed_experiments(gsc["pages"],state.get("last_commit")); result["checks"]["experiments"]={"new":len(experiments)}
    sb=Supabase();
    if args.local_only: sb.enabled=False
    if sb.enabled:
        old_keywords={r["source_key"]:r for r in sb.get("seo_keywords","select=source_key,current_position,baseline_position,keyword&source_key=not.is.null")}
        old_pages={r["source_key"]:r for r in sb.get("seo_pages","select=source_key,impressions,url&source_key=not.is.null")}
        old_audits={r["source_key"]:r for r in sb.get("seo_technical","select=id,source_key,status&source_key=like.audit:*")}
        alerts=[]
        for r in gsc["queries"]:
            old=old_keywords.get(r["source_key"]); prev=old.get("current_position") if old else None
            r["previous_position"]=prev
            if not old: r["baseline_position"]=r["current_position"]
            if prev is not None and r["current_position"]-float(prev)>3:
                alerts.append({"source_key":f"keyword-drop:{date.today()}:{r['source_key']}","type":"keyword_drop","severity":"High","message":f"{r['keyword']} dropped {r['current_position']-float(prev):.1f} positions","url":r.get("target_url","")})
        for r in gsc["pages"]:
            old=old_pages.get(r["source_key"])
            if old and (old.get("impressions") or 0)>0 and r["impressions"]==0:
                alerts.append({"source_key":f"page-zero:{date.today()}:{r['source_key']}","type":"lost_impressions","severity":"High","message":"Page lost all Search Console impressions","url":r["url"]})
        visible={r["url"].rstrip("/") for r in gsc["pages"] if r.get("impressions",0)>0}
        for job in json.loads((ROOT/"tools/jobs_registry.json").read_text()):
            if job.get("status","open") in ("closed","expired"): continue
            try: age=(date.today()-date.fromisoformat(job.get("date",str(date.today())))).days
            except ValueError: continue
            url=SITE_URL.rstrip("/")+"/jobs/"+job["slug"]
            if age>=7 and url.rstrip("/") not in visible:
                alerts.append({"source_key":f"not-indexed:{url}","type":"indexing_delay","severity":"High","message":f"Job has no Search Console impressions {age} days after publication","url":url})
        current_audit_keys={r["source_key"] for r in audit}
        for key,row in old_audits.items():
            if key not in current_audit_keys and row.get("status")!="validated":
                sb.patch("seo_technical",f"id=eq.{row['id']}",{"status":"validated","fix_date":str(date.today()),"validation":f"Automatically rechecked and validated {date.today()}"})
        sb.upsert("seo_kpi_daily",gsc["daily"],"date"); sb.upsert("seo_keywords",gsc["queries"],"source_key"); sb.upsert("seo_pages",gsc["pages"],"source_key")
        sb.upsert("seo_technical",audit,"source_key"); sb.upsert("seo_sector_opportunities",sector_rows,"sector"); sb.upsert("seo_experiments",experiments,"source_key"); sb.upsert("seo_alerts",alerts,"source_key")
        # On each course Day 7, create an editable weekly-summary draft if those fields are empty.
        settings=sb.get("seo_settings","select=value&key=eq.course_start")
        if settings:
            raw_start=settings[0].get("value"); raw_start=raw_start.strip('"') if isinstance(raw_start,str) else raw_start
            try:
                elapsed=(date.today()-date.fromisoformat(raw_start)).days
                week=elapsed//7+1
                if 1<=week<=16 and elapsed%7==6:
                    rows=sb.get("seo_course_weeks",f"select=data&week=eq.{week}")
                    data=(rows[0].get("data") if rows else {}) or {}; resume=data.setdefault("resume",{})
                    top_sector=sector_rows[0]["sector"] if sector_rows else "No sector data"
                    learned=[f"Search Console imported {len(gsc['queries'])} queries and {len(gsc['pages'])} pages.",f"Highest current job supply is {top_sector}.",f"The automated audit is tracking {len(audit)} current issues."]
                    issues=[x["message"] for x in alerts[:3]] or [x["issue"] for x in audit[:3]]
                    if not any(resume.get("learned") or []): resume["learned"]=learned
                    if not any(resume.get("issues") or []): resume["issues"]=(issues+["","",""])[:3]
                    if not resume.get("next"): resume["next"]="Review this draft against the weekly KPI changes and choose one measurable next action."
                    sb.upsert("seo_course_weeks",[{"week":week,"data":data}],"week")
            except (ValueError,TypeError): pass
        page_perf={r["url"].rstrip("/"):r for r in gsc["pages"]}
        monitored=sb.get("seo_experiments","select=id,page,review_schedule,review_results,status&status=eq.monitoring")
        for experiment in monitored:
            results=experiment.get("review_results") or {}; due=False
            for review_day in experiment.get("review_schedule") or []:
                if review_day<=str(date.today()) and review_day not in results:
                    perf=page_perf.get((experiment.get("page") or "").rstrip("/"),{})
                    results[review_day]={k:perf.get(k) for k in ("clicks","impressions","ctr","position")}; due=True
            if due:
                schedule=experiment.get("review_schedule") or []
                done=bool(schedule and all(x in results for x in schedule))
                sb.patch("seo_experiments",f"id=eq.{experiment['id']}",{"review_results":results,"after_data":json.dumps(results),"status":"complete" if done else "monitoring"})
        result["checks"]["supabase"]={"ok":True,"alerts":len(alerts)}
    else:
        result["checks"]["supabase"]={"ok":False,"error":"SUPABASE_SERVICE_ROLE_KEY not configured; local report only"}
    next_state={"last_run":result["generated_at"]}
    if sb.enabled: next_state["last_commit"]=latest
    elif state.get("last_commit"): next_state["last_commit"]=state["last_commit"]
    STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(next_state,indent=2)); REPORT.parent.mkdir(exist_ok=True); REPORT.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2)); return 0 if result["checks"]["gsc"]["ok"] else 1


if __name__=="__main__": raise SystemExit(main())
