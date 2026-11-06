#!/usr/bin/env python3
"""Install the shared eligibility and post-application alert UI on every job page."""

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "jobs"
ASSET_VERSION = "20261106"
ASSET_NAMES = (
    "job-eligibility-gate.css",
    "job-alert-launcher.css",
    "job-alert-focus.css",
    "job-alert-subscribe.js",
    "job-alert-after-apply.js",
    "job-eligibility-gate.js",
)

ASSETS = f"""<link href="/assets/job-eligibility-gate.css?v={ASSET_VERSION}" rel="stylesheet" type="text/css"/>
<link href="/assets/job-alert-launcher.css?v={ASSET_VERSION}" rel="stylesheet" type="text/css"/>
<link href="/assets/job-alert-focus.css?v={ASSET_VERSION}" rel="stylesheet" type="text/css"/>
<script defer src="/assets/job-alert-subscribe.js?v={ASSET_VERSION}"></script>
<script defer src="/assets/job-alert-after-apply.js?v={ASSET_VERSION}"></script>
<script defer src="/assets/job-eligibility-gate.js?v={ASSET_VERSION}"></script>
"""


def install(path: Path) -> bool:
    page = path.read_text(encoding="utf-8")
    original_page = page
    if 'id="job-apply-panel"' not in page:
        return False

    # Replace any prior versions, then reinstall one canonical block.
    for asset in ASSET_NAMES:
        page = re.sub(
            rf'(?m)^[ \t]*<(?:link|script)\b(?=[^\n]*(?:href|src)=["\']/assets/{re.escape(asset)}(?:\?[^"\']*)?["\'])[^>]*>(?:</script>)?[ \t]*\n?',
            "",
            page,
        )

    if "</head>" not in page:
        raise ValueError(f"Missing </head> in {path}")
    page = re.sub(
        r'(?m)^(?:>[ \t]*\n){6}(?=</head>)',
        "",
        page,
    )
    page = page.replace("</head>", ASSETS + "</head>", 1)
    if page == original_page:
        return False
    path.write_text(page, encoding="utf-8")
    return True


def main() -> None:
    registry = json.loads((ROOT / "tools" / "jobs_registry.json").read_text(encoding="utf-8"))
    paths = set()
    for job in registry:
        if job.get("status") in ("closed", "expired"):
            continue
        slug = job["slug"]
        paths.update((JOBS / slug / "index.html", JOBS / f"{slug}.html"))
    changed = sum(install(path) for path in sorted(paths) if path.exists())
    print(f"Installed the application system on {changed} job page files.")


if __name__ == "__main__":
    main()
