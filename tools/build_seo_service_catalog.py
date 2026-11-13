#!/usr/bin/env python3
"""Build the admin's service catalogue from the website's own SEO metadata."""
from __future__ import annotations
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ("employers.html", "Recruitment for Malta Employers", "recruitment agency Malta", 95, "Malta"),
    ("opening-jobs-in-malta.html", "Jobs in Malta", "jobs in Malta", 100, "Malta and Europe"),
    ("study-in-malta.html", "Study in Malta", "study in Malta", 95, "International"),
    ("subcontracting-jobs-in-malta.html", "Subcontracting in Malta", "subcontracting jobs Malta", 75, "Malta"),
    ("hospitality-jobs-in-malta.html", "Hospitality Jobs in Malta", "hospitality jobs Malta", 85, "Malta"),
    ("construction-jobs-in-malta.html", "Construction Jobs in Malta", "construction jobs Malta", 85, "Malta"),
    ("customer-service-jobs-in-malta.html", "Customer Service Jobs in Malta", "customer service jobs Malta", 80, "Malta"),
    ("finance-jobs-in-malta.html", "Finance Jobs in Malta", "finance jobs Malta", 80, "Malta"),
    ("retail-jobs-in-malta.html", "Retail Jobs in Malta", "retail jobs Malta", 75, "Malta"),
    ("information-technology-programs.html", "IT Study Programmes in Malta", "IT courses Malta", 75, "International"),
    ("business-administration-programs.html", "Business Administration Programmes", "business courses Malta", 70, "International"),
]

def meta(source: str, name: str) -> str:
    patterns = [
        rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']*)',
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']{re.escape(name)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, source, re.I)
        if match:
            return html.unescape(match.group(1)).strip()
    return ""

def title(source: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", source, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip() if match else ""

services = []
for filename, fallback_name, keyword, priority, location in PAGES:
    path = ROOT / filename
    if not path.exists():
        continue
    source = path.read_text(encoding="utf-8", errors="ignore")
    description = meta(source, "description")
    slug = filename.removesuffix(".html")
    services.append({
        "name": fallback_name,
        "slug": slug,
        "short_description": description,
        "main_keyword": keyword,
        "secondary_keywords": [],
        "seo_title": title(source) or fallback_name,
        "meta_description": description,
        "target_location": location,
        "status": "active",
        "priority": priority,
        "indexable": True,
    })

output = {"generated_at": datetime.now(timezone.utc).isoformat(), "source": "website SEO metadata", "services": services}
(ROOT / "assets" / "seo-service-catalog.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Built {len(services)} service records")
