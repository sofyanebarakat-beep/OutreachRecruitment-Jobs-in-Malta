#!/usr/bin/env python3
"""Install the shared eligibility and post-application alert UI on every job page."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "jobs"

ASSETS = """<link href="/assets/job-eligibility-gate.css" rel="stylesheet" type="text/css"/>
<link href="/assets/job-alert-launcher.css" rel="stylesheet" type="text/css"/>
<link href="/assets/job-alert-focus.css" rel="stylesheet" type="text/css"/>
<script defer src="/assets/job-alert-subscribe.js"></script>
<script defer src="/assets/job-alert-after-apply.js"></script>
<script defer src="/assets/job-eligibility-gate.js"></script>
"""


def install(path: Path) -> bool:
    page = path.read_text(encoding="utf-8")
    if 'id="job-apply-panel"' not in page:
        return False

    # Remove old one-off includes before installing one canonical block.
    for line in ASSETS.splitlines():
        page = page.replace(line + "\n", "").replace(line, "")
    page = page.replace('<script src="/assets/job-eligibility-gate.js"></script>', "")

    if "</head>" not in page:
        raise ValueError(f"Missing </head> in {path}")
    page = page.replace("</head>", ASSETS + "</head>", 1)
    path.write_text(page, encoding="utf-8")
    return True


def main() -> None:
    paths = sorted(set(JOBS.glob("*/index.html")) | set(JOBS.glob("*.html")))
    changed = sum(install(path) for path in paths)
    print(f"Installed the application system on {changed} job page files.")


if __name__ == "__main__":
    main()
