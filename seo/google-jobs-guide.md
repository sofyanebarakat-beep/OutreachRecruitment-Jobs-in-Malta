# Google Jobs — Complete Implementation Guide
## Outreach Recruitment | outreachrecruitment.net

---

## What is Google Jobs?

Google Jobs is a free job search feature that surfaces job postings
directly in Google Search results as a rich result panel (carousel).
It draws from `JobPosting` structured data embedded in your job pages.

**Traffic value:** Google Jobs listings appear above organic results
and can drive direct applications without needing a paid job board.

---

## Requirements Checklist

### Required fields (Google will NOT index without these)
- [ ] `@type: "JobPosting"`
- [ ] `title` — matches the visible `<h1>` on the page exactly
- [ ] `description` — min 200 characters, plain text or HTML
- [ ] `datePosted` — ISO 8601 format: `YYYY-MM-DD`
- [ ] `hiringOrganization` with `name` and `sameAs`
- [ ] `jobLocation` with `address` (OR `jobLocationType: "TELECOMMUTE"`)

### Strongly recommended (boosts ranking and click-through)
- [ ] `validThrough` — expiry date; Google deprioritises expired jobs
- [ ] `baseSalary` — pages with salary get ~30% more clicks
- [ ] `employmentType` — FULL_TIME, PART_TIME, CONTRACTOR, etc.
- [ ] `directApply: true` — shows a "Direct Apply" badge
- [ ] `url` — canonical URL of the job posting

### Nice to have
- [ ] `skills`
- [ ] `educationRequirements`
- [ ] `experienceRequirements`
- [ ] `jobBenefits`
- [ ] `identifier` — your internal job ID

---

## Implementation Steps

### Step 1 — Add JobPosting schema to each job page

Copy `seo/schema-jobposting-template.html` and fill in all values.
Paste the `<script type="application/ld+json">` block inside `<head>`
of every job page (e.g. `jobs/barista.html`).

**Critical rule:** The `title` in your schema MUST match the `<h1>`
visible on the page. Google cross-checks them and will reject mismatches.

### Step 2 — Verify with Google's Rich Results Test

1. Deploy the page
2. Go to: https://search.google.com/test/rich-results
3. Enter the job page URL (e.g. `https://outreachrecruitment.net/jobs/barista`)
4. Check for `JobPosting` detection — fix any warnings

### Step 3 — Submit sitemap to Google Search Console

1. Go to: https://search.google.com/search-console
2. Add property: `https://outreachrecruitment.net`
3. Sitemaps → Submit:
   - `https://outreachrecruitment.net/sitemap_index.xml`
4. Request indexing for each job page individually

### Step 4 — Monitor in Search Console

- **Search Console → Search Results → Filter by page type: "Job"**
- Watch for: impressions, clicks, CTR
- **Enhancements → Job Postings** — shows indexing errors

---

## Per-Job Page Head Tag Template

```html
<!-- Inside <head> of jobs/JOB-SLUG.html -->

<title>JOB_TITLE in Malta | Outreach Recruitment</title>
<meta name="description" content="Apply for JOB_TITLE in CITY. SALARY. EMPLOYMENT_TYPE. Apply through Outreach Recruitment Agency."/>
<link rel="canonical" href="https://outreachrecruitment.net/jobs/JOB_SLUG"/>
<meta name="robots" content="index, follow"/>

<!-- Open Graph -->
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://outreachrecruitment.net/jobs/JOB_SLUG"/>
<meta property="og:title" content="JOB_TITLE in Malta | Outreach Recruitment"/>
<meta property="og:description" content="Apply for JOB_TITLE in Malta. Through Outreach Recruitment Agency."/>
<meta property="og:image" content="https://outreachrecruitment.net/assets/og-image.jpg"/>
<meta property="og:site_name" content="Outreach Recruitment"/>

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="JOB_TITLE in Malta | Outreach Recruitment"/>
<meta name="twitter:description" content="JOB_TITLE vacancy in Malta. Apply now."/>
<meta name="twitter:image" content="https://outreachrecruitment.net/assets/og-image.jpg"/>

<!-- JobPosting Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "JOB_TITLE",
  "description": "FULL_DESCRIPTION",
  "datePosted": "YYYY-MM-DD",
  "validThrough": "YYYY-MM-DD",
  "employmentType": "FULL_TIME",
  "url": "https://outreachrecruitment.net/jobs/JOB_SLUG",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "Outreach Recruitment",
    "sameAs": "https://outreachrecruitment.net",
    "logo": "https://outreachrecruitment.net/assets/outreach-recruitment-logo.svg"
  },
  "jobLocation": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Malta",
      "addressCountry": "MT"
    }
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "EUR",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": 1200,
      "maxValue": 1800,
      "unitText": "MONTH"
    }
  },
  "directApply": true,
  "applicationContact": {
    "@type": "ContactPoint",
    "email": "hr@outreachrecruitment.net"
  }
}
</script>

<!-- Breadcrumb Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://outreachrecruitment.net/" },
    { "@type": "ListItem", "position": 2, "name": "Jobs", "item": "https://outreachrecruitment.net/jobs" },
    { "@type": "ListItem", "position": 3, "name": "JOB_TITLE", "item": "https://outreachrecruitment.net/jobs/JOB_SLUG" }
  ]
}
</script>
```

---

## AI Search Optimisation (ChatGPT, Gemini, Perplexity)

AI search engines (ChatGPT Browse, Gemini, Perplexity) crawl your
site using your `robots.txt` and sitemap. To rank in AI search:

### 1 — Clear, factual entity language
On your homepage and about page, state directly:
- What you are: "Outreach Recruitment is a Malta-based recruitment agency"
- What you do: "We connect EU candidates with jobs in Malta and Europe"
- Who you serve: "Employers in Malta and job seekers across the EU"

AI models extract entity facts from the first 200 words of a page.

### 2 — FAQ content
Add FAQ sections to key pages with questions AI models are likely
to answer:
- "How do I find a job in Malta?"
- "What documents do I need to work in Malta?"
- "How does Outreach Recruitment work?"
- "What jobs are available in Malta for EU citizens?"

Use `FAQPage` schema alongside the visible content.

### 3 — Consistent NAP (Name / Address / Phone)
Ensure the same company name, email, and location appear on:
- Your website (every page footer)
- Google Business Profile
- LinkedIn company page
- Facebook page

### 4 — Add an llms.txt file (Perplexity / AI crawlers)
Create `/llms.txt` in your root — a plain-text summary of your site
for AI crawlers:

```
# Outreach Recruitment
> Malta's leading recruitment agency connecting EU candidates with jobs in Malta and Europe.

## About
Outreach Recruitment connects employers in Malta with qualified EU talent.
Services: candidate sourcing, CV screening, interview coordination, visa support.
Email: hr@outreachrecruitment.net
Website: https://outreachrecruitment.net

## Services
- Job placement in Malta
- Employer recruitment support
- Study in Malta guidance
- CV and career consultation

## Current Job Listings
See: https://outreachrecruitment.net/jobs
```

---

## Local SEO (Google Business Profile)

1. **Claim your Google Business Profile:**
   https://business.google.com
   - Category: "Employment Agency" (primary)
   - Additional: "Recruitment Agency", "Staffing Agency"

2. **Complete all fields:**
   - Business name: Outreach Recruitment
   - Website: https://outreachrecruitment.net
   - Email: hr@outreachrecruitment.net
   - Description: 750 chars describing your services
   - Hours: Mon–Fri 09:00–18:00

3. **Add LocalBusiness schema** (already in `schema-organization.html`)
   - The `@type: ["Organization", "LocalBusiness"]` covers both

4. **Geo meta tags** (already in `index.html`):
   ```html
   <meta name="geo.region" content="MT"/>
   <meta name="geo.placename" content="Malta"/>
   <meta name="geo.position" content="35.9375;14.3754"/>
   <meta name="ICBM" content="35.9375, 14.3754"/>
   ```

5. **Citations** — list your site on:
   - Malta Business Registry
   - Yellow Pages Malta (yellit.com)
   - Jobsplus.com.mt (Malta government job board)
   - LinkedIn Jobs
   - Indeed Malta

---

## Ongoing Maintenance

| Action | Frequency |
|---|---|
| Update `validThrough` on job pages | When a role is filled |
| Remove filled jobs from `sitemap-jobs.xml` | Immediately on fill |
| Add new jobs to `sitemap-jobs.xml` | On publication |
| Submit sitemap_index.xml to Search Console | On first deploy |
| Check Search Console for schema errors | Weekly |
| Review Google Jobs impressions | Monthly |
| Update `lastmod` in sitemaps | On each content change |

---

## Files in This SEO Setup

```
robots.txt                          ← Controls crawler access
sitemap_index.xml                   ← Master sitemap index
sitemaps/
  sitemap-pages.xml                 ← Core pages
  sitemap-jobs.xml                  ← Job pages (update as jobs change)
  sitemap-blog.xml                  ← Blog articles
seo/
  schema-organization.html          ← Organization schema (all pages)
  schema-website.html               ← WebSite schema (homepage only)
  schema-breadcrumb-template.html   ← Breadcrumb schema (per page)
  schema-jobposting-template.html   ← JobPosting schema (job pages)
  meta-tags-template.html           ← Title/OG/Twitter tags (per page)
  ga4-snippet.html                  ← Google Analytics 4
  google-jobs-guide.md              ← This file
```
