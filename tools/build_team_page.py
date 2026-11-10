#!/usr/bin/env python3
"""
build_team_page.py — build /our-team ("Meet Our Team") from tools/team_data.json.

Uses about.html as the shell (same header, footer, menus, scripts and site styles) and replaces
the page content with: hero heading, a featured CEO card, a grid of team cards (photo, name, role;
on hover the photo darkens and social icons slide up — like the reference "team-1" section),
and a profile dialog opened by clicking any card (photo, name, role, bio, email, socials).

While "ready" is false in the data file the page is noindex (placeholders must not be indexed).

Usage: python3 tools/build_team_page.py
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tools" / "team_data.json"
OUT = ROOT / "our-team.html"
SITE = "https://outreachrecruitment.net"
URL = f"{SITE}/our-team"
E = lambda s: html.escape(str(s or ""), quote=True)

ICONS = {
    "linkedin": ('LinkedIn', '<path d="M6.94 8.5H3.56V20h3.38V8.5ZM5.25 3A1.97 1.97 0 1 0 5.3 7a1.97 1.97 0 0 0-.05-4ZM20.44 13.4c0-3.1-1.65-5.15-4.4-5.15a3.83 3.83 0 0 0-3.44 1.9V8.5H9.37c.04.93 0 11.5 0 11.5h3.23v-6.42c0-.34.03-.69.13-.93.28-.69.9-1.4 1.95-1.4 1.38 0 1.93 1.05 1.93 2.6V20h3.23z" fill="currentColor"/>'),
    "facebook": ('Facebook', '<path d="M14 8.5V6.8c0-.8.5-1 1-1h2V2.5h-2.8C11.1 2.5 10.5 4.8 10.5 6.3v2.2H8.5V12h2v9.5H14V12h2.6l.4-3.5z" fill="currentColor"/>'),
    "instagram": ('Instagram', '<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/>'),
    "x": ('X', '<path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.3l4.4 5.8zm-1.1 16.2h1.7L7.4 4.7H5.6z" fill="currentColor"/>'),
}
# Used when a person has no personal social links yet: their icons point to the company's pages.
COMPANY_SOCIALS = {"linkedin": "https://www.linkedin.com/company/outreach-recruitment-agency/",
                   "facebook": "https://www.facebook.com/outreachrecruit/",
                   "instagram": "https://www.instagram.com/outreachrecruitment_agency",
                   "x": "https://x.com/OutreachRecrt"}
EMAIL_ICON = '<path d="M3 5.5h18v13H3z M3.5 6l8.5 7 8.5-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>'


# Which networks to show (others stay in the data for later), and the shared contact email.
SHOW_SOCIALS = ["linkedin"]
DEFAULT_EMAIL = "hr@outreachrecruitment.net"


def email_of(person: dict) -> str:
    return person.get("email") or DEFAULT_EMAIL


def socials_html(person: dict, cls: str) -> str:
    items = []
    own = {k: v for k, v in (person.get("socials") or {}).items() if v and v != "#"}
    links = own or COMPANY_SOCIALS
    for key, (label, path) in ICONS.items():
        url = links.get(key, "") if key in SHOW_SOCIALS else ""
        if url:
            who = E(person["name"]) if own else "Outreach Recruitment"
            items.append(f'<li><a class="{cls}-link" href="{E(url)}" target="_blank" rel="noopener" aria-label="{who} on {label}">'
                         f'<svg viewBox="0 0 24 24" aria-hidden="true">{path}</svg></a></li>')
    mail = email_of(person)
    items.append(f'<li><a class="{cls}-link" href="mailto:{E(mail)}" aria-label="Email {E(person["name"])} ({E(mail)})" title="{E(mail)}">'
                 f'<svg viewBox="0 0 24 24" aria-hidden="true">{EMAIL_ICON}</svg></a></li>')
    return f'<ul class="{cls}" role="list">{"".join(items)}</ul>'


def pos_style(person: dict) -> str:
    """Optional "photo_position" (e.g. "center 55%") moves the face up/down inside the crop."""
    pos = person.get("photo_position")
    return f' style="object-position: {E(pos)}"' if pos else ""


def card(person: dict, idx: int) -> str:
    return f"""<article class="team-card" data-member="{idx}">
  <button class="team-card-open" type="button" aria-label="View profile of {E(person['name'])}" data-open="{idx}"></button>
  <div class="team-img-wrap"><img class="team-img" src="{E(person['photo'])}" alt="{E(person['name'])}, {E(person['role'])} at Outreach Recruitment" loading="lazy" width="413" height="367"{pos_style(person)}></div>
  <div class="team-card-body"><h3 class="team-name">{E(person['name'])}</h3>
    <div class="team-card-foot">{socials_html(person, 'card-social')}<button class="team-view-btn" type="button" data-open="{idx}">View profile</button></div></div>
</article>"""


CSS = """<style id="team-page-style">
.team-page { padding-bottom: 6rem; }
.team-hero { text-align: center; max-width: 760px; margin: 0 auto; padding: 2rem 0 3rem; }
.team-hero .team-sub { font-size: 1.1rem; opacity: .8; margin-top: 1rem; }
/* CEO */
.ceo-card { position: relative; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 0; background: #f6f6f6;
  border-radius: 24px; overflow: hidden; margin: 0 auto 4rem; max-width: 880px; transition: box-shadow .35s ease; }
.ceo-card:hover { box-shadow: 0 18px 40px rgba(22, 22, 22, .1); }
.ceo-card .team-img-wrap { aspect-ratio: 4 / 4.4; border-radius: 0; }
.ceo-body { padding: clamp(1.75rem, 4vw, 3.5rem); display: flex; flex-direction: column; justify-content: center; align-items: flex-start; gap: 1.25rem; }
.ceo-eyebrow { display: inline-flex; width: fit-content; font-size: .78rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  color: #442DFA; background: #eeebff; padding: .35rem .8rem; border-radius: 999px; }
.ceo-name { font-size: clamp(1.8rem, 3.4vw, 2.6rem); line-height: 1.1; margin: 0; }
.ceo-role { font-weight: 600; opacity: .75; margin: 0; }
.ceo-bio { line-height: 1.65; margin: 0; }
.ceo-quote { border-left: 3px solid #442DFA; padding-left: 1rem; font-style: italic; margin: .5rem 0 0; }
.ceo-actions { display: flex; gap: .75rem; flex-wrap: wrap; margin-top: .5rem; }
.ceo-btn { display: inline-flex; align-items: center; gap: .4rem; border-radius: 999px; padding: .7rem 1.2rem; font-weight: 600;
  border: 1px solid #161616; background: transparent; color: inherit; cursor: pointer; font: inherit; text-decoration: none; }
.ceo-btn.primary { background: #442DFA; border-color: #442DFA; color: #fff; }
/* Grid + cards (reference style: rounded card, photo on top, grey panel, hover overlay with socials) */
.team-section-title { text-align: center; margin: 0 0 2.5rem; }
.team-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.25rem 1.25rem; }
.team-card { position: relative; background: #f6f6f6; border-radius: 24px; overflow: hidden; transition: transform .35s ease, box-shadow .35s ease; }
.team-card:hover { transform: translateY(-4px); box-shadow: 0 18px 40px rgba(22, 22, 22, .1); }
.team-card-open { position: absolute; inset: 0; z-index: 2; width: 100%; height: 100%; border: 0; background: transparent; cursor: pointer; }
.team-card-open:focus-visible { outline: 3px solid #442DFA; outline-offset: -3px; border-radius: 24px; }
.team-img-wrap { position: relative; aspect-ratio: 413 / 367; overflow: hidden; background: #eeebff; }
.team-img { width: 100%; height: 100%; object-fit: cover; object-position: center 25%; display: block; transition: transform .6s ease; }
.team-img-wrap::after { content: ""; position: absolute; inset: 0; background: rgba(16, 16, 30, .38); opacity: 0; transition: opacity .35s ease; }
.team-card:hover .team-img, .ceo-card:hover .team-img { transform: scale(1.04); }
.team-card:hover .team-img-wrap::after, .ceo-card:hover .team-img-wrap::after { opacity: 1; }
.team-social { position: absolute; left: 0; right: 0; bottom: 1.25rem; z-index: 3; display: flex; justify-content: center; gap: .5rem;
  margin: 0; padding: 0; list-style: none; opacity: 0; transform: translateY(24px); transition: opacity .35s ease, transform .35s ease; }
.team-card:hover .team-social, .ceo-card:hover .team-social, .team-card:focus-within .team-social { opacity: 1; transform: translateY(0); }
.team-social-link { display: grid; place-items: center; width: 40px; height: 40px; border-radius: 50%; color: #fff;
  background: rgba(255, 255, 255, .18); backdrop-filter: blur(6px); transition: background .2s ease; }
.team-social-link:hover { background: #442DFA; }
.team-social-link svg { width: 18px; height: 18px; }
.team-card-body { padding: 1.25rem 1.25rem 1.4rem; }
.team-name { font-size: 1.2rem; margin: 0 0 .35rem; }
.team-role { margin: 0; font-size: .95rem; opacity: .75; }
.team-card-body { display: flex; flex-direction: column; gap: 1rem; }
.team-card-foot { display: flex; align-items: center; justify-content: space-between; gap: .75rem; flex-wrap: wrap; }
.card-social { display: flex; gap: .4rem; margin: 0; padding: 0; list-style: none; position: relative; z-index: 3; }
.card-social-link { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; border: 1px solid #dcdcdc;
  color: #161616; background: #fff; transition: background .2s ease, color .2s ease, border-color .2s ease; }
.card-social-link:hover, .card-social-link:focus-visible { background: #442DFA; border-color: #442DFA; color: #fff; }
.card-social-link svg { width: 16px; height: 16px; }
.team-view-btn { position: relative; z-index: 3; border: 0; border-radius: 999px; padding: .6rem 1.1rem; font: inherit; font-weight: 600;
  font-size: .9rem; background: #442DFA; color: #fff; cursor: pointer; transition: background .2s ease; }
.team-view-btn:hover { background: #2f1bd6; }
.ceo-body .card-social-link { width: 42px; height: 42px; }
.ceo-body .card-social-link svg { width: 18px; height: 18px; }
@media (max-width: 400px) { .team-card-foot { flex-direction: column; align-items: flex-start; } }
.team-lead { display: flex; justify-content: center; margin-bottom: 4rem; }
.team-lead .team-card { width: calc((100% - 2.5rem) / 3); }
@media (max-width: 991px) { .team-lead .team-card { width: calc((100% - 1.25rem) / 2); } }
@media (max-width: 600px) { .team-lead .team-card { width: 100%; } }
/* Profile dialog */
.team-dialog { border: 0; border-radius: 24px; padding: 0; width: min(880px, calc(100vw - 32px)); max-height: calc(100vh - 48px); }
.team-dialog::backdrop { background: rgba(16, 16, 30, .55); }
.team-dialog-inner { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 3fr); }
.team-dialog-photo { width: 100%; height: 100%; min-height: 320px; object-fit: cover; object-position: center 25%; display: block; background: #eeebff; }
.team-dialog-body { padding: 2rem 2rem 2.25rem; display: flex; flex-direction: column; gap: .75rem; overflow-y: auto; }
.team-dialog-close { position: absolute; top: .9rem; right: .9rem; width: 40px; height: 40px; border-radius: 50%; border: 0; z-index: 2;
  background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,.15); font-size: 1.3rem; cursor: pointer; }
.team-dialog-socials { display: flex; gap: .5rem; flex-wrap: wrap; margin: .5rem 0 0; padding: 0; list-style: none; }
.team-dialog-socials-link { display: grid; place-items: center; width: 40px; height: 40px; border-radius: 50%; border: 1px solid #ddd; color: #161616; }
.team-dialog-socials-link:hover { background: #442DFA; border-color: #442DFA; color: #fff; }
.team-dialog-socials-link svg { width: 18px; height: 18px; }
@media (max-width: 991px) { .team-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .ceo-card { grid-template-columns: minmax(0, 1fr); max-width: 560px; } .ceo-card .team-img-wrap { aspect-ratio: 1 / 1; } }
@media (max-width: 600px) { .team-grid { grid-template-columns: minmax(0, 1fr); } .team-dialog-inner { grid-template-columns: minmax(0, 1fr); }
  .team-dialog-photo { min-height: 0; aspect-ratio: 1; } }
/* Touch screens have no hover: show the social icons all the time */
@media (hover: none) { .team-social { opacity: 1; transform: none; } .team-img-wrap::after { opacity: .25; } }
</style>"""

SCRIPT = """<script id="team-page-script">
(function () {
  var data = window.__TEAM__ || [];
  var dlg = document.getElementById('team-dialog');
  if (!dlg || !dlg.showModal) return;
  var lastFocus = null;
  function open(i) {
    var p = data[i]; if (!p) return;
    lastFocus = document.activeElement;
    dlg.querySelector('.team-dialog-photo').src = p.photo;
    dlg.querySelector('.team-dialog-photo').alt = p.name;
    dlg.querySelector('.team-dialog-photo').style.objectPosition = p.pos || '';
    dlg.querySelector('.team-dialog-name').textContent = p.name;
    dlg.querySelector('.team-dialog-role').textContent = p.role;
    dlg.querySelector('.team-dialog-bio').textContent = p.bio || '';
    var q = dlg.querySelector('.team-dialog-quote'); q.textContent = p.quote || ''; q.hidden = !p.quote;
    var mail = dlg.querySelector('.team-dialog-email');
    if (p.email) { mail.href = 'mailto:' + p.email; mail.textContent = p.email; mail.hidden = false; } else { mail.hidden = true; }
    dlg.querySelector('.team-dialog-socials').innerHTML = p.socialsHtml || '';
    dlg.showModal();
  }
  document.querySelectorAll('[data-open]').forEach(function (b) {
    b.addEventListener('click', function () { open(+b.getAttribute('data-open')); });
  });
  dlg.querySelector('.team-dialog-close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', function () { if (lastFocus) lastFocus.focus(); });
})();
</script>"""


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    ceo, members = d["ceo"], d["members"]
    people = [ceo] + members
    s = (ROOT / "about.html").read_text(encoding="utf-8")

    title = "Meet Our Team | Outreach Recruitment Agency Malta"
    desc = ("Meet the Outreach Recruitment team in Malta — the recruitment specialists who connect employers with "
            "the right people and help candidates find their next job.")
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1, flags=re.S)
    def meta(attr, name, value):
        nonlocal s
        s = re.sub(rf'<meta content="[^"]*" {attr}="{re.escape(name)}"/>', f'<meta content="{E(value)}" {attr}="{name}"/>', s)
    meta("name", "description", desc); meta("property", "og:description", desc); meta("name", "twitter:description", desc)
    meta("property", "og:title", title); meta("name", "twitter:title", title); meta("property", "og:url", URL)
    s = re.sub(r'(<link href=")[^"]*(" rel="canonical"/>)', rf"\g<1>{URL}\g<2>", s, count=1)
    s = s.replace('<meta content="width=device-width, initial-scale=1" name="viewport"/>',
                  '<meta content="width=device-width, initial-scale=1" name="viewport"/>'
                  + ("" if d.get("ready") else '\n<meta content="noindex, follow" name="robots"/>'), 1)

    # Structured data: breadcrumb always; team members only once the real details are in.
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "About Us", "item": f"{SITE}/about"},
        {"@type": "ListItem", "position": 3, "name": "Our Team", "item": URL}]}]
    if d.get("ready"):
        ld.append({"@context": "https://schema.org", "@type": "AboutPage", "url": URL, "name": title,
                   "mainEntity": {"@type": "Organization", "name": "Outreach Recruitment Ltd", "url": SITE,
                                  "employee": [{"@type": "Person", "name": p["name"], "jobTitle": p["role"],
                                                "image": SITE + p["photo"] if p["photo"].startswith("/") else p["photo"]}
                                               for p in people]}})
    s = re.sub(r'<script type="application/ld\+json">.*?"AboutPage".*?</script>',
               "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld),
               s, count=1, flags=re.S)
    s = s.replace("</head>", CSS + "\n</head>", 1)

    ceo_html = f'<div class="team-lead">{card(ceo, 0)}</div>'
    grid = "\n".join(card(m, i + 1) for i, m in enumerate(members))
    content = f"""
<section class="section team-page">
  <div class="w-layout-blockcontainer container w-container">
    <div class="team-hero" data-gsap-scroll="text">
      <h1 class="heading-h1">{E(d['page']['title'])}</h1>
      <p class="team-sub">{E(d['page']['subtitle'])}</p>
    </div>
    {ceo_html}
    <h2 class="heading-h3 team-section-title">The people behind Outreach Recruitment</h2>
    <div class="team-grid">
{grid}
    </div>
  </div>
</section>
<dialog class="team-dialog" id="team-dialog" aria-labelledby="team-dialog-name">
  <button class="team-dialog-close" type="button" aria-label="Close profile">×</button>
  <div class="team-dialog-inner">
    <img class="team-dialog-photo" src="" alt="">
    <div class="team-dialog-body">
      <h2 class="heading-h4 team-dialog-name" id="team-dialog-name"></h2>
      <p class="team-dialog-role ceo-role"></p>
      <p class="team-dialog-bio ceo-bio"></p>
      <blockquote class="team-dialog-quote ceo-quote" hidden></blockquote>
      <a class="team-dialog-email" href="#" hidden></a>
      <ul class="team-dialog-socials" role="list"></ul>
    </div>
  </div>
</dialog>
"""
    a = s.index('<main class="main">') + len('<main class="main">')
    b = s.index("</main>")
    inner = s[a:b]
    cta = re.search(r'<section class="section cta">.*?</section>', inner, re.S)
    s = s[:a] + content + (cta.group(0) if cta else "") + s[b:]

    payload = [{"name": p["name"], "role": p["role"], "photo": p["photo"], "bio": p.get("bio", ""), "quote": p.get("quote", ""),
                "email": email_of(p), "pos": p.get("photo_position", ""), "socialsHtml": socials_html(p, "team-dialog-socials").replace('<ul class="team-dialog-socials" role="list">', "").replace("</ul>", "")}
               for p in people]
    s = s.replace("</body>", f"<script>window.__TEAM__ = {json.dumps(payload, ensure_ascii=False)};</script>\n{SCRIPT}\n</body>", 1)
    OUT.write_text(s, encoding="utf-8")
    print(f"our-team.html written ({len(people)} people; {'indexable' if d.get('ready') else 'noindex — placeholders'})")


if __name__ == "__main__":
    main()
