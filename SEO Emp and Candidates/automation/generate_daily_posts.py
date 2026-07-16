#!/usr/bin/env python3
"""Generate three review-ready Outreach Recruitment SEO article drafts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "SEO Emp and Candidates" / "SKILL.md"
TOPICS = Path(__file__).with_name("topics.json")
STATE = Path(__file__).with_name("state.json")
OUTPUT = ROOT / "SEO Emp and Candidates" / "generated" / "daily"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:80].rstrip("-")


def load_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def existing_topics() -> str:
    paths = list((ROOT / "blog").glob("*.html")) + list(OUTPUT.glob("*.md"))
    return "\n".join(f"- {p.stem}" for p in sorted(paths))


def choose_topics(count: int):
    topics = load_json(TOPICS, [])
    if len(topics) < count:
        raise SystemExit(f"topics.json needs at least {count} topics")
    state = load_json(STATE, {"next_index": 0})
    start = int(state.get("next_index", 0)) % len(topics)
    chosen = [topics[(start + i) % len(topics)] for i in range(count)]
    state["next_index"] = (start + count) % len(topics)
    state["last_run"] = dt.date.today().isoformat()
    return chosen, state


def extract_text(payload: dict) -> str:
    if payload.get("output_text"):
        return payload["output_text"]
    chunks = []
    for item in payload.get("output", []):
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                chunks.append(part.get("text", ""))
    return "\n".join(chunks).strip()


def call_openai(prompt: str, model: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required (add it as a GitHub Actions secret)")
    body = json.dumps({
        "model": model,
        "input": prompt,
        "max_output_tokens": 9000,
    }).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            text = extract_text(json.load(response))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"OpenAI API error {exc.code}: {detail[:1000]}") from exc
    if len(text) < 1500:
        raise SystemExit("Model returned an unexpectedly short article")
    return text


def prompt_for(topic: dict, skill: str, date: str) -> str:
    return f"""Use the following Outreach Recruitment skill instructions to write ONE complete,
review-ready SEO blog article in Markdown. Do not claim that it has been published.

TOPIC: {topic['topic']}
AUDIENCE: {topic['audience']}
PRIMARY KEYWORD: {topic['primary_keyword']}
PUBLICATION DATE: {date}

Return only Markdown. Begin with YAML frontmatter containing title, slug, audience,
primary_keyword, seo_title, meta_description, date, status: draft, and review_required: true.
Then include the full useful article, direct-answer box as a blockquote, key takeaways,
logical H2/H3 sections, three audience-appropriate CTAs, 4-6 FAQs, related internal links,
schema recommendations, image brief/alt text, and SEO Audit Notes. Do not invent statistics,
clients, salaries, legal rules, visas, sponsorship, guarantees, or changing government facts.
Flag any time-sensitive fact for human verification. Avoid duplicating these existing topics:
{existing_topics()}

SKILL INSTRUCTIONS:
{skill}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5.6-luna"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    today = dt.date.today().isoformat()
    topics, state = choose_topics(args.count)
    if args.dry_run:
        print(json.dumps(topics, indent=2))
        return 0
    skill = SKILL.read_text()
    day_dir = OUTPUT / today
    day_dir.mkdir(parents=True, exist_ok=True)
    for topic in topics:
        slug = slugify(topic["topic"])
        destination = day_dir / f"{slug}.md"
        destination.write_text(call_openai(prompt_for(topic, skill, today), args.model).rstrip() + "\n")
        print(destination.relative_to(ROOT))
    STATE.write_text(json.dumps(state, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
