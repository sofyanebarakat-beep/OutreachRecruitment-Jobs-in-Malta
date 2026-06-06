from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
SOURCE_LOGO = Path("/Users/sof/Downloads/Untitled design.svg")
ASSET_DIR = ROOT / "assets"
LOGO_FILE = ASSET_DIR / "outreach-recruitment-logo.svg"
LOGO_SRC = "/assets/outreach-recruitment-logo.svg"

LOGO_IMG = (
    f'<img alt="Outreach Recruitment logo" src="{LOGO_SRC}" '
    'style="display:block;width:100%;height:100%;object-fit:contain;"/>'
)

PATTERNS = [
    re.compile(r'(<div class="nav-logo w-embed">)<svg\b.*?</svg>(</div>)', re.S),
    re.compile(r'(<div class="footer-logo w-embed">)<svg\b.*?</svg>(</div>)', re.S),
    re.compile(r'(<div class="logo w-embed"[^>]*>)<svg\b.*?</svg>(</div>)', re.S),
]


def replace_logos(html: str) -> tuple[str, int]:
    total = 0
    for pattern in PATTERNS:
        html, count = pattern.subn(rf"\1{LOGO_IMG}\2", html)
        total += count
    return html, total


def main() -> None:
    if not SOURCE_LOGO.exists():
        raise FileNotFoundError(f"Logo not found: {SOURCE_LOGO}")

    ASSET_DIR.mkdir(exist_ok=True)
    shutil.copyfile(SOURCE_LOGO, LOGO_FILE)

    changed_files = []
    replacements = 0

    for path in ROOT.rglob("*.html"):
        html = path.read_text()
        updated, count = replace_logos(html)
        if count:
            path.write_text(updated)
            changed_files.append(path.relative_to(ROOT))
            replacements += count

    print(f"Copied logo to {LOGO_FILE.relative_to(ROOT)}")
    print(f"Updated {replacements} logo blocks in {len(changed_files)} files")
    for path in changed_files:
        print(path)


if __name__ == "__main__":
    main()
