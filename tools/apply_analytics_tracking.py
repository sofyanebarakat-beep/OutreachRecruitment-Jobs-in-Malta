#!/usr/bin/env python3
"""Install the real GA4 tag and delegated conversion tracking on public HTML pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENT_ID = "G-FK09PDN6TK"
GA_TAG = (
    '<!-- Google tag (gtag.js) --><script async src="https://www.googletagmanager.com/gtag/js?id='
    + MEASUREMENT_ID + '"></script><script>window.dataLayer=window.dataLayer||[];'
    "function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','"
    + MEASUREMENT_ID + "');</script>"
)
EVENT_TAG = '<script defer src="/assets/analytics-events.js"></script>'
SKIP_PARTS = {".git", "admin", "reports", "components", "images"}


def public_pages():
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        # Tiny files are legacy redirects; analytics would only double-count the destination.
        if path.stat().st_size < 5000:
            continue
        yield path


def main() -> int:
    ga_added = events_added = 0
    for path in public_pages():
        text = path.read_text(encoding="utf-8", errors="replace")
        changed = False
        if MEASUREMENT_ID not in text and "</head>" in text.lower():
            pos = text.lower().rfind("</head>")
            text = text[:pos] + GA_TAG + text[pos:]
            ga_added += 1
            changed = True
        if "analytics-events.js" not in text and "</body>" in text.lower():
            pos = text.lower().rfind("</body>")
            text = text[:pos] + EVENT_TAG + text[pos:]
            events_added += 1
            changed = True
        if changed:
            path.write_text(text, encoding="utf-8")
    print(f"GA4 added to {ga_added} content pages; conversion events added to {events_added} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
