---
name: job-board-sync-auditor
description: Audit Outreach Recruitment job board synchronization between outreachrecruitment.net/jobs, outreach-recruitment-agency.careers-page.com, and the local static jobs grid. Use when the user asks to compare open-position counts, find missing jobs, produce a daily job sync report, or check whether both job pages show the same active vacancies.
---

# Job Board Sync Auditor

## Overview

Compare Outreach Recruitment job listings across:

- Public website jobs page: `https://outreachrecruitment.net/jobs/`
- Careers platform: `https://outreach-recruitment-agency.careers-page.com/`
- Local static jobs grid: `jobs/index.html`, when present

Use this skill to report whether open-position counts match and which jobs appear to be missing from one source.

## Workflow

1. Run `tools/audit_job_boards.py`.
2. Review the generated Markdown report in `reports/`.
3. Summarize:
   - Open-position count on each source.
   - Whether counts match.
   - Jobs missing from the public website/local grid compared with the careers platform.
   - Jobs present on the public website/local grid but not found on the careers platform.
   - Any scraper limitations or source warnings.
4. If the user asks to fix the mismatch, use the existing job import/update tools before editing HTML manually:
   - `tools/scrape_careers_page.py`
   - `tools/add_jobs_from_csv.py`
   - `tools/update_jobs_listing.py`

## Daily Automation Guidance

A skill cannot run itself every day. To automate daily checks, connect the script to one of:

- GitHub Actions scheduled workflow.
- Server cron job.
- Netlify Scheduled Function.
- External monitor such as Zapier, Make, or a small VPS cron.

The daily task should run:

```bash
python3 tools/audit_job_boards.py
```

If the report says counts do not match, notify the user with:

- Careers platform count.
- Public website count.
- Local static grid count, if available.
- Count difference.
- Missing jobs.
- Suggested next action.

## Matching Rules

- Normalize titles before comparison: lowercase, trim spaces, remove repeated punctuation, and normalize ampersands.
- Treat the careers platform as the source of truth for active open positions unless the user says otherwise.
- Do not assume all public website jobs are visible if the site only renders the first page of results in static HTML.
- Clearly label partial results when only first-page public website titles can be scraped.
- Flag suspicious SEO/spam footer links on the public website separately because they may harm ranking and trust.

## Output Rules

- Be concise but specific.
- Include exact source URLs.
- Include report file path.
- Include a short recommendation.
- Do not claim a job is definitely missing if the source page pagination or JavaScript prevents full scraping; say it is missing from the scraped/visible results.
