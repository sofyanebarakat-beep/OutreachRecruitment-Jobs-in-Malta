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

# One article per pillar per day, in this fixed rotation order.
PILLARS = ["Employer", "Candidate", "JobsInMalta", "StudyInMalta", "Brand"]


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
    by_pillar: dict[str, list[dict]] = {}
    for topic in topics:
        by_pillar.setdefault(topic["pillar"], []).append(topic)
    missing = [p for p in PILLARS if not by_pillar.get(p)]
    if missing:
        raise SystemExit(f"topics.json is missing topics for pillar(s): {', '.join(missing)}")

    state = load_json(STATE, {})
    pillar_state = state.get("pillars", {})

    chosen = []
    for i in range(count):
        pillar = PILLARS[i % len(PILLARS)]
        pillar_topics = by_pillar[pillar]
        next_index = int(pillar_state.get(pillar, {}).get("next_index", 0)) % len(pillar_topics)
        chosen.append(pillar_topics[next_index])
        pillar_state[pillar] = {"next_index": (next_index + 1) % len(pillar_topics)}

    state = {"pillars": pillar_state, "last_run": dt.date.today().isoformat()}
    return chosen, state


def extract_openai_text(payload: dict) -> str:
    if payload.get("output_text"):
        return payload["output_text"]
    chunks = []
    for item in payload.get("output", []):
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                chunks.append(part.get("text", ""))
    return "\n".join(chunks).strip()


def call_model(prompt: str, model: str) -> str:
    github_token = os.environ.get("GITHUB_TOKEN")
    openai_key = os.environ.get("OPENAI_API_KEY")
    if github_token:
        endpoint = "https://models.github.ai/inference/chat/completions"
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 6000,
        }).encode()
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        }
        provider = "GitHub Models"
    elif openai_key:
        endpoint = "https://api.openai.com/v1/responses"
        body = json.dumps({
            "model": model,
            "input": prompt,
            "max_output_tokens": 9000,
        }).encode()
        headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
        provider = "OpenAI"
    else:
        raise SystemExit("GITHUB_TOKEN or OPENAI_API_KEY is required")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            payload = json.load(response)
            if github_token:
                text = payload["choices"][0]["message"]["content"].strip()
            else:
                text = extract_openai_text(payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"{provider} API error {exc.code}: {detail[:1000]}") from exc
    if len(text) < 1500:
        raise SystemExit("Model returned an unexpectedly short article")
    return text


def prompt_for(topic: dict, skill: str, date: str) -> str:
    return f"""Use the following Outreach Recruitment skill instructions to write ONE complete,
review-ready SEO blog article in Markdown. Do not claim that it has been published.

PILLAR: {topic['pillar']}
TOPIC: {topic['topic']}
AUDIENCE: {topic['audience']}
PRIMARY KEYWORD: {topic['primary_keyword']}
PUBLICATION DATE: {date}

Apply the Audience Rules subsection for this PILLAR from the skill instructions below (Employer
Content, Candidate Content, Jobs in Malta (Market) Content, Study in Malta Content, or Brand /
Company Content). If PILLAR is StudyInMalta, still produce the same lightweight Markdown draft
structure as every other pillar — do not attempt the full STUDY IN MALTA SKILLS HTML template.

Return only Markdown. Begin with YAML frontmatter containing title, slug, pillar, audience,
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
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--model", default=os.environ.get("AI_MODEL", "openai/gpt-4.1-mini"))
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
        destination.write_text(call_model(prompt_for(topic, skill, today), args.model).rstrip() + "\n")
        print(destination.relative_to(ROOT))
    STATE.write_text(json.dumps(state, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
