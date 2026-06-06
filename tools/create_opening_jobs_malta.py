from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "careers.html"
OUT = ROOT / "jobs" / "index.html"

TITLE_OLD = "Jobs in Malta and Europe | Apply Now"
DESC_OLD = "Browse current jobs in Malta and jobs in Europe. Register your CV with Outreach Recruitment and apply for EU candidate vacancies."
TITLE_NEW = "Opening Jobs in Malta | Outreach Recruitment"
DESC_NEW = "Search opening jobs in Malta with Outreach Recruitment. Browse featured jobs, filter roles, and apply for Malta and Europe vacancies."

JOBS = [
    {
        "title": "Barista",
        "category": "Hospitality",
        "location": "Sliema, Malta",
        "type": "Full time",
        "href": "/jobs/barista",
        "featured": True,
        "latest": False,
        "urgent": True,
        "posted": "Posted 2 days ago",
        "date": "2026-06-02",
        "eligibility": "Only residents in Malta",
    },
    {
        "title": "People Connector",
        "category": "People Ops",
        "location": "St. Julian's, Malta",
        "type": "Flexible",
        "href": "/jobs/people-connector",
        "featured": True,
        "latest": False,
        "urgent": False,
        "posted": "Posted 4 days ago",
        "date": "2026-05-31",
        "eligibility": "Residents in Malta & Europeans",
    },
    {
        "title": "Project Manager",
        "category": "Management",
        "location": "Valletta, Malta",
        "type": "Full time",
        "href": "/jobs/project-manager",
        "featured": True,
        "latest": True,
        "urgent": True,
        "posted": "New this week",
        "date": "2026-06-04",
        "eligibility": "Only for Europeans",
    },
    {
        "title": "Product Designer",
        "category": "Design",
        "location": "Mosta, Malta",
        "type": "Hybrid",
        "href": "/jobs/product-designer",
        "featured": False,
        "latest": True,
        "urgent": False,
        "posted": "Posted 1 day ago",
        "date": "2026-06-03",
        "eligibility": "Worldwide",
    },
    {
        "title": "AI Research Scientist",
        "category": "Tech",
        "location": "Birkirkara, Malta",
        "type": "Full time",
        "href": "/jobs/ai-research-scientist",
        "featured": False,
        "latest": True,
        "urgent": False,
        "posted": "New this week",
        "date": "2026-06-04",
        "eligibility": "Maltese only",
    },
]


def job_card(job: dict, index: int) -> str:
    urgency = '<span class="opening-job-badge urgent">Urgent</span>' if job["urgent"] else ""
    return f"""<article class="opening-job-card" data-opening-job data-featured="{str(job['featured']).lower()}" data-latest="{str(job['latest']).lower()}" data-title="{job['title'].lower()}" data-category="{job['category']}" data-location="{job['location'].lower()}" data-date="{job['date']}">
<a class="opening-job-link" href="{job['href']}"><div class="opening-job-layout"><div class="opening-job-main"><div class="opening-job-top"><img class="opening-job-logo" src="/assets/job-card-logo.jpg" alt="Outreach Recruitment job logo"/><span class="opening-job-badge">Easy apply</span>{urgency}</div><div class="opening-job-title-row"><h3 class="heading-h5">{job['title']}</h3></div><div class="opening-job-company">Outreach Recruitment</div><div class="opening-job-location">{job['location']}</div><div class="opening-job-meta"><span>{job['category']}</span><span>{job['type']}</span><span>{job['eligibility']}</span></div><div class="opening-job-action"><span class="button-label">Apply now</span><span class="opening-job-arrow">&rarr;</span></div></div><div class="opening-job-icons" aria-hidden="true"><svg class="opening-job-icon" fill="none" viewBox="0 0 24 24"><path d="M7 4.75h10a1.5 1.5 0 0 1 1.5 1.5v13l-6.5-3.5-6.5 3.5v-13A1.5 1.5 0 0 1 7 4.75Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.4"/></svg><svg class="opening-job-icon" fill="none" viewBox="0 0 24 24"><path d="M5.5 6.5h13a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-5.25L8.5 20.25V17.5h-3a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.4"/></svg></div></div></a>
</article>"""


def build_main() -> str:
    cards = "".join(job_card(job, i + 1) for i, job in enumerate(JOBS))
    featured_count = sum(1 for job in JOBS if job["featured"])
    latest_count = sum(1 for job in JOBS if job["latest"])
    all_count = len(JOBS)
    return f"""<main class="main"><section class="section opening-jobs-hero"><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content"><div class="w-layout-vflex text center narrow" data-gsap-scroll="text"><div class="tag">Opening jobs in Malta</div><h1 class="heading-h1">Find your next job in Malta</h1><p class="text-medium">Search trusted vacancies for EU candidates, explore featured openings, and apply with recruitment support from Outreach Recruitment.</p></div><div class="opening-filter-sticky"><div class="opening-jobs-filter" id="opening-jobs-filter" role="search" aria-label="Filter opening jobs in Malta"><div class="opening-filter-field"><label class="caption" for="opening-search">Job title or keyword</label><input class="text-field opening-filter-input" id="opening-search" placeholder="Search roles, skills, or departments" type="search" autocomplete="off"/></div><div class="opening-filter-field"><label class="caption" for="opening-category">Category</label><select class="text-field opening-filter-input" id="opening-category"><option value="">All categories</option><option value="Hospitality">Hospitality</option><option value="People Ops">People Ops</option><option value="Management">Management</option><option value="Design">Design</option><option value="Tech">Tech</option></select></div><div class="opening-filter-field"><label class="caption" for="opening-location">Location</label><input class="text-field opening-filter-input" id="opening-location" placeholder="Sliema, Valletta, Mosta..." type="search" autocomplete="off"/></div><button class="button-primary opening-filter-button" id="opening-filter-button" type="button"><span class="button-label">Clear filters</span></button></div><div class="opening-trending"><span class="caption blue-caption">Trending searches</span><button class="opening-chip" data-opening-chip="Hospitality" type="button">Hospitality</button><button class="opening-chip" data-opening-chip="People Ops" type="button">People Ops</button><button class="opening-chip" data-opening-chip="Management" type="button">Management</button><button class="opening-chip" data-opening-chip="Tech" type="button">Tech</button></div><div class="opening-location-chips" aria-label="Popular Malta locations"><span class="caption blue-caption">Locations</span><button class="opening-chip" data-opening-location="Sliema" type="button">Sliema</button><button class="opening-chip" data-opening-location="St. Julian's" type="button">St. Julian's</button><button class="opening-chip" data-opening-location="Valletta" type="button">Valletta</button><button class="opening-chip" data-opening-location="Mosta" type="button">Mosta</button><button class="opening-chip" data-opening-location="Birkirkara" type="button">Birkirkara</button></div></div></div></div></section><a class="opening-mobile-filter" href="#opening-jobs-filter">Filter jobs</a><section class="section opening-featured-jobs" id="opening-jobs-results"><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content"><div class="opening-results-bar"><div class="opening-job-tabs" aria-label="Job list tabs"><button class="opening-tab is-active" data-opening-tab="featured" type="button">Featured <span>{featured_count}</span></button><button class="opening-tab" data-opening-tab="latest" type="button">Latest <span>{latest_count}</span></button><button class="opening-tab" data-opening-tab="all" type="button">All <span>{all_count}</span></button></div></div><div class="opening-jobs-grid" id="opening-jobs-grid">{cards}</div><div class="opening-pagination" id="opening-pagination" hidden><button class="opening-page-button" id="opening-page-prev" type="button">Previous</button><div class="opening-page-numbers" id="opening-page-numbers" aria-label="Job result pages"></div><button class="opening-page-button" id="opening-page-next" type="button">Next</button></div><div class="opening-register-cv"><div><h2 class="heading-h4">Do not see the right job?</h2><p class="text-medium">Register your CV and our recruitment team will contact you when a suitable Malta vacancy opens.</p></div><a class="button-primary animated w-inline-block" href="/book-a-call"><div class="button-label">Register CV</div></a></div><div class="opening-empty" id="opening-empty" hidden><p class="text-medium">No jobs match your filter. Try another keyword.</p></div></div></div></section><section class="section opening-jobs-seo"><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content"><div class="opening-seo-grid"><div><h2 class="heading-h3">Jobs in Malta, Malta vacancies, and jobs in Europe</h2><p class="text-medium">Explore <a href="/jobs/">jobs in Malta</a>, including <a href="/jobs/?category=Hospitality">hospitality jobs Malta</a>, international <a href="/home-c">jobs in Europe</a>, and vacancies suitable for <a href="/book-a-call">EU candidates</a>. Outreach Recruitment helps candidates review current roles and register their CV for future Malta vacancies.</p></div><div class="opening-seo-list"><a href="/jobs/">jobs in Malta</a><span>Malta vacancies</span><a href="/book-a-call">EU candidates</a><a href="/jobs/?category=Hospitality">hospitality jobs Malta</a><a href="/home-c">jobs in Europe</a></div></div></div></div></section></main><script>
(function () {{
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-opening-job]'));
  var search = document.getElementById('opening-search');
  var category = document.getElementById('opening-category');
  var location = document.getElementById('opening-location');
  var empty = document.getElementById('opening-empty');
  var searchButton = document.getElementById('opening-filter-button');
  var chips = Array.prototype.slice.call(document.querySelectorAll('[data-opening-chip]'));
  var locationChips = Array.prototype.slice.call(document.querySelectorAll('[data-opening-location]'));
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-opening-tab]'));
  var pagination = document.getElementById('opening-pagination');
  var pageNumbers = document.getElementById('opening-page-numbers');
  var prevPage = document.getElementById('opening-page-prev');
  var nextPage = document.getElementById('opening-page-next');
  var pageSize = 9;
  var currentPage = 1;
  var activeTab = 'featured';
  var results = document.getElementById('opening-jobs-results');
  var hasInteracted = false;

  function applyInitialQuery() {{
    if (!window.URLSearchParams) return;
    var params = new URLSearchParams(window.location.search);
    if (params.get('category')) category.value = params.get('category');
    if (params.get('location')) location.value = params.get('location');
    if (params.get('q')) search.value = params.get('q');
    if (params.get('category') || params.get('location') || params.get('q')) activeTab = 'all';
  }}

  function nudgeToResults() {{
    if (!hasInteracted || !results) return;
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var top = results.getBoundingClientRect().top + window.pageYOffset - 84;
    window.scrollTo({{ top: top, behavior: reduceMotion ? 'auto' : 'smooth' }});
  }}

  function applyFilters() {{
    var q = (search.value || '').toLowerCase().trim();
    var cat = category.value;
    var loc = (location.value || '').toLowerCase().trim();
    var matched = cards.filter(function (card) {{
      var matchesTab = activeTab === 'all'
        || (activeTab === 'featured' && card.getAttribute('data-featured') === 'true')
        || (activeTab === 'latest' && card.getAttribute('data-latest') === 'true');
      return matchesTab
        && (!q || card.getAttribute('data-title').indexOf(q) !== -1)
        && (!cat || card.getAttribute('data-category') === cat)
        && (!loc || card.getAttribute('data-location').indexOf(loc) !== -1);
    }});

    var totalPages = Math.max(1, Math.ceil(matched.length / pageSize));
    if (currentPage > totalPages) currentPage = totalPages;
    var first = (currentPage - 1) * pageSize;
    var last = first + pageSize;

    cards.forEach(function (card) {{
      card.hidden = matched.indexOf(card) === -1 || matched.indexOf(card) < first || matched.indexOf(card) >= last;
    }});

    empty.hidden = matched.length !== 0;
    renderPagination(totalPages, matched.length);
    nudgeToResults();
  }}

  function renderPagination(totalPages, totalJobs) {{
    if (!pagination || !pageNumbers) return;
    pagination.hidden = totalJobs <= pageSize;
    pageNumbers.innerHTML = '';
    if (totalJobs <= pageSize) return;
    prevPage.disabled = currentPage === 1;
    nextPage.disabled = currentPage === totalPages;
    for (var i = 1; i <= totalPages; i += 1) {{
      var button = document.createElement('button');
      button.className = 'opening-page-number' + (i === currentPage ? ' is-active' : '');
      button.type = 'button';
      button.textContent = i;
      button.setAttribute('aria-label', 'Show page ' + i);
      button.addEventListener('click', (function (page) {{
        return function () {{
          hasInteracted = true;
          currentPage = page;
          applyFilters();
        }};
      }})(i));
      pageNumbers.appendChild(button);
    }}
  }}

  [search, category, location].forEach(function (field) {{
    field.addEventListener(field.tagName === 'SELECT' ? 'change' : 'input', function () {{
      hasInteracted = true;
      currentPage = 1;
      applyFilters();
    }});
  }});

  if (searchButton) searchButton.addEventListener('click', function () {{
    hasInteracted = true;
    search.value = '';
    category.value = '';
    location.value = '';
    currentPage = 1;
    applyFilters();
  }});
  tabs.forEach(function (tab) {{
    tab.addEventListener('click', function () {{
      hasInteracted = true;
      currentPage = 1;
      activeTab = tab.getAttribute('data-opening-tab');
      tabs.forEach(function (item) {{
        item.classList.toggle('is-active', item === tab);
      }});
      applyFilters();
    }});
  }});
  chips.forEach(function (chip) {{
    chip.addEventListener('click', function () {{
      hasInteracted = true;
      category.value = chip.getAttribute('data-opening-chip');
      currentPage = 1;
      applyFilters();
    }});
  }});
  locationChips.forEach(function (chip) {{
    chip.addEventListener('click', function () {{
      hasInteracted = true;
      location.value = chip.getAttribute('data-opening-location');
      currentPage = 1;
      applyFilters();
    }});
  }});
  if (prevPage) prevPage.addEventListener('click', function () {{
    if (currentPage === 1) return;
    hasInteracted = true;
    currentPage -= 1;
    applyFilters();
  }});
  if (nextPage) nextPage.addEventListener('click', function () {{
    hasInteracted = true;
    currentPage += 1;
    applyFilters();
  }});
  applyInitialQuery();
  if (activeTab === 'all') {{
    tabs.forEach(function (item) {{
      item.classList.toggle('is-active', item.getAttribute('data-opening-tab') === 'all');
    }});
  }}
  applyFilters();
}}());
</script>"""


def main() -> None:
    html = SOURCE.read_text()
    html = html.replace(f"<title>{TITLE_OLD}</title>", f"<title>{TITLE_NEW}</title>")
    html = html.replace(f'<meta content="{DESC_OLD}" name="description"/>', f'<meta content="{DESC_NEW}" name="description"/>')
    html = html.replace(f'<meta content="{TITLE_OLD}" property="og:title"/>', f'<meta content="{TITLE_NEW}" property="og:title"/>')
    html = html.replace(f'<meta content="{DESC_OLD}" property="og:description"/>', f'<meta content="{DESC_NEW}" property="og:description"/>')
    html = html.replace(f'<meta content="{TITLE_OLD}" name="twitter:title"/>', f'<meta content="{TITLE_NEW}" name="twitter:title"/>')
    html = html.replace(f'<meta content="{DESC_OLD}" name="twitter:description"/>', f'<meta content="{DESC_NEW}" name="twitter:description"/>')
    html = html.replace('<link href="/careers" rel="canonical"/>', '<link href="/jobs/" rel="canonical"/>')
    html = html.replace('<meta content="/careers" property="og:url"/>', '<meta content="/jobs/" property="og:url"/>')

    body_tag_start = html.index("<body")
    body_tag_end = html.index(">", body_tag_start) + 1
    main_start = html.index('<main class="main">', body_tag_end)
    footer_start = html.index('<footer class="footer"', main_start)
    scripts_start = html.index('<script crossorigin="anonymous" integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0="')

    before_body = html[:body_tag_start] + '<body class="opening-jobs-page">'
    header = html[body_tag_end:main_start]
    footer_and_scripts = html[footer_start:scripts_start] + html[scripts_start:]
    page = before_body + header + build_main() + footer_and_scripts
    page = page.replace('aria-current="page" ', "")
    page = page.replace(" w--current", "")
    page = page.replace('href="/careers"', 'href="/jobs/"')
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page)
    print(f"Created {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
