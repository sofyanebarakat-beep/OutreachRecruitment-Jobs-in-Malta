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

## MANDATORY LINKS & CTAs (MUST APPEAR IN EVERY ARTICLE)

These four links are NON-NEGOTIABLE. Embed them naturally in the article body at the positions specified below. Do not skip any of them.

| Link | URL | Minimum Appearances | Placement |
|---|---|---|---|
| Apply Now CTA Button | https://apply.outreachstudy.eu/ | 3× | After Introduction / Mid-article / Before Conclusion |
| Browse Programs | https://outreachrecruitment.net/study-in-malta#programs-table | 2× | Programs section + Conclusion |
| Study in Malta Guide | https://outreachrecruitment.net/study-in-malta | 2× | Introduction + Internal Links section |
| Free Webinar | https://outreachrecruitment.net/webinar-study-in-malta.html | 2× | Mid-article + Conclusion |
| Malta Study Guide | https://outreachrecruitment.net/malta-study-guide/ | 2× | Mid-article callout + Internal Links section |

### Apply Now CTA Button HTML (use verbatim at each placement)

```html
<div class="cta-box" style="background:#1a56db;padding:24px;border-radius:8px;text-align:center;margin:32px 0;">
  <p style="color:#fff;font-size:18px;font-weight:600;margin-bottom:12px;">Ready to Study in Malta?</p>
  <a href="https://apply.outreachstudy.eu/" target="_blank" rel="noopener"
     style="background:#fff;color:#1a56db;padding:12px 28px;border-radius:6px;font-weight:700;text-decoration:none;display:inline-block;">
    Apply Now →
  </a>
</div>
```

### Free Webinar CTA HTML (use verbatim at each placement)

```html
<div class="webinar-box" style="background:#f0fdf4;border-left:4px solid #16a34a;padding:20px;border-radius:6px;margin:32px 0;">
  <p style="font-weight:700;margin-bottom:6px;">Free Study in Malta Webinar</p>
  <p style="margin-bottom:12px;">Join our free webinar and get expert answers about studying in Malta, visa requirements, and available programs.</p>
  <a href="https://outreachrecruitment.net/webinar-study-in-malta.html" target="_blank" rel="noopener"
     style="background:#16a34a;color:#fff;padding:10px 22px;border-radius:6px;font-weight:600;text-decoration:none;display:inline-block;">
    Register for the Free Webinar →
  </a>
</div>
```

### Programs CTA HTML (use verbatim at each placement)

```html
<div class="programs-box" style="background:#faf5ff;border:1px solid #a855f7;padding:20px;border-radius:6px;margin:32px 0;">
  <p style="font-weight:700;margin-bottom:6px;">Explore Study Programs in Malta</p>
  <p style="margin-bottom:12px;">Browse bachelor's, master's, and English language programs available to international students.</p>
  <a href="https://outreachrecruitment.net/study-in-malta#programs-table" target="_blank" rel="noopener"
     style="background:#a855f7;color:#fff;padding:10px 22px;border-radius:6px;font-weight:600;text-decoration:none;display:inline-block;">
    Browse All Programs →
  </a>
</div>
```

### Malta Study Guide CTA HTML (use verbatim at each placement)

```html
<div class="guide-box" style="background:#fff7ed;border-left:4px solid #ea580c;padding:20px;border-radius:6px;margin:32px 0;">
  <p style="font-weight:700;margin-bottom:6px;">Malta Study Guide — Everything You Need to Know</p>
  <p style="margin-bottom:12px;">Access our complete Malta Study Guide: visa steps, universities, costs, scholarships, accommodation, and more — all in one place.</p>
  <a href="https://outreachrecruitment.net/malta-study-guide/" target="_blank" rel="noopener"
     style="background:#ea580c;color:#fff;padding:10px 22px;border-radius:6px;font-weight:600;text-decoration:none;display:inline-block;">
    Read the Full Malta Study Guide →
  </a>
</div>
```

### Mandatory CTA Placement Checklist (verify before finishing)

- Apply Now CTA after Introduction ✓
- Apply Now CTA mid-article ✓
- Apply Now CTA before Conclusion ✓
- Browse Programs CTA in programs section ✓
- Browse Programs CTA in Conclusion ✓
- Study in Malta link in Introduction ✓
- Study in Malta link in Internal Links section ✓
- Free Webinar CTA mid-article ✓
- Free Webinar CTA in Conclusion ✓
- Malta Study Guide CTA mid-article ✓
- Malta Study Guide link in Internal Links section ✓

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
7. Full Article (4000+ words) — all 5 mandatory CTAs embedded at correct positions
8. Featured Snippet
9. FAQ Section
10. People Also Ask
11. Voice Search Questions
12. Entity Map
13. Internal Link Opportunities — include the 5 mandatory links with anchor texts
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
