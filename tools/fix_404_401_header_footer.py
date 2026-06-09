"""Apply the correct header/footer from index.html to 404.html and 401.html."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "index.html"
COMPONENTS = ROOT / "components"
HEADER_FILE = COMPONENTS / "header.html"
FOOTER_FILE = COMPONENTS / "footer.html"

HEADER_RE = re.compile(r'<div class="navigation w-nav".*?(?=<main\b)', re.S)
FOOTER_RE = re.compile(r'<footer class="footer">.*?</footer>', re.S)
# Matches the nav block inside a page (ends just before the page content container)
INNER_NAV_RE = re.compile(
    r'<div class="navigation w-nav".*?<div class="navigation-overlay"></div></div>',
    re.S,
)


def get_components() -> tuple[str, str]:
    src = SOURCE.read_text(encoding="utf-8")
    h = HEADER_RE.search(src)
    f = FOOTER_RE.search(src)
    if not h or not f:
        raise SystemExit("Could not find header/footer in index.html")
    COMPONENTS.mkdir(exist_ok=True)
    nav = h.group(0).strip()
    footer = f.group(0).strip()
    HEADER_FILE.write_text(nav, encoding="utf-8")
    FOOTER_FILE.write_text(footer, encoding="utf-8")
    return nav, footer


def fix_page(path: Path, nav: str, footer: str, has_old_nav: bool) -> None:
    html = path.read_text(encoding="utf-8")

    # 1. Remove old nav from inside the section (if present)
    if has_old_nav:
        html = INNER_NAV_RE.sub("", html, count=1)

    # 2. Move <main> out of <body> open — insert nav between <body> and <main>
    html = re.sub(
        r'(<body>)(<main\b)',
        lambda m: m.group(1) + nav + "\n" + m.group(2),
        html,
        count=1,
    )

    # 3. Add footer after </main> (before the first <script>)
    html = html.replace("</main>", "</main>\n" + footer, 1)

    path.write_text(html, encoding="utf-8")
    print(f"  Fixed: {path.name}")


def main() -> None:
    nav, footer = get_components()
    print("Extracted header/footer from index.html")

    fix_page(ROOT / "404.html", nav, footer, has_old_nav=True)
    fix_page(ROOT / "401.html", nav, footer, has_old_nav=False)
    print("Done.")


if __name__ == "__main__":
    main()
