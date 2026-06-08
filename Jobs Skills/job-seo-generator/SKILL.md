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
3. Generate every requested section in the template.
4. Keep all generated structured-data fields aligned with visible page content.
5. Avoid keyword stuffing, fake locations, fake salaries, fake benefits, and unsupported visa/work permit claims.
6. Use Malta-focused SEO when the role is located in Malta.
7. Make the job title concise and clean. Do not include salary, employer, location, dates, or promotional words in the schema `title`.

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

## Quality Checks

Before finalizing, verify:

- Job title matches the visible page title.
- Location city, region, and country are realistic and consistent.
- Employer is `Outreach Recruitment Ltd` unless the user provides another authorized hiring organization.
- Salary appears only if it will also be visible on the page.
- Expiry date is present for active job postings when possible.
- Application URL uses the Outreach Recruitment careers platform unless the user provides a role-specific apply URL.
- The output can be translated into valid `JobPosting` JSON-LD without adding hidden facts.
