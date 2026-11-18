#!/usr/bin/env python3
"""build_open_jobs_json.py — small list of open jobs for the Help Center pop-up (assets/open-jobs.json).
The pop-up suggests matching jobs while someone types their job title. Refreshed daily by run_sync_agent.sh."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
reg = json.loads((ROOT / "tools" / "jobs_registry.json").read_text(encoding="utf-8"))
jobs = [{"t": j["title"], "s": j["slug"], "l": (j.get("location") or "Malta").replace(", Malta", ""), "p": j.get("salary") or "",
         "c": j.get("category") or "", "k": j.get("keywords") or ""}
        for j in reg if j.get("status") not in ("closed", "expired") and (ROOT / "jobs" / j["slug"]).is_dir()]
out = ROOT / "assets" / "open-jobs.json"
out.write_text(json.dumps(jobs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"open-jobs.json: {len(jobs)} jobs, {out.stat().st_size // 1024} KB")
