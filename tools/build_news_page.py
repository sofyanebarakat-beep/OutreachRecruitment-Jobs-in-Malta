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


def badge(a: dict) -> str:
    return f'<span class="nu-badge">{E(a["cats"][0])}</span>'


def card(a: dict, extra: str = "") -> str:
    cats = " ".join(CAT_SLUG[c] for c in a["cats"])
    search = E((a["title"] + " " + a["desc"] + " " + " ".join(a["cats"])).lower())
    return f"""<article class="nu-card{extra}" data-cats="{cats}" data-search="{search}">
  <a class="nu-card-img" href="{E(a['url'])}" tabindex="-1" aria-hidden="true"><img src="{E(a['img'])}" alt="" loading="lazy" width="390" height="200"></a>
  <div class="nu-meta">{badge(a)}<time datetime="{a['date']:%Y-%m-%d}">{fmt(a['date'])}</time></div>
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


def ad(slot: dict, size: str, cls: str) -> str:
    """An ad slot: a real banner when image+link are set in tools/news_page.json, otherwise the placeholder."""
    if slot.get("image") and slot.get("link"):
        return (f'<a class="nu-ad {cls} has-banner" href="{E(slot["link"])}"><img src="{E(slot["image"])}" '
                f'alt="{E(slot.get("alt", "Advertisement"))}" loading="lazy"></a>')
    return f'<div class="nu-ad {cls}" aria-label="Advertising space"><span>Ad space</span><small>{size}</small></div>'


CSS = """<style id="news-page-style">
/* Header stays fixed and visible (the theme hides it while scrolling) */
.navigation.w-nav { position: fixed !important; top: 0 !important; left: 0; right: 0; z-index: 1000;
  transform: none !important; translate: none !important; opacity: 1 !important; }
body { background: #fff; }
.nu { --ink: #121212; --muted: #6b6b6b; --line: #e9e9e9; --soft: #f5f5f5; --brand: #442DFA;
  font-family: var(--_🅰-typography---font-family--body, "BDO Grotesk", Arial, sans-serif); color: var(--ink);
  padding: 9.5rem 0 5rem; background: #fff; }
.nu-wrap { width: min(1240px, 100% - 32px); margin: 0 auto; }
.nu h1, .nu h2, .nu h3 { font-family: inherit; color: var(--ink); letter-spacing: -.02em; margin: 0; }
.nu a { color: inherit; text-decoration: none; }
.nu-btn { display: inline-flex; align-items: center; justify-content: center; gap: .5rem; min-height: 52px; padding: 0 1.6rem;
  border-radius: 999px; font-weight: 600; font-size: 1rem; border: 1px solid var(--ink); cursor: pointer; transition: transform .25s ease, background .25s ease, color .25s ease; font-family: inherit; }
.nu-btn:hover { transform: translateY(-2px); }
.nu-btn.dark { background: var(--ink); color: #fff !important; }
.nu-btn.dark:hover { background: var(--brand); border-color: var(--brand); }
.nu-btn.outline { background: #fff; color: var(--ink); }
.nu-btn.outline:hover { background: var(--ink); color: #fff !important; }
.nu-badge { display: inline-flex; align-items: center; padding: .35rem .75rem; border-radius: 999px; background: var(--soft);
  font-size: .85rem; font-weight: 600; color: var(--ink); white-space: nowrap; }
.nu-meta { display: flex; align-items: center; gap: .6rem; color: var(--muted); font-size: .9rem; font-weight: 500; flex-wrap: wrap; }
/* Title row */
.nu-head { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.nu-head h1 { font-size: clamp(2.2rem, 4vw, 3rem); font-weight: 700; line-height: 1.05; }
.nu-head-btns { display: flex; gap: .9rem; flex-wrap: wrap; }
.nu-chips { display: flex; gap: .6rem; flex-wrap: wrap; margin: 0 0 2.25rem; padding: 0; list-style: none; }
.nu-chip { display: inline-flex; padding: .55rem 1.05rem; border-radius: 999px; background: var(--soft); font-weight: 600; font-size: .95rem;
  border: 0; cursor: pointer; font-family: inherit; color: var(--ink); transition: background .2s ease, color .2s ease; }
.nu-chip:hover { background: #e6e6e6; }
.nu-chip.is-active { background: var(--ink); color: #fff; }
/* Featured */
.nu-featured { position: relative; display: flex; align-items: center; min-height: 460px; overflow: hidden; background: #222; isolation: isolate; }
.nu-featured img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .8s ease; }
.nu-featured::before { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(90deg, rgba(10,10,10,.82) 0%, rgba(10,10,10,.55) 45%, rgba(10,10,10,.08) 100%); }
.nu-featured:hover img { transform: scale(1.03); }
.nu-featured-body { padding: clamp(1.75rem, 5vw, 4.5rem); max-width: 620px; color: #fff; display: flex; flex-direction: column; gap: 1rem; }
.nu-featured .nu-badge { background: #fff; }
.nu-featured .nu-meta { color: #fff; }
.nu-featured h2 { color: #fff; font-size: clamp(1.6rem, 3vw, 2.1rem); font-weight: 700; line-height: 1.2; }
.nu-featured p { margin: 0; color: rgba(255,255,255,.88); line-height: 1.65; }
.nu-author { display: flex; align-items: center; gap: .6rem; font-weight: 600; }
.nu-author span { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; background: #fff; }
.nu-author img { position: static !important; width: 22px !important; height: auto !important; z-index: 0 !important; transform: none !important; }
/* Trending */
.nu-label { display: flex; align-items: center; gap: 2rem; margin: 3rem 0 2rem; font-weight: 700; font-size: 1.15rem; }
.nu-label::after { content: ""; flex: 1; height: 1px; background: var(--line); }
.nu-trend { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2.25rem; }
.nu-hcard { display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 1.75rem; align-items: center; }
.nu-hcard-img { display: block; aspect-ratio: 11 / 10; overflow: hidden; background: var(--soft); }
.nu-hcard-img img, .nu-card-img img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .6s ease; }
.nu-hcard:hover img, .nu-card:hover .nu-card-img img { transform: scale(1.05); }
.nu-hcard h3 { font-size: 1.25rem; font-weight: 700; line-height: 1.35; margin-bottom: .6rem; }
.nu-hcard p { margin: 0 0 .9rem; color: var(--muted); line-height: 1.65; }
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
.nu-latest-head h2 { font-size: clamp(1.9rem, 3vw, 2.5rem); font-weight: 700; }
.nu-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 3rem 2.25rem; }
.nu-card { display: flex; flex-direction: column; gap: 1rem; }
.nu-grid .nu-card { padding-bottom: 3rem; border-bottom: 1px solid var(--line); }
.nu-card[hidden] { display: none; }
.nu-card-img { display: block; aspect-ratio: 39 / 20; overflow: hidden; background: var(--soft); }
.nu-card-title { font-size: 1.25rem; font-weight: 700; line-height: 1.35; }
.nu-card-title a:hover, .nu-hcard h3 a:hover { text-decoration: underline; text-underline-offset: 3px; }
.nu-card-text { margin: 0; color: var(--muted); line-height: 1.65; }
.nu-empty { color: var(--muted); padding: 2rem 0; }
.nu-pager { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 3rem; }
.nu-pager [hidden] { display: none; }
.nu-pager .nu-page-info { color: var(--muted); font-weight: 500; }
/* Newsletter */
.nu-news { position: relative; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); align-items: center; background: #121212;
  color: #fff; overflow: hidden; margin: 6rem 0; min-height: 480px; scroll-margin-top: 120px; }
.nu-news-img { align-self: center; padding: 3rem 1rem 3rem 3rem; }
.nu-news-img img { width: 100%; max-width: 600px; display: block; margin: 0 auto; }
.nu-news-body { padding: 4rem 3.5rem 4rem 1rem; display: flex; flex-direction: column; gap: 1.1rem; }
.nu-news h2 { color: #fff; font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight: 700; line-height: 1.15; }
.nu-news p { margin: 0; color: rgba(255,255,255,.82); line-height: 1.7; }
.nu-form { display: flex; flex-direction: column; gap: .8rem; margin-top: .6rem; max-width: 500px; }
.nu-pill { display: flex; align-items: center; background: #fff; border-radius: 999px; padding: .35rem .35rem .35rem 1.4rem; }
.nu-pill input { flex: 1; min-width: 0; border: 0; background: transparent; font: inherit; color: var(--ink); height: 50px; outline: none; }
.nu-pill .nu-btn { min-height: 46px; padding: 0 1.3rem; font-size: .95rem; white-space: nowrap; }
.nu-pill .nu-btn svg { width: 16px; height: 16px; }
.nu-step2 { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; }
.nu-step2[hidden] { display: none; }
.nu-step2 input, .nu-step2 select { width: 100%; height: 50px; border-radius: 999px; border: 0; padding: 0 1.2rem; font: inherit; background: #fff; color: var(--ink); }
.nu-step2 .nu-full { grid-column: 1 / -1; }
.nu-consent { display: flex; gap: .6rem; align-items: flex-start; font-size: .85rem; color: rgba(255,255,255,.75); line-height: 1.5; }
.nu-consent { font-weight: 400; cursor: pointer; }
.nu-step2 .nu-consent input { width: 18px; height: 18px; min-width: 18px; padding: 0; margin: .15rem 0 0; border-radius: 4px; accent-color: var(--brand); }
.nu-status { min-height: 1.2em; font-size: .92rem; margin: 0; }
.nu-status.is-error { color: #ff8a8a; }
.nu-status.is-ok { color: #9ff0b5; }
.nu-check { display: flex; align-items: center; gap: .6rem; font-weight: 600; color: #fff; }
.nu-check svg { width: 20px; height: 20px; }
/* Popular by category */
.nu-pop-head { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 2.25rem; }
.nu-pop-head h2 { font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight: 700; }
.nu-tabs { display: flex; gap: .7rem; flex-wrap: wrap; }
.nu-panel { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2rem; animation: nu-fade .45s ease; }
.nu-panel[hidden] { display: none; }
@keyframes nu-fade { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
.nu-center { display: flex; justify-content: center; margin-top: 2.75rem; }
/* Must-read guides */
.nu-guides { background: var(--soft); padding: 6rem 0; margin-top: 6rem; }
.nu-guides-head { text-align: center; max-width: 760px; margin: 0 auto 3rem; }
.nu-guides-head h2 { font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight: 700; margin-bottom: .9rem; }
.nu-guides-head p { margin: 0; color: var(--muted); line-height: 1.7; }
.nu-guide-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2.25rem; }
.nu-guide { position: relative; display: flex; align-items: flex-end; min-height: 540px; overflow: hidden; isolation: isolate; background: #222; }
.nu-guide > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .8s ease; }
.nu-guide::before { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(180deg, rgba(10,10,10,0) 30%, rgba(10,10,10,.85) 100%); }
.nu-guide:hover > img { transform: scale(1.04); }
.nu-guide-body { padding: 3rem; color: #fff; display: flex; flex-direction: column; gap: 1rem; }
.nu-guide .nu-badge { background: #fff; }
.nu-guide .nu-meta { color: #fff; }
.nu-guide h3 { color: #fff; font-size: clamp(1.5rem, 2.4vw, 1.9rem); font-weight: 700; line-height: 1.25; }
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
  .nu-news-img { order: 2; padding: 1rem 2rem 2.5rem; }
  .nu-news-img img { max-width: 420px; }
  .nu-follow { flex-direction: row; align-items: center; justify-content: space-between; width: 100%; border-bottom: 0; padding-bottom: 0; }
  .nu-news-body { padding: 3rem 2rem 1rem; }
  .nu-panel { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .nu-guide-grid { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 640px) {
  .nu-head-btns, .nu-head-btns .nu-btn { width: 100%; }
  .nu-head-btns .nu-btn { flex: 1; padding: 0 1rem; white-space: nowrap; font-size: .95rem; }
  .nu-latest-head .nu-btn { display: none; }
  .nu-news-img img { max-width: 300px; }
  .nu-featured { min-height: 520px; align-items: flex-end; }
  .nu-featured::before { background: linear-gradient(180deg, rgba(10,10,10,.1) 0%, rgba(10,10,10,.88) 70%); }
  .nu-hcard { grid-template-columns: 120px minmax(0, 1fr); gap: 1rem; align-items: start; }
  .nu-hcard h3 { font-size: 1.05rem; }
  .nu-hcard p { display: none; }
  .nu-grid, .nu-panel { grid-template-columns: minmax(0, 1fr); }
  .nu-ad-wide { min-height: 110px; margin: 3.5rem 0; }
  .nu-step2 { grid-template-columns: minmax(0, 1fr); }
  .nu-pill .nu-btn span { display: none; }
  .nu-guide { min-height: 440px; }
  .nu-guide-body { padding: 1.75rem; }
  .nu-guide-icon { top: 1.75rem; left: 1.75rem; }
}
@media (prefers-reduced-motion: reduce) { .nu * { transition: none !important; animation: none !important; } }
</style>"""

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

  // Newsletter: email first, then name + country (required by the subscriber list)
  var codes = %(codes)s.split(' ');
  var names = window.Intl && Intl.DisplayNames ? new Intl.DisplayNames(['en'], { type: 'region' }) : null;
  var countries = codes.map(function (c) { return [c, c === 'XK' ? 'Kosovo' : names ? names.of(c) : c]; }).sort(function (a, b) { return a[1].localeCompare(b[1]); });
  var sel = document.getElementById('nu-country');
  countries.forEach(function (c) { var o = document.createElement('option'); o.value = c[0]; o.textContent = c[1]; sel.appendChild(o); });
  var form = document.getElementById('nu-form'), step2 = document.getElementById('nu-step2'), status = document.getElementById('nu-status'), btn = document.getElementById('nu-submit');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.elements.website.value) return;
    if (step2.hidden) {
      if (!form.elements.email.reportValidity()) return;
      step2.hidden = false; step2.querySelectorAll('input, select').forEach(function (el) { el.required = el.type !== 'hidden'; });
      btn.querySelector('span').textContent = 'Confirm'; form.elements.full_name.focus(); return;
    }
    if (!form.reportValidity()) return;
    if (!window.OutreachJobAlerts) { status.textContent = 'The newsletter is unavailable right now. Please try again shortly.'; status.className = 'nu-status is-error'; return; }
    var c = countries.find(function (x) { return x[0] === sel.value; });
    btn.disabled = true; status.textContent = 'Subscribing…'; status.className = 'nu-status';
    window.OutreachJobAlerts.subscribe({ email: form.elements.email.value.trim(), fullName: form.elements.full_name.value.trim(), countryCode: c[0], countryName: c[1],
      sourceType: 'footer_signup', sourceJob: 'News & Updates newsletter', sourceUrl: location.href.split('#')[0], jobCategory: 'Newsletter: ' + form.elements.interest.value })
      .then(function (r) {
        form.innerHTML = '<p class="nu-check">' + %(check)s + (r && r.already_subscribed ? 'You are already subscribed — thank you!' : 'Thank you — you are subscribed!') + '</p>';
      }).catch(function (err) { btn.disabled = false; status.textContent = err.message || 'We could not save your subscription. Please try again.'; status.className = 'nu-status is-error'; });
  });
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

    s = (ROOT / "about.html").read_text(encoding="utf-8")
    title = "News & Updates | Outreach Recruitment Malta"
    desc = ("Latest news, guides and updates from Outreach Recruitment for students, employers and candidates in Malta — "
            "study in Malta, hiring advice and job-search tips.")
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1, flags=re.S)

    def meta(attr, name, value):
        nonlocal s
        s = re.sub(rf'<meta content="[^"]*" {attr}="{re.escape(name)}"/>', f'<meta content="{E(value)}" {attr}="{name}"/>', s)
    meta("name", "description", desc); meta("property", "og:description", desc); meta("name", "twitter:description", desc)
    meta("property", "og:title", title); meta("name", "twitter:title", title); meta("property", "og:url", URL)
    meta("property", "og:image", SITE + featured["img"]); meta("name", "twitter:image", SITE + featured["img"])
    s = re.sub(r'(<link href=")[^"]*(" rel="canonical"/>)', rf"\g<1>{URL}\g<2>", s, count=1)
    s = s.replace('<meta content="width=device-width, initial-scale=1" name="viewport"/>',
                  '<meta content="width=device-width, initial-scale=1" name="viewport"/>'
                  + ("" if settings.get("ready") else '\n<meta content="noindex, follow" name="robots"/>'), 1)
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
              {"@type": "ListItem", "position": 2, "name": "News & Updates", "item": URL}]},
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": "News & Updates", "url": URL, "description": desc,
           "mainEntity": {"@type": "ItemList", "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "url": SITE + a["url"], "name": a["title"]} for i, a in enumerate(arts)]}}]
    s = re.sub(r'<script type="application/ld\+json">.*?"AboutPage".*?</script>',
               "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld),
               s, count=1, flags=re.S)
    s = s.replace("</head>", CSS + "\n</head>", 1)

    trend_html = "".join(f"""<article class="nu-hcard">
  <a class="nu-hcard-img" href="{E(a['url'])}" tabindex="-1" aria-hidden="true"><img src="{E(a['img'])}" alt="" loading="lazy" width="220" height="200"></a>
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
  <img src="{E(g['img'])}" alt="" loading="lazy"><span class="nu-guide-icon">{BOOK_ICON}</span>
  <div class="nu-guide-body"><div class="nu-meta">{badge(g)}<time datetime="{g['date']:%Y-%m-%d}">{fmt(g['date'])}</time></div>
  <h3>{E(g['title'])}</h3><div class="nu-author"><span><img src="/assets/outreach-recruitment-logo.svg" alt=""></span>by Outreach Recruitment</div></div>
</a>""" for g in guides)

    content = f"""
<div class="nu">
  <div class="nu-wrap">
    <div class="nu-head"><h1>News &amp; Updates</h1>
      <div class="nu-head-btns"><a class="nu-btn dark" href="#newsletter">Subscribe</a><a class="nu-btn outline" href="#latest" data-filter="all" data-scroll>Browse all articles</a></div></div>
    <ul class="nu-chips" role="list">{chips}</ul>
    <a class="nu-featured" href="{E(featured['url'])}">
      <img src="{E(featured['img'])}" alt="{E(featured['alt'] or featured['title'])}" width="1240" height="460">
      <div class="nu-featured-body"><div class="nu-meta">{badge(featured)}<time datetime="{featured['date']:%Y-%m-%d}">{fmt(featured['date'])}</time></div>
        <h2>{E(featured['title'])}</h2><p>{E(featured['desc'])}</p>
        <div class="nu-author"><span><img src="/assets/outreach-recruitment-logo.svg" alt=""></span>by Outreach Recruitment</div></div>
    </a>
    <div class="nu-label">Trending Now</div>
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
          <a class="nu-btn outline" href="#latest" data-filter="all">Browse all articles</a></div>
        <div class="nu-grid" id="nu-grid">{"".join(card(a) for a in arts)}</div>
        <p class="nu-empty" id="nu-empty" hidden>No articles match your search yet — try another word or category.</p>
        <div class="nu-pager"><button class="nu-btn outline" id="nu-prev" type="button">Previous</button>
          <span class="nu-page-info" id="nu-page-info" aria-live="polite"></span>
          <button class="nu-btn dark" id="nu-next" type="button">Next</button></div>
      </section>
    </div>
    <section class="nu-news" id="newsletter" aria-labelledby="nu-news-title">
      <div class="nu-news-img"><img src="/assets/news/newsletter-laptop.png" alt="The Outreach Recruitment website on a laptop" loading="lazy" width="990" height="721"></div>
      <div class="nu-news-body">
        <h2 id="nu-news-title">Subscribe to our newsletter to receive our latest news &amp; updates</h2>
        <p>New jobs, hiring advice and Study in Malta updates — straight to your inbox. No spam, unsubscribe anytime.</p>
        <form class="nu-form" id="nu-form" novalidate>
          <div class="nu-pill"><input name="email" type="email" placeholder="Enter your email address" autocomplete="email" maxlength="254" required aria-label="Email address">
            <button class="nu-btn dark" id="nu-submit" type="submit">{MAIL_ICON}<span>Subscribe</span></button></div>
          <div class="nu-step2" id="nu-step2" hidden>
            <input name="full_name" type="text" placeholder="Full name" autocomplete="name" maxlength="120" aria-label="Full name">
            <select id="nu-country" name="country" aria-label="Country of residence"><option value="">Country of residence</option></select>
            <select class="nu-full" name="interest" aria-label="I am interested in">
              <option value="Candidates">I'm looking for a job in Malta</option><option value="Employers">I'm an employer hiring in Malta</option>
              <option value="Study in Malta">I want to study in Malta</option></select>
            <label class="nu-consent nu-full"><input type="checkbox" name="consent">I agree to receive emails from Outreach Recruitment. I can unsubscribe at any time.</label>
          </div>
          <input name="website" type="text" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
          <p class="nu-status" id="nu-status" role="status"></p>
        </form>
      </div>
    </section>
    <section aria-labelledby="nu-pop-title">
      <div class="nu-pop-head"><h2 id="nu-pop-title">Popular articles by category</h2><div class="nu-tabs" role="tablist">{tabs}</div></div>
      {panels}
      <div class="nu-center"><a class="nu-btn outline" id="nu-pop-all" href="#latest" data-filter="study-in-malta" data-scroll>Browse all articles</a></div>
    </section>
  </div>
  <section class="nu-guides" aria-labelledby="nu-guides-title">
    <div class="nu-wrap">
      <div class="nu-guides-head"><h2 id="nu-guides-title">Must-read guides</h2>
        <p>Our most complete guides for studying in Malta and hiring the right people — start here.</p></div>
      <div class="nu-guide-grid">{guide_html}</div>
      <div class="nu-center"><a class="nu-btn dark" href="#latest" data-filter="all" data-scroll>Explore all articles</a></div>
    </div>
  </section>
  <div class="nu-wrap">{ad(ads.get("bottom", {}), "728 x 90 px", "nu-ad-wide")}</div>
</div>
"""
    a = s.index('<main class="main">') + len('<main class="main">')
    b = s.index("</main>")
    s = s[:a] + content + s[b:]

    codes = re.search(r'countryCodes="([^"]+)"', (ROOT / "assets" / "footer-job-alerts.js").read_text(encoding="utf-8")).group(1)
    script = SCRIPT % {"per": PER_PAGE, "codes": json.dumps(codes), "check": json.dumps(CHECK_ICON)}
    s = s.replace("</body>", script + "\n</body>", 1)
    OUT.write_text(s, encoding="utf-8")
    counts = {c: sum(c in x["cats"] for x in arts) for c in CATS}
    print(f"news-updates.html written: {len(arts)} articles {counts}; featured = {featured['title'][:50]}; "
          f"{'indexable' if settings.get('ready') else 'noindex'}")


if __name__ == "__main__":
    main()
