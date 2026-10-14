-- Picture library for Admin › Email Marketing.
-- Run once in Supabase → SQL Editor (project atcitaqyraeqngcsaeun). Safe to re-run.
-- Bucket "marketing" is public for READING single files (so pictures can be embedded in emails),
-- but only admins (emails in public.admin_users) can list, upload or delete.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('marketing', 'marketing', true, 10485760, array['image/png', 'image/jpeg', 'image/webp', 'image/gif'])
on conflict (id) do update set public = excluded.public,
  file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "marketing admin read" on storage.objects;
create policy "marketing admin read" on storage.objects
  for select to authenticated using (bucket_id = 'marketing' and public.is_admin());

drop policy if exists "marketing admin insert" on storage.objects;
create policy "marketing admin insert" on storage.objects
  for insert to authenticated with check (bucket_id = 'marketing' and public.is_admin());

drop policy if exists "marketing admin update" on storage.objects;
create policy "marketing admin update" on storage.objects
  for update to authenticated using (bucket_id = 'marketing' and public.is_admin())
  with check (bucket_id = 'marketing' and public.is_admin());

drop policy if exists "marketing admin delete" on storage.objects;
create policy "marketing admin delete" on storage.objects
  for delete to authenticated using (bucket_id = 'marketing' and public.is_admin());
