"""
Notify Google Indexing API about job URLs.

Setup:
1. Create a Google Cloud service account and enable the Indexing API.
2. Add the service-account email as an owner or delegated owner in Search Console.
3. Install google-auth if needed:
   python3 -m pip install google-auth
4. Run with credentials:
   GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json python3 tools/google_indexing_api.py update
   Or place a service account JSON in tools/private/ and run the script directly.

Commands:
  update   Submit active job URLs as URL_UPDATED.
  delete   Submit expired job URLs as URL_DELETED.

Optional:
  --slug plumber --slug welder   Limit to selected job slugs.
  --dry-run                      Print payloads without sending.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tools" / "jobs_registry.json"
PRIVATE_CREDENTIALS_DIR = ROOT / "tools" / "private"
BASE_URL = "https://outreachrecruitment.net"
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPE = "https://www.googleapis.com/auth/indexing"


def default_credentials_path() -> Path | None:
    if not PRIVATE_CREDENTIALS_DIR.exists():
        return None

    candidates = sorted(PRIVATE_CREDENTIALS_DIR.glob("*.json"))
    if not candidates:
        return None
    if len(candidates) > 1:
        names = ", ".join(path.name for path in candidates)
        raise SystemExit(
            "Multiple credential JSON files found in tools/private. "
            f"Set GOOGLE_APPLICATION_CREDENTIALS to choose one: {names}"
        )
    return candidates[0]


def load_access_token() -> str:
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: google-auth. Install it with "
            "`python3 -m pip install google-auth`."
        ) from exc

    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        default_path = default_credentials_path()
        if default_path is None:
            raise SystemExit(
                "Set GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json "
                "or place one service account JSON file in tools/private/."
            )
        credentials_path = str(default_path)

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=[SCOPE],
    )
    credentials.refresh(Request())
    return credentials.token


def active(job: dict, today: str) -> bool:
    return (
        job.get("status", "active").lower() != "expired"
        and job.get("valid_through", "9999-12-31") >= today
    )


def selected_jobs(slugs: set[str], mode: str) -> list[dict]:
    today = date.today().isoformat()
    jobs = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if slugs:
        jobs = [job for job in jobs if job["slug"] in slugs]
    if mode == "update":
        return [job for job in jobs if active(job, today)]
    return [job for job in jobs if not active(job, today)]


def publish(token: str, url: str, notification_type: str) -> tuple[int, str]:
    body = json.dumps({"url": url, "type": notification_type}).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["update", "delete"])
    parser.add_argument("--slug", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    jobs = selected_jobs(set(args.slug), args.mode)
    notification_type = "URL_UPDATED" if args.mode == "update" else "URL_DELETED"

    print(f"Selected jobs: {len(jobs)}")
    print(f"Notification type: {notification_type}")

    if args.dry_run:
        for job in jobs:
            print(json.dumps({"url": f"{BASE_URL}/jobs/{job['slug']}", "type": notification_type}))
        return

    token = load_access_token()
    failures = 0
    for job in jobs:
        url = f"{BASE_URL}/jobs/{job['slug']}"
        status, response = publish(token, url, notification_type)
        ok = 200 <= status < 300
        failures += 0 if ok else 1
        print(f"{status} {url}")
        if not ok:
            print(response[:1000], file=sys.stderr)
        time.sleep(args.sleep)

    print(f"Done. Success: {len(jobs) - failures}, failures: {failures}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
