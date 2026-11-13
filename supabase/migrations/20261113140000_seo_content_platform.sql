-- Outreach Recruitment production SEO content platform.
-- Uses the existing public.is_admin() authorization function.
create extension if not exists pgcrypto;

create table if not exists public.seo_business_settings (
  id uuid primary key default gen_random_uuid(), key text not null unique, value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
create table if not exists public.seo_services (
  id uuid primary key default gen_random_uuid(), name text not null, slug text not null unique,
  short_description text, content text, main_keyword text, secondary_keywords text[] not null default '{}',
  seo_title text, meta_description text, featured_image_url text, image_alt text, target_location text default 'Malta',
  faqs jsonb not null default '[]', internal_links jsonb not null default '[]', status text not null default 'active' check(status in ('active','inactive')),
  priority int not null default 50 check(priority between 1 and 100), indexable boolean not null default true,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.seo_campaigns (
  id uuid primary key default gen_random_uuid(), name text not null, target_location text default 'Malta', language text default 'English',
  objective text, status text not null default 'planning' check(status in ('planning','active','paused','completed')),
  start_date date, articles_per_month int not null default 4, publishing_schedule text, notes text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.seo_campaign_services (
  campaign_id uuid references public.seo_campaigns on delete cascade, service_id uuid references public.seo_services on delete cascade,
  primary key(campaign_id,service_id)
);
create table if not exists public.seo_topics (
  id uuid primary key default gen_random_uuid(), keyword text not null, intent text not null default 'informational' check(intent in ('informational','commercial','transactional','local')),
  service_id uuid references public.seo_services on delete set null, campaign_id uuid references public.seo_campaigns on delete set null,
  target_location text default 'Malta', priority int default 50 check(priority between 1 and 100),
  status text not null default 'idea' check(status in ('idea','approved','drafted','rejected')), suggested_title text, notes text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique(keyword,target_location)
);
create table if not exists public.seo_articles (
  id uuid primary key default gen_random_uuid(), title text not null, slug text not null unique, excerpt text, focus_keyword text,
  secondary_keywords text[] not null default '{}', seo_title text, meta_description text, canonical_url text,
  og_title text, og_description text, og_image_url text, twitter_card text default 'summary_large_image', indexable boolean not null default true,
  service_id uuid references public.seo_services on delete set null, campaign_id uuid references public.seo_campaigns on delete set null,
  topic_id uuid references public.seo_topics on delete set null, language text default 'English', body text,
  featured_image_url text, featured_image_alt text, featured_image_width int, featured_image_height int,
  section_images jsonb not null default '[]', faqs jsonb not null default '[]', internal_links jsonb not null default '[]',
  schema_json jsonb not null default '{}'::jsonb,
  status text not null default 'draft' check(status in ('draft','generated','review','approved','scheduled','published','rejected','failed')),
  scheduled_at timestamptz, published_at timestamptz, published_url text, rejection_reason text,
  quality_score int default 0 check(quality_score between 0 and 100), quality_notes text,
  created_by uuid references auth.users on delete set null, approved_by uuid references auth.users on delete set null,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.seo_article_versions (
  id uuid primary key default gen_random_uuid(), article_id uuid not null references public.seo_articles on delete cascade,
  version int not null, snapshot jsonb not null, created_by uuid references auth.users on delete set null,
  created_at timestamptz not null default now(), unique(article_id,version)
);
create table if not exists public.seo_uploaded_images (
  id uuid primary key default gen_random_uuid(), article_id uuid references public.seo_articles on delete cascade,
  service_id uuid references public.seo_services on delete cascade, storage_path text not null unique, public_url text,
  mime_type text not null check(mime_type in ('image/jpeg','image/png','image/webp')), size_bytes bigint not null check(size_bytes <= 5242880),
  width int, height int, alt_text text not null, caption text, section_heading text, created_at timestamptz not null default now()
);
create table if not exists public.seo_schedules (
  id uuid primary key default gen_random_uuid(), article_id uuid not null references public.seo_articles on delete cascade,
  scheduled_at timestamptz not null, status text not null default 'pending', attempts int not null default 0,
  last_error text, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.seo_api_budgets (
  id uuid primary key default gen_random_uuid(), month text not null unique, monthly_limit numeric(12,4) not null default 100,
  current_spend numeric(12,4) not null default 0, reserved_spend numeric(12,4) not null default 0,
  warning_threshold int not null default 80 check(warning_threshold between 1 and 100), hard_stop boolean not null default true,
  updated_at timestamptz not null default now()
);
create table if not exists public.seo_api_usage (
  id uuid primary key default gen_random_uuid(), article_id uuid references public.seo_articles on delete set null,
  provider text not null, model text not null, action text not null, input_tokens int default 0, output_tokens int default 0,
  cost numeric(12,6) not null default 0, created_at timestamptz not null default now()
);
create table if not exists public.seo_automation_logs (
  id uuid primary key default gen_random_uuid(), job_name text not null, started_at timestamptz not null default now(), ended_at timestamptz,
  status text not null check(status in ('running','success','failed','skipped')), message text,
  article_id uuid references public.seo_articles on delete set null, error_details text, retry_count int not null default 0,
  updated_at timestamptz not null default now()
);
create table if not exists public.seo_leads (
  id uuid primary key default gen_random_uuid(), source_url text, source_type text, campaign_id uuid references public.seo_campaigns on delete set null,
  email text, metadata jsonb not null default '{}', created_at timestamptz not null default now()
);

-- Public visitors may read only published/indexable content. Admins own every write.
do $$ declare t text; begin
  foreach t in array array['seo_business_settings','seo_services','seo_campaigns','seo_campaign_services','seo_topics','seo_articles','seo_article_versions','seo_uploaded_images','seo_schedules','seo_api_budgets','seo_api_usage','seo_automation_logs','seo_leads'] loop
    execute format('alter table public.%I enable row level security',t);
    execute format('drop policy if exists %I on public.%I',t||'_admin_all',t);
    execute format('create policy %I on public.%I for all to authenticated using (public.is_admin()) with check (public.is_admin())',t||'_admin_all',t);
    execute format('grant select,insert,update,delete on public.%I to authenticated',t);
  end loop;
end $$;
drop policy if exists seo_services_public_read on public.seo_services;
create policy seo_services_public_read on public.seo_services for select to anon using(status='active' and indexable);
drop policy if exists seo_articles_public_read on public.seo_articles;
create policy seo_articles_public_read on public.seo_articles for select to anon using(status='published' and indexable);
grant select on public.seo_services, public.seo_articles to anon;

-- Storage bucket: authenticated admins can upload; images are publicly readable for social/SEO metadata.
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values('seo-content','seo-content',true,5242880,array['image/jpeg','image/png','image/webp']) on conflict(id) do update
set file_size_limit=excluded.file_size_limit, allowed_mime_types=excluded.allowed_mime_types;
drop policy if exists seo_content_public_read on storage.objects;
create policy seo_content_public_read on storage.objects for select to public using(bucket_id='seo-content');
drop policy if exists seo_content_admin_write on storage.objects;
create policy seo_content_admin_write on storage.objects for all to authenticated using(bucket_id='seo-content' and public.is_admin()) with check(bucket_id='seo-content' and public.is_admin());

insert into public.seo_services(name,slug,short_description,main_keyword,secondary_keywords,seo_title,meta_description,target_location,status,priority,indexable)
values
('Recruitment for Malta Employers','recruitment-for-employers-malta','Demo service — recruitment support for companies hiring in Malta.','recruitment agency Malta',array['hire staff Malta','Malta employers'],'Recruitment Agency Malta | Outreach Recruitment','Recruitment agency Malta support for employers hiring qualified people across Europe.','Malta','active',90,true),
('Jobs in Malta for European Candidates','jobs-in-malta-european-candidates','Demo service — job-search support for candidates already based in Europe.','jobs in Malta',array['work in Malta','Malta vacancies'],'Jobs in Malta for European Candidates','Explore jobs in Malta and practical support for candidates currently based in Europe.','Malta and Europe','active',95,true),
('Study in Malta','study-in-malta-international-students','Demo service — guidance for international students considering Malta.','study in Malta',array['Malta courses international students','Malta student guide'],'Study in Malta | International Student Guidance','Study in Malta with clear guidance for international students comparing courses and preparing their move.','International','active',85,true)
on conflict(slug) do nothing;
insert into public.seo_api_budgets(month,monthly_limit,current_spend,reserved_spend,warning_threshold,hard_stop)
values(to_char(now(),'YYYY-MM'),100,0,0,80,true) on conflict(month) do nothing;
