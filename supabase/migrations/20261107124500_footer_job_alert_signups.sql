alter table public.job_alert_subscribers
  drop constraint if exists job_alert_subscribers_source_type_check;

alter table public.job_alert_subscribers
  add constraint job_alert_subscribers_source_type_check
  check (source_type in ('location_blocked', 'post_application', 'footer_signup'));

create or replace function public.subscribe_job_alert_v2(
  p_email text,
  p_full_name text,
  p_country_code text,
  p_country_name text,
  p_source_type text,
  p_source_job text default null,
  p_source_url text default null,
  p_job_category text default null
) returns jsonb
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
  existing public.job_alert_subscribers%rowtype;
  subscriber_id uuid;
begin
  if clean_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' or length(clean_email) > 254 then raise exception 'Please enter a valid email address'; end if;
  if length(clean_name) < 2 or length(clean_name) > 120 then raise exception 'Please enter your full name'; end if;
  if clean_country_code !~ '^[A-Z]{2}$' or length(clean_country_name) < 2 then raise exception 'Please select your current country of residence'; end if;
  if clean_source not in ('location_blocked', 'post_application', 'footer_signup') then raise exception 'Invalid subscription source'; end if;

  select * into existing from public.job_alert_subscribers where email = clean_email;
  if found and existing.status = 'active' then
    return jsonb_build_object('id', existing.id, 'created', false, 'already_subscribed', true, 'reactivated', false);
  end if;

  if found then
    update public.job_alert_subscribers set
      full_name = clean_name, country_code = clean_country_code, country_name = clean_country_name,
      source_type = clean_source,
      sources = case when clean_source = any(sources) then sources else array_append(sources, clean_source) end,
      source_job = coalesce(nullif(trim(coalesce(p_source_job, '')), ''), source_job),
      source_jobs = case when nullif(trim(coalesce(p_source_job, '')), '') is null or trim(p_source_job) = any(source_jobs) then source_jobs else array_append(source_jobs, trim(p_source_job)) end,
      source_url = coalesce(nullif(trim(coalesce(p_source_url, '')), ''), source_url),
      job_category = coalesce(nullif(trim(coalesce(p_job_category, '')), ''), job_category),
      status = 'active', consent_at = now(), last_opt_in_at = now()
    where id = existing.id returning id into subscriber_id;
    return jsonb_build_object('id', subscriber_id, 'created', false, 'already_subscribed', false, 'reactivated', true);
  end if;

  insert into public.job_alert_subscribers(email,full_name,country_code,country_name,source_type,sources,source_job,source_jobs,source_url,job_category,status)
  values(clean_email,clean_name,clean_country_code,clean_country_name,clean_source,array[clean_source],nullif(trim(coalesce(p_source_job,'')),''),case when nullif(trim(coalesce(p_source_job,'')),'') is null then '{}'::text[] else array[trim(p_source_job)] end,nullif(trim(coalesce(p_source_url,'')),''),nullif(trim(coalesce(p_job_category,'')),''),'active')
  returning id into subscriber_id;
  return jsonb_build_object('id', subscriber_id, 'created', true, 'already_subscribed', false, 'reactivated', false);
exception when unique_violation then
  select id into subscriber_id from public.job_alert_subscribers where email = clean_email;
  return jsonb_build_object('id', subscriber_id, 'created', false, 'already_subscribed', true, 'reactivated', false);
end;
$$;

grant execute on function public.subscribe_job_alert_v2(text,text,text,text,text,text,text,text) to anon, authenticated;
