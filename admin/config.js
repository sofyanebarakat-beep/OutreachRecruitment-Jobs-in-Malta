// Supabase connection for the SEO admin.
// Leave both empty to run in local mode (data saved in this browser only).
// Fill in from Supabase → Project Settings → API. The anon/publishable key is
// safe to commit: every table is locked by RLS to emails in public.admin_users
// (see supabase/admin_schema.sql). NEVER put the service_role key here.
const adminLocalPreview = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && new URLSearchParams(location.search).has("local");
window.ADMIN_CONFIG = {
  SUPABASE_URL: adminLocalPreview ? "" : "https://atcitaqyraeqngcsaeun.supabase.co",
  SUPABASE_ANON_KEY: adminLocalPreview ? "" : "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY",
  // Real site data served from this repo (relative to /admin/)
  JOBS_REGISTRY: "../tools/jobs_registry.json",
  GSC_PAGES_CSV: "../reports/gsc_search_performance.csv",
  GSC_PROBLEMS_CSV: "../reports/gsc_indexing_problems.csv",
  AUTOMATION_REPORT: "../reports/seo-automation-latest.json",
  // Baseline recorded 2026-09-09 (28-day sitewide GSC)
  BASELINE: { date: "2026-09-09", clicks28: 1251, impressions28: 31700 },
};
