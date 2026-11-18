#!/usr/bin/env python3
"""
add_help_widget_sitewide.py — put the Help Center chat bubble (assets/help-widget.js) on every website page.

Idempotent: adds <script defer src="/assets/help-widget.js?v=N"> before </body> on every public page
(pages with the site footer), or updates the version. Skips the admin, redirect stubs and tooling folders.
Runs daily from run_sync_agent.sh so newly generated pages get the bubble too.

Usage: python3 tools/add_help_widget_sitewide.py [--commit]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3"
TAG = f'<script defer src="/assets/help-widget.js?v={VERSION}"></script>'
SKIP = {"admin", "node_modules", "reports", "tools", "tmp", "tests", "docs", "supabase", "src", "scripts", "components",
        "Jobs Skills", "SEO Emp and Candidates", "STUDY IN MALTA SKILLS", ".git", ".github"}


def pages():
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in SKIP or any(part.startswith(".") for part in rel.parts):
            continue
        yield p


def main(argv: list[str]) -> int:
    changed = []
    for p in pages():
        s = p.read_text(encoding="utf-8", errors="ignore")
        if 'class="footer"' not in s or "</body>" not in s or 'http-equiv="refresh"' in s:
            continue
        new = re.sub(r'<script defer src="/assets/help-widget\.js(\?v=[^"]*)?"></script>', TAG, s)
        if TAG not in new:
            i = new.rfind("</body>")
            new = new[:i] + TAG + "\n" + new[i:]
        if new.count("/assets/help-widget.js") > 1:  # keep only the first tag
            first = new.find(TAG) + len(TAG)
            new = new[:first] + re.sub(r'\n?<script defer src="/assets/help-widget\.js[^"]*"></script>', "", new[first:])
        if new != s:
            p.write_text(new, encoding="utf-8")
            changed.append(str(p.relative_to(ROOT)))
    print(f"help widget: {len(changed)} page(s) updated")
    if changed and "--commit" in argv:
        git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        for i in range(0, len(changed), 200):
            git("add", "--", *changed[i:i + 200])
        if git("diff", "--cached", "--quiet").returncode:
            git("commit", "-m", "Help Center chat bubble on new pages")
            git("pull", "--no-rebase", "--no-edit", "origin", "main")
            r = git("push", "origin", "main")
            print("pushed" if r.returncode == 0 else f"push failed: {r.stderr.strip()[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
