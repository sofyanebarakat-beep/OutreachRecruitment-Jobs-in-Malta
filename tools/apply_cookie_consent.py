from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TAG = '<script defer src="/assets/cookie-consent.js" type="text/javascript"></script>'
EXCLUDE_DIRS = {"components", "reports", "node_modules"}


def main() -> None:
    changed = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in EXCLUDE_DIRS:
            continue

        html = path.read_text()
        if SCRIPT_TAG in html:
            continue

        marker = "</body>"
        marker_index = html.rfind(marker)
        if marker_index == -1:
            continue

        html = html[:marker_index] + SCRIPT_TAG + html[marker_index:]
        path.write_text(html)
        changed.append(rel)

    print(f"Added cookie consent banner to {len(changed)} files")
    for path in changed[:20]:
        print(path)
    if len(changed) > 20:
        print(f"... and {len(changed) - 20} more")


if __name__ == "__main__":
    main()
