# STUDY IN MALTA SKILLS
## SEO + AEO + AIO + GEO Content Generation System
### Outreach Recruitment — outreachrecruitment.net

---

## What This Folder Does

This skill system generates fully optimized, publication-ready articles (+4000 words) for the **Study in Malta** topic cluster on Outreach Recruitment.

Each article is optimized for:

| Engine | Optimization |
|---|---|
| Google Search | Traditional SEO, E-E-A-T, Rich Results |
| Google AI Overviews | AEO, Featured Snippets, Structured Data |
| ChatGPT / Gemini / Claude | AIO, Entity SEO, Semantic Depth |
| Perplexity / Bing Copilot | GEO, Topical Authority, Citation Signals |
| Voice Search | Conversational Queries, Direct Answers |

---

## Folder Structure

```
STUDY IN MALTA SKILLS/
├── README.md                  ← You are here
├── SKILL-TEMPLATE.md          ← Full prompt template (reference)
├── generate-article.py        ← CLI tool to fill variables
└── generated/                 ← Output folder for saved prompts & articles
```

---

## How to Generate an Article

### Option A — Use the Python CLI

```bash
cd "STUDY IN MALTA SKILLS"
python3 generate-article.py
```

You will be asked for:
1. **Topic** — e.g. `How to Study in Malta as an International Student`
2. **Primary Keyword** — e.g. `study in Malta`
3. **Secondary Keywords** — e.g. `Malta student visa, universities in Malta, cost of living Malta`

The filled prompt is saved to `generated/` and ready to paste into Claude Code.

### Option B — Use Claude Code Directly

Open `SKILL-TEMPLATE.md`, fill in the three `[INSERT ...]` placeholders, and paste the full prompt into Claude Code.

---

## Study in Malta — Suggested Article Topics

| # | Topic | Primary Keyword |
|---|---|---|
| 1 | How to Study in Malta as an International Student | study in Malta |
| 2 | Malta Student Visa Guide 2026 | Malta student visa |
| 3 | Best Universities in Malta 2026 | universities in Malta |
| 4 | Cost of Living in Malta for Students | cost of living Malta students |
| 5 | Scholarships in Malta for International Students | scholarships Malta |
| 6 | Student Accommodation in Malta | student accommodation Malta |
| 7 | Working While Studying in Malta | work while studying Malta |
| 8 | English Language Courses in Malta | English courses Malta |
| 9 | Post-Study Work Opportunities in Malta | post-study work Malta |
| 10 | Malta Student Residence Permit Guide | Malta residence permit students |

---

## Content Cluster Map

```
[PILLAR] Study in Malta
├── Malta Student Visa
│   ├── Visa Requirements
│   ├── Visa Application Process
│   └── Student Residence Permit
├── Universities in Malta
│   ├── University of Malta
│   ├── MCAST
│   └── Private Colleges
├── Cost of Living in Malta
│   ├── Accommodation Costs
│   ├── Food & Transport
│   └── Tuition Fees
└── Work & Careers
    ├── Work While Studying
    ├── Student Jobs in Malta
    └── Post-Study Work
```

---

---

## Mandatory Links in Every Article

These 4 links are hardwired into the skill. Every generated article must include them.

| Link | URL | Min. Appearances | Anchor Text |
|---|---|---|---|
| Apply Now CTA | https://apply.outreachstudy.eu/ | 3× | "Apply Now", "Start Your Application", "Apply to Study in Malta" |
| Browse Programs | https://outreachrecruitment.net/study-in-malta#programs-table | 2× | "browse available programs", "view all study programs in Malta" |
| Study in Malta Guide | https://outreachrecruitment.net/study-in-malta | 2× | "Study in Malta", "complete guide to studying in Malta" |
| Free Webinar | https://outreachrecruitment.net/webinar-study-in-malta.html | 2× | "free webinar", "join our free Study in Malta webinar" |
| Malta Study Guide | https://outreachrecruitment.net/malta-study-guide/ | 2× | "Malta Study Guide", "full Malta study guide", "read our complete Malta study guide" |

Each link has a styled HTML CTA block defined in `SKILL-TEMPLATE.md` for use inside article HTML files.

---

## URL Routing Rules — Always Apply These

### Study in Malta articles → `/malta-study-guide/[slug]`

All articles about studying in Malta (visa, universities, costs, accommodation, scholarships, English courses, student life, post-study work) must:

- **Live at:** `outreachrecruitment.net/malta-study-guide/[slug]`
- **File saved to:** `malta-study-guide/[slug].html` (project root subfolder)
- **Canonical:** `<link rel="canonical" href="https://outreachrecruitment.net/malta-study-guide/[slug]" />`
- **Never use** `/blog/[slug]` or just `/[slug]` for Study in Malta content

| Correct ✅ | Wrong ❌ |
|---|---|
| `/malta-study-guide/student-accommodation-in-malta` | `/blog/student-accommodation-in-malta` |
| `/malta-study-guide/malta-student-visa-complete-guide` | `/student-accommodation-in-malta` |

---

### General blog articles → `/[slug]` (root, no `/blog/` prefix)

All general blog posts (career advice, recruitment tips, team structure, etc.) must:

- **Live at:** `outreachrecruitment.net/[slug]`
- **File saved to:** `[slug].html` (project root)
- **Canonical:** `<link rel="canonical" href="https://outreachrecruitment.net/[slug]" />`
- **Never use** `/blog/[slug]` — the `/blog/` prefix is deprecated and causes 404 errors

| Correct ✅ | Wrong ❌ |
|---|---|
| `/why-malta-is-becoming-europes-top-destination` | `/blog/why-malta-is-becoming-europes-top-destination` |
| `/how-decision-clarity-removes-friction` | `/blog/how-decision-clarity-removes-friction` |

---

## Contact / Business Details

- **Business:** Outreach Recruitment
- **Website:** https://outreachrecruitment.net/
- **Email:** info@outreachrecruitment.net
- **Location:** Malta, European Union
- **Author:** Sofyane Barakat
