"""
Fix and audit JobPosting JSON-LD on job detail pages.

The script uses tools/jobs_registry.json as the source of active jobs, reads the
matching jobs/<slug>/index.html page, rebuilds the JobPosting schema, and writes
the updated JSON-LD back into the page.
"""
from __future__ import annotations

import json
import re
from datetime import date
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tools" / "jobs_registry.json"
JOBS = ROOT / "jobs"
BASE_URL = "https://outreachrecruitment.net"
TODAY = date.today().isoformat()
DEFAULT_VALID_THROUGH = "2026-12-31"
DEFAULT_POSTAL_CODE = "0000"

REQUIRED_FIELDS = [
    "title",
    "description",
    "datePosted",
    "hiringOrganization",
    "jobLocation",
]

EMPLOYMENT_TYPE = {
    "full-time": "FULL_TIME",
    "part-time": "PART_TIME",
    "subcontracting": "CONTRACTOR",
    "contract": "CONTRACTOR",
    "temporary": "TEMPORARY",
    "internship": "INTERN",
}

OCCUPATIONAL_CATEGORY = {
    "hospitality": "Food Service Workers",
    "retail": "Retail Sales Workers",
    "engineering & maintenance": "Installation, Maintenance, and Repair Workers",
    "it": "Computer and Mathematical Occupations",
    "it & technology": "Computer and Mathematical Occupations",
    "finance": "Business and Financial Operations Occupations",
    "finance & accounting": "Business and Financial Operations Occupations",
    "healthcare": "Healthcare Support Occupations",
    "education": "Educational Instruction and Library Occupations",
    "logistics": "Transportation and Material Moving Occupations",
    "construction": "Construction and Extraction Occupations",
    "administration": "Office and Administrative Support Occupations",
    "marketing": "Arts, Design, Entertainment, Sports, and Media Occupations",
    "sales": "Sales and Related Occupations",
}


def clean_text(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_section(html: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}</h2><div class=\"w-richtext\">(.*?)(?:</div>)"
    match = re.search(pattern, html, flags=re.S)
    return match.group(1) if match else ""


def extract_list_items(section_html: str) -> list[str]:
    return [clean_text(item) for item in re.findall(r"<li[^>]*>(.*?)</li>", section_html, flags=re.S) if clean_text(item)]


def extract_paragraph(section_html: str) -> str:
    match = re.search(r"<p[^>]*>(.*?)</p>", section_html, flags=re.S)
    return clean_text(match.group(1)) if match else clean_text(section_html)


def first_jobposting_schema(html: str) -> dict | None:
    for block in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, flags=re.S):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "JobPosting":
            return data
    return None


def description_from_page(html: str, job: dict) -> str:
    about = extract_paragraph(extract_section(html, "About the Role"))
    responsibilities = extract_list_items(extract_section(html, "Key Responsibilities"))
    requirements = extract_list_items(extract_section(html, "Requirements"))
    offer = extract_list_items(extract_section(html, "What's on Offer"))

    if not about:
        about = (
            f"{job['title']} role in {job['location']} within {job['category']}. "
            "Apply through Outreach Recruitment Agency."
        )
    if not responsibilities:
        responsibilities = [f"Carry out duties related to the {job['title']} role."]
    if not requirements:
        requirements = ["Relevant experience or suitability for the role."]

    parts = [f"<p>{escape(about)}</p>"]
    parts.append("<p>Key Responsibilities:</p><ul>" + "".join(f"<li>{escape(item)}</li>" for item in responsibilities) + "</ul>")
    parts.append("<p>Requirements:</p><ul>" + "".join(f"<li>{escape(item)}</li>" for item in requirements) + "</ul>")
    if offer:
        parts.append("<p>What's on Offer:</p><ul>" + "".join(f"<li>{escape(item)}</li>" for item in offer) + "</ul>")
    return "".join(parts)


def schema_employment_type(value: str) -> str:
    return EMPLOYMENT_TYPE.get(value.lower(), "FULL_TIME")


def city_from_location(location: str) -> str:
    return location.split(",")[0].strip()


def hiring_organization(job: dict) -> dict:
    if str(job.get("confidential_employer", "")).lower() in {"1", "true", "yes"}:
        return {
            "@type": "Organization",
            "name": "confidential",
        }

    name = (
        job.get("employer_name")
        or job.get("hiring_organization")
        or job.get("company_name")
        or "Outreach Recruitment Ltd"
    )
    organization = {
        "@type": "Organization",
        "name": name,
    }
    same_as = job.get("employer_url") or (BASE_URL if name == "Outreach Recruitment Ltd" else "")
    logo = job.get("employer_logo") or (f"{BASE_URL}/assets/outreach-recruitment-logo.svg" if name == "Outreach Recruitment Ltd" else "")
    if same_as:
        organization["sameAs"] = same_as
    if logo:
        organization["logo"] = logo
    return organization


def postal_address(job: dict) -> dict:
    locality = job.get("address_locality") or city_from_location(job["location"])
    address = {
        "@type": "PostalAddress",
        "streetAddress": job.get("street_address") or job.get("location") or locality,
        "addressLocality": locality,
        "addressRegion": job.get("address_region") or "Malta",
        "postalCode": job.get("postal_code") or DEFAULT_POSTAL_CODE,
        "addressCountry": job.get("address_country") or "MT",
    }
    return address


def credential_category(text: str) -> str:
    value = text.lower()
    if "postgraduate" in value or "master" in value or "phd" in value or "doctorate" in value:
        return "postgraduate degree"
    if "degree" in value or "university" in value or "bachelor" in value or "mqf" in value or "eqf" in value:
        return "bachelor degree"
    if "certificate" in value or "certification" in value or "licence" in value or "license" in value:
        return "professional certificate"
    if "diploma" in value or "associate" in value:
        return "associate degree"
    if "school" in value:
        return "high school"
    return "no requirements"


def months_of_experience(text: str) -> int | None:
    matches = []
    for number, unit in re.findall(r"(\d+)\s*(?:\+)?\s*(year|years|yr|yrs|month|months)", text.lower()):
        n = int(number)
        matches.append(n * 12 if unit.startswith(("year", "yr")) else n)
    return min(matches) if matches else None


def section_text(html: str, heading: str) -> str:
    section = extract_section(html, heading)
    items = extract_list_items(section)
    if items:
        return " ".join(items)
    return extract_paragraph(section)


def education_requirements(html: str, job: dict) -> dict:
    text = job.get("education_requirements") or section_text(html, "Requirements")
    return {
        "@type": "EducationalOccupationalCredential",
        "credentialCategory": credential_category(text),
    }


def experience_requirements(html: str, job: dict) -> dict | str:
    text = job.get("experience_requirements") or section_text(html, "Requirements")
    months = months_of_experience(text)
    if months is None:
        if "experience" in text.lower():
            months = 1
        else:
            return "no requirements"
    return {
        "@type": "OccupationalExperienceRequirements",
        "monthsOfExperience": months,
    }


def base_salary(job: dict) -> dict | None:
    currency = job.get("salary_currency") or "EUR"
    unit = (job.get("salary_unit") or "YEAR").upper()
    if unit not in {"HOUR", "DAY", "WEEK", "MONTH", "YEAR"}:
        unit = "YEAR"

    value = job.get("base_salary") or job.get("salary")
    min_value = job.get("salary_min")
    max_value = job.get("salary_max")
    if value:
        try:
            quantity = {
                "@type": "QuantitativeValue",
                "value": float(str(value).replace(",", "").strip()),
                "unitText": unit,
            }
        except ValueError:
            return None
    elif min_value and max_value:
        try:
            quantity = {
                "@type": "QuantitativeValue",
                "minValue": float(str(min_value).replace(",", "").strip()),
                "maxValue": float(str(max_value).replace(",", "").strip()),
                "unitText": unit,
            }
        except ValueError:
            return None
    else:
        return None

    return {
        "@type": "MonetaryAmount",
        "currency": currency,
        "value": quantity,
    }


def fallback_job_from_schema(path: Path, html: str, schema: dict) -> dict:
    slug = path.parent.name
    address = ((schema.get("jobLocation") or {}).get("address") or {})
    org = schema.get("hiringOrganization") or {}
    employment = schema.get("employmentType") or "FULL_TIME"
    employment_label = employment.replace("_", "-").title()
    location = ", ".join(
        value for value in [address.get("addressLocality"), address.get("addressRegion")]
        if value
    ) or "Malta"
    job = {
        "slug": slug,
        "title": schema.get("title") or slug.replace("-", " ").title(),
        "category": schema.get("industry") or schema.get("occupationalCategory") or "General",
        "location": location,
        "location_slug": location.lower(),
        "employment_type": employment_label,
        "work_mode": "Remote" if schema.get("jobLocationType") == "TELECOMMUTE" else "On-Site",
        "date": schema.get("datePosted") or TODAY,
        "valid_through": schema.get("validThrough") or DEFAULT_VALID_THROUGH,
        "employer_name": org.get("name") or "Outreach Recruitment Ltd",
        "employer_url": org.get("sameAs") or "",
        "employer_logo": org.get("logo") or "",
        "street_address": address.get("streetAddress") or "",
        "postal_code": address.get("postalCode") or "",
        "address_locality": address.get("addressLocality") or "",
        "address_region": address.get("addressRegion") or "",
        "address_country": address.get("addressCountry") or "",
    }
    existing_education = schema.get("educationRequirements")
    if isinstance(existing_education, str):
        job["education_requirements"] = existing_education
    existing_experience = schema.get("experienceRequirements")
    if isinstance(existing_experience, str):
        job["experience_requirements"] = existing_experience
    return job


def build_schema(html: str, job: dict) -> dict:
    slug = job["slug"]
    title = job["title"]
    city = city_from_location(job["location"])
    category = job["category"]
    valid_through = job.get("valid_through") or DEFAULT_VALID_THROUGH

    schema = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": title,
        "description": description_from_page(html, job),
        "identifier": {
            "@type": "PropertyValue",
            "name": "Outreach Recruitment Ltd",
            "value": slug,
        },
        "url": f"{BASE_URL}/jobs/{slug}",
        "datePosted": job["date"],
        "employmentType": schema_employment_type(job["employment_type"]),
        "industry": category,
        "occupationalCategory": OCCUPATIONAL_CATEGORY.get(category.lower(), category),
        "hiringOrganization": hiring_organization(job),
        "jobLocation": {
            "@type": "Place",
            "address": postal_address(job),
        },
        "applicantLocationRequirements": {
            "@type": "Country",
            "name": "Malta",
        },
        "workHours": job["employment_type"],
        "educationRequirements": education_requirements(html, job),
        "experienceRequirements": experience_requirements(html, job),
        "directApply": True,
        "applicationContact": {
            "@type": "ContactPoint",
            "email": "hr@outreachrecruitment.net",
            "contactType": "Human Resources",
        },
    }
    if valid_through:
        schema["validThrough"] = valid_through
    if job.get("work_mode", "").lower() == "remote":
        schema["jobLocationType"] = "TELECOMMUTE"
    salary = base_salary(job)
    if salary:
        schema["baseSalary"] = salary
    return schema


def replace_jobposting_schema(html: str, schema: dict) -> tuple[str, bool]:
    pattern = r'(<script type="application/ld\+json">\s*)(\{.*?"@type"\s*:\s*"JobPosting".*?\})(\s*</script>)'
    replacement = r"\1" + json.dumps(schema, ensure_ascii=False, indent=2) + r"\3"
    updated, count = re.subn(pattern, replacement, html, count=1, flags=re.S)
    return updated, count == 1


def validate_schema(schema: dict) -> list[str]:
    issues = []
    for field in REQUIRED_FIELDS:
        if not schema.get(field):
            issues.append(f"missing {field}")

    if schema.get("@type") != "JobPosting":
        issues.append("invalid @type")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(T.*)?", schema.get("datePosted", "")):
        issues.append("invalid datePosted")
    if schema.get("validThrough") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}(T.*)?", schema["validThrough"]):
        issues.append("invalid validThrough")
    if schema.get("validThrough", "9999-12-31") < TODAY:
        issues.append("expired validThrough")
    if schema.get("description") == schema.get("title"):
        issues.append("description equals title")
    if not re.search(r"<(p|ul|li|br)\b", schema.get("description", "")):
        issues.append("description is not HTML formatted")

    org = schema.get("hiringOrganization") or {}
    if not org.get("name"):
        issues.append("missing hiringOrganization.name")

    address = ((schema.get("jobLocation") or {}).get("address") or {})
    if not address.get("addressCountry"):
        issues.append("missing jobLocation.address.addressCountry")
    if not address.get("addressLocality"):
        issues.append("missing jobLocation.address.addressLocality")
    return issues


def main() -> None:
    jobs = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry_slugs = {job["slug"] for job in jobs}
    extra_jobs = []
    for path in sorted(JOBS.glob("*/index.html")):
        if path.parent.name in registry_slugs:
            continue
        html = path.read_text(encoding="utf-8")
        schema = first_jobposting_schema(html)
        if schema:
            extra_jobs.append(fallback_job_from_schema(path, html, schema))

    all_jobs = jobs + extra_jobs
    changed = 0
    missing_pages = []
    failed_replace = []
    audit_rows = []
    registry_changed = False

    for job in all_jobs:
        path = JOBS / job["slug"] / "index.html"
        if not path.exists():
            missing_pages.append(job["slug"])
            continue

        html = path.read_text(encoding="utf-8")
        schema = build_schema(html, job)
        issues = validate_schema(schema)
        updated, ok = replace_jobposting_schema(html, schema)
        if not ok:
            failed_replace.append(job["slug"])
            continue
        if updated != html:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            if job["slug"] in registry_slugs and job.get("lastmod") != TODAY:
                job["lastmod"] = TODAY
                registry_changed = True
        audit_rows.append((job["slug"], len(schema["description"]), issues))

    issue_rows = [(slug, length, issues) for slug, length, issues in audit_rows if issues]

    print(f"Jobs in registry: {len(jobs)}")
    print(f"Extra job pages with schema: {len(extra_jobs)}")
    print(f"Pages updated: {changed}")
    print(f"Pages audited: {len(audit_rows)}")
    print(f"Missing pages: {len(missing_pages)}")
    print(f"Schema replace failures: {len(failed_replace)}")
    print(f"Pages with schema issues after rebuild: {len(issue_rows)}")
    if registry_changed:
        REGISTRY.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Registry lastmod fields updated: yes")
    else:
        print("Registry lastmod fields updated: no")
    print("")

    if missing_pages:
        print("Missing pages:")
        for slug in missing_pages:
            print(f"  - {slug}")

    if failed_replace:
        print("Schema replace failures:")
        for slug in failed_replace:
            print(f"  - {slug}")

    if issue_rows:
        print("Schema issues:")
        for slug, _, issues in issue_rows:
            print(f"  - {slug}: {', '.join(issues)}")
    else:
        print("Schema issues: none")

    print("")
    print("Sample audited pages:")
    for slug, length, _ in audit_rows[:10]:
        print(f"  - {slug}: JobPosting OK, description {length} chars")


if __name__ == "__main__":
    main()
