# Job SEO Output Template

Generate all sections below unless the user asks for only specific fields.

## Section 1 - SEO Package

- SEO Title, 60 characters max, format: Job Title Job in City, Malta | Outreach Recruitment
- Meta Title
- Meta Description, 120–155 characters, must include job title, city, and "Apply now"
- URL Slug
- Canonical URL
- Candidate Search Intent
- Primary Job Category
- Secondary Job Categories
- Primary Keyword
- Secondary Keywords
- Long Tail Keywords
- LSI Keywords
- Employer Keywords
- Industry Keywords
- Location Keywords
- Location Keyword Variations
- Industry Keyword Variations
- Career Level Keywords
- Open Graph Title
- Open Graph Description
- Open Graph Image recommendation
- Twitter Card Title
- Twitter Card Description
- Google Jobs Optimization Notes
- SERP Competitor Analysis
- Ranking Opportunity Notes

Keyword rules:

- Use long-tail, role-specific keywords wherever possible.
- Include Malta-focused modifiers for Malta roles.
- Include city-specific keywords only when a city is known.
- Include salary, visa, relocation, remote, or sponsorship keywords only when those details are visible and supported.
- Keep keyword lists useful for publishing, not stuffed or repetitive.

## Section 2 - Google Jobs Package

- Job Title
- H1
- Short Job Summary
- Primary Job Category
- Secondary Job Categories
- Employment Type (FULL_TIME / PART_TIME / CONTRACTOR / TEMPORARY / INTERN / VOLUNTEER / PER_DIEM / OTHER)
- Industry
- Sector
- Location (city)
- Country (Malta / MT)
- Remote Status (On-Site / Hybrid / Remote)
- Salary Range (visible on page, or Not disclosed)
- Salary Currency (EUR)
- Salary Visibility (Public / Private / Not specified)
- Job Type, default to `Direct Job` unless the user provides another type
- Target Location, default to `Residents in Malta & Europeans` unless the user provides another target
- Private Salary Note, only if the user provides salary but does not want it published
- Date Posted
- Valid Through (expiry date — must also be visible on the page)
- Job ID / Reference Number
- Hiring Organization (name, URL, logo)
- Application URL
- Application Method
- Direct Apply Status
- Work Hours / Shift Pattern
- Occupational Category
- Visa Sponsorship Status
- Work Permit Support
- Language Requirements
- Education Requirements
- Experience Requirements
- Qualifications and Certifications
- Responsibilities (as a separate field from description)
- Incentive Compensation (bonus, commission, tips — if applicable)
- Skills Required
- Benefits
- Suggested Internal Links (category hub, location hub, related jobs)
- Freshness / Update Notes
- Conversion Notes
- Sitemap Update Note
- Indexing API Submission Note

## Section 3 - AI Search Package

Create an AI-friendly version that ChatGPT, Gemini, Claude, Copilot, Perplexity, and other answer engines can understand and cite.

Include:

- Direct Answer Summary, 40-60 words
- AI Summary, about 100 words
- Key Facts Table:
  - Position
  - Industry
  - Location
  - Salary
  - Job Type
  - Target Location
  - Employment Type
  - Experience
  - Education
  - Language
  - Visa Support
  - Work Permit Support
  - Employer
  - Application Method
- Entity Mentions
- Candidate Fit Summary
- Related Candidate Questions

The direct answer summary should clearly state what the job is, where it is based, the employment type, and who should apply.

## Section 4 - Job Content

Write a fully optimized job page with all sections below. Target at least 1000 words for full page copy. Use proper H2 and H3 headings. If the source job description is too thin, expand responsibly without inventing unsupported benefits, salary, visa sponsorship, or employer-specific claims.

Include:

- Job Highlights block (salary if visible, employment type, location, work mode, experience, working hours) — place near the top of the page
- Badges (Immediate Start / Training Provided / Full-Time Position / Visa Sponsorship Available / Career Growth Opportunities / Relocation Assistance / Language Bonus) — include only badges supported by the job details
- Introduction paragraph
- About the Role — 2–3 paragraphs
- Key Responsibilities — bulleted list
- Key Requirements — required skills, experience, and qualifications
- Skills Required — specific tools, software, certifications, platforms
- Preferred Qualifications — nice-to-have items
- Languages Required — only when stated or clearly required
- What We Offer — benefits, work environment, salary range if visible
- Career Growth Opportunities — only when supported by the job details
- About the Company — anonymised paragraph, for example "Our client is a well-established hotel group based in St Julian's" — do not invent employer-specific claims
- Visa Sponsorship and Relocation Assistance — include only when explicitly stated
- Reporting To — include only when the reporting line is stated or can be inferred
- Contract Duration — include for temporary or fixed-term roles
- Application Deadline — visible date matching validThrough
- Neighbourhood or Location Description — one sentence describing the area, for example "Located in St Julian's, near Spinola Bay and the Paceville entertainment district" — include when the city is known
- Response Timeline — always include: "We aim to respond to all applications within 3–5 business days"
- Why Join This Company
- About Outreach Recruitment
- How To Apply — clear instructions, reference number, and application URL
- Closing Statement
- FAQ Section with 4-6 questions and answers
- Similar Jobs — 3–5 links to related open roles
- Latest Jobs — 3–5 links to the most recently posted jobs
- People Also Viewed — 3–5 links to roles candidates commonly compare

FAQ guidance:

- Answer candidate questions directly.
- Include the job title and location naturally where useful.
- Cover application process, experience, employment type, location, salary only if visible, and work permit/visa only if supported.
- Do not repeat the same answer in different words.

## Section 5 - JobPosting JSON-LD Content Plan

Provide a complete, ready-to-use JSON-LD plan for the JobPosting schema.

Include values for:

- `@context`: `https://schema.org`
- `@type`: `JobPosting`
- `title`
- `description`
- `datePosted`
- `validThrough`
- `employmentType`
- `workHours`
- `occupationalCategory`
- `industry`
- `identifier` (PropertyValue with reference number)
- `hiringOrganization` (name, sameAs, logo)
- `jobLocation` (streetAddress, addressLocality, addressRegion, addressCountry)
- `applicantLocationRequirements` — if remote or location-restricted
- `jobLocationType` — TELECOMMUTE only for fully remote roles
- `baseSalary` — only when salary is visible on the page (minValue, maxValue, unitText, @type: QuantitativeValue)
- `salaryCurrency` — EUR, required whenever baseSalary is included
- `experienceRequirements`
- `educationRequirements`
- `qualifications`
- `responsibilities`
- `incentiveCompensation` — only when bonus, commission, or tips apply
- `skills`
- `jobBenefits`
- `directApply`

Also include:

- `BreadcrumbList` schema block: Home → Jobs → Category → Job Title
- `FAQPage` schema block: matching the visible FAQ section
- `ImageObject` schema block: url, width, height, caption for the featured image

Include:

- Schema fields to include
- Schema fields to omit because details are not specified
- Schema warning notes for salary, remote status, visa sponsorship, work permit support, benefits, education, experience, location, working hours, and expiry date

Salary schema rule:

- Include `baseSalary` only when the same salary is visible on the job page.
- If salary is private or not meant to be displayed, mark visible salary as `Not disclosed` or `Not specified` and omit `baseSalary`.
- Do not add hidden salary only for SEO.
- Always pair `baseSalary` with `salaryCurrency: EUR`.

## Section 6 - Internal Linking Plan

Suggest relevant internal links for:

- Main jobs page: `/jobs/`
- Primary category hub page (e.g. `hospitality-jobs-in-malta.html`)
- Secondary category hub pages
- Location hub page (e.g. `jobs-in-st-julians.html`) when the city matches
- 3–5 related open job pages with descriptive anchor text
- Blog posts or guides relevant to the industry or role
- Jobs index page for the new job card link

Also flag:

- Which category hub pages should link back to this job page
- Which location hub pages should link back to this job page
- Whether the job is currently orphaned from all category pages

Use descriptive anchor text. Do not suggest irrelevant links just to add more links.

## Section 7 - SERP and Competitor Plan

Identify likely competing result types:

- Job boards
- Recruitment agencies
- Employer career pages
- LinkedIn jobs
- Indeed, JobsinMalta, Keepmeposted, and other Malta job platforms
- Government, industry, or professional body pages when relevant

Include:

- Main competitors by page type
- Why candidates may click those pages
- How this job page can compete
- Content gaps this job page should fill
- FAQ or structured data opportunities

## Section 8 - Entity SEO Plan

List the important entities to include naturally:

- Job title and synonyms
- Job category
- Industry and sector
- Location city, region, and Malta
- Employment type and seniority
- Skills, tools, certifications, licenses, and languages
- Employer
- Application method
- Reference number
- Neighbourhood or area description when city is known

Do not include unsupported entities.

## Section 9 - Freshness and Conversion Plan

Include:

- Date posted
- Valid through / expiry date (must be visible on the page)
- Whether the job appears active
- Recommended refresh timing: every 14–30 days
- Apply call-to-action
- Application URL
- Reference number
- Response timeline: "We aim to respond within 3–5 business days"
- Candidate friction points to avoid
- Sitemap lastmod update note
- Google Search Console resubmission note
- Google Indexing API submission note

## Section 10 - Duplicate Content Prevention Notes

Include:

- Unique angle for this job page
- Role-specific details used
- Generic text to avoid
- Similar-job duplication risks
- Duplicate title risk assessment — flag if another job page has the same title
- Recommendations for making the page more distinct

## Section 11 - Site Publishing Plan

When the user asks to add the job to the Outreach Recruitment website, include:

- Job listing page URL: `https://outreachrecruitment.net/jobs/`
- Local listing file to update, usually `jobs/index.html`
- Target grid: `opening-jobs-grid`
- New job card HTML plan
- Job detail page path: `/jobs/{seo-slug}/`
- Card link path: `/jobs/{seo-slug}/`
- Card title
- Card location
- Card employment type
- Card category
- Card badges (if applicable)
- Job detail metadata grid must show: `Category`, `Employment Type`, `Work Mode`, `Job Type`, and `Target Location`
- Use `Job Type: Direct Job` unless the user provides another job type
- Use `Target Location: Residents in Malta & Europeans` unless the user provides another target location
- Do not show the old `Salary` card in the metadata grid
- Card `data-title`
- Card `data-category`
- Card `data-location`
- Card `data-date`
- Whether the card should be first in the grid
- Old open-position count
- New open-position count
- Count labels to update: `+{count} Open Positions`, `Showing {count} jobs`, `.or-counter-num`, `open positions now`
- Sitemap entry to add: URL, lastmod, priority
- Sitemap index lastmod to update
- Category hub pages to update with a link to this job
- Location hub pages to update with a link to this job
- Google Indexing API command to run after publishing

Publishing rules:

- Insert the new active job as the first card in `opening-jobs-grid`.
- Mark it as new/latest using the existing card pattern.
- Increase the count by 1 for one new active job, or by the number of active jobs added.
- Do not hard-code a count number; read the current count and increment it.
- Keep all visible counts consistent.
- Do not increase counts for draft, expired, duplicate, or unpublished jobs.

## Section 12 - Image SEO Plan

Include:

- Recommended image filename: `{job-title}-job-malta.jpg` or `.webp`
- ALT tag: `{Job Title} job opportunity in {City}, Malta — Outreach Recruitment`
- ImageObject schema: url, width, height, caption
- Open Graph image recommendation
- Note: compress all images to WebP for performance
- Note: add explicit width and height attributes to prevent CLS
- Note: use lazy loading for images below the fold

## Section 13 - Off-Page Distribution Plan

Include a checklist of off-page actions to take after publishing:

- Post on LinkedIn company page with the direct job page URL
- Post on Facebook with the direct job page URL — Facebook links index fast
- Submit to Indeed (free) — creates a backlink and cross-platform authority signal
- Submit to Glassdoor
- Submit to Jooble
- Submit to Jobrapido
- Submit to MaltaPark
- Publish a supporting article or note on Medium if the role is senior or specialist
- Share in Malta career communities and relevant directories
- Post on Google Business Profile with the direct apply link
- Share on Instagram story with a link in bio

## Section 14 - Advanced Schema Plan

List additional schema types relevant to this page and surrounding site structure:

For this job page:
- `JobPosting` — covered in Section 5
- `BreadcrumbList` — covered in Section 5
- `FAQPage` — covered in Section 5
- `ImageObject` — covered in Section 12

For the category hub page linked from this job:
- `CollectionPage`
- `ItemList` with each job as a `ListItem`
- `BreadcrumbList`

For the main jobs index page:
- `WebSite` with `SearchAction`
- `Organization`

For the homepage and contact page:
- `LocalBusiness`
- `ContactPage`

## Section 15 - Advanced SEO Recommendations

Include the following recommendations when relevant to this job or role type:

- RSS feed: recommend adding this job category to the relevant RSS feed (Latest Jobs, Hospitality Jobs, Marine Jobs, IT Jobs)
- Job collection: recommend adding this job to relevant collection pages (Latest Jobs in Malta, Full-Time Jobs in Malta, etc.)
- Author and publisher info: `"author": "Outreach Recruitment"` and `dateModified` on the job page
- Pagination schema: `rel="next"` and `rel="prev"` on paginated job listing pages
- hreflang: recommend adding language tags if targeting French or Arabic-speaking job seekers
- Core Web Vitals note: flag if images need WebP conversion, lazy loading, or if scripts should be deferred to improve LCP below 2.5 seconds
- HTML sitemap: recommend this job is added to the HTML sitemap page
- Video: recommend adding a short "work with us" video if available — unlocks video rich results in Google
- Google Business Profile: create a GBP post for this vacancy with the direct apply link

## Section 16 - SEO Quality Checklist

Confirm all of the following before finalizing:

- Meta title follows the format: Job Title Job in City, Malta | Outreach Recruitment
- Meta title is under 60 characters
- Meta title contains the word "Job" or "Jobs"
- Meta title contains "Malta" for Malta roles
- Meta description is between 120 and 155 characters
- Meta description includes "Apply now" or "Apply today"
- Slug is lowercase, short, hyphenated, and does not include dates or salary
- Primary keyword appears naturally in the SEO title, H1, first paragraph, and meta description
- Canonical URL points to the correct job page URL
- Open Graph tags are present: og:title, og:description, og:image, og:url, og:type
- Job title matches the visible page H1
- Location is consistent across visible content and schema fields
- Salary appears only if visible on the page
- baseSalary paired with salaryCurrency: EUR
- validThrough is present in schema and visible on the page
- employmentType is present and matches visible content
- experienceRequirements is present and visible on the page
- educationRequirements is present and visible on the page
- qualifications field is present when certifications or licences apply
- responsibilities is a separate schema field
- skills field is present and matches the Skills Required section
- jobBenefits field is present when a benefits section is on the page
- workHours field is present when hours or shift pattern is stated
- BreadcrumbList schema is included
- FAQPage schema matches the visible FAQ section
- ImageObject schema is included for the featured image
- Job Highlights block is present near the top of the page
- Neighbourhood description is included when the city is known
- Response timeline statement is included
- Similar Jobs section is present
- Latest Jobs section is present
- People Also Viewed section is present
- Application deadline is visible on the page
- Page word count is at least 300 words
- About the Company paragraph is present
- Job detail metadata grid includes Category, Employment Type, Work Mode, Job Type, and Target Location
- Visa, work permit, remote, relocation, and benefits claims are included only when supported
- FAQ answers are useful for candidates and answer-engine visibility
- JobPosting schema content matches the visible page exactly
- Category mapping is relevant
- Duplicate title risk has been assessed
- Internal links include the category hub page and location hub page
- Off-page distribution checklist is included
- Sitemap entry is included in the site publishing plan
- Indexing API submission note is included
- No unsupported salary, visa sponsorship, work permit support, remote work, relocation, benefits, or urgency claims are added
- If publishing to the website, the new job is first in `opening-jobs-grid`
- If publishing to the website, all open-position counts were increased consistently
