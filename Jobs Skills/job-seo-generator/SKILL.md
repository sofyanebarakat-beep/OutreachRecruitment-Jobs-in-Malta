---
name: job-seo-generator
description: Generate complete Google Jobs-ready, SEO-optimized, AI-search-friendly job posting packages from a job title and job description. Use when the user provides a job title, job description, vacancy details, or asks to create job SEO fields, JobPosting schema content, Google Jobs content, GEO/AEO content, meta tags, keywords, slugs, or full job detail page copy for Outreach Recruitment jobs.
---

# Job SEO Generator

## Overview

Transform a provided job title and job description into a complete job detail content package for Google Jobs, organic search, AI search engines, and recruitment platforms.

Use this skill for Outreach Recruitment job pages and similar vacancy pages where the output must be ready for visible page content and structured data.

## Required Inputs

Collect or infer the following from the user request and job description:

- Job title
- Job description
- Location city
- Location region
- Employment type
- Salary range
- Expiry date
- Reference number
- Candidate Origin — who should apply: `Malta residents` / `EU relocating` / `International` / `Open` (default: `Open`)
- Immediate Start — whether urgency is stated: `Yes` / `No` / `Not stated` (default: `Not stated`)

If any field is missing, make a reasonable assumption only when the job description clearly supports it. Otherwise mark the value as `Not specified` and keep structured-data fields honest.

## Workflow

1. Read `references/outreach-employer.md` for static employer details.
2. Read `references/job-output-template.md` for the required output sections.
3. Identify the role category, candidate search intent, likely industry, location modifiers, and seniority level before writing.
4. Generate every requested section in the template.
5. Keep all generated structured-data fields aligned with visible page content.
6. Avoid keyword stuffing, fake locations, fake salaries, fake benefits, and unsupported visa/work permit claims.
7. Use Malta-focused SEO when the role is located in Malta.
8. Make the job title concise and clean. Do not include salary, employer, location, dates, or promotional words in the schema `title`.
9. Create unique copy for every vacancy by using the actual duties, requirements, industry, location, and seniority from the source material.
10. Apply the SERP analysis, entity SEO, job category mapping, candidate question, freshness, conversion, duplicate prevention, and schema safety rules even when the user provides only a short job description.
11. When the user asks to create or publish a new job in the site, add the job to the jobs page and update open-position counts using the Site Publishing Rules.

## SEO Expansion Rules

For every job package, generate:

- Primary SEO keyword
- 5 secondary keywords
- 5 long-tail keywords
- Location-based keyword variations
- Industry keyword variations
- Candidate search intent
- Suggested SEO slug
- SEO title under 60 characters following the format: Job Title Job in City, Malta | Outreach Recruitment
- Meta description 120–155 characters including job title, city, and "Apply now"
- 4-6 FAQ questions and answers
- Internal linking suggestions including category hub pages and location pages
- Short AI-search answer summary
- Google Jobs optimization notes

Use the main job title, location, industry, seniority, and employment type naturally. Avoid repeating the same keyword too many times.

## Meta Title Rules

Every meta title must:

- Follow the format: `Job Title Job in City, Malta | Outreach Recruitment`
- Be a maximum of 60 characters
- Contain the word "Job" or "Jobs"
- Contain the word "Malta" for Malta-based roles
- Include the city when known
- Not include salary, employer name variations, dates, or promotional words

## Meta Description Rules

Every meta description must:

- Be between 120 and 155 characters
- Include the job title
- Include the city and Malta
- Include a call-to-action phrase such as "Apply now" or "Apply today"
- Match the visible page content

## Candidate Origin Rules

The Candidate Origin field determines how the job is positioned in SEO copy, schema, keyword targeting, and the details grid. Apply the following rules based on the value provided.

**Malta residents:**
- Set `applicantLocationRequirements: Malta` in the JobPosting schema
- Set the Job Target grid value to: `Residents in Malta`
- Include keywords such as `[job title] jobs Malta`, `jobs for Malta residents`, `local hiring Malta`
- Do not include relocation, EU, or international keywords
- Do not mention visa or work permit unless explicitly stated

**EU relocating:**
- Set `applicantLocationRequirements: European Union` in the JobPosting schema
- Set the Job Target grid value to: `EU Nationals & Relocating Candidates`
- Include keywords such as `[job title] jobs Malta for Europeans`, `relocate to Malta [job title]`, `EU candidates Malta`
- Include a relocation note in the page intro only if relocation assistance is explicitly stated
- Do not mention visa sponsorship unless explicitly provided

**International:**
- Set `applicantLocationRequirements: Worldwide` in the JobPosting schema
- Set the Job Target grid value to: `International Applicants Welcome`
- Include keywords such as `[job title] Malta international`, `work in Malta [job title]`
- Include a work permit or visa note only if explicitly stated in the job description
- Do not imply sponsorship or permit support unless explicitly confirmed

**Open (default):**
- Set the Job Target grid value to: `Residents in Malta & Europeans`
- Include standard Malta location keywords
- Do not reference visa, sponsorship, or international relocation unless stated

## Keyword Targeting Rules

- Prefer long-tail, role-specific keywords over generic terms.
- Use Malta location modifiers for Malta roles, such as `jobs in Malta`, `{job title} jobs Malta`, `{industry} jobs in Malta`, and `{city} jobs`.
- Include city-specific modifiers only when the city is known or clearly supported.
- Include salary keywords only when salary is visible on the page.
- Include visa, relocation, sponsorship, or work permit keywords only when explicitly provided or clearly supported.
- Apply Candidate Origin keyword rules: include relocation and EU keywords only when Candidate Origin is `EU relocating` or `International`.
- Include `immediate start` or `urgent vacancy` keywords only when `Immediate Start: Yes` is provided.
- Match keywords to candidate intent: role search, location search, industry search, salary search, career level search, or urgent vacancy search.
- Do not create misleading keywords for remote work, flexible work, benefits, or employer names unless they are supported by the job details.

## AEO and GEO Rules

Optimize for answer engines and generative search by including:

- A direct 40-60 word answer summary that explains the job, location, employment type, and ideal candidate.
- A concise key facts table.
- FAQ answers that can stand alone in search snippets.
- Natural entity mentions, including the role, Malta, Outreach Recruitment Ltd, industry, employment type, and application method.
- Clear, factual language that AI systems can quote or summarize without needing hidden context.

Do not over-optimize for AI search at the expense of human readability.

## SERP Competitor Analysis Rules

For every job package, identify the likely competing page types for the target keyword:

- Job boards
- Recruitment agencies
- Employer career pages
- LinkedIn jobs
- Indeed, JobsinMalta, Keepmeposted, and other Malta job platforms
- Government, industry, or professional body pages when relevant

Explain how the Outreach Recruitment job page can compete through clearer job details, stronger FAQs, better location relevance, fresh posting dates, internal links, and accurate `JobPosting` structured data.

## Entity SEO Rules

Include relevant entities naturally in visible content, keyword fields, FAQs, and AI-search sections:

- Clean job title and common role synonyms
- Main job category and related categories
- Industry, sector, and department where inferable
- Location city, region, Malta, and nearby location modifiers when supported
- Employment type, seniority, shift pattern, and working hours when provided
- Required skills, tools, software, licenses, certifications, and languages
- Employer entity: Outreach Recruitment Ltd
- Application method and reference number

Do not force entities that are not relevant to the job. Do not invent certifications, tools, languages, licenses, or locations.

## Job Category Mapping Rules

Classify every job into one primary category and up to three secondary categories.

Use categories such as:

- Hospitality jobs
- Catering jobs
- Restaurant jobs
- Hotel jobs
- Retail jobs
- Sales jobs
- Customer service jobs
- Finance jobs
- Accounting jobs
- Administrative jobs
- HR and recruitment jobs
- IT jobs
- Marketing jobs
- Healthcare jobs
- Care jobs
- Construction jobs
- Engineering jobs
- Technical jobs
- Manufacturing jobs
- Maritime jobs
- Logistics jobs
- Driving jobs
- Cleaning jobs
- Security jobs
- Skilled trades jobs

Use the category mapping to suggest internal links, related jobs, and keyword variations.

## Google Jobs Schema Rules

Every job page must include a complete `JobPosting` JSON-LD block. Generate values for all fields below. Mark fields as omitted only when the detail is genuinely unknown and cannot be safely inferred.

Required schema fields:

- `@context`: `https://schema.org`
- `@type`: `JobPosting`
- `title`: clean job title only, no salary, no location, no promotional text
- `description`: full HTML-safe job description visible on the page
- `datePosted`: ISO date when the job was published
- `validThrough`: ISO date when the job expires — must also be visible on the page
- `employmentType`: FULL_TIME, PART_TIME, CONTRACTOR, TEMPORARY, INTERN, VOLUNTEER, PER_DIEM, or OTHER
- `hiringOrganization`: name, sameAs URL, and logo — use Outreach Recruitment Ltd and its website by default
- `jobLocation`: streetAddress, addressLocality (city), addressRegion (Malta), addressCountry (MT)
- `baseSalary`: include only when salary is visible on the page — must use `unitText` (MONTH or YEAR) and `value` with `minValue`, `maxValue`, and `@type: QuantitativeValue`
- `salaryCurrency`: must be `EUR` whenever `baseSalary` is included
- `experienceRequirements`: years of experience, for example "Minimum 2 years experience in a similar role"
- `educationRequirements`: degree level or equivalent, for example "Bachelor's degree or equivalent experience"
- `qualifications`: specific certifications, licences, or professional qualifications, for example "ACCA qualified", "HACCP certified", "Clean driving licence"
- `responsibilities`: list of key duties as a separate field from the description
- `incentiveCompensation`: bonus, commission, tips, or other variable pay — include only when clearly supported
- `skills`: comma-separated list of specific skills and tools, for example "Xero, ACCA, Excel, customer-facing accounting"
- `jobBenefits`: visible benefits list, for example "Health insurance, meal allowance, career progression"
- `workHours`: shift pattern or working hours, for example "Monday to Friday, 08:00–17:00" or "40 hours per week"
- `occupationalCategory`: O*NET or ISCO category when inferable
- `industry`: the industry sector, for example "Hospitality", "Finance", "Information Technology"
- `directApply`: `true` only when candidates can apply directly through the Outreach Recruitment platform or a direct employer application link
- `identifier`: `@type: PropertyValue`, `name`: reference number label, `value`: actual reference number
- `jobLocationType`: include `TELECOMMUTE` only for fully remote roles — omit for on-site roles
- `applicantLocationRequirements`: set based on Candidate Origin field — `Malta` for Malta residents, `European Union` for EU relocating, `Worldwide` for International, standard Malta for Open
- `jobImmediateStart`: set to `true` only when `Immediate Start: Yes` is provided — omit otherwise

Also add these supporting schema blocks on every job page:

- `BreadcrumbList`: Home → Jobs → Category → Job Title
- `FAQPage`: 4–6 FAQ items matching the visible FAQ section
- `ImageObject`: for the job page featured image or company logo

## Badge and Highlight Rules

Every job page must include a visible Job Highlights block near the top of the page showing:

- Salary range (if visible)
- Employment type (Full-Time, Part-Time, Contract, etc.)
- Location and work mode (On-Site, Hybrid, Remote)
- Experience required
- Shift pattern or working hours
- Candidate Origin (e.g. "Open to EU candidates", "Malta residents only", "International applicants welcome")

Add trust and urgency badges where clearly supported by the job details. Use only these approved badges:

- Immediate Start — only when `Immediate Start: Yes` is provided or the job description explicitly states urgency. When active, add `"jobImmediateStart": true` to the JobPosting schema and include urgency language in the intro paragraph and CTA.
- Training Provided — only when mentioned in the job description
- Full-Time Position — for FULL_TIME roles
- Visa Sponsorship Available — only when explicitly stated
- Career Growth Opportunities — only when progression is mentioned
- Relocation Assistance — only when explicitly stated
- Language Bonus — only when a language premium is mentioned

Do not invent badges. Only show badges that match the actual job details.

When `Immediate Start: Yes`:
- Add "Immediate Start Available" badge to the Job Highlights block
- Use urgency language in the page intro: "This is an urgent vacancy — we are interviewing immediately."
- Add urgency keywords to the SEO package: `immediate start [job title] Malta`, `urgent [job title] vacancy Malta`
- Set `"jobImmediateStart": true` in the JobPosting JSON-LD
- Mention in the FAQ: "Is an immediate start required?" → "Yes, the employer is looking to fill this role as soon as possible."

When `Immediate Start: No` or `Not stated`:
- Do not add the Immediate Start badge
- Do not use urgency language
- Omit `jobImmediateStart` from the schema

## Rich Content Section Rules

Every full job page must include all of the following visible sections:

- Job Highlights (salary, type, location, experience, hours)
- About the Role — 2–3 paragraph introduction
- Key Responsibilities — bulleted list from the job description
- Key Requirements — required skills, experience, and qualifications
- Skills Required — specific tools, software, and certifications
- Preferred Qualifications — nice-to-have items
- Languages Required — include only when stated or clearly required by the role
- What We Offer (benefits, salary range if visible, work environment)
- Career Growth Opportunities — include only when supported
- About the Company — anonymised paragraph such as "Our client is a leading hotel group operating in St Julian's" — do not invent employer-specific claims
- Visa Sponsorship and Relocation Assistance — include only when explicitly stated
- Reporting To — include only when the reporting line is stated or inferable
- Contract Duration — include for temporary or fixed-term roles
- Application Deadline — visible date matching `validThrough`
- Response Timeline — always include: "We aim to respond to all applications within 3–5 business days"
- How to Apply — clear instructions and application URL
- Neighbourhood or Location Description — one sentence describing the area, for example "Located in St Julian's, near Spinola Bay and the Paceville entertainment district" — include when the city is known
- FAQ Section — 4–6 questions and answers
- Similar Jobs — 3–5 links to related open roles using descriptive anchor text
- Latest Jobs — 3–5 links to the most recently posted jobs
- People Also Viewed — 3–5 links to related roles candidates commonly compare

Minimum page word count is 300 words. Target 1000+ words for full job page copy.

## Candidate Question Rules

Generate related keyword questions that match real candidate searches, such as:

- What experience is needed for this job?
- Is this job full-time or part-time?
- Where is this job located?
- How can I apply for this job?
- Is salary provided for this job?
- Are work permit or visa details mentioned?
- What skills are required for this role?
- Is this role suitable for junior or experienced candidates?
- What industry is this job in?

Turn the strongest 4-6 questions into the FAQ section. Only answer with details supported by the job description or static employer data.

## Freshness and Update Rules

For active job postings:

- Use a clear `datePosted` when available.
- Use a clear `validThrough` when available.
- If the expiry date is missing, mark it as `Not specified` and do not invent one.
- Do not present expired jobs as active.
- Recommend reviewing or refreshing active job pages every 14-30 days.
- Keep expiry dates, salary, location, and application URLs consistent across visible content and schema fields.
- Recommend updating `lastmod` in the sitemap every time the page is changed.
- Recommend resubmitting the sitemap in Google Search Console after each update.
- Recommend using the Google Indexing API to resubmit updated pages immediately.

Use ISO-style dates, such as `2026-07-30`, for schema-ready fields when dates are provided.

## Conversion Optimization Rules

Every full job page should help candidates apply quickly. Include:

- A clear opening summary
- Who the job is suitable for
- Key responsibilities
- Key requirements
- Salary and benefits only when provided
- Location and employment type
- Reference number
- Simple application instructions
- Direct call to apply
- Contact or application URL
- Response timeline statement

Keep the apply section clear, visible, and free of unnecessary friction.

## Duplicate Content Prevention Rules

When creating multiple similar job pages:

- Rewrite introductions uniquely.
- Use role-specific duties from the job description.
- Mention the specific industry, location, shift pattern, tools, and requirements where provided.
- Avoid reusing the same generic paragraphs across different jobs.
- Keep the Outreach Recruitment description short and consistent.
- Make the role content unique enough to stand on its own in search results.

If the provided job description is thin, expand responsibly using safe role expectations, but clearly avoid unsupported employer-specific claims.

## Duplicate Title Prevention Rules

When two or more pages exist for the same role:

- Add a differentiator to the second page title, such as the hotel name, area of the island, shift pattern, or "(2nd Opening)".
- Ensure the canonical URL points to the intended primary page.
- Add a note in the internal linking plan if pages risk cannibalization.

## Internal Linking Rules

For every job package, suggest internal links to:

- Main jobs index: `/jobs/`
- Primary category hub page (e.g. `hospitality-jobs-in-malta.html`)
- Secondary category hub pages where relevant
- Location pages where they exist (e.g. `jobs-in-st-julians.html`)
- 3–5 related open job pages
- Blog posts or guides relevant to the industry or role

Category hub pages to link from:

- Hospitality Jobs in Malta
- Marine Jobs in Malta
- Engineering Jobs in Malta
- IT Jobs in Malta
- Healthcare Jobs in Malta
- Finance Jobs in Malta
- Construction Jobs in Malta
- Sales Jobs in Malta
- Insurance Jobs in Malta

Location hub pages to link from when the city matches:

- Jobs in St Julian's, Malta
- Jobs in Sliema, Malta
- Jobs in Valletta, Malta
- Jobs in Gozo, Malta
- Jobs in Mellieha, Malta
- Jobs in Birkirkara, Malta
- Jobs in Mosta, Malta
- Jobs in Paola, Malta

When a new job page is created, always flag which category hub pages and location hub pages should link back to it.

## Image SEO Rules

For every job page, generate:

- A descriptive image filename following the pattern: `{job-title}-job-malta.jpg`
- A descriptive ALT tag: `{Job Title} job opportunity in {City}, Malta — Outreach Recruitment`
- An `ImageObject` schema block with `url`, `width`, `height`, and `caption`
- Open Graph image tag recommendation using the same image

Rename all images descriptively. Do not use generic filenames like `image1.jpg` or `job-card-logo.jpg` as the primary job page image.

## Open Graph and Social Rules

Every job page must include:

- `og:title` — matches the SEO title
- `og:description` — matches the meta description
- `og:image` — descriptive job or company image
- `og:type` — `website`
- `og:url` — matches the canonical URL
- Twitter card title
- Twitter card description

Include these in the SEO package output.

## Advanced Schema Rules

For every job page, in addition to `JobPosting`, recommend adding:

- `BreadcrumbList` — Home > Jobs > Category > Job Title
- `FAQPage` — matching the visible FAQ section
- `ImageObject` — for the featured image

For category hub pages, recommend:

- `CollectionPage` — wrapping the list of jobs on the page
- `ItemList` — listing each job as a `ListItem` with `name`, `url`, and `position`
- `BreadcrumbList` — Home > Category

For the main jobs index page, recommend:

- `WebSite` — with `SearchAction` for sitelinks search box
- `Organization` — with name, URL, logo, social profiles, and contact info

For the home page and contact page, recommend:

- `LocalBusiness` — with name, address, phone, email, geo coordinates, and opening hours
- `ContactPage`

## Off-Page Distribution Rules

For every new job published, include an off-page distribution checklist in the output:

- Post on LinkedIn company page with the direct link to the job page
- Post on Facebook with the direct link — Facebook links are indexed quickly
- Submit to Indeed (free listing) — creates a backlink and cross-platform authority signal
- Submit to Glassdoor
- Submit to Jooble
- Submit to Jobrapido
- Submit to MaltaPark
- Publish a supporting note on Medium if the role is senior or specialist
- Share in relevant Malta career communities and directories

## Google Business Profile Rules

Include a note with every job package recommending:

- Ensure a Google Business Profile exists for Outreach Recruitment at the correct address
- Link from GBP posts to the new job page
- Use GBP posts to announce new vacancies with a direct apply link

## Advanced SEO Recommendations

Include the following recommendations in the output when relevant:

- RSS feed generation: suggest RSS feeds for Latest Jobs, Hospitality Jobs, Marine Jobs, and IT Jobs
- Job collections: recommend creating collection pages for Latest Jobs in Malta, Remote Jobs in Malta, Full-Time Jobs in Malta, and Hospitality Jobs in Malta
- Pagination schema: add `rel="next"` and `rel="prev"` on paginated job listing pages
- Author and publisher info: add `author` as `Outreach Recruitment` and `dateModified` to each job page
- Core Web Vitals: flag if images need WebP conversion, lazy loading, or if scripts should be deferred
- HTML sitemap: recommend creating an HTML sitemap page for additional crawl coverage
- Category-specific XML sitemaps: recommend separate sitemaps for jobs, blog, pages, and video

## Structured Data Safety Rules

Do not add schema fields that are not visible on the page or clearly supported by the source details.

Avoid unsupported values for:

- Salary
- Remote status
- Visa sponsorship
- Work permit support
- Benefits
- Education requirements
- Experience requirements
- Job location
- Working hours
- Employment type
- Application deadline

If a value is uncertain, use `Not specified` in visible content and omit unsupported schema fields where omission is more accurate than guessing.

## Salary Visibility Rules

Google Jobs structured data must match visible page content. Do not add salary to `baseSalary`, SEO copy, meta content, or hidden structured data if the salary is not visible on the job page.

When salary is provided but the user does not want it shown publicly:

- Mark visible salary as `Not disclosed` or `Not specified`.
- Omit `baseSalary` from `JobPosting` JSON-LD.
- Do not use salary keywords in SEO title, meta description, keyword lists, or FAQs.
- Do not mention salary ranges in AI-search summaries or internal linking notes.
- Keep the salary internally only if the user asks for a private recruiter note, clearly separated from publishable content.

When salary is provided and allowed to be visible:

- Show the same salary range in the visible job page content.
- Use the same currency and range in `baseSalary`.
- Always pair `baseSalary` with `salaryCurrency: EUR`.
- Keep salary wording consistent across the job page, SEO package, FAQs, and schema.

## Site Publishing Rules

When the user asks to add a generated job to the Outreach Recruitment website, complete these site updates after creating the job content:

- Add the new job to `https://outreachrecruitment.net/jobs/` in the `opening-jobs-grid`.
- In the local project, update the jobs listing source that contains `id="opening-jobs-grid"`, usually `jobs/index.html`.
- Insert the new job card as the first job in `opening-jobs-grid` so it appears as the newest opening.
- Mark the new card as latest/new using the existing card pattern, such as `data-opening-job`, `data-featured="true"`, `data-latest="true"`, and `<div class="opening-card-day">New</div>`.
- Use the generated job slug for the card link, for example `/jobs/{seo-slug}/`.
- Use the generated job title, location, employment type, category, and date in the card fields and `data-*` attributes.
- Create or update the individual job detail page at `/jobs/{seo-slug}/` when the user asks for the full site implementation.
- Increase the open-position count by 1 from the current value.
- Keep every visible count consistent, including `+{count} Open Positions`, `Showing {count} jobs`, tab/filter labels, and any `.or-counter-num` value followed by `open positions now`.
- Do not hard-code a specific number; always read the current count and increment it by the number of new active jobs being added.
- If the site has JavaScript that derives counters from the actual number of job cards, still verify the visible fallback/static counts are consistent.
- After editing, search the repo for the old count and new count to ensure no visible job counters were missed.
- Do not increase counts for draft, expired, duplicate, or unpublished jobs.
- After publishing, add the new job page URL to `sitemaps/sitemap-jobs.xml` with the current date as `lastmod`.
- Update `sitemap_index.xml` with the new `lastmod` date for `sitemap-jobs.xml`.
- Recommend submitting the sitemap in Google Search Console.
- Recommend running the Google Indexing API script to submit the new URL immediately.
- Add the new job to the matching category hub page internal links.
- Add the new job to the matching location hub page internal links if one exists.

## Job Page Body Content Rules

When generating the HTML job detail page or the Section 4 job content:

- Do not repeat the salary in body copy sections such as bullet lists, introductions, or "What's on Offer".
- Do not include the reference number in the visible body text.
- Do not include salary in the `JobPosting` JSON-LD schema or the JSON-LD description field since it is not shown on the visible page.

### Details Grid — Fourth Field

The fourth field in the details grid (Category | Employment Type | Work Mode | **fourth**) must always be:

- **Label:** `Job Target`
- **Value:** determined by the Candidate Origin field:
  - `Malta residents` → `Residents in Malta`
  - `EU relocating` → `EU Nationals & Relocating Candidates`
  - `International` → `International Applicants Welcome`
  - `Open` or not stated → `Residents in Malta & Europeans` (default)

Do not use the Salary field in the details grid. The Job Target field replaces it on all Outreach Recruitment job pages.

## Output Rules

- Output all template sections unless the user asks for a smaller subset.
- Use natural human language.
- Generate unique content for each job.
- Use HTML-friendly headings when writing long job page content.
- Keep meta descriptions between 120 and 155 characters.
- Keep SEO titles under 60 characters.
- Use ISO-style dates for `datePosted` and `validThrough` when dates are available.
- Use `EUR` as the default salary currency unless the user specifies otherwise.
- Use `Malta` as the default country for Outreach Recruitment Malta roles unless the user specifies another country.
- Use `Malta` as the default location region for Outreach Recruitment jobs unless the user specifies another region.
- Use a lowercase, hyphenated URL slug with no dates, salary, or filler words.
- Place the primary keyword naturally in the SEO title, H1, first paragraph, and meta description when it reads well.
- Include internal link suggestions for relevant job category, location, and industry pages.
- Include an FAQ section for full job page outputs unless the user asks for structured data only.
- Include `directApply` in schema only when candidates can apply directly on the Outreach Recruitment platform or another direct employer/recruiter application page.

## Quality Checks

Before finalizing, verify:

- Job title matches the visible page title.
- Meta title follows the format: Job Title Job in City, Malta | Outreach Recruitment and is under 60 characters.
- Meta title contains the word "Job" or "Jobs".
- Meta title contains "Malta" for Malta roles.
- Meta description is between 120 and 155 characters and includes "Apply now" or "Apply today".
- Location city, region, and country are realistic and consistent.
- Employer is `Outreach Recruitment Ltd` unless the user provides another authorized hiring organization.
- Salary appears only if it will also be visible on the page.
- `salaryCurrency` is set to `EUR` whenever `baseSalary` is included.
- `validThrough` is present and visible on the page.
- `employmentType` is present and matches visible content.
- `experienceRequirements` is present and visible on the page.
- `educationRequirements` is present and visible on the page.
- `qualifications` is present when certifications or licences apply.
- `responsibilities` is present as a separate field.
- `skills` field is present and matches the Skills Required section.
- `jobBenefits` is present when a benefits section is on the page.
- `workHours` is present when hours or shift pattern is stated.
- `BreadcrumbList` schema is included.
- `FAQPage` schema matches the visible FAQ section.
- `ImageObject` schema is included for the featured image.
- Open Graph tags are included.
- Expiry date is present for active job postings when possible.
- Application URL uses the Outreach Recruitment careers platform unless the user provides a role-specific apply URL.
- The output can be translated into valid `JobPosting` JSON-LD without adding hidden facts.
- Primary keyword appears naturally in the SEO title, H1, first paragraph, and meta description.
- SEO title is under 60 characters.
- Meta description is 120–155 characters.
- Slug is lowercase, short, hyphenated, and relevant.
- FAQ answers are direct, useful, and not repetitive.
- Internal links include the category hub page and location hub page.
- Similar Jobs, Latest Jobs, and People Also Viewed sections are included.
- Neighbourhood description is included when the city is known.
- Response timeline statement is included.
- Content is unique and not copied from a generic job description.
- No unsupported salary, visa sponsorship, work permit support, remote work, relocation, benefits, or urgency claims are added.
- `jobImmediateStart: true` is only present in schema when `Immediate Start: Yes` was explicitly provided.
- `applicantLocationRequirements` matches the Candidate Origin value provided.
- Job Target grid value matches the Candidate Origin: Malta residents → "Residents in Malta", EU relocating → "EU Nationals & Relocating Candidates", International → "International Applicants Welcome", Open → "Residents in Malta & Europeans".
- Immediate Start badge only appears when `Immediate Start: Yes` was provided.
- Urgency keywords only appear in the SEO package when `Immediate Start: Yes` was provided.
- Job detail metadata grid includes Category, Employment Type, Work Mode, Job Type, and Target Location.
- Off-page distribution checklist is included.
- Sitemap update and indexing API submission notes are included.
- Canonical tag points to the correct job page URL.
- Duplicate title risk has been assessed and flagged if applicable.
