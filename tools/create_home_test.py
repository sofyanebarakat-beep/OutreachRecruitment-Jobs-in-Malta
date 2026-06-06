from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
OUT = ROOT / "home-test.html"

TITLE_OLD = "Jobs in Malta for EU Candidates | Outreach Recruitment"
DESC_OLD = "Find jobs in Malta and jobs in Europe with Outreach Recruitment. Trusted support for EU candidates ready to apply or send a CV."
TITLE_NEW = "Home Test | Outreach Recruitment"
DESC_NEW = "Home test page for Outreach Recruitment with a focused Work in Malta and Europe hero section."

ARROW_ICON = """<div class="button-rail"><div class="button-circle small accent"><div class="icon small w-embed"><svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--_⚡️-icons---icon-stroke)"></path>
</svg></div></div></div><div class="icon-button"><div class="icon small w-embed"><svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="var(--_⚡️-icons---icon-strk)"></path>
</svg></div></div>"""

HERO_SECTION = f"""<main class="main"><div class="frame"><section class="section hero-full-screen home-test-slider" aria-label="Home test hero slides">
<div class="home-test-slide is-active" data-home-test-slide="0"><div class="hero-media"><video autoplay="" class="media-fill" loop="" muted="" playsinline="" poster="https://cdn.prod.website-files.com/6996b31b0e199fa8510adf4f%2F69c68466b5d360d4ec32f751_14221326_3840_2160_30fps-main_poster.0000000.jpg" preload="metadata"><source src="/assets/videos/jobs-malta-europe.mp4" type="video/mp4"/></video></div><div class="hero-overlay"></div><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex hero-header"><div class="home-test-slide-count" data-home-test-count>01 / 03</div><div class="w-layout-vflex text center narrow"><div class="tag">Opening jobs</div><h1 class="heading-h1">Jobs in Malta<br/>and Europe</h1><div class="text-medium">Trusted roles for candidates ready to work in Malta or Europe.</div></div><div class="w-layout-vflex buttons"><a class="button-primary animated w-inline-block" href="/book-a-call"><div class="button-label" data-figma-id="12018:4671">Talk to us</div>{ARROW_ICON}</a><a class="button-secondary w-inline-block" data-wf--button-secondary--variant="large" href="/careers"><div class="button-label" data-figma-id="12018:4671">View Jobs</div></a></div></div></div></div>
<div class="home-test-slide" data-home-test-slide="1"><div class="hero-media"><video autoplay="" class="media-fill" loop="" muted="" playsinline="" poster="https://cdn.prod.website-files.com/6996b31b0e199fa8510adf4f%2F69aa7c1d4af42495de38dae0_Smiling%20Professional%20Woman_poster.0000000.jpg" preload="metadata"><source src="/assets/videos/employers-hr-solutions.mp4" type="video/mp4"/></video></div><div class="hero-overlay"></div><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex hero-header"><div class="home-test-slide-count" data-home-test-count>02 / 03</div><div class="w-layout-vflex text center narrow"><div class="tag">For employers</div><h1 class="heading-h1">Employers<br/>and HR Solutions</h1><div class="text-medium">Screened candidates and hiring support for busy HR teams.</div></div><div class="w-layout-vflex buttons"><a class="button-primary animated w-inline-block" href="/book-a-call"><div class="button-label" data-figma-id="12018:4671">Talk to us</div>{ARROW_ICON}</a><a class="button-secondary w-inline-block" data-wf--button-secondary--variant="large" href="/service"><div class="button-label" data-figma-id="12018:4671">Hire Talent</div></a></div></div></div></div>
<div class="home-test-slide" data-home-test-slide="2"><div class="hero-media"><video autoplay="" class="media-fill" loop="" muted="" playsinline="" poster="https://cdn.prod.website-files.com/6996b31b0e199fa8510adf4f%2F69c67c4d6b2a4c2ddad5d6e6_Radiant%20Smile%20Close-Up_poster.0000000.jpg" preload="metadata"><source src="/assets/videos/study-in-malta.mp4" type="video/mp4"/></video></div><div class="hero-overlay"></div><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex hero-header"><div class="home-test-slide-count" data-home-test-count>03 / 03</div><div class="w-layout-vflex text center narrow"><div class="tag">Study in Malta</div><h1 class="heading-h1">Study<br/>in Malta</h1><div class="text-medium">Guidance for students planning their next step in Malta.</div></div><div class="w-layout-vflex buttons"><a class="button-primary animated w-inline-block" href="/book-a-call"><div class="button-label" data-figma-id="12018:4671">Talk to us</div>{ARROW_ICON}</a><a class="button-secondary w-inline-block" data-wf--button-secondary--variant="large" href="/contact-a"><div class="button-label" data-figma-id="12018:4671">Study Options</div></a></div></div></div></div>
<button aria-label="Previous slide" class="home-test-slide-arrow prev" data-home-test-prev type="button">‹</button><button aria-label="Next slide" class="home-test-slide-arrow next" data-home-test-next type="button">›</button>
<div class="home-test-slide-nav" aria-label="Hero slide controls"><button aria-label="Show jobs slide" class="home-test-slide-dot is-active" data-home-test-dot="0" type="button"></button><button aria-label="Show employers slide" class="home-test-slide-dot" data-home-test-dot="1" type="button"></button><button aria-label="Show study slide" class="home-test-slide-dot" data-home-test-dot="2" type="button"></button></div>
</section></div>__SPOTLIGHT_SECTION__<section class="section home-test-seo"><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content"><div class="w-layout-vflex text center narrow"><h2 class="heading-h3">Recruitment, jobs, and study support in Malta and Europe</h2><p class="text-medium">Outreach Recruitment supports candidates searching for jobs in Malta and Jobs in Europe, employers looking for HR solutions and reliable talent, and students exploring study in Malta opportunities.</p></div><div class="w-layout-vflex buttons"><a class="button-secondary w-inline-block" href="/careers"><div class="button-label">Jobs in Malta</div></a><a class="button-secondary w-inline-block" href="/service"><div class="button-label">Employer HR Solutions</div></a><a class="button-secondary w-inline-block" href="/contact-a"><div class="button-label">Study in Malta</div></a></div></div></div></section></main><script>
(function () {{
  var slides = Array.prototype.slice.call(document.querySelectorAll('[data-home-test-slide]'));
  var dots = Array.prototype.slice.call(document.querySelectorAll('[data-home-test-dot]'));
  var prev = document.querySelector('[data-home-test-prev]');
  var next = document.querySelector('[data-home-test-next]');
  var index = 0;
  function showSlide(next) {{
    index = next;
    slides.forEach(function (slide, i) {{ slide.classList.toggle('is-active', i === index); }});
    dots.forEach(function (dot, i) {{ dot.classList.toggle('is-active', i === index); }});
  }}
  function step(direction) {{
    showSlide((index + direction + slides.length) % slides.length);
  }}
  dots.forEach(function (dot) {{
    dot.addEventListener('click', function () {{
      showSlide(parseInt(dot.getAttribute('data-home-test-dot'), 10));
    }});
  }});
  if (prev) prev.addEventListener('click', function () {{ step(-1); }});
  if (next) next.addEventListener('click', function () {{ step(1); }});
  if (slides.length > 1) {{
    setInterval(function () {{ showSlide((index + 1) % slides.length); }}, 12000);
  }}
}}());
</script>"""


def slice_between(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def extract_service_spotlight(html: str, main_start: int) -> str:
    start = html.index('<div class="frame"><section class="section padding-top-large">', main_start)
    end = html.index('</section></div>', start) + len('</section></div>')
    section = html[start:end]
    return section.replace(
        "Designed for companies beyond the startup phase",
        "Recruitment support for candidates and employers",
    ).replace(
        "Designed for <em>beyond</em> companies the startup phase",
        "Recruitment support for candidates and employers",
    )


def main() -> None:
    html = INDEX.read_text()
    html = html.replace(TITLE_OLD, TITLE_NEW)
    html = html.replace(DESC_OLD, DESC_NEW)
    html = html.replace('<link href="/" rel="canonical"/>', '<link href="/home-test" rel="canonical"/>')
    html = html.replace('<meta content="/" property="og:url"/>', '<meta content="/home-test" property="og:url"/>')
    html = html.replace('"url": "/"', '"url": "/home-test"', 1)
    html = html.replace('"name": "Jobs in Malta for EU Candidates | Outreach Recruitment"', f'"name": "{TITLE_NEW}"')
    html = html.replace(f'"description": "{DESC_OLD}"', f'"description": "{DESC_NEW}"')

    body_start = html.index("<body>")
    nav_start = html.index('<div class="navigation w-nav"', body_start)
    main_start = html.index('<main class="main">', nav_start)
    spotlight_section = extract_service_spotlight(html, main_start)
    header = html[body_start + len("<body>"):main_start]

    footer_start = html.index('<footer class="footer"', main_start)
    footer_end = html.index("</footer>", footer_start) + len("</footer>")
    footer = html[footer_start:footer_end]

    scripts_start = html.index('<script crossorigin="anonymous" integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0="')
    scripts = html[scripts_start:]

    before_body = html[:body_start] + '<body class="home-test-page">'
    page = before_body + header + HERO_SECTION.replace("__SPOTLIGHT_SECTION__", spotlight_section) + footer + scripts
    page = page.replace('aria-current="page" ', "")
    page = page.replace(" w--current", "")
    page = page.replace('<a class="navigation-link" href="/">Home</a>', '<a class="navigation-link" href="/">Home</a>')
    OUT.write_text(page)
    print(f"Created {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
