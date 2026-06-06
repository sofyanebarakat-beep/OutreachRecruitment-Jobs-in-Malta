from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "index.html"
COMPONENTS = ROOT / "components"
HEADER = COMPONENTS / "header.html"
FOOTER = COMPONENTS / "footer.html"

HEADER_RE = re.compile(r'<div class="navigation w-nav".*?(?=<main\b)', re.S)
FOOTER_RE = re.compile(r'<footer class="footer">.*?</footer>', re.S)
SKIP_DIRS = {".git", ".codex-recovery", "components"}


def html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel_parts = set(path.relative_to(ROOT).parts)
        if rel_parts & SKIP_DIRS:
            continue
        files.append(path)
    return sorted(files)


def extract_from_home() -> None:
    source_html = SOURCE.read_text(encoding="utf-8")
    header_match = HEADER_RE.search(source_html)
    footer_match = FOOTER_RE.search(source_html)
    if not header_match or not footer_match:
        raise SystemExit("Could not find home header/footer in index.html")

    COMPONENTS.mkdir(exist_ok=True)
    HEADER.write_text(header_match.group(0).strip() + "\n", encoding="utf-8")
    FOOTER.write_text(footer_match.group(0).strip() + "\n", encoding="utf-8")
    print("Extracted home header/footer into components/")


def main() -> None:
    if not HEADER.exists() or not FOOTER.exists():
        extract_from_home()

    header = HEADER.read_text(encoding="utf-8").strip()
    footer = FOOTER.read_text(encoding="utf-8").strip()
    changed: list[Path] = []

    for path in html_files():
        html = path.read_text(encoding="utf-8", errors="replace")
        updated = HEADER_RE.sub(header, html, count=1)
        updated = FOOTER_RE.sub(footer, updated, count=1)
        if updated != html:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(ROOT))

    print(f"Applied home header/footer to {len(changed)} files")
    for path in changed:
        print(path)


if __name__ == "__main__":
    import sys

    if "--extract" in sys.argv:
        extract_from_home()
    main()
