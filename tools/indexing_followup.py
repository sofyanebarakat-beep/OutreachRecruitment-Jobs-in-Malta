#!/usr/bin/env python3
"""
indexing_followup.py — did Google pick up the jobs we published?

From 2 days after a job is published (registry "date") until Google confirms it, each
run asks the Search Console URL Inspection API whether the page is indexed and whether
Google detected a Job Posting (i.e. it can appear in Google for Jobs). Pages that are not
indexed get one more Indexing API ping. A job is followed for up to 14 days.

State: tools/indexing_followup.json  {slug: {"status": "ok"|"pending"|"gave_up", ...}}

Usage:
  python3 tools/indexing_followup.py            # check due jobs, print results
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
STATE_PATH = ROOT / "tools" / "indexing_followup.json"
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
SITE = "https://outreachrecruitment.net"
FIRST_CHECK_DAYS = 2
GIVE_UP_DAYS = 14
MAX_CHECKS_PER_RUN = 40  # URL Inspection quota is 2,000/day; stay far below it


def live_url(slug: str) -> str:
    # GitHub Pages 301-redirects /jobs/<slug> to /jobs/<slug>/, so Google indexes the slash form;
    # inspecting the no-slash URL only ever answers "Page with redirect".
    return f"{SITE}/jobs/{slug}/"


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def run(dry: bool = False) -> dict:
    """Returns {"checked": n, "ok": [...], "flagged": [...], "error": str}."""
    from job_sync_agent import gsc_access_token, inspect_gsc_url

    today = date.today()
    state = load_state()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    due = []
    for job in registry:
        if job.get("status", "").lower() in ("closed", "expired"):
            continue
        try:
            published = date.fromisoformat(str(job.get("date", ""))[:10])
        except ValueError:
            continue
        age = (today - published).days
        st = state.get(job["slug"], {})
        if age < FIRST_CHECK_DAYS or st.get("status") in ("ok", "gave_up") or age > GIVE_UP_DAYS + 7:
            continue
        if st.get("checked") == today.isoformat():
            continue
        due.append((job, age))
    due = due[:MAX_CHECKS_PER_RUN]
    out = {"checked": 0, "ok": [], "flagged": [], "error": ""}
    if not due:
        return out
    try:
        token = gsc_access_token()
    except Exception as e:
        out["error"] = f"Search Console login failed: {e}"[:200]
        return out

    repings = []
    for job, age in due:
        url = live_url(job["slug"])
        status, data = inspect_gsc_url(token, url)
        if status != 200:  # Search Console answers 500 now and then — one retry
            time.sleep(5)
            status, data = inspect_gsc_url(token, url)
        if status != 200:
            continue  # not checked; tried again next run
        out["checked"] += 1
        res = (data or {}).get("inspectionResult", {}) if status == 200 else {}
        idx = res.get("indexStatusResult", {}) or {}
        rich = res.get("richResultsResult", {}) or {}
        types = {str(i.get("richResultType", "")) for i in rich.get("detectedItems", []) or []}
        indexed = idx.get("verdict") == "PASS"
        job_posting = any("job" in t.lower() for t in types)
        coverage = idx.get("coverageState", "") or (data or {}).get("error", {}).get("message", f"HTTP {status}")
        row = {"title": job["title"], "slug": job["slug"], "url": url, "age_days": age,
               "indexed": indexed, "job_posting": job_posting, "coverage": coverage}
        st = {"checked": today.isoformat(), "published": job.get("date"), "indexed": indexed,
              "job_posting": job_posting, "coverage": coverage}
        if indexed and job_posting:
            st["status"] = "ok"
            out["ok"].append(row)
        else:
            st["status"] = "gave_up" if age >= GIVE_UP_DAYS else "pending"
            if not indexed:
                row["reason"] = f"not indexed yet ({coverage})"
                repings.append({"title": job["title"], "slug": job["slug"], "url": url,
                                "type": "URL_UPDATED", "source": "indexing_followup"})
            else:
                row["reason"] = "indexed, but Google shows no Job Posting for it (won't appear in Google Jobs)"
            if st["status"] == "gave_up":
                row["reason"] += f" — still missing after {age} days, needs a manual look"
            out["flagged"].append(row)
        state[job["slug"]] = st

    if repings and not dry:
        try:
            from job_sync_agent import submit_google_indexing
            submit_google_indexing(repings)
        except Exception:
            pass
    if not dry:
        STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    print(json.dumps(run(dry="--dry-run" in sys.argv), indent=2, ensure_ascii=False))
