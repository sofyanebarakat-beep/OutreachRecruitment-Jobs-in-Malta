#!/usr/bin/env python3
"""Replace legacy footer email forms with the shared job-alert signup."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = '<link href="/assets/footer-job-alerts.css?v=20261107c" rel="stylesheet" type="text/css"/>\n<script defer src="/assets/job-alert-subscribe.js?v=20261107c"></script>\n<script defer src="/assets/footer-job-alerts.js?v=20261107c"></script>\n'
FOOTER_RE = re.compile(r'<div class="footer-newsletter">.*?<div class="text-small">Be first to get new job alerts\.</div></div>', re.S)

def update(path: Path) -> bool:
    page = path.read_text(encoding="utf-8")
    original = page
    page, count = FOOTER_RE.subn('<div class="footer-newsletter" data-footer-job-alert></div>', page)
    if count > 1:
        raise ValueError(f"Multiple footer newsletters in {path}")
    if not count and 'data-footer-job-alert' not in page:
        return False
    for asset in ("footer-job-alerts.css", "job-alert-subscribe.js", "footer-job-alerts.js"):
        asset_path = rf'/assets/{re.escape(asset)}(?:\?[^"\']*)?'
        page = re.sub(rf'<link\b[^>]*href=["\']{asset_path}["\'][^>]*>\s*', '', page)
        page = re.sub(rf'<script\b[^>]*src=["\']{asset_path}["\'][^>]*>\s*</script>\s*', '', page)
    page = page.replace('</head>', ASSETS + '</head>', 1)
    if page != original:
        path.write_text(page, encoding="utf-8")
        return True
    return False

def main() -> None:
    changed = sum(update(path) for path in ROOT.rglob("*.html") if ".git" not in path.parts)
    print(f"Installed footer job alerts on {changed} HTML files.")

if __name__ == "__main__":
    main()
