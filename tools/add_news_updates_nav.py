#!/usr/bin/env python3
"""Add "News & Updates" (/news-updates) under Company in the header dropdown and the footer, sitewide.

Idempotent: the header and footer both use the same Company link list, so one replacement covers both.
Usage: python3 tools/add_news_updates_nav.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"node_modules", ".git", "reports", "admin", "seo-app", "src", "docs", "components",
        "Jobs Skills", "SEO Emp and Candidates", "STUDY IN MALTA SKILLS"}
OLD = '<a class="nav-item" href="/service">About Us</a><a class="nav-item" href="/our-team">Our Team</a>'
LINK = '<a class="nav-item" href="/news-updates">News &amp; Updates</a>'
NEW = OLD + LINK


def main() -> None:
    changed = 0
    for p in ROOT.rglob("*.html"):
        if SKIP & set(p.relative_to(ROOT).parts):
            continue
        t = p.read_text(encoding="utf-8", errors="surrogateescape")
        if OLD not in t:
            continue
        u = t.replace(NEW, OLD).replace(OLD, NEW)  # normalise, so re-runs never duplicate the link
        if u != t:
            p.write_text(u, encoding="utf-8", errors="surrogateescape")
            changed += 1
    print(f"News & Updates link added/kept on {changed} changed pages")


if __name__ == "__main__":
    main()
