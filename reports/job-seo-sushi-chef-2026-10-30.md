# Job SEO Package — Sushi Chef (St. Julian's, Malta)

Source: https://outreach-recruitment-agency.careers-page.com/jobs/09692c92-ffc9-4ef7-864b-3b71329f209b
Apply: https://outreach-recruitment-agency.careers-page.com/jobs/09692c92-ffc9-4ef7-864b-3b71329f209b/apply
Published URL: https://outreachrecruitment.net/jobs/sushi-chef
Private reference (NOT displayed on the page; kept in an HTML comment only): `OR-SUSH-2026-002`
Private deadline (schema `validThrough` only, NOT displayed): `2029-12-30`

## Section 1 — SEO Package

- SEO title: `Sushi Chef Job in St. Julian's, Malta | Outreach Recruitment` (≤ 60 chars)
- Meta description: `Sushi Chef job in St. Julian's, Malta at a prestigious Asian-inspired restaurant. €1,900 per month, full-time. Apply now with Outreach Recruitment.`
- URL slug: `sushi-chef` — reuses the address of the expired June 2026 Sushi Chef posting (old ATS id `c1d869fe…`), so the URL keeps its search history instead of creating a second "Sushi Chef" page.
- Canonical: `https://outreachrecruitment.net/jobs/sushi-chef`
- Candidate search intent: experienced sushi / Japanese-cuisine chefs looking for a full-time kitchen role in Malta's main dining district.
- Primary category: Hospitality
- Primary keyword: Sushi chef job Malta
- Secondary keywords: sushi chef St Julian's, Japanese chef jobs Malta, chef jobs St Julian's, restaurant chef jobs Malta, hospitality jobs Malta
- Long-tail keywords: full-time sushi chef job St Julian's Malta €1,900; sushi chef vacancy high-end restaurant Malta; Japanese cuisine chef job Malta
- LSI keywords: sashimi, nigiri, maki, seafood handling, knife skills, HACCP, Asian-inspired cuisine, Head Chef
- Open Graph image: https://outreachrecruitment.net/assets/jobs-malta-hospitality.png
- Google Jobs: full `JobPosting` with `baseSalary` €1,900 / MONTH (from the careers-page schema), `directApply: true`, private `validThrough`.

## Section 2 — Google Jobs Package

- Title / H1: Sushi Chef
- Employment type: FULL_TIME · Work mode: On-Site · Job type: Direct Job
- Location: St. Julian's, Malta
- Industry: Hospitality — Restaurants & Japanese Cuisine · Occupational category: 35-1011.00 Chefs and Head Cooks
- Salary: €1,900 per month (source: careers-page `baseSalary`; "gross" not stated, so not written)
- Target Location: Residents in Malta & Europeans
- Date posted: 2026-10-30 · Valid through (private): 2029-12-30
- Work hours: full-time, evenings, weekends and public holidays
- Experience: previous Sushi Chef experience in a reputable or high-end restaurant
- Languages: good command of English. The careers page mentions Japanese *cuisine* only — Japanese language is NOT a requirement (the fact-sheet parser flagged "Japanese" from the cuisine wording; ignored).
- Visa / relocation / accommodation: not stated — omitted.

## Section 3 — AI Search Package

Direct answer: Sushi Chef is a full-time, on-site vacancy in St. Julian's, Malta, advertised by Outreach Recruitment for a prestigious international restaurant specialising in Asian-inspired cuisine. The chef prepares sushi, sashimi, nigiri, maki and other Japanese specialities to high-end standards. Previous sushi chef experience, strong knife skills, HACCP knowledge and good English are required. Pay: €1,900 per month. Apply online through Outreach Recruitment.

Related questions (all answered in the visible FAQ + FAQPage schema): pay · type of restaurant · experience needed · dishes prepared · working hours · language required.

## Section 4 — Job Content

Built from `tools/job_specs/sushi-chef.json`: About the Role (3 paragraphs), Key Responsibilities (10), Requirements (10), What's on Offer (6), Skills (6), Preferred (2), Languages, About the Company, Location (St. Julian's), How To Apply, 6 job-specific FAQs. All duties and requirements are taken from the careers-page description.

## Section 5 — JobPosting JSON-LD Content Plan

Included: title, description, identifier, url, datePosted, dateModified, validThrough (private), employmentType, workHours, industry, occupationalCategory, baseSalary (EUR 1,900 MONTH), hiringOrganization, jobLocation, experienceRequirements, qualifications, responsibilities, skills, jobBenefits, directApply. Supporting: BreadcrumbList, FAQPage (= visible FAQ), ImageObject.

## Section 6 — Internal Linking Plan

- `/jobs/` (main index — card added, ItemList position 1)
- Hub: `/hospitality-jobs-in-malta` (breadcrumb + extra links; the hub's ItemList already lists `/jobs/sushi-chef/`)
- Similar jobs (open Hospitality jobs): Host / Receptionist, Hotel Maintenance Assistant, Housekeeper (Rabat), Receptionist

## Section 7 — SERP and Competitor Plan

Competes with JobsinMalta, Indeed Malta, Keepmeposted and LinkedIn listings. Advantage: published salary, precise duties, 6 FAQs, full JobPosting data for Google for Jobs.

## Section 8 — Entity SEO Plan

Sushi Chef, St. Julian's, Malta, Hospitality, Japanese cuisine, Asian-inspired restaurant, sashimi, nigiri, maki, HACCP, Head Chef, Outreach Recruitment. No unsupported entities (visa, accommodation, Japanese language).

## Section 9 — Freshness and Conversion Plan

- Posted 2026-10-30; the daily job sync keeps it open/closed in line with the careers page (matched by UUID).
- CTAs: header Apply Now, sidebar, How To Apply, mobile CTA bar → embedded ATS form for this UUID only.
- Response timeline: 3–5 business days.

## Section 10 — Duplicate Content Prevention Notes

The previous Sushi Chef page (same slug, expired posting) was rebuilt in place and its expired registry entry removed, so there is one Sushi Chef page, not two. Content is new and based on the October 2026 listing.

## Section 11 — Site Publishing Plan

- Registry: expired `sushi-chef` entry (ATS `c1d869fe…`) removed; new entry added — Hospitality, `St. Julian's, Malta`, salary `€1,900 per month`, `valid_through` 2029-12-30, apply_url `09692c92…/apply` (checked unique in the registry).
- Pages: `jobs/sushi-chef/index.html` and `jobs/sushi-chef.html` (byte-identical).
- `python3 tools/update_jobs_listing.py` → `/jobs/` grid, counts, filters and `sitemaps/sitemap-jobs.xml` rebuilt.
- `jobs/index.html` ItemList JSON-LD: Sushi Chef inserted at position 1, renumbered, `numberOfItems` 118.
- Fact sheet saved: `tools/ats_snapshots/09692c92-ffc9-4ef7-864b-3b71329f209b.json`.

## Section 12 — SEO Quality Checklist

- [x] SEO title ≤ 60 chars; meta description 120–155 chars with salary and "Apply now"
- [x] Salary from source shown in header chip, sidebar, offer list, FAQ, meta description and schema
- [x] Reference number and deadline not visible
- [x] FAQ closed by default; FAQPage = visible FAQ
- [x] Only this job's ATS UUID on the page; old UUID `c1d869fe…` fully removed
- [x] `python3 tools/verify_job_page.py sushi-chef` → OK ✅
- [x] No template leftovers (Crane / Mqabba / old uuid)
