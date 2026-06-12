# Job SEO Output Template

Generate all sections below unless the user asks for only specific fields.

## Section 1 - SEO Package

- SEO Title, 60 characters max
- Meta Title
- Meta Description, 155 characters max
- URL Slug
- Canonical URL
- Candidate Search Intent
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
- Employment Type
- Industry
- Sector
- Location
- Country
- Remote Status
- Salary
- Salary Currency
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

## Section 6 - Internal Linking Plan

Suggest relevant internal links for:

- Main jobs page
- Job category page
- Location page
- Industry page
- Related jobs page
- Employer or recruitment service page, when relevant

Use descriptive anchor text. Do not suggest irrelevant links just to add more links.

## Section 7 - SEO Quality Checklist

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
