# Job SEO Output Template

Generate all sections below unless the user asks for only specific fields.

## Section 1 - SEO Package

- SEO Title, 60 characters max
- Meta Title
- Meta Description, 155 characters max
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
- Employment Type
- Industry
- Sector
- Location
- Country
- Remote Status
- Salary
- Salary Currency
- Salary Visibility
- Private Salary Note, only if the user provides salary but does not want it published
- Date Posted
- Valid Through
- Job ID
- Hiring Organization
- Application URL
- Application Method
- Visa Sponsorship Status
- Work Permit Support
- Language Requirements
- Education Requirements
- Experience Requirements
- Working Hours
- Benefits
- Direct Apply Status
- Suggested Internal Links
- Freshness / Update Notes
- Conversion Notes

## Section 3 - AI Search Package

Create an AI-friendly version that ChatGPT, Gemini, Claude, Copilot, Perplexity, and other answer engines can understand and cite.

Include:

- Direct Answer Summary, 40-60 words
- AI Summary, about 100 words
- Key Facts Table
- Position
- Industry
- Location
- Salary
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

Write a fully optimized job page.

Include:

- Introduction
- About the Role
- Key Responsibilities
- Requirements
- Preferred Qualifications
- Benefits
- Why Join This Company
- About Outreach Recruitment
- How To Apply
- Closing Statement
- FAQ Section with 4-6 questions and answers

Target at least 1000 words when the user requests full page copy. Use proper H2 and H3 headings. If the source job description is too thin, expand responsibly without inventing unsupported benefits, salary, visa sponsorship, or employer-specific claims.

FAQ guidance:

- Answer candidate questions directly.
- Include the job title and location naturally where useful.
- Cover application process, experience, employment type, location, salary only if visible, and work permit/visa only if supported.
- Do not repeat the same answer in different words.

## Section 5 - JobPosting JSON-LD Content Plan

Provide a content-ready plan for schema fields:

- `@context`
- `@type`
- `title`
- `description`
- `datePosted`
- `validThrough`
- `employmentType`
- `identifier`
- `hiringOrganization`
- `jobLocation`
- `applicantLocationRequirements`, if remote or location-restricted
- `jobLocationType`, if remote
- `baseSalary`, if visible salary is available
- `educationRequirements`
- `experienceRequirements`
- `industry`
- `occupationalCategory`, if inferable
- `directApply`, if the application flow is direct

Do not add hidden structured data that is not visible or clearly supported by the page content.

Also include:

- Schema fields to include
- Schema fields to omit because details are not specified
- Schema warning notes for salary, remote status, visa sponsorship, work permit support, benefits, education, experience, location, working hours, and expiry date

Salary schema rule:

- Include `baseSalary` only when the same salary is visible on the job page.
- If salary is private or not meant to be displayed, mark visible salary as `Not disclosed` or `Not specified` and omit `baseSalary`.
- Do not add hidden salary only for SEO.

## Section 6 - Internal Linking Plan

Suggest relevant internal links for:

- Main jobs page
- Job category page
- Location page
- Industry page
- Related jobs page
- Employer or recruitment service page, when relevant

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

Do not include unsupported entities.

## Section 9 - Freshness and Conversion Plan

Include:

- Date posted
- Valid through / expiry date
- Whether the job appears active
- Recommended refresh timing
- Apply call-to-action
- Application URL
- Reference number
- Candidate friction points to avoid

## Section 10 - Duplicate Content Prevention Notes

Include:

- Unique angle for this job page
- Role-specific details used
- Generic text to avoid
- Similar-job duplication risks
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
- Card `data-title`
- Card `data-category`
- Card `data-location`
- Card `data-date`
- Whether the card should be first in the grid
- Old open-position count
- New open-position count
- Count labels to update, including `+{count} Open Positions`, `Showing {count} jobs`, `.or-counter-num`, and `open positions now`

Publishing rules:

- Insert the new active job as the first card in `opening-jobs-grid`.
- Mark it as new/latest using the existing card pattern.
- Increase the count by 1 for one new active job, or by the number of active jobs added.
- Do not hard-code `217`; read the current count and increment it.
- Keep all visible counts consistent.
- Do not increase counts for draft, expired, duplicate, or unpublished jobs.

## Section 12 - SEO Quality Checklist

Confirm:

- Primary keyword appears naturally in the SEO title, H1, first paragraph, and meta description.
- SEO title is under 60 characters.
- Meta description is under 155 characters.
- Slug is lowercase, short, hyphenated, and does not include dates or salary.
- Job title is concise and not keyword-stuffed.
- Location is consistent across visible content and schema fields.
- Salary is included only if visible in the page content.
- Visa, work permit, remote, relocation, and benefits claims are included only when supported.
- FAQ answers are useful for candidates and answer-engine visibility.
- JobPosting schema content matches the visible page exactly.
- Category mapping is relevant.
- SERP competitor plan is realistic.
- Entity list contains only supported or safely inferable entities.
- Freshness and expiry details are not invented.
- Apply instructions are clear and conversion-focused.
- Duplicate content risks have been reduced.
- If publishing to the website, the new job is first in `opening-jobs-grid`.
- If publishing to the website, all open-position counts were increased consistently.
