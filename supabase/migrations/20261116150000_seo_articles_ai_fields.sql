-- Fix: "Could not find the 'entities' column of 'seo_articles' in the schema cache".
-- The AI generator returns entities, external_sources and social_posts with every draft.
-- Add them as columns so drafts save from both the admin and the Edge Function.
-- Safe to run more than once.
alter table public.seo_articles add column if not exists entities         jsonb not null default '[]'::jsonb;
alter table public.seo_articles add column if not exists external_sources jsonb not null default '[]'::jsonb;
alter table public.seo_articles add column if not exists social_posts     jsonb not null default '{}'::jsonb;

-- Make the API see the new columns immediately (clears the "schema cache" error).
notify pgrst, 'reload schema';
