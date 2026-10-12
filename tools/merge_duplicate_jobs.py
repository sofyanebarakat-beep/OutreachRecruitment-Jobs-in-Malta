#!/usr/bin/env python3
"""
merge_duplicate_jobs.py — one careers-page job = one registry entry = one address.

Groups registry entries that share a careers-page ID (the uuid in apply_url). For each group:
  - keeps ONE entry: the one with a full page (not a redirect stub), preferring the open one,
    then the most recently updated; it takes the newest title / city / salary / dates
  - the job is open if any entry in the group was open (the careers page decides tomorrow anyway)
  - every other entry is removed; its address becomes a permanent redirect to the kept page
    (meta refresh 0 + canonical + location.replace — GitHub Pages cannot send a real 301)
  - links across the site are rewritten to point straight at the kept address
  - old → new addresses are recorded in tools/job_redirects.json

Entries marked "replaced_by" (a careers-page ID that changed into a different job) are not
duplicates and are left alone.

Usage:
  python3 tools/merge_duplicate_jobs.py [--dry-run]
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
REDIRECTS_PATH = ROOT / "tools" / "job_redirects.json"
SITE = "https://outreachrecruitment.net"
OPEN_VALID_THROUGH = "2029-12-30"
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
SKIP_DIRS = {".git", "node_modules", "reports", "admin", "components", "images", "assets"}


def is_open(j: dict) -> bool:
    return j.get("status", "active").lower() not in ("closed", "expired")


def stub_html(title: str, target: str) -> str:
    url = f"{SITE}/jobs/{target}"
    t = htmllib.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="0; url={url}"/>
<link rel="canonical" href="{url}"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{t} | Outreach Recruitment</title>
<script>window.location.replace("{url}");</script>
</head>
<body>
<p>This page has moved. If you are not redirected automatically, <a href="{url}">click here</a>.</p>
</body>
</html>
"""


def has_own_page(slug: str) -> bool:
    for f in (ROOT / "jobs" / f"{slug}.html", ROOT / "jobs" / slug / "index.html"):
        if f.exists() and f.stat().st_size > 5000:
            return True
    return False


def plan(registry: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for j in registry:
        m = UUID_RE.search(j.get("apply_url", ""))
        if m and not j.get("replaced_by"):
            groups[m.group(0)].append(j)
    merges = []
    for uuid, entries in groups.items():
        if len(entries) < 2:
            continue
        ranked = sorted(entries, key=lambda j: (has_own_page(j["slug"]), is_open(j),
                                                j.get("lastmod", "") or j.get("date", "")), reverse=True)
        keep = ranked[0]
        newest_open = next((j for j in sorted(entries, key=lambda j: j.get("lastmod", "") or j.get("date", ""),
                                              reverse=True) if is_open(j)), None)
        merges.append({"uuid": uuid, "keep": keep, "drop": ranked[1:], "source": newest_open or keep,
                       "open": any(is_open(j) for j in entries)})
    return merges


def rewrite_links(old_to_new: dict[str, str], skip: set[Path]) -> list[str]:
    if not old_to_new:
        return []
    pattern = re.compile(r"((?:https?://outreachrecruitment\.net)?/jobs/)(" + "|".join(
        re.escape(s) for s in sorted(old_to_new, key=len, reverse=True)) + r")(?=[/\"'#?])")
    touched = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts) or path in skip:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new = pattern.sub(lambda m: m.group(1) + old_to_new[m.group(2)], text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            touched.append(str(path.relative_to(ROOT)))
    return touched


def run(dry: bool = False) -> dict:
    import job_page_state
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    merges = plan(registry)
    out = {"merged": [], "touched": []}
    if not merges:
        return out
    try:
        redirects = json.loads(REDIRECTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        redirects = {}
    old_to_new: dict[str, str] = {}
    stub_files: set[Path] = set()
    for m in merges:
        keep, src = m["keep"], m["source"]
        out["merged"].append({"keep": keep["slug"], "dropped": [d["slug"] for d in m["drop"]],
                              "open": m["open"], "title": src["title"]})
        if dry:
            continue
        for field in ("title", "location", "location_slug", "salary", "employment_type", "work_mode", "date",
                      "apply_url", "keywords"):
            if src.get(field):
                keep[field] = src[field]
        if (keep.get("category") or "General") == "General":
            keep["category"] = next((d.get("category") for d in m["drop"]
                                     if d.get("category") not in (None, "", "General")), keep.get("category"))
        if m["open"]:
            keep.pop("status", None)
            keep["valid_through"] = OPEN_VALID_THROUGH
        for d in m["drop"]:
            registry.remove(d)
            if d["slug"] == keep["slug"]:
                continue
            old_to_new[d["slug"]] = keep["slug"]
            redirects[d["slug"]] = keep["slug"]
            for f in (ROOT / "jobs" / f"{d['slug']}.html", ROOT / "jobs" / d["slug"] / "index.html"):
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(stub_html(keep["title"], keep["slug"]), encoding="utf-8")
                stub_files.add(f)
                out["touched"].append(str(f.relative_to(ROOT)))
    if dry:
        return out
    # Older redirects that pointed at a now-dropped address follow it to the kept one.
    for old, new in list(redirects.items()):
        while new in old_to_new:
            new = old_to_new[new]
        redirects[old] = new
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REDIRECTS_PATH.write_text(json.dumps(dict(sorted(redirects.items())), indent=2) + "\n", encoding="utf-8")
    out["touched"] += rewrite_links(old_to_new, stub_files)
    for m in merges:  # page shows open/closed to match the merged entry
        out["touched"] += job_page_state.set_state(m["keep"]["slug"], not m["open"])
        if m["open"]:
            for f in job_page_state.pages(m["keep"]["slug"]):
                text = f.read_text(encoding="utf-8")
                new = re.sub(r'("validThrough"\s*:\s*)"[^"]*"', rf'\1"{OPEN_VALID_THROUGH}"', text)
                if new != text:
                    f.write_text(new, encoding="utf-8")
                    out["touched"].append(str(f.relative_to(ROOT)))
    out["touched"] = sorted(set(out["touched"]))
    return out


if __name__ == "__main__":
    res = run(dry="--dry-run" in sys.argv)
    for m in res["merged"]:
        print(f"  keep /jobs/{m['keep']} ({'open' if m['open'] else 'closed'}) ← redirect from "
              + ", ".join(f"/jobs/{d}" for d in m["dropped"]))
    print(f"{len(res['merged'])} duplicate group(s){' (dry run)' if '--dry-run' in sys.argv else ''}; "
          f"{len(res['touched'])} file(s) changed")
