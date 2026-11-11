#!/usr/bin/env python3
"""Apply the shared blog article layout (assets/blog-article.css/js) to blog/*.html.

Idempotent: pages already using the layout are re-rendered from their own parts.
Usage: python3 tools/apply_blog_template.py [blog/file.html ...]   (default: all articles)
"""
import html
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
SITE = "https://outreachrecruitment.net"
ASSET_V = "3"
RELATED_HEADINGS = {"read more", "à lire aussi", "leggi anche"}

I18N = {
    "en": dict(back="Back to Blog", home="Home", min="min read", more="Browse more related articles below",
               all="View all", toc="On this page", share="Share", copy="Copy link", copied="Copied!",
               by="Written by Outreach Recruitment",
               about="Recruitment specialists in Malta helping employers hire and candidates find work.",
               brand="Outreach Recruitment",
               emp_t="Hiring in Malta?", emp_p="Get pre-vetted candidates shortlisted for you.", emp_b="Request support",
               emp_bar="Need hiring support?", emp_bar_b="Contact us",
               job_t="Looking for work in Malta?", job_p="Browse current vacancies and apply today.", job_b="View jobs",
               job_bar="Looking for a job in Malta?", job_bar_b="View jobs",
               stu_t="Want to study in Malta?", stu_p="Get free guidance on programmes and applications.", stu_b="Study in Malta",
               stu_bar="Want to study in Malta?", stu_bar_b="Get started"),
    "fr": dict(back="Retour au blog", home="Accueil", min="min de lecture", more="Découvrez d'autres articles",
               all="Tout voir", toc="Sur cette page", share="Partager", copy="Copier le lien", copied="Copié !",
               by="Rédigé par Outreach Recruitment",
               about="Spécialistes du recrutement à Malte, au service des employeurs et des candidats.",
               brand="Outreach Recruitment",
               emp_t="Vous recrutez à Malte ?", emp_p="Recevez une présélection de candidats vérifiés.", emp_b="Demander de l'aide",
               emp_bar="Besoin d'aide pour recruter ?", emp_bar_b="Contact",
               job_t="Vous cherchez du travail à Malte ?", job_p="Consultez les offres actuelles et postulez.", job_b="Voir les offres",
               job_bar="Vous cherchez un emploi à Malte ?", job_bar_b="Voir les offres",
               stu_t="Étudier à Malte ?", stu_p="Conseils gratuits sur les programmes et les candidatures.", stu_b="Étudier à Malte",
               stu_bar="Étudier à Malte ?", stu_bar_b="Commencer"),
    "it": dict(back="Torna al blog", home="Home", min="min di lettura", more="Scopri altri articoli correlati",
               all="Vedi tutti", toc="In questa pagina", share="Condividi", copy="Copia link", copied="Copiato!",
               by="Scritto da Outreach Recruitment",
               about="Specialisti del recruitment a Malta al servizio di aziende e candidati.",
               brand="Outreach Recruitment",
               emp_t="Assumi a Malta?", emp_p="Ricevi una selezione di candidati verificati.", emp_b="Richiedi supporto",
               emp_bar="Serve supporto per assumere?", emp_bar_b="Contattaci",
               job_t="Cerchi lavoro a Malta?", job_p="Scopri le offerte attuali e candidati.", job_b="Vedi le offerte",
               job_bar="Cerchi lavoro a Malta?", job_bar_b="Vedi le offerte",
               stu_t="Vuoi studiare a Malta?", stu_p="Consulenza gratuita su programmi e candidature.", stu_b="Studiare a Malta",
               stu_bar="Vuoi studiare a Malta?", stu_bar_b="Inizia"),
}


def esc(s):
    return html.escape(s, quote=True)


def articles():
    return sorted(p for p in BLOG.glob("*.html") if p.name != "index.html")


def txt(el):
    return el.get_text(" ", strip=True) if el else ""


def extract(path):
    """Return meta dict + body html + related hrefs for one article."""
    raw = path.read_text(encoding="utf-8")
    a, b = raw.index('<main class="main">'), raw.index("</main>")
    main = BeautifulSoup(raw[a:b + len("</main>")], "html.parser")
    meta = {"slug": path.stem, "related": []}
    if main.select_one(".od-section"):
        meta["tag"] = txt(main.select_one(".od-tag"))
        meta["title"] = txt(main.select_one(".od-title"))
        spans = main.select(".od-meta span")
        meta["date"] = txt(spans[1]) if len(spans) > 1 else ""
        img = main.select_one(".od-image img")
        body_root = main.select_one("#odBody") or main.select_one(".od-rich")
        body = "".join(str(c) for c in body_root.contents)
        for c in main.select(".od-more a.od-card"):
            meta["related"].append(c["href"])
        meta["rel_done"] = True
    else:
        hdr = main.select_one(".page-header")
        meta["tag"] = txt(hdr.select_one(".tag"))
        meta["title"] = txt(hdr.select_one("h1"))
        meta["date"] = txt(hdr.select_one(".caption"))
        img = hdr.select_one(".cms-featured-media img")
        sec = [s for s in main.find("main").find_all("section", recursive=False) if s is not hdr][0]
        container = sec.select_one(".w-layout-blockcontainer") or sec
        mainel = main.find("main")
        node = None
        for el in mainel.find_all(True):
            if txt(el).strip().lower() in RELATED_HEADINGS and not el.find(["a", "img", "section"]):
                node = el
                break
        if node is not None:
            while node.parent is not mainel:
                p = node.parent
                if p.find(class_="w-richtext") or p.find("table") or p.find(class_="faq-item"):
                    break
                node = p
            for l in node.find_all("a", href=True):
                meta["related"].append(l["href"])
            node.decompose()
        else:
            meta["warn"] = "no related heading"
        for bt in container.find_all(class_="buttons"):
            if bt.find("a", href="/blog/"):
                bt.decompose()
        for h in container.find_all("h1"):
            if not h.get_text().replace("\u200d", "").strip():
                h.decompose()
        body = "".join(str(c) for c in container.contents)
    m = re.search(r'<meta name="author" content="([^"]+)"', raw[:a])
    meta["author"] = html.unescape(m.group(1)) if m else ""
    meta["img_src"] = img["src"] if img else ""
    meta["img_alt"] = img.get("alt", "") if img else ""
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    meta["mins"] = max(1, math.ceil(words / 200))
    meta["body"] = body
    return meta, raw


# Articles whose hero is a designed graphic (text in the image): show it whole, never cropped.
FULL_HERO = {"moving-to-malta-for-work"}


def team_member(name):
    """Return the Our Team entry (name, role, photo, LinkedIn) for an article author, or None."""
    if not name:
        return None
    data = json.loads((ROOT / "tools" / "team_data.json").read_text(encoding="utf-8"))
    for p in [data["ceo"]] + data["members"]:
        if p["name"].lower() == name.lower():
            return p
    return None


AUTHOR_CSS = (
    '<style id="od-author-style">'
    '.od-byline{display:inline-flex;align-items:center;gap:8px;color:#0c0407;font-weight:600;text-decoration:none}'
    '.od-byline img{width:28px;height:28px;border-radius:50%;object-fit:cover;flex:none;box-shadow:0 0 0 2px #fff,0 0 0 3px #e4e0ff}'
    '.od-byline:hover{color:#442dfa}'
    '.od-author-role{display:block;margin-top:2px;font-size:13px;font-weight:600;color:#442dfa}'
    '.od-author-in{display:inline-flex;align-items:center;gap:6px;margin-top:8px;font-size:13px;font-weight:600;color:#0a66c2;text-decoration:none}'
    '.od-author-in svg{width:15px;height:15px}'
    '</style>'
)
IN_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.94 8.5H3.56V20h3.38V8.5ZM5.25 3A1.97 1.97 0 1 0 5.3 7a1.97 1.97 0 0 0-.05-4ZM20.44 13.4c0-3.1-1.65-5.15-4.4-5.15a3.83 3.83 0 0 0-3.44 1.9V8.5H9.37c.04.93 0 11.5 0 11.5h3.23v-6.42c0-.34.03-.69.13-.93.28-.69.9-1.4 1.95-1.4 1.38 0 1.93 1.05 1.93 2.6V20h3.23z"/></svg>')


def short_date(d):
    try:
        return datetime.strptime(d, "%B %d, %Y").strftime("%b %-d, %Y")
    except ValueError:
        return d


def kind(tag):
    t = tag.lower()
    if "study" in t:
        return "stu"
    if any(w in t for w in ("employer", "team", "culture", "structure")):
        return "emp"
    return "job"


def pick_related(meta, all_meta):
    known = {m["slug"] for m in all_meta}
    out = []
    for h in meta["related"]:
        s = h.strip("/").split("/")[-1].replace(".html", "")
        if s in known and s != meta["slug"] and s not in out:
            out.append(s)
    pool = sorted(all_meta, key=lambda m: (m["tag"] != meta["tag"], m["slug"]))
    for m in pool:
        if len(out) >= 3:
            break
        if m["slug"] != meta["slug"] and m["slug"] not in out:
            out.append(m["slug"])
    return out[:3]


def render(meta, all_meta, lang):
    L = I18N.get(lang, I18N["en"])
    k = kind(meta["tag"] + " " + meta["slug"].replace("-", " "))
    by_slug = {m["slug"]: m for m in all_meta}
    url = f"{SITE}/{meta['slug']}/"
    cards = "".join(
        f'<a class="od-card" href="/{s}/"><div class="od-card-img"><img src="{esc(by_slug[s]["img_src"])}" '
        f'alt="{esc(by_slug[s]["img_alt"])}" loading="lazy" decoding="async"/><span>{esc(by_slug[s]["tag"])}</span></div>'
        f'<div class="od-card-meta"><span>{esc(short_date(by_slug[s]["date"]))}</span><i></i>'
        f'<span>{by_slug[s]["mins"]} {L["min"]}</span></div><h3>{esc(by_slug[s]["title"])}</h3></a>'
        for s in pick_related(meta, all_meta)
    )
    cta_href = {"emp": "/contact-us.html", "job": "/jobs/", "stu": "/study-in-malta.html"}[k]
    share_text = esc(meta["title"] + " " + url)
    share = (
        f'<div class="od-share"><span>{L["share"]}</span>'
        f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={esc(url)}" target="_blank" rel="noopener">LinkedIn</a>'
        f'<a href="https://wa.me/?text={html.escape(meta["title"] + " " + url, quote=True).replace(" ", "%20")}" target="_blank" rel="noopener">WhatsApp</a>'
        f'<button type="button" data-od-copy data-done="{esc(L["copied"])}">{L["copy"]}</button></div>'
    )
    who = team_member(meta.get("author"))
    if who:
        pos = who.get("photo_position", "center 30%")
        li = (who.get("socials") or {}).get("linkedin", "")
        byline = (f'<span><a class="od-byline" href="/our-team"><img src="{esc(who["photo"])}" alt="{esc(who["name"])}" width="28" height="28" '
                  f'style="object-position:{esc(pos)}"/>{esc(who["name"])}</a></span>')
        author_box = (f'{AUTHOR_CSS}<div class="od-author"><img src="{esc(who["photo"])}" alt="{esc(who["name"])}, {esc(who["role"])} at Outreach Recruitment" '
                      f'width="56" height="56" loading="lazy" style="object-position:{esc(pos)}"/><div><strong>Written by {esc(who["name"])}</strong>'
                      f'<span class="od-author-role">{esc(who["role"])} · Outreach Recruitment</span><p>{esc(who.get("bio", ""))}</p>'
                      + (f'<a class="od-author-in" href="{esc(li)}" target="_blank" rel="noopener">{IN_SVG}Connect on LinkedIn</a>' if li else "")
                      + '</div></div>')
    else:
        byline = f'<span>{L["brand"]}</span>'
        author_box = (f'<div class="od-author"><img src="/assets/job-card-logo.jpg" alt="Outreach Recruitment" width="56" height="56" loading="lazy"/>'
                      f'<div><strong>{L["by"]}</strong><p>{L["about"]}</p></div></div>')
    return f'''<main class="main">
    <div class="od-progress" id="odProgress"></div>
    <section class="od-section">
      <div class="od-container">
        <div class="od-layout">
          <div class="od-left">
            <nav class="od-crumbs" aria-label="Breadcrumb"><a href="/blog/">&larr; {L["back"]}</a><span>/</span><a href="/">{L["home"]}</a><span>/</span><b>{esc(meta["tag"])}</b></nav>
            <div class="od-tag">{esc(meta["tag"])}</div>
            <div class="od-meta">{byline}<i></i><span>{esc(meta["date"])}</span><i></i><span>{meta["mins"]} {L["min"]}</span></div>
            <h1 class="od-title">{esc(meta["title"])}</h1>
            <div class="od-image{' od-image-full' if meta['slug'] in FULL_HERO else ''}"><img src="{esc(meta["img_src"])}" alt="{esc(meta["img_alt"])}" width="1200" height="630" fetchpriority="high" decoding="async"/></div>
            <article class="cms-article od-rich" id="odBody">{meta["body"]}</article>
            <div class="od-end">
              {author_box}
              {share}
            </div>
          </div>
          <aside class="od-right">
            <details class="od-side-block od-toc" id="odToc" open><summary>{L["toc"]}</summary><ol></ol></details>
            <div class="od-side-block od-cta-card"><h2>{L[k + "_t"]}</h2><p>{L[k + "_p"]}</p><a class="od-btn" href="{cta_href}">{L[k + "_b"]}</a></div>
          </aside>
        </div>
      </div>
    </section>
    <section class="od-more"><div class="od-container">
      <div class="od-more-head"><h2>{L["more"]}</h2><a class="od-btn" href="/blog/">{L["all"]} &rsaquo;</a></div>
      <div class="od-cards">{cards}</div>
    </div></section>
    <div class="od-cta-bar" id="odCtaBar"><span>{L[k + "_bar"]}</span><a href="{cta_href}">{L[k + "_bar_b"]}</a></div>
  </main>'''


def rewrite_page(path, meta, raw, all_meta):
    lang = (re.search(r'<html[^>]*\blang="(\w+)"', raw) or [None, "en"])[1]
    new_main = render(meta, all_meta, lang)
    a, b = raw.index('<main class="main">'), raw.index("</main>") + len("</main>")
    t = raw[:a] + new_main + raw[b:]
    # drop inline layout CSS/JS from the first hand-built version of this layout
    i = t.find("    .od-section{margin:0 20px")
    if i != -1:
        j = t.index("  </style>", i)
        t = t[:i] + t[j:]
    t = re.sub(r'<script>\(function\(\)\{var b=document\.getElementById\("odProgress"\).*?</script>\n?', "", t, flags=re.S)
    css = f'<link href="/assets/blog-article.css?v={ASSET_V}" rel="stylesheet" type="text/css"/>\n'
    if "/assets/blog-article.css" not in t:
        marker = '<style id="blog-white-bg">'
        t = t.replace(marker, css + marker, 1) if marker in t else t.replace("</head>", css + "</head>", 1)
    js = f'<script src="/assets/blog-article.js?v={ASSET_V}" defer></script>\n'
    if "/assets/blog-article.js" not in t:
        t = t.replace("</body>", js + "</body>", 1)
    path.write_text(t, encoding="utf-8")
    # GitHub Pages has no rewrites: /<slug>/ is served from <slug>/index.html
    out = ROOT / path.stem / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(t, encoding="utf-8")


def root_copies():
    """Some slugs are served from a root-level .html file instead of blog/."""
    return [ROOT / p.name for p in articles() if (ROOT / p.name).exists()]


def main(argv):
    files = [Path(a).resolve() for a in argv] or articles() + root_copies()
    all_meta = [extract(p)[0] for p in articles()]
    for p in files:
        meta, raw = extract(p)
        rewrite_page(p, meta, raw, all_meta)
        print(("WARN " + meta["warn"] + " " if meta.get("warn") else "ok   ") + str(p.relative_to(ROOT)))


if __name__ == "__main__":
    main(sys.argv[1:])
