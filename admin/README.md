# SEO Admin — Learn, Analytics and SEO Workspace

Private admin at `/admin/` (noindex, blocked in robots.txt, not linked from the site).

- **Today**: the five most useful learning, measurement and action priorities in one place
- **Learn**: current week, all 16 weeks, practice mode, QCM/decisions, evidence, progress and weekly reviews
- **Analytics**: separate Search Console and GA4 views, keywords, pages, sectors, locations and confidence labels
- **SEO Workspace**: ranked priorities, opportunities, experiments, audits, content, links and alerts
- **Integrations & sync**: connection health, latest automation run, warnings and data-freshness guidance
- **Learning dashboard**: course day and score, 28-day KPIs vs the previous 28 days, trend charts and decision signals
- **Daily KPI tracking**: import the Search Console "Dates" CSV, then add GA4 users, applications and employer leads
- **Live site data**: reads `tools/jobs_registry.json` and `reports/gsc_search_performance.csv` (real repo data)
- **Course**: all 16 weeks, with 7-day rhythm, tasks, worksheet, QCM + answer guide, auto weekly KPI review, deliverable and résumé
- **Trackers**: keywords, pages, content, technical, backlinks, local, AI visibility, experiments (the PDF's dashboard tabs 03–10)
- **Practice mode**: choose a real data opportunity, record the observation, hypothesis, decision, implementation and review
- **Opportunity inbox**: automatic keyword, CTR, technical and sector exercises ranked by impact and effort
- **Evidence locker**: attach proof of work to a week and task
- **Decision simulator**: one evidence-based decision scenario for every course week
- **Separate scores**: learning progress, practical evidence and business KPI direction
- **Weekly review**: an editable automatic draft connecting KPI changes to lessons and the next measurable action

## Storage
- Without config: **local mode** (this browser only; use Settings → Export backup).
- With Supabase:
  1. Run `supabase/admin_schema.sql` in the SQL editor
  2. Create your auth user, `insert into public.admin_users(email) values ('you@…');`, and disable sign-ups
  3. Fill `SUPABASE_URL` + `SUPABASE_ANON_KEY` in `admin/config.js` (publishable/anon key only, never a secret or service-role key)
  4. Settings → "Copy local browser data to Supabase"

## Daily automation

`tools/seo_course_automation.py` runs after the existing job-sync agent each morning. It:

- imports final Search Console daily totals, queries and pages;
- imports GA4 organic users, `apply_click`, `employer_lead_submit` and AI-referral sessions when GA4 API access is configured;
- audits titles, descriptions, H1s, canonicals, image alt text, JobPosting schema and orphan pages;
- builds the Week 5 sector opportunity table;
- records page-changing git commits as 7/30/60/90-day experiments;
- creates keyword-drop and lost-impression alerts.

Copy `tools/seo_automation.env.example` to the gitignored
`tools/private/seo_automation.env`, add a newly rotated service-role key and the GA4 numeric
property ID, then run `chmod 600 tools/private/seo_automation.env`. Never put that key in
`admin/config.js` or any public HTML/JavaScript file.

Run once manually with:

```bash
python3 tools/seo_course_automation.py
```

The script always writes `reports/seo-automation-latest.json`; it writes Supabase only when
the private server-side configuration is present.
