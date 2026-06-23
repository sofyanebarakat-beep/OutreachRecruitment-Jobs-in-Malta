# Job Sync Report — Outreach Recruitment

Generated: 2026-06-23

→ **0 to add** · **4 to close** · **0 alert(s)**

---

## Jobs to Add

0 job(s) on the careers platform not yet on the static website.

- None
---

## Jobs to Close

4 job(s) on the static website no longer found on the careers platform.
Keep pages live but disable all application functionality.

Close the following jobs using the expire-job skill.

Jobs to close (these positions are no longer accepting applications):
- Contact Centre Team Leader → slug: contact-centre-team-leader
- Outlet Manager → slug: outlet-manager
- Handyman → slug: handyman
- Application Developer (Drupal) → slug: application-developer-drupal

Steps (all mandatory — do not skip any):
1. Run: python3 tools/expire_job.py contact-centre-team-leader outlet-manager handyman application-developer-drupal
2. Verify tools/jobs_registry.json shows status: "expired" for all 4 slugs
3. On each job detail page (jobs/[slug]/index.html):
   a. Remove the entire #job-apply-panel section
   b. Remove all elements with [data-job-apply-trigger] (Apply Now buttons)
   c. Remove the .job-mobile-apply-cta sticky bar
   d. In the cms-article How To Apply section, replace the apply link and button with:
      "This position is no longer accepting applications. Browse our current open vacancies →"
      linking to /jobs/
   e. Confirm the JobPosting schema validThrough is set to a past date
4. In jobs/index.html: mark each closed job card with a "Position Closed" badge — do NOT remove the cards from the grid
5. Update sitemaps/sitemap-jobs.xml — set <lastmod> for each closed job URL to today

