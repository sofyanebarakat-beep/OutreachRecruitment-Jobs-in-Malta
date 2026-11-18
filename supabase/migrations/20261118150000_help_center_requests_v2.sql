-- Help Center v2 — run this ONE file in the Supabase SQL Editor (it also covers 20261118120000 if that was not run).
-- Topic-specific forms: Jobs / General questions, Hire (company + phone) and Study in Malta (phone + study plans).
create table if not exists public.help_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  full_name text not null,
  email text not null,
  current_location text,
  nationality text,
  job_title text,
  topic text not null default 'General',
  message text,
  page_url text,
  status text not null default 'new',
  admin_notes text
);
alter table public.help_requests add column if not exists phone text;
alter table public.help_requests add column if not exists company text;
alter table public.help_requests add column if not exists details jsonb not null default '{}'::jsonb;
alter table public.help_requests alter column current_location drop not null;
alter table public.help_requests alter column nationality drop not null;
alter table public.help_requests alter column job_title drop not null;
alter table public.help_requests alter column message drop not null;
alter table public.help_requests drop constraint if exists help_requests_topic_check;
alter table public.help_requests add constraint help_requests_topic_check check (topic in ('Jobs in Malta','Hire','Study in Malta','General'));
alter table public.help_requests drop constraint if exists help_requests_status_check;
alter table public.help_requests add constraint help_requests_status_check check (status in ('new','in_progress','answered','closed'));
create index if not exists help_requests_created_idx on public.help_requests (created_at desc);
create index if not exists help_requests_status_idx on public.help_requests (status);

alter table public.help_requests enable row level security;
drop policy if exists help_requests_admin_all on public.help_requests;
create policy help_requests_admin_all on public.help_requests for all to authenticated
  using (public.is_admin()) with check (public.is_admin());
grant select, insert, update, delete on public.help_requests to authenticated;

-- One validated entry point for every form in the pop-up. Visitors cannot read the table.
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
  insert into public.help_requests(full_name, email, phone, company, current_location, nationality, job_title, topic, message, page_url, details)
  values (v_name, v_email, nullif(v_phone, ''), nullif(v_company, ''), nullif(v_location, ''), nullif(v_nationality, ''), nullif(v_job, ''),
          v_topic, nullif(v_message, ''), left(p->>'page_url', 500), coalesce(p->'details', '{}'::jsonb))
  returning id into new_id;
  return jsonb_build_object('id', new_id, 'ok', true);
end;
$$;
revoke all on function public.submit_help_request_v2(jsonb) from public;
grant execute on function public.submit_help_request_v2(jsonb) to anon, authenticated;
