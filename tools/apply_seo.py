from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = ""
OG_IMAGE = "https://cdn.prod.website-files.com/6996b31b0e199fa8510adf4f/69e5e8d53dca7cbcd9f6ca7f_20dff26555483fbbd4aa10f583ca8f37_OG.jpg"

INDEXABLE_SKIP = {
    "+442081336421.html",
    "+48223071842.html",
    "+48918862418.html",
    "401.html",
    "404.html",
    "hi@108.supply.html",
    "legal.html",
    "licenses.html",
    "style-guide.html",
    "help.html",
}

PAGE_META = {
    "index.html": {
        "title": "Jobs in Malta for EU Candidates | Outreach Recruitment",
        "description": "Find jobs in Malta and jobs in Europe with Outreach Recruitment. Trusted support for EU candidates ready to apply or send a CV.",
        "h1": "Jobs in Malta for EU Candidates",
        "focus": "home",
    },
    "home-b.html": {
        "title": "Jobs in Europe for EU Candidates | Outreach Recruitment",
        "description": "Explore jobs in Europe with recruitment support for EU candidates seeking reliable employers, career options, and relocation-friendly roles.",
        "h1": "Jobs in Europe for EU Candidates",
        "focus": "home",
    },
    "home-c.html": {
        "title": "Work in Malta and Europe | Outreach Recruitment",
        "description": "Apply for job opportunities in Malta and across Europe. Outreach Recruitment connects EU candidates with trusted employers.",
        "h1": "Work in Malta and Europe",
        "focus": "home",
    },
    "careers.html": {
        "title": "Jobs in Malta and Europe | Apply Now",
        "description": "Browse current jobs in Malta and jobs in Europe. Register your CV with Outreach Recruitment and apply for EU candidate vacancies.",
        "h1": "Jobs in Malta and Jobs in Europe",
        "focus": "jobs",
    },
    "about.html": {
        "title": "About Outreach Recruitment | Jobs in Malta",
        "description": "Learn how Outreach Recruitment supports EU candidates and employers with jobs in Malta, jobs in Europe, and trusted hiring advice.",
        "h1": "About Outreach Recruitment",
        "focus": "about",
    },
    "service.html": {
        "title": "Recruitment Agency Malta | EU Talent Hiring",
        "description": "Outreach Recruitment helps employers hire EU candidates for jobs in Malta and Europe with clear sourcing and recruitment support.",
        "h1": "Recruitment Agency Malta for EU Talent",
        "focus": "employers",
    },
    "contact-a.html": {
        "title": "Contact for Jobs in Malta | Outreach Recruitment",
        "description": "Contact Outreach Recruitment to ask about jobs in Malta, jobs in Europe, candidate registration, or EU recruitment services.",
        "h1": "Contact Outreach Recruitment",
        "focus": "contact",
    },
    "contact-b.html": {
        "title": "Send Your CV for Jobs in Malta",
        "description": "Send your CV to Outreach Recruitment for jobs in Malta and Europe. Candidate support for EU job seekers ready to apply.",
        "h1": "Send Your CV for Jobs in Malta",
        "focus": "contact",
    },
    "contact-c.html": {
        "title": "Recruitment Support for EU Candidates",
        "description": "Speak with Outreach Recruitment about EU candidate jobs, Malta vacancies, and job opportunities across Europe.",
        "h1": "Recruitment Support for EU Candidates",
        "focus": "contact",
    },
    "book-a-call.html": {
        "title": "Register for Jobs in Malta and Europe",
        "description": "Register as a candidate and let Outreach Recruitment help you apply for jobs in Malta and Europe with trusted recruitment support.",
        "h1": "Register for Jobs in Malta and Europe",
        "focus": "register",
    },
    "blog.html": {
        "title": "Jobs in Malta and Europe Career Advice",
        "description": "Career advice for EU candidates looking for jobs in Malta and jobs in Europe, from CV preparation to interview support.",
        "h1": "Career Advice for Jobs in Malta and Europe",
        "focus": "blog",
    },
    "clients-a.html": {
        "title": "Hiring in Malta and Europe | Employers",
        "description": "See how Outreach Recruitment supports employers hiring in Malta and Europe with reliable EU candidates and recruitment services.",
        "h1": "Hiring in Malta and Europe",
        "focus": "employers",
    },
    "clients-b.html": {
        "title": "EU Candidate Recruitment for Employers",
        "description": "Recruit EU candidates for jobs in Malta and Europe with Outreach Recruitment's practical sourcing and employer support.",
        "h1": "EU Candidate Recruitment for Employers",
        "focus": "employers",
    },
    "clients-c.html": {
        "title": "Recruitment Results in Malta and Europe",
        "description": "Outreach Recruitment helps employers connect with EU candidates for Malta jobs, Europe jobs, and long-term hiring needs.",
        "h1": "Recruitment Results in Malta and Europe",
        "focus": "employers",
    },
    "401.html": {
        "title": "Access Restricted | Outreach Recruitment",
        "description": "This Outreach Recruitment page is restricted. Visit the homepage to explore jobs in Malta and jobs in Europe.",
        "h1": "Access Restricted",
        "focus": "utility",
    },
    "404.html": {
        "title": "Page Not Found | Outreach Recruitment",
        "description": "This page could not be found. Return to Outreach Recruitment to explore jobs in Malta and jobs in Europe.",
        "h1": "Page Not Found",
        "focus": "utility",
    },
    "legal.html": {
        "title": "Legal Information | Outreach Recruitment",
        "description": "Legal information for Outreach Recruitment, supporting candidates and employers with jobs in Malta and jobs in Europe.",
        "h1": "Legal Information",
        "focus": "utility",
    },
    "licenses.html": {
        "title": "Licenses | Outreach Recruitment",
        "description": "Licenses and asset information for the Outreach Recruitment website for jobs in Malta and Europe.",
        "h1": "Licenses",
        "focus": "utility",
    },
    "style-guide.html": {
        "title": "Style Guide | Outreach Recruitment",
        "description": "Style guide for the Outreach Recruitment website, focused on jobs in Malta and jobs in Europe.",
        "h1": "Style Guide",
        "focus": "utility",
    },
    "help.html": {
        "title": "Help | Outreach Recruitment",
        "description": "Get help using Outreach Recruitment to find jobs in Malta, jobs in Europe, or employer recruitment support.",
        "h1": "Help",
        "focus": "utility",
    },
}

JOB_META = {
    "jobs/product-designer.html": ("Product Designer", "Warsaw, Poland", "Design"),
    "jobs/project-manager.html": ("Project Manager", "Berlin, Germany", "Project Management"),
    "jobs/people-connector.html": ("People Connector", "Szczecin, Poland", "Recruitment"),
    "jobs/barista.html": ("Barista", "Stargard, Poland", "Hospitality"),
    "jobs/ai-research-scientist.html": ("AI Research Scientist", "Warsaw, Poland", "Technology"),
}

BLOG_TITLES = {
    "blog/how-structure-quietly-builds-trust-inside-a-team-long-before-anyone-talks-about-culture.html": "How Structure Builds Trust for EU Job Seekers",
    "blog/the-invisible-architecture-behind-teams-that-move-fast-without-constantly-realigning.html": "How Strong Teams Help EU Candidates Succeed",
    "blog/why-most-teams-dont-have-a-performance-problem-but-a-structure-problem.html": "Why Clear Roles Matter in European Jobs",
    "blog/why-the-absence-of-clear-roles-slowly-erodes-confidence-across-even-the-most-talented-teams.html": "Clear Roles for Jobs in Europe",
    "blog/how-decision-clarity-removes-more-friction-than-motivation-ever-will.html": "Decision Clarity for Work in Europe",
}

CLIENT_TITLES = {
    "clients/modulabs.html": "Recruitment Case Study for Malta Hiring",
    "clients/nothing.html": "European Hiring Case Study",
    "clients/evermind.html": "EU Candidate Hiring Case Study",
    "clients/hollow.html": "Scaling Hiring in Malta and Europe",
    "clients/nerdstack.html": "Technology Recruitment in Europe",
    "clients/haldenmiller.html": "Employer Recruitment Support in Europe",
}

FOCUS_COPY = {
    "home": {
        "heading": "Find jobs in Malta with trusted recruitment support",
        "body": "Outreach Recruitment connects EU candidates with employers offering jobs in Malta and jobs in Europe. Browse current vacancies, send your CV, and get practical support for your next move.",
        "links": [("/careers", "Explore jobs in Europe"), ("/book-a-call", "Register as a candidate"), ("/contact-a", "Contact recruitment support")],
    },
    "jobs": {
        "heading": "Apply for current vacancies in Malta and across Europe",
        "body": "Search job opportunities in Malta and Europe, including roles suitable for EU candidates. Register your CV so Outreach Recruitment can match your experience with reliable employers.",
        "links": [("/jobs/product-designer", "View a job detail page"), ("/book-a-call", "Send your CV"), ("/contact-a", "Ask about Malta jobs")],
    },
    "job": {
        "heading": "Apply for this role with Outreach Recruitment",
        "body": "This opportunity is part of our jobs in Europe network for EU candidates. If the role fits your experience, send your CV and our recruitment team will guide the next steps.",
        "links": [("/careers", "See all jobs"), ("/book-a-call", "Apply for jobs in Malta"), ("/contact-a", "Ask a recruiter")],
    },
    "about": {
        "heading": "Recruitment support for EU candidates and employers",
        "body": "Outreach Recruitment understands the Malta job market and European hiring needs. We help candidates find work in Malta and Europe while supporting employers looking for reliable EU talent.",
        "links": [("/careers", "Browse jobs"), ("/service", "Employer recruitment services"), ("/contact-a", "Contact the team")],
    },
    "contact": {
        "heading": "Speak to us about jobs in Malta and Europe",
        "body": "Contact Outreach Recruitment if you want to apply for jobs in Malta, explore jobs in Europe, register your CV, or ask about recruitment for EU candidates.",
        "links": [("/careers", "View current vacancies"), ("/book-a-call", "Register your CV"), ("/service", "Hiring support")],
    },
    "register": {
        "heading": "Register your CV for Malta and Europe jobs",
        "body": "EU candidates can register with Outreach Recruitment to hear about suitable vacancies, receive application guidance, and apply for jobs in Malta and across Europe.",
        "links": [("/careers", "Explore jobs"), ("/contact-a", "Contact recruitment support"), ("/about", "About Outreach Recruitment")],
    },
    "employers": {
        "heading": "Hire EU candidates for jobs in Malta and Europe",
        "body": "Outreach Recruitment helps employers source, assess, and connect with reliable EU candidates for vacancies in Malta and across Europe.",
        "links": [("/careers", "Candidate job board"), ("/about", "About our agency"), ("/contact-a", "Discuss hiring")],
    },
    "blog": {
        "heading": "Career guidance for EU candidates",
        "body": "Read practical advice for candidates applying for jobs in Malta and jobs in Europe, including role clarity, interview preparation, and choosing reliable employers.",
        "links": [("/careers", "Browse jobs in Malta"), ("/book-a-call", "Register your CV"), ("/contact-a", "Ask for support")],
    },
}


def path_to_url(rel: str) -> str:
    slug = rel[:-5] if rel.endswith(".html") else rel
    if slug == "index":
        return "/"
    return f"/{slug}"


def metadata_for(rel: str, original_title: str) -> dict[str, str]:
    if rel in PAGE_META:
        return PAGE_META[rel]
    if rel in JOB_META:
        title, location, industry = JOB_META[rel]
        return {
            "title": f"{title} Jobs in Europe | Outreach Recruitment",
            "description": f"Apply for {title} jobs in Europe with Outreach Recruitment. {industry} opportunity for EU candidates in {location}.",
            "h1": f"{title} Jobs in Europe",
            "focus": "job",
        }
    if rel in BLOG_TITLES:
        title = BLOG_TITLES[rel]
        return {
            "title": title[:58],
            "description": "Career advice for EU candidates looking for jobs in Malta and jobs in Europe with trusted recruitment support.",
            "h1": title,
            "focus": "blog",
        }
    if rel in CLIENT_TITLES:
        title = CLIENT_TITLES[rel]
        return {
            "title": title[:58],
            "description": "Employer recruitment insight for hiring EU candidates and filling jobs in Malta and across Europe.",
            "h1": title,
            "focus": "employers",
        }
    stem = Path(rel).stem.replace("-", " ").title()
    return {
        "title": f"{stem} | Outreach Recruitment",
        "description": "Outreach Recruitment connects EU candidates with jobs in Malta and jobs in Europe through trusted recruitment support.",
        "h1": stem,
        "focus": "home",
    }


def schema_for(rel: str, meta: dict[str, str]) -> dict:
    url = path_to_url(rel)
    org = {
        "@type": "Organization",
        "name": "Outreach Recruitment",
        "url": "/",
        "description": "Recruitment agency helping EU candidates find jobs in Malta and jobs in Europe.",
        "areaServed": ["Malta", "Europe", "European Union"],
        "knowsAbout": [
            "jobs in Malta",
            "Jobs in Europe",
            "recruitment agency Malta",
            "EU candidates jobs",
        ],
    }
    breadcrumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
            {"@type": "ListItem", "position": 2, "name": meta["h1"], "item": url},
        ],
    }
    if rel in JOB_META:
        job_title, location, industry = JOB_META[rel]
        country = location.split(", ")[-1] if ", " in location else location
        return {
            "@context": "https://schema.org",
            "@graph": [
                org,
                breadcrumbs,
                {
                    "@type": "JobPosting",
                    "title": job_title,
                    "description": f"{job_title} opportunity for EU candidates looking for jobs in Europe. Apply through Outreach Recruitment for trusted recruitment support.",
                    "datePosted": "2026-05-06",
                    "employmentType": "FULL_TIME",
                    "industry": industry,
                    "hiringOrganization": org,
                    "applicantLocationRequirements": {"@type": "Country", "name": "European Union"},
                    "jobLocation": {
                        "@type": "Place",
                        "address": {
                            "@type": "PostalAddress",
                            "addressLocality": location,
                            "addressCountry": country,
                        },
                    },
                    "url": url,
                },
            ],
        }
    page_type = {
        "about": "AboutPage",
        "contact": "ContactPage",
        "register": "RegisterAction",
        "blog": "Blog",
    }.get(meta["focus"], "WebPage")
    graph = [org, breadcrumbs]
    graph.append(
        {
            "@type": page_type if page_type != "RegisterAction" else "WebPage",
            "name": meta["title"],
            "description": meta["description"],
            "url": url,
            "inLanguage": "en",
            "publisher": org,
            "about": ["jobs in Malta", "Jobs in Europe", "EU candidates", "recruitment agency Malta"],
        }
    )
    if rel == "index.html":
        graph.append(
            {
                "@type": "WebSite",
                "name": "Outreach Recruitment",
                "url": "/",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": "/careers?search={search_term_string}",
                    "query-input": "required name=search_term_string",
                },
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def seo_section(meta: dict[str, str]) -> str:
    copy = FOCUS_COPY.get(meta["focus"], FOCUS_COPY["home"])
    links = "".join(f'<a class="button-secondary w-inline-block" href="{href}"><div class="button-label">{label}</div></a>' for href, label in copy["links"])
    return (
        '<section class="section outreach-seo" data-seo="jobs-malta-europe">'
        '<div class="w-layout-blockcontainer container w-container">'
        '<div class="w-layout-vflex section-content">'
        '<div class="w-layout-vflex text center narrow">'
        f'<h2 class="heading-h3">{html.escape(copy["heading"])}</h2>'
        f'<p class="text-medium">{html.escape(copy["body"])}</p>'
        '</div>'
        f'<div class="w-layout-vflex buttons">{links}</div>'
        '</div>'
        '</div>'
        '</section>'
    )


def replace_head(text: str, rel: str, meta: dict[str, str]) -> str:
    title = html.escape(meta["title"])
    desc = html.escape(meta["description"])
    url = path_to_url(rel)
    noindex = rel in INDEXABLE_SKIP
    text = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", text, count=1, flags=re.S)
    seo_meta = [
        f'<meta content="{desc}" name="description"/>',
        f'<meta content="{title}" property="og:title"/>',
        f'<meta content="{desc}" property="og:description"/>',
        f'<meta content="{OG_IMAGE}" property="og:image"/>',
        f'<meta content="{title}" name="twitter:title"/>',
        f'<meta content="{desc}" name="twitter:description"/>',
        f'<meta content="{OG_IMAGE}" name="twitter:image"/>',
        '<meta content="website" property="og:type"/>',
        '<meta content="summary_large_image" name="twitter:card"/>',
        f'<link href="{url}" rel="canonical"/>',
        f'<meta content="{url}" property="og:url"/>',
        '<meta content="Outreach Recruitment" property="og:site_name"/>',
        '<meta content="index, follow" name="robots"/>' if not noindex else '<meta content="noindex, follow" name="robots"/>',
    ]
    targets = [
        r'<meta [^>]*(?:name|property)="description"[^>]*/>',
        r'<meta [^>]*(?:name|property)="og:title"[^>]*/>',
        r'<meta [^>]*(?:name|property)="og:description"[^>]*/>',
        r'<meta [^>]*(?:name|property)="og:image"[^>]*/>',
        r'<meta [^>]*(?:name|property)="twitter:title"[^>]*/>',
        r'<meta [^>]*(?:name|property)="twitter:description"[^>]*/>',
        r'<meta [^>]*(?:name|property)="twitter:image"[^>]*/>',
        r'<meta [^>]*(?:name|property)="og:type"[^>]*/>',
        r'<meta [^>]*(?:name|property)="twitter:card"[^>]*/>',
        r'<link [^>]*rel="canonical"[^>]*/>',
        r'<meta [^>]*(?:name|property)="og:url"[^>]*/>',
        r'<meta [^>]*(?:name|property)="og:site_name"[^>]*/>',
        r'<meta [^>]*(?:name|property)="robots"[^>]*/>',
    ]
    for pattern in targets:
        text = re.sub(pattern, "", text, flags=re.S)
    text = re.sub(r"(</title>)", r"\1" + "".join(seo_meta), text, count=1)
    schema = json.dumps(schema_for(rel, meta), indent=2)
    text = re.sub(r'<script type="application/ld\+json">\s*.*?\s*</script>', f'<script type="application/ld+json">\n{schema}\n</script>', text, count=1, flags=re.S)
    return text


def apply_visible_copy(text: str, meta: dict[str, str], rel: str) -> str:
    h1 = html.escape(meta["h1"])
    text = re.sub(r'<h1 class="heading-h1">.*?</h1>', f'<h1 class="heading-h1">{h1}</h1>', text, count=1, flags=re.S)
    text = re.sub(r'<h1 class="heading-h2">.*?</h1>', f'<h1 class="heading-h2">{h1}</h1>', text, count=1, flags=re.S)
    text = text.replace("People Work™", "Outreach Recruitment")
    text = text.replace("People Work", "Outreach Recruitment")
    text = text.replace("Get Template", "Send your CV")
    text = text.replace("Get template", "Send your CV")
    text = text.replace("Visit help", "Contact us")
    text = text.replace("Start your <br/>dream career", "Find jobs in<br/>Malta & Europe")
    text = text.replace("Home A", "Home")
    text = text.replace("Home B", "Jobs in Malta")
    text = text.replace("Home C", "Jobs in Europe")
    text = text.replace("Careers", "Jobs")
    text = text.replace("Book a call", "Register CV")
    text = text.replace("Book a Call", "Register CV")
    text = text.replace("Job Offer (CMS)", "Job Details")
    text = text.replace("Blog (CMS)", "Career Advice")
    text = re.sub(r'alt=""', f'alt="{html.escape(meta["h1"])} - Outreach Recruitment jobs in Malta and Europe"', text)
    if rel in INDEXABLE_SKIP:
        text = re.sub(r'<section class="section outreach-seo" data-seo="jobs-malta-europe">.*?</section>', "", text, flags=re.S)
    elif 'data-seo="jobs-malta-europe"' not in text:
        if "</main>" in text:
            text = text.replace("</main>", seo_section(meta) + "</main>", 1)
        else:
            text = text.replace("</body>", seo_section(meta) + "</body>", 1)
    return text


def main() -> None:
    html_files = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("jobs/*.html")) + sorted(ROOT.glob("blog/*.html")) + sorted(ROOT.glob("clients/*.html"))
    urls = []
    for path in html_files:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text()
        original_title_match = re.search(r"<title>(.*?)</title>", text, flags=re.S)
        original_title = original_title_match.group(1) if original_title_match else rel
        meta = metadata_for(rel, original_title)
        text = replace_head(text, rel, meta)
        text = apply_visible_copy(text, meta, rel)
        path.write_text(text)
        if rel not in INDEXABLE_SKIP:
            urls.append(path_to_url(rel))

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sorted(set(urls)):
        priority = "1.0" if url == "/" else "0.8"
        sitemap.append(f"  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n")
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n")


if __name__ == "__main__":
    main()
