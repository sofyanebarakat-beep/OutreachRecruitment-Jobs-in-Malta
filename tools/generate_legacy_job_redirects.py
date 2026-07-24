#!/usr/bin/env python3
"""
generate_legacy_job_redirects.py — Create static redirect stubs for legacy /job/{slug} URLs.

Why this exists:
  netlify.toml declares 301 redirects from /job/:slug to /jobs/:slug, but the
  live site is served by GitHub Pages, which does not process netlify.toml.
  Any legacy /job/{slug} URL that Google (or an old backlink/bookmark) still
  has hard-404s in production instead of consolidating into the current
  /jobs/{slug} page.

  Since GitHub Pages can't do path-pattern server redirects, this generates
  a real static file per slug at job/{slug}/index.html that redirects via
  canonical + 0-second meta refresh + JS replace (the same technique already
  used by 404.html and the /study-in-malta-from-* stub pages in this repo).

Source of truth: existing jobs/{slug}/index.html directories on disk (not
tools/jobs_registry.json, which can contain expired slugs with no live page).

Usage:
  python3 tools/generate_legacy_job_redirects.py           # dry-run (report only)
  python3 tools/generate_legacy_job_redirects.py --fix     # write stub files
"""

import argparse
import json
from pathlib import Path

BASE_URL = "https://outreachrecruitment.net"
ROOT = Path(__file__).resolve().parents[1]
JOBS_DIR = ROOT / "jobs"
LEGACY_DIR = ROOT / "job"
REGISTRY = ROOT / "tools" / "jobs_registry.json"

STUB_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{title} | Outreach Recruitment</title>
<meta http-equiv="refresh" content="0;url={target}"/>
<link href="{target}" rel="canonical"/>
<meta content="noarchive" name="robots"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<script>window.location.replace("{target}");</script>
</head>
<body>
<p>This job listing has moved. <a href="{target}">Continue to {title}</a>.</p>
</body>
</html>
"""


def load_titles() -> dict:
    if not REGISTRY.exists():
        return {}
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {d["slug"]: d.get("title", d["slug"]) for d in data}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate legacy /job/{slug} redirect stubs.")
    parser.add_argument("--fix", action="store_true", help="Write stub files (default is dry-run)")
    args = parser.parse_args()

    titles = load_titles()
    slugs = sorted(p.name for p in JOBS_DIR.iterdir() if p.is_dir() and (p / "index.html").exists())

    to_create = []
    for slug in slugs:
        stub_path = LEGACY_DIR / slug / "index.html"
        if not stub_path.exists():
            to_create.append((slug, stub_path))

    print(f"Live job pages found : {len(slugs)}")
    print(f"Legacy stubs missing : {len(to_create)}")

    if not args.fix:
        for slug, _ in to_create[:10]:
            print(f"  would create: job/{slug}/index.html")
        if len(to_create) > 10:
            print(f"  ... and {len(to_create) - 10} more")
        print("\nRun with --fix to write these files.")
        return

    for slug, stub_path in to_create:
        title = titles.get(slug, slug.replace("-", " ").title())
        target = f"{BASE_URL}/jobs/{slug}"
        stub_path.parent.mkdir(parents=True, exist_ok=True)
        stub_path.write_text(
            STUB_TEMPLATE.format(title=title, target=target),
            encoding="utf-8",
        )
    print(f"Created {len(to_create)} redirect stub(s) under job/.")


if __name__ == "__main__":
    main()
