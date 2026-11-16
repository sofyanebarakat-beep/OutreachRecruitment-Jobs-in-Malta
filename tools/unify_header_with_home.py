#!/usr/bin/env python3
"""Make the header + submenus on every page look/behave like the homepage header.

The header *markup* is already shared (tools/apply_home_header_footer.py), but some
pages miss the homepage's header stylesheets/scripts (so submenus and the "View Jobs"
button render wrong) and others restyle the bar (white strip, no top gap, white pill).

For every page that has the shared header this script:
  1. adds any missing homepage header/footer assets (menu CSS/JS, footer job-alert CSS/JS);
  2. puts /assets/header-unify.css as the last thing in <head> so it wins over page overrides.

Idempotent. Usage: python3 tools/unify_header_with_home.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"node_modules", ".git", "reports", "admin", "seo-app", "src", "docs", "components",
        "Jobs Skills", "SEO Emp and Candidates", "STUDY IN MALTA SKILLS", "tmp", "tests", "supabase"}
MARKER = 'class="navigation w-nav"'

# (substring that proves the asset is present, tag to insert) — same tags the homepage uses
HEAD_ASSETS = [
    ("footer-job-alerts.css", '<link href="/assets/footer-job-alerts.css?v=20261107c" rel="stylesheet" type="text/css"/>'),
    ("mobile-header-v2.css", '<link href="/assets/mobile-header-v2.css" rel="stylesheet" type="text/css"/>'),
    ("resources-menu-v2.css", '<link href="/assets/resources-menu-v2.css" rel="stylesheet" type="text/css"/>'),
    ("services-menu-v1.css", '<link href="/assets/services-menu-v1.css?v=20261111-company" rel="stylesheet" type="text/css"/>'),
    ("job-alert-subscribe.js", '<script defer src="/assets/job-alert-subscribe.js?v=20261107c"></script>'),
    ("footer-job-alerts.js", '<script defer src="/assets/footer-job-alerts.js?v=20261107c"></script>'),
    ("resources-menu-v1.js", '<script defer src="/assets/resources-menu-v1.js"></script>'),
]
UNIFY = '<link href="/assets/header-unify.css?v=1" rel="stylesheet" type="text/css"/>'


def main() -> None:
    changed = 0
    for p in sorted(ROOT.rglob("*.html")):
        if SKIP & set(p.relative_to(ROOT).parts):
            continue
        t = p.read_text(encoding="utf-8", errors="surrogateescape")
        if MARKER not in t or "</head>" not in t:
            continue
        u = t.replace(UNIFY, "")
        add = "".join(tag for key, tag in HEAD_ASSETS if key not in u)
        u = u.replace("</head>", add + UNIFY + "</head>", 1)
        if u != t:
            p.write_text(u, encoding="utf-8", errors="surrogateescape")
            changed += 1
    print(f"Header unified on {changed} changed pages")


if __name__ == "__main__":
    main()
