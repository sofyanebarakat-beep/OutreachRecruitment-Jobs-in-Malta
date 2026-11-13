alter table public.seo_articles add column if not exists author_name text not null default 'Outreach Recruitment';
alter table public.seo_articles add column if not exists template_style text not null default 'editorial' check(template_style in ('editorial'));
