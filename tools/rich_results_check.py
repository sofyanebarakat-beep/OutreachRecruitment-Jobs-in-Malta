#!/usr/bin/env python3
"""
rich_results_check.py — once a month: does Google still show each open job as a Job Posting?

For every open job page the Search Console URL Inspection API is asked for its rich-result
status. A page is a problem when it is indexed but Google detects no Job Posting, or when the
Job Posting has ERROR-level issues (warnings are counted, not repaired). Problem pages are put
into tools/page_audit.json as "google_issues", which the daily page check repairs through the
skill-driven update + pre-publish check, most serious first.

Runs on the first daily sync of each month (state: tools/rich_results.json). Force with --force.

Usage:
  python3 tools/rich_results_check.py [--force] [--dry-run]
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
STATE_PATH = ROOT / "tools" / "rich_results.json"
AUDIT_PATH = ROOT / "tools" / "page_audit.json"
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
SITE = "https://outreachrecruitment.net"


def due(force: bool = False) -> bool:
    try:
        last = json.loads(STATE_PATH.read_text(encoding="utf-8")).get("last_run", "")
    except Exception:
        last = ""
    return force or last[:7] != date.today().isoformat()[:7]


def run(force: bool = False, dry: bool = False) -> dict | None:
    """Returns a summary dict, or None when this month's check already ran."""
    if not due(force):
        return None
    from job_sync_agent import gsc_access_token, inspect_gsc_url
    from verify_job_page import real_slug

    jobs = [j for j in json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
            if j.get("status", "").lower() not in ("closed", "expired")]
    out = {"checked": 0, "job_posting_ok": 0, "warnings": 0, "not_indexed": 0, "problems": [], "error": ""}
    try:
        token = gsc_access_token()
    except Exception as e:
        out["error"] = f"Search Console login failed: {e}"[:200]
        return out

    try:
        audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except Exception:
        audit = {}
    pages = {}
    for j in jobs:
        slug = real_slug(j["slug"])
        if slug in pages:
            continue
        url = f"{SITE}/jobs/{slug}/"
        status, data = inspect_gsc_url(token, url)
        if status != 200:
            time.sleep(3)
            status, data = inspect_gsc_url(token, url)
        if status != 200:
            continue
        out["checked"] += 1
        res = data.get("inspectionResult", {})
        indexed = (res.get("indexStatusResult") or {}).get("verdict") == "PASS"
        rich = res.get("richResultsResult") or {}
        job_items = [d for d in rich.get("detectedItems", []) or []
                     if "job" in str(d.get("richResultType", "")).lower()]
        issues = [i for d in job_items for it in d.get("items", []) or [] for i in it.get("issues", []) or []]
        errors = sorted({i.get("issueMessage", "") for i in issues if i.get("severity") == "ERROR"})
        warns = {i.get("issueMessage", "") for i in issues if i.get("severity") != "ERROR"}
        out["warnings"] += len(warns)
        pages[slug] = {"indexed": indexed, "job_posting": bool(job_items), "errors": errors, "warnings": sorted(warns)}
        if not indexed:
            out["not_indexed"] += 1  # the indexing follow-up handles these
            continue
        problems = []
        if not job_items:
            problems.append("Google shows no Job Posting for this page (JobPosting structured data not recognised)")
        problems += [f"Google Job Posting error: {e}" for e in errors]
        if problems:
            out["problems"].append({"title": j["title"], "slug": slug, "url": url, "reason": "; ".join(problems)})
            st = audit.setdefault(slug, {"first_seen": date.today().isoformat(), "attempts": 0})
            st["google_issues"] = problems
        else:
            out["job_posting_ok"] += 1
            if slug in audit:
                audit[slug].pop("google_issues", None)
        time.sleep(0.3)
    if not dry:
        AUDIT_PATH.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        STATE_PATH.write_text(json.dumps({"last_run": date.today().isoformat(), "summary": {
            k: v for k, v in out.items() if k != "problems"}, "pages": pages}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    return out


if __name__ == "__main__":
    res = run(force="--force" in sys.argv, dry="--dry-run" in sys.argv)
    if res is None:
        print("Already checked this month (use --force).")
    else:
        print(json.dumps({k: v for k, v in res.items() if k != "problems"}, indent=2))
        for p in res["problems"]:
            print(f"  ✗ {p['title']}: {p['reason']}")
