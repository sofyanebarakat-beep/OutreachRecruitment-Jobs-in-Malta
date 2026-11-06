create table if not exists public.jobs_featured (
  id text primary key check (id = 'current'),
  slugs text[] not null check (cardinality(slugs) = 3),
  updated_at timestamptz not null default now()
);

alter table public.jobs_featured enable row level security;

drop policy if exists jobs_featured_public_read on public.jobs_featured;
create policy jobs_featured_public_read on public.jobs_featured
  for select to anon, authenticated using (true);

drop policy if exists jobs_featured_admin_write on public.jobs_featured;
create policy jobs_featured_admin_write on public.jobs_featured
  for all to authenticated using (public.is_admin()) with check (public.is_admin());

drop trigger if exists jobs_featured_touch on public.jobs_featured;
create trigger jobs_featured_touch before update on public.jobs_featured
  for each row execute function public.touch_updated_at();

grant select on public.jobs_featured to anon, authenticated;
grant insert, update, delete on public.jobs_featured to authenticated;
