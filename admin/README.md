# SEO Admin — 120-Day SEO Course + KPI tracker

Private admin at `/admin/` (noindex, blocked in robots.txt, not linked from the site).

- **Dashboard**: course day and score, 28-day KPIs vs the previous 28 days, trend charts, decision signals
- **Daily KPI tracking**: import the Search Console "Dates" CSV, then add GA4 users, applications and employer leads
- **Live site data**: reads `tools/jobs_registry.json` and `reports/gsc_search_performance.csv` (real repo data)
- **Course**: all 16 weeks, with 7-day rhythm, tasks, worksheet, QCM + answer guide, auto weekly KPI review, deliverable and résumé
- **Trackers**: keywords, pages, content, technical, backlinks, local, AI visibility, experiments (the PDF's dashboard tabs 03–10)

## Storage
- Without config: **local mode** (this browser only; use Settings → Export backup).
- With Supabase:
  1. Run `supabase/admin_schema.sql` in the SQL editor
  2. Create your auth user, `insert into public.admin_users(email) values ('you@…');`, and disable sign-ups
  3. Fill `SUPABASE_URL` + `SUPABASE_ANON_KEY` in `admin/config.js` (anon key only, never service_role)
  4. Settings → "Copy local browser data to Supabase"
