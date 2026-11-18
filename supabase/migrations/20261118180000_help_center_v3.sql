-- Help Center v3 — run once in the Supabase SQL Editor (after 20261118150000_help_center_requests_v2.sql).
-- Consent + 12-month retention, stronger spam limits, reply tracking, client flag, email-alert flag,
-- missed-search log and published Help Center questions (FAQs) built from answered requests.

-- 1) Requests: tracking columns
alter table public.help_requests add column if not exists consent_at timestamptz;
alter table public.help_requests add column if not exists answered_at timestamptz;
alter table public.help_requests add column if not exists alerted_at timestamptz;
alter table public.help_requests add column if not exists converted boolean not null default false;
alter table public.help_requests add column if not exists assigned_to text;

create or replace function public.help_requests_touch() returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  if new.status in ('answered','closed') and old.status not in ('answered','closed') and new.answered_at is null then
    new.answered_at := now();
  end if;
  return new;
end $$;
drop trigger if exists help_requests_touch on public.help_requests;
create trigger help_requests_touch before update on public.help_requests for each row execute function public.help_requests_touch();

-- 2) Submit: consent required, time-to-fill check, global flood limit, 12-month retention
create or replace function public.submit_help_request_v2(p jsonb) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_topic text := coalesce(nullif(trim(p->>'topic'), ''), 'General');
  v_name text := trim(coalesce(p->>'full_name', ''));
  v_email text := lower(trim(coalesce(p->>'email', '')));
  v_phone text := trim(coalesce(p->>'phone', ''));
  v_company text := trim(coalesce(p->>'company', ''));
  v_location text := trim(coalesce(p->>'current_location', ''));
  v_nationality text := trim(coalesce(p->>'nationality', ''));
  v_job text := trim(coalesce(p->>'job_title', ''));
  v_message text := trim(coalesce(p->>'message', ''));
  new_id uuid;
begin
  if coalesce(p->>'consent', '') <> 'true' then raise exception 'Please accept the privacy notice to send your request'; end if;
  if coalesce((p->>'elapsed_ms')::int, 0) < 2500 then raise exception 'Please take a moment to fill in the form'; end if;
  if v_topic not in ('Jobs in Malta','Hire','Study in Malta','General') then v_topic := 'General'; end if;
  if length(v_name) < 2 or length(v_name) > 120 then raise exception 'Please enter your full name'; end if;
  if v_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' or length(v_email) > 254 then raise exception 'Please enter a valid email address'; end if;
  if v_topic in ('Hire','Study in Malta') and v_phone !~ '^\+[0-9][0-9 ]{6,18}$' then raise exception 'Please enter a valid phone number'; end if;
  if v_topic = 'Hire' and length(v_company) < 2 then raise exception 'Please enter your company name'; end if;
  if v_topic in ('Jobs in Malta','General','Study in Malta') and (length(v_location) < 2 or length(v_nationality) < 2) then
    raise exception 'Please choose your current location and nationality'; end if;
  if v_topic in ('Jobs in Malta','General') and (length(v_job) < 2 or length(v_message) < 5) then raise exception 'Please add your job and your question'; end if;
  if greatest(length(v_company), length(v_location), length(v_nationality), length(v_job)) > 120 or length(v_message) > 4000 then
    raise exception 'One of the fields is too long'; end if;
  if (select count(*) from public.help_requests where email = v_email and created_at > now() - interval '1 hour') >= 5 then
    raise exception 'You have sent several requests already — our team will reply soon'; end if;
  if (select count(*) from public.help_requests where created_at > now() - interval '10 minutes') >= 40 then
    raise exception 'We are receiving many requests right now — please try again in a few minutes'; end if;
  -- GDPR retention: requests older than 12 months are deleted automatically
  delete from public.help_requests where created_at < now() - interval '12 months';
  insert into public.help_requests(full_name, email, phone, company, current_location, nationality, job_title, topic, message, page_url, details, consent_at)
  values (v_name, v_email, nullif(v_phone, ''), nullif(v_company, ''), nullif(v_location, ''), nullif(v_nationality, ''), nullif(v_job, ''),
          v_topic, nullif(v_message, ''), left(p->>'page_url', 500), coalesce(p->'details', '{}'::jsonb), now())
  returning id into new_id;
  return jsonb_build_object('id', new_id, 'ok', true);
end;
$$;
revoke all on function public.submit_help_request_v2(jsonb) from public;
grant execute on function public.submit_help_request_v2(jsonb) to anon, authenticated;

-- 3) Searches on /help-center with no results (shows which questions to write next)
create table if not exists public.help_search_misses (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  query text not null
);
create index if not exists help_search_misses_created_idx on public.help_search_misses (created_at desc);
alter table public.help_search_misses enable row level security;
drop policy if exists help_search_misses_admin_all on public.help_search_misses;
create policy help_search_misses_admin_all on public.help_search_misses for all to authenticated
  using (public.is_admin()) with check (public.is_admin());
grant select, delete on public.help_search_misses to authenticated;

create or replace function public.log_help_search_miss(q text) returns void
language plpgsql security definer set search_path = public as $$
declare clean text := lower(regexp_replace(trim(coalesce(q, '')), '\s+', ' ', 'g'));
begin
  if length(clean) < 3 or length(clean) > 120 then return; end if;
  if (select count(*) from public.help_search_misses where created_at > now() - interval '1 minute') >= 30 then return; end if;
  delete from public.help_search_misses where created_at < now() - interval '12 months';
  insert into public.help_search_misses(query) values (clean);
end $$;
revoke all on function public.log_help_search_miss(text) from public;
grant execute on function public.log_help_search_miss(text) to anon, authenticated;

-- 4) Help Center questions published on the website (built into /help-center by tools/build_help_center.py)
create table if not exists public.help_faqs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  category text not null check (category in ('jobs-in-malta','hire','study-in-malta')),
  question text not null,
  answer text not null,
  slug text not null unique,
  status text not null default 'draft' check (status in ('draft','published')),
  author_name text,
  source_request_id uuid references public.help_requests(id) on delete set null
);
alter table public.help_faqs enable row level security;
drop policy if exists help_faqs_admin_all on public.help_faqs;
create policy help_faqs_admin_all on public.help_faqs for all to authenticated
  using (public.is_admin()) with check (public.is_admin());
drop policy if exists help_faqs_public_read on public.help_faqs;
create policy help_faqs_public_read on public.help_faqs for select to anon using (status = 'published');
grant select, insert, update, delete on public.help_faqs to authenticated;
grant select on public.help_faqs to anon;
