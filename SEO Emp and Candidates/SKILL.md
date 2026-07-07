---
name: employer-candidate-seo-generator
description: Generate SEO-optimized, AI-search-friendly content packages for Outreach Recruitment employer and candidate pages. Use when creating employer service pages, recruitment landing pages, candidate career guides, job seeker content, hiring guides, meta tags, FAQs, schema recommendations, internal links, or conversion copy for Outreach Recruitment audiences.
---

# Employer and Candidate SEO Generator

## Overview

Create complete SEO content packages for Outreach Recruitment pages that target either:

- Employers looking for recruitment, staffing, HR, talent acquisition, or hiring support in Malta.
- Candidates looking for jobs, career guidance, applications, interviews, relocation, or work opportunities in Malta.

Use this skill for service pages, landing pages, blog articles, guides, FAQ hubs, category pages, and conversion-focused SEO content.

## Required Inputs

Collect or infer the following from the user request:

- Page or article topic
- Target audience: `Employers`, `Candidates`, or `Both`
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
14. Keep all claims aligned with visible page content and provided facts.

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
