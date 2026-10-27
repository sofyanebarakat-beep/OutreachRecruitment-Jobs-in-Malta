#!/usr/bin/env python3
"""
verify_job_page.py — the gate every new or updated job page must pass before it goes live.

Checks (on both jobs/<slug>/index.html and jobs/<slug>.html):
  - JobPosting JSON-LD parses and has the fields Google for Jobs needs
  - canonical, <title> and <h1> belong to this job
  - the apply link uses this job's ATS uuid, and no other ATS uuid is on the page
  - salary matches the careers page (or the owner's own registry salary);
    never an invented number when neither has one
  - nothing left over from the template page it was cloned from
  - reference number and deadline are not visible
  - FAQPage schema questions == visible FAQ questions
  - the page renders in headless Chrome (h1, FAQ, enough text)

Usage:
  python3 tools/verify_job_page.py <slug> [<slug> ...]     # uses registry + saved fact sheets
"""
from __future__ import annotations

import html as htmllib
import json
import re
import subprocess
import sys
import tempfile
import threading
from datetime import date
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ats_facts import load_snapshot  # noqa: E402

SITE = "https://outreachrecruitment.net"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
JSONLD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
REQUIRED = ["title", "description", "datePosted", "validThrough", "employmentType", "hiringOrganization",
            "jobLocation"]
# Pages new jobs are cloned from — their names must not survive in a new page.
TEMPLATE_MARKERS = ["client-accountant", "Client Accountant", "head-chef-in-gozo", "Head Chef in Gozo",
                    "jobs/plumber", "7dac46c7"]


def jsonld_items(page: str) -> list[dict]:
    items = []
    for block in JSONLD_RE.findall(page):
        try:
            data = json.loads(block)
        except Exception:
            items.append({"@type": "__invalid__"})
            continue
        for item in data if isinstance(data, list) else data.get("@graph", [data]):
            if isinstance(item, dict):
                items.append(item)
    return items


def visible_text(page: str) -> str:
    body = page.split("<body", 1)[-1]
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"<(script|style|template|noscript)\b.*?</\1>", " ", body, flags=re.S | re.I)
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", body)))


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", htmllib.unescape(s).lower()).strip()


def numbers_in(text: str) -> set[int]:
    out = set()
    for raw, k in re.findall(r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*([kK])?", text):
        v = float(raw.replace(",", ""))
        out.add(int(round(v * 1000 if k else v)))
    return out


def expected_salary(job: dict, facts: dict | None) -> tuple[float, float] | None:
    s = (facts or {}).get("salary")
    if s:
        return float(s["min"]), float(s["max"])
    reg = job.get("salary") or job.get("owner_salary")  # the owner's own figure, e.g. "€19,200–€20,000"
    if reg:
        nums = sorted(numbers_in(str(reg)))
        if nums:
            return float(nums[0]), float(nums[-1])
    return None


def check_static(path: Path, job: dict, facts: dict | None) -> list[str]:
    page = path.read_text(encoding="utf-8")
    slug, uuid, title = job["slug"], "", job["title"]
    m = UUID_RE.search(job.get("apply_url", ""))
    uuid = m.group(0) if m else ""
    p: list[str] = []

    items = jsonld_items(page)
    if any(i.get("@type") == "__invalid__" for i in items):
        p.append("a JSON-LD block does not parse")
    postings = [i for i in items if i.get("@type") == "JobPosting"]
    if len(postings) != 1:
        p.append(f"expected 1 JobPosting schema, found {len(postings)}")
    posting = postings[0] if postings else {}
    missing = [k for k in REQUIRED if not posting.get(k)]
    if missing:
        p.append("JobPosting missing " + ", ".join(missing))
    if str(posting.get("validThrough", "9999"))[:10] < date.today().isoformat():
        p.append("JobPosting validThrough is in the past")

    canon = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*>', page)
    if not canon or f"/jobs/{slug}" not in canon.group(0):
        p.append("canonical does not point to this job")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    if not h1 or norm(title)[:25] not in norm(re.sub(r"<[^>]+>", " ", h1.group(1))):
        p.append("<h1> does not contain the job title")
    t = re.search(r"<title>(.*?)</title>", page, re.S)
    stems = lambda s: {w[:5] for w in norm(s).split()}
    if not t or not {w[:5] for w in norm(title).split()[:1]} <= stems(t.group(1)):
        p.append("<title> does not mention the job")

    # Apply link / uuid
    if not uuid or f"{uuid}/apply" not in page:
        p.append("apply link with this job's ATS uuid not found")
    others = {u for u in UUID_RE.findall(page) if u != uuid
              and re.search(rf"careers-page\.com/jobs/{u}", page)}
    if others:
        p.append(f"page links other ATS job(s): {', '.join(sorted(others))[:80]}")

    # Salary
    text = visible_text(page)
    want = expected_salary(job, facts)
    base = posting.get("baseSalary") or {}
    val = base.get("value", {}) if isinstance(base, dict) else {}
    if want:
        lo, hi = want
        got = (val.get("minValue", val.get("value")), val.get("maxValue", val.get("value"))) if isinstance(val, dict) else (None, None)
        try:
            ok = abs(float(got[0]) - lo) < 1 and abs(float(got[1]) - hi) < 1
        except (TypeError, ValueError):
            ok = False
        if not ok:
            p.append(f"schema baseSalary {got} does not match the careers page ({lo:g}–{hi:g})")
        if int(round(lo)) not in numbers_in(text):
            p.append(f"salary {lo:g} is not shown on the page")
    elif facts is not None:  # without a fact sheet we cannot tell where a salary came from
        if base:
            p.append("schema has a baseSalary but the careers page gives none (invented salary)")
        if "competitive" not in text.lower():
            p.append("no salary on the careers page, but the page does not say 'Competitive salary'")

    # Template leftovers (outside the similar-jobs carousel)
    core = re.sub(r'<div[^>]*id="similar-jobs".*?(?=</section>)', " ", page, flags=re.S)
    own = f"{slug} {title} {uuid}".lower()
    leaks = [mk for mk in TEMPLATE_MARKERS if mk.lower() in core.lower() and mk.lower() not in own]
    if leaks:
        p.append("left over from the template: " + ", ".join(leaks))

    # An open job must not carry the closed-page treatment; it must have a real category.
    if "<!-- job-closed:head -->" in page:
        p.append("page is still marked 'Position Closed'")
    if (job.get("category") or "General").strip().lower() in ("", "general"):
        p.append("job has no real category (still 'General')")

    # Private data
    if re.search(r"\bOR-[A-Z]{2,8}-\d{4}-\d{2,4}\b", text):
        p.append("reference number is visible")
    if re.search(r"\b2029\b|application deadline|closing date", text, re.I):
        p.append("deadline is visible")

    # FAQ schema == visible FAQ
    faq = next((i for i in items if i.get("@type") == "FAQPage"), None)
    visible_q = [norm(re.sub(r"<[^>]+>", " ", q)) for q in
                 re.findall(r'class="faq-item-top"[^>]*>\s*<h3[^>]*>(.*?)</h3>', page, re.S)]
    if not faq:
        p.append("no FAQPage schema")
    else:
        schema_q = [norm(q.get("name", "")) for q in faq.get("mainEntity", [])]
        if sorted(schema_q) != sorted(visible_q):
            p.append(f"FAQ schema ({len(schema_q)} questions) does not match the visible FAQ ({len(visible_q)})")
    return p


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D401
        pass

    def do_GET(self):  # noqa: N802
        # This simple server cannot stream video (no Range support): the hero video then never
        # finishes and headless Chrome hangs. The check does not need video, so refuse it.
        if self.path.split("?")[0].lower().endswith((".webm", ".mp4", ".mov")):
            self.send_error(404)
            return
        super().do_GET()


def check_render(slug: str, title: str) -> list[str]:
    """Render the page in headless Chrome against a local server. No --virtual-time-budget: with the
    streaming hero video, simulated time never advances and Chrome hangs (seen 2026-10-27). --timeout
    makes Chrome dump the DOM after at most 20 s of real time."""
    if not Path(CHROME).exists():
        return []
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory() as profile:
            out = subprocess.run(
                [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
                 "--timeout=20000", "--autoplay-policy=user-gesture-required", "--dump-dom",
                 f"http://127.0.0.1:{server.server_address[1]}/jobs/{slug}/"],
                capture_output=True, text=True, timeout=90)
        dom = out.stdout
    except Exception as e:
        return [f"Chrome could not render the page ({e})"]
    finally:
        server.shutdown()
    p = []
    if len(visible_text(dom)) < 1500:
        p.append("rendered page has almost no text")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", dom, re.S)
    if not h1 or norm(title)[:25] not in norm(re.sub(r"<[^>]+>", " ", h1.group(1))):
        p.append("rendered page shows no job-title heading")
    if "faq-item" not in dom:
        p.append("rendered page has no FAQ")
    return p


STUB_TARGET_RE = re.compile(r'url=https?://outreachrecruitment\.net/jobs/([a-z0-9-]+)|'
                            r'location\.replace\(["\']https?://outreachrecruitment\.net/jobs/([a-z0-9-]+)')


def real_slug(slug: str, _hops: int = 0) -> str:
    """Older jobs keep only a small redirect stub at jobs/<slug>; the page lives at the target."""
    if _hops > 2:
        return slug
    for f in (ROOT / "jobs" / f"{slug}.html", ROOT / "jobs" / slug / "index.html"):
        if f.exists():
            text = f.read_text(encoding="utf-8", errors="replace")
            if len(text) > 5000:
                return slug
            m = STUB_TARGET_RE.search(text)
            if m and (m.group(1) or m.group(2)) != slug:
                return real_slug(m.group(1) or m.group(2), _hops + 1)
    return slug


def real_pages(slug: str) -> list[Path]:
    """jobs/<slug>/index.html and/or the flat jobs/<slug>.html (GitHub Pages serves the flat
    file first), skipping redirect stubs — following a stub to the page it points to."""
    slug = real_slug(slug)
    out = []
    for f in (ROOT / "jobs" / slug / "index.html", ROOT / "jobs" / f"{slug}.html"):
        if f.exists():
            head = f.read_text(encoding="utf-8", errors="replace")
            if len(head) > 5000 and 'http-equiv="refresh"' not in head[:3000].lower():
                out.append(f)
    return out


def verify(job: dict, facts: dict | None = None, render: bool = True) -> list[str]:
    job = dict(job, slug=real_slug(job["slug"]))
    slug = job["slug"]
    files = real_pages(slug)
    problems = [] if files else [f"no page found for jobs/{slug}"]
    for f in files:
        if f.exists():
            problems += [f"{f.name}: {x}" if f.name != "index.html" else x for x in check_static(f, job, facts)]
    if render and not problems:
        problems += check_render(slug, job["title"])
    return problems


if __name__ == "__main__":
    reg = {j["slug"]: j for j in json.loads((ROOT / "tools" / "jobs_registry.json").read_text())}
    bad = 0
    for s in sys.argv[1:]:
        job = reg.get(s)
        if not job:
            print(f"{s}: not in registry")
            bad += 1
            continue
        m = UUID_RE.search(job.get("apply_url", ""))
        probs = verify(job, load_snapshot(m.group(0)) if m else None)
        bad += bool(probs)
        print(f"{s}: " + ("OK ✅" if not probs else "\n  - " + "\n  - ".join(probs)))
    sys.exit(1 if bad else 0)
