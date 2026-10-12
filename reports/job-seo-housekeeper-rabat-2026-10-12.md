# Job SEO Package — Housekeeper (Rabat, Malta)

Generated: 2026-10-12 · Source: ATS job `a80eda89-20ac-432b-8ce9-48512b5ff8ef`

## 1. SEO Package

- **SEO Title:** Housekeeper Job in Rabat, Malta | Outreach Recruitment
- **Meta Description:** Apply for a Housekeeper job in Rabat, Malta through Outreach Recruitment Agency. Hospitality role. Apply now.
- **URL Slug:** `housekeeper-rabat` (differentiator added — "Housekeeper" is already used by 4 other live job pages; slug carries the location per the site's existing convention, e.g. `maintenance-manager-mellieha`)
- **Canonical URL:** https://outreachrecruitment.net/jobs/housekeeper-rabat
- **Candidate Search Intent:** Role search (housekeeper/cleaner), location search (Rabat Malta jobs), salary search (€1,400/month visible)
- **Primary Category:** Hospitality · **Secondary:** Cleaning, Guest House/Boutique Hotel
- **Primary Keyword:** housekeeper job Rabat Malta
- **Secondary Keywords:** housekeeping jobs Malta, Rabat Malta jobs, boutique guest house housekeeper, cleaning jobs Malta, Malta residents housekeeping job
- **Long Tail:** full-time housekeeper job Rabat Malta, €1400 housekeeper job Malta, housekeeper job Malta residents only
- **Candidate Origin Keywords:** jobs for Malta residents, local hiring Malta (per Candidate Origin = Malta residents — no EU/relocation keywords used)
- **OG Image:** /assets/jobs-malta-hospitality.png (existing project-owned hospitality asset — reused)
- **Google Jobs Notes:** salary is genuinely visible on the ATS source (€1,400/month) so `baseSalary`/`salaryCurrency` are correctly included and match the visible chip exactly.

## 2. Google Jobs Package

| Field | Value |
|---|---|
| Employment Type | FULL_TIME |
| Industry | Hospitality |
| Location | Rabat, Malta |
| Remote Status | On-Site |
| Salary | €1,400 / month (visible, matches `baseSalary` in schema) |
| Job Type | Direct Job |
| Target Location | **Residents in Malta** (Candidate Origin = Malta residents — source explicitly states "Current Malta residency required") |
| Date Posted | 2026-10-12 |
| Valid Through | 2029-12-30 (PRIVATE — schema + registry only, never shown visibly) |
| Reference | OR-HSKP-2026-001 (PRIVATE — HTML comment only) |
| Application Method | Apply online via embedded ATS iframe |
| Direct Apply | true |
| Experience | Prior housekeeping/cleaning experience preferred, not strictly required |
| Education | No requirements |
| Skills | Room cleaning, bed prep, linen management, laundry handling, stocking amenities, hygiene protocols |

## 3. AI Search Package

**Direct Answer (54 words):** Outreach Recruitment is hiring a full-time, on-site Housekeeper for a boutique 9-bedroom guest house in Rabat, Malta, paying €1,400 per month. Duties cover daily cleaning of guest rooms, linen and laundry management, and restocking amenities. Current Malta residency is required to apply. Prior housekeeping experience is preferred. Apply directly through Outreach Recruitment.

**Entity mentions:** Housekeeper, Rabat, Malta, Outreach Recruitment Ltd, Hospitality, Full-Time, On-Site, €1,400/month, Malta residency requirement.

## 4. Job Content

Built on the client-accountant/kitchen-helper rich template. Sections live: Job Highlights, About the Role, Key Responsibilities, Requirements (includes the Malta-residency requirement, stated plainly since it's explicitly in the source), What's on Offer, About Outreach Recruitment, How To Apply, FAQ (generic, closed by default), Similar Jobs. ~290 words body copy.

## 5. JobPosting JSON-LD Plan

Included: title ("Housekeeper" — kept clean, no location per schema title rules), description, identifier, url, datePosted, employmentType, industry, occupationalCategory ("Maids and Housekeeping Cleaners"), hiringOrganization, jobLocation (Rabat), applicantLocationRequirements (Malta), workHours, educationRequirements, experienceRequirements, skills, responsibilities, **baseSalary** (`MonetaryAmount`, EUR, 1400/1400, unitText MONTH) + **salaryCurrency**, directApply, validThrough (private). Omitted: `jobBenefits` (source listed no benefits section — not invented), `qualifications` (no certifications stated), `incentiveCompensation` (none).

## 6. Internal Linking Plan

- Main jobs index: `/jobs/` ✅ (card added, first/newest)
- Category hub: `hospitality-jobs-in-malta.html` — not yet linked from the hub page (out of this task's explicit scope; flagging for follow-up)
- Similar Jobs links: `/jobs/housekeeping-attendant/` (St. Julian's), `/jobs/public-area-cleaner/` (Sliema) — both genuinely open roles
- No Rabat location hub page exists on this site — nothing to link

## 7. SERP & Competitor Plan

Competes against generic Indeed/JobsinMalta housekeeping listings. Differentiation: real salary disclosed (most competing listings don't), clear residency requirement stated upfront (filters unqualified applicants), fresh posting, structured data.

## 8. Entity SEO Plan

Housekeeper, synonyms (room attendant, cleaner), Hospitality industry, Rabat/Malta, Full-Time/On-Site, cleaning/linen/laundry skills, Outreach Recruitment Ltd, €1,400/month, Malta residency requirement, apply-online method.

## 9. Freshness & Conversion Plan

Posted 2026-10-12. Expiry kept private (2029-12-30 placeholder — role stays listed until the daily ATS sync closes it). Refresh recommended every 14–30 days. Salary disclosed up front removes a common friction point for this role type.

## 10. Duplicate Content Prevention

**Duplicate title risk flagged:** the clean schema/H1 title "Housekeeper" is shared with 4 other job pages (`housekeeper`, `housekeeper-2`, `housekeeper-3`, `housekeeper-4` — several closed/expired). This matches the site's existing convention (e.g. "Maintenance Manager" / `maintenance-manager-mellieha`) of keeping the schema title clean and carrying the differentiator in the slug and in the visible location/meta content instead. Content itself (boutique 9-bedroom guest house, Rabat, Malta-residency requirement, €1,400/month) is unique to this role and not copied from any other housekeeping listing.

## 11. Site Publishing Plan — COMPLETED

- Registry entry added to `tools/jobs_registry.json` (no `status` key = open, `valid_through: 2029-12-30`)
- `python3 tools/update_jobs_listing.py` run successfully — open count now **116** (was 114), card inserted first/newest in `opening-jobs-grid`, `jobs/index.html` and homepage counts all updated consistently
- `jobs/housekeeper-rabat/index.html` and `jobs/housekeeper-rabat.html` written with identical content
- Sitemap: `sitemaps/sitemap-jobs.xml` and `sitemap_index.xml`/`sitemap.xml` lastmod refreshed automatically by the script

## 12. Image SEO Plan

Reused existing project asset `/assets/jobs-malta-hospitality.png` — no bespoke image generated.

## Leak / Privacy Check (performed)

- No leftover "Kitchen Helper" / "kitchen-helper" / old UUID / old city ("St. Paul's Bay") / old salary ("Negotiable") text anywhere in the final HTML
- Reference number `OR-HSKP-2026-001` only in an HTML comment (not rendered)
- `validThrough: 2029-12-30` only inside the JSON-LD `<script>` block
- Salary (€1,400/month) is genuinely sourced from the ATS listing, shown consistently in the header chip and schema, not fabricated, not repeated in body copy sections
- Candidate-origin claim ("Malta residency required") is explicitly supported by the ATS source text — not invented, and no unsupported EU/visa/relocation language was added
- `apply_url` verified against the ATS UUID: `a80eda89-20ac-432b-8ce9-48512b5ff8ef`
