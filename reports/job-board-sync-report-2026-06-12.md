# Job Board Sync Report

Generated: 2026-06-12T12:09:06

## Counts

| Source | Count | Jobs scraped | Partial | URL |
|---|---:|---:|---|---|
| Careers platform | 220 | 200 | No | https://outreach-recruitment-agency.careers-page.com/?page=22 |
| Public website | Not found | 199 | Yes | https://outreachrecruitment.net/jobs/ |
| Local static grid | 218 | 198 | No | /Users/sof/Documents/Projects/OutreachRecruitmentwebsite/OutreachRecruitment-Jobs-in-Malta/jobs/index.html |

## Status

Counts do not match.

## Missing From Public Website Scrape

- Marine Mechanical Foreman
- Plate Shop Foreman
- Administration Specialist

## Missing From Local Static Grid

- Marine Mechanical Foreman
- Plate Shop Foreman
- Administration Specialist

## Public Website Jobs Not Found On Careers Platform

- Business Systems Analyst
- Multilingual Contact Centre Agent

## Local Static Jobs Not Found On Careers Platform

- Business Systems Analyst

## Warnings

- Careers platform: Careers count is 220, but scraper collected 200 titles.
- Public website: Suspicious footer/link text found on public site: bet
- Local static grid: Found 218 local job cards, but extracted 198 unique titles.

## Recommended Next Action

- Treat the careers platform as source of truth unless instructed otherwise.
- If local static grid differs, run `python3 tools/scrape_careers_page.py --csv-only` and review/import updates.
- If the public WordPress page differs, update or repair the WordPress jobs source so it mirrors the careers platform.
