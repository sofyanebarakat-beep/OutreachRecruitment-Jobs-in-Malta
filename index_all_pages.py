#!/usr/bin/env python3
"""
Google Indexing API — Submit all sitemap URLs for indexing.

SETUP (one-time):
  1. Go to https://console.cloud.google.com → New project → Enable "Web Search Indexing API"
  2. IAM & Admin → Service Accounts → Create → Download JSON key → save as service-account.json
     in the same folder as this script.
  3. Google Search Console → Settings → Users and permissions → Add user
     → paste the service account email (ends in @...gserviceaccount.com) → Owner
  4. pip install google-auth google-auth-httplib2 google-api-python-client

USAGE:
  python3 index_all_pages.py                  # submit all URLs from all sitemaps
  python3 index_all_pages.py --dry-run        # print URLs without submitting
  python3 index_all_pages.py --sitemap sitemaps/sitemap-jobs.xml   # one sitemap only
"""

import argparse
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

SITEMAP_INDEX = "sitemap_index.xml"
SERVICE_ACCOUNT_FILE = "service-account.json"
INDEXING_API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
QUOTA_DELAY = 0.5  # seconds between requests (API limit: 200/day, burst 600/min)


def load_urls_from_sitemap(sitemap_path: str) -> list[str]:
    """Parse a local sitemap XML file and return all <loc> URLs."""
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    try:
        tree = ET.parse(sitemap_path)
    except FileNotFoundError:
        print(f"  [WARN] Sitemap not found: {sitemap_path}")
        return []
    root = tree.getroot()

    # Sitemap index → recurse into child sitemaps
    if root.tag in ("{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex", "sitemapindex"):
        urls = []
        for sitemap in root.findall("sm:sitemap", ns):
            loc = sitemap.find("sm:loc", ns)
            if loc is not None and loc.text:
                child_path = url_to_local_path(loc.text.strip())
                urls.extend(load_urls_from_sitemap(child_path))
        return urls

    # Regular urlset
    urls = []
    for url in root.findall("sm:url", ns):
        loc = url.find("sm:loc", ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls


def url_to_local_path(url: str) -> str:
    """Convert a full sitemap URL to a local file path."""
    base = "https://outreachrecruitment.net/"
    if url.startswith(base):
        return url[len(base):]
    return url


def get_credentials(service_account_file: str):
    """Load Google service account credentials."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        print("ERROR: Missing dependencies. Run:")
        print("  pip install google-auth google-auth-httplib2 google-api-python-client")
        sys.exit(1)

    scopes = ["https://www.googleapis.com/auth/indexing"]
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes
    )
    return credentials


def submit_url(session, url: str, dry_run: bool = False) -> dict:
    """Submit a single URL to the Google Indexing API."""
    if dry_run:
        print(f"  [DRY RUN] {url}")
        return {"status": "dry_run"}

    payload = {"url": url, "type": "URL_UPDATED"}
    response = session.post(INDEXING_API_ENDPOINT, json=payload)
    return {"status": response.status_code, "body": response.json()}


def main():
    parser = argparse.ArgumentParser(description="Submit all sitemap URLs to Google Indexing API")
    parser.add_argument("--dry-run", action="store_true", help="Print URLs without submitting")
    parser.add_argument("--sitemap", type=str, default=SITEMAP_INDEX, help="Sitemap file to process")
    parser.add_argument("--service-account", type=str, default=SERVICE_ACCOUNT_FILE)
    args = parser.parse_args()

    # Load URLs
    print(f"Reading sitemap: {args.sitemap}")
    urls = load_urls_from_sitemap(args.sitemap)
    # Deduplicate preserving order
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    print(f"Found {len(unique_urls)} unique URLs\n")

    if args.dry_run:
        for url in unique_urls:
            print(f"  {url}")
        print(f"\n[DRY RUN] Would submit {len(unique_urls)} URLs")
        return

    # Check credentials file
    if not os.path.exists(args.service_account):
        print(f"ERROR: Service account file not found: {args.service_account}")
        print("See setup instructions at the top of this script.")
        sys.exit(1)

    credentials = get_credentials(args.service_account)

    import google.auth.transport.requests
    authed_session = google.auth.transport.requests.AuthorizedSession(credentials)

    # Submit all URLs
    results = {"ok": [], "error": [], "skipped": []}
    print(f"Submitting {len(unique_urls)} URLs...\n")

    for i, url in enumerate(unique_urls, 1):
        result = submit_url(authed_session, url)
        status = result.get("status")

        if status == 200:
            print(f"  ✓ [{i}/{len(unique_urls)}] {url}")
            results["ok"].append(url)
        elif status == 429:
            print(f"  ⚠ [{i}/{len(unique_urls)}] RATE LIMITED — waiting 60s...")
            time.sleep(60)
            # Retry once
            result = submit_url(authed_session, url)
            if result.get("status") == 200:
                results["ok"].append(url)
                print(f"  ✓ Retry succeeded: {url}")
            else:
                results["error"].append((url, result))
                print(f"  ✗ Retry failed: {url} — {result}")
        elif status == 403:
            print(f"  ✗ [{i}/{len(unique_urls)}] PERMISSION DENIED — {url}")
            print("    Check: service account added as Owner in Search Console?")
            results["error"].append((url, result))
        else:
            print(f"  ✗ [{i}/{len(unique_urls)}] HTTP {status} — {url}")
            body = result.get("body", {})
            if body:
                print(f"    {body}")
            results["error"].append((url, result))

        time.sleep(QUOTA_DELAY)

    # Summary
    print(f"\n{'='*50}")
    print(f"DONE — {len(unique_urls)} URLs processed")
    print(f"  ✓ Submitted:  {len(results['ok'])}")
    print(f"  ✗ Errors:     {len(results['error'])}")

    # Save report
    report_path = "reports/indexing-report.json"
    os.makedirs("reports", exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({
            "total": len(unique_urls),
            "ok": results["ok"],
            "errors": [(u, str(r)) for u, r in results["error"]],
        }, f, indent=2)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
