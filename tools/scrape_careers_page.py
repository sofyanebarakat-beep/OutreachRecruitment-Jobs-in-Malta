"""
scrape_careers_page.py
======================
Scrapes ALL open positions from outreach-recruitment-agency.careers-page.com,
builds a CSV, and imports them via add_jobs_from_csv.py.

Usage:
    python3 tools/scrape_careers_page.py            # scrape + import
    python3 tools/scrape_careers_page.py --csv-only # scrape → CSV, no import
    python3 tools/scrape_careers_page.py --dry-run  # list jobs found, no files written
"""
from __future__ import annotations
import csv
import json
import re
import sys
import time
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

CAREERS_BASE  = "https://outreach-recruitment-agency.careers-page.com"
ROOT          = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "tools" / "jobs_registry.json"
OUT_CSV       = ROOT / "tools" / "jobs_scraped.csv"

DELAY_SECS    = 1.8   # polite delay between requests


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helper
# ─────────────────────────────────────────────────────────────────────────────

def fetch(url: str, retries: int = 6) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for attempt in range(retries):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except URLError as e:
            is_429 = "429" in str(e)
            if attempt < retries - 1:
                wait = 15 * (attempt + 1) if is_429 else 2 ** attempt
                print(f"    [{type(e).__name__} {e}] waiting {wait}s …", end=" ", flush=True)
                time.sleep(wait)
            else:
                raise
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — collect all job UUIDs from listing pages
# ─────────────────────────────────────────────────────────────────────────────

UUID_RE  = re.compile(r'href="/jobs/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"', re.I)
PAGES_RE = re.compile(r'page=(\d+)')

def get_all_job_ids() -> list[str]:
    """Return list of all unique UUIDs from all listing pages."""
    ids: list[str] = []
    seen: set[str] = set()
    page = 1

    while True:
        url = CAREERS_BASE if page == 1 else f"{CAREERS_BASE}/?page={page}"
        print(f"  Listing page {page} … {url}")
        try:
            html = fetch(url)
        except Exception as e:
            print(f"  ERROR fetching page {page}: {e}")
            break

        found = UUID_RE.findall(html)
        if not found:
            break  # no more jobs

        new_found = 0
        for uid in found:
            if uid not in seen:
                seen.add(uid)
                ids.append(uid)
                new_found += 1

        if new_found == 0:
            break  # duplicate page, we're done

        # Check if there's a next page
        all_pages = [int(m) for m in PAGES_RE.findall(html)]
        max_page  = max(all_pages) if all_pages else page
        if page >= max_page and new_found == 0:
            break

        page += 1
        time.sleep(DELAY_SECS)

        # Safety limit
        if page > 30:
            break

    return ids


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — parse individual job pages
# ─────────────────────────────────────────────────────────────────────────────

class JobPageParser(HTMLParser):
    """Lightweight state-machine parser for careers-page.com job detail pages."""

    def __init__(self):
        super().__init__()
        self._stack: list[str] = []
        self._text_buf: list[str] = []

        # Collected data
        self.title       = ""
        self.location    = ""
        self.department  = ""
        self.emp_type    = ""
        self.work_mode   = ""
        self.description_blocks: list[tuple[str, str]] = []  # (tag, text)

        # Internal state
        self._in_title   = False
        self._capture    = False
        self._depth      = 0
        self._cap_tag    = ""

    # ── helpers ──────────────────────────────────────────────────────────────

    def _flush(self) -> str:
        t = " ".join(" ".join(self._text_buf).split())
        self._text_buf.clear()
        return t

    # ── parser callbacks ─────────────────────────────────────────────────────

    def handle_starttag(self, tag: str, attrs: list):
        self._stack.append(tag)
        attr_dict = dict(attrs)
        cls = attr_dict.get("class", "")

        if tag == "title":
            self._in_title = True

        # Capture heading tags — these mark section boundaries
        if tag in ("h1", "h2", "h3", "strong") and self._capture:
            self._flush()

    def handle_endtag(self, tag: str):
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

        if tag == "title":
            self._in_title = False
            if not self.title:
                raw = self._flush()
                self.title = raw.replace("| Outreach Recruitment Agency", "").strip()
            self._flush()

    def handle_data(self, data: str):
        text = data.strip()
        if not text:
            return

        if self._in_title:
            self._text_buf.append(text)
            return

        self._text_buf.append(text)

    def get_raw_text(self) -> str:
        return " ".join(self._text_buf)


def strip_tags(html: str) -> str:
    """Remove HTML tags, decode entities, normalise whitespace."""
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    html = re.sub(r"<li[^>]*>", "\n• ", html, flags=re.I)
    html = re.sub(r"<(?:h[1-6]|p|div|section)[^>]*>", "\n\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", "", html)
    html = html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    html = html.replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def extract_section(text: str, *headings: str) -> list[str]:
    """Extract bullet items under a named section heading."""
    # Build a combined stop pattern: any of the known headings OR two blank lines
    all_headings = [
        "Key Responsibilities", "Responsibilities", "Main Duties", "Duties",
        "Your tasks", "Your Tasks", "The Role", "Main Tasks",
        "Requirements", "What We're Looking For", "Qualifications",
        "Job Requirements", "Who We Need", "The Ideal Candidate", "Your Profile",
        "What's on Offer", "What We Offer", "Benefits", "Package", "Why Join",
        "On Offer", "We Offer", "Remuneration", "What You Get",
    ]
    stop_alts = "|".join(re.escape(h) for h in all_headings)
    stop_pat = rf"(?:\n\n(?:{stop_alts})|\Z)"

    for h in headings:
        pattern = rf"(?<!\w){re.escape(h)}\s*\n(.*?){stop_pat}"
        m = re.search(pattern, text, re.S | re.I)
        if m:
            block = m.group(1)
            items = [l.lstrip("•- ").strip() for l in block.splitlines() if l.strip() and l.strip() not in ("•", "-")]
            items = [i for i in items if len(i) > 5]
            if items:
                return items
    return []


def extract_about(text: str) -> str:
    """Extract the 'About / intro' paragraph(s)."""
    # Try to find text before the first major section heading
    first_section = re.search(
        r"(Key Responsibilities|Responsibilities|Requirements|What.s on Offer|About the Role)",
        text, re.I
    )
    if first_section:
        intro = text[:first_section.start()].strip()
        # Remove any "Job Description" heading lines
        intro = re.sub(r"^(Job Description|About|Overview|Role Overview)[:\s]*\n?", "", intro, flags=re.I).strip()
        if len(intro) > 50:
            return intro
    return text[:600].strip()


def _clean_location(city: str) -> str:
    """Normalise location string — avoid double-Malta."""
    city = city.strip()
    # If it already ends with ", Malta" or "Malta" don't append again
    if re.search(r",?\s*Malta\s*$", city, re.I):
        # Ensure consistent formatting
        city = re.sub(r",?\s*Malta\s*$", "", city, flags=re.I).strip()
    return f"{city}, Malta" if city else "Malta"


def parse_jsonld(html: str) -> dict:
    """Parse JSON-LD JobPosting schema from page HTML. Returns {} if not found."""
    schema = re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I)
    if not schema:
        return {}
    try:
        data = json.loads(schema.group(1))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def parse_job_page(uuid: str) -> dict | None:
    """Fetch and parse a single job page. Returns job dict or None on failure."""
    url = f"{CAREERS_BASE}/jobs/{uuid}"
    try:
        html = fetch(url)
    except Exception as e:
        print(f"    ERROR fetching {uuid}: {e}")
        return None

    ld = parse_jsonld(html)

    # ── Title ─────────────────────────────────────────────────────────────────
    from html import unescape as _unescape
    title = _unescape(ld.get("title", "").strip())
    if not title:
        m = re.search(r"<title>([^<]+)</title>", html, re.I)
        if m:
            raw = m.group(1).strip()
            title = re.sub(r"\s*[\|—–-]\s*(Outreach Recruitment.*|careers-page\.com.*)", "", raw, flags=re.I).strip()
        title = _unescape(title)
    if not title:
        return None

    # ── Location ──────────────────────────────────────────────────────────────
    location = "Malta"
    loc_data = ld.get("jobLocation", {})
    if isinstance(loc_data, dict):
        addr = loc_data.get("address", {})
        city = addr.get("addressLocality", "").strip()
        if city:
            location = _clean_location(city)
    if location == "Malta":
        # Fallback: grep well-known Maltese towns from HTML
        m = re.search(
            r"(Mellieħa|Mellieha|Valletta|Valetta|Sliema|Floriana|Birkirkara|"
            r"St\.? Julian'?s?|Msida|Gżira|Gzira|Żabbar|Zabbar|Naxxar|Paola|"
            r"Qormi|Żejtun|Zejtun|Luqa|Ta'? Xbiex|San Ġiljan|San Ġwann|Mosta)",
            html, re.I
        )
        if m:
            location = _clean_location(m.group(1))

    # ── Employment type ───────────────────────────────────────────────────────
    et_raw = ld.get("employmentType", "FULL_TIME")
    et_map = {"FULL_TIME": "Full-Time", "PART_TIME": "Part-Time",
              "CONTRACTOR": "Subcontracting", "TEMPORARY": "Part-Time",
              "INTERN": "Internship", "OTHER": "Full-Time"}
    emp_type = et_map.get(et_raw, "Full-Time")

    # ── Work mode ─────────────────────────────────────────────────────────────
    work_mode = "On-Site"
    if ld.get("jobLocationType") == "TELECOMMUTE":
        work_mode = "Remote"
    elif re.search(r"\bhybrid\b", title, re.I):
        work_mode = "Hybrid"
    elif re.search(r"\bhybrid\b", ld.get("description", ""), re.I):
        work_mode = "Hybrid"

    # ── Department ────────────────────────────────────────────────────────────
    department = ld.get("occupationalCategory", "").strip() or guess_department(title)

    # ── Description text from JSON-LD (clean, already parsed) ─────────────────
    # The JSON-LD description contains the full text with \n\n paragraph breaks
    # and \n• bullet items — perfect for section extraction
    desc_text = ld.get("description", "")
    if not desc_text:
        # Fallback to HTML body parsing
        h1_end = re.search(r'</h1>', html, re.I)
        body_html = html[h1_end.end():] if h1_end else html
        desc_text = strip_tags(body_html)
    else:
        # JSON-LD description itself contains HTML — strip it
        desc_text = strip_tags(desc_text)

    # ── Extract sections ──────────────────────────────────────────────────────
    about = extract_about(desc_text)
    responsibilities = extract_section(desc_text,
        "Key Responsibilities", "Responsibilities", "Main Duties", "Duties", "Key Duties",
        "Your tasks", "Your Tasks", "The Role", "Main Tasks", "Role Overview",
        "Key Tasks", "Day-to-day", "What you'll do", "What You'll Do")
    requirements = extract_section(desc_text,
        "Requirements", "What We're Looking For", "Qualifications", "What you need",
        "What We Need", "Candidate Profile", "Job Requirements", "Who We Need",
        "Who are we looking for", "The Ideal Candidate", "Skills & Experience",
        "Your Profile", "About You")
    offer = extract_section(desc_text,
        "What's on Offer", "What We Offer", "Benefits", "What's Offered", "Package",
        "On Offer", "We Offer", "Remuneration", "Why Join", "Why join us",
        "What You Get", "What's in it for you", "Compensation", "Perks")
    closing = ""
    m_closing = re.search(r"(If you (?:are|have|would)[^.]{10,80}\.)", desc_text, re.I)
    if m_closing:
        closing = m_closing.group(1).strip()

    return {
        "uuid":            uuid,
        "title":           title,
        "department":      department,
        "location":        location,
        "employment_type": emp_type,
        "work_mode":       work_mode,
        "about":           about,
        "responsibilities": "|".join(responsibilities),
        "requirements":    "|".join(requirements),
        "offer":           "|".join(offer),
        "closing":         closing,
    }


def guess_department(title: str) -> str:
    """Fallback category guess from job title keywords."""
    t = title.lower()
    if any(k in t for k in ["chef", "waiter", "server", "cook", "f&b", "food", "beverage", "bartend", "restaurant", "sommelier"]):
        return "Hospitality"
    if any(k in t for k in ["plumb", "weld", "electric", "techni", "engineer", "mainten", "mechanic", "hvac", "plant", "fabricat"]):
        return "Engineering & Maintenance"
    if any(k in t for k in ["it ", "developer", "software", "network", "systems", "data", "cyber", "devops", "cloud", ".net", "java"]):
        return "IT & Technology"
    if any(k in t for k in ["account", "finance", "audit", "tax", "bookkeep"]):
        return "Finance & Accounting"
    if any(k in t for k in ["nurse", "doctor", "health", "care", "medical", "pharmacy", "therapist"]):
        return "Healthcare"
    if any(k in t for k in ["sales", "business develop", "account manag"]):
        return "Sales"
    if any(k in t for k in ["market", "content", "seo", "social media", "digital", "brand"]):
        return "Marketing"
    if any(k in t for k in ["hr ", "human resource", "recruit", "talent", "people"]):
        return "HR & Recruitment"
    if any(k in t for k in ["logistics", "driver", "delivery", "warehouse", "supply chain", "transport"]):
        return "Logistics"
    if any(k in t for k in ["retail", "shop", "store", "cashier", "merchandis"]):
        return "Retail"
    if any(k in t for k in ["admin", "coordinator", "assistant", "secretary", "reception", "office"]):
        return "Administration"
    if any(k in t for k in ["project manag", "programme manag"]):
        return "Management"
    if any(k in t for k in ["teach", "educat", "tutor", "lecturer", "trainer"]):
        return "Education"
    return "General"


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — write CSV
# ─────────────────────────────────────────────────────────────────────────────

CSV_FIELDS = [
    "title", "slug", "category", "location", "employment_type", "work_mode",
    "apply_url", "about", "responsibilities", "requirements", "offer",
    "closing", "keywords", "date", "valid_through", "featured",
]


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def jobs_to_csv(jobs: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for j in jobs:
            writer.writerow({
                "title":           j["title"],
                "slug":            slugify(j["title"]),
                "category":        j["department"],
                "location":        j["location"],
                "employment_type": j["employment_type"],
                "work_mode":       j["work_mode"],
                "apply_url":       f"{CAREERS_BASE}/jobs/{j['uuid']}/apply",
                "about":           j["about"],
                "responsibilities": j["responsibilities"],
                "requirements":    j["requirements"],
                "offer":           j["offer"],
                "closing":         j["closing"],
                "keywords":        "",
                "date":            "2026-06-09",
                "valid_through":   "2026-12-31",
                "featured":        "true",
            })
    print(f"  CSV written → {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def load_existing_slugs() -> set[str]:
    if REGISTRY_PATH.exists():
        reg = json.loads(REGISTRY_PATH.read_text())
        return {j["slug"] for j in reg}
    return set()


def main() -> None:
    dry_run  = "--dry-run"  in sys.argv
    csv_only = "--csv-only" in sys.argv

    print("=" * 60)
    print("Outreach Recruitment — Careers Page Scraper")
    print("=" * 60)

    # ── 1. Collect all UUIDs from listing pages ───────────────────────────────
    print("\n[1/3] Collecting job listings …")
    all_uuids = get_all_job_ids()
    print(f"  Found {len(all_uuids)} job(s) on careers page")

    if dry_run:
        print("\nDry run — jobs found:")
        for uid in all_uuids:
            print(f"  {uid}")
        return

    # ── 2. Filter out already-imported jobs ────────────────────────────────────
    existing = load_existing_slugs()

    # UUIDs already added (we know their apply URLs)
    known_uuids = {
        "42b8f29a-855b-494c-916c-10b71e9d162d",  # plumber
        "1d27aeab-ef4d-4800-b734-ef6c2b516f03",  # welder
        "3cec7018-e57f-4346-96be-05a05a8316e2",  # server
    }
    to_fetch = [uid for uid in all_uuids if uid not in known_uuids]
    print(f"  {len(known_uuids)} already imported, {len(to_fetch)} to process")

    # ── 3. Fetch & parse each job page ─────────────────────────────────────────
    print(f"\n[2/3] Fetching {len(to_fetch)} job detail pages …")
    jobs_data: list[dict] = []
    errors = 0

    for i, uuid in enumerate(to_fetch, start=1):
        print(f"  [{i}/{len(to_fetch)}] {uuid} …", end=" ", flush=True)
        job = parse_job_page(uuid)
        if job:
            # Check if slug already exists
            slug = slugify(job["title"])
            if slug in existing:
                # Disambiguate with a counter
                counter = 2
                while f"{slug}-{counter}" in existing:
                    counter += 1
                slug = f"{slug}-{counter}"
            existing.add(slug)
            jobs_data.append(job)
            print(f"OK — {job['title']} ({job['location']})")
        else:
            print("FAILED")
            errors += 1
        time.sleep(DELAY_SECS)

    print(f"\n  Collected {len(jobs_data)} job(s), {errors} error(s)")

    if not jobs_data:
        print("No new jobs to add.")
        return

    # ── 4. Write CSV ──────────────────────────────────────────────────────────
    print(f"\n[3/3] Writing CSV …")
    jobs_to_csv(jobs_data, OUT_CSV)

    if csv_only:
        print(f"\nCSV-only mode. Review {OUT_CSV.name} then run:")
        print(f"  python3 tools/add_jobs_from_csv.py tools/jobs_scraped.csv")
        return

    # ── 5. Auto-import ────────────────────────────────────────────────────────
    print("\nImporting jobs …")
    result = subprocess.run(
        ["python3", str(ROOT / "tools" / "add_jobs_from_csv.py"), str(OUT_CSV)],
        cwd=str(ROOT), capture_output=False
    )

    if result.returncode == 0:
        print("\nAll done! Now run:")
        print("  git add -A && git commit -m 'Import all careers page jobs' && git push origin main")
    else:
        print("Import had errors. Check output above.")


if __name__ == "__main__":
    main()
