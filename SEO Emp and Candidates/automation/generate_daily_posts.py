#!/usr/bin/env python3
"""Generate three review-ready Outreach Recruitment SEO article drafts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
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

# Spacing between sequential model calls to avoid tripping the free-tier rate limit.
INTER_CALL_DELAY_SECONDS = 20
MAX_RETRIES = 5
RETRY_BASE_DELAY_SECONDS = 20
RETRY_MAX_DELAY_SECONDS = 180


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:80].rstrip("-")


def load_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def existing_topics() -> str:
    paths = list((ROOT / "blog").glob("*.html")) + list(OUTPUT.glob("*.md"))
    return "\n".join(f"- {p.stem}" for p in sorted(paths))


def choose_topics(count: int):
    """Pick one topic per pillar in rotation order.

    Returns (entries, pillar_state) where pillar_state is the *pre-run* per-pillar
    index map. Each entry carries the index/count it was drawn from so the caller
    can advance that pillar's index only after a successful generation — a topic
    that fails (e.g. rate limited) is retried on the next run instead of being
    skipped.
    """
    topics = load_json(TOPICS, [])
    by_pillar: dict[str, list[dict]] = {}
    for topic in topics:
        by_pillar.setdefault(topic["pillar"], []).append(topic)
    missing = [p for p in PILLARS if not by_pillar.get(p)]
    if missing:
        raise SystemExit(f"topics.json is missing topics for pillar(s): {', '.join(missing)}")

    state = load_json(STATE, {})
    pillar_state = dict(state.get("pillars", {}))

    entries = []
    for i in range(count):
        pillar = PILLARS[i % len(PILLARS)]
        pillar_topics = by_pillar[pillar]
        used_index = int(pillar_state.get(pillar, {}).get("next_index", 0)) % len(pillar_topics)
        entries.append({
            "pillar": pillar,
            "topic": pillar_topics[used_index],
            "index": used_index,
            "count": len(pillar_topics),
        })

    return entries, pillar_state


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
        endpoint = "https://api.openai.com/v1/chat/completions"
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 6000,
        }).encode()
        headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
        provider = "OpenAI"
    else:
        raise SystemExit("GITHUB_TOKEN or OPENAI_API_KEY is required")

    delay = RETRY_BASE_DELAY_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
        try:
            # Increased timeout from 300s to 600s (10 minutes) for better resilience
            with urllib.request.urlopen(request, timeout=600) as response:
                payload = json.load(response)
                text = payload["choices"][0]["message"]["content"].strip()
            if len(text) < 1500:
                raise SystemExit("Model returned an unexpectedly short article")
            return text
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            retryable = exc.code == 429 or exc.code >= 500
            if not retryable or attempt == MAX_RETRIES:
                raise SystemExit(f"{provider} API error {exc.code}: {detail[:1000]}") from exc
            wait = delay
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if retry_after:
                try:
                    wait = max(wait, int(float(retry_after)))
                except ValueError:
                    pass
            print(
                f"{provider} API error {exc.code} (attempt {attempt}/{MAX_RETRIES}); "
                f"retrying in {wait}s",
                file=sys.stderr,
            )
            time.sleep(wait)
            delay = min(delay * 2, RETRY_MAX_DELAY_SECONDS)
        except urllib.error.URLError as exc:
            # Handle connection timeouts and other URL errors with retry logic
            is_timeout = "timed out" in str(exc).lower() or "connection" in str(exc).lower()
            if not is_timeout or attempt == MAX_RETRIES:
                raise SystemExit(f"{provider} connection error: {str(exc)[:1000]}") from exc
            wait = delay
            print(
                f"{provider} connection error (attempt {attempt}/{MAX_RETRIES}): {str(exc)[:100]}; "
                f"retrying in {wait}s",
                file=sys.stderr,
            )
            time.sleep(wait)
            delay = min(delay * 2, RETRY_MAX_DELAY_SECONDS)

    raise SystemExit(f"{provider} API request failed after {MAX_RETRIES} attempts")


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
    entries, pillar_state = choose_topics(args.count)
    if args.dry_run:
        print(json.dumps([e["topic"] for e in entries], indent=2))
        return 0
    skill = SKILL.read_text()
    day_dir = OUTPUT / today
    day_dir.mkdir(parents=True, exist_ok=True)

    succeeded = 0
    failed_pillars = []
    for i, entry in enumerate(entries):
        if i > 0:
            time.sleep(INTER_CALL_DELAY_SECONDS)
        topic = entry["topic"]
        try:
            text = call_model(prompt_for(topic, skill, today), args.model)
        except SystemExit as exc:
            print(f"WARNING: skipping {entry['pillar']} topic {topic['topic']!r}: {exc}", file=sys.stderr)
            failed_pillars.append(entry["pillar"])
            continue
        slug = slugify(topic["topic"])
        destination = day_dir / f"{slug}.md"
        destination.write_text(text.rstrip() + "\n")
        print(destination.relative_to(ROOT))
        pillar_state[entry["pillar"]] = {"next_index": (entry["index"] + 1) % entry["count"]}
        succeeded += 1

    STATE.write_text(json.dumps({"pillars": pillar_state, "last_run": today}, indent=2) + "\n")

    if failed_pillars:
        print(
            f"{len(failed_pillars)}/{len(entries)} pillar(s) failed and will retry next run: "
            f"{', '.join(failed_pillars)}",
            file=sys.stderr,
        )
    if succeeded == 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
