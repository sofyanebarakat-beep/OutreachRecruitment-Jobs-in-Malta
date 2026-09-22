# Daily Job Sync Report — 2026-09-22 Monday

Generated: 2026-09-22T08:00:00 (updated after background agent delivered careers data)

> ⚠️ **PLATFORM INACCESSIBLE** — The careers platform (outreach-recruitment-agency.careers-page.com) returned 403 Forbidden via the network proxy. The 157-job careers list was reconstructed from the local repository (jobs/ directory HTML files + 2026-09-21 sync baseline). Website data is current (read from local repository).

---

## Summary

| Metric | Value |
|---|---|
| Careers platform jobs | **157** _(reconstructed from local repo — platform inaccessible today)_ |
| Website (outreachrecruitment.net/jobs) | **191** |
| Gap: jobs to ADD | ✅ **0 — all jobs in sync** |
| Gap: jobs to CLOSE | **30** _(on website, not on careers platform)_ |
| Jobs added to website since yesterday | ✅ 2 resolved: Head Chef in Gozo, Storekeeper |
| ⚠️ Location flag | Storekeeper on careers = Birkirkara; new website page = Żebbuġ — verify locations match |

---

## Changes Since Yesterday (2026-09-21)

### ✅ Resolved — Added to website
These jobs were in yesterday's "missing" list and have now been added to the website:

1. **Head Chef in Gozo** — Marsalforn, Gozo, Malta _(added 2026-09-21)_
2. **Storekeeper** — Żebbuġ, Malta _(added 2026-09-21)_

---

## Jobs to ADD to the website

✅ **All jobs are in sync — no action needed today.**

The full 157-job careers platform list (reconstructed from local repository) was cross-matched against the 191 website jobs using fuzzy title matching (threshold 0.82). Every careers platform job has a corresponding website page.

_Note: "Chefs de Partie" and "Heavy equipment mech" from yesterday's missing list resolve as follows:_
- **Chefs de Partie** — maps to existing "Chef De Partie" / "Chef de Partie" pages (St. Julian's, Mellieħa, Floriana) ✓
- **Heavy equipment mech** — maps to existing "Heavy Equipment Mechanic" pages (Żejtun + Santa Venera) ✓

_⚠️ Location mismatch to verify: The website's new Storekeeper page uses location **Żebbuġ** and UUID `0094a7ce`, but the careers platform lists Storekeeper in **Birkirkara** (UUID `d36ec63f`, page at /jobs/storekeeper/). Confirm whether these are two different positions or whether the Żebbuġ page has the wrong location._

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

1. **Unblock careers platform** — `outreach-recruitment-agency.careers-page.com` is blocked by the egress proxy (403 Forbidden). This prevents the agent from detecting new jobs posted to the platform today. Contact the session administrator to allowlist this domain.

2. **Process 28 confirmed CLOSE items** — 28 jobs are clearly on the website but not on the careers platform (all with 4+ consecutive days extra). Remove their cards and decrement the count.

3. **Verify before closing — 2 flagged items:**
   - "Senior HR Coordinator - Spanish Speaking" — the careers platform has "Senior HR Coordinador" (typo, sim=0.97). Same job — do NOT close.
   - "Application Developer (Drupal)" — careers has "Application Developer (Drupal) - Hybrid" (sim=0.87). Likely a fuzzy match for the hybrid version — review before closing.

4. **Verify Storekeeper location** — Website has Storekeeper (Żebbuġ, UUID 0094a7ce) but careers platform shows Storekeeper (Birkirkara, UUID d36ec63f). Confirm if these are two separate listings or a location error.
