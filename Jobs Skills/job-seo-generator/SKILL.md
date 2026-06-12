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
- SEO title under 60 characters
- Meta description under 155 characters
- 4-6 FAQ questions and answers
- Internal linking suggestions
- Short AI-search answer summary
- Google Jobs optimization notes

Use the main job title, location, industry, seniority, and employment type naturally. Avoid repeating the same keyword too many times.

## Keyword Targeting Rules

- Prefer long-tail, role-specific keywords over generic terms.
- Use Malta location modifiers for Malta roles, such as `jobs in Malta`, `{job title} jobs Malta`, `{industry} jobs in Malta`, and `{city} jobs`.
- Include city-specific modifiers only when the city is known or clearly supported.
- Include salary keywords only when salary is visible on the page.
- Include visa, relocation, sponsorship, or work permit keywords only when explicitly provided or clearly supported.
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

## Site Publishing Rules

When the user asks to add a generated job to the Outreach Recruitment website, complete these site updates after creating the job content:

- Add the new job to `https://outreachrecruitment.net/jobs/` in the `opening-jobs-grid`.
- In the local project, update the jobs listing source that contains `id="opening-jobs-grid"`, usually `jobs/index.html`.
- Insert the new job card as the first job in `opening-jobs-grid` so it appears as the newest opening.
- Mark the new card as latest/new using the existing card pattern, such as `data-opening-job`, `data-featured="true"`, `data-latest="true"`, and `<div class="opening-card-day">New</div>`.
- Use the generated job slug for the card link, for example `/jobs/{seo-slug}/`.
- Use the generated job title, location, employment type, category, and date in the card fields and `data-*` attributes.
- Create or update the individual job detail page at `/jobs/{seo-slug}/` when the user asks for the full site implementation.
- Increase the open-position count by 1 from the current value. For example, if the page currently says `+217 Open Positions`, `Showing 217 jobs`, and `<span class="heading-h4 or-counter-num">217</span>`, update all of them to `218`.
- Keep every visible count consistent, including `+{count} Open Positions`, `Showing {count} jobs`, tab/filter labels, and any `.or-counter-num` value followed by `open positions now`.
- Do not hard-code `217`; always read the current count and increment it by the number of new active jobs being added.
- If the site has JavaScript that derives counters from the actual number of job cards, still verify the visible fallback/static counts are consistent.
- After editing, search the repo for the old count and new count to ensure no visible job counters were missed.
- Do not increase counts for draft, expired, duplicate, or unpublished jobs.

## Output Rules

- Output all template sections unless the user asks for a smaller subset.
- Use natural human language.
- Generate unique content for each job.
- Use HTML-friendly headings when writing long job page content.
- Keep meta descriptions under 155 characters.
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
- Location city, region, and country are realistic and consistent.
- Employer is `Outreach Recruitment Ltd` unless the user provides another authorized hiring organization.
- Salary appears only if it will also be visible on the page.
- Expiry date is present for active job postings when possible.
- Application URL uses the Outreach Recruitment careers platform unless the user provides a role-specific apply URL.
- The output can be translated into valid `JobPosting` JSON-LD without adding hidden facts.
- Primary keyword appears naturally in the SEO title, H1, first paragraph, and meta description.
- SEO title is under 60 characters.
- Meta description is under 155 characters.
- Slug is lowercase, short, hyphenated, and relevant.
- FAQ answers are direct, useful, and not repetitive.
- Internal links are relevant to the role, industry, or location.
- Content is unique and not copied from a generic job description.
- No unsupported salary, visa sponsorship, work permit support, remote work, relocation, benefits, or urgency claims are added.
