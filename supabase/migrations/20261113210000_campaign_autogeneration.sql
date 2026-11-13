alter table public.seo_campaigns add column if not exists service_id uuid references public.seo_services on delete set null;
alter table public.seo_campaigns add column if not exists publish_days text[] not null default array['Tuesday','Friday'];
alter table public.seo_campaigns add column if not exists publish_time time not null default '09:00';
alter table public.seo_campaigns add column if not exists auto_generate boolean not null default true;
alter table public.seo_campaigns add column if not exists target_words int not null default 1200 check(target_words in (800,1200,1600,2000));
alter table public.seo_campaigns add column if not exists author_name text not null default 'Outreach Recruitment';
