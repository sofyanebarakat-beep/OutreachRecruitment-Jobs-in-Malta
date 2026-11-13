# Outreach Admin — Course & KPI

## SEO Control Centre (`/admin/seo/`)

The React + TypeScript SEO publishing suite lives at `/admin/seo/` and uses the same Supabase authentication and admin allow-list as this legacy admin. Apply `supabase/migrations/20261113140000_seo_content_platform.sql`, then build with `npm run build:seo`.

Server-side AI generation is provided by the `generate-seo-content` Edge Function. Configure `OPENAI_API_KEY`, optionally `OPENAI_MODEL`, deploy the function, and keep the service-role key only in Supabase's managed function environment. The browser never receives privileged credentials.

`OPENAI_API_KEY` is optional. Without it, manual and scheduled generation use the built-in free article generator. The article editor offers approximate 800, 1,200, 1,600 and 2,000-word targets. Adding a paid key later automatically upgrades scheduled Edge Function generation without changing the workflow.

Connected generation checks `GEMINI_API_KEY`, then `GROQ_API_KEY`, then `OPENAI_API_KEY`, and finally uses the built-in generator. Optional model overrides are `GEMINI_MODEL` (default `gemini-2.5-flash`) and `GROQ_MODEL` (default `openai/gpt-oss-20b`). Provider keys must exist only in Supabase Edge Function secrets.

Published articles use the same shared editorial template as `/moving-to-malta-for-work/`. The article editor's **Written by** selector uses the real team list; the selected author is carried into the visible author card, HTML author metadata and BlogPosting structured data. Apply `20261113200000_article_authors.sql` before using this field.

Campaign automation uses `20261113210000_campaign_autogeneration.sql`. An active campaign stores its related service, monthly article target, publishing weekdays, Malta publishing time, word-count target and author. Saving it creates deduplicated keyword topics and immediately asks the Edge Function for the first review-ready drafts; later scheduled runs continue up to the monthly limit. Drafts always remain in `generated` status until an administrator reviews them. The article editor detects every Markdown `##` section and provides a separate secure image upload, alt-text and caption control for each one; those images are inserted beneath the matching section heading when published.

After applying that migration, redeploy the updated function:

```bash
supabase link --project-ref atcitaqyraeqngcsaeun
supabase db push
supabase functions deploy generate-seo-content --project-ref atcitaqyraeqngcsaeun
```

Search Console and GA4 remain automatic: `tools/seo_course_automation.py` writes connected data to `seo_kpi_daily`, which the new Analytics page reads directly. Do not add Google credentials to browser JavaScript.

Service pages are derived from the website itself by `tools/build_seo_service_catalog.py`. The daily local automation refreshes `assets/seo-service-catalog.json`; **Services SEO → Sync from website** safely upserts that catalogue into Supabase. **Keywords & Topics → Find ideas from Google** converts the existing Search Console keyword feed into deduplicated content opportunities.

Approved topics are turned into drafts automatically every Monday, Wednesday and Friday by `.github/workflows/seo-content-control-centre.yml`. Add repository secrets `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`, deploy the Edge Function, and approve topics in the dashboard. Generated content is saved with `generated` status and is never published without human review and approval.

After reviewing the generated text, the administrator only needs to add the featured image and alt text, then choose **Publish now** or set the status to **Scheduled** with a publication date. `.github/workflows/publish-scheduled-seo-articles.yml` checks every 15 minutes, builds the static SEO page, updates routes and the sitemap, adds the card to `/news-updates`, and marks the Supabase article as published. Failed validation leaves the article unpublished with an error in its quality notes.

The Autopilot migration adds automatic topic selection, duplicate-keyword protection, image prompts, internal-link suggestions, platform-specific social/newsletter drafts, Google indexing preparation, and 7/30/60-day performance review records. Social copy always enters an approval queue; no external account is posted to without approval.

Apply `supabase/migrations/20261113190000_seo_autopilot.sql` after the base content-platform migration. Website Settings contains the Autopilot master switch and individual controls. The Social Approval Queue lets an administrator approve or reject generated copy without connecting or posting to external accounts.

Autopilot generates drafts daily. `review-published-seo-content.yml` runs weekly and completes due 7/30/60-day reviews using the Search Console page metrics already imported into Supabase, saving a concrete improvement recommendation for each article.

Private admin at `/admin/` (noindex, not linked from the site). Sidebar sections:

- **Marketing › Job Sync** (opens first) — the daily careers-page ⇄ website sync report: the headline
  ("✅ In sync — careers page N / website N (+x opened, -y closed, z updated)"), counts, live-site check,
  new / closed / reopened / updated jobs with what changed, items needing attention, notes, the Google
  indexing check, site housekeeping, and every earlier day (`#/jobsync/<date>`). Reads
  `reports/daily-sync/index.json` + `<date>.json`, which `tools/daily_job_sync.py` pushes every morning.
- **Marketing › Featured Jobs** — choose exactly six open jobs for gold highlighting in the `/jobs/`
  results grid. Save publishes the selection to Supabase; the public
  page reads it directly, so no listing rebuild or site deployment is needed. Apply the `jobs_featured`
  table/policies in `supabase/admin_schema.sql` before using this section. Browser-only mode cannot publish.
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
- **Marketing › Social Media** (`social.js`) — tabs that generate a picture **title**, **subtitle** and a
  ready **caption** (link + hashtags): Employers, Candidates, Study in Malta, Salary calculator (same 2026
  tax bands / SSC as `/salary-calculator-malta`), New jobs this week, Jobs by sector (live counts, hub
  links), Quotes, Myth vs Fact, Poll, Malta holidays & events. "Generate another" cycles ideas; everything is
  editable before copying.
- **Social Media extras** — *Today's post* card (weekly plan Mon quote · Tue new jobs · Wed candidate tip ·
  Thu employer post · Fri poll · Sat job of the day · Sun study; a holiday/international day on the date goes
  first) with "Coming up (next 7 days)"; *Job of the day* (fair daily rotation through all open jobs, intro from
  the careers page); *FAQ posts* from `admin/faq-posts.json` (built daily by `tools/build_social_faqs.py`:
  general questions + job-specific questions of open jobs); *hashtag sets* per tab (candidates, employers,
  students, jobs, each sector, none); *your own ideas* per tab (Supabase `seo_settings` key `social_ideas`
  when signed in, else this browser).
- **Malta holidays & events** (`calendar-malta.js`) — month by month: the 14 Malta public holidays (Good Friday
  from the Easter date), Easter Sunday, recurring events whose dates vary (Carnival — computed from Ash
  Wednesday —, Fireworks Festival, festa season, Notte Bianca, Birgufest, Middle Sea Race…, flagged "confirm
  the date"), relevant international days and a hiring / study moment per month. Each item has a ready post.
  **Generate picture** creates a square 1080×1080 social post in the fixed Outreach format. Selecting a job
  automatically fills its title, location, salary, employment type and the first 4–5 requirements from the
  careers-page description. The logo and layout stay fixed while each job remembers its own chosen background.
  The fixed Outreach logo and layout adapt to Instagram/Facebook square (1080×1080), Story (1080×1920)
  and LinkedIn landscape (1200×627). The finished PNG can be copied or downloaded.
  "Copy for email" = rich text with real bold; "Copy for social media" = Unicode bold. Also a Generic
  round-up post and editable templates (`{title}`, `{apply_url}` … saved in the browser). Today's new jobs
  (from the latest sync report) are shown first. Code: `marketing.js`.

- **Course** — the 30-day *Outreach Recruitment — SEO & KPI Course* (1 hour daily: theory, practice,
  QCM, KPI tracking): every day has its own plain-language goal, numbered practical checklist, saved
  step progress, illustrated walkthrough, good/bad examples, beginner help, copyable worksheet,
  browser-saved screenshot evidence, expected result and notes; plus the 30-day progress grid, the 4-week plan with
  its KPIs, Day 1 keyword progress, success KPIs, tools and the next step. Content: `course30-data.js`.
- **KPI** — the course's 90-day targets (organic clicks +20%, impressions +30%, 5 priority keywords in
  the Top 10, 30 lessons), 28-day check-ins, trend charts, priority keywords and the baseline.
- **Course Notes** — one structured, report-ready note for every course day. Includes rich formatting
  (headings, bold, italic, underline, lists and text colour), lesson search, note completion progress,
  reusable learning/practice/evidence/problem/next-action prompts, and full-report copy, HTML download,
  preview and print actions. Rich paste from ChatGPT preserves safe headings, emphasis, lists, tables,
  links, quotes and code; Markdown tables/lists are converted when only plain text is available. Notes
  and the complete report can be copied back out with their formatting intact. Notes are stored with the
  existing course settings in Supabase or locally.

Files: `index.html`, `jobsync.js`, `featuredjobs.js`, `marketing.js`, `images.js`, `social.js`, `calendar-malta.js`, `course30.js`, `course30.css`, `course30-data.js`, `config.js`.

## Data
Supabase project from `config.js` (`atcitaqyraeqngcsaeun`), locked by RLS to emails in `public.admin_users`
(schema: `supabase/admin_schema.sql`).
- `seo_settings` key `course30` — progress, day notes, baseline, priority keywords, KPI check-ins
- `seo_kpi_daily` (read) — daily Search Console totals from `tools/seo_course_automation.py`; the KPI page
  turns them into rolling 28-day totals automatically
- `seo_keywords` (read) — live positions, `source_key = "gsc:<keyword>"`
- `jobs_featured` — the ordered six-job public `/jobs/` highlights; readable by visitors and writable only by signed-in admins

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
