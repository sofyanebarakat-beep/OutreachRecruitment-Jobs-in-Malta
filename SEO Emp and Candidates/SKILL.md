---
name: employer-candidate-seo-generator
description: Generate and audit SEO-optimized, AI-search-friendly content packages for Outreach Recruitment across five content pillars — Employers, Candidates, Jobs in Malta (job market), Study in Malta (international students), and Brand (company trust content). Use when creating or improving employer service pages, recruitment landing pages, candidate career guides, job market/industry content, study-in-Malta content, brand/company pages, meta tags, FAQs, schema recommendations, internal links, SEO audits, content refreshes, or conversion copy for Outreach Recruitment audiences.
---

# Employer and Candidate SEO Generator

## Overview

Create complete SEO content packages for Outreach Recruitment pages that target one of five content pillars:

- Employers looking for recruitment, staffing, HR, talent acquisition, or hiring support in Malta.
- Candidates looking for jobs, career guidance, applications, interviews, relocation, or work opportunities in Malta.
- Jobs in Malta: job-market and industry content that funnels traffic into the live jobs board (`/jobs/`) and category hubs, distinct from Candidate application/career guidance.
- Study in Malta: content for international students considering studying in Malta.
- Brand: company-story and trust content about Outreach Recruitment Ltd itself.

Use this skill for service pages, landing pages, blog articles, guides, FAQ hubs, category pages, and conversion-focused SEO content.

## Required Inputs

Collect or infer the following from the user request:

- Page or article topic
- Target audience/pillar: `Employers`, `Candidates`, `Jobs in Malta`, `Study in Malta`, `Brand`, or `Both` (Employers + Candidates)
- Primary keyword
- Secondary keywords
- Page type: service page, landing page, blog article, guide, FAQ page, category page, or comparison page
- Target location, usually Malta
- Conversion goal
- Preferred CTA, if provided

If important details are missing, make a reasonable assumption from the topic. If the assumption affects claims, mark the item as `Not specified` and keep copy factual.

## Core Website Context

Brand: Outreach Recruitment Ltd

Website: `https://outreachrecruitment.net/`

Primary audiences:

- Employers in Malta that need reliable recruitment support, faster hiring, better shortlists, and reduced hiring friction.
- Candidates seeking jobs in Malta, career opportunities, application guidance, and support from a recruitment agency.

Use clear, professional English. Keep copy practical, trustworthy, and specific to recruitment in Malta.

## Mandatory Internal Links

Use links naturally in the body copy where relevant. Do not force every link into every page if it does not match the audience or intent.

| Link Purpose | URL | Best Use |
|---|---|---|
| Jobs in Malta | `https://outreachrecruitment.net/jobs/` | Candidate pages, job search guides, job category pages |
| Employers page | `https://outreachrecruitment.net/employers.html` | Employer pages, recruitment service pages, hiring guides |
| Contact page | `https://outreachrecruitment.net/contact-us.html` | Employer enquiries and general conversion CTAs |
| Careers page | `https://outreachrecruitment.net/careers.html` | Candidate guidance and career support pages |
| People Connector | `https://outreachrecruitment.net/jobs/people-connector.html` | Candidate registration or general application intent |
| Study in Malta guide | `https://outreachrecruitment.net/study-in-malta` | Study in Malta pillar content |
| Study in Malta apply | `https://apply.outreachstudy.eu/` | Study in Malta pillar CTAs |
| About page | `https://outreachrecruitment.net/about.html` | Brand pillar content |

## Audience Rules

### Employer Content

Focus on:

- Hiring qualified candidates in Malta
- Recruitment agency support
- Shortlisting and screening
- Permanent, temporary, hospitality, finance, IT, construction, healthcare, retail, customer service, and admin recruitment
- Reducing time-to-hire
- Improving candidate quality
- Supporting urgent vacancies
- Clear employer enquiry CTAs

Avoid unsupported claims about guaranteed placements, exact hiring timelines, legal advice, salary benchmarks, or market statistics unless the source is provided.

### Candidate Content

Focus on:

- Finding jobs in Malta
- Applying through Outreach Recruitment
- Preparing CVs and applications
- Understanding role requirements
- Interview preparation
- Job categories and location-based searches
- Work eligibility, permits, or relocation only when framed carefully and factually
- Clear apply or browse jobs CTAs

Avoid promising jobs, visas, work permits, salaries, accommodation, or employer sponsorship unless explicitly supported.

### Jobs in Malta (Market) Content

Focus on:

- Broader job-market and industry trends in Malta, not individual application steps
- Which industries and job categories are hiring: hospitality, IT, finance, construction, engineering, healthcare, retail, customer service, admin, sales, insurance, marine
- Overviews of job categories that link to the relevant category hub (e.g. `/hospitality-jobs-in-malta`, `/it-jobs-in-malta.html`, `/finance-jobs-in-malta.html`, `/construction-jobs-in-malta.html`, `/engineering-jobs-in-malta.html`, `/sales-jobs-in-malta.html`, `/insurance-jobs-in-malta.html`, `/marine-jobs-in-malta.html`)
- Seasonal or cyclical hiring patterns in Malta when factually grounded
- Clear CTAs to browse the live jobs board

This pillar is distinct from Candidate content: Candidate content teaches an individual how to apply, prepare a CV, or interview; Jobs in Malta content maps the market and drives traffic into the jobs board and category hubs.

Avoid inventing salary ranges, hiring volumes, or market statistics unless the source is provided.

### Study in Malta Content

Focus on:

- International students considering studying in Malta: courses, universities, student visas, cost of living, accommodation, working while studying
- EU and non-EU student pathways, framed carefully and factually
- Mandatory CTAs: `Apply Now` to `https://apply.outreachstudy.eu/`, and links to `https://outreachrecruitment.net/study-in-malta` and `https://outreachrecruitment.net/webinar-study-in-malta.html` where relevant

The daily automation for this pillar produces the same lightweight Markdown draft structure as the other pillars (see SEO Output Requirements), not the full publish-ready HTML build. When a Study in Malta draft is promoted to a live page, follow the full `STUDY IN MALTA SKILLS/SKILL-TEMPLATE.md` template (position-zero block, key takeaways, testimonials, sticky ToC, data-sources section, full schema) rather than publishing the lightweight draft as-is.

Avoid inventing visa rules, tuition fees, scholarship amounts, or statistics; flag time-sensitive facts for verification against official Malta sources.

### Brand / Company Content

Focus on:

- Who Outreach Recruitment Ltd is, how the agency works, its recruitment process, and its values
- Why employers and candidates trust Outreach Recruitment
- Explaining the agency's approach to matching candidates and employers in Malta

Link to `about.html`, `employers.html`, `careers.html`, or `contact-us.html` depending on the angle.

Do not invent client names, hiring statistics, testimonials, awards, or years-in-business claims. Keep claims limited to what is already stated on the live site or provided by the user.

## Workflow

1. Identify whether the content is for employers, candidates, or both.
2. Define search intent: informational, commercial, transactional, navigational, or local SEO.
3. Run a keyword cannibalization check against known site pages and proposed existing topics.
4. Assess whether Outreach Recruitment can rank for the primary keyword.
5. If the primary keyword is too broad, choose a longer-tail Malta-focused keyword.
6. Build a competitor gap plan for the target keyword.
7. Generate the content package using the required output structure.
8. Add internal links and CTAs that match the audience.
9. Add FAQ content that answers real search questions.
10. Recommend appropriate schema markup.
11. Produce the required image set with the Codex `imagegen` skill when a suitable project-owned asset does not already exist, then save final assets inside the workspace before wiring them into the page.
12. For generated blog HTML files, apply the Blog HTML Layout Requirements before final review.
13. For any generated HTML page or post with FAQs, apply the FAQ HTML Style Requirements before final review.
14. Apply the Article UX and Ranking Requirements to improve readability, internal linking, conversion, and snippet eligibility.
15. Apply the SEO Audit and Optimization Requirements when improving an existing page or before final publication.
16. Keep all claims aligned with visible page content and provided facts.

## Daily Draft Automation

Use `automation/generate_daily_posts.py` when the user asks for recurring content. The
scheduled GitHub workflow uses the free, rate-limited GitHub Models service, generates five
Markdown drafts per day — one per pillar (`Employer`, `Candidate`, `JobsInMalta`, `StudyInMalta`,
`Brand`) — and opens a review pull request. Keep `status: draft` and
`review_required: true` until a human checks claims,
keyword cannibalization, links, and brand quality. Never treat draft generation as publication.
The Study in Malta draft stays in the same lightweight Markdown format as the other four pillars;
it is expanded to the full `STUDY IN MALTA SKILLS/SKILL-TEMPLATE.md` build only when a human
promotes it to a live page.

Maintain the rotating per-pillar queues in `automation/topics.json`, where every topic carries a
`pillar` field. Add fresh topics to each pillar's queue before it wraps, and avoid primary
keywords already targeted by live pages.

## SEO Output Requirements

For every package, generate:

- Page title or H1
- Primary keyword
- 5-8 secondary keywords
- 5 long-tail keywords
- Search intent
- Suggested slug
- SEO title under 60 characters
- Meta description under 155 characters
- Position Zero answer, 40-60 words
- Key takeaways
- Full page outline with H2 and H3 structure
- Draft page or article copy
- FAQ section with 4-8 questions
- Internal linking suggestions
- CTA recommendations
- Schema recommendations
- AI-search summary
- Image alt text suggestions

## Article UX and Ranking Requirements

For every publishable article, guide, landing page, or service page:

- Add a concise direct answer near the top of the page, 40-60 words, styled as an `answer-box` or equivalent visible summary block.
- Use short paragraphs, clear H2/H3 hierarchy, and enough spacing between headings and body text for easy scanning.
- Use tables for checklists, comparisons, documents, requirements, timelines, pros/cons, role categories, or step-by-step summaries instead of dense paragraph blocks.
- Use highlighted boxes for quick answers, key takeaways, warnings, official-source reminders, and CTAs.
- Include audience-matched CTAs at natural decision points: after the introduction, mid-page, and near the conclusion.
- For candidate pages, prefer CTAs such as `Browse jobs in Malta`, `Register your interest`, `Prepare your CV`, and relevant interview or application guides.
- For employer pages, prefer CTAs such as `Request recruitment support`, `Contact Outreach Recruitment`, `View employer services`, and `Book a call` when that path exists.
- End blog posts with 2-3 related articles using the existing `article-card` style and internally link to relevant guides in the body.
- Naturally include relevant entities where accurate: Outreach Recruitment Ltd, Malta, jobs in Malta, recruitment agency, employers, candidates, and official Malta entities such as Jobsplus or Identita Malta when the topic requires them.
- For topics involving documents, permits, eligibility, taxes, employment law, visas, work status, or official processes, add a visible accuracy note that the content is general guidance, not legal advice, and link to relevant official Malta resources where useful.
- Before final delivery, check that the page has: home header/footer, working hero image, matching OG/schema images, readable mobile table behavior, visible CTAs, FAQ accordion behavior, related article cards, and an updated `blog/index.html` card when publishing a blog post.

## SEO Audit and Optimization Requirements

When generating, improving, or refreshing a page, perform a compact ranking audit and apply fixes where practical:

- Confirm the page targets one clear primary keyword and that title, H1, slug, intro, metadata, and FAQ intent support it without keyword stuffing.
- Check heading structure: one H1, logical H2/H3 hierarchy, no skipped or decorative headings that confuse the article outline.
- Optimize SEO title under 60 characters and meta description under 155 characters, with Malta/location intent when relevant.
- Add or improve the featured-snippet answer block near the top and make sure it directly answers the primary query.
- Check FAQ quality: questions should match search intent, answers should be concise, visible in HTML, styled with the FAQ accordion component, and reflected accurately in `FAQPage` schema.
- Recommend or add 3-6 internal links from existing relevant pages/posts, and add 2-3 related article cards at the end of blog posts.
- Check image SEO: descriptive filenames, meaningful alt text, visible hero image, card thumbnail, OG/Twitter image, and matching JSON-LD image.
- Check schema markup: use only schemas matching visible page content, usually `BlogPosting`/`Article`, `FAQPage`, `BreadcrumbList`, `Organization`, `Service`, or `LocalBusiness` depending on page type.
- Improve CTAs so the next step matches the audience and intent, without mixing employer and candidate conversion paths in the same paragraph.
- Flag thin content, duplicated generic sections, weak local relevance, unsupported claims, or missing official-source notes for sensitive topics.
- For old or existing posts, refresh stale dates, outdated claims, weak introductions, missing FAQs, poor CTA placement, missing related posts, and missing schema/image fields.
- For new topic planning, suggest candidate keywords and employer keywords separately, prioritizing Malta-specific long-tail searches with commercial or practical intent.
- Finish with a short `SEO Audit Notes` section listing what was improved and any remaining risk or manual follow-up.

## Publishing Image Requirements

For every publishable page or blog article, create or specify a complete image set before final publication:

- Use the Codex `imagegen` skill for bespoke raster visuals when a suitable existing project asset does not already exist.
- Save generated project assets inside the workspace `assets/` folder or another page-referenced workspace path; never leave referenced files only in Codex generated-images storage.
- Produce a hero image, an Open Graph/Twitter image, and a card thumbnail from the same visual direction when practical.
- Recommended dimensions: hero image sized for the page template, OG/Twitter image at `1200x630`, and card thumbnail at `400x210`.
- Use descriptive filenames based on the page slug, such as `{slug}-og.jpg` and `{slug}-thumb.jpg`.
- Update `og:image`, `twitter:image`, visible hero image, card thumbnail, JSON-LD image fields, and image alt text so they all match the final asset choices.
- Until the user provides the generated assets, use the best existing site asset as a temporary placeholder and clearly mark that it should be replaced.

## Blog HTML Layout Requirements

For every new publishable blog article generated by this skill:

- Use the same site header and footer as the home page at `https://outreachrecruitment.net/`. In the workspace, source these from `components/header.html` and `components/footer.html`, which mirror the home page `index.html` shell.
- Do not create a custom, simplified, or standalone blog header/footer.
- Include the home page post-footer utility markup and Webflow scripts from `index.html` after the footer so navigation, dropdowns, mobile menu, and footer interactions keep working.
- Match the article layout format used by `blog/why-employers-in-malta-trust-outreach-recruitment.html`.
- Use `<main class="main">`.
- Start the visible article with `<section class="section page-header">`, including the blog back link, audience/topic tag, `h1.heading-h1`, `caption blue-caption` publish date, and `cms-featured-media` hero image.
- Place article copy inside `<section class="section padding-top-extra-small">`, `container tight`, `cms-article`, and `w-richtext`.
- Keep article-specific metadata, schema, canonical URL, hero image, OG image, alt text, category tag, and date aligned with the generated topic.
- Add a `Read more` section using existing `article-card` markup when related posts are included.
- When adding the post to `blog/index.html`, use the existing blog card/listing structure and the generated thumbnail.

## FAQ HTML Style Requirements

For every generated HTML page or blog post that includes FAQs:

- Use the Outreach accordion FAQ component style, not plain stacked `h3` and `p` blocks.
- Wrap the FAQ items in `<div class="faq-list" data-gsap-scroll="stagger">`.
- For each FAQ, use this structure:
  - `<div class="faq-item">`
  - `<div class="faq-item-top">`
  - `<h3 class="text-large strong">Question text</h3>`
  - `<div class="faq-button"><div class="button-circle small">...plus/minus icons...</div></div>`
  - `<div class="faq-item-bottom"><div class="faq-item-text-wrapper"><p class="text-medium">Answer text</p></div></div>`
- Use the same plus and minus SVG icon pattern as existing Outreach FAQ components: plus icon has horizontal and vertical paths; minus icon has only the horizontal path.
- Keep FAQ answers visible to search engines in the HTML and keep `FAQPage` schema aligned with the same visible questions and answers.
- Ensure the page includes the interaction needed to toggle `.faq-item.or-open`, either through the shared site interactions script or a page-local click handler for `.faq-item-top`.
- If page-local styling is needed, scope it to the article or FAQ section, such as `.article-faq-section`, so it does not change unrelated site FAQ blocks.

## Keyword Targeting Rules

- Use Malta modifiers where relevant: `Malta`, `jobs in Malta`, `recruitment agency Malta`, `hiring in Malta`, `Malta employers`, `career opportunities Malta`.
- Prefer specific long-tail keywords over broad generic terms.
- Match employer keywords to commercial hiring intent.
- Match candidate keywords to job search, application, career, and role-category intent.
- Do not use salary, visa, sponsorship, remote work, or relocation keywords unless supported.
- Keep keywords natural. Do not repeat the primary keyword in every paragraph.

## SERP and Gap Analysis Rules

Before writing, identify the likely competitor page types:

- Recruitment agencies in Malta
- Job boards
- Employer career pages
- LinkedIn and large job platforms
- Government or official employment resources
- HR consultancies
- Career advice blogs

Summarize what competitors usually cover and how the Outreach Recruitment page can be stronger through:

- Malta-specific detail
- Clearer employer or candidate intent
- Better FAQs
- Stronger internal links
- Better conversion path
- More practical step-by-step guidance
- Cleaner page structure for AI search

## AEO and GEO Rules

Optimize for AI-powered search by including:

- A concise direct answer near the top of the page
- A key facts table where useful
- Standalone FAQ answers
- Entity mentions such as Outreach Recruitment Ltd, Malta, recruitment agency, employers, candidates, jobs, hiring, and relevant job categories
- Clear definitions for recruitment terms when useful
- Short, factual paragraphs that can be quoted by answer engines

Do not make the content robotic. Human readability comes first.

## Conversion Rules

Employer pages should lead to enquiry or contact.

Candidate pages should lead to browsing jobs, applying, or registering interest.

Use CTA text such as:

- `Request recruitment support`
- `Contact Outreach Recruitment`
- `Find candidates in Malta`
- `Browse jobs in Malta`
- `Apply for jobs in Malta`
- `Register your interest`

Place CTAs:

- After the introduction
- Mid-page after the strongest value section
- Before the conclusion

## Schema Recommendations

Choose schema based on page type:

- `Service` for employer recruitment service pages
- `Organization` for brand/entity reinforcement
- `LocalBusiness` when location relevance is central
- `FAQPage` for FAQ sections
- `Article` or `BlogPosting` for guides and articles
- `BreadcrumbList` for all publishable pages
- `JobPosting` only for individual job vacancies, not general candidate guides

Schema must match visible page content. Do not add hidden claims.

## Safety and Accuracy Rules

- Do not invent client names, hiring statistics, salaries, legal outcomes, or government rules.
- Do not present immigration, visa, tax, or employment-law information as legal advice.
- Use cautious wording for work permits and eligibility.
- If a fact could change, recommend verifying it before publishing.
- Keep employer and candidate claims distinct.
- Avoid duplicate generic paragraphs across multiple pages.

## Final Output Structure

Return content in this order:

1. SEO Research
2. Cannibalization Check
3. Can We Rank?
4. Recommended Keyword Strategy
5. SEO Metadata
6. Page Outline
7. Full Draft
8. FAQs
9. Internal Links and CTAs
10. Schema Recommendations
11. AI Search Summary
12. Publishing Checklist
