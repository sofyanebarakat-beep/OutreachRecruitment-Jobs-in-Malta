#!/usr/bin/env python3
"""menu_help_center.py — site menus: Help Center under Company (header) and at the top of footer Resources;
remove Career Advice and Register CV from the footer Resources column. Idempotent; run after adding pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"admin", "node_modules", ".git", "tmp", "tests", "reports"}
HC = '<a class="nav-item" href="/help-center/">Help Center</a>'
HEADER_OLD = '<a class="nav-item" href="/news-updates">News &amp; Updates</a></div></div></nav></div>'
HEADER_NEW = '<a class="nav-item" href="/news-updates">News &amp; Updates</a>' + HC + '</div></div></nav></div>'
FOOTER_OLD = ('<div class="caption muted">Resources</div><div class="nav-list"><a class="nav-item" href="/salary-calculator-malta">Malta Salary Calculator</a>'
              '<a class="nav-item" href="/blog">Career Advice</a><a class="nav-item" href="/book-a-call">Register CV</a>')
FOOTER_NEW = ('<div class="caption muted">Resources</div><div class="nav-list">' + HC +
              '<a class="nav-item" href="/salary-calculator-malta">Malta Salary Calculator</a>')

changed = 0
for p in ROOT.rglob("*.html"):
    if p.relative_to(ROOT).parts[0] in SKIP:
        continue
    s = p.read_text(encoding="utf-8", errors="ignore")
    n = s.replace(HEADER_OLD, HEADER_NEW).replace(FOOTER_OLD, FOOTER_NEW)
    if n != s:
        p.write_text(n, encoding="utf-8")
        changed += 1
print(f"menus: {changed} page(s) updated")
