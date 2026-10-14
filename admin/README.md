# Outreach Admin — Course & KPI

Private admin at `/admin/` (noindex, not linked from the site). Sidebar sections:

- **Marketing › Job Sync** (opens first) — the daily careers-page ⇄ website sync report: the headline
  ("✅ In sync — careers page N / website N (+x opened, -y closed, z updated)"), counts, live-site check,
  new / closed / reopened / updated jobs with what changed, items needing attention, notes, the Google
  indexing check, site housekeeping, and every earlier day (`#/jobsync/<date>`). Reads
  `reports/daily-sync/index.json` + `<date>.json`, which `tools/daily_job_sync.py` pushes every morning.
- **Marketing › Email Marketing** — ready-to-paste job posts built from the careers-page description
  (fact sheet `tools/ats_snapshots/<uuid>.json`). Default job post = a short introduction only: title,
  city · type · salary, "Outreach Recruitment is recruiting on behalf of our client, …" (client and
  adjectives taken from the careers page), the role in one sentence ("You'll …"), "✨ What's in it for
  you", a call to action, "🌐 Apply now:" the job's page on the website, "💼 More Jobs:", hashtags.
  Bullet lists are still available as template placeholders.
  **Picture library** (`images.js`): upload pictures to a post; they are saved for next time and the
  picture chosen for each job is remembered. Signed in + bucket set up → saved online in Supabase Storage
  (bucket `marketing`, run `supabase/marketing_storage.sql` once) and embedded in "Copy for email";
  otherwise saved in the browser (IndexedDB) with Copy picture / Download. Large pictures are resized to 1600px.
  "Copy for email" = rich text with real bold; "Copy for social media" = Unicode bold. Also a Generic
  round-up post and editable templates (`{title}`, `{apply_url}` … saved in the browser). Today's new jobs
  (from the latest sync report) are shown first. Code: `marketing.js`.

- **Course** — the 30-day *Outreach Recruitment — SEO & KPI Course* (1 hour daily: theory, practice,
  QCM, KPI tracking): today's lesson, a 30-day progress grid with notes per day, the 4-week plan with
  its KPIs, Day 1 keyword progress, success KPIs, tools and the next step. Content: `course30-data.js`.
- **KPI** — the course's 90-day targets (organic clicks +20%, impressions +30%, 5 priority keywords in
  the Top 10, 30 lessons), 28-day check-ins, trend charts, priority keywords and the baseline.

Files: `index.html`, `jobsync.js`, `marketing.js`, `images.js`, `course30.js`, `course30.css`, `course30-data.js`, `config.js`.

## Data
Supabase project from `config.js` (`atcitaqyraeqngcsaeun`), locked by RLS to emails in `public.admin_users`
(schema: `supabase/admin_schema.sql`).
- `seo_settings` key `course30` — progress, day notes, baseline, priority keywords, KPI check-ins
- `seo_kpi_daily` (read) — daily Search Console totals from `tools/seo_course_automation.py`; the KPI page
  turns them into rolling 28-day totals automatically
- `seo_keywords` (read) — live positions, `source_key = "gsc:<keyword>"`

If the database cannot be reached (e.g. the free project is paused), the admin offers browser-only mode;
**KPI → History → Copy browser data to the database** moves that data across later.
Password reset emails return to `/admin/` — add `https://outreachrecruitment.net/admin/` to
Supabase → Authentication → URL configuration → Redirect URLs.

Local preview without a database: `python3 -m http.server` then open `http://localhost:8000/admin/?local`.

---

## Previous SEO admin (not loaded)
`admin.js`, `admin.css`, `course-*.js` are the earlier 16-week SEO admin; kept for reference.


Private admin at `/admin/` (noindex, blocked in robots.txt, not linked from the site).

- **Today**: the five most useful learning, measurement and action priorities in one place
- **Learn**: current week, all 16 weeks, practice mode, QCM/decisions, evidence, progress and weekly reviews
- **Analytics**: separate Search Console and GA4 views, keywords, pages, sectors, locations and confidence labels
- **SEO Workspace**: ranked priorities, opportunities, experiments, audits, content, links and alerts
- **Integrations & sync**: connection health, latest automation run, warnings and data-freshness guidance
- **Learning dashboard**: course day and score, 28-day KPIs vs the previous 28 days, trend charts and decision signals
- **Daily KPI tracking**: one-click automatic sync/refresh from connected Search Console, GA4 and Supabase data, with manual entry kept as a fallback
- **Live site data**: reads `tools/jobs_registry.json` and `reports/gsc_search_performance.csv` (real repo data)
- **Course**: all 16 weeks, with 7-day rhythm, tasks, worksheet, QCM + answer guide, auto weekly KPI review, deliverable and résumé
- **Week-specific measurement help**: each course week identifies the business question, relevant KPIs, exact data sources, interpretation guidance and a one-click suggested review action
- **Decision-coach workflow**: Learn → Do → Measure → Decide → Evidence stage filters, focused KPI scorecards, data-confidence labels, combined-signal explanations, structured actions, appropriate 7–90 day review timing, one-click experiments, examples/warnings and evidence-based completion gates
- **Notion and Sheets exports**: copy tasks, daily plans, note questions, evidence, KPI actions, reviews, unfinished work, action plans, portfolio entries or all 16 weeks as a single column; copy a complete Notion-ready Markdown page or download a weekly Markdown + CSV pack
- **Notion database pack**: import-ready Tasks, KPI, Experiments and Evidence databases with stable IDs, relationship instructions, formulas and recommended views in `admin/notion-templates/`
- **Simple course mode**: each week opens with only one short lesson, the next unfinished practical task, one notes/evidence box and one completion button; advanced material remains available under Full details
- **Simple admin navigation**: the default menu contains only Today, My next task, Course weeks, Record results and My notes; specialist dashboards and trackers stay behind one Advanced tools switch
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

The Daily KPI page has a **Sync automatically** button. By default it refreshes the latest
automation status and KPI rows from Supabase. If a protected server sync service is available,
set its URL as `SYNC_ENDPOINT` in `admin/config.js`; the button will request a new automation
run first and then refresh the table. The endpoint must keep Google and Supabase service
credentials on the server—never place private credentials in the browser configuration.
