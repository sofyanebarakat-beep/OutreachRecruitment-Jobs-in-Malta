create table if not exists public.job_alert_subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null unique check (email = lower(email) and length(email) between 5 and 254),
  full_name text not null check (length(full_name) between 2 and 120),
  country_code text not null check (country_code ~ '^[A-Z]{2}$'),
  country_name text not null check (length(country_name) between 2 and 100),
  source_type text not null check (source_type in ('location_blocked', 'post_application')),
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

create or replace function public.subscribe_job_alert(
  p_email text,
  p_full_name text,
  p_country_code text,
  p_country_name text,
  p_source_type text,
  p_source_job text default null,
  p_source_url text default null,
  p_job_category text default null
) returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  clean_email text := lower(trim(coalesce(p_email, '')));
  clean_name text := trim(coalesce(p_full_name, ''));
  clean_country_code text := upper(trim(coalesce(p_country_code, '')));
  clean_country_name text := trim(coalesce(p_country_name, ''));
  clean_source text := trim(coalesce(p_source_type, ''));
  subscriber_id uuid;
begin
  if clean_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' or length(clean_email) > 254 then
    raise exception 'Please enter a valid email address';
  end if;
  if length(clean_name) < 2 or length(clean_name) > 120 then
    raise exception 'Please enter your full name';
  end if;
  if clean_country_code !~ '^[A-Z]{2}$' or length(clean_country_name) < 2 then
    raise exception 'Please select your current country of residence';
  end if;
  if clean_source not in ('location_blocked', 'post_application') then
    raise exception 'Invalid subscription source';
  end if;

  insert into public.job_alert_subscribers (
    email, full_name, country_code, country_name, source_type, sources,
    source_job, source_jobs, source_url, job_category, status
  ) values (
    clean_email, clean_name, clean_country_code, clean_country_name, clean_source, array[clean_source],
    nullif(trim(coalesce(p_source_job, '')), ''),
    case when nullif(trim(coalesce(p_source_job, '')), '') is null then '{}'::text[] else array[trim(p_source_job)] end,
    nullif(trim(coalesce(p_source_url, '')), ''), nullif(trim(coalesce(p_job_category, '')), ''), 'active'
  )
  on conflict (email) do update set
    full_name = excluded.full_name,
    country_code = excluded.country_code,
    country_name = excluded.country_name,
    source_type = excluded.source_type,
    sources = case when excluded.source_type = any(job_alert_subscribers.sources)
      then job_alert_subscribers.sources else array_append(job_alert_subscribers.sources, excluded.source_type) end,
    source_job = coalesce(excluded.source_job, job_alert_subscribers.source_job),
    source_jobs = case when excluded.source_job is null or excluded.source_job = any(job_alert_subscribers.source_jobs)
      then job_alert_subscribers.source_jobs else array_append(job_alert_subscribers.source_jobs, excluded.source_job) end,
    source_url = coalesce(excluded.source_url, job_alert_subscribers.source_url),
    job_category = coalesce(excluded.job_category, job_alert_subscribers.job_category),
    status = 'active',
    consent_at = now(),
    last_opt_in_at = now()
  returning id into subscriber_id;

  return subscriber_id;
end;
$$;

revoke all on public.job_alert_subscribers from anon;
grant select, update, delete on public.job_alert_subscribers to authenticated;
grant execute on function public.subscribe_job_alert(text,text,text,text,text,text,text,text) to anon, authenticated;
