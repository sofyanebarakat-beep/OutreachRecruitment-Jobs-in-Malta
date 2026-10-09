"""Build customer-service-jobs-in-malta(.html + /index.html) from the hospitality hub template.
Edit JOBS / FAQS / guide text here and re-run: python3 tools/build_customer_service_hub.py"""
import json, re, sys, html as H
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
SRC = ROOT / "hospitality-jobs-in-malta.html"
SLUG = "customer-service-jobs-in-malta"
URL = f"https://outreachrecruitment.net/{SLUG}"
IMG = "https://outreachrecruitment.net/assets/customer-service-malta-call-centre-hero.webp"
TITLE = "Customer Service Jobs in Malta | Call Centre & Call Agent Jobs"
H1 = "Customer Service Jobs in Malta"
DESC = ("Customer service jobs in Malta: call centre, call agent and service client roles in Floriana. "
        "Salaries from &euro;19,000. EU nationals. Apply online today.")
INTRO = ("Call centre, call agent and customer contact roles in Floriana, Malta &mdash; for English speakers "
         "with Italian, French or Arabic. Apply directly through Outreach Recruitment.")

LANGS = "Good English plus Italian, French or Arabic"
ELIGIBLE = "EU nationals only"
JOBS = [
    dict(slug="customer-contact-agent", title="Customer Contact Agent",
         cat="Insurance", date="2026-06-09", salary="&euro;19,000&ndash;&euro;22,000",
         target=ELIGIBLE, langs="English + French, English + Italian, or English + Arabic + French",
         hours="40-hour week, rotating shifts incl. weekends",
         summary=("Be the first point of contact for insured customers who need help while abroad &mdash; "
                  "handling calls, emails and online channels, opening cases and explaining procedures with empathy.")),
    dict(slug="administration-specialist", title="Administration Specialist",
         cat="Administration", date="2026-07-01", salary="&euro;40,000&ndash;&euro;50,000",
         target=ELIGIBLE, langs=LANGS,
         hours="Office-based or hybrid",
         summary=("Support medical claims operations, cost containment and case management for a healthcare "
                  "and insurance assistance team &mdash; including SAP invoice processing, reporting and KPIs.")),
    dict(slug="assistance-operations-coordinator", title="Assistance Operations Coordinator",
         cat="Insurance", date="2026-09-02", salary="&euro;19,200&ndash;&euro;20,000",
         target=ELIGIBLE, langs=LANGS,
         hours="24/7 shift rota incl. weekends and nights",
         summary=("Take roadside, motor and home assistance requests by phone and digital channels, dispatch "
                  "the right contractor and stay with each case until the customer is looked after.")),
]
NOTICE = "Due to the urgent hiring requirements for these positions, only EU nationals will be considered."
SUBTITLE = "Good communication skills in English and at least one additional language: Italian, French, or Arabic."

ARROW = ('<svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M5 12H19M19 12L12 5M19 '
         '12L12 19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
         'stroke-width="var(--_⚡️-icons---icon-stroke)"></path></svg>')

FAQS = [
    ("What is a call center service client job in Malta?",
     "A call center service client job (customer service in a call centre) means helping customers by phone, email and chat &mdash; answering questions, opening and following up cases, and solving problems. In Malta these roles are common in insurance and assistance companies serving customers across Europe. Our current openings in Floriana are for candidates with good English plus Italian, French or Arabic."),
    ("What customer service jobs in Malta are open right now?",
     "We are currently recruiting for three customer service roles in Floriana, Malta: Customer Contact Agent, "
     "Administration Specialist and Assistance Operations Coordinator. All three are full-time direct jobs with our clients."),
    ("How much do customer service and call centre jobs in Malta pay?",
     "Salary ranges are: Customer Contact Agent &euro;19,000&ndash;&euro;22,000, Administration Specialist "
     "&euro;40,000&ndash;&euro;50,000, and Assistance Operations Coordinator &euro;19,200&ndash;&euro;20,000 per year. You can estimate take-home pay with our <a href=\"/salary-calculator-malta\">Malta Salary Calculator</a>."),
    ("Which languages do I need for these customer service jobs?",
     "Good communication skills in English and at least one additional language: Italian, French, or Arabic. "
     "Maltese is not required. The Customer Contact Agent role needs English plus French, English plus Italian, "
     "or English, Arabic and French."),
    ("Do I need previous call centre experience?",
     "Not always. Previous experience in customer service, a contact centre, insurance, hospitality or retail is an "
     "asset, and the Customer Contact Agent and Assistance Operations Coordinator roles include training.  The Administration Specialist role does require experience in insurance, healthcare "
     "administration or medical claims."),
    ("What are the working hours for call agent jobs in Malta?",
     "The Customer Contact Agent role is a 40-hour week on a rotating shift pattern that includes weekends and public "
     "holidays. The Assistance Operations Coordinator role runs on a 24/7 rota, including weekends and night shifts. "
     "Check each listing for the exact schedule."),
    ("Is remote or hybrid work available?",
     "Some roles offer it. The Assistance Operations Coordinator role offers two remote days per week after three "
     "months, and the Administration Specialist role is office-based or hybrid."),
    ("Who can apply for these positions?",
     "Due to the urgent hiring requirements for these positions, only EU nationals will be considered."),
    ("Where are these customer service jobs located?",
     "All three roles are based in Floriana, just outside Valletta's main gate, with a major bus interchange on the "
     "doorstep &mdash; practical for shift workers travelling at all hours."),
    ("How do I apply for customer service jobs in Malta?",
     "Click the role that fits your profile and apply online through the listing. Our recruitment team reviews every "
     "application and will contact you within a few working days to discuss next steps."),
    ("Need more information?",
     "Our team is happy to help. Reach out to us directly:<br><br><strong>Email:</strong> "
     "<a href=\"mailto:hr@outreachrecruitment.net\">hr@outreachrecruitment.net</a>"),
]

def card(j):
    data_title = H.escape(f"{j['title']} floriana, malta".lower())
    return (f'<article class="opening-job-card opening-job-card--centered" data-opening-job="" data-featured="true" '
            f'data-latest="true" data-title="{data_title}" data-category="{j["cat"]}" data-location="floriana, malta" '
            f'data-date="{j["date"]}"><a class="opening-job-link" href="/jobs/{j["slug"]}"><div class="opening-card-day">New</div>'
            f'<img class="opening-job-logo" src="/assets/job-card-logo.jpg" alt="Outreach Recruitment job logo"/>'
            f'<h3 class="heading-h5">{j["title"]}</h3><div class="opening-job-company">Floriana, Malta</div>'
            f'<div class="opening-job-meta"><span>Full-Time</span><span>{j["cat"]}</span><span>Salary Range: {j["salary"]}</span></div></a></article>')

def faq_item(q, a, tpl_item):
    return tpl_item.replace("@@Q@@", q).replace("@@A@@", a)

def plain(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", s))).strip()

t = SRC.read_text()

# ---------- JSON-LD ----------
ld_page = {
    "@context": "https://schema.org", "@type": "CollectionPage", "name": plain(TITLE), "headline": H1, "description": plain(DESC), "url": URL,
    "inLanguage": "en", "datePublished": "2026-10-07", "dateModified": "2026-10-07",
    "keywords": "customer service jobs in Malta, call centre jobs in Malta, call center service client in Malta, call agent jobs in Malta, contact centre jobs Malta, customer care jobs Malta",
    "primaryImageOfPage": {"@type": "ImageObject", "url": IMG, "width": 1800, "height": 2400},
    "isPartOf": {"@type": "WebSite", "name": "Outreach Recruitment", "url": "https://outreachrecruitment.net/"},
    "about": {"@type": "Organization", "name": "Outreach Recruitment", "url": "https://outreachrecruitment.net",
              "description": "Outreach Recruitment is a Malta-based recruitment agency connecting qualified candidates with leading employers across customer service, insurance, hospitality and other sectors.",
              "areaServed": "Malta", "serviceType": "Recruitment Agency"},
    "mainEntity": {"@type": "ItemList", "name": "Open Customer Service & Call Centre Jobs in Malta",
                   "description": "Current customer service, call centre and call agent vacancies in Malta placed through Outreach Recruitment.",
                   "numberOfItems": len(JOBS),
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": plain(j["title"]),
                                        "url": f"https://outreachrecruitment.net/jobs/{j['slug']}"} for i, j in enumerate(JOBS)]},
}
ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://outreachrecruitment.net/"},
    {"@type": "ListItem", "position": 2, "name": "Jobs in Malta", "item": "https://outreachrecruitment.net/jobs"},
    {"@type": "ListItem", "position": 3, "name": H1, "item": URL}]}
ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in FAQS]}
ld_html = "".join(f'<script type="application/ld+json">\n{json.dumps(x, indent=2, ensure_ascii=False)}\n</script>'
                  for x in (ld_page, ld_bc, ld_faq))
lds = list(re.finditer(r'<script type="application/ld\+json">.*?</script>', t, re.S))
assert len(lds) == 3, len(lds)
for m in reversed(lds[1:]):
    t = t[:m.start()] + t[m.end():]
m = lds[0]
t = t[:m.start()] + ld_html + t[m.end():]

# ---------- head meta ----------
old_title = "Hospitality Jobs in Malta | Outreach Recruitment"
old_desc = "Browse open hospitality jobs in Malta. Find hotel, restaurant, chef, bartender and F&amp;B vacancies across Malta and apply through Outreach Recruitment today."
assert t.count(old_desc) == 3 and t.count(f"<title>{old_title}</title>") == 1
t = t.replace(old_desc, DESC)
t = t.replace(f"<title>{old_title}</title>", f"<title>{H.escape(TITLE)}</title>")
t = t.replace(f'content="{old_title}"', f'content="{H.escape(TITLE)}"')
t = t.replace('data-wf-page="hospitality-jobs-in-malta"', f'data-wf-page="{SLUG}"')
t = t.replace("https://outreachrecruitment.net/assets/jobs-malta-hospitality.webp", IMG)
t = t.replace('https://outreachrecruitment.net/hospitality-jobs-in-malta/" rel="canonical"', f'{URL}" rel="canonical"')
t = t.replace('content="https://outreachrecruitment.net/hospitality-jobs-in-malta/" property="og:url"', f'content="{URL}" property="og:url"')

t = t.replace('content="https://outreachrecruitment.net/assets/og-preview.jpg" property="og:image"', f'content="{IMG}" property="og:image"')
t = t.replace('<meta content="website" property="og:type"/>', '<meta content="website" property="og:type"/><meta content="Call agent with headset in a customer service call centre in Malta" property="og:image:alt"/><meta content="' + IMG + '" name="twitter:image"/>', 1)
# ---------- hero ----------
t = t.replace('alt="Hospitality jobs in Malta" class="media-fill"', 'alt="Call agent with headset working in a customer service call centre in Malta" class="media-fill"')
t = t.replace('<h1 class="heading-h1">Hospitality Jobs in Malta</h1>', f'<h1 class="heading-h1">{H1}</h1>')

# ---------- page speed: responsive LCP hero, visible before JS ----------
B = "https://outreachrecruitment.net/assets/customer-service-malta-call-centre-hero"
SRCSET = f"{B}-600.webp 600w, {B}-900.webp 900w, {B}-1200.webp 1200w"
SIZES = "(max-width: 767px) 100vw, 50vw"
old_pre = f'<link rel="preload" as="image" href="{IMG}" fetchpriority="high"/>'
assert old_pre in t
t = t.replace(old_pre, f'<link rel="preload" as="image" href="{B}-900.webp" imagesrcset="{SRCSET}" imagesizes="{SIZES}" fetchpriority="high"/>')
old_img = f'class="media-fill" fetchpriority="high" sizes="100vw" src="{IMG}">'
assert old_img in t
t = t.replace(old_img, f'class="media-fill" fetchpriority="high" decoding="async" width="1200" height="1600" '
                       f'sizes="{SIZES}" srcset="{SRCSET}" src="{B}-900.webp">')
t = t.replace("</head>", '<style id="lcp-hero-visible">html.w-mod-js:not(.w-mod-ix3) .hero-2 img.media-fill'
                         '{visibility:visible !important}</style></head>', 1)
old_intro = re.search(r'(<h1 class="heading-h1">[^<]*</h1><div class="text-medium" role="group">)(.*?)(</div>)', t, re.S)
t = t[:old_intro.start(2)] + INTRO + t[old_intro.end(2):]

# ---------- main sections: jobs grid, FAQ, guide, popular searches ----------
s_jobs = t.index('<section class="section padding-top-large" id="top-jobs">')
s_faq = t.index('<section class="section padding-top-large">', s_jobs + 10)
s_guide = t.index('<section class="section padding-top-large" aria-labelledby="hospitality-jobs-malta-guide">')
main_end = t.index('</main>')

jobs_tpl = t[s_jobs:s_faq]
grid_start = jobs_tpl.index('<div class="opening-jobs-centered-grid"')
grid_open_end = jobs_tpl.index('>', grid_start) + 1
jobs_html = (jobs_tpl[:grid_open_end].replace('<h2 class="heading-h2">Open Positions</h2>',
                                              '<h2 class="heading-h2">Call Centre &amp; Call Agent Jobs in Malta &mdash; Hiring Now</h2>'
                                              f'<p class="cs-eu-notice">{NOTICE}</p><p class="cs-lang-subtitle">{SUBTITLE}</p>')
             + "".join(card(j) for j in JOBS) + '</div></div></div></div></section></div>')

faq_tpl = t[s_faq:s_guide]
first_item = re.search(r'<div class="faq-item">.*?</p></div></div></div>', faq_tpl, re.S).group(0)
item_tpl = re.sub(r'(<h3 class="text-large strong">).*?(</h3>)', r'\1@@Q@@\2', first_item, flags=re.S)
item_tpl = re.sub(r'(<p class="text-medium">).*?(</p>)', r'\1@@A@@\2', item_tpl, flags=re.S)
list_start = faq_tpl.index('<div class="faq-list"')
list_open_end = faq_tpl.index('>', list_start) + 1
faq_tpl = faq_tpl.replace('Everything you need to know as a <em>candidate</em>', 'Customer Service Jobs in Malta: <em>FAQs</em>')
faq_html = (faq_tpl[:list_open_end] + "".join(faq_item(q, a, item_tpl) for q, a in FAQS)
            + '</div></div></div></section>')

role_rows = "\n".join(
    f'<li><a href="/jobs/{j["slug"]}"><strong>{j["title"]}</strong></a> &mdash; {j["summary"]} '
    f'<em>Salary:</em> {j["salary"]}. <em>Languages:</em> {j["langs"]}. <em>Hours:</em> {j["hours"]}. '
    f'<em>Who can apply:</em> {j["target"]}.</li>' for j in JOBS)

guide_html = f'''<section class="section padding-top-large" aria-labelledby="customer-service-jobs-malta-guide"><div class="w-layout-blockcontainer container tight w-container"><div class="w-layout-vflex section-content"><div class="cms-article"><div class="stack gap-07" data-gsap-scroll="stagger"><div class="w-richtext" data-gsap-scroll="stagger">

<h2 id="customer-service-jobs-malta-guide">Customer Service Jobs in Malta: The Complete Guide for Call Centre &amp; Call Agent Candidates</h2>
<p>Malta is one of Europe's busiest hubs for multilingual customer support. International insurers, assistance companies and service providers run their contact centres from the island because English is an official language and the workforce speaks many European languages. That makes <strong>customer service jobs in Malta</strong> one of the most accessible ways to start or grow a career here &mdash; whether you are a first-time call agent or an experienced contact centre professional. Outreach Recruitment places candidates directly with these employers.</p>

<h3>Open Customer Service Roles in Floriana</h3>
<p>All three roles below are full-time direct jobs with our clients in Floriana, just outside Valletta:</p>
<ul>
{role_rows}
</ul>

<h3>Customer Service Jobs in Malta at a Glance</h3>
<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;"><table style="width:100%;min-width:560px;border-collapse:collapse;font-size:15px;line-height:1.5;">
<thead><tr>{''.join(f'<th style="text-align:left;padding:10px 12px;border-bottom:2px solid #1c262333;">{h}</th>' for h in ("Role","Salary","Languages","Hours","Who can apply"))}</tr></thead>
<tbody>
{"".join(f'<tr><td style="padding:10px 12px;border-bottom:1px solid #1c26231f;"><a href="/jobs/{j["slug"]}">{j["title"]}</a></td>' + "".join(f'<td style="padding:10px 12px;border-bottom:1px solid #1c26231f;">{j[k]}</td>' for k in ("salary","langs","hours","target")) + "</tr>" for j in JOBS)}
</tbody></table></div>

<h3>Call Agent Jobs in Malta: What the Work Looks Like</h3>
<p><strong>Call agent jobs in Malta</strong> go well beyond answering the phone. In the roles we recruit for, you handle inbound calls, emails and chats, open and update cases in the company's systems, explain policy terms and procedures, and work with internal teams or external contractors to resolve each request. Many positions follow service level agreements, so accuracy, calm under pressure and clear communication matter more than a long CV. Assistance and insurance contact centres often run extended or 24/7 hours, which is why shift patterns, weekend work and shift allowances are common.</p>

<h3>Call Center Service Client in Malta for French, Italian and Arabic Speakers</h3>
<p>If you are searching for a <strong>call center service client in Malta</strong>, your languages are your biggest advantage. The Customer Contact Agent role is open to candidates fluent in English plus French, English plus Italian, or English, Arabic and French, supporting insured customers who need help while travelling abroad. Experience in customer service, travel assistance or claims handling is an asset, and students of nursing or healthcare-related courses are encouraged to apply. Not sure your level is enough? Read our guide to <a href="/blog/language-requirements-customer-service-jobs-malta">language requirements for customer service jobs</a>.</p>
<p lang="fr"><em>Vous cherchez un poste en service client ou en centre d'appels &agrave; Malte&nbsp;? Si vous parlez couramment fran&ccedil;ais et anglais, postulez en ligne pour le poste de Customer Contact Agent &agrave; Floriana. Lisez notre <a href="/blog/emploi-centre-appels-malte-francophones">guide pour travailler dans un centre d'appels &agrave; Malte</a>.</em></p>

<p lang="it"><em>Cerchi lavoro a Malta in un call center o nel servizio clienti? Se parli fluentemente italiano e inglese, candidati online per il ruolo di Customer Contact Agent a Floriana. Leggi la nostra <a href="/blog/lavoro-call-center-malta-italiani">guida al lavoro nei call center a Malta</a>.</em></p>

<h3>Customer Care &amp; Contact Centre Jobs in Malta</h3>
<p><strong>Customer care jobs in Malta</strong> and <strong>contact centre jobs</strong> are concentrated in insurance, travel assistance and roadside assistance &mdash; services that support customers across Europe from a single Maltese hub. The roles on this page cover the full range: inbound call handling and case creation (Customer Contact Agent), claims administration (Administration Specialist), and dispatch and contractor coordination on a 24/7 operations floor (Assistance Operations Coordinator).</p>

<h3>Administration &amp; Back Office Jobs Behind the Contact Centre</h3>
<p>Not every customer service career is on the phones. The Administration Specialist role supports the team behind the scenes &mdash; medical claims administration, SAP invoice processing, cost containment, case management and KPI reporting. It suits candidates with a degree in healthcare or business administration (or nursing) and experience in insurance, medical claims or TPA services, and offers hybrid working.</p>

<h3>Customer Service Jobs in Malta Salary: What to Expect</h3>
<p>Salaries depend on the role, languages and shift pattern. On this page the salary ranges are <strong>&euro;19,000&ndash;&euro;22,000</strong> for the Customer Contact Agent, <strong>&euro;40,000&ndash;&euro;50,000</strong> for the Administration Specialist and <strong>&euro;19,200&ndash;&euro;20,000</strong> for the Assistance Operations Coordinator. Across Malta's contact centres, multilingual skills, night or weekend shifts and performance bonuses are the main drivers of higher pay. Estimate your take-home pay with our <a href="/salary-calculator-malta">Malta Salary Calculator</a>, or see our full breakdown of <a href="/blog/call-centre-salary-malta">call centre salaries in Malta</a>.</p>

<h3>Skills Employers Look For</h3>
<ul>
<li><strong>Languages:</strong> good English plus at least one of Italian, French or Arabic.</li>
<li><strong>Communication and empathy:</strong> customers often call on a bad day &mdash; a breakdown, a medical issue abroad, a claim.</li>
<li><strong>Computer skills:</strong> comfort with case-management systems and Microsoft Office.</li>
<li><strong>Composure:</strong> staying organised and calm with multiple priorities and time-critical situations.</li>
<li><strong>Flexibility:</strong> willingness to work rotating shifts, including weekends where the role requires it.</li>
</ul>

<h3>How to Apply for Customer Service Jobs in Malta</h3>
<p>Choose the role that matches your languages and experience above, open the listing and apply online. Outreach Recruitment reviews every application personally, runs a short phone screen, and arranges your interview with the client &mdash; prepare with our <a href="/blog/call-centre-interview-questions-malta">call centre interview questions and sample answers</a>. Due to the urgent hiring requirements for these positions, only EU nationals will be considered. You can also browse all <a href="/jobs">jobs in Malta</a> or our <a href="/insurance-jobs-in-malta">insurance jobs in Malta</a>.</p>

</div></div></div></div></div></section>'''

keywords = ["Customer Service Jobs in Malta", "Call Center Service Client in Malta", "Call Agent Jobs in Malta",
            "Call Centre Jobs in Malta", "Call Center Jobs Malta", "Contact Centre Jobs Malta", "Customer Care Jobs in Malta",
            "Customer Support Jobs Malta", "Customer Service Representative Jobs Malta", "Customer Service Jobs Malta Salary",
            "Call Centre Salary Malta", "Call Centre Jobs Malta for Foreigners", "Customer Service Jobs Malta for EU Citizens",
            "Multilingual Jobs in Malta", "French Speaking Jobs in Malta", "Italian Speaking Jobs in Malta",
            "Arabic Speaking Jobs in Malta", "English Speaking Jobs in Malta",
            "Insurance Customer Service Jobs Malta", "Insurance Call Centre Jobs Malta", "Travel Assistance Jobs Malta",
            "Roadside Assistance Jobs Malta", "Claims Handler Jobs Malta", "Customer Contact Agent Jobs Malta",
            "Assistance Coordinator Jobs Malta", "Administration Jobs in Malta", "Back Office Jobs Malta",
            "Medical Claims Jobs Malta", "Shift Work Jobs Malta", "Night Shift Jobs Malta", "Hybrid Jobs in Malta",
            "Jobs in Floriana", "Call Centre Jobs Valletta", "Entry Level Customer Service Jobs Malta",
            "Customer Service Jobs Malta No Experience", "Service Client Malte", "Centre d'Appels Malte",
            "Emploi Service Client Malte", "Lavoro Call Center Malta", "Lavoro a Malta Servizio Clienti",
            "Apply for Customer Service Jobs in Malta", "Outreach Recruitment Customer Service Jobs"]
popular_html = ('<section class="section padding-top-small padding-bottom-small" aria-label="Related customer service job searches">'
                '<div class="w-layout-blockcontainer container w-container"><p class="text-small" style="color:#565e6d;line-height:1.9;">'
                'Popular searches: ' + ", ".join(f"<strong>{H.escape(k)}</strong>" for k in keywords) + '.</p></div></section>')

GUIDES = [  # blog cluster built by tools/build_customer_service_blog.py
    ("call-centre-salary-malta", "Call centre salary in Malta 2026", "Real published pay, shift allowances and gross vs net."),
    ("call-centre-interview-questions-malta", "Call centre interview questions", "Common questions with sample answers and the language check."),
    ("language-requirements-customer-service-jobs-malta", "Language requirements", "Which languages each role needs and what &ldquo;fluent&rdquo; means."),
    ("emploi-centre-appels-malte-francophones", "Guide pour francophones", "Travailler dans un centre d'appels &agrave; Malte (en fran&ccedil;ais)."),
    ("lavoro-call-center-malta-italiani", "Guida per italiani", "Lavorare in un call center a Malta (in italiano)."),
]
guides_html = ('<style id="cs-guides-css">.cs-guides{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;margin-top:24px}'
               '.cs-guide{display:flex;flex-direction:column;border-radius:12px;overflow:hidden;background:#fff;border:1px solid #1c26231f;color:inherit;text-decoration:none;transition:transform .15s}'
               '.cs-guide:hover{transform:translateY(-2px)}.cs-guide img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block}'
               '.cs-guide div{padding:14px 16px}.cs-guide strong{display:block;font-size:17px;margin-bottom:4px}.cs-guide span{font-size:14px;color:#565e6d;line-height:1.45}</style>'
               '<section class="section padding-top-large" aria-labelledby="customer-service-guides"><div class="w-layout-blockcontainer container w-container"><div class="w-layout-vflex section-content">'
               '<h2 class="heading-h2" id="customer-service-guides">Customer Service Career Guides</h2>'
               '<p class="text-medium">Salaries, interviews and language tips for call centre jobs in Malta.</p><div class="cs-guides">'
               + "".join(f'<a class="cs-guide" href="/blog/{s}"><img src="/assets/blog-featured/{s}.jpg" alt="{plain(t)}" loading="lazy" width="1600" height="900"/>'
                         f'<div><strong>{t}</strong><span>{d}</span></div></a>' for s, t, d in GUIDES if (ROOT / "blog" / f"{s}.html").exists())
               + '</div></div></div></section>')

t = t[:s_jobs] + jobs_html + faq_html + guide_html + guides_html + popular_html + t[main_end:]

# open positions: EU notice + language subtitle under the title, one card per row
t = t.replace("</head>", '<style id="cs-open-positions">'
    '.cs-eu-notice{display:inline-block;margin:18px auto 0;padding:10px 18px;border-radius:999px;background:#FF7A00;color:#fff;'
    'font-weight:600;font-size:15px;line-height:1.45;max-width:760px}'
    '.cs-lang-subtitle{margin:14px auto 0;color:rgba(255,255,255,.78);font-size:17px;line-height:1.5;max-width:720px}'
    '#top15-dark-frame .opening-jobs-centered-grid{grid-template-columns:1fr !important;max-width:900px;width:100%;margin-left:auto;margin-right:auto}'
    '@media (max-width:767px){.cs-eu-notice{border-radius:14px;font-size:14px}.cs-lang-subtitle{font-size:15px}'
    '#top15-dark-frame .opening-job-card--centered .opening-job-link{grid-template-columns:2.4rem 1fr;grid-template-areas:"logo title" "logo loc" "meta meta"}'
    '#top15-dark-frame .opening-job-card--centered .opening-job-meta{grid-row:auto;justify-content:flex-start;flex-wrap:wrap;margin-top:.6rem}'
    '#top15-dark-frame .opening-job-card--centered .opening-job-link::after{display:none}}'
    '</style></head>', 1)

# ---------- page speed: drop JS a listing page doesn't need ----------
# Lenis smooth scroll, SplitText, the GSAP marquee and the infinite-slider clone script.
# Keep gsap + ScrollTrigger (Webflow IX3 needs them to reveal headings) and every
# webflow.schunk (the webpack runtime stops if one chunk is missing).
for old in ('<link href="https://cdn.jsdelivr.net/npm/lenis@1.2.3/dist/lenis.css" rel="stylesheet"/>',
            '<script defer src="https://cdn.jsdelivr.net/npm/lenis@1.2.3/dist/lenis.min.js"></script>',
            '<script defer src="https://cdn.prod.website-files.com/gsap/3.15.0/SplitText.min.js" type="text/javascript"></script>'):
    assert old in t, old
    t = t.replace(old, "")
t = t.replace("gsap.registerPlugin(SplitText,ScrollTrigger)", "gsap.registerPlugin(ScrollTrigger)")
for marker in ("108™ Smooth Scroll", "GSAP Marquee", "108™ Infinite Slider"):
    m = re.search(r"<script>(?:(?!</script>).)*?" + re.escape(marker) + r".*?</script>", t, re.S)
    assert m, marker
    t = t[:m.start()] + t[m.end():]

# ---------- FAQ accordion fix (same as manufacturing hub) ----------
man = (ROOT / "manufacturing-jobs-in-malta.html").read_text()
style = re.search(r'<style id="faq-accordion-fix">.*?</style>', man, re.S).group(0)
script = re.search(r'<script>\(function\(\)\{var items=document\.querySelectorAll\("\.faq-list \.faq-item"\).*?</script>', man, re.S).group(0)
t = t.replace("</head>", style + "</head>", 1)
t = t.replace("</body>", script + "</body>", 1)

leftover = [m.start() for m in re.finditer(r"(?i)hospitality", t)]
for p in leftover:
    print("hospitality ref:", t[max(0, p - 60):p + 40].replace("\n", " "))

(ROOT / f"{SLUG}.html").write_text(t)
(ROOT / SLUG).mkdir(exist_ok=True)
(ROOT / SLUG / "index.html").write_text(t)
print("written", len(t))
