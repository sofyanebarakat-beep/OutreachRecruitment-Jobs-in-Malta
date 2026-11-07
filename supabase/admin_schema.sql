-- Outreach Recruitment — SEO Admin schema (120-Day SEO Course + KPI tracker)
-- Run once in Supabase → SQL Editor. Safe to re-run (idempotent).
--
-- Access model: only emails listed in public.admin_users can read/write.
-- After running this file:
--   1. Authentication → Users → "Add user" (email + password) for yourself.
--   2. insert into public.admin_users(email) values ('<your login email>');
--   3. Authentication → Providers → Email: turn OFF "Allow new users to sign up".

create extension if not exists pgcrypto;

-- ── Access control ──────────────────────────────────────────────
create table if not exists public.admin_users (
  email text primary key,
  created_at timestamptz not null default now()
);
alter table public.admin_users enable row level security;

create or replace function public.is_admin()
returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (
    select 1 from public.admin_users
    where lower(email) = lower(coalesce(auth.jwt() ->> 'email', ''))
  );
$$;

drop policy if exists admin_users_self_read on public.admin_users;
create policy admin_users_self_read on public.admin_users
  for select to authenticated using (public.is_admin());

-- ── updated_at trigger ──────────────────────────────────────────
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end; $$;

-- ── Tables ──────────────────────────────────────────────────────
-- 00 Settings (course start date, baseline, etc.)
create table if not exists public.seo_settings (
  key text primary key,
  value jsonb,
  updated_at timestamptz not null default now()
);

-- Public jobs-page spotlight, managed by authenticated admins.
create table if not exists public.jobs_featured (
  id text primary key check (id = 'current'),
  slugs text[] not null,
  updated_at timestamptz not null default now()
);
alter table public.jobs_featured drop constraint if exists jobs_featured_slugs_check;
alter table public.jobs_featured drop constraint if exists jobs_featured_three_slugs_check;
alter table public.jobs_featured drop constraint if exists jobs_featured_six_slugs_check;
alter table public.jobs_featured
  add constraint jobs_featured_six_slugs_check check (cardinality(slugs) between 3 and 6);
alter table public.jobs_featured enable row level security;
drop policy if exists jobs_featured_public_read on public.jobs_featured;
create policy jobs_featured_public_read on public.jobs_featured
  for select to anon, authenticated using (true);
drop policy if exists jobs_featured_admin_write on public.jobs_featured;
create policy jobs_featured_admin_write on public.jobs_featured
  for all to authenticated using (public.is_admin()) with check (public.is_admin());
grant select on public.jobs_featured to anon, authenticated;
grant insert, update, delete on public.jobs_featured to authenticated;

-- 02 Daily tracking
create table if not exists public.seo_kpi_daily (
  id uuid primary key default gen_random_uuid(),
  date date not null unique,
  clicks integer,
  impressions integer,
  ctr numeric,            -- percent, e.g. 3.95
  avg_position numeric,
  organic_users integer,
  applications integer,
  employer_leads integer,
  ai_referrals integer,
  source text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 03 Keywords
create table if not exists public.seo_keywords (
  id uuid primary key default gen_random_uuid(),
  keyword text not null,
  intent text,            -- candidate / employer / informational / navigational
  sector text,
  target_url text,
  baseline_position numeric,
  current_position numeric,
  target_position numeric,
  volume integer,
  notes text,
  source_key text,
  previous_position numeric,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 04 Pages
create table if not exists public.seo_pages (
  id uuid primary key default gen_random_uuid(),
  url text not null,
  target_query text,
  clicks integer,
  impressions integer,
  ctr numeric,
  position numeric,
  conversions integer,
  action text,
  notes text,
  source_key text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 05 Content
create table if not exists public.seo_content (
  id uuid primary key default gen_random_uuid(),
  idea text not null,
  cluster text,
  intent text,
  status text,            -- idea / brief / writing / published / refresh
  url text,
  publish_date date,
  results text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 06 Technical
create table if not exists public.seo_technical (
  id uuid primary key default gen_random_uuid(),
  issue text not null,
  severity text,          -- Critical / High / Medium / Low
  url text,
  owner text,
  status text,            -- open / in progress / fixed / validated
  fix_date date,
  validation text,
  source_key text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 07 Backlinks
create table if not exists public.seo_backlinks (
  id uuid primary key default gen_random_uuid(),
  prospect text not null,
  site_url text,
  relevance integer,      -- 1-5
  legitimacy integer,     -- 1-5
  contact text,
  status text,            -- prospect / contacted / replied / acquired / rejected
  target_url text,
  acquired_link text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 08 Local
create table if not exists public.seo_local (
  id uuid primary key default gen_random_uuid(),
  action text not null,
  type text,              -- profile / citation / review / location page
  platform text,
  status text,
  date date,
  url text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 09 AI visibility
create table if not exists public.seo_ai_visibility (
  id uuid primary key default gen_random_uuid(),
  date date not null,
  question text not null,
  engine text,            -- Google AI Overview / ChatGPT / Perplexity / Gemini / Copilot
  surfaced boolean default false,
  cited boolean default false,
  referral_sessions integer,
  competitors text,
  result text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 10 Experiments
create table if not exists public.seo_experiments (
  id uuid primary key default gen_random_uuid(),
  change text not null,
  hypothesis text,
  page text,
  start_date date,
  review_date date,
  before_data text,
  after_data text,
  conclusion text,
  source_key text,
  commit_sha text,
  status text,
  review_schedule jsonb not null default '[]'::jsonb,
  review_results jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Safe upgrades for projects created with an earlier version of this file.
alter table public.seo_kpi_daily add column if not exists ai_referrals integer;
alter table public.seo_kpi_daily add column if not exists source text;
alter table public.seo_keywords add column if not exists source_key text;
alter table public.seo_keywords add column if not exists previous_position numeric;
alter table public.seo_pages add column if not exists source_key text;
alter table public.seo_technical add column if not exists source_key text;
alter table public.seo_experiments add column if not exists source_key text;
alter table public.seo_experiments add column if not exists commit_sha text;
alter table public.seo_experiments add column if not exists status text;
alter table public.seo_experiments add column if not exists review_schedule jsonb not null default '[]'::jsonb;
alter table public.seo_experiments add column if not exists review_results jsonb not null default '{}'::jsonb;

drop index if exists public.seo_keywords_source_key_uidx;
drop index if exists public.seo_pages_source_key_uidx;
drop index if exists public.seo_technical_source_key_uidx;
drop index if exists public.seo_experiments_source_key_uidx;
create unique index seo_keywords_source_key_uidx on public.seo_keywords(source_key);
create unique index seo_pages_source_key_uidx on public.seo_pages(source_key);
create unique index seo_technical_source_key_uidx on public.seo_technical(source_key);
create unique index seo_experiments_source_key_uidx on public.seo_experiments(source_key);

create table if not exists public.seo_sector_opportunities (
  sector text primary key,
  open_jobs integer not null default 0,
  sector_page_exists boolean not null default false,
  url text,
  impressions integer,
  avg_position numeric,
  updated_at timestamptz not null default now()
);

create table if not exists public.seo_alerts (
  id uuid primary key default gen_random_uuid(),
  source_key text unique not null,
  type text not null,
  severity text not null,
  message text not null,
  url text,
  resolved boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Guided learning: automatically prioritised practice opportunities.
create table if not exists public.seo_opportunities (
  id uuid primary key default gen_random_uuid(),
  source_key text unique not null,
  category text not null,
  title text not null,
  explanation text,
  recommended_action text,
  course_week integer check (course_week between 1 and 16),
  priority text,
  impact integer check (impact between 1 and 5),
  effort integer check (effort between 1 and 5),
  url text,
  metrics jsonb not null default '{}'::jsonb,
  status text not null default 'new',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Evidence saved while completing practical course work.
create table if not exists public.seo_evidence (
  id uuid primary key default gen_random_uuid(),
  week integer not null check (week between 1 and 16),
  task_index integer,
  type text,
  title text not null,
  url text,
  notes text,
  captured_at date not null default current_date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Saved answers from the decision simulator.
create table if not exists public.seo_decisions (
  id uuid primary key default gen_random_uuid(),
  week integer not null check (week between 1 and 16),
  scenario text not null,
  selected_answer text,
  correct_answer text,
  is_correct boolean,
  reasoning text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Candidate job-alert subscribers. Public signups go through the validated
-- subscribe_job_alert RPC below; only admins can read or manage the table.
create table if not exists public.job_alert_subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null unique check (email = lower(email) and length(email) between 5 and 254),
  full_name text not null check (length(full_name) between 2 and 120),
  country_code text not null check (country_code ~ '^[A-Z]{2}$'),
  country_name text not null check (length(country_name) between 2 and 100),
  source_type text not null check (source_type in ('location_blocked', 'post_application', 'footer_signup')),
  sources text[] not null default '{}',
  source_job text,
  source_jobs text[] not null default '{}',
  source_url text,
  job_category text,
  status text not null default 'active' check (status in ('active', 'unsubscribed')),
  consent_at timestamptz not null default now(),
  last_opt_in_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.job_alert_subscribers enable row level security;
drop policy if exists job_alert_subscribers_admin_all on public.job_alert_subscribers;
create policy job_alert_subscribers_admin_all on public.job_alert_subscribers
  for all to authenticated using (public.is_admin()) with check (public.is_admin());
drop trigger if exists job_alert_subscribers_touch on public.job_alert_subscribers;
create trigger job_alert_subscribers_touch before update on public.job_alert_subscribers
  for each row execute function public.touch_updated_at();

create or replace function public.subscribe_job_alert(p_email text,p_full_name text,p_country_code text,p_country_name text,p_source_type text,p_source_job text default null,p_source_url text default null,p_job_category text default null)
returns uuid language plpgsql security definer set search_path = public as $$
declare clean_email text:=lower(trim(coalesce(p_email,''))); clean_name text:=trim(coalesce(p_full_name,'')); clean_country_code text:=upper(trim(coalesce(p_country_code,''))); clean_country_name text:=trim(coalesce(p_country_name,'')); clean_source text:=trim(coalesce(p_source_type,'')); subscriber_id uuid;
begin
  if clean_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' or length(clean_email)>254 then raise exception 'Please enter a valid email address'; end if;
  if length(clean_name)<2 or length(clean_name)>120 then raise exception 'Please enter your full name'; end if;
  if clean_country_code !~ '^[A-Z]{2}$' or length(clean_country_name)<2 then raise exception 'Please select your current country of residence'; end if;
  if clean_source not in ('location_blocked','post_application','footer_signup') then raise exception 'Invalid subscription source'; end if;
  insert into public.job_alert_subscribers(email,full_name,country_code,country_name,source_type,sources,source_job,source_jobs,source_url,job_category,status)
  values(clean_email,clean_name,clean_country_code,clean_country_name,clean_source,array[clean_source],nullif(trim(coalesce(p_source_job,'')),''),case when nullif(trim(coalesce(p_source_job,'')),'') is null then '{}'::text[] else array[trim(p_source_job)] end,nullif(trim(coalesce(p_source_url,'')),''),nullif(trim(coalesce(p_job_category,'')),''),'active')
  on conflict(email) do update set full_name=excluded.full_name,country_code=excluded.country_code,country_name=excluded.country_name,source_type=excluded.source_type,sources=case when excluded.source_type=any(job_alert_subscribers.sources) then job_alert_subscribers.sources else array_append(job_alert_subscribers.sources,excluded.source_type) end,source_job=coalesce(excluded.source_job,job_alert_subscribers.source_job),source_jobs=case when excluded.source_job is null or excluded.source_job=any(job_alert_subscribers.source_jobs) then job_alert_subscribers.source_jobs else array_append(job_alert_subscribers.source_jobs,excluded.source_job) end,source_url=coalesce(excluded.source_url,job_alert_subscribers.source_url),job_category=coalesce(excluded.job_category,job_alert_subscribers.job_category),status='active',consent_at=now(),last_opt_in_at=now()
  returning id into subscriber_id; return subscriber_id;
end; $$;
revoke all on public.job_alert_subscribers from anon;
grant select,update,delete on public.job_alert_subscribers to authenticated;
grant execute on function public.subscribe_job_alert(text,text,text,text,text,text,text,text) to anon,authenticated;

-- Course progress: one row per week (tasks, worksheet, QCM, KPI actions, résumé…)
create table if not exists public.seo_course_weeks (
  week integer primary key check (week between 0 and 16),  -- 0 = course-level (monthly, final, competencies)
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- ── RLS + triggers for every admin table ────────────────────────
do $$
declare t text;
begin
  foreach t in array array[
    'seo_settings','seo_kpi_daily','seo_keywords','seo_pages','seo_content',
    'seo_technical','seo_backlinks','seo_local','seo_ai_visibility',
    'seo_experiments','seo_course_weeks','seo_sector_opportunities','seo_alerts',
    'seo_opportunities','seo_evidence','seo_decisions','job_alert_subscribers'
  ] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists %I on public.%I', t || '_admin_all', t);
    execute format(
      'create policy %I on public.%I for all to authenticated using (public.is_admin()) with check (public.is_admin())',
      t || '_admin_all', t);
    execute format('drop trigger if exists %I on public.%I', t || '_touch', t);
    execute format(
      'create trigger %I before update on public.%I for each row execute function public.touch_updated_at()',
      t || '_touch', t);
  end loop;
end $$;
