#!/usr/bin/env python3
"""
fix_canonical.py — Audit and repair <link rel="canonical"> tags on job detail pages.

Rules enforced:
  1. Exactly one canonical tag per page.
  2. href must be an absolute URL: https://outreachrecruitment.net/jobs/{slug}
  3. No trailing slash (matches the site convention).
  4. Canonical must match the page's own slug (no cross-page pointing).

Usage:
  python3 tools/fix_canonical.py           # dry-run (report only)
  python3 tools/fix_canonical.py --fix     # apply fixes in place
"""

import os
import re
import sys
import argparse
from pathlib import Path

BASE_URL = "https://outreachrecruitment.net"
JOBS_DIR = Path(__file__).parent.parent / "jobs"

CANONICAL_RE = re.compile(r'<link([^>]*rel=["\']canonical["\'][^>]*|[^>]*href=[^>]*rel=["\']canonical["\'][^>]*)/?>', re.IGNORECASE)
HREF_RE = re.compile(r'href=["\']([^"\']*)["\']', re.IGNORECASE)


def expected_canonical(slug: str) -> str:
    return f"{BASE_URL}/jobs/{slug}"


def audit_file(path: Path, fix: bool) -> dict:
    slug = path.parent.name
    expected = expected_canonical(slug)
    content = path.read_text(encoding="utf-8")

    matches = list(CANONICAL_RE.finditer(content))
    result = {"slug": slug, "path": str(path), "issues": [], "fixed": False}

    if len(matches) == 0:
        result["issues"].append("MISSING canonical tag")
        if fix:
            insert_after = "</title>"
            canonical_tag = f'<link href="{expected}" rel="canonical"/>'
            if insert_after in content:
                new_content = content.replace(insert_after, f"{insert_after}\n{canonical_tag}", 1)
                path.write_text(new_content, encoding="utf-8")
                result["fixed"] = True
        return result

    if len(matches) > 1:
        result["issues"].append(f"DUPLICATE: {len(matches)} canonical tags found")
        if fix:
            canonical_tag = f'<link href="{expected}" rel="canonical"/>'
            new_content = CANONICAL_RE.sub("", content)
            first_title_end = new_content.find("</title>")
            if first_title_end >= 0:
                new_content = new_content[:first_title_end + len("</title>")] + "\n" + canonical_tag + new_content[first_title_end + len("</title>"):]
            path.write_text(new_content, encoding="utf-8")
            result["fixed"] = True
        return result

    match = matches[0]
    href_match = HREF_RE.search(match.group(0))
    current_href = href_match.group(1) if href_match else ""
    current_href_norm = current_href.rstrip("/")

    if current_href_norm != expected:
        result["issues"].append(f"WRONG href: '{current_href}' → should be '{expected}'")
        if fix:
            old_tag = match.group(0)
            new_tag = f'<link href="{expected}" rel="canonical"/>'
            path.write_text(content.replace(old_tag, new_tag, 1), encoding="utf-8")
            result["fixed"] = True

    return result


def main():
    parser = argparse.ArgumentParser(description="Audit and fix canonical tags on job detail pages.")
    parser.add_argument("--fix", action="store_true", help="Apply fixes in place (default is dry-run)")
    args = parser.parse_args()

    job_pages = sorted(
        [p for p in JOBS_DIR.rglob("index.html") if p.parent != JOBS_DIR],
        key=lambda p: p.parent.name,
    )

    total = len(job_pages)
    issues_found = 0
    fixed_count = 0

    for page in job_pages:
        result = audit_file(page, fix=args.fix)
        if result["issues"]:
            issues_found += 1
            status = "FIXED" if result["fixed"] else "NEEDS FIX"
            print(f"[{status}] {result['slug']}")
            for issue in result["issues"]:
                print(f"         {issue}")
            if result["fixed"]:
                fixed_count += 1

    print()
    print(f"Scanned : {total} job pages")
    print(f"Issues  : {issues_found}")
    if args.fix:
        print(f"Fixed   : {fixed_count}")
    else:
        print("Run with --fix to apply repairs.")


if __name__ == "__main__":
    main()
