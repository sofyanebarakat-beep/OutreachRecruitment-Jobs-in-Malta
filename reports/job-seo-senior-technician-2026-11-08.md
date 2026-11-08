# Job SEO Package — Senior Technician (Gżira, Malta)

Source: https://outreach-recruitment-agency.careers-page.com/jobs/a5cdd055-a18e-4aad-b319-7d66d6e85ed9
Posted on the careers page: 2026-11-06 · Built: 2026-11-08 · Page: https://outreachrecruitment.net/jobs/senior-technician
Spec (rebuild any time): `tools/job_specs/senior-technician.json` → `python3 tools/build_job_page.py tools/job_specs/senior-technician.json`
Inputs: Full-time · Direct Job · On-site · Candidate Origin: Open (not stated) · Immediate Start: Not stated · Salary **Competitive salary** (none on the careers page)

## 1 SEO
- Meta title (60): Senior Technician Job in Gżira, Malta | Outreach Recruitment
- Meta description (150): Senior Technician job in Gżira, Malta: diagnose and repair vehicles for an established automotive group. Training abroad, health insurance. Apply now.
- Slug: `senior-technician` · Canonical: https://outreachrecruitment.net/jobs/senior-technician
- Search intent: Experienced car technicians/mechanics fluent in Maltese and English seeking a senior workshop role with training abroad in Gżira.
- Primary keyword: senior technician job Malta · Secondary: automotive technician jobs Malta, car mechanic jobs Gżira, vehicle diagnostics jobs Malta, auto electrician jobs Malta, workshop jobs Gżira
- Long-tail: senior automotive technician job in Gżira Malta, car technician with training abroad Malta, wiring harness repair technician Malta
- OG/Twitter title = meta title; OG/Twitter description = meta description; image /assets/jobs-malta-others.png

## 2 Google Jobs
FULL_TIME · Direct Job · Gżira, Malta (MT) · On-site · no baseSalary (careers page gives none) · Target "Residents in Malta & Europeans" (no applicantLocationRequirements) · category Engineering & Maintenance · industry Automotive — Aftersales & Workshop · occupationalCategory 49-3023.00 Automotive Service Technicians and Mechanics · education: not stated · experience: Previous experience in an automotive workshop or a similar technical position would be considered an asset · languages: Maltese — fluent; English — fluent · work hours: Full-time, on-site · apply online at https://outreach-recruitment-agency.careers-page.com/jobs/a5cdd055-a18e-4aad-b319-7d66d6e85ed9/apply · validThrough 2029-12-30 (private) · reference OR-SNTC-2026-001 (private, HTML comment only) · no visa/work-permit claims.

## 3 AI search
Direct answer: Outreach Recruitment is recruiting on behalf of our client, a well-established automotive group in Malta, for an experienced and technically skilled Senior Automotive Technician to join its workshop team in Gżira. It is a full-time, on-site role in Gżira, Malta with a competitive salary; apply online through Outreach Recruitment.

## 4 Content on the page
Badges New / Direct Job / Full-Time; chips Engineering & Maintenance · Competitive salary · Full-Time · Gżira, Malta; About the Role (3), Key Responsibilities (16), Requirements (7), What's on Offer (5), Skills (6), Preferred Qualifications (1), Languages (2), About the Company, Location (Gżira), About Outreach Recruitment, How To Apply. All facts come from the careers-page fact sheet `tools/ats_snapshots/a5cdd055-a18e-4aad-b319-7d66d6e85ed9.json`; nothing invented.

## 5 JobPosting JSON-LD
title, description (HTML of the visible sections), datePosted 2026-11-06, dateModified 2026-11-08, validThrough 2029-12-30, employmentType FULL_TIME, hiringOrganization Outreach Recruitment Ltd, jobLocation Gżira, Malta MT, identifier = slug, industry + occupationalCategory, experienceRequirements, qualifications, responsibilities, skills, jobBenefits, workHours, directApply. No baseSalary (careers page gives none). Omitted (not in source): incentiveCompensation, jobImmediateStart, applicantLocationRequirements.

## 6 Internal linking
Breadcrumb Home › Jobs in Malta › Engineering Jobs in Malta › Senior Technician; How-to-apply links: Engineering Jobs in Malta, Malta salary calculator, All jobs in Malta; Similar jobs (open Engineering & Maintenance jobs from the registry): workshop-assistant-manager, pdi-leading-hand, facilities-maintenance-and-health-and-safety-manager, maintenance-person.

## 7 SERP / competitors
Keepmeposted, jobsplus.gov.mt, Indeed MT, Facebook groups for "automotive technician Malta"; mostly short listings. Edge: full duty list, training FAQ, direct apply.

## 8 Entity SEO
Outreach Recruitment Ltd · Gżira, Malta · automotive group · vehicle diagnostics · wiring harness · job cards · Garage Manager · O*NET 49-3023.00

## 9 Freshness & conversion
dateModified set on build; the daily sync keeps the page in step with the careers page and closes it when the ATS job closes. Inline application panel (lazy iframe of this job's apply URL, eligibility gate, success handling, optional Outreach-managed job alerts) and all Apply buttons point to this job's careers-page apply form only.

## 10 Duplicate-content prevention
Unique slug and copy rewritten from the source; several Gżira automotive roles were posted on 2026-11-06, so each intro, location sentence and FAQ set is written separately. Canonical to /jobs/senior-technician; flat jobs/senior-technician.html is byte-identical to jobs/senior-technician/index.html. Notes: Title kept as on the careers page (Senior Technician); copy says Senior Automotive Technician as the source body does. No education requirement stated, so educationRequirements omitted from schema.

## 11 Publishing
Files: jobs/senior-technician/index.html, jobs/senior-technician.html; registry entry in tools/jobs_registry.json (category Engineering & Maintenance, valid_through 2029-12-30, no salary, no status). FAQ (6, closed by default): What does a Senior Technician do in this role?; Is previous workshop experience required?; Which languages do I need?; Is training provided?; Is a salary stated for this role?; How do I apply?. Not committed/pushed — the sync script handles listing, sitemap and publishing.

## 12 Image SEO & checklist
Image /assets/jobs-malta-others.png (ImageObject caption "Senior Technician job opportunity in Gżira, Malta — Outreach Recruitment").
✅ title ≤60 · description 120–155 · salary from the careers page everywhere (Competitive salary) · reference and deadline private · FAQ schema = visible FAQ · apply link uses this job's careers-page ID only · no template leftovers · passed tools/verify_job_page.py (static + headless Chrome render).
