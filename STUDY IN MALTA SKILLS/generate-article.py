#!/usr/bin/env python3
"""
STUDY IN MALTA — Article Generator
Outreach Recruitment | outreachrecruitment.net

Usage:
    python3 generate-article.py

You will be prompted for:
  - Topic
  - Primary Keyword
  - Secondary Keywords

The script outputs a filled prompt ready to paste into Claude Code.
"""

from datetime import date

SKILL_PROMPT = """
Your task is to create a fully optimized, publication-ready article (+4000 words) for **Outreach Recruitment** (https://outreachrecruitment.net/) that ranks in Google Search, Google AI Overviews, ChatGPT, Gemini, Claude, Perplexity, Bing Copilot, and other AI-powered search engines.

**Website:** https://outreachrecruitment.net/
**Topic:** {topic}
**Primary Keyword:** {primary_keyword}
**Secondary Keywords:** {secondary_keywords}
**Target Audience:** International students interested in studying in Malta.
**Language:** English

---

## TRADITIONAL SEO REQUIREMENTS

Perform comprehensive keyword research and include:

- Primary Keyword
- Secondary Keywords
- Long-Tail Keywords
- Semantic Keywords
- LSI Keywords
- Keyword Variations
- Search Intent Analysis

Generate:

- SEO Title (60 characters max)
- Meta Title
- Meta Description (155 characters max)
- URL Slug
- H1, H2, H3, H4

Create:

- Introduction
- Table of Contents
- Conclusion
- Internal Link Suggestions
- External Link Suggestions
- Anchor Text Suggestions
- Image Alt Text Suggestions
- Image File Name Suggestions

Ensure: natural keyword placement, high readability, fresh content, mobile-friendly formatting, short paragraphs, proper heading hierarchy.

---

## E-E-A-T OPTIMIZATION

Include:

- Author Name: Sofyane Barakat
- Author Bio & Credentials (Recruitment & International Education Specialist, Malta)
- Expert Review Section
- Real Experience Examples
- Trust Signals
- Contact Information Section
- References Section

---

## AEO (ANSWER ENGINE OPTIMIZATION)

Optimize for: Google Featured Snippets, Google AI Overviews, Voice Search

Create:
1. Direct Answer (40-60 words)
2. Definition Block
3. Step-by-Step Answer
4. Numbered Lists
5. Bullet Lists
6. Comparison Tables

Generate: Main Question, Related Questions, People Also Ask Questions, Conversational Queries, Voice Search Questions

Include: Short Answer, Medium Answer, Detailed Answer, Key Takeaways, Summary Box

---

## AIO (AI OPTIMIZATION)

Optimize for: ChatGPT, Gemini, Claude, Perplexity, Bing Copilot

Generate: Topic Summary, Content Summary, Key Facts, Key Statistics, Entity Recognition, Topic Relationships, Expert Insights, Citations, Source Attribution

Include: Definitions, Examples, Comparisons, FAQs, Tables, Lists

Ensure: Semantic relevance, Contextual depth, Entity coverage, AI retrieval optimization

---

## GEO (GENERATIVE ENGINE OPTIMIZATION)

Ensure complete topical authority. Include sections: What Is..., Why..., Benefits, Requirements, Application Process, Costs, Comparison, Pros and Cons, Common Mistakes, Best Practices, FAQs, Conclusion

Generate: Related Entities, Entity Relationships, Topic Map, Supporting Subtopics, Knowledge Graph Opportunities

Include: Statistics, Research Data, Industry Reports, Expert Quotes

---

## ENTITY SEO

Naturally include and explain: Malta, European Union, International Students, Student Visa, Higher Education, Bachelor's Degree, Master's Degree, English Language Courses, Tuition Fees, Accommodation, Work Permit, Student Employment, Post-Study Work, Visa Application, Student Residence Permit, Language Schools, Colleges in Malta, Universities in Malta

Include semantic relationships between entities.

---

## RICH RESULTS & SCHEMA

Generate production-ready JSON-LD for:
1. Organization Schema
2. WebSite Schema
3. SearchAction Schema
4. Article Schema
5. BlogPosting Schema
6. FAQPage Schema
7. BreadcrumbList Schema
8. Person Schema
9. EducationalOrganization Schema
10. Course Schema
11. VideoObject Schema
12. ImageObject Schema
13. Review Schema
14. Event Schema
15. LocalBusiness Schema

---

## LOCAL SEO

Business Details:
- Business Name: Outreach Recruitment
- Website: https://outreachrecruitment.net/
- Email: info@outreachrecruitment.net
- Location: Malta
- Focus: Study in Malta, Jobs in Malta

Generate: Local SEO recommendations, Google Business Profile recommendations, Local citation opportunities, Map optimization suggestions, Review acquisition strategy, Local FAQ section, Location-based content opportunities

---

## INTERNATIONAL SEO

Generate: hreflang recommendations, Country targeting strategy, Language targeting strategy, Subfolder recommendations, Localization opportunities, Regional content opportunities, Country-specific landing page suggestions, Multilingual SEO recommendations

---

## CONTENT CLUSTER SEO

Pillar Pages: Study in Malta | Malta Student Visa | Universities in Malta | Cost of Living in Malta

Cluster Pages: Scholarships in Malta | Accommodation in Malta | Work While Studying | Student Jobs in Malta | Post-Study Work Opportunities | Malta Visa Requirements | English Courses in Malta

Generate: Parent Pages, Child Pages, Hub Pages, Internal Linking Strategy, Topical Authority Map

---

## CTR OPTIMIZATION

Generate:
- 5 SEO Titles
- 5 Meta Descriptions
- 5 Featured Snippet Variations
- 5 FAQ Snippet Variations
- 5 AI Overview-Friendly Summaries

Optimize for: Higher CTR, Longer dwell time, Lower bounce rate, Better engagement

---

## OUTPUT FORMAT

Provide the final output in this exact order:

1. SEO Research
2. Search Intent
3. Keyword Strategy
4. SEO Title Options (5)
5. Meta Descriptions (5)
6. URL Slug
7. Full Article (4000+ words)
8. Featured Snippet
9. FAQ Section
10. People Also Ask
11. Voice Search Questions
12. Entity Map
13. Internal Link Opportunities
14. External Link Opportunities
15. Content Cluster Map
16. Local SEO Strategy
17. International SEO Strategy
18. Schema Markup (JSON-LD)
19. AI Optimization Recommendations
20. GEO Recommendations
21. CTR Optimization Recommendations

The article must be comprehensive, factually accurate, authoritative, and optimized for both traditional search engines and AI search engines.
"""

def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text

def main():
    print("\n" + "="*60)
    print("  STUDY IN MALTA — Article Generator")
    print("  Outreach Recruitment | outreachrecruitment.net")
    print("="*60 + "\n")

    topic = input("Topic: ").strip()
    primary_keyword = input("Primary Keyword: ").strip()
    secondary_keywords = input("Secondary Keywords (comma-separated): ").strip()

    filled = SKILL_PROMPT.format(
        topic=topic,
        primary_keyword=primary_keyword,
        secondary_keywords=secondary_keywords,
    )

    slug = slugify(primary_keyword)
    today = date.today().strftime("%Y-%m-%d")
    filename = f"generated/{slug}-{today}-PROMPT.txt"

    script_dir = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
    output_path = __import__('os').path.join(script_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(filled)

    print(f"\n✓ Prompt saved to: STUDY IN MALTA SKILLS/{filename}")
    print("\n--- NEXT STEP ---")
    print("Open Claude Code and paste the prompt above, or run:")
    print(f"  cat \"{output_path}\" | pbcopy  (copies to clipboard on Mac)")
    print()

if __name__ == "__main__":
    main()
