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
