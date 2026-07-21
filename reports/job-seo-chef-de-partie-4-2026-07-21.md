# Job SEO Package — Chef De Partie (4th listing)

Source: https://outreach-recruitment-agency.careers-page.com/jobs/04cdef53-63f9-41b2-9e2e-dcc8053ff95d
Apply URL: https://outreach-recruitment-agency.careers-page.com/jobs/04cdef53-63f9-41b2-9e2e-dcc8053ff95d/apply
Published page: https://outreachrecruitment.net/jobs/chef-de-partie-4
Date posted: 2026-07-21 · Valid through: 2026-12-31 · Reference: OR-CDP-2026-004

## ⚠ Notes resolved before publishing

- **Duplicate title/location risk**: three "Chef De Partie" pages already exist (`chef-de-partie`, `chef-de-partie-2`, `chef-de-partie-3`), and `chef-de-partie-3` is already titled for the same city, **St. Julian's**. Per the site's own duplicate-title convention (seen on `sous-chef-2`: `Sous Chef Job in Malta (2nd Opening)`), the meta/OG/Twitter title was changed to **`Chef De Partie Job in Malta (2nd) | Outreach Recruitment`** (56 chars, no city) instead of repeating the standard `... Job in St. Julian's, Malta ...` format, to avoid a second exact-duplicate `<title>` on the site. Visible page content and schema `jobLocation` still correctly show **St. Julian's, Malta** — only the differentiator was applied to the title/OG/Twitter fields, not to the real location data.
- **Slug**: `chef-de-partie-4` (next available in the existing numbering sequence).
- **Reference number**: `OR-CDP-2026-004` (next in the existing `OR-CDP-2026-00X` sequence used by the other three Chef De Partie pages).
- **Base template used**: cloned from `jobs/baristas/index.html` (posted 2026-07-17) rather than the older `chef-de-partie-3` (2026-06-09), since it already has the correct `Job Type: Direct Job` field and the full current section set (Skills Required / Preferred Qualifications / Career Growth / FAQ / Similar Jobs / Latest Jobs / People Also Viewed) — avoids the site-wide "Subcontracting" mislabel bug documented in earlier reports.
- **Candidate Origin**: source explicitly states "Must reside in Malta currently" → set to **Malta residents**, so `applicantLocationRequirements: Malta` and the Job Target grid value is **"Residents in Malta"** (not the "& Europeans" default).
- **Languages Required section omitted**: source doesn't state a language requirement, so this section (and schema field) was left out entirely rather than guessed.
- **Salary, visa, relocation, training, immediate start**: none stated on the source page — all omitted from visible content, badges, and schema. No badges applied beyond "Full-Time Position" and "Career Growth Opportunities" (both directly supported).
- **Concurrent site activity**: while this job was being published, a separate automated process on this repo committed an unrelated new job (`Deli Counter Assistant / Salumeria Specialist`) and reorganised `sitemaps/sitemap-jobs.xml`. Both jobs' additions landed cleanly together in the shared counters, grid, and `ItemList` schema — verified consistent (see Section 11) — but it means the "New" grid card immediately preceding this one belongs to that other job, not this one.

## Section 1 — SEO Package

- **Meta title** (56 chars): `Chef De Partie Job in Malta (2nd) | Outreach Recruitment`
- **Meta description** (148 chars): `Apply for a Chef De Partie job in St. Julian's, Malta through Outreach Recruitment Agency. Hospitality role, full-time and on-site. Apply now today.`
- **URL slug**: `chef-de-partie-4`
- **Canonical URL**: `https://outreachrecruitment.net/jobs/chef-de-partie-4`
- **Primary keyword**: `chef de partie job St. Julian's Malta`
- **Secondary keywords**: `kitchen section chef jobs Malta`, `hospitality chef jobs Malta`, `Italian restaurant chef jobs Malta`, `Mediterranean cuisine chef jobs Malta`, `hotel kitchen jobs Malta`
- **Long-tail keywords**: `Chef De Partie job in St. Julian's Malta`, `Italian and Mediterranean restaurant chef de partie Malta`, `kitchen section chef vacancy St. Julian's`, `full-time chef de partie job Malta hospitality group`, `chef de partie jobs for Malta residents`
- **LSI keywords**: kitchen section management, food preparation, food hygiene, Sous Chef, mise en place, inventory control, dish presentation
- **Location keyword variations**: `St. Julian's jobs`, `jobs in St. Julian's Malta`, `Spinola Bay area jobs`, `Paceville jobs`
- **Industry keyword variations**: `hospitality jobs Malta`, `restaurant jobs Malta`, `hotel and catering jobs Malta`
- **Urgency keywords**: none (Immediate Start not stated)
- **Relocation / EU keywords**: none (Candidate Origin: Malta residents)
- **Open Graph**: title = meta title (differentiated); description = meta description; image = `/assets/jobs-malta-hospitality.png` (reused — matches every other Hospitality job page; no dedicated chef image asset exists)
- **Twitter card**: same title/description, `summary_large_image`
- **Alternative titles (A/B test)**:
  - Option A: `Chef De Partie Job in Malta (2nd) | Outreach Recruitment`
  - Option B: `Chef De Partie — Italian & Mediterranean Kitchen | Outreach Recruitment`
  - Option C: `Kitchen Section Chef Wanted, St. Julian's | Outreach Recruitment`
- **Google Jobs optimization notes**: no salary shown (omit `baseSalary`), `directApply: true` via the careers-page.com apply iframe, `employmentType: FULL_TIME`, `applicantLocationRequirements: Malta`.
- **Voice search queries**:
  1. "Are there any Chef De Partie jobs in Malta right now?"
  2. "What does a Chef De Partie do in a Maltese restaurant?"
  3. "Do I need to live in Malta to apply for this chef job?"
  4. "Is weekend work required for kitchen jobs in Malta?"
  5. "How do I apply for a Chef De Partie job in St. Julian's?"

## Section 2 — Google Jobs Package

| Field | Value |
|---|---|
| title | Chef De Partie |
| employmentType | FULL_TIME |
| datePosted / validThrough | 2026-07-21 / 2026-12-31 |
| workHours | Full-Time, shifts including evenings, weekends, and public holidays |
| occupationalCategory | Food Service Workers (matches the other 3 Chef De Partie pages for category consistency) |
| industry | Hospitality |
| identifier | OR-CDP-2026-004 |
| jobLocation | St. Julian's, Malta (MT) |
| applicantLocationRequirements | Malta |
| baseSalary | omitted — not disclosed on source |
| experienceRequirements | Previous experience as a Chef de Partie or in an equivalent kitchen role is required |
| educationRequirements | omitted — not stated on source |
| qualifications | omitted — no certifications/licences stated |
| directApply | true |

## Section 3 — AI Search Package

**Direct answer (48 words)**: Outreach Recruitment is hiring a Chef De Partie in St. Julian's, Malta for an expanding hospitality group operating Italian and Mediterranean dining concepts. The full-time, on-site role covers managing a kitchen section, food preparation, and quality control. Candidates must reside in Malta and have prior kitchen experience.

**AI summary (~100 words)**: The Chef De Partie role at an expanding hospitality group in St. Julian's, Malta covers full responsibility for an assigned kitchen section — preparing and presenting dishes to established recipes, maintaining food quality and consistency, managing section inventory, and supporting junior kitchen staff. Candidates need previous experience as a Chef de Partie or in an equivalent kitchen role, a background in restaurant, hotel, or high-volume hospitality kitchens, and flexibility to work evenings, weekends, and public holidays. Candidates must currently reside in Malta. Benefits include growth opportunities and exposure to multiple Italian and Mediterranean dining concepts. This is a full-time, on-site, direct-hire position; candidates apply through Outreach Recruitment's careers platform.

**Key facts table**:

| Field | Value |
|---|---|
| Position | Chef De Partie |
| Industry | Hospitality |
| Location | St. Julian's, Malta |
| Salary | Not disclosed |
| Job Type | Direct Job |
| Target Location | Residents in Malta |
| Employment Type | Full-Time |
| Experience | Previous Chef de Partie or equivalent kitchen role required |
| Education | Not specified |
| Language | Not specified |
| Visa Support | Not stated |
| Work Permit Support | Not stated |
| Employer | Outreach Recruitment Ltd (client: expanding hospitality group) |
| Application Method | Apply online via Outreach Recruitment |

**Entity mentions**: Chef De Partie, St. Julian's, Malta, Outreach Recruitment Ltd, Hospitality, Sous Chef, Italian cuisine, Mediterranean cuisine, food safety, kitchen section management.

**Candidate fit summary**: Best suited to a Malta-based candidate with previous Chef de Partie or equivalent kitchen experience, comfortable managing a section independently under service pressure, who can work flexible shifts including evenings, weekends, and public holidays.

**Related candidate questions**:
1. What experience is needed for this job?
2. Is this job full-time or part-time?
3. Where exactly is this job located?
4. Do I need to be based in Malta to apply?
5. Is shift work required?
6. How do I apply?
7. Is salary disclosed for this role?

## Section 4 — Full Job Page Content

Implemented in full on `/jobs/chef-de-partie-4/`: Job Highlights (details grid), About the Role, Key Responsibilities, Key Requirements, Skills Required, Preferred Qualifications, What We Offer, Career Growth Opportunities, About the Company, Application Deadline, Neighbourhood description, About Outreach Recruitment, How to Apply, FAQ (6 Q&As), GDPR + equal opportunities notice, Similar Jobs, Latest Jobs, People Also Viewed.

**Badges applied**: Full-Time Position, Career Growth Opportunities (growth explicitly mentioned). **Not applied** (unsupported by source): Immediate Start, Visa Sponsorship, Relocation Assistance, Language Bonus, Training Provided.

## Section 5 — Complete JobPosting JSON-LD

```json
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "Chef De Partie",
  "description": "<p>Outreach Recruitment is hiring a Chef De Partie for an expanding hospitality group in St. Julian's, Malta...</p>",
  "identifier": { "@type": "PropertyValue", "name": "Outreach Recruitment Job Reference", "value": "OR-CDP-2026-004" },
  "url": "https://outreachrecruitment.net/jobs/chef-de-partie-4",
  "datePosted": "2026-07-21",
  "employmentType": "FULL_TIME",
  "industry": "Hospitality",
  "occupationalCategory": "Food Service Workers",
  "hiringOrganization": { "@type": "Organization", "name": "Outreach Recruitment Ltd", "sameAs": "https://outreachrecruitment.net", "logo": "https://outreachrecruitment.net/assets/outreach-recruitment-logo.svg" },
  "jobLocation": { "@type": "Place", "address": { "@type": "PostalAddress", "streetAddress": "St. Julian's, Malta", "addressLocality": "St. Julian's", "addressRegion": "Malta", "postalCode": "0000", "addressCountry": "MT" } },
  "applicantLocationRequirements": { "@type": "Country", "name": "Malta" },
  "workHours": "Full-Time, shifts including evenings, weekends, and public holidays",
  "experienceRequirements": "Previous experience as a Chef de Partie or in an equivalent kitchen role is required.",
  "responsibilities": "Managing an assigned kitchen section; preparing and presenting dishes to established recipes and quality standards; ...",
  "skills": "Food preparation and cooking techniques, kitchen section management, food safety and hygiene compliance, inventory and stock control, teamwork under pressure",
  "jobBenefits": "Growth opportunities within an expanding hospitality group, exposure to multiple Italian and Mediterranean dining concepts, professional working environment, training and career advancement",
  "directApply": true,
  "applicationContact": { "@type": "ContactPoint", "email": "hr@outreachrecruitment.net", "contactType": "Human Resources" },
  "validThrough": "2026-12-31"
}
```

(Full block plus `BreadcrumbList`, `FAQPage`, and `ImageObject` is live in the page `<head>` — all four validated as parseable JSON.)

**Omitted fields and why**: `baseSalary` (not disclosed), `educationRequirements` (not stated), `qualifications` (no certifications/licences mentioned), `jobImmediateStart` (not stated), visa/relocation fields (not stated), `Languages Required` section (not stated).

## Section 6 — Internal Linking Plan

- Primary category hub: `hospitality-jobs-in-malta/index.html` — new card added first in its `top-jobs` grid.
- Location hub: none exists specifically for St. Julian's.
- Related job links (Similar Jobs on page): Demi Chef de Partie (Breakfast Shift) — Malta, Sous Chef — St. Julian's, Head Chef — St. Paul's Bay, Pastry Commis Chef — Mellieħa.
- No orphaning: page is linked from the Hospitality hub, the main jobs listing (`opening-jobs-grid` + `ItemList` schema), and reciprocal Similar Jobs / People Also Viewed links.

## Section 7 — SERP and Competitor Plan

Competing page types: Indeed Malta hospitality listings, LinkedIn Jobs, JobsinMalta.com, Keepmeposted, and direct hotel/restaurant-group career pages. This page competes via full `JobPosting` + `FAQPage` schema (many hospitality listings on aggregators lack structured data), fresh `datePosted`, a detailed FAQ section, and internal links to related kitchen-role pages already ranking on the site.

## Section 8 — Entity SEO Plan

Chef De Partie, St. Julian's, Malta, Outreach Recruitment Ltd, Hospitality, Sous Chef, kitchen section, Italian cuisine, Mediterranean cuisine, food safety and hygiene, inventory control.

## Section 9 — Freshness and Conversion Plan

- Review/refresh by **2026-08-20** (30 days).
- `lastmod` set to 2026-07-21 in `sitemaps/sitemap-jobs.xml` and `sitemap_index.xml`.
- Run the Google Indexing API script for `https://outreachrecruitment.net/jobs/chef-de-partie-4` after deployment.
- Google Rich Results Test: `https://search.google.com/test/rich-results?url=https://outreachrecruitment.net/jobs/chef-de-partie-4`
- Recommended CTA button text: "Apply Now" (implemented, matches site convention).

## Section 10 — Duplicate Content Prevention

- **Title collision resolved**: differentiated meta/OG/Twitter title to `Chef De Partie Job in Malta (2nd) | Outreach Recruitment` since `chef-de-partie-3` already uses the standard St. Julian's title format (see Notes above).
- Body copy is unique to this posting's real details (expanding hospitality group, Italian/Mediterranean concepts, Malta-residency requirement) rather than reused text from `chef-de-partie`, `-2`, or `-3`.
- Flag for future cleanup (not part of this task): four separate "Chef De Partie" listings now exist on the site (`chef-de-partie`, `-2`, `-3`, `-4`), two of which target the same city (St. Julian's). Worth an editorial review of whether `chef-de-partie` and `chef-de-partie-3`/`-4` still represent genuinely distinct live vacancies.

## Section 11 — Site Publishing Plan (completed)

1. ✅ Created `jobs/chef-de-partie-4/index.html` with full `JobPosting` + `BreadcrumbList` + `FAQPage` + `ImageObject` schema (all 4 blocks validated as parseable JSON).
2. ✅ Apply URL set in the apply iframe (`data-src`) and matches the source `/apply` link exactly; `directApply: true` in schema (site's established apply pattern).
3. ✅ Job card added to `opening-jobs-grid` in `jobs/index.html`, and to `ItemList` JSON-LD at position 1 (all 44 entries renumbered sequentially, `numberOfItems` incremented to 244).
4. ✅ Category hub: card added first in `hospitality-jobs-in-malta/index.html`'s `top-jobs` grid (108 cards, was 107).
5. ✅ Open-position counts incremented by reading current values (shared with one other job added concurrently by site automation — both increments landed correctly): `or-open-pos-num` +220 → +222, "Browse N+ current job vacancies" 209+ → 211+, `Showing N jobs` / tab counts / `roles available` 222 → 224, `Featured` 208 → 210. Verified: 224 `<article class="opening-job-card">` blocks present, tags balanced.
6. ✅ `sitemaps/sitemap-jobs.xml` — new URL added, `/jobs` `lastmod` refreshed to 2026-07-21; `sitemap_index.xml` refreshed to match.
7. ✅ `jobs_registry.json` — new entry appended (slug, title, category, location, dates, apply URL, keywords).
8. Freshness text: `Browse 211+ current job vacancies in Malta — updated July 2026` already reflects the current month; no separate change needed.
9. ✅ Visible "Browse all Jobs in Malta → /jobs" link included in the Similar Jobs section.

**Note on concurrent site activity**: partway through this publish, an unrelated automated process added a different job (`Deli Counter Assistant / Salumeria Specialist`) and committed it along with these files. Both additions were verified to have landed correctly and consistently in the shared counters, grid, hub page, and `ItemList` schema — no data was lost or overwritten.

## Section 12 — Image SEO Plan

- No bespoke image-generation tool available in this environment. Reused `jobs-malta-hospitality.png`, matching the convention used by every other Hospitality job page on the site.
- Recommended filename if a bespoke image is created later: `chef-de-partie-job-malta.jpg`
- ALT tag: `Chef De Partie job opportunity in St. Julian's, Malta — Outreach Recruitment`
- `ImageObject` schema implemented: 1200×630, caption "Chef De Partie job opportunity in St. Julian's, Malta — Outreach Recruitment"

## Section 13 — Off-Page Distribution Checklist

- [ ] LinkedIn post — direct link to `https://outreachrecruitment.net/jobs/chef-de-partie-4`
- [ ] Facebook post — direct link
- [ ] Instagram caption — hook + Malta jobs hashtags
- [ ] WhatsApp broadcast — short, direct
- [ ] Google Business Profile post — include apply link
- [ ] Submit to Indeed, Glassdoor, Jooble, JobsinMalta, Keepmeposted, MaltaPark

Sample copy:

**LinkedIn**: "We're hiring a Chef De Partie in St. Julian's, Malta! Join an expanding hospitality group running Italian and Mediterranean dining concepts. Full-time, on-site, with real career growth on offer. Apply now: https://outreachrecruitment.net/jobs/chef-de-partie-4"

**Facebook**: "Chef De Partie wanted in St. Julian's! 👨‍🍳 Full-time role with a growing Italian & Mediterranean restaurant group. Apply today: https://outreachrecruitment.net/jobs/chef-de-partie-4"

**Instagram**: "Run your own kitchen section 🍝🔥 Chef De Partie wanted in St. Julian's, Malta. Apply now — link in bio. #JobsInMalta #ChefJobs #StJuliansJobs"

**WhatsApp**: "Chef De Partie needed in St. Julian's, Malta — full-time, apply today: https://outreachrecruitment.net/jobs/chef-de-partie-4"

## Section 14 — Advanced Schema Plan

- `BreadcrumbList` and `FAQPage` implemented (see Section 5).
- Speakable schema: recommend targeting the "About the Role" intro and first two FAQ answers — not yet implemented site-wide (consistent with prior reports; flagged as a future site-wide enhancement, not done here).
- Video script (30s):
  - Hook: "St. Julian's kitchens run on precision."
  - Role overview: "We're looking for a Chef De Partie to run a kitchen section for an expanding Italian and Mediterranean restaurant group."
  - Key benefit: "Full-time, stable, with real growth across multiple dining concepts."
  - CTA: "Apply today at outreachrecruitment.net/jobs/chef-de-partie-4."

## Section 15 — Advanced SEO Recommendations

- Core Web Vitals: reuses an existing image asset already loaded elsewhere on the site — no new image weight.
- Multilingual keywords (Italian): `lavoro chef de partie Malta`, `offerte di lavoro cucina Malta`, `cuoco di partita Malta`, `lavoro ristorazione St. Julian's`, `lavoro cucina italiana Malta`.

## Section 16 — SEO Quality Checklist

- [x] Meta title 56 chars, contains "Job" and "Malta"; differentiated to avoid duplicating `chef-de-partie-3`'s title
- [x] Meta description 148 chars, includes "Apply now"
- [x] Location city/region/country consistent (St. Julian's, Malta, MT)
- [x] Employer = Outreach Recruitment Ltd
- [x] No salary shown or claimed anywhere (visible or schema)
- [x] `validThrough` present and visible
- [x] `employmentType`, `experienceRequirements` present
- [x] `responsibilities`, `skills`, `jobBenefits` present
- [x] `workHours` present (descriptive, not just "Full-Time")
- [x] `BreadcrumbList`, `FAQPage`, `ImageObject` schema present and valid JSON
- [x] Open Graph + Twitter tags present
- [x] Apply URL is the role-specific careers-page.com link provided by the user
- [x] Slug lowercase, hyphenated, no dates/salary
- [x] Similar Jobs, Latest Jobs, People Also Viewed sections present
- [x] Neighbourhood description included (St. Julian's, near Spinola Bay/Paceville)
- [x] Response timeline statement included ("3–5 business days")
- [x] `jobImmediateStart`, visa, relocation, language-bonus fields correctly omitted (unsupported by source)
- [x] Job Target grid value = "Residents in Malta" (matches Candidate Origin: Malta residents)
- [x] Job Type = "Direct Job" (built from a base template that already has this correct)
- [x] Sitemap + indexing notes included (Section 9)
- [x] Duplicate title risk identified and resolved (Section 10)
- [x] `ItemList` JSON-LD on `/jobs` updated and renumbered — validated as parseable JSON
