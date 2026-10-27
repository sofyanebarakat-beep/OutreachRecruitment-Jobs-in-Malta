#!/usr/bin/env python3
"""
footer_blue_banner.py — replace the footer promo background video with a blue brand banner
and set the footer tagline, on every page that has the shared footer.

Idempotent: pages that already have the banner are left alone (the tagline and white logo are still enforced).

Usage:
  python3 tools/footer_blue_banner.py            # dry run
  python3 tools/footer_blue_banner.py --write
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", "reports"}

TAGLINE = "We support your career move"
BANNER = (
    '<div class="promo-media or-footer-banner" aria-hidden="true" style="background:'
    "radial-gradient(120% 90% at 88% 8%,rgba(255,255,255,.22) 0%,rgba(255,255,255,0) 55%),"
    "radial-gradient(80% 70% at 6% 100%,rgba(17,8,92,.55) 0%,rgba(17,8,92,0) 60%),"
    'linear-gradient(135deg,#5b47ff 0%,#442DFA 48%,#2a19b5 100%);"></div>'
)

PROMO = re.compile(r'(<div class="footer-promo"[^>]*>)(.*?)(<div class="footer-main")', re.S)
MEDIA = re.compile(r'<div class="promo-media">.*?(?=<div class="promo-content">)', re.S)
# the logo is red/blue; make it white so it reads on the blue banner
LOGO_OLD = 'src="/assets/outreach-recruitment-logo.svg" style="display:block;width:100%;height:100%;object-fit:contain;"/>'
LOGO_NEW = 'src="/assets/outreach-recruitment-logo.svg" style="display:block;width:100%;height:100%;object-fit:contain;filter:brightness(0) invert(1);"/>'
HEADING = re.compile(r'(<div class="promo-bottom">\s*<div class="heading-h5">|<div class="w-layout-hflex promo-bottom"><div class="heading-h5">)(.*?)(</div>)', re.S)


def fix(s: str) -> tuple[str, list[str]]:
    m = PROMO.search(s)
    if not m:
        return s, []
    block, done = m.group(2), []
    if "or-footer-banner" not in block:
        block, n = MEDIA.subn(BANNER, block, count=1)
        if n:
            done.append("banner")
    if LOGO_OLD in block:
        block = block.replace(LOGO_OLD, LOGO_NEW, 1)
        done.append("logo")
    block, n = HEADING.subn(lambda h: h.group(1) + TAGLINE + h.group(3) if h.group(2) != TAGLINE else h.group(0), block, count=1)
    if n and TAGLINE not in m.group(2):
        done.append("tagline")
    return s[: m.start(2)] + block + s[m.end(2):], done


def main() -> None:
    write = "--write" in sys.argv
    changed = skipped = 0
    for p in sorted(ROOT.rglob("*.html")):
        if SKIP & set(p.relative_to(ROOT).parts):
            continue
        s = p.read_text(encoding="utf-8", errors="ignore")
        if 'class="footer-promo"' not in s:
            continue
        new, done = fix(s)
        if new == s:
            skipped += 1
            if "or-footer-banner" not in s:
                print(f"  no change (unexpected markup): {p.relative_to(ROOT)}")
            continue
        changed += 1
        if write:
            p.write_text(new, encoding="utf-8")
    print(f"{'updated' if write else 'would update'} {changed} page(s); {skipped} unchanged")


if __name__ == "__main__":
    main()
