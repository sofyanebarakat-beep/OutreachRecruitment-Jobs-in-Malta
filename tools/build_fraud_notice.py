#!/usr/bin/env python3
"""build_fraud_notice.py — /fraud-notice/: public notice about fraudsters using the Outreach Recruitment name.
Built from the about.html shell (site header/footer). Re-run after editing the text below."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://outreachrecruitment.net"
URL = f"{SITE}/fraud-notice/"
E = lambda s: html.escape(str(s), quote=True)
TITLE = "Public Notice: Fraudulent Job Offers Using Our Name | Outreach Recruitment"
DESC = ("Warning: individuals are fraudulently using the Outreach Recruitment name to offer remote jobs in Malta. "
        "They are not affiliated with us. See how to recognise and report fake offers.")
PUBLISHED = "2026-11-19"

CSS = """<style id="fraud-notice-style">
.navigation.w-nav { position: fixed !important; top: 0 !important; left: 0; right: 0; z-index: 1000; transform: none !important;
  translate: none !important; opacity: 1 !important; background: #fff !important; padding-top: 0 !important; box-shadow: 0 1px 0 #ececec; }
body { background: #fff; }
.fn { --ink: #1c2623; --muted: rgba(28,38,35,.68); --brand: #442DFA; --warn: #b42318; --warn-bg: #fef3f2;
  --serif: var(--_🅰-typography---font-family--heading, "Libre Caslon Condensed", "Times New Roman", serif);
  font-family: var(--_🅰-typography---font-family--body, "BDO Grotesk", Arial, sans-serif); color: var(--ink); padding: 9.5rem 0 5rem; }
.fn-wrap { width: min(820px, 100% - 32px); margin: 0 auto; }
.fn h1, .fn h2 { font-family: var(--serif); font-weight: 400 !important; letter-spacing: -.5px; margin: 0; color: var(--ink); }
.fn-notice { border-radius: 24px; overflow: hidden; background: #fff; border: 1px solid #f1d2cf; box-shadow: 0 24px 60px rgba(180,35,24,.10); }
.fn-notice-head { display: flex; align-items: center; gap: .6rem; padding: .9rem 1.6rem; background: var(--warn); color: #fff; font-weight: 700;
  font-size: .82rem; letter-spacing: .12em; text-transform: uppercase; }
.fn-icon { font-size: 1.1rem; letter-spacing: 0; }
.fn-notice-date { margin-left: auto; font-weight: 500; letter-spacing: .02em; text-transform: none; opacity: .9; }
.fn-notice-body { padding: clamp(1.6rem, 5vw, 3rem); background: linear-gradient(180deg, #fff8f7 0%, #fff 40%); }
.fn .fn-notice h1 { font-family: inherit !important; font-weight: 800 !important; font-size: clamp(1.45rem, 3.2vw, 2.05rem); line-height: 1.25;
  letter-spacing: .01em; color: var(--warn); margin: 0 0 1.5rem; padding-bottom: 1.25rem; border-bottom: 2px solid #f4c7c3; }
.fn-notice p { margin: 0 0 1.1rem; font-size: 1.1rem; line-height: 1.75; color: #2a2a2a; }
.fn-notice .fn-key { padding: 1rem 1.2rem; border-left: 4px solid var(--warn); background: var(--warn-bg); border-radius: 0 12px 12px 0; font-weight: 600; color: #7a271a; }
.fn-notice .fn-site a { font-weight: 700; }
.fn-notice-sign { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-top: 2rem; padding-top: 1.25rem; border-top: 1px solid #f1e4e2; }
.fn-notice-sign img { height: 30px; width: auto; }
.fn-notice-sign span { font-weight: 800; font-size: 1.1rem; letter-spacing: .02em; }
.fn h2 { font-family: var(--serif); font-weight: 400 !important; letter-spacing: -.5px; margin: 0; color: var(--ink); }
.fn-badge { display: inline-flex; align-items: center; gap: .5rem; padding: .45rem .9rem; border-radius: 999px; background: var(--warn-bg); color: var(--warn);
  font-weight: 700; font-size: .82rem; letter-spacing: .06em; text-transform: uppercase; }
.fn h1 { font-size: clamp(2.2rem, 4.5vw, 3.4rem); line-height: 1.08; margin: 1rem 0 .75rem; }
.fn-date { color: var(--muted); font-size: .95rem; margin: 0 0 2rem; }
.fn-card { border: 1px solid #f4c7c3; background: var(--warn-bg); border-radius: 20px; padding: clamp(1.4rem, 4vw, 2.2rem); }
.fn-card p { margin: 0 0 1rem; line-height: 1.7; font-size: 1.08rem; }
.fn-card p:last-child { margin-bottom: 0; }
.fn-card strong { color: var(--warn); }
.fn-sign { font-weight: 700; }
.fn h2 { font-size: clamp(1.7rem, 3vw, 2.2rem); margin: 3rem 0 1rem; }
.fn ul { padding-left: 1.2rem; margin: 0; } .fn li { margin: .55rem 0; line-height: 1.6; }
.fn a { color: var(--brand); }
.fn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.fn-tile { border: 1px solid #ececec; border-radius: 16px; padding: 1.25rem 1.4rem; background: #fff; }
.fn-tile h3 { margin: 0 0 .5rem; font-size: 1.05rem; }
.fn-tile p { margin: 0; color: var(--muted); line-height: 1.6; }
.fn-cta { display: flex; flex-wrap: wrap; gap: .75rem; margin-top: 1.25rem; }
.fn-btn { display: inline-flex; align-items: center; padding: .9rem 1.4rem; border-radius: 999px; font-weight: 600; text-decoration: none !important; }
.fn-btn.primary { background: var(--brand); color: #fff !important; } .fn-btn.light { background: #ECEAE1; color: #1c2623 !important; }
@media (max-width: 640px) { .fn { padding-top: 8rem; } .fn-grid { grid-template-columns: 1fr; } }
</style>"""


REPORT_JS = ('<script>document.addEventListener("click",function(e){var a=e.target.closest("[data-report]");if(!a)return;'
             'e.preventDefault();e.stopPropagation();if(window.OutreachHelp&&window.OutreachHelp.report)window.OutreachHelp.report();},true);</script>')


def main() -> None:
    s = (ROOT / "about.html").read_text(encoding="utf-8")
    s = re.sub(r"<title>.*?</title>", f"<title>{E(TITLE)}</title>", s, count=1, flags=re.S)
    for attr, name, value in [("name", "description", DESC), ("property", "og:description", DESC), ("name", "twitter:description", DESC),
                              ("property", "og:title", TITLE), ("name", "twitter:title", TITLE), ("property", "og:url", URL)]:
        s = re.sub(rf'<meta content="[^"]*" {attr}="{re.escape(name)}"/>', f'<meta content="{E(value)}" {attr}="{name}"/>', s)
    s = re.sub(r'(<link href=")[^"]*(" rel="canonical"/>)', rf"\g<1>{URL}\g<2>", s, count=1)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": "Public notice: fraudulent activities using our company name",
           "url": URL, "description": DESC, "datePublished": PUBLISHED, "inLanguage": "en",
           "publisher": {"@type": "Organization", "name": "Outreach Recruitment Ltd", "url": f"{SITE}/"}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
              {"@type": "ListItem", "position": 2, "name": "Fraud notice", "item": URL}]}]
    s = re.sub(r'<script type="application/ld\+json">.*?"AboutPage".*?</script>',
               "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld), s, count=1, flags=re.S)
    s = s.replace("</head>", CSS + "\n</head>", 1)
    content = f"""<div class="fn"><div class="fn-wrap">
  <article class="fn-notice" aria-labelledby="fn-title">
    <header class="fn-notice-head"><span class="fn-icon" aria-hidden="true">⚠️</span><span>Public notice</span><span class="fn-notice-date">19 November 2026</span></header>
    <div class="fn-notice-body">
      <h1 id="fn-title">PUBLIC NOTICE: FRAUDULENT ACTIVITIES USING OUR COMPANY NAME</h1>
      <p>We wish to alert our valued candidates, partners, and the general public that individuals are fraudulently using our company name, Outreach Recruitment and offering remote jobs in Malta.</p>
      <p class="fn-key">Please be advised that these individuals are NOT affiliated with, authorized by, or representatives of our company.</p>
      <p>We sincerely regret any inconvenience or losses that may have resulted from these fraudulent activities.</p>
      <p class="fn-site">Our jobs can be found on our website - <a href="/jobs/">www.outreachrecruitment.net</a></p>
      <p>Your safety and trust are important to us. Thank you for your understanding and continued support.</p>
      <footer class="fn-notice-sign"><img src="/assets/outreach-recruitment-logo.svg" alt="Outreach Recruitment" width="150" height="34"><span>Management</span></footer>
    </div>
  </article>
  <h2>How to check an offer is real</h2>
  <div class="fn-grid">
    <div class="fn-tile"><h3>Our jobs are on our website</h3><p>Every job we recruit for is listed on <a href="/jobs/">outreachrecruitment.net/jobs</a>. If you can't find the job there, treat the offer with caution.</p></div>
    <div class="fn-tile"><h3>Our email address</h3><p>Our team only contacts you from an <b>@outreachrecruitment.net</b> email address.</p></div>
  </div>
  <h2>If you receive a suspicious offer</h2>
  <ul>
    <li>Do not send money, bank details or personal documents.</li>
    <li>Report it to us, so we can follow up and warn others.</li>
  </ul>
  <div class="fn-cta"><a class="fn-btn primary" href="#help-chat" data-report>Report a suspicious offer</a><a class="fn-btn light" href="/jobs/">See our real jobs</a></div>
</div></div>
"""
    content += REPORT_JS
    a = s.index('<main class="main">') + len('<main class="main">')
    b = s.index("</main>")
    s = s[:a] + content + s[b:]
    s = re.sub(r'<section class="section cta">.*?</section>', "", s, count=1, flags=re.S)
    out = ROOT / "fraud-notice" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding="utf-8")
    sm = ROOT / "sitemaps" / "sitemap-pages.xml"
    x = sm.read_text(encoding="utf-8")
    if URL not in x:
        sm.write_text(x.replace("</urlset>", f"  <url>\n    <loc>{URL}</loc>\n    <lastmod>{PUBLISHED}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n\n</urlset>", 1), encoding="utf-8")
    print("fraud-notice/index.html written")


if __name__ == "__main__":
    main()
