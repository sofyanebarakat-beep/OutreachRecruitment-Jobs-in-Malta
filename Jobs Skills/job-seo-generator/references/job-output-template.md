# Job SEO Output Template

Generate all sections below unless the user asks for only specific fields.

## Section 1 - SEO Package

- SEO Title, 60 characters max
- Meta Title
- Meta Description, 155 characters max
- URL Slug
- Canonical URL
- Primary Keyword
- Secondary Keywords
- Long Tail Keywords
- LSI Keywords
- Employer Keywords
- Industry Keywords
- Location Keywords
- Open Graph Title
- Open Graph Description
- Twitter Card Title
- Twitter Card Description

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

## Section 3 - AI Search Package

Create an AI-friendly version that ChatGPT, Gemini, Claude, Copilot, Perplexity, and other answer engines can understand and cite.

Include:

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

Target at least 1000 words when the user requests full page copy. Use proper H2 and H3 headings. If the source job description is too thin, expand responsibly without inventing unsupported benefits, salary, visa sponsorship, or employer-specific claims.

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
