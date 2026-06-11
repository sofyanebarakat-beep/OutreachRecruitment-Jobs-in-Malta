"""
Expire one or more jobs cleanly.

Usage:
  python3 tools/expire_job.py plumber welder

What it does:
- Marks each job as expired in tools/jobs_registry.json.
- Sets valid_through to yesterday, so existing JobPosting schema is expired.
- Rebuilds JobPosting schema on the affected pages.
- Regenerates homepage/jobs page/sitemaps, which hides expired jobs from lists.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tools" / "jobs_registry.json"


def main() -> None:
    slugs = set(sys.argv[1:])
    if not slugs:
        raise SystemExit("Usage: python3 tools/expire_job.py job-slug [job-slug ...]")

    jobs = json.loads(REGISTRY.read_text(encoding="utf-8"))
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    found = set()

    for job in jobs:
        if job["slug"] in slugs:
            job["status"] = "expired"
            job["valid_through"] = yesterday
            job["lastmod"] = date.today().isoformat()
            found.add(job["slug"])

    missing = sorted(slugs - found)
    if missing:
        raise SystemExit("Unknown job slug(s): " + ", ".join(missing))

    REGISTRY.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    subprocess.run(["python3", str(ROOT / "tools" / "fix_jobposting_schema.py")], check=True)
    subprocess.run(["python3", str(ROOT / "tools" / "update_jobs_listing.py")], check=True)

    print("Expired job(s): " + ", ".join(sorted(found)))


if __name__ == "__main__":
    main()
