#!/usr/bin/env python3
"""Normalize legacy open vacancies to the current job/application template."""

import json
from pathlib import Path

from add_jobs_from_csv import generate_job_page


ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "jobs"
REGISTRY = ROOT / "tools" / "jobs_registry.json"

LEGACY_FLAT_PAGES = (
    "electronic-technician",
    "commercial-divers",
    "trailer-drivers",
    "marine-mechanical-foreman",
    "administration-specialist",
    "delivery-man",
    "hvac-technician",
)


def clean_html(page: str) -> str:
    return "\n".join(line.rstrip() for line in page.splitlines()) + "\n"


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    open_jobs = [job for job in registry if job.get("status", "").lower() not in {"closed", "expired"}]
    by_slug = {job["slug"]: job for job in open_jobs}

    # These pages already contain the current design, but their trailing-slash
    # routes still served old redirect shells instead of the actual page.
    for slug in LEGACY_FLAT_PAGES:
        source = JOBS / f"{slug}.html"
        destination = JOBS / slug / "index.html"
        destination.write_text(clean_html(source.read_text(encoding="utf-8")), encoding="utf-8")

    # This was the final genuinely old-layout open vacancy. Rebuild it through
    # the same generator used by current job pages while retaining its content.
    job = dict(by_slug["application-developer-drupal"])
    job.update(
        about=(
            "This full-time hybrid role supports a delivery team working with a major European client. "
            "It is suited to a senior IT professional with at least 10 years of experience, strong Drupal "
            "10+ development skills, SharePoint-to-Drupal migration knowledge, database experience, and "
            "confident English communication for client-facing technical work."
        ),
        responsibilities="|".join(
            (
                "Install, support, and carry out security-related upgrades for Drupal websites.",
                "Develop custom Drupal modules, plugins, templates, and site functionality.",
                "Maintain structural coherence of Drupal websites and navigation systems.",
                "Provide maintenance support and implement new features according to business needs.",
                "Integrate Drupal systems with third-party applications and services.",
                "Customise themes and migrate data from SharePoint Online and SharePoint 2019.",
                "Administer and maintain applications and supporting infrastructure.",
                "Work within a delivery team supporting a major European client.",
            )
        ),
        requirements="|".join(
            (
                "University degree with a minimum of 10 years of IT professional experience.",
                "Proficiency in Drupal 10+ development, content structuring, hooks, APIs, and theming.",
                "Experience with responsive web design and object-oriented programming.",
                "SharePoint-to-Drupal migration expertise.",
                "Knowledge of MySQL and Azure Database for MySQL.",
                "Data visualisation skills using D3.js or Chart.js.",
                "Experience with JavaScript, jQuery, React, Angular, Vue.js, PHP, HTML5, CSS3, and AJAX.",
                "Microsoft Entra ID, Microsoft Graph API, and Azure DevOps experience.",
                "Web services and API development experience.",
                "Fluent English communication skills.",
            )
        ),
        offer="|".join(
            (
                "Full-time hybrid working arrangement.",
                "Opportunity to support a major European client.",
                "Exposure to Drupal 10+, SharePoint migration, Azure, APIs, and modern web technologies.",
                "Competitive salary package.",
                "Professional technical environment with long-term project scope.",
            )
        ),
        closing="If your background matches this Application Developer (Drupal) role, apply online today.",
    )
    page = clean_html(generate_job_page(job, other_jobs=open_jobs))
    (JOBS / job["slug"] / "index.html").write_text(page, encoding="utf-8")
    (JOBS / f'{job["slug"]}.html').write_text(page, encoding="utf-8")

    print(f"Normalized {len(LEGACY_FLAT_PAGES) + 1} open job templates.")


if __name__ == "__main__":
    main()
