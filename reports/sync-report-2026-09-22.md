# Daily Job Sync Report — 2026-09-22 Monday

Generated: 2026-09-22T08:00:00

> ⚠️ **PLATFORM INACCESSIBLE TODAY** — The careers platform (outreach-recruitment-agency.careers-page.com) returned 403 Forbidden via the network proxy. Careers platform data is from the previous successful run (2026-09-21). Website data is current (read from local repository).

---

## Summary

| Metric | Value |
|---|---|
| Careers platform jobs | 157 _(last confirmed 2026-09-21)_ |
| Website (outreachrecruitment.net/jobs) | **191** |
| Gap: jobs to ADD | **2 unconfirmed** _(platform inaccessible — carried forward from yesterday)_ |
| Gap: jobs to CLOSE | **30** _(website only, not on careers — 1 day older than yesterday)_ |
| Jobs added to website since yesterday | ✅ 2 resolved: Head Chef in Gozo, Storekeeper |

---

## Changes Since Yesterday (2026-09-21)

### ✅ Resolved — Added to website
These jobs were in yesterday's "missing" list and have now been added to the website:

1. **Head Chef in Gozo** — Marsalforn, Gozo, Malta _(added 2026-09-21)_
2. **Storekeeper** — Żebbuġ, Malta _(added 2026-09-21)_

---

## Jobs to ADD to the website

> ⚠️ Cannot confirm or retrieve new jobs — careers platform inaccessible today (403 Forbidden). The following are carried forward from yesterday's missing list. Job descriptions cannot be fetched.

The following 2 jobs appeared on the careers platform yesterday but have no match on the website:

1. **Chefs de Partie** — Location unknown (careers platform inaccessible)
   - _Note: "Chef de Partie" already exists on website (Mellieħa, Valletta, St. Julian's). Verify whether this is a new distinct listing._
2. **Heavy equipment mech** — Location unknown (careers platform inaccessible)
   - _Note: "Heavy Equipment Mechanic" already exists on website (Żejtun + Santa Venera). This may be a 3rd listing or a title variation. Verify on the careers platform._

Additionally, 2 title-mismatch items require review:
- **Careers:** "Senior HR Coordinador - Spanish Speaking" ↔ **Website:** "Senior HR Coordinator - Spanish Speaking" _(sim=0.97 — likely same job with typo on careers; no action needed)_
- **Careers:** "Application Developer (Drupal) - Hybrid" ↔ **Website:** "Application Developer (Drupal)" _(sim=0.86 — may be a distinct hybrid role; add if different)_

---

## Prompts: Add jobs to website

> ⚠️ Job descriptions cannot be fetched while the careers platform is inaccessible. Prompts below are stubs — run manually once the platform is reachable, or add the descriptions from the careers platform manually.

---
### Prompt: Add Chefs de Partie

Add a new job using the job-seo-generator skill.

Job title: Chefs de Partie
Category: Hospitality
Location city: [FETCH FROM CAREERS PLATFORM — inaccessible today]
Salary range: Not disclosed
Expiry date: 2026-11-21
Apply URL: [FETCH UUID FROM https://outreach-recruitment-agency.careers-page.com — inaccessible today]

Job description:
[FETCH FROM https://outreach-recruitment-agency.careers-page.com — inaccessible today]

Defaults (apply silently):
- Employment type: Full-time
- Reference number: OR-CDP-2026-NNN
- Application method: Apply online
- Remote status: On-site
- Language: English
- Salary: always in baseSalary JSON-LD only, never visible on page — show "Competitive" instead

---
### Prompt: Verify — Heavy equipment mech

Before adding: confirm this is a **new 3rd listing** distinct from existing "Heavy Equipment Mechanic" pages already on the website:
- /jobs/heavy-equipment-mechanic/ (Żejtun, Malta — 2026-08-27)
- /jobs/heavy-equipment-mechanic-2/ (Santa Venera, Malta — 2026-08-11)

If it IS a new listing:

Add a new job using the job-seo-generator skill.

Job title: [FULL TITLE FROM CAREERS PLATFORM]
Category: Engineering
Location city: [FETCH FROM CAREERS PLATFORM]
Salary range: Not disclosed
Expiry date: 2026-11-21
Apply URL: [FETCH UUID FROM https://outreach-recruitment-agency.careers-page.com]

Job description:
[FETCH FROM CAREERS PLATFORM]

---

## Jobs to CLOSE on the website

The following 30 jobs are on the website but **not** on the careers platform. Day count shows how many consecutive days they have been "extra." Longest-running are highest priority.

> ⚠️ Review items marked with ⚠️ before closing — they may have fuzzy matches on the careers platform.

| # | Job Title | Location | Days Extra | Notes |
|---|-----------|----------|-----------|-------|
| 1 | Senior HR Coordinator - Spanish Speaking | Luqa, Malta | **12d** | ⚠️ Careers has "Senior HR Coordinador" (sim=0.97) — likely same job. Do NOT close. |
| 2 | Front Office Supervisor | St. Julian's, Malta | **12d** | |
| 3 | Front Desk Agent | St. Julian's, Malta | **12d** | |
| 4 | Hostess | St. Julian's, Malta | **12d** | |
| 5 | Deli Counter Assistant / Salumeria Specialist | Birkirkara, Malta | **12d** | |
| 6 | Baristas | St. Julian's, Malta | **12d** | |
| 7 | Assistant Executive Housekeeper | St. Julian's, Malta | **12d** | |
| 8 | Application Developer (Drupal) | Valletta, Malta | **12d** | ⚠️ Careers has "Application Developer (Drupal) - Hybrid" (sim=0.86). Review — may be distinct roles. |
| 9 | Kitchen Porter | Msida, Malta | **11d** | |
| 10 | Food & Beverage Staff | St. Julian's, Malta | **11d** | |
| 11 | Pool Attendants | St. Julian's, Malta | **11d** | |
| 12 | Associate Tax Advisor | Msida, Malta | **8d** | |
| 13 | Sales Executive B2B | Birkirkara, Malta | **7d** | |
| 14 | Front Office Assistant | Mellieħa, Malta | **5d** | |
| 15 | Showroom Sales Executive | Malta | **5d** | |
| 16 | Sales Engineer | Mosta, Malta | **5d** | |
| 17 | Builders and Shutterers | Qormi, Malta | **5d** | |
| 18 | Driver - Malta C License | Qormi, Malta | **5d** | |
| 19 | Barber | Paola, Malta | **5d** | |
| 20 | Lead Azure Infrastructure Architect | Malta | **5d** | |
| 21 | Bartender in Gozo | Malta | **5d** | |
| 22 | Restaurant Supervisor in Gozo | Malta | **5d** | |
| 23 | Real Estate Agents | Malta | **5d** | |
| 24 | Kitchen Helpers in Gozo | Malta | **5d** | |
| 25 | Lead Microsoft 365 Architect  Modern Work & Security | Malta | **5d** | |
| 26 | Real Estate Managers | Malta | **5d** | |
| 27 | Servers in Gozo | Malta | **5d** | |
| 28 | Waiters | Valletta, Malta | **4d** | |
| 29 | Barista | Mellieħa, Malta | **5d** | |
| 30 | Project Manager - Construction | Mosta, Malta | **4d** | |

---

### CLOSE Instructions

> CLOSE: Front Office Supervisor — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Front Desk Agent — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Hostess — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Deli Counter Assistant / Salumeria Specialist — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (retail-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Baristas — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Assistant Executive Housekeeper — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Application Developer (Drupal) — ⚠️ REVIEW FIRST: verify careers platform no longer has a non-hybrid Drupal developer listing before closing. If confirmed absent: Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (it-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Kitchen Porter — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Food & Beverage Staff — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Pool Attendants — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Associate Tax Advisor — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (finance-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Sales Executive B2B — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (sales-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Front Office Assistant — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Showroom Sales Executive — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (sales-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Sales Engineer — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (engineering-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Builders and Shutterers — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (construction-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Driver - Malta C License — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (construction-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Barber — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (retail-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Lead Azure Infrastructure Architect — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (it-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Bartender in Gozo — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Restaurant Supervisor in Gozo — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Real Estate Agents — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (sales-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Kitchen Helpers in Gozo — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Lead Microsoft 365 Architect  Modern Work & Security — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (it-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Real Estate Managers — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (sales-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Servers in Gozo — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Waiters — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Barista — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (hospitality-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

> CLOSE: Project Manager - Construction — Remove the job card from jobs/index.html opening-jobs-grid and from the matching category page (construction-jobs-in-malta.html) opening-jobs-centered-grid. Update the open-position count down by 1 in jobs/index.html.

---

## Action Required

1. **Unblock careers platform** — The sync cannot run fully while `outreach-recruitment-agency.careers-page.com` is blocked by the egress proxy (403 Forbidden). All new jobs posted to the careers platform since yesterday are invisible to this agent. Contact the session administrator to allowlist this domain.

2. **Review 2 unconfirmed ADD items** — Once the careers platform is accessible, verify "Chefs de Partie" and the "Heavy equipment mech" listing to determine if they are distinct new jobs needing website pages.

3. **Review 2 flagged CLOSE items** — "Senior HR Coordinator - Spanish Speaking" and "Application Developer (Drupal)" have fuzzy matches on the careers platform. Verify before closing.
