-- Help Center: questions sent from the support pop-up on /help-center (read and answered in /admin → Help Center Inbox).
create table if not exists public.help_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  full_name text not null,
  email text not null,
  current_location text not null,
  nationality text not null,
  job_title text not null,
  topic text not null default 'General' check (topic in ('Jobs in Malta','Hire','Study in Malta','General')),
  message text not null,
  page_url text,
  status text not null default 'new' check (status in ('new','in_progress','answered','closed')),
  admin_notes text
);
create index if not exists help_requests_created_idx on public.help_requests (created_at desc);
create index if not exists help_requests_status_idx on public.help_requests (status);

alter table public.help_requests enable row level security;
drop policy if exists help_requests_admin_all on public.help_requests;
create policy help_requests_admin_all on public.help_requests for all to authenticated
  using (public.is_admin()) with check (public.is_admin());
grant select, insert, update, delete on public.help_requests to authenticated;

-- Visitors never read the table; they can only submit through this validated function.
create or replace function public.submit_help_request(
  p_full_name text, p_email text, p_current_location text, p_nationality text,
  p_job_title text, p_topic text, p_message text, p_page_url text default null
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  clean_email text := lower(trim(coalesce(p_email, '')));
  clean_topic text := coalesce(nullif(trim(p_topic), ''), 'General');
  new_id uuid;
begin
  if length(trim(coalesce(p_full_name, ''))) < 2 or length(p_full_name) > 120 then raise exception 'Please enter your full name'; end if;
  if clean_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' or length(clean_email) > 254 then raise exception 'Please enter a valid email address'; end if;
  if length(trim(coalesce(p_current_location, ''))) < 2 or length(p_current_location) > 120 then raise exception 'Please enter your current location'; end if;
  if length(trim(coalesce(p_nationality, ''))) < 2 or length(p_nationality) > 120 then raise exception 'Please enter your nationality'; end if;
  if length(trim(coalesce(p_job_title, ''))) < 2 or length(p_job_title) > 120 then raise exception 'Please enter your job'; end if;
  if length(trim(coalesce(p_message, ''))) < 5 or length(p_message) > 4000 then raise exception 'Please write your question'; end if;
  if clean_topic not in ('Jobs in Malta','Hire','Study in Malta','General') then clean_topic := 'General'; end if;
  -- simple flood protection: at most 5 questions per email per hour
  if (select count(*) from public.help_requests where email = clean_email and created_at > now() - interval '1 hour') >= 5 then
    raise exception 'You have sent several questions already — our team will reply soon';
  end if;
  insert into public.help_requests(full_name, email, current_location, nationality, job_title, topic, message, page_url)
  values (trim(p_full_name), clean_email, trim(p_current_location), trim(p_nationality), trim(p_job_title), clean_topic, trim(p_message), left(p_page_url, 500))
  returning id into new_id;
  return jsonb_build_object('id', new_id, 'ok', true);
end;
$$;

revoke all on function public.submit_help_request(text,text,text,text,text,text,text,text) from public;
grant execute on function public.submit_help_request(text,text,text,text,text,text,text,text) to anon, authenticated;
