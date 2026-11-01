# Job SEO Package — Back Office Administrator (Gżira, Malta)

Source: https://outreach-recruitment-agency.careers-page.com/jobs/a76cf000-1af2-4763-aa11-82eddec33737
Posted on the careers page: 2026-10-30 · Built: 2026-11-01 · Page: https://outreachrecruitment.net/jobs/back-office-administrator
Spec (rebuild any time): `tools/job_specs/back-office-administrator.json` → `python3 tools/build_job_page.py tools/job_specs/back-office-administrator.json`
Inputs: Full-time · Direct Job · On-site · Candidate Origin: Open (not stated) · Immediate Start: Not stated · Salary **Competitive salary** (none on the careers page)

## 1 SEO
- Meta title (56): Back Office Administrator Job in Gżira, Malta | Outreach
- Meta description (148): Back Office Administrator job in Gżira, Malta with an automotive aftersales team. Full-time, competitive salary, health insurance. Apply now online.
- Slug: `back-office-administrator` · Canonical: https://outreachrecruitment.net/jobs/back-office-administrator
- Search intent: Office administrators and customer service staff with some motor-vehicle knowledge looking for an aftersales back-office role in Gżira.
- Primary keyword: back office administrator job Malta · Secondary: admin jobs Gżira, aftersales administrator Malta, service booking administrator job, automotive office jobs Malta, CRM administrator job Malta
- Long-tail: back office administrator job in Gżira Malta, automotive aftersales back office administrator full-time, service appointment administrator car workshop Malta
- OG/Twitter title = meta title; OG/Twitter description = meta description; image /assets/jobs-malta-hr-admin.png

## 2 Google Jobs
FULL_TIME · Direct Job · Gżira, Malta (MT) · On-site · no baseSalary (careers page gives none) · Target "Residents in Malta & Europeans" (no applicantLocationRequirements) · category Administration · industry Automotive — Aftersales Administration · occupationalCategory 43-9061.00 Office Clerks, General · education: Minimum O-Level standard of education · experience: Previous experience in administration, customer service or a similar role will be considered an advantage · languages: English · work hours: Full-time, on-site · apply online at https://outreach-recruitment-agency.careers-page.com/jobs/a76cf000-1af2-4763-aa11-82eddec33737/apply · validThrough 2029-12-30 (private) · reference OR-BOAD-2026-001 (private, HTML comment only) · no visa/work-permit claims.

## 3 AI search
Direct answer: Outreach Recruitment is recruiting on behalf of our client, a well-established company within Malta's automotive industry, for an organised and customer-focused Back Office Administrator to join its aftersales team in Gżira. It is a full-time, on-site role in Gżira with a competitive salary; apply online through Outreach Recruitment.

## 4 Content on the page
Badges New / Direct Job / Full-Time; chips Administration · Competitive salary · Full-Time · Gżira, Malta; About the Role (3), Key Responsibilities (13), Requirements (10), What's on Offer (6), Skills (6), Preferred Qualifications (1), Languages (1), About the Company, Location (Gżira), About Outreach Recruitment, How To Apply. All facts come from the careers-page fact sheet `tools/ats_snapshots/a76cf000-1af2-4763-aa11-82eddec33737.json`; nothing invented. English is the site default (the careers page names no language).

## 5 JobPosting JSON-LD
title, description (HTML of the visible sections), datePosted 2026-10-30, dateModified 2026-11-01, validThrough 2029-12-30, employmentType FULL_TIME, hiringOrganization Outreach Recruitment Ltd, jobLocation Gżira MT, identifier = slug, industry + occupationalCategory, experienceRequirements, educationRequirements, qualifications, responsibilities, skills, jobBenefits, workHours, directApply. No baseSalary (careers page gives none). Omitted (not in source): incentiveCompensation, jobImmediateStart, applicantLocationRequirements.

## 6 Internal linking
Breadcrumb Home › Jobs in Malta › Customer Service Jobs in Malta › Back Office Administrator; How-to-apply links: Customer Service Jobs in Malta, Malta salary calculator, All jobs in Malta; Similar jobs (open only): warranty-administrator, leasing-administration-officer, aftersales-receptionist, senior-clerk. Note: there is no Administration hub page yet, so the breadcrumb uses Customer Service Jobs in Malta (same as senior-clerk).

## 7 SERP / competitors
Keepmeposted, jobsplus.gov.mt, Indeed MT and LinkedIn for "back office administrator Malta". Edge: automotive-specific duties, FAQ rich content, direct apply.

## 8 Entity SEO
Outreach Recruitment Ltd (recruiter, Malta) · Gżira, Malta · automotive industry · Aftersales, workshop, CRM, job cards, recalls, invoices, warranty documentation · role entity "Back Office Administrator" · O*NET 43-9061.00 Office Clerks, General.

## 9 Freshness & conversion
dateModified set on build; the daily sync keeps the page in step with the careers page and closes it when the ATS job closes. Apply panel + sticky apply buttons point to this job's careers-page apply form only.

## 10 Duplicate-content prevention
Unique slug and copy rewritten from the source; five Gżira automotive roles were posted the same day, so each intro, location sentence and FAQ set is written separately. Canonical to /jobs/back-office-administrator; flat jobs/back-office-administrator.html is byte-identical to jobs/back-office-administrator/index.html (GitHub Pages serves the flat file first). No other page has this title.

## 11 Publishing
Files: jobs/back-office-administrator/index.html, jobs/back-office-administrator.html; registry entry in tools/jobs_registry.json (category Administration, valid_through 2029-12-30, no salary, no status). FAQ (6, closed by default): What does a Back Office Administrator do here?; Is a salary stated for this role?; Do I need automotive knowledge?; What education is required?; Is training provided?; How do I apply?. Not committed/pushed — the sync script handles listing, sitemap and publishing. Similar-job cards were hand-picked after the build (rebuilding from the spec re-picks them by category).

## 12 Image SEO & checklist
Image /assets/jobs-malta-hr-admin.png (ImageObject caption "Back Office Administrator job opportunity in Gżira, Malta — Outreach Recruitment").
✅ title ≤60 · description 120–155 · salary from the careers page everywhere (Competitive salary) · reference and deadline private · FAQ schema = visible FAQ · apply link uses this job's careers-page ID only · no template leftovers · passed tools/verify_job_page.py (static + headless Chrome render).
