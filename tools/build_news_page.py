#!/usr/bin/env python3
"""
build_news_page.py — build /news-updates ("News & Updates") from the site's articles.

Layout follows the "featured articles / trending / latest + sidebar / newsletter / popular by category"
magazine idea, inside the site's own header and footer (about.html is the shell).

Articles come from blog/*.html (English only) plus the Study in Malta guide pages listed in STUDY_PAGES.
Each article gets one or more of the three main categories: Study in Malta, Employers, Candidates.
Re-run after adding articles:  python3 tools/build_news_page.py

Settings live in tools/news_page.json (ad slots, "ready" flag). While "ready" is false the page is noindex.
"""
from __future__ import annotations

import html
import json
import math
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://outreachrecruitment.net"
URL = f"{SITE}/news-updates"
OUT = ROOT / "news-updates.html"
SETTINGS = ROOT / "tools" / "news_page.json"
CATS = ["Study in Malta", "Employers", "Candidates"]
CAT_SLUG = {"Study in Malta": "study-in-malta", "Employers": "employers", "Candidates": "candidates"}
PER_PAGE = 6
E = lambda s: html.escape(str(s or ""), quote=True)

# Study in Malta guide pages that are not in blog/ but belong in the Study category.
STUDY_PAGES = ["study-in-malta-complete-guide", "study-in-malta-from-india", "study-in-malta-from-morocco", "malta-study-guide"]


def categories(tag: str) -> list[str]:
    t = tag.lower()
    if "study" in t or "application guide" in t:
        return ["Study in Malta"]
    if t in ("employers", "culture", "decision making", "team structure"):
        return ["Employers"]
    if "candidates" in t and "employers" in t:
        return ["Candidates", "Employers"]
    return ["Candidates"]


def parse_date(s: str) -> datetime:
    for fmt in ("%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.strip().replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime(2026, 1, 1)


def meta_content(b: BeautifulSoup, **attrs) -> str:
    m = b.find("meta", attrs=attrs)
    return (m.get("content") or "").strip() if m else ""


def clean_desc(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= 160 else s[:157].rsplit(" ", 1)[0] + "…"


def blog_articles() -> list[dict]:
    out = []
    for p in sorted((ROOT / "blog").glob("*.html")):
        if p.name == "index.html":
            continue
        b = BeautifulSoup(p.read_text(encoding="utf-8"), "html.parser")
        if (b.html.get("lang") or "en")[:2] != "en" or not b.select_one(".od-section"):
            continue
        spans = [s.get_text(strip=True) for s in b.select(".od-meta span")]
        img = b.select_one(".od-image img")
        canon = b.find("link", rel="canonical")
        tag = b.select_one(".od-tag").get_text(strip=True)
        body = b.select_one("#odBody") or b.select_one(".od-rich")
        words = len(body.get_text(" ").split()) if body else 800
        mins = next((int(re.match(r"\d+", s).group()) for s in spans if "min" in s and re.match(r"\d+", s)), max(1, math.ceil(words / 200)))
        out.append({
            "slug": p.stem,
            "title": b.select_one(".od-title").get_text(" ", strip=True),
            "url": canon["href"].replace(SITE, "") if canon else f"/{p.stem}/",
            "img": img["src"] if img else "",
            "alt": (img.get("alt") if img else "") or "",
            "date": parse_date(spans[1] if len(spans) > 1 else ""),
            "desc": clean_desc(meta_content(b, name="description")),
            "mins": mins,
            "cats": categories(tag),
            "author": meta_content(b, name="author"),
        })
    return out


def study_pages(known_titles: set[str]) -> list[dict]:
    out = []
    for slug in STUDY_PAGES:
        p = ROOT / slug / "index.html"
        if not p.exists():
            p = ROOT / f"{slug}.html"
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf-8")
        b = BeautifulSoup(raw, "html.parser")
        title = (meta_content(b, property="og:title") or (b.title.get_text() if b.title else slug))
        title = re.split(r"\s+[—|]\s+", title)[0].strip()
        if title in known_titles:
            continue
        img = meta_content(b, property="og:image").replace(SITE, "")
        if not img:
            first = b.select_one("main img[src]")
            img = first["src"] if first else "/assets/studyinmaltaa.png"
        dp = re.search(r'"datePublished"\s*:\s*"([^"]+)"', raw)
        words = len((b.find("main") or b).get_text(" ").split())
        out.append({"slug": slug, "title": title, "url": f"/{slug}", "img": img, "alt": title,
                    "date": parse_date(dp.group(1)) if dp else datetime(2026, 6, 10),
                    "desc": clean_desc(meta_content(b, name="description") or meta_content(b, property="og:description")),
                    "mins": max(1, math.ceil(words / 220)), "cats": ["Study in Malta"]})
    return out


def fmt(d: datetime) -> str:
    return d.strftime("%b %-d, %Y")


TEAM = json.loads((ROOT / "tools" / "team_data.json").read_text(encoding="utf-8"))
TEAM_BY_NAME = {p["name"].lower(): p for p in [TEAM["ceo"]] + TEAM["members"]}


def by(a: dict) -> str:
    """Small author avatar + name for articles written by a team member."""
    p = TEAM_BY_NAME.get((a.get("author") or "").lower())
    if not p:
        return ""
    return (f'<span class="nu-by"><img src="{E(p["photo"])}" alt="" width="22" height="22" '
            f'style="object-position:{E(p.get("photo_position", "center 30%"))}">{E(p["name"])}</span>')


def badge(a: dict) -> str:
    return f'<span class="nu-badge">{E(a["cats"][0])}</span>'


def card(a: dict, extra: str = "") -> str:
    cats = " ".join(CAT_SLUG[c] for c in a["cats"])
    search = E((a["title"] + " " + a["desc"] + " " + " ".join(a["cats"])).lower())
    return f"""<article class="nu-card{extra}" data-cats="{cats}" data-search="{search}">
  <a class="nu-card-img" href="{E(a['url'])}" tabindex="-1" aria-hidden="true"><img src="{E(a['img'])}" alt="{E(a['title'])}" loading="lazy" width="390" height="200"></a>
  <div class="nu-meta">{badge(a)}<time datetime="{a['date']:%Y-%m-%d}">{fmt(a['date'])}</time>{by(a)}</div>
  <h3 class="nu-card-title"><a href="{E(a['url'])}">{E(a['title'])}</a></h3>
  <p class="nu-card-text">{E(a['desc'])}</p>
</article>"""


ICONS = {
    "LinkedIn": ("https://www.linkedin.com/company/outreach-recruitment-agency/", '<path d="M6.94 8.5H3.56V20h3.38V8.5ZM5.25 3A1.97 1.97 0 1 0 5.3 7a1.97 1.97 0 0 0-.05-4ZM20.44 13.4c0-3.1-1.65-5.15-4.4-5.15a3.83 3.83 0 0 0-3.44 1.9V8.5H9.37c.04.93 0 11.5 0 11.5h3.23v-6.42c0-.34.03-.69.13-.93.28-.69.9-1.4 1.95-1.4 1.38 0 1.93 1.05 1.93 2.6V20h3.23z" fill="currentColor"/>'),
    "Facebook": ("https://www.facebook.com/outreachrecruit/", '<path d="M14 8.5V6.8c0-.8.5-1 1-1h2V2.5h-2.8C11.1 2.5 10.5 4.8 10.5 6.3v2.2H8.5V12h2v9.5H14V12h2.6l.4-3.5z" fill="currentColor"/>'),
    "Instagram": ("https://www.instagram.com/outreachrecruitment_agency", '<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/>'),
    "TikTok": ("https://www.tiktok.com/@outreachrecruitment", '<path d="M16.6 3c.4 2.2 1.9 3.7 4.1 3.9v3.2a7.4 7.4 0 0 1-4-1.3v6.3a5.9 5.9 0 1 1-5.9-5.9c.3 0 .7 0 1 .1v3.3a2.7 2.7 0 1 0 1.8 2.5V3z" fill="currentColor"/>'),
    "YouTube": ("https://www.youtube.com/@outreachrecruitmentagency", '<path d="M21.6 7.2a2.6 2.6 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.6 2.6 0 0 0 2.4 7.2 27 27 0 0 0 2 12a27 27 0 0 0 .4 4.8 2.6 2.6 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.6 2.6 0 0 0 1.8-1.8A27 27 0 0 0 22 12a27 27 0 0 0-.4-4.8ZM10 15V9l5.2 3z" fill="currentColor"/>'),
    "X": ("https://x.com/OutreachRecrt", '<path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.3l4.4 5.8zm-1.1 16.2h1.7L7.4 4.7H5.6z" fill="currentColor"/>'),
}


JOBS_BANNERS: dict[str, str] = {}


def open_jobs() -> list[dict]:
    reg = json.loads((ROOT / "tools" / "jobs_registry.json").read_text(encoding="utf-8"))
    jobs = [j for j in reg if j.get("status") not in ("closed", "expired")]
    jobs.sort(key=lambda j: (not j.get("featured"), j.get("date", "")), reverse=False)
    jobs.sort(key=lambda j: j.get("date", ""), reverse=True)
    return jobs


def jobs_banner(kind: str, jobs: list[dict], reverse: bool = False) -> str:
    """Animated house banner promoting /jobs/: open-jobs count + scrolling job titles + button."""
    seen, chips = set(), []
    for j in jobs:
        t = re.sub(r"\s*\(.*?\)", "", j["title"]).strip()
        if t.lower() not in seen:
            seen.add(t.lower()); chips.append(t)
        if len(chips) == 14:
            break
    if reverse:
        chips = chips[::-1]
    row = "".join(f"<span>{E(c)}</span>" for c in chips)
    count = len(jobs)
    return f"""<a class="nu-jobs nu-jobs-{kind}" href="/jobs/" aria-label="View {count} open jobs in Malta">
  <div class="nu-jobs-text"><span class="nu-jobs-count"><b data-count="{count}">{count}</b> open jobs</span><strong>Find your next job in Malta</strong></div>
  <div class="nu-jobs-ticker" aria-hidden="true"><div class="nu-jobs-track{' rev' if reverse else ''}">{row}{row}</div></div>
  <span class="nu-btn accent nu-jobs-btn">View jobs{ARROW}</span>
</a>"""


def ad(slot: dict, size: str, cls: str) -> str:
    """An ad slot: a real banner when image+link are set in tools/news_page.json, otherwise the placeholder."""
    if slot.get("image") and slot.get("link"):
        return (f'<a class="nu-ad {cls} has-banner" href="{E(slot["link"])}"><img src="{E(slot["image"])}" '
                f'alt="{E(slot.get("alt", "Advertisement"))}" loading="lazy"></a>')
    return JOBS_BANNERS[cls]


CSS = """<style id="news-page-style">
/* Header stays fixed and visible (the theme hides it while scrolling) */
.navigation.w-nav { position: fixed !important; top: 0 !important; left: 0; right: 0; z-index: 1000;
  transform: none !important; translate: none !important; opacity: 1 !important;
  background: #fff !important; padding-top: 0 !important; box-shadow: 0 1px 0 #ececec; }
body { background: #fff; }
.nu { --ink: #1c2623; --muted: rgba(28, 38, 35, .64); --serif: var(--_🅰-typography---font-family--heading, "Libre Caslon Condensed", "Times New Roman", serif); --line: #e9e9e9; --soft: #f5f5f5; --brand: #442DFA;
  font-family: var(--_🅰-typography---font-family--body, "BDO Grotesk", Arial, sans-serif); color: var(--ink);
  padding: 9.5rem 0 5rem; background: #fff; }
.nu-wrap { width: min(1240px, 100% - 32px); margin: 0 auto; }
.nu h1, .nu h2, .nu h3 { font-family: var(--serif); font-weight: 400 !important; color: var(--ink); letter-spacing: -.5px; line-height: 1.08; margin: 0; }
.nu a { color: inherit; text-decoration: none; }
.nu-btn { display: inline-flex; align-items: center; justify-content: space-between; gap: .9rem; height: 56px; padding: 0 8px 0 22px;
  border-radius: 20px; border: 0; font-family: inherit; font-weight: 600; font-size: 1rem; line-height: 1; cursor: pointer; white-space: nowrap;
  text-decoration: none; transition: background .25s ease, color .25s ease; }
.nu-arrow { display: grid; place-items: center; flex: none; width: 40px; height: 40px; border-radius: 16px; background: var(--brand); color: #fff; overflow: hidden; }
.nu-arrow svg { width: 18px; height: 18px; }
.nu-arrow.back { transform: scaleX(-1); }
#nu-prev { padding: 0 22px 0 8px; }
.nu-btn:hover .nu-arrow svg { animation: nu-arrow .5s ease; }
@keyframes nu-arrow { 0% { transform: none; } 45% { transform: translateX(150%); } 46% { transform: translateX(-150%); } 100% { transform: none; } }
.nu-btn.light { background: #ECEAE1; color: #2c2d2d !important; }
.nu-btn.light:hover { background: #e1ddd0; }
.nu-btn.accent { background: var(--brand); color: #fff !important; }
.nu-btn.accent .nu-arrow { background: #fff; color: var(--brand); }
.nu-btn.accent:hover { background: #3420d9; }
.nu-badge { display: inline-flex; align-items: center; padding: .5rem .75rem; border-radius: 200px; background: var(--brand);
  font-size: .75rem; line-height: 1; font-weight: 600; letter-spacing: 1.25px; text-transform: uppercase; color: #fff; white-space: nowrap; }
.nu-meta { display: flex; align-items: center; gap: .6rem; color: var(--muted); font-size: .9rem; font-weight: 500; flex-wrap: wrap; }
/* Title row */
.nu-head { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.nu-head h1 { font-size: clamp(2.75rem, 5vw, 4.25rem); }
.nu-head-btns { display: flex; gap: .9rem; flex-wrap: wrap; }
.nu-intro { max-width: 760px; margin: 0 0 1.75rem; color: var(--muted); font-size: 1.05rem; line-height: 1.7; }
.nu-intro a { color: var(--ink); text-decoration: underline; text-decoration-color: rgba(68,45,250,.4); text-underline-offset: 3px; }
.nu-intro a:hover { color: var(--brand); }
.nu-chips { display: flex; gap: .6rem; flex-wrap: wrap; margin: 0 0 2.25rem; padding: 0; list-style: none; }
.nu-chip { display: inline-flex; padding: .55rem 1.05rem; border-radius: 999px; background: var(--soft); font-weight: 600; font-size: .95rem;
  border: 0; cursor: pointer; font-family: inherit; color: var(--ink); transition: background .2s ease, color .2s ease; }
.nu-chip:hover { background: #e6e6e6; }
.nu-chip.is-active { background: var(--brand); color: #fff; }
/* Featured */
.nu-featured { position: relative; display: flex; align-items: center; min-height: 460px; overflow: hidden; background: #222; isolation: isolate; }
.nu-featured img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .8s ease; }
.nu-featured::before { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(90deg, rgba(10,10,10,.82) 0%, rgba(10,10,10,.55) 45%, rgba(10,10,10,.08) 100%); }
.nu-featured:hover img { transform: scale(1.03); }
.nu-featured-body { padding: clamp(1.75rem, 5vw, 4.5rem); max-width: 620px; color: #fff; display: flex; flex-direction: column; gap: 1rem; }
.nu-featured .nu-meta { color: #fff; }
.nu-featured h2 { color: #fff; font-size: clamp(2rem, 3.6vw, 2.9rem); }
.nu-featured p { margin: 0; color: rgba(255,255,255,.88); line-height: 1.65; }
.nu-author { display: flex; align-items: center; gap: .6rem; font-weight: 600; }
.nu-author span { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; background: #fff; }
.nu-author img { position: static !important; width: 22px !important; height: auto !important; z-index: 0 !important; transform: none !important; }
/* Trending */
.nu .nu-label { display: flex; align-items: center; gap: 2rem; margin: 3rem 0 2rem; font-family: inherit; font-weight: 700 !important; font-size: 1.15rem; letter-spacing: 0; }
.nu-label::after { content: ""; flex: 1; height: 1px; background: var(--line); }
.nu-trend { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2.25rem; }
.nu-hcard { display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 1.75rem; align-items: center; }
.nu-hcard-img { display: block; aspect-ratio: 11 / 10; overflow: hidden; background: var(--soft); }
.nu-hcard-img img, .nu-card-img img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s ease; }
.nu-hcard:hover img, .nu-card:hover .nu-card-img img { transform: scale(1.05); }
.nu-hcard h3 { font-size: 1.6rem; margin-bottom: .6rem; }
.nu-hcard p { margin: 0 0 .9rem; color: var(--muted); line-height: 1.65; }
.nu-by { display: inline-flex; align-items: center; gap: .4rem; color: var(--ink); font-weight: 600; }
.nu-by img { width: 22px; height: 22px; border-radius: 50%; object-fit: cover; }
.nu-dot { width: 4px; height: 4px; border-radius: 50%; background: #b5b5b5; }
/* Ads */
.nu-ad { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .35rem; background: #121212;
  color: #fff; text-transform: uppercase; letter-spacing: .08em; overflow: hidden; isolation: isolate; }
.nu-ad::before { content: ""; position: absolute; inset: 0; z-index: -1; opacity: .5;
  background: linear-gradient(to top right, transparent calc(50% - .5px), #3a3a3a, transparent calc(50% + .5px)),
              linear-gradient(to bottom right, transparent calc(50% - .5px), #3a3a3a, transparent calc(50% + .5px)); }
.nu-ad span { font-size: 1.2rem; font-weight: 500; background: #121212; padding: 0 1.5rem; }
.nu-ad small { font-size: .8rem; background: #121212; padding: 0 1rem; }
.nu-ad-wide { min-height: 152px; margin: 5rem 0; }
.nu-ad-box { aspect-ratio: 1; width: 100%; }
.nu-ad.has-banner::before { display: none; }
.nu-ad.has-banner img { width: 100%; height: 100%; object-fit: cover; display: block; }
/* Animated jobs banners */
.nu-jobs { position: relative; display: grid; align-items: center; gap: 1.5rem 2rem; overflow: hidden; isolation: isolate; color: #fff !important;
  background: linear-gradient(120deg, #2a17c9, #442DFA 45%, #6b55ff); text-decoration: none; }
.nu-jobs::before { content: ""; position: absolute; inset: -40% -10%; z-index: -1; opacity: .35;
  background: radial-gradient(closest-side, rgba(255,255,255,.55), transparent 70%) 0 0 / 40% 120% no-repeat; animation: nu-sheen 7s ease-in-out infinite; }
@keyframes nu-sheen { 0% { background-position: -40% 50%; } 50% { background-position: 140% 50%; } 100% { background-position: -40% 50%; } }
.nu-jobs-wide { grid-template-columns: auto minmax(0, 1fr) auto; min-height: 152px; padding: 1.5rem 2rem; margin: 5rem 0; border-radius: 24px; }
.nu-jobs-box { grid-template-columns: minmax(0, 1fr); gap: 1.25rem; padding: 1.75rem 1.5rem; border-radius: 24px; }
.nu-jobs-text { display: flex; flex-direction: column; gap: .35rem; }
.nu-jobs strong, .nu-jobs-count, .nu-jobs-count b { color: #fff !important; }
.nu-jobs-count { font-size: .8rem; font-weight: 600; letter-spacing: 1.25px; text-transform: uppercase; opacity: .9; }
.nu-jobs-count b { font-size: 1.05rem; font-variant-numeric: tabular-nums; }
.nu-jobs strong { font-family: var(--serif); font-weight: 400; font-size: clamp(1.7rem, 2.6vw, 2.3rem); line-height: 1.05; letter-spacing: -.5px; }
.nu-jobs-box strong { font-size: 2rem; }
.nu-jobs-box .nu-jobs-count b { display: block; font-family: var(--serif); font-size: 4.5rem; line-height: 1; font-weight: 400; letter-spacing: -1px; text-transform: none; }
.nu-jobs-ticker { overflow: hidden; -webkit-mask-image: linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent); mask-image: linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent); }
.nu-jobs-track { display: flex; gap: .6rem; width: max-content; animation: nu-ticker 38s linear infinite; }
.nu-jobs-track.rev { animation-direction: reverse; }
.nu-jobs:hover .nu-jobs-track { animation-play-state: paused; }
.nu-jobs-track span { padding: .5rem .9rem; border-radius: 999px; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.22); font-size: .9rem; font-weight: 500; white-space: nowrap; }
@keyframes nu-ticker { to { transform: translateX(-50%); } }
.nu-jobs-btn.nu-btn.accent { background: #fff; color: var(--brand) !important; }
.nu-jobs-btn.nu-btn.accent .nu-arrow { background: var(--brand); color: #fff; }
.nu-jobs:hover .nu-jobs-btn .nu-arrow svg { animation: nu-arrow .5s ease; }
.nu-jobs-box .nu-jobs-btn { justify-self: start; }
/* Sidebar + latest */
.nu-split { display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 0; }
.nu-side { padding-right: 3.5rem; border-right: 1px solid var(--line); }
.nu-side-inner { position: sticky; top: 120px; display: flex; flex-direction: column; gap: 2rem; }
.nu-side-logo img { height: 40px; width: auto; display: block; }
.nu-side p { margin: .9rem 0 0; color: var(--muted); line-height: 1.7; }
.nu-search { position: relative; }
.nu-search input { width: 100%; height: 58px; border: 0; border-radius: 999px; background: var(--soft); padding: 0 3.4rem 0 1.4rem; font: inherit; color: var(--ink); }
.nu-search input:focus { outline: 2px solid var(--ink); }
.nu-search svg { position: absolute; right: 1.3rem; top: 50%; translate: 0 -50%; width: 20px; height: 20px; pointer-events: none; }
.nu-follow { display: flex; flex-direction: column; align-items: flex-start; gap: .8rem; padding-bottom: 2rem; border-bottom: 1px solid var(--line); }
.nu-follow strong { font-size: 1.15rem; }
.nu-follow ul { display: flex; gap: .2rem; margin: 0; padding: 0; list-style: none; flex-wrap: wrap; }
.nu-follow a { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; transition: background .2s ease, color .2s ease, transform .3s cubic-bezier(.34,1.8,.64,1); }
.nu-follow a:hover { background: var(--ink); color: #fff; transform: translateY(-3px); }
.nu-follow svg { width: 17px; height: 17px; }
.nu-latest { padding-left: 4rem; min-width: 0; }
.nu-latest-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 2.5rem; }
.nu-latest-head h2 { font-size: clamp(2.3rem, 4vw, 3.5rem); }
.nu-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 3rem 2.25rem; }
.nu-card { display: flex; flex-direction: column; gap: 1rem; }
.nu-grid .nu-card { padding-bottom: 3rem; border-bottom: 1px solid var(--line); }
.nu-card[hidden] { display: none; }
.nu-card-img { display: block; aspect-ratio: 39 / 20; overflow: hidden; background: var(--soft); }
.nu-card-title { font-size: 1.65rem; line-height: 1.12; }
.nu-card-title a:hover, .nu-hcard h3 a:hover { text-decoration: underline; text-underline-offset: 3px; }
.nu-card-text { margin: 0; color: var(--muted); line-height: 1.65; }
.nu-empty { color: var(--muted); padding: 2rem 0; }
.nu-pager { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 3rem; }
.nu-pager [hidden] { display: none; }
.nu-pager .nu-page-info { color: var(--muted); font-weight: 500; }
/* Newsletter */
.nu-news { position: relative; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); align-items: center; background: #262626;
  color: #fff; overflow: hidden; margin: 6rem 0; min-height: 480px; scroll-margin-top: 120px; }
.nu-news-img { align-self: stretch; display: flex; align-items: center; justify-content: center; background: #262626; padding: 3rem 2.5rem; }
.nu-news-img img { width: 100%; max-width: 480px; display: block; margin: 0 auto; }
.nu-news-body { padding: 4rem 3.5rem; display: flex; flex-direction: column; gap: 1.1rem; }
.nu-news h2 { color: #fff; font-size: clamp(2.3rem, 4vw, 3.4rem); }
.nu-news p { margin: 0; color: rgba(255,255,255,.82); line-height: 1.7; }
.nu-form { display: flex; flex-direction: column; gap: 1rem; margin-top: .6rem; max-width: 560px; }
.nu-form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; }
.nu-form label { display: grid; align-content: start; gap: .4rem; color: #fff; font-size: .8rem; font-weight: 700; }
.nu-form input[type=email], .nu-form input[type=search] { width: 100%; height: 50px; box-sizing: border-box; padding: .7rem .9rem; border: 1px solid rgba(255,255,255,.2);
  border-radius: 12px; background: #fff; color: var(--ink); font: inherit; font-weight: 400; }
.nu-form input::placeholder { color: #6f6a86; opacity: 1; }
.nu-form input:focus { outline: 3px solid rgba(143,130,255,.45); border-color: #8f82ff; }
.nu-form label small { color: rgba(255,255,255,.62); font-size: .72rem; font-weight: 500; }
.nu-consent { display: flex !important; flex-direction: row; align-items: flex-start; gap: .6rem; font-size: .85rem !important; font-weight: 400 !important;
  color: rgba(255,255,255,.78) !important; line-height: 1.5; cursor: pointer; }
.nu-consent input { width: 18px; height: 18px; min-width: 18px; margin: .15rem 0 0; accent-color: #8f82ff; }
.nu-submit { align-self: flex-start; }
.nu-submit:disabled { opacity: .7; cursor: wait; }
.nu-status { min-height: 1.2em; font-size: .92rem; margin: 0; }
.nu-status.is-error { color: #ff8a8a; }
.nu-status.is-ok { color: #9ff0b5; }
.nu-check { display: flex; align-items: center; gap: .6rem; font-weight: 600; color: #fff; }
.nu-check svg { width: 20px; height: 20px; }
/* Popular by category */
.nu-pop-head { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 2.25rem; }
.nu-pop-head h2 { font-size: clamp(2.3rem, 4vw, 3.5rem); }
.nu-tabs { display: flex; gap: .7rem; flex-wrap: wrap; }
.nu-panel { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2rem; animation: nu-fade .45s ease; }
.nu-panel[hidden] { display: none; }
@keyframes nu-fade { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
.nu-center { display: flex; justify-content: center; margin-top: 2.75rem; }
/* Must-read guides */
.nu-guides { background: var(--soft); padding: 6rem 0; margin-top: 6rem; }
.nu-guides-head { text-align: center; max-width: 760px; margin: 0 auto 3rem; }
.nu-guides-head h2 { font-size: clamp(2.3rem, 4vw, 3.5rem); margin-bottom: .9rem; }
.nu-guides-head p { margin: 0; color: var(--muted); line-height: 1.7; }
.nu-guide-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2.25rem; }
.nu-guide { position: relative; display: flex; align-items: flex-end; min-height: 540px; overflow: hidden; isolation: isolate; background: #222; }
.nu-guide > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .8s ease; }
.nu-guide::before { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(10,10,10,0) 30%, rgba(10,10,10,.85) 100%); }
.nu-guide:hover > img { transform: scale(1.04); }
.nu-guide-body { padding: 3rem; color: #fff; display: flex; flex-direction: column; gap: 1rem; }
.nu-guide .nu-meta { color: #fff; }
.nu-guide h3 { color: #fff; font-size: clamp(1.9rem, 3vw, 2.6rem); }
.nu-guide-icon { position: absolute; top: 3rem; left: 3rem; display: grid; place-items: center; width: 62px; height: 62px; border-radius: 50%; background: #121212; color: #fff; }
.nu-guide-icon svg { width: 26px; height: 26px; }
/* Responsive */
@media (max-width: 991px) {
  .nu { padding-top: 8rem; }
  .nu-trend { grid-template-columns: minmax(0, 1fr); }
  .nu-split { grid-template-columns: minmax(0, 1fr); }
  .nu-side { padding: 0 0 3rem; border-right: 0; border-bottom: 1px solid var(--line); margin-bottom: 3rem; }
  .nu-side-inner { position: static; }
  .nu-side-ad { display: none; }
  .nu-latest { padding-left: 0; }
  .nu-news { grid-template-columns: minmax(0, 1fr); }
  .nu-news-img { order: 2; padding: 2.5rem 2rem; }
  .nu-news-img img { max-width: 420px; }
  .nu-follow { flex-direction: row; align-items: center; justify-content: space-between; width: 100%; border-bottom: 0; padding-bottom: 0; }
  .nu-news-body { padding: 3rem 2rem; }
  .nu-panel { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .nu-guide-grid { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 640px) {
  .nu-head-btns, .nu-head-btns .nu-btn { width: 100%; }
  .nu-head-btns .nu-btn { flex: 1; padding: 0 6px 0 16px; font-size: .95rem; }
  .nu-latest-head .nu-btn { display: none; }
  .nu-news-img img { max-width: 300px; }
  .nu-featured { min-height: 520px; align-items: flex-end; }
  .nu-featured::before { background: linear-gradient(180deg, rgba(10,10,10,.1) 0%, rgba(10,10,10,.88) 70%); }
  .nu-hcard { grid-template-columns: 120px minmax(0, 1fr); gap: 1rem; align-items: start; }
  .nu-hcard h3 { font-size: 1.3rem; }
  .nu-hcard p { display: none; }
  .nu-grid, .nu-panel { grid-template-columns: minmax(0, 1fr); }
  .nu-ad-wide { min-height: 110px; margin: 3.5rem 0; }
  .nu-jobs-wide { grid-template-columns: minmax(0, 1fr); margin: 3.5rem 0; padding: 1.75rem 1.5rem; }
  .nu-jobs-wide .nu-jobs-btn { justify-self: start; }
  .nu-form-grid { grid-template-columns: minmax(0, 1fr); }
  .nu-submit { align-self: stretch; }
  .nu-guide { min-height: 440px; }
  .nu-guide-body { padding: 1.75rem; }
  .nu-guide-icon { top: 1.75rem; left: 1.75rem; }
}
@media (prefers-reduced-motion: reduce) { .nu *, .nu *::before { transition: none !important; animation: none !important; } }
</style>"""

ARROW_RAW = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW = f'<span class="nu-arrow">{ARROW_RAW}</span>'
MAIL_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5.5h18v13H3z M3.5 6l8.5 7 8.5-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
SEARCH_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CHECK_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="#fff"/><path d="m7.5 12.3 3 3 6-6.3" fill="none" stroke="#121212" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
BOOK_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5zM4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'

SCRIPT = """<script id="news-page-script">
(function () {
  var PER = %(per)d, page = 1, cat = 'all', q = '';
  var cards = [].slice.call(document.querySelectorAll('#nu-grid .nu-card'));
  var prev = document.getElementById('nu-prev'), next = document.getElementById('nu-next'), info = document.getElementById('nu-page-info');
  var empty = document.getElementById('nu-empty'), search = document.getElementById('nu-search');
  function render(scroll) {
    var match = cards.filter(function (c) {
      return (cat === 'all' || (' ' + c.dataset.cats + ' ').indexOf(' ' + cat + ' ') > -1) && (!q || c.dataset.search.indexOf(q) > -1);
    });
    var pages = Math.max(1, Math.ceil(match.length / PER)); if (page > pages) page = pages;
    cards.forEach(function (c) { c.hidden = true; });
    match.slice((page - 1) * PER, page * PER).forEach(function (c) { c.hidden = false; });
    empty.hidden = match.length > 0;
    prev.hidden = page <= 1; next.hidden = page >= pages;
    info.textContent = match.length ? 'Page ' + page + ' of ' + pages : '';
    document.querySelectorAll('[data-filter]').forEach(function (b) { b.classList.toggle('is-active', b.dataset.filter === cat); b.setAttribute('aria-pressed', b.dataset.filter === cat); });
    if (scroll) document.getElementById('latest').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function setCat(c, scroll) {
    cat = c; page = 1; render(scroll);
    try { var u = new URL(location.href); if (c === 'all') u.searchParams.delete('category'); else u.searchParams.set('category', c); history.replaceState(null, '', u); } catch (e) {}
  }
  document.querySelectorAll('[data-filter]').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); setCat(b.dataset.filter, b.hasAttribute('data-scroll')); }); });
  prev.addEventListener('click', function () { page--; render(true); });
  next.addEventListener('click', function () { page++; render(true); });
  var t; search.addEventListener('input', function () { clearTimeout(t); t = setTimeout(function () { q = search.value.trim().toLowerCase(); page = 1; render(false); }, 150); });
  search.form && search.form.addEventListener('submit', function (e) { e.preventDefault(); q = search.value.trim().toLowerCase(); page = 1; render(true); });
  var start = new URLSearchParams(location.search).get('category');
  setCat(['study-in-malta', 'employers', 'candidates'].indexOf(start) > -1 ? start : 'all', false);
  if (start) setTimeout(function () { document.getElementById('latest').scrollIntoView({ block: 'start' }); }, 300);

  // Popular by category tabs
  var tabs = [].slice.call(document.querySelectorAll('.nu-tab'));
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { var on = t === tab; t.classList.toggle('is-active', on); t.setAttribute('aria-selected', on); document.getElementById(t.getAttribute('aria-controls')).hidden = !on; });
      document.getElementById('nu-pop-all').dataset.filter = tab.dataset.cat;
    });
  });

  // Newsletter: same list as the footer job-alert form (email + country). The list needs a name, so
  // newsletter sign-ups are stored as "Newsletter subscriber".
  var codes = %(codes)s.split(' ');
  var names = window.Intl && Intl.DisplayNames ? new Intl.DisplayNames(['en'], { type: 'region' }) : null;
  var countries = codes.map(function (c) { return [c, c === 'XK' ? 'Kosovo' : names ? names.of(c) : c]; }).sort(function (a, b) { return a[1].localeCompare(b[1]); });
  document.getElementById('nu-countries').innerHTML = countries.map(function (c) { return '<option value="' + c[1].replace(/"/g, '&quot;') + '"></option>'; }).join('');
  function countryOf(v) { v = (v || '').trim().toLowerCase(); return countries.find(function (c) { return c[1].toLowerCase() === v || c[0].toLowerCase() === v; }); }
  var form = document.getElementById('nu-form'), status = document.getElementById('nu-status'), btn = document.getElementById('nu-submit');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var match = countryOf(form.elements.country.value);
    form.elements.country.setCustomValidity(match ? '' : 'Please choose a country from the suggestions.');
    if (!form.reportValidity() || form.elements.website.value) return;
    if (!window.OutreachJobAlerts) { status.textContent = 'The newsletter is unavailable right now. Please try again shortly.'; status.className = 'nu-status is-error'; return; }
    var email = form.elements.email.value.trim();
    btn.disabled = true; btn.querySelector('span').textContent = 'Subscribing…'; status.textContent = ''; status.className = 'nu-status';
    window.OutreachJobAlerts.subscribe({ email: email, fullName: 'Newsletter subscriber', countryCode: match[0], countryName: match[1],
      sourceType: 'footer_signup', sourceJob: 'News & Updates newsletter', sourceUrl: location.href.split('#')[0], jobCategory: 'News & Updates newsletter' })
      .then(function (r) {
        form.innerHTML = '<p class="nu-check">' + %(check)s + (r && r.already_subscribed ? 'This email is already subscribed — thank you!' : r && r.reactivated ? 'Welcome back — you are subscribed again.' : 'Thank you — you are subscribed!') + '</p>';
      }).catch(function (err) { btn.disabled = false; btn.querySelector('span').textContent = 'Subscribe'; status.textContent = err.message || 'We could not save your subscription. Please try again.'; status.className = 'nu-status is-error'; });
  });
  form.elements.country.addEventListener('input', function () { form.elements.country.setCustomValidity(''); });

  // Jobs banners: count up the open-jobs number when the banner scrolls into view
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return; io.unobserve(en.target);
        var el = en.target, end = +el.dataset.count, t0 = null;
        if (matchMedia('(prefers-reduced-motion: reduce)').matches) { el.textContent = end; return; }
        requestAnimationFrame(function step(t) { t0 = t0 || t; var k = Math.min(1, (t - t0) / 1200); el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); });
      });
    });
    document.querySelectorAll('[data-count]').forEach(function (el) { el.textContent = '0'; io.observe(el); });
  }
})();
</script>"""


def main() -> None:
    settings = json.loads(SETTINGS.read_text(encoding="utf-8")) if SETTINGS.exists() else {}
    arts = blog_articles()
    arts += study_pages({a["title"] for a in arts})
    arts.sort(key=lambda a: a["date"], reverse=True)
    by_url = {a["url"].strip("/"): a for a in arts}

    def pick(key, default):
        chosen = [by_url[s.strip("/")] for s in settings.get(key, []) if s.strip("/") in by_url]
        return chosen or default

    featured = pick("featured", arts[:1])[0]
    trending = pick("trending", [a for a in arts if a is not featured][:2])[:2]
    guides = pick("guides", [next(a for a in arts if a["cats"][0] == c and a is not featured) for c in ("Study in Malta", "Employers")])[:2]
    ads = settings.get("ads", {})
    jobs = open_jobs()
    JOBS_BANNERS["nu-ad-wide"] = jobs_banner("wide", jobs)
    JOBS_BANNERS["nu-ad-box"] = jobs_banner("box", jobs, reverse=True)

    s = (ROOT / "about.html").read_text(encoding="utf-8")
    title = "News & Updates: Jobs, Hiring & Study in Malta | Outreach Recruitment"
    desc = ("Malta news and guides from Outreach Recruitment: job-search tips for candidates, hiring advice for employers "
            "and Study in Malta updates.")
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1, flags=re.S)

    def meta(attr, name, value):
        nonlocal s
        s = re.sub(rf'<meta content="[^"]*" {attr}="{re.escape(name)}"/>', f'<meta content="{E(value)}" {attr}="{name}"/>', s)
    meta("name", "description", desc); meta("property", "og:description", desc); meta("name", "twitter:description", desc)
    meta("property", "og:title", title); meta("name", "twitter:title", title); meta("property", "og:url", URL)
    meta("property", "og:image", SITE + featured["img"]); meta("name", "twitter:image", SITE + featured["img"])
    meta("property", "og:type", "website")
    s = re.sub(r'(<link href=")[^"]*(" rel="canonical"/>)', rf"\g<1>{URL}\g<2>", s, count=1)
    s = s.replace('<meta content="width=device-width, initial-scale=1" name="viewport"/>',
                  '<meta content="width=device-width, initial-scale=1" name="viewport"/>'
                  + ("" if settings.get("ready") else '\n<meta content="noindex, follow" name="robots"/>'), 1)
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
              {"@type": "ListItem", "position": 2, "name": "News & Updates", "item": URL}]},
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": "News & Updates", "url": URL, "description": desc,
           "inLanguage": "en", "dateModified": arts[0]["date"].strftime("%Y-%m-%d"),
           "isPartOf": {"@type": "WebSite", "name": "Outreach Recruitment", "url": f"{SITE}/"},
           "publisher": {"@type": "Organization", "name": "Outreach Recruitment Ltd", "url": f"{SITE}/",
                         "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/outreach-recruitment-logo.svg"}},
           "about": [{"@type": "Thing", "name": n} for n in ("Jobs in Malta", "Recruitment in Malta", "Study in Malta")],
           "mainEntity": {"@type": "ItemList", "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "url": SITE + a["url"], "name": a["title"]} for i, a in enumerate(arts)]}}]
    s = re.sub(r'<script type="application/ld\+json">.*?"AboutPage".*?</script>',
               "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld),
               s, count=1, flags=re.S)
    s = s.replace("</head>", CSS + "\n</head>", 1)

    trend_html = "".join(f"""<article class="nu-hcard">
  <a class="nu-hcard-img" href="{E(a['url'])}" tabindex="-1" aria-hidden="true"><img src="{E(a['img'])}" alt="{E(a['title'])}" loading="lazy" width="220" height="200"></a>
  <div><h3><a href="{E(a['url'])}">{E(a['title'])}</a></h3><p>{E(a['desc'])}</p>
  <div class="nu-meta"><time datetime="{a['date']:%Y-%m-%d}">{fmt(a['date'])}</time><i class="nu-dot"></i><span>{a['mins']} min read</span></div></div>
</article>""" for a in trending)
    follow = "".join(f'<li><a href="{u}" target="_blank" rel="noopener" aria-label="Outreach Recruitment on {n}"><svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg></a></li>'
                     for n, (u, p) in ICONS.items())
    chips = '<li><button class="nu-chip" type="button" data-filter="all" data-scroll>All articles</button></li>' + "".join(
        f'<li><button class="nu-chip" type="button" data-filter="{CAT_SLUG[c]}" data-scroll>{E(c)}</button></li>' for c in CATS)
    tabs = "".join(f'<button class="nu-chip nu-tab{" is-active" if i == 0 else ""}" type="button" role="tab" aria-selected="{str(i == 0).lower()}" '
                   f'aria-controls="nu-panel-{CAT_SLUG[c]}" data-cat="{CAT_SLUG[c]}">{E(c)}</button>' for i, c in enumerate(CATS))
    panels = "".join(f'<div class="nu-panel" id="nu-panel-{CAT_SLUG[c]}" role="tabpanel"{"" if i == 0 else " hidden"}>'
                     + "".join(card(a) for a in [x for x in arts if c in x["cats"]][:3]) + "</div>" for i, c in enumerate(CATS))
    guide_html = "".join(f"""<a class="nu-guide" href="{E(g['url'])}">
  <img src="{E(g['img'])}" alt="{E(g['title'])}" loading="lazy"><span class="nu-guide-icon">{BOOK_ICON}</span>
  <div class="nu-guide-body"><div class="nu-meta">{badge(g)}<time datetime="{g['date']:%Y-%m-%d}">{fmt(g['date'])}</time></div>
  <h3>{E(g['title'])}</h3><div class="nu-author"><span><img src="/assets/outreach-recruitment-logo.svg" alt=""></span>by Outreach Recruitment</div></div>
</a>""" for g in guides)

    content = f"""
<div class="nu">
  <div class="nu-wrap">
    <div class="nu-head"><h1>News &amp; Updates</h1>
      <div class="nu-head-btns"><a class="nu-btn accent" href="#newsletter">Subscribe{ARROW}</a><a class="nu-btn light" href="#latest" data-filter="all" data-scroll>Browse all articles{ARROW}</a></div></div>
    <p class="nu-intro">The latest news, guides and practical advice from the Outreach Recruitment team in Malta —
      job-search and CV tips for <a href="/jobs/">candidates looking for jobs in Malta</a>, hiring advice for
      <a href="/employers">employers recruiting in Malta</a>, and everything you need to
      <a href="/study-in-malta-complete-guide">study in Malta</a> as an international student.</p>
    <ul class="nu-chips" role="list">{chips}</ul>
    <a class="nu-featured" href="{E(featured['url'])}">
      <img src="{E(featured['img'])}" alt="{E(featured['alt'] or featured['title'])}" width="1240" height="460">
      <div class="nu-featured-body"><div class="nu-meta">{badge(featured)}<time datetime="{featured['date']:%Y-%m-%d}">{fmt(featured['date'])}</time></div>
        <h2>{E(featured['title'])}</h2><p>{E(featured['desc'])}</p>
        <div class="nu-author"><span><img src="/assets/outreach-recruitment-logo.svg" alt=""></span>by Outreach Recruitment</div></div>
    </a>
    <h2 class="nu-label">Trending Now</h2>
    <div class="nu-trend">{trend_html}</div>
    {ad(ads.get("top", {}), "728 x 90 px", "nu-ad-wide")}
    <div class="nu-split">
      <aside class="nu-side"><div class="nu-side-inner">
        <div><a class="nu-side-logo" href="/"><img src="/assets/outreach-recruitment-logo.svg" alt="Outreach Recruitment"></a>
          <p>News, guides and updates for students, employers and candidates in Malta — from the Outreach Recruitment team.</p></div>
        <form class="nu-search" role="search"><label class="sr-only" for="nu-search" style="position:absolute;left:-9999px">Search articles</label>
          <input id="nu-search" type="search" placeholder="Search for articles…" autocomplete="off">{SEARCH_ICON}</form>
        <div class="nu-follow"><strong>Follow us</strong><ul role="list">{follow}</ul></div>
        <div class="nu-side-ad">{ad(ads.get("sidebar", {}), "300 x 300 px", "nu-ad-box")}</div>
      </div></aside>
      <section class="nu-latest" id="latest" aria-labelledby="nu-latest-title" style="scroll-margin-top:120px">
        <div class="nu-latest-head"><h2 id="nu-latest-title">Latest articles</h2>
          <a class="nu-btn light" href="#latest" data-filter="all">Browse all articles{ARROW}</a></div>
        <div class="nu-grid" id="nu-grid">{"".join(card(a) for a in arts)}</div>
        <p class="nu-empty" id="nu-empty" hidden>No articles match your search yet — try another word or category.</p>
        <div class="nu-pager"><button class="nu-btn light" id="nu-prev" type="button"><span class="nu-arrow back">{ARROW_RAW}</span>Previous</button>
          <span class="nu-page-info" id="nu-page-info" aria-live="polite"></span>
          <button class="nu-btn accent" id="nu-next" type="button">Next{ARROW}</button></div>
      </section>
    </div>
    <section class="nu-news" id="newsletter" aria-labelledby="nu-news-title">
      <div class="nu-news-img"><img src="/assets/news/newsletter-illustration.svg" alt="Outreach Recruitment newsletter: new jobs, study in Malta and hiring updates by email" loading="lazy" width="560" height="460"></div>
      <div class="nu-news-body">
        <h2 id="nu-news-title">Subscribe to our newsletter to receive our latest news &amp; updates</h2>
        <p>New jobs, hiring advice and Study in Malta updates — straight to your inbox. No spam, unsubscribe anytime.</p>
        <form class="nu-form" id="nu-form" novalidate>
          <div class="nu-form-grid">
            <label><span>Email address</span><input name="email" type="email" autocomplete="email" maxlength="254" placeholder="you@example.com" required></label>
            <label><span>Current country of residence</span><input name="country" type="search" list="nu-countries" autocomplete="country-name" placeholder="Type to search countries" required>
              <datalist id="nu-countries"></datalist><small>Start typing, then choose your country.</small></label>
          </div>
          <label class="nu-consent"><input name="consent" type="checkbox" required><span>I agree to receive news, updates and relevant job alerts from Outreach Recruitment. I can unsubscribe at any time.</span></label>
          <input name="website" type="text" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
          <button class="nu-btn accent nu-submit" id="nu-submit" type="submit"><span>Subscribe</span>{ARROW}</button>
          <p class="nu-status" id="nu-status" role="status" aria-live="polite"></p>
        </form>
      </div>
    </section>
    <section aria-labelledby="nu-pop-title">
      <div class="nu-pop-head"><h2 id="nu-pop-title">Popular articles by category</h2><div class="nu-tabs" role="tablist">{tabs}</div></div>
      {panels}
      <div class="nu-center"><a class="nu-btn light" id="nu-pop-all" href="#latest" data-filter="study-in-malta" data-scroll>Browse all articles{ARROW}</a></div>
    </section>
  </div>
  <section class="nu-guides" aria-labelledby="nu-guides-title">
    <div class="nu-wrap">
      <div class="nu-guides-head"><h2 id="nu-guides-title">Must-read guides</h2>
        <p>Our most complete guides for studying in Malta and hiring the right people — start here.</p></div>
      <div class="nu-guide-grid">{guide_html}</div>
      <div class="nu-center"><a class="nu-btn accent" href="#latest" data-filter="all" data-scroll>Explore all articles{ARROW}</a></div>
    </div>
  </section>
  <div class="nu-wrap">{ad(ads.get("bottom", {}), "728 x 90 px", "nu-ad-wide").replace('nu-jobs-track"', 'nu-jobs-track rev"')}</div>
</div>
"""
    a = s.index('<main class="main">') + len('<main class="main">')
    b = s.index("</main>")
    s = s[:a] + content + s[b:]
    # The shell's "For teams preparing for growth, not hype" CTA (after </main>) does not belong on this page.
    s = re.sub(r'<section class="section cta">.*?</section>', "", s, count=1, flags=re.S)

    codes = re.search(r'countryCodes="([^"]+)"', (ROOT / "assets" / "footer-job-alerts.js").read_text(encoding="utf-8")).group(1)
    script = SCRIPT % {"per": PER_PAGE, "codes": json.dumps(codes), "check": json.dumps(CHECK_ICON)}
    s = s.replace("</body>", script + "\n</body>", 1)
    OUT.write_text(s, encoding="utf-8")
    counts = {c: sum(c in x["cats"] for x in arts) for c in CATS}
    print(f"news-updates.html written: {len(arts)} articles {counts}; featured = {featured['title'][:50]}; "
          f"{'indexable' if settings.get('ready') else 'noindex'}")


if __name__ == "__main__":
    main()
