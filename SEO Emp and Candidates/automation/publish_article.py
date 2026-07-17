#!/usr/bin/env python3
"""Build a generated Markdown draft into a live, publish-ready HTML page.

Unlike generate_daily_posts.py, this script owns every link, image, and CTA in the
final page itself — the model's Markdown body is treated as untrusted content for the
article prose only. This is what makes unattended daily auto-publish safe from the two
bug classes a human review previously caught: broken links (links are never authored by
the model) and stray HTML/script injection (all model text is HTML-escaped before use).

It does NOT catch factual errors in the prose itself (invented claims, wrong emphasis) —
that class of risk is only reduced by the stronger prompt in generate_daily_posts.py, not
eliminated. See SKILL.md and the workflow's own comments for the accepted trade-off.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_SOURCE = ROOT / "blog" / "pre-departure-course-certificate-malta.html"
BLOG_INDEX = ROOT / "blog" / "index.html"
SITEMAP_BLOG = ROOT / "sitemaps" / "sitemap-blog.xml"
SITEMAP_PAGES = ROOT / "sitemaps" / "sitemap-pages.xml"

DATE_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


class BuildError(Exception):
    """Raised when a draft can't be safely turned into a page. Caller skips it."""


# --------------------------------------------------------------------------------
# Per-pillar fixed data. The model never supplies links, images, or CTA copy — all
# of it comes from here, so it is always correct by construction.
# --------------------------------------------------------------------------------

IMAGE_POOL = {
    "Employer": [
        ("/assets/jobs-malta-hr-admin.png", "Recruiter and candidate shaking hands during a recruitment process in Malta"),
        ("/assets/recruitment-agency-in-malta-hero.png", "Recruiter meeting with a candidate and employer in a modern Malta office"),
        ("/assets/recruitment.png", "Recruitment consultant reviewing candidate shortlists for a Malta employer"),
    ],
    "Candidate": [
        ("/assets/jobs-malta-hospitality.png", "Hospitality staff serving guests in a Malta hotel restaurant"),
        ("/assets/jobs-malta-customer-support.png", "Customer support professional at work in a Malta office"),
        ("/assets/about-us.jpg", "Team meeting in a modern Malta office environment"),
    ],
    "JobsInMalta": [
        ("/assets/jobs-malta-hospitality.png", "Hospitality staff serving guests in a Malta hotel"),
        ("/assets/jobs-malta-construction.png", "Construction workers on a job site in Malta"),
        ("/assets/jobs-malta-finance.png", "Finance professionals working in a Malta office"),
        ("/assets/jobs-malta-it-tech.png", "IT professional working in a Malta office"),
        ("/assets/hospitality-manpower-solutions-malta-hero.png", "Hospitality team preparing to welcome guests in a Malta hotel"),
    ],
    "StudyInMalta": [
        ("/assets/studyinmaltaa.png", "International students studying together in Malta"),
        ("/assets/applystudyinmalta.png", "Student completing a study-in-Malta application online"),
        ("/assets/visastudy.jpg", "International student reviewing study and visa documents for Malta"),
    ],
    "Brand": [
        ("/assets/why-employers-malta-trust-outreach-recruitment-thumb.jpg", "Recruiter and employer reviewing candidate shortlist together in a Malta office"),
        ("/assets/about-us.jpg", "Team meeting in a modern Malta office environment"),
        ("/assets/recruitment-agency-in-malta-hero.png", "Recruiter meeting with a candidate and employer in a modern Malta office"),
    ],
}

CTA_MAP = {
    "Employer": [
        ("Need support filling a role in Malta?",
         "Outreach Recruitment can help you shortlist engaged, pre-vetted candidates and manage communication through every stage of the process.",
         "Request recruitment support", "/contact-us.html", False),
        ("Ready to fill your next role in Malta?",
         "Speak to Outreach Recruitment about sourcing, screening, and keeping candidates engaged from first contact to offer.",
         "View employer services", "/employers.html", False),
    ],
    "Candidate": [
        ("Browse jobs in Malta now",
         "See current vacancies across every sector Outreach Recruitment recruits for.",
         "Browse jobs in Malta", "/jobs/", False),
        ("Ready to apply?",
         "Register your interest with Outreach Recruitment and get matched with current openings in Malta.",
         "Register your interest", "/jobs/people-connector.html", False),
    ],
    "JobsInMalta": [
        ("See what's hiring right now",
         "Browse live vacancies across Malta's industries.",
         "Browse jobs in Malta", "/jobs/", False),
        ("Find your next role",
         "Register your interest and get matched with current openings across Malta.",
         "Register your interest", "/jobs/people-connector.html", False),
    ],
    "StudyInMalta": [
        ("Explore study programmes in Malta",
         "Browse bachelor's, master's, and English language programmes available to international students.",
         "Browse available programs", "/study-in-malta#programs-table", False),
        ("Ready to Study in Malta?",
         "Start your application today and get guidance on programmes, visas, and next steps.",
         "Apply Now", "https://apply.outreachstudy.eu/", True),
    ],
    "Brand": [
        ("Want to work with Outreach Recruitment?",
         "Whether you're hiring or job hunting, get in touch to see how we can help.",
         "Contact Outreach Recruitment", "/contact-us.html", False),
        ("Learn more about us",
         "See how Outreach Recruitment supports employers and candidates across Malta.",
         "About Outreach Recruitment", "/about.html", False),
    ],
}

# (href, image, alt, tag, title) — hand-verified real pages only.
RELATED_POOL = {
    "Employer": [
        ("/blog/why-employers-in-malta-trust-outreach-recruitment.html", "/assets/why-employers-malta-trust-outreach-recruitment-thumb.jpg", "Recruiter and employer reviewing candidate shortlist together in a Malta office", "Employers", "Why employers in Malta trust Outreach Recruitment to hire right"),
        ("/blog/recruitment-agency-in-malta.html", "/assets/recruitment-agency-in-malta-thumb.jpg", "Recruiter meeting with a candidate and employer in a modern Malta office", "Candidates &amp; Employers", "Recruitment agency in Malta: a guide for candidates and employers"),
        ("/blog/hospitality-manpower-solutions-malta.html", "/assets/hospitality-manpower-solutions-malta-thumb.jpg", "Hotel manager and recruitment consultant reviewing hospitality manpower needs in a Malta hotel lobby", "Employers", "Hospitality Manpower Solutions in Malta for Employers"),
        ("/blog/what-to-expect-from-a-recruitment-agency-in-malta.html", "/assets/jobs-malta-hr-admin.png", "Recruitment consultants reviewing candidate profiles in a Malta office", "Candidates", "What to expect from a recruitment agency as a job seeker in Malta"),
    ],
    "Candidate": [
        ("/blog/cv-writing-tips-how-to-get-hired-in-malta.html", "/assets/FastApplication.png", "Job seeker preparing a CV on a laptop before applying for jobs in Malta", "Candidates", "CV writing tips that get you hired in Malta"),
        ("/blog/what-to-expect-from-a-recruitment-agency-in-malta.html", "/assets/jobs-malta-hr-admin.png", "Recruitment consultants reviewing candidate profiles in a Malta office", "Candidates", "What to expect from a recruitment agency as a job seeker in Malta"),
        ("/blog/how-to-answer-common-interview-questions-in-malta.html", "/assets/Jobs in Malta (9).png", "Two professionals shaking hands after a successful job interview in Malta", "Candidates", "How to answer common interview questions in Malta"),
        ("/blog/what-documents-do-i-need-to-apply-for-a-job-in-malta.html", "/assets/what-documents-do-i-need-to-apply-for-a-job-in-malta-thumb.jpg", "Candidate preparing CV, certificates, and identity documents before applying for jobs in Malta", "Candidates", "What documents do I need to apply for a job in Malta?"),
        ("/blog/best-industries-hiring-in-malta-right-now.html", "/assets/Jobs in Malta (12).png", "A successful handshake after a job interview in Malta, resume on the desk", "Candidates", "Best industries hiring in Malta right now"),
    ],
    "JobsInMalta": [
        ("/blog/best-industries-hiring-in-malta-right-now.html", "/assets/Jobs in Malta (12).png", "A successful handshake after a job interview in Malta, resume on the desk", "Candidates", "Best industries hiring in Malta right now"),
        ("/blog/hospitality-manpower-solutions-malta.html", "/assets/hospitality-manpower-solutions-malta-thumb.jpg", "Hotel manager and recruitment consultant reviewing hospitality manpower needs in a Malta hotel lobby", "Employers", "Hospitality Manpower Solutions in Malta for Employers"),
        ("/blog/recruitment-agency-in-malta.html", "/assets/recruitment-agency-in-malta-thumb.jpg", "Recruiter meeting with a candidate and employer in a modern Malta office", "Candidates &amp; Employers", "Recruitment agency in Malta: a guide for candidates and employers"),
        ("/blog/cv-writing-tips-how-to-get-hired-in-malta.html", "/assets/FastApplication.png", "Job seeker preparing a CV on a laptop before applying for jobs in Malta", "Candidates", "CV writing tips that get you hired in Malta"),
    ],
    "StudyInMalta": [
        ("/why-malta-is-becoming-europes-top-destination-for-international-students.html", "/assets/studyinmaltaa.png", "International students exploring Malta", "Study in Malta", "Why Malta is becoming Europe's top destination for international students"),
        ("/how-to-apply-to-study-in-malta-a-step-by-step-guide.html", "/assets/applystudyinmalta.png", "Student completing a study-in-Malta application online", "Study in Malta", "How to apply to study in Malta: a step-by-step guide"),
        ("/student-accommodation-in-malta.html", "/assets/studyinmaltaa.png", "Student accommodation building in Malta", "Study in Malta", "Student accommodation in Malta"),
        ("/working-while-studying-in-malta.html", "/assets/visastudy.jpg", "International student balancing work and study in Malta", "Study in Malta", "Working while studying in Malta"),
    ],
    "Brand": [
        ("/blog/why-employers-in-malta-trust-outreach-recruitment.html", "/assets/why-employers-malta-trust-outreach-recruitment-thumb.jpg", "Recruiter and employer reviewing candidate shortlist together in a Malta office", "Employers", "Why employers in Malta trust Outreach Recruitment to hire right"),
        ("/blog/recruitment-agency-in-malta.html", "/assets/recruitment-agency-in-malta-thumb.jpg", "Recruiter meeting with a candidate and employer in a modern Malta office", "Candidates &amp; Employers", "Recruitment agency in Malta: a guide for candidates and employers"),
        ("/blog/your-trusted-hospitality-recruitment-agency-in-malta.html", "/assets/your-trusted-hospitality-recruitment-agency-in-malta-thumb-v2.jpg", "Recruitment consultant, hospitality candidate, and hiring manager reviewing opportunities in a bright Malta hotel setting", "Candidates &amp; Employers", "Your Trusted Hospitality Recruitment Agency in Malta"),
        ("/blog/what-to-expect-from-a-recruitment-agency-in-malta.html", "/assets/jobs-malta-hr-admin.png", "Recruitment consultants reviewing candidate profiles in a Malta office", "Candidates", "What to expect from a recruitment agency as a job seeker in Malta"),
    ],
}

TAG_MAP = {
    "Employer": "Employers",
    "Candidate": "Candidates",
    "JobsInMalta": "Jobs in Malta",
    "StudyInMalta": "Study in Malta",
    "Brand": "Candidates &amp; Employers",
}

# blog/index.html only has "employers" and "candidates" data-blog-section groups.
# StudyInMalta pages aren't listed there at all, matching the site's existing
# precedent for its other root-level Study in Malta pages.
BLOG_INDEX_SECTION = {
    "Employer": "employers",
    "Candidate": "candidates",
    "JobsInMalta": "candidates",
    "Brand": "employers",
}


def pick(pool: list, slug: str):
    """Deterministic pseudo-random pick so the same slug always gets the same asset,
    but different slugs spread across the pool instead of always picking index 0."""
    idx = zlib.crc32(slug.encode()) % len(pool)
    return pool[idx]


# --------------------------------------------------------------------------------
# Frontmatter + body parsing
# --------------------------------------------------------------------------------

def strip_wrapping_fence(text: str) -> str:
    lines = text.strip("\n").split("\n")
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    text = strip_wrapping_fence(text)
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        raise BuildError("No YAML frontmatter block (--- ... ---) found")
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"').strip("'")
        fm[key.strip()] = value
    required = ["title", "slug", "pillar", "audience", "primary_keyword", "seo_title", "meta_description", "date"]
    missing = [k for k in required if not fm.get(k)]
    if missing:
        raise BuildError(f"Frontmatter missing required keys: {missing}")
    if fm["pillar"] not in IMAGE_POOL:
        raise BuildError(f"Unknown pillar {fm['pillar']!r}")
    fm["slug"] = re.sub(r"[^a-z0-9-]", "", fm["slug"].lower().replace(" ", "-"))
    if not fm["slug"]:
        raise BuildError("Slug is empty after normalisation")
    return fm, body.strip("\n")


# --------------------------------------------------------------------------------
# Minimal Markdown -> HTML for the constrained subset the prompt asks for.
# All text is HTML-escaped before any tag is added, so stray HTML/script text
# from the model can never become live markup.
# --------------------------------------------------------------------------------

def inline_md(text: str) -> str:
    escaped = html.escape(text.strip(), quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def render_table(lines: list[str]) -> str:
    rows = [
        [c.strip() for c in line.strip().strip("|").split("|")]
        for line in lines
        if not re.match(r"^\s*\|?[\s:|-]+\|?\s*$", line)
    ]
    if not rows:
        return ""
    head, *body_rows = rows
    thead = "".join(f"<th>{inline_md(c)}</th>" for c in head)
    tbody = "".join(
        "<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in row) + "</tr>"
        for row in body_rows
    )
    return (
        '<div class="article-table-wrap"><table class="check-table">'
        f"<thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>"
    )


def render_blocks(md: str) -> str:
    """Render a chunk of Markdown (no headings) into paragraphs/lists/tables."""
    out = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(render_table(block))
            continue
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline_md(it)}</li>" for it in items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline_md(it)}</li>" for it in items) + "</ol>")
            continue
        # paragraph: collect until blank line or start of a list/table
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^([-*]\s+|\d+\.\s+|\|)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline_md(' '.join(para))}</p>")
    return "\n".join(out)


def parse_answer_box(body: str) -> tuple[str, str]:
    lines = body.split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    quote_lines = []
    while i < len(lines) and lines[i].strip().startswith(">"):
        quote_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
        i += 1
    if not quote_lines:
        raise BuildError("No direct-answer blockquote found at the start of the body")
    answer = inline_md(" ".join(quote_lines))
    rest = "\n".join(lines[i:])
    return answer, rest


def split_by_marker(body: str, marker: str) -> list[tuple[str, str]]:
    """Split into (heading_text, content) chunks on a single heading level (## or ###),
    without descending into deeper heading levels — those stay as literal text in
    `content` for the caller to split again if it wants nesting."""
    pattern = re.compile(rf"^{re.escape(marker)}\s+(.+)$", re.M)
    matches = list(pattern.finditer(body))
    sections = []
    for idx, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        sections.append((heading, body[start:end]))
    return sections


def split_sections(body: str) -> list[tuple[str, str]]:
    """Split into (heading_text, content) chunks on top-level ## markdown headings only.
    Any ### subheadings inside stay as literal text in `content`."""
    return split_by_marker(body, "##")


def render_faqs(faq_content: str) -> tuple[str, list[tuple[str, str]]]:
    qa_pattern = re.compile(r"^###\s+(.+?)\s*$", re.M)
    matches = list(qa_pattern.finditer(faq_content))
    if len(matches) < 3:
        raise BuildError(f"FAQ section has only {len(matches)} questions (need at least 3)")
    pairs = []
    for idx, m in enumerate(matches):
        q = html.escape(m.group(1).strip(), quote=False)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(faq_content)
        answer_raw = " ".join(l.strip() for l in faq_content[start:end].strip().split("\n") if l.strip())
        a = inline_md(answer_raw)
        if not a:
            continue
        pairs.append((q, a))
    if len(pairs) < 3:
        raise BuildError("Fewer than 3 FAQ pairs had non-empty answers")

    items = []
    for q, a in pairs:
        items.append(
            '<div class="faq-item">'
            f'<div class="faq-item-top"><h3 class="text-large strong">{q}</h3>'
            '<div class="faq-button"><div class="button-circle small">'
            '<div class="plus"><svg fill="none" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M6 2V10M2 6H10" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"/></svg></div>'
            '<div class="minus"><svg fill="none" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M2 6H10" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"/></svg></div>'
            "</div></div></div>"
            f'<div class="faq-item-bottom"><div class="faq-item-text-wrapper"><p class="text-medium">{a}</p></div></div>'
            "</div>"
        )
    html_out = (
        '<section class="article-faq-section"><h2>FAQs</h2>'
        '<div class="faq-list" data-gsap-scroll="stagger">' + "".join(items) + "</div></section>"
    )
    # Un-escape for JSON-LD (schema wants plain text, not HTML-escaped)
    plain_pairs = [(html.unescape(q), html.unescape(re.sub(r"<[^>]+>", "", a))) for q, a in pairs]
    return html_out, plain_pairs


def render_body(fm: dict, body: str) -> tuple[str, list[tuple[str, str]]]:
    answer, rest = parse_answer_box(body)
    sections = split_sections(rest)
    if not sections:
        raise BuildError("No ## sections found after the direct-answer blockquote")

    pillar = fm["pillar"]
    ctas = CTA_MAP[pillar]

    parts = [f'<section><div class="answer-box"><strong>Quick answer:</strong> {answer}</div></section>']

    faq_html = None
    faq_pairs: list[tuple[str, str]] = []
    body_h2_count = 0
    for heading, content in sections:
        if heading.strip().lower() == "faqs":
            faq_html, faq_pairs = render_faqs(content)
            continue
        if heading.strip().lower() == "key takeaways":
            parts.append(f"<section><h2>{inline_md(heading)}</h2>{render_blocks(content)}</section>")
            continue

        body_h2_count += 1
        # A ## section's content may contain ### subheadings — render those nested.
        sub_sections = split_by_marker(content, "###")
        pre_content = content[: content.find("###")] if "###" in content else content
        section_html = [f"<h2>{inline_md(heading)}</h2>", render_blocks(pre_content)]
        for sub_heading, sub_content in sub_sections:
            section_html.append(f"<h3>{inline_md(sub_heading)}</h3>{render_blocks(sub_content)}")
        parts.append("<section>" + "".join(section_html) + "</section>")

        if body_h2_count == 2 and ctas:
            h, p, label, href, external = ctas[0]
            target = ' target="_blank" rel="noopener"' if external else ""
            parts.append(
                f'<div class="cta-box"><h2>{inline_md(h)}</h2><p>{inline_md(p)}</p>'
                f'<a href="{href}"{target}>{html.escape(label, quote=False)}</a></div>'
            )

    if faq_html is None:
        raise BuildError("No ## FAQs section found")
    parts.append(faq_html)

    if ctas:
        h, p, label, href, external = ctas[-1]
        target = ' target="_blank" rel="noopener"' if external else ""
        parts.append(
            f'<div class="cta-box"><h2>{inline_md(h)}</h2><p>{inline_md(p)}</p>'
            f'<a href="{href}"{target}>{html.escape(label, quote=False)}</a></div>'
        )

    return "\n".join(parts), faq_pairs


# --------------------------------------------------------------------------------
# Page assembly (reuses the live template's boilerplate, extracted at build time
# so it can never drift from the real site chrome).
# --------------------------------------------------------------------------------

def extract_boilerplate() -> tuple[str, str, str]:
    text = TEMPLATE_SOURCE.read_text()
    style_m = re.search(r"(  <style>\n.*?\n  </style>\n)", text, re.S)
    nav_m = re.search(r"(<body>\n.*?<div class=\"navigation-overlay\"></div></div>\n)", text, re.S)
    footer_m = re.search(r"(  <footer class=\"footer\">.*?</html>\n?)$", text, re.S)
    if not (style_m and nav_m and footer_m):
        raise BuildError("Could not locate boilerplate blocks in template source — template may have changed")
    return style_m.group(1), nav_m.group(1), footer_m.group(1)


def related_cards(pillar: str, exclude_href: str) -> str:
    pool = [c for c in RELATED_POOL[pillar] if c[0] != exclude_href]
    chosen = pool[:3] if len(pool) <= 3 else [pool[i] for i in sorted(
        {zlib.crc32((exclude_href + str(i)).encode()) % len(pool) for i in range(6)}
    )[:3]]
    if len(chosen) < 3:
        chosen = pool[:3]
    return "\n            ".join(
        f'<a class="article-card w-inline-block" href="{href}"><img src="{img}" alt="{alt}">'
        f'<div class="article-card-content"><div class="caption blue-caption">{tag}</div>'
        f"<h3 class=\"heading-h5\">{title}</h3></div></a>"
        for href, img, alt, tag, title in chosen
    )


def human_date(iso_date: str) -> str:
    y, mo, d = iso_date.split("-")
    return f"{DATE_MONTHS[int(mo) - 1]} {int(d)}, {y}"


def build_page(fm: dict, body_html: str, faq_pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    pillar = fm["pillar"]
    slug = fm["slug"]
    is_root = pillar == "StudyInMalta"
    dest_rel = f"{slug}.html" if is_root else f"blog/{slug}.html"
    canonical = f"https://outreachrecruitment.net/{slug}" if is_root else f"https://outreachrecruitment.net/blog/{slug}"
    back_href = "/study-in-malta" if is_root else "/blog/"
    back_text = "Back to Study in Malta" if is_root else "Back to Blog"

    img_path, img_alt = pick(IMAGE_POOL[pillar], slug)
    tag = TAG_MAP[pillar]
    title = html.escape(fm["title"], quote=False)
    seo_title = html.escape(fm["seo_title"], quote=False)
    meta_desc = html.escape(fm["meta_description"], quote=False)
    og_image_abs = f"https://outreachrecruitment.net{img_path}"

    org_id = "https://outreachrecruitment.net/#organization"
    if is_root:
        breadcrumb = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://outreachrecruitment.net/"},
            {"@type": "ListItem", "position": 2, "name": "Study in Malta", "item": "https://outreachrecruitment.net/study-in-malta"},
            {"@type": "ListItem", "position": 3, "name": fm["title"], "item": canonical},
        ]
    else:
        breadcrumb = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://outreachrecruitment.net/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://outreachrecruitment.net/blog/"},
            {"@type": "ListItem", "position": 3, "name": fm["title"], "item": canonical},
        ]
    graph = [
        {"@type": "Organization", "@id": org_id, "name": "Outreach Recruitment Ltd",
         "url": "https://outreachrecruitment.net/",
         "logo": {"@type": "ImageObject", "url": "https://outreachrecruitment.net/assets/outreach-recruitment-logo.svg"}},
        {"@type": "BlogPosting", "@id": f"{canonical}#article", "headline": fm["title"],
         "description": fm["meta_description"], "url": canonical,
         "image": {"@type": "ImageObject", "url": og_image_abs, "width": 1200, "height": 630},
         "datePublished": f"{fm['date']}T00:00:00Z", "dateModified": f"{fm['date']}T00:00:00Z",
         "author": {"@id": org_id}, "publisher": {"@id": org_id}, "inLanguage": "en",
         "keywords": fm["primary_keyword"], "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}},
        {"@type": "BreadcrumbList", "itemListElement": breadcrumb},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq_pairs
        ]},
    ]
    # Escape "</" so a stray "</script" anywhere in model-derived text (e.g. a title
    # or FAQ answer) can never break out of the surrounding HTML <script> element.
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    schema = schema.replace("</", "<\\/")

    style_block, nav_block, footer_block = extract_boilerplate()
    related = related_cards(pillar, f"/{dest_rel}" if is_root else f"/{dest_rel}")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>{seo_title}</title>
  <meta name="description" content="{meta_desc}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{meta_desc}"/>
  <meta property="og:image" content="{og_image_abs}"/>
  <meta property="og:image:width" content="1200"/>
  <meta property="og:image:height" content="630"/>
  <meta property="og:image:type" content="image/png"/>
  <meta property="og:image:alt" content="{html.escape(img_alt, quote=False)}"/>
  <meta property="og:type" content="article"/>
  <meta property="og:url" content="{canonical}"/>
  <meta property="og:site_name" content="Outreach Recruitment Agency"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="{title}"/>
  <meta name="twitter:description" content="{meta_desc}"/>
  <meta name="twitter:image" content="{og_image_abs}"/>
  <link rel="canonical" href="{canonical}"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <link rel="preconnect" href="https://cdn.prod.website-files.com" crossorigin/>
  <link rel="dns-prefetch" href="https://cdn.prod.website-files.com"/>
  <link crossorigin="anonymous" href="https://cdn.prod.website-files.com/6996b31b0e199fa8510adf4f/css/people-work-webflow-108-template.webflow.shared.6c8c6beff.css" integrity="sha384-bIxr7/VAGMc1npTdLY7+pxf0nBYi2449/GvW5FYUfyx/ZQEFNpXpICDcC/gSarqa" rel="stylesheet" type="text/css"/>
  <link href="/assets/brand-overrides.css" rel="stylesheet" type="text/css"/>
  <link href="/assets/job-card-logo.jpg" rel="icon" type="image/jpeg"/>
  <link href="/assets/job-card-logo.jpg" rel="apple-touch-icon"/>
{style_block}  <script type="application/ld+json">
  {schema}
  </script>
</head>
{nav_block}
  <main class="main">
    <section class="section page-header">
      <div class="w-layout-blockcontainer container w-container">
        <div class="w-layout-vflex section-content">
          <div class="w-layout-vflex text center" data-gsap-scroll="text">
            <a href="{back_href}" style="display:inline-flex;align-items:center;gap:0.35rem;font-size:0.85rem;color:#442DFA;text-decoration:none;margin-bottom:0.9rem;font-weight:600;">&larr; {back_text}</a>
            <div class="tag darker">{tag}</div>
            <h1 class="heading-h1">{title}</h1>
            <div class="caption blue-caption">{human_date(fm['date'])}</div>
          </div>
          <div class="cms-featured-media" data-gsap-scroll="fade"><img src="{img_path}" alt="{html.escape(img_alt, quote=False)}" class="media-fill" loading="lazy" sizes="100vw" srcset="{img_path}"/></div>
        </div>
      </div>
    </section>
    <section class="section padding-top-extra-small">
      <div class="w-layout-blockcontainer container tight w-container">
        <article class="cms-article">
          <div class="w-richtext">
{body_html}
          </div>
        </article>
        <section>
          <h2 class="heading-h3">Read more</h2>
          <div class="related-grid">
            {related}
          </div>
        </section>
      </div>
    </section>
  </main>
{footer_block}"""

    meta = {
        "dest_rel": dest_rel, "canonical": canonical, "pillar": pillar, "slug": slug,
        "title": fm["title"], "tag": tag, "img_path": img_path, "img_alt": img_alt,
        "date_human": human_date(fm["date"]), "date_iso": fm["date"], "is_root": is_root,
    }
    return page, meta


# --------------------------------------------------------------------------------
# Validation — objective build correctness only, not content review.
# --------------------------------------------------------------------------------

def validate_page(page: str) -> list[str]:
    problems = []
    for tag in ("html", "head", "body", "main", "article", "section", "footer"):
        opens = len(re.findall(rf"<{tag}[ >]", page))
        closes = len(re.findall(rf"</{tag}>", page))
        if opens != closes:
            problems.append(f"<{tag}> unbalanced: {opens} open vs {closes} close")

    m = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', page, re.S)
    if not m:
        problems.append("JSON-LD script block missing")
    else:
        try:
            json.loads(m.group(1))
        except json.JSONDecodeError as exc:
            problems.append(f"JSON-LD does not parse: {exc}")

    for ref in set(re.findall(r'(?:src|href)="(/[^"]+)"', page)):
        path = ref.split("#")[0].split("?")[0]
        if path in ("/", ""):
            continue
        candidate = ROOT / path.lstrip("/")
        if candidate.exists() or candidate.with_suffix(".html").exists() or (candidate / "index.html").exists():
            continue
        problems.append(f"broken local reference: {ref}")

    return problems


# --------------------------------------------------------------------------------
# blog/index.html + sitemap updates (idempotent — skip if href/loc already present)
# --------------------------------------------------------------------------------

def card_html(dest_rel: str, meta: dict, read_time: str) -> str:
    href = f"/{dest_rel}"
    return (
        f'<article class="article-card w-dyn-item" data-blog-subcategory="{meta["slug"]}" role="listitem">'
        f'<a class="card-link w-inline-block" href="{href}"></a>'
        '<div class="article-card-media"><div class="article-card-overlay"></div>'
        f'<div class="article-card-button"><a class="button-primary animated w-inline-block" href="{href}">'
        '<div class="button-label" data-figma-id="12018:4671">Read article</div>'
        '<div class="button-rail"><div class="button-circle small accent"><div class="icon small w-embed">'
        '<svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--_⚡️-icons---icon-stroke)"></path></svg>'
        '</div></div></div><div class="icon-button"><div class="icon small w-embed"><svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--_⚡️-icons---icon-stroke)"></path></svg></div></div></a></div>'
        f'<img alt="{html.escape(meta["img_alt"], quote=False)}" class="media-fill" loading="lazy" src="{meta["img_path"]}"/></div>'
        f'<div class="w-layout-vflex stack gap-04"><div class="tag darker">{meta["tag"]}</div>'
        f'<h3 class="heading-h6 capitalize">{html.escape(meta["title"], quote=False)}</h3>'
        f'<div class="text-small" style="color:#888;font-size:0.78rem;">{meta["date_human"]} &middot; {read_time}</div></div></article>'
    )


def update_blog_index(meta: dict) -> bool:
    if meta["pillar"] not in BLOG_INDEX_SECTION:
        return False
    href = f"/{meta['dest_rel']}"
    html_text = BLOG_INDEX.read_text()
    if href in html_text:
        return False  # already present, idempotent no-op
    section = BLOG_INDEX_SECTION[meta["pillar"]]
    marker = f'data-blog-section="{section}"'
    idx = html_text.index(marker)
    grid_marker = '<div class="articles-grid w-dyn-items" data-gsap-scroll="stagger" role="list">'
    grid_idx = html_text.index(grid_marker, idx) + len(grid_marker)
    card = card_html(meta["dest_rel"], meta, "4 min read")
    html_text = html_text[:grid_idx] + card + html_text[grid_idx:]
    BLOG_INDEX.write_text(html_text)
    return True


def update_sitemap(meta: dict) -> bool:
    sitemap = SITEMAP_PAGES if meta["is_root"] else SITEMAP_BLOG
    text = sitemap.read_text()
    if meta["canonical"] in text:
        return False
    entry = (
        "  <url>\n"
        f"    <loc>{meta['canonical']}</loc>\n"
        f"    <lastmod>{meta['date_iso']}</lastmod>\n"
        "    <changefreq>monthly</changefreq>\n"
        "    <priority>0.7</priority>\n"
        "  </url>\n"
    )
    if "\n</urlset>" in text:
        text = text.replace("\n</urlset>", f"\n{entry}\n</urlset>", 1)
    else:
        text = text.replace("</urlset>", f"{entry}</urlset>", 1)
    sitemap.write_text(text)
    return True


# --------------------------------------------------------------------------------

def publish_one(md_path: Path) -> dict:
    """Returns {"ok": True, "dest_rel": ..., "canonical": ...} or {"ok": False, "error": ...}."""
    try:
        raw = md_path.read_text()
        fm, body = parse_frontmatter(raw)
        body_html, faq_pairs = render_body(fm, body)
        page, meta = build_page(fm, body_html, faq_pairs)
        problems = validate_page(page)
        if problems:
            raise BuildError("validation failed: " + "; ".join(problems))
        dest = ROOT / meta["dest_rel"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page)
        touched = [meta["dest_rel"]]
        if update_blog_index(meta):
            touched.append("blog/index.html")
        sitemap_rel = "sitemaps/sitemap-pages.xml" if meta["is_root"] else "sitemaps/sitemap-blog.xml"
        if update_sitemap(meta):
            touched.append(sitemap_rel)
        return {"ok": True, "dest_rel": meta["dest_rel"], "canonical": meta["canonical"],
                "source": str(md_path), "touched": touched}
    except BuildError as exc:
        return {"ok": False, "error": str(exc), "source": str(md_path)}
    except Exception as exc:  # noqa: BLE001 - unattended pipeline, never crash the batch
        return {"ok": False, "error": f"unexpected error: {exc}", "source": str(md_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("day_dir", help="Directory of generated .md drafts for one day")
    args = parser.parse_args()
    day_dir = Path(args.day_dir)
    if not day_dir.is_dir():
        raise SystemExit(f"Not a directory: {day_dir}")

    results = [publish_one(p) for p in sorted(day_dir.glob("*.md"))]
    ok = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]

    for r in ok:
        print(f"PUBLISHED {r['dest_rel']} -> {r['canonical']}")
    for r in failed:
        print(f"SKIPPED (left as draft) {r['source']}: {r['error']}", file=sys.stderr)

    touched_paths = sorted({p for r in ok for p in r["touched"]})
    # Machine-readable summary line for the workflow to parse — always the last
    # line of stdout so `tail -1` picks it up regardless of what's printed above.
    print(json.dumps({
        "published": len(ok),
        "skipped": len(failed),
        "touched_paths": touched_paths,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
