-- The first featured-jobs migration allowed exactly three slugs. The admin and
-- public job board now curate six, so replace every legacy constraint name.
alter table public.jobs_featured
  drop constraint if exists jobs_featured_slugs_check;

alter table public.jobs_featured
  drop constraint if exists jobs_featured_three_slugs_check;

alter table public.jobs_featured
  drop constraint if exists jobs_featured_six_slugs_check;

alter table public.jobs_featured
  add constraint jobs_featured_six_slugs_check
  check (cardinality(slugs) between 3 and 6);
