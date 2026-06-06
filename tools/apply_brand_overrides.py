from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OVERRIDE_LINK = '<link href="/assets/brand-overrides.css" rel="stylesheet" type="text/css"/>'


def main() -> None:
    changed = []
    for path in ROOT.rglob("*.html"):
        html = path.read_text()
        if OVERRIDE_LINK in html:
            continue

        marker = 'rel="stylesheet" type="text/css"/>'
        marker_index = html.find(marker)
        if marker_index == -1:
            continue

        insert_at = marker_index + len(marker)
        html = html[:insert_at] + OVERRIDE_LINK + html[insert_at:]
        path.write_text(html)
        changed.append(path.relative_to(ROOT))

    print(f"Added brand override stylesheet to {len(changed)} files")
    for path in changed:
        print(path)


if __name__ == "__main__":
    main()
