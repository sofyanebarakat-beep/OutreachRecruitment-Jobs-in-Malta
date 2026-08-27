#!/usr/bin/env python3
"""
migrate_jobs_to_rich.py
=======================
Convert the remaining OLD single-column job pages under ``jobs/`` to the RICH
"Client Accountant" template by re-rendering them through
``add_jobs_from_csv.generate_job_page`` (which clones ``jobs/plumber/index.html``).

The old pages are themselves an earlier generation of that same generator, so
their five content sections (About the Role / Key Responsibilities / Requirements
/ What's on Offer / How To Apply) are highly regular. This script extracts that
content, reconciles metadata against ``tools/jobs_registry.json`` (registry wins),
regenerates the page, runs a placeholder-leak guard, and writes the result back
to whichever file currently holds the real content.

Usage
-----
    python3 tools/migrate_jobs_to_rich.py --dry-run            # preview everything
    python3 tools/migrate_jobs_to_rich.py --dry-run --only barista,cleaner
    python3 tools/migrate_jobs_to_rich.py --limit 20           # convert first 20
    python3 tools/migrate_jobs_to_rich.py --report-only        # just classify

Never commits, never touches the registry / sitemap / jobs listing.
Idempotent: pages already containing ``job-layout`` are skipped.
"""
from __future__ import annotations

import argparse
import difflib
import html as _html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from add_jobs_from_csv import (  # noqa: E402
    JOBS,
    generate_job_page,
    load_registry,
)

SCRATCH = Path("/private/tmp/claude-501/-Users-sof-Documents-Projects-OutreachRecruitmentwebsite-OutreachRecruitment-Jobs-in-Malta/ad1cbfa1-6608-4d52-9473-e87bfde02bc0/scratchpad/migrate_preview")

# ── Heading handling ────────────────────────────────────────────────────────
# Canonical slots the generator fills.
SLOT_ABOUT, SLOT_RESP, SLOT_REQ, SLOT_OFFER, SLOT_CLOSING = (
    "about", "responsibilities", "requirements", "offer", "closing"
)
STANDARD = {
    "about the role": SLOT_ABOUT,
    "key responsibilities": SLOT_RESP,
    "requirements": SLOT_REQ,
    "what's on offer": SLOT_OFFER,
    "how to apply": SLOT_CLOSING,
}
# Fixed block the rich template already carries, or pure metadata that must not
# be folded into prose — ignore if seen in the source.
IGNORE_HEADINGS = {
    "about outreach recruitment", "frequently asked questions", "faq",
    "application deadline", "deadline", "location", "job location", "job type",
    "employment type", "work mode", "start date", "reporting to", "reports to",
    "interview process", "recruitment process", "salary", "job reference",
    "reference", "contract type", "hours", "working hours", "shift pattern",
}
# Non-standard headings merged into the nearest canonical slot.
MERGE = {
    "introduction": SLOT_ABOUT,
    "overview": SLOT_ABOUT,
    "role overview": SLOT_ABOUT,
    "the role": SLOT_ABOUT,
    "the opportunity": SLOT_ABOUT,
    "about the company": SLOT_ABOUT,
    "about our client": SLOT_ABOUT,
    "about the client": SLOT_ABOUT,
    "the company": SLOT_ABOUT,
    "responsibilities": SLOT_RESP,
    "duties": SLOT_RESP,
    "key duties": SLOT_RESP,
    "what you'll do": SLOT_RESP,
    "what you will do": SLOT_RESP,
    "key requirements": SLOT_REQ,
    "requirements & skills": SLOT_REQ,
    "skills required": SLOT_REQ,
    "skills and experience": SLOT_REQ,
    "skills & experience": SLOT_REQ,
    "experience required": SLOT_REQ,
    "languages required": SLOT_REQ,
    "language requirements": SLOT_REQ,
    "qualifications": SLOT_REQ,
    "preferred qualifications": SLOT_REQ,
    "nice to have": SLOT_REQ,
    "what we're looking for": SLOT_REQ,
    "what we are looking for": SLOT_REQ,
    "the ideal candidate": SLOT_REQ,
    "benefits": SLOT_OFFER,
    "what we offer": SLOT_OFFER,
    "what's in it for you": SLOT_OFFER,
    "career growth": SLOT_OFFER,
    "career growth opportunities": SLOT_OFFER,
    "growth opportunities": SLOT_OFFER,
    "why join": SLOT_OFFER,
    "why join us": SLOT_OFFER,
    "why join this company": SLOT_OFFER,
    "why join outreach recruitment?": SLOT_OFFER,
    "why join outreach recruitment": SLOT_OFFER,
    "our offer": SLOT_OFFER,
    "remuneration": SLOT_OFFER,
    "remuneration & benefits": SLOT_OFFER,
    "package": SLOT_OFFER,
    "compensation": SLOT_OFFER,
    "what we are looking for": SLOT_REQ,
    "what we're looking for": SLOT_REQ,
    "closing statement": SLOT_CLOSING,
    "closing": SLOT_CLOSING,
}

CANON_META = ("title", "category", "location", "employment_type",
              "work_mode", "date", "valid_through", "apply_url")

PLUMBER_APPLY_UUID = "42b8f29a-855b-494c-916c-10b71e9d162d"


# ── small helpers ──────────────────────────────────────────────────────────

def norm_heading(raw: str) -> str:
    s = _html.unescape(_html.unescape(raw))
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("’", "'").replace("‘", "'").replace("&#x27;", "'")
    s = re.sub(r"\s+", " ", s).strip().lower().rstrip(":")
    return s


def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|li|ul|div|h[1-6])>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = _html.unescape(_html.unescape(s))
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", s)
    return s.strip()


def li_items(block: str) -> list[str]:
    return [strip_tags(m).strip()
            for m in re.findall(r"<li[^>]*>(.*?)</li>", block, re.S)
            if strip_tags(m).strip()]


def paras(block: str) -> list[str]:
    """Prose block -> list of paragraph strings."""
    # normalise <p>..</p> and bare double-newline paragraphs
    parts = re.split(r"</p>\s*<p[^>]*>|\n\s*\n", block)
    out = []
    for p in parts:
        txt = strip_tags(p).strip()
        if txt:
            # collapse internal single newlines to spaces
            out.append(re.sub(r"\s*\n\s*", " ", txt))
    return out


def classify_file(text: str) -> str:
    if "job-layout" in text:
        return "rich"
    if len(text) < 4000 and re.search(
        r'http-equiv="refresh"|location\.replace|location\.href', text
    ):
        return "stub"
    return "old"


# ── parsing an old page ───────────────────────────────────────────────────

# Old pages come in two flavours: minified single-line Webflow HTML, and newer
# pretty-printed HTML with newlines/indentation between tags — hence the \s*.
SECTION_RE = re.compile(
    r'<div class="stack gap-07"[^>]*>\s*<h2 class="heading-h4"[^>]*>(.*?)</h2>\s*'
    r'<div class="w-richtext">(.*?)</div>\s*</div>', re.S
)


def parse_old(text: str) -> dict | None:
    """Return a parsed dict, or None if the page has no usable job body."""
    if "outreach-apply-frame" not in text:
        return None

    sections = SECTION_RE.findall(text)
    if not sections:
        return None

    slots = {SLOT_ABOUT: [], SLOT_RESP: [], SLOT_REQ: [], SLOT_OFFER: []}
    closing = ""
    merged: list[str] = []   # (heading -> slot) notes for the report
    dropped: list[str] = []  # headings whose content was discarded

    seen_standard = set()
    for raw_h, body in sections:
        h = norm_heading(raw_h)
        is_list = "<li" in body
        if h in STANDARD:
            slot = STANDARD[h]
            seen_standard.add(h)
        elif h in IGNORE_HEADINGS:
            continue
        elif h in MERGE:
            slot = MERGE[h]
            merged.append(f"{raw_h.strip()} -> {slot}")
        else:
            # unknown extra heading — drop its content (per "force into 5
            # sections"), but record it so it can be reviewed / hand-added.
            dropped.append(f"{raw_h.strip()} ({len(strip_tags(body))} chars)")
            continue

        if slot == SLOT_CLOSING:
            # Only the first <p>; the block also contains an "Apply Now" button.
            pm = re.search(r"<p[^>]*>(.*?)</p>", body, re.S)
            cand = strip_tags(pm.group(1)) if pm else ""
            cand = re.sub(r"\s*\n\s*", " ", cand).strip()
            # Drop any "... and quote reference OR-XX-2026-001 (when contacting …)."
            cand = re.sub(
                r"[,;]?\s*(and\s+|then\s+)?(please\s+)?"
                r"(quot(e|ing)\s+(the\s+)?(job\s+)?ref(erence)?\.?"
                r"|(job\s+)?ref(erence)?\.?\s*(number|no\.?|:)?\s*OR-[A-Z0-9]+-\d{4})"
                r"\b.*$",
                "", cand, flags=re.I | re.S,
            ).strip().rstrip(",;")
            cand = re.sub(r"\s+([.!?])", r"\1", cand)
            if cand and cand[-1] not in ".!?":
                cand += "."
            if len(cand) > len(closing):
                closing = cand
            continue

        if is_list:
            slots[slot].extend(li_items(body))
        else:
            for para in paras(body):
                # unknown-heading prose keeps a short lead-in
                slots[slot].append(para)

    if not seen_standard & {"about the role", "key responsibilities"}:
        return None  # not really the standard body

    def js(jsonld_key: str) -> str:
        m = re.search(rf'"{jsonld_key}":\s*"((?:[^"\\]|\\.)*)"', text)
        return _html.unescape(m.group(1).replace('\\"', '"')) if m else ""

    def detail(label: str) -> str:
        m = re.search(
            rf'<div class="caption blue-caption">\s*{re.escape(label)}\s*</div>\s*'
            rf'<div class="text-medium">\s*([^<]*?)\s*</div>', text,
        )
        return _html.unescape(_html.unescape(m.group(1).strip())) if m else ""

    apply_m = re.search(
        r'<iframe class="outreach-apply-frame[^"]*"[^>]*data-src="([^"]+)"', text, re.S
    )
    loc = js("streetAddress") or detail("Target Location")
    # streetAddress is usually "City, Malta"
    if loc and not loc.lower().endswith("malta"):
        loc = f"{loc}, Malta"

    return {
        "title": js("title"),
        "category": detail("Category"),
        "employment_type": detail("Employment Type"),
        "work_mode": detail("Work Mode"),
        "job_reference": detail("Job Reference"),
        "location": loc,
        "date": js("datePosted"),
        "valid_through": js("validThrough"),
        "apply_url": apply_m.group(1) if apply_m else "",
        "about": "</p><p>".join(slots[SLOT_ABOUT]),
        "responsibilities": "|".join(slots[SLOT_RESP]),
        "requirements": "|".join(slots[SLOT_REQ]),
        "offer": "|".join(slots[SLOT_OFFER]),
        "closing": closing,
        "_merged": merged,
        "_dropped": dropped,
    }


# ── leak guard ────────────────────────────────────────────────────────────

def leak_hits(html: str, job: dict) -> list[str]:
    # Ignore the carousel — its cards legitimately carry other jobs' real data
    # (a sibling job really located in Mellieħa, a real /jobs/site-coordinator …).
    scan = re.sub(
        r'<div class="similar-jobs-track".*?</div></div></div></div></section></main>',
        "", html, flags=re.S,
    )
    hits = []
    for pat in (r"[Pp]lumber", PLUMBER_APPLY_UUID):
        if re.search(pat, scan):
            hits.append(pat)
    # "Mellieħa" is only a leak when this job is NOT actually in Mellieħa.
    if "mellieħa" not in job["location"].lower() and "Mellieħa" in scan:
        hits.append("Mellieħa (job not in Mellieħa)")
    if (job["category"] != "Engineering & Maintenance"
            and "Engineering &amp; Maintenance" in scan):
        hits.append("Engineering &amp; Maintenance (wrong category)")
    return hits


# ── target discovery ─────────────────────────────────────────────────────

def discover() -> dict[str, list[Path]]:
    """slug -> list of content file Path(s) that still hold OLD markup."""
    out: dict[str, list[Path]] = {}
    for p in sorted(JOBS.rglob("*.html")):
        rel = p.relative_to(JOBS)
        if rel.parts[0] == "index.html" or p.name == "index.html" and len(rel.parts) == 1:
            continue
        if p.name == "index.html":
            slug = rel.parts[0]
        else:
            slug = p.stem
        if slug == "index":
            continue
        if slug.endswith("-apply"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if classify_file(text) == "old":
            out.setdefault(slug, []).append(p)
    return out


# ── main ─────────────────────────────────────────────────────────────────

def build_job(slug: str, parsed: dict, reg: dict | None) -> tuple[dict, list[str]]:
    notes = []
    reg = reg or {}

    def pick(key, fallback):
        rv = reg.get(key)
        pv = parsed.get(key) or fallback
        if rv and pv and str(rv).strip() != str(pv).strip() and key in (
            "category", "apply_url", "employment_type", "work_mode"
        ):
            notes.append(f"{key}: registry={rv!r} page={parsed.get(key)!r}")
        return rv or pv

    from datetime import date, timedelta
    today = date.today().isoformat()
    one_year = (date.today() + timedelta(days=365)).isoformat()

    job = {
        "slug": slug,
        "title": pick("title", slug.replace("-", " ").title()),
        "category": pick("category", "General"),
        "location": pick("location", "Malta"),
        "employment_type": pick("employment_type", "Full-Time"),
        "work_mode": pick("work_mode", "On-Site"),
        "apply_url": pick("apply_url", ""),
        "date": pick("date", today),
        "valid_through": pick("valid_through", one_year),
        "keywords": reg.get("keywords", ""),
        "featured": reg.get("featured", True),
        "status": reg.get("status"),
        "about": parsed["about"],
        "responsibilities": parsed["responsibilities"],
        "requirements": parsed["requirements"],
        "offer": parsed["offer"],
        "closing": parsed["closing"],
    }
    job["location_slug"] = reg.get("location_slug") or job["location"].lower()
    return job, notes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated slugs")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    registry = load_registry()
    reg_by_slug = {j["slug"]: j for j in registry}

    targets = discover()
    only = {s.strip() for s in args.only.split(",")} if args.only else None
    if only:
        targets = {s: v for s, v in targets.items() if s in only}

    # order: open jobs before closed/expired, then alphabetical
    def sort_key(slug: str):
        st = reg_by_slug.get(slug, {}).get("status")
        return (0 if st in (None, "open") else 1, slug)

    slugs = sorted(targets, key=sort_key)
    if args.limit:
        slugs = slugs[: args.limit]

    stats = {k: [] for k in (
        "converted", "skipped_no_body", "not_in_registry",
        "leak_error", "parse_error", "merged", "dropped"
    )}

    if args.dry_run:
        SCRATCH.mkdir(parents=True, exist_ok=True)

    for slug in slugs:
        files = targets[slug]
        text = files[0].read_text(encoding="utf-8", errors="replace")
        try:
            parsed = parse_old(text)
        except Exception as e:  # noqa: BLE001
            stats["parse_error"].append(f"{slug}: {e}")
            continue
        if parsed is None:
            stats["skipped_no_body"].append(slug)
            continue

        reg = reg_by_slug.get(slug)
        if reg is None:
            stats["not_in_registry"].append(slug)
        job, notes = build_job(slug, parsed, reg)

        if parsed["_merged"]:
            stats["merged"].append(f"{slug}: " + "; ".join(parsed["_merged"]))
        if parsed["_dropped"]:
            stats["dropped"].append(f"{slug}: " + "; ".join(parsed["_dropped"]))

        try:
            html = generate_job_page(job, other_jobs=registry)
        except Exception as e:  # noqa: BLE001
            stats["parse_error"].append(f"{slug}: generate failed: {e}")
            continue

        hits = leak_hits(html, job)
        if hits:
            stats["leak_error"].append(f"{slug}: {hits}")
            continue

        rel_names = ", ".join(str(f.relative_to(JOBS.parent)) for f in files)
        if args.report_only:
            stats["converted"].append(f"{slug}  [{rel_names}]")
            continue

        if args.dry_run:
            old_lines = text.splitlines(keepends=True)
            new_lines = html.splitlines(keepends=True)
            diff = list(difflib.unified_diff(
                old_lines, new_lines, fromfile=f"a/{slug}", tofile=f"b/{slug}", n=0
            ))
            (SCRATCH / f"{slug}.html").write_text(html, encoding="utf-8")
            add = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
            rem = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
            note = f"  ({'; '.join(notes)})" if notes else ""
            stats["converted"].append(
                f"{slug:<45} {len(old_lines):>4} -> {len(new_lines):>4} lines "
                f"(+{add}/-{rem}){note}"
            )
        else:
            for f in files:
                f.write_text(html, encoding="utf-8")
            note = f"  ({'; '.join(notes)})" if notes else ""
            stats["converted"].append(f"{slug}  [{rel_names}]{note}")

    # ── report ──
    print("\n" + "=" * 72)
    mode = ("REPORT ONLY" if args.report_only
            else "DRY RUN" if args.dry_run else "WRITE")
    print(f"migrate_jobs_to_rich — {mode}")
    print("=" * 72)
    print(f"\nCONVERTED ({len(stats['converted'])}):")
    for s in stats["converted"]:
        print("  " + s)
    for key, label in (
        ("skipped_no_body", "SKIPPED — non-standard / no job body (need manual conversion)"),
        ("not_in_registry", "NOT IN REGISTRY (used page data)"),
        ("merged", "MERGED extra sections"),
        ("dropped", "DROPPED content"),
        ("leak_error", "LEAK GUARD BLOCKED (not written)"),
        ("parse_error", "ERRORS"),
    ):
        if stats[key]:
            print(f"\n{label} ({len(stats[key])}):")
            for s in stats[key]:
                print("  " + s)
    if args.dry_run:
        print(f"\nPreview HTML written to: {SCRATCH}")


if __name__ == "__main__":
    main()
