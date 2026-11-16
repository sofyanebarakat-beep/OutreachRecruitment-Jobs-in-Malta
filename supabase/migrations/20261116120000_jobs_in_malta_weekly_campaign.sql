-- "Jobs in Malta" content category + weekly new-openings campaign.
-- Safe to run more than once (Supabase Dashboard → SQL Editor → Run).

-- 1. Category on campaigns, topics and articles (decides where a published article is filed:
--    "Jobs in Malta" → /news-updates/jobs-in-malta/ + the Jobs in Malta chip on /news-updates).
alter table public.seo_campaigns add column if not exists category text not null default 'Candidates';
alter table public.seo_topics    add column if not exists category text;
alter table public.seo_articles  add column if not exists category text;
alter table public.seo_campaigns drop constraint if exists seo_campaigns_category_check;
alter table public.seo_campaigns add constraint seo_campaigns_category_check
  check (category in ('Jobs in Malta','Candidates','Employers','Study in Malta'));

-- 2. Campaign type: a normal keyword campaign, or the weekly "new jobs in Malta" round-up that is
--    built from the Job Sync data (new openings of the past week, linked to their job pages).
alter table public.seo_campaigns add column if not exists campaign_type text not null default 'standard';
alter table public.seo_campaigns drop constraint if exists seo_campaigns_campaign_type_check;
alter table public.seo_campaigns add constraint seo_campaigns_campaign_type_check
  check (campaign_type in ('standard','weekly_new_jobs'));

-- 3. The open jobs an article links to (slug, title, city, salary, url), for the editor and audits.
alter table public.seo_articles add column if not exists related_jobs jsonb not null default '[]'::jsonb;

-- 4. The campaign itself: every Monday 09:00 Malta, one round-up of that week's new openings.
insert into public.seo_campaigns
  (name, category, campaign_type, target_location, language, objective, status, start_date,
   articles_per_month, publish_days, publish_time, auto_generate, target_words, author_name,
   service_id, publishing_schedule, notes)
select 'Jobs in Malta — New openings every Monday', 'Jobs in Malta', 'weekly_new_jobs', 'Malta', 'English',
       'Rank for "jobs in Malta" and "new jobs in Malta this week": every Monday publish a round-up of the jobs that opened '
       || 'in the past 7 days (detected from Job Sync), each linked to its job page on outreachrecruitment.net/jobs/.',
       'active', current_date, 5, array['Monday'], '09:00', true, 800, 'Outreach Recruitment',
       (select id from public.seo_services where slug = 'jobs-in-malta-european-candidates'),
       'Monday at 09:00 Malta time',
       'Weekly draft is created automatically from Job Sync. Add the featured image, check the text, then Publish now or Schedule.'
where not exists (select 1 from public.seo_campaigns where campaign_type = 'weekly_new_jobs');

-- 5. Keyword targets for the category (deduplicated on keyword + location).
insert into public.seo_topics (keyword, intent, target_location, priority, status, suggested_title, notes, category, campaign_id, service_id)
select k.keyword, k.intent, 'Malta', k.priority, 'approved', k.title,
       'Jobs in Malta weekly campaign keyword', 'Jobs in Malta',
       (select id from public.seo_campaigns where campaign_type = 'weekly_new_jobs' order by created_at limit 1),
       (select id from public.seo_services where slug = 'jobs-in-malta-european-candidates')
from (values
  ('jobs in malta',                    'transactional', 100, 'Jobs in Malta This Week'),
  ('new jobs in malta this week',      'transactional',  95, 'New Jobs in Malta This Week'),
  ('latest jobs in malta',             'transactional',  90, 'Latest Jobs in Malta'),
  ('job vacancies in malta',           'transactional',  88, 'Job Vacancies in Malta'),
  ('job openings in malta',            'transactional',  85, 'Job Openings in Malta'),
  ('jobs in malta for residents',      'local',          80, 'Jobs in Malta for Candidates Living in Malta'),
  ('full time jobs in malta',          'transactional',  75, 'Full-Time Jobs in Malta'),
  ('jobs in malta with salary',        'commercial',     72, 'Jobs in Malta With Salary Shown'),
  ('hiring now in malta',              'transactional',  70, 'Companies Hiring Now in Malta'),
  ('recruitment agency jobs malta',    'commercial',     65, 'Recruitment Agency Jobs in Malta')
) as k(keyword, intent, priority, title)
on conflict (keyword, target_location) do update
  set category = excluded.category,
      campaign_id = coalesce(public.seo_topics.campaign_id, excluded.campaign_id);
