#!/usr/bin/env python3
"""
build_help_center.py — the /help-center pages (template layout, placeholder text for now).

  /help-center/                         home: hero + search + category cards
  /help-center/<category>/              category: header + question cards   (jobs-in-malta, hire, study-in-malta)
  /help-center/question/<slug>/         question: hero + article card

Uses about.html as the shell (site header + footer), adds the support bubble (assets/help-widget.js).
Edit CATEGORIES / QUESTIONS below and re-run:  python3 tools/build_help_center.py
Pages are noindex while READY is False (placeholder text).
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://outreachrecruitment.net"
READY = False
E = lambda s: html.escape(str(s), quote=True)
LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque ac pellentesque diam felis."
LOREM2 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque tellus rutrum rhoncus ipsum maecenas tellus. Consequat odio viverra convallis."

ICONS = {
    "jobs-in-malta": '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="7" y="15" width="34" height="24" rx="5" fill="#442DFA"/><path d="M18 15v-3a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v3" fill="none" stroke="#1c2623" stroke-width="3"/><path d="M7 25h34" stroke="#1c2623" stroke-width="3"/><rect x="21" y="22" width="6" height="6" rx="1.5" fill="#fff"/></svg>',
    "hire": '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="18" cy="17" r="7" fill="#442DFA"/><path d="M5 38c1.5-7 6.5-11 13-11s11.5 4 13 11" fill="#442DFA"/><circle cx="33" cy="15" r="5" fill="#1c2623"/><path d="M28 26c6 0 11 3 13 10" fill="none" stroke="#1c2623" stroke-width="3" stroke-linecap="round"/></svg>',
    "study-in-malta": '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M4 18 24 9l20 9-20 9z" fill="#442DFA"/><path d="M12 23v9c0 3 5 6 12 6s12-3 12-6v-9" fill="none" stroke="#1c2623" stroke-width="3"/><path d="M44 18v11" stroke="#1c2623" stroke-width="3" stroke-linecap="round"/></svg>',
}
CATEGORIES = [
    ("jobs-in-malta", "Jobs in Malta"),
    ("hire", "Hire"),
    ("study-in-malta", "Study in Malta"),
]
# Placeholder questions, used for a category until real questions are published from the admin
# (Help Center Inbox → "Turn into Help Center article", stored in the Supabase table help_faqs).
PLACEHOLDERS = [(f"{c}-question-{i}", c, f"{name} question title {i}?") for c, name in CATEGORIES for i in range(1, 5)]
QUESTIONS: list[tuple[str, str, str]] = []
REAL: dict[str, dict] = {}


def load_faqs() -> list[dict]:
    """Published Help Center questions from Supabase (public read). Empty if the table does not exist yet."""
    import urllib.request
    try:
        url = "https://atcitaqyraeqngcsaeun.supabase.co/rest/v1/help_faqs?select=*&status=eq.published&order=created_at.asc"
        key = "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY"
        req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"[]")
    except Exception as exc:  # noqa: BLE001
        print(f"note: no published Help Center questions loaded ({exc})")
        return []


def md(text: str) -> str:
    """Small Markdown → HTML for answers: paragraphs, - lists, ## / ### headings, **bold**, [links](url)."""
    def inline(t: str) -> str:
        t = E(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", r'<a href="\2">\1</a>', t)
    out = []
    for block in re.split(r"\n\s*\n", str(text or "").replace("\r", "").strip()):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        if all(re.match(r"^[-*]\s+", l) for l in lines):
            items = [inline(re.sub(r"^[-*]\s+", "", l)) for l in lines]
            out.append("<ul>" + "".join("<li>" + i + "</li>" for i in items) + "</ul>")
        elif lines[0].startswith("### "):
            out.append(f"<h3>{inline(lines[0][4:])}</h3>" + (f"<p>{inline(' '.join(lines[1:]))}</p>" if lines[1:] else ""))
        elif lines[0].startswith("## "):
            out.append(f"<h2>{inline(lines[0][3:])}</h2>" + (f"<p>{inline(' '.join(lines[1:]))}</p>" if lines[1:] else ""))
        else:
            out.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(out)


def excerpt(text: str, n: int = 170) -> str:
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"[#*>]|^-\s", "", str(text or ""), flags=re.M))
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"

CSS = """<style id="help-center-style">
.navigation.w-nav { position: fixed !important; top: 0 !important; left: 0; right: 0; z-index: 1000; transform: none !important;
  translate: none !important; opacity: 1 !important; background: #fff !important; padding-top: 0 !important; box-shadow: 0 1px 0 #ececec; }
body { background: #fff; }
.hc { --ink: #1c2623; --muted: rgba(28,38,35,.64); --brand: #442DFA; --soft: #f4f2ff; --line: #ececec;
  --serif: var(--_🅰-typography---font-family--heading, "Libre Caslon Condensed", "Times New Roman", serif);
  font-family: var(--_🅰-typography---font-family--body, "BDO Grotesk", Arial, sans-serif); color: var(--ink); }
.hc h1, .hc h2, .hc h3 { font-family: var(--serif); font-weight: 400 !important; letter-spacing: -.5px; margin: 0; color: inherit; }
.hc a { text-decoration: none; }
.hc-wrap { width: min(1180px, 100% - 32px); margin: 0 auto; }
.hc-narrow { width: min(760px, 100% - 32px); margin: 0 auto; }
/* hero */
.hc-hero { position: relative; overflow: visible; background: var(--brand); color: #fff; text-align: center; padding: 11rem 0 9.5rem; isolation: isolate; }
.hc-hero::before { content: ""; position: absolute; inset: 0; z-index: -1; opacity: .16;
  background-image: linear-gradient(rgba(255,255,255,.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.6) 1px, transparent 1px);
  background-size: 56px 56px; mask-image: linear-gradient(180deg, transparent, #000 40%, #000); -webkit-mask-image: linear-gradient(180deg, transparent, #000 40%, #000); }
.hc-hero h1 { font-size: clamp(2.6rem, 5vw, 4.2rem); line-height: 1.05; color: #fff; }
.hc-hero p { margin: 1rem auto 0; max-width: 620px; font-size: 1.15rem; color: rgba(255,255,255,.9); }
.hc-search { display: flex; align-items: center; gap: .5rem; max-width: 720px; margin: 2.25rem auto 0; padding: 6px 6px 6px 20px; border-radius: 999px; background: #fff; box-shadow: 0 0 0 4px rgba(255,255,255,.35); }
.hc-search svg { width: 20px; height: 20px; color: #777; flex: none; }
.hc-search input { flex: 1; min-width: 0; border: 0; outline: none; font: inherit; font-size: 1rem; padding: .8rem .2rem; color: var(--ink); background: transparent; }
.hc-search button { border: 0; border-radius: 999px; padding: .9rem 1.8rem; background: var(--brand); color: #fff; font: inherit; font-weight: 600; cursor: pointer; }
/* live search */
.hc-search-box { position: relative; max-width: 720px; margin: 2.25rem auto 0; text-align: left; }
.hc-search-box .hc-search { margin: 0; }
.hc-results { position: absolute; left: 0; right: 0; top: calc(100% + 10px); z-index: 20; background: #fff; color: var(--ink); border-radius: 18px;
  box-shadow: 0 24px 60px rgba(16,16,30,.25); overflow: hidden; max-height: min(460px, 60vh); display: flex; flex-direction: column; }
.hc-results[hidden] { display: none; }
.hc-hero.searching { z-index: 5; }
.hc-results ul { list-style: none; margin: 0; padding: 8px; overflow-y: auto; }
.hc-results li a { display: flex; flex-direction: column; gap: 3px; padding: 11px 14px; border-radius: 12px; color: var(--ink); }
.hc-results li a:hover, .hc-results li a.on { background: var(--soft); }
.hc-results li b { font-weight: 600; font-size: 1rem; } .hc-results li b mark { background: #e6e1ff; color: inherit; border-radius: 3px; padding: 0 2px; }
.hc-results li small { color: var(--muted); font-size: .82rem; }
.hc-results .hc-none { padding: 18px 18px 6px; color: var(--muted); }
.hc-ask { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 18px; border-top: 1px solid var(--line); background: #fafafa; }
.hc-ask span { font-size: .95rem; color: var(--muted); }
.hc-ask button { border: 0; border-radius: 999px; padding: .7rem 1.2rem; background: var(--brand); color: #fff; font: inherit; font-weight: 600; cursor: pointer; white-space: nowrap; }
.hc-ask-cta { margin-top: 1.25rem; color: rgba(255,255,255,.9); font-size: .98rem; }
.hc-ask-cta button { background: none; border: 0; color: #fff; font: inherit; font-weight: 700; text-decoration: underline; text-underline-offset: 3px; cursor: pointer; padding: 0; }
/* category cards */
.hc-cards { position: relative; z-index: 2; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.5rem; margin-top: -6rem; padding-bottom: 5rem; }
.hc-card { display: flex; flex-direction: column; align-items: center; text-align: center; gap: .9rem; padding: 2.75rem 2rem 2.5rem; border-radius: 22px; background: #fff;
  border: 1px solid var(--line); box-shadow: 0 18px 40px rgba(16,16,30,.08); color: var(--ink); transition: transform .25s ease, box-shadow .25s ease; }
.hc-card:hover { transform: translateY(-4px); box-shadow: 0 24px 50px rgba(68,45,250,.16); }
.hc-icon { display: grid; place-items: center; width: 84px; height: 84px; border-radius: 50%; background: var(--soft); }
.hc-icon svg { width: 46px; height: 46px; }
.hc-card h2 { font-size: 1.9rem; color: var(--brand); }
.hc-card p { margin: 0; color: var(--muted); line-height: 1.65; }
.hc-count { font-size: .85rem; font-weight: 600; color: var(--brand); }
/* category page */
.hc-page { padding: 10rem 0 5rem; }
.hc-cat-head { display: flex; gap: 1.75rem; align-items: flex-start; padding-bottom: 2.5rem; border-bottom: 1px solid var(--line); margin-bottom: 2.5rem; }
.hc-cat-head .hc-icon { width: 76px; height: 76px; flex: none; }
.hc-cat-head h1 { font-size: clamp(2.2rem, 4vw, 3.2rem); }
.hc-cat-head p { margin: .6rem 0 0; color: var(--muted); font-size: 1.15rem; line-height: 1.6; }
.hc-crumbs { display: flex; gap: .5rem; flex-wrap: wrap; font-size: .9rem; color: var(--muted); margin-bottom: 1.75rem; }
.hc-crumbs a { color: var(--brand); }
.hc-q { display: block; padding: 2rem 2.25rem; margin-bottom: 1.25rem; border: 1px solid var(--line); border-radius: 18px; background: #fff; color: var(--ink);
  box-shadow: 0 6px 18px rgba(16,16,30,.04); transition: border-color .2s ease, box-shadow .2s ease; }
.hc-q:hover { border-color: var(--brand); box-shadow: 0 14px 34px rgba(68,45,250,.12); }
.hc-q h2 { font-size: 1.6rem; color: var(--brand); margin-bottom: .6rem; }
.hc-q p { margin: 0 0 1.25rem; color: var(--muted); line-height: 1.6; }
.hc-by { display: flex; align-items: center; gap: .8rem; }
.hc-by span.av { display: grid; place-items: center; width: 44px; height: 44px; border-radius: 50%; background: var(--soft); flex: none; }
.hc-by span.av img { width: 30px; height: auto; }
.hc-by b { display: block; font-size: .98rem; color: var(--ink); }
.hc-by small { color: var(--muted); font-size: .88rem; }
/* question page */
.hc-qhero { padding-bottom: 12rem; }
.hc-qhero h1 { max-width: 880px; margin: 0 auto; font-size: clamp(2.2rem, 4.2vw, 3.4rem); }
.hc-qhero .hc-by { justify-content: center; margin-top: 2rem; text-align: left; }
.hc-qhero .hc-by b { color: #fff; } .hc-qhero .hc-by small { color: rgba(255,255,255,.8); }
.hc-qhero .hc-by span.av { background: #fff; }
.hc-article { position: relative; z-index: 2; margin: -9rem auto 5rem; padding: clamp(2rem, 5vw, 4rem); border-radius: 24px; background: #fff;
  border: 1px solid var(--line); box-shadow: 0 24px 60px rgba(16,16,30,.08); }
.hc-article h2 { font-size: clamp(1.8rem, 3vw, 2.4rem); margin: 0 0 1rem; }
.hc-article h3 { font-family: inherit !important; font-weight: 700 !important; font-size: 1.2rem; letter-spacing: 0; margin: 2.25rem 0 .8rem; }
.hc-article p { margin: 0 0 1.1rem; line-height: 1.75; color: #333; }
.hc-article a { color: var(--brand); text-decoration: underline; text-underline-offset: 3px; }
.hc-article ul { padding-left: 1.2rem; margin: 0 0 1.25rem; } .hc-article li { margin: .4rem 0; color: #333; }
.hc-figure { margin: 2rem 0 2.5rem; }
.hc-figure div { display: grid; place-items: center; aspect-ratio: 16 / 8.5; border-radius: 16px; background: var(--brand); color: rgba(255,255,255,.75); font-weight: 600; letter-spacing: .08em; text-transform: uppercase; font-size: .85rem; }
.hc-figure figcaption { margin-top: .7rem; font-size: .9rem; color: var(--muted); }
.hc-help { margin-top: 3rem; padding: 1.75rem 2rem; border-radius: 18px; background: var(--soft); display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.hc-help strong { font-family: var(--serif); font-weight: 400; font-size: 1.6rem; }
.hc-btn { display: inline-flex; align-items: center; gap: .6rem; padding: .85rem 1.5rem; border-radius: 999px; background: var(--brand); color: #fff !important; font-weight: 600; text-decoration: none !important; }
@media (max-width: 900px) { .hc-cards { grid-template-columns: minmax(0, 1fr); margin-top: -5rem; } .hc-hero { padding: 9rem 0 8rem; } }
@media (max-width: 600px) { .hc-ask { flex-direction: column; align-items: stretch; } .hc-ask button { width: 100%; } .hc-cat-head { flex-direction: column; gap: 1rem; } .hc-q { padding: 1.5rem; } .hc-search button { padding: .9rem 1.2rem; } .hc-search { padding-left: 14px; } }
</style>"""

SEARCH_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'


def search_index() -> list[dict]:
    """Help Center questions + website articles, searched live on /help-center/."""
    items = [{"t": t, "u": f"/help-center/question/{s}/", "c": "Help Center · " + dict(CATEGORIES)[c],
              "k": excerpt(REAL[s]["answer"], 300) if s in REAL else ""} for s, c, t in QUESTIONS]
    try:
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from build_news_page import blog_articles
        for a in blog_articles():
            items.append({"t": a["title"], "u": a["url"], "c": "Article · " + a["cats"][0], "k": a["desc"]})
    except Exception as exc:  # noqa: BLE001 - search still works with the Help Center questions
        print(f"warning: articles not added to search: {exc}")
    return items


SEARCH_SCRIPT = """<script>
(function () {
  var IDX = %s;
  var q = document.getElementById("hc-q"), box = document.getElementById("hc-results"), ul = box.querySelector("ul"), hero = document.querySelector(".hc-hero");
  new MutationObserver(function () { if (box.hidden) hero.classList.remove("searching"); }).observe(box, { attributes: true, attributeFilter: ["hidden"] });
  var norm = function (s) { return String(s).toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, ""); };
  var esc = function (s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; };
  function mark(t, words) { var h = esc(t); words.forEach(function (w) { if (w.length > 1) h = h.replace(new RegExp("(" + w.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&") + ")", "ig"), "<mark>$1</mark>"); }); return h; }
  function search() {
    var words = norm(q.value).split(/\\s+/).filter(Boolean);
    if (!words.length) { box.hidden = true; q.setAttribute("aria-expanded", "false"); return; }
    var hits = IDX.map(function (x) {
      var hay = norm(x.t + " " + x.k + " " + x.c), title = norm(x.t), score = 0;
      for (var i = 0; i < words.length; i++) { if (hay.indexOf(words[i]) < 0) return null; score += title.indexOf(words[i]) > -1 ? 3 : 1; }
      return { x: x, s: score };
    }).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).slice(0, 8);
    ul.innerHTML = hits.length ? hits.map(function (h) { return '<li><a href="' + h.x.u + '"><b>' + mark(h.x.t, words) + '</b><small>' + esc(h.x.c) + '</small></a></li>'; }).join("")
      : '<li class="hc-none">No results for “' + esc(q.value.trim()) + '”.</li>';
    clearTimeout(missT);
    if (!hits.length) missT = setTimeout(function () { logMiss(q.value.trim()); }, 1500);
    box.hidden = false; q.setAttribute("aria-expanded", "true"); hero.classList.add("searching");
  }
  var missT, logged = {};
  function logMiss(term) {
    var k = norm(term); if (k.length < 3 || logged[k]) return; logged[k] = 1;
    fetch("https://atcitaqyraeqngcsaeun.supabase.co/rest/v1/rpc/log_help_search_miss", { method: "POST",
      headers: { "Content-Type": "application/json", apikey: "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY", Authorization: "Bearer sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY" },
      body: JSON.stringify({ q: term }) }).catch(function () {});
  }
  q.addEventListener("input", search); q.addEventListener("focus", search);
  document.getElementById("hc-form").addEventListener("submit", function (e) { e.preventDefault(); search(); var a = ul.querySelector("a"); if (a && !box.hidden) a.focus(); });
  document.addEventListener("click", function (e) { if (!e.target.closest(".hc-search-box")) box.hidden = true; });
  q.addEventListener("keydown", function (e) { if (e.key === "Escape") box.hidden = true; if (e.key === "ArrowDown") { var a = ul.querySelector("a"); if (a) { e.preventDefault(); a.focus(); } } });
  document.querySelectorAll("[data-ask]").forEach(function (b) { b.addEventListener("click", function () { box.hidden = true; if (window.OutreachHelp) window.OutreachHelp.ask("General"); }); });
})();
</script>"""


def by(q: dict | None = None) -> str:
    if not q:
        return ('<div class="hc-by"><span class="av"><img src="/assets/outreach-recruitment-logo.svg" alt=""></span>'
                '<div><b>Outreach Recruitment</b><small>Author name · Date</small></div></div>')
    from datetime import datetime
    d = datetime.fromisoformat(str(q.get("updated_at") or q.get("created_at"))[:19]).strftime("%-d %B %Y")
    return ('<div class="hc-by"><span class="av"><img src="/assets/outreach-recruitment-logo.svg" alt=""></span>'
            f'<div><b>{E(q.get("author_name") or "Outreach Recruitment")}</b><small>Updated {d}</small></div></div>')


def page(title: str, desc: str, url: str, content: str, crumbs: list[tuple[str, str]]) -> str:
    s = (ROOT / "about.html").read_text(encoding="utf-8")
    full = f"{title} | Help Center | Outreach Recruitment"
    s = re.sub(r"<title>.*?</title>", f"<title>{E(full)}</title>", s, count=1, flags=re.S)
    for attr, name, value in [("name", "description", desc), ("property", "og:description", desc), ("name", "twitter:description", desc),
                              ("property", "og:title", full), ("name", "twitter:title", full), ("property", "og:url", url)]:
        s = re.sub(rf'<meta content="[^"]*" {attr}="{re.escape(name)}"/>', f'<meta content="{E(value)}" {attr}="{name}"/>', s)
    s = re.sub(r'(<link href=")[^"]*(" rel="canonical"/>)', rf"\g<1>{url}\g<2>", s, count=1)
    if not READY:
        s = s.replace('<meta content="width=device-width, initial-scale=1" name="viewport"/>',
                      '<meta content="width=device-width, initial-scale=1" name="viewport"/>\n<meta content="noindex, follow" name="robots"/>', 1)
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + h} for i, (n, h) in enumerate(crumbs)]}
    s = re.sub(r'<script type="application/ld\+json">.*?"AboutPage".*?</script>',
               f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>', s, count=1, flags=re.S)
    s = s.replace("</head>", CSS + "\n</head>", 1)
    a = s.index('<main class="main">') + len('<main class="main">')
    b = s.index("</main>")
    s = s[:a] + f'<div class="hc">{content}</div>' + s[b:]
    s = re.sub(r'<section class="section cta">.*?</section>', "", s, count=1, flags=re.S)
    if "/assets/help-widget.js" not in s:  # the shell may already carry it (tools/add_help_widget_sitewide.py)
        s = s.replace("</body>", '<script defer src="/assets/help-widget.js?v=4"></script>\n</body>', 1)
    return s


def crumbs_html(items: list[tuple[str, str]]) -> str:
    parts = [f'<a href="{h}">{E(n)}</a>' for n, h in items[:-1]] + [f"<span>{E(items[-1][0])}</span>"]
    return '<nav class="hc-crumbs" aria-label="Breadcrumb">' + "<span>/</span>".join(parts) + "</nav>"


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main() -> None:
    faqs = load_faqs()
    for c, _ in CATEGORIES:
        real = [q for q in faqs if q.get("category") == c]
        if real:
            for q in real:
                REAL[q["slug"]] = q
                QUESTIONS.append((q["slug"], c, q["question"]))
        else:
            QUESTIONS.extend(x for x in PLACEHOLDERS if x[1] == c)
    counts = {c: sum(1 for q in QUESTIONS if q[1] == c) for c, _ in CATEGORIES}
    cards = "".join(f'<a class="hc-card" href="/help-center/{c}/"><span class="hc-icon">{ICONS[c]}</span><h2>{E(n)}</h2>'
                    f'<p>{LOREM}</p><span class="hc-count">{counts[c]} articles</span></a>' for c, n in CATEGORIES)
    home = f"""<section class="hc-hero"><div class="hc-wrap"><h1>Help Center</h1><p>Have questions? Search through our Help Center.</p>
  <div class="hc-search-box"><form class="hc-search" role="search" action="/help-center/" id="hc-form"><label for="hc-q" style="position:absolute;left:-9999px">Search</label>
    {SEARCH_ICON}<input id="hc-q" type="search" placeholder="Search for questions or topics…" autocomplete="off" aria-controls="hc-results" aria-expanded="false"><button type="submit">Search</button></form>
    <div class="hc-results" id="hc-results" hidden><ul role="listbox"></ul>
      <div class="hc-ask"><span>Can't find your question?</span><button type="button" data-ask>Ask our team</button></div></div></div>
  <p class="hc-ask-cta">Didn't find what you need? <button type="button" data-ask>Ask our team</button></p></div></section>
<div class="hc-wrap"><div class="hc-cards">{cards}</div></div>"""
    home += SEARCH_SCRIPT % json.dumps(search_index(), ensure_ascii=False)
    write("help-center/index.html", page("Help Center", "Answers to common questions about jobs in Malta, hiring staff and studying in Malta.",
                                        f"{SITE}/help-center/", home, [("Home", "/"), ("Help Center", "/help-center/")]))
    for c, name in CATEGORIES:
        qs = "".join(f'<a class="hc-q" href="/help-center/question/{s}/"><h2>{E(t)}</h2><p>{E(excerpt(REAL[s]["answer"])) if s in REAL else LOREM2}</p>{by(REAL.get(s))}</a>'
                     for s, cc, t in QUESTIONS if cc == c)
        trail = [("Home", "/"), ("Help Center", "/help-center/"), (name, f"/help-center/{c}/")]
        content = f"""<div class="hc-page"><div class="hc-narrow">{crumbs_html(trail)}
  <div class="hc-cat-head"><span class="hc-icon">{ICONS[c]}</span><div><h1>{E(name)}</h1><p>{LOREM}</p></div></div>{qs}
  <div class="hc-help"><strong>Can't find your answer?</strong><a class="hc-btn" href="#help-chat" data-topic="{E(name)}">Ask our team</a></div></div></div>"""
        write(f"help-center/{c}/index.html", page(name, f"{name} — questions and answers from Outreach Recruitment.", f"{SITE}/help-center/{c}/", content, trail))
    for s, c, t in QUESTIONS:
        name = dict(CATEGORIES)[c]
        trail = [("Home", "/"), ("Help Center", "/help-center/"), (name, f"/help-center/{c}/"), (t, f"/help-center/question/{s}/")]
        if s in REAL:
            q = REAL[s]
            body = (md(q["answer"]) + f'<div class="hc-help"><strong>Still need help?</strong><a class="hc-btn" href="#help-chat" data-topic="{E(name)}">Ask our team</a></div>')
            content = f"""<section class="hc-hero hc-qhero"><div class="hc-wrap"><h1>{E(t)}</h1><p>{E(excerpt(q["answer"], 200))}</p>{by(q)}</div></section>
<div class="hc-narrow"><article class="hc-article">{crumbs_html(trail)}{body}</article></div>"""
            write(f"help-center/question/{s}/index.html", page(t, excerpt(q["answer"], 155), f"{SITE}/help-center/question/{s}/", content, trail))
            continue
        body = f"""<h2>Section heading</h2><p>{LOREM2} <a href="/jobs/">Example link</a>, neque. Viverra purus pretium elementum tincidunt mollis.</p>
<p>{LOREM2}</p><figure class="hc-figure"><div>Image</div><figcaption>Image caption.</figcaption></figure>
<h2>Section heading</h2><p>{LOREM2}</p><h3>Sub heading</h3><p>{LOREM2}</p>
<ul><li>List item</li><li>List item</li><li>List item</li><li>List item</li></ul>
<h3>Sub heading</h3><p>{LOREM2}</p><figure class="hc-figure"><div>Image</div><figcaption>Image caption.</figcaption></figure>
<h2>Section heading</h2><p>{LOREM2}</p>
<div class="hc-help"><strong>Still need help?</strong><a class="hc-btn" href="#help-chat" data-topic="{E(name)}">Ask our team</a></div>"""
        content = f"""<section class="hc-hero hc-qhero"><div class="hc-wrap"><h1>{E(t)}</h1><p>{LOREM2}</p>{by()}</div></section>
<div class="hc-narrow"><article class="hc-article">{crumbs_html(trail)}{body}</article></div>"""
        write(f"help-center/question/{s}/index.html", page(t, LOREM2, f"{SITE}/help-center/question/{s}/", content, trail))
    # Remove pages of questions that no longer exist (placeholders replaced by real questions, or unpublished).
    import shutil
    keep = {s for s, _, _ in QUESTIONS}
    for d in (ROOT / "help-center" / "question").iterdir():
        if d.is_dir() and d.name not in keep:
            shutil.rmtree(d)
    print(f"help center: 1 home, {len(CATEGORIES)} categories, {len(QUESTIONS)} questions ({len(REAL)} published, "
          f"{'indexable' if READY else 'noindex'})")


if __name__ == "__main__":
    main()
