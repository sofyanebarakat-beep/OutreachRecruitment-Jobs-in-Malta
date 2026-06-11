# STUDY IN MALTA — SEO ARTICLE GENERATOR SKILL
## Outreach Recruitment | outreachrecruitment.net

---

## HOW TO USE THIS SKILL

Fill in the three variables below, then run the full prompt.

| Variable | Your Input |
|---|---|
| `[INSERT TOPIC]` | e.g. "How to Study in Malta as an International Student" |
| `[INSERT PRIMARY KEYWORD]` | e.g. "study in Malta" |
| `[INSERT SECONDARY KEYWORDS]` | e.g. "Malta student visa, universities in Malta, cost of living Malta" |

---

## FULL SKILL PROMPT

> Copy everything below this line and send it to Claude Code with your variables filled in.

---

Your task is to create a fully optimized, publication-ready article (+4000 words) for **Outreach Recruitment** (https://outreachrecruitment.net/) that ranks in Google Search, Google AI Overviews, ChatGPT, Gemini, Claude, Perplexity, Bing Copilot, and other AI-powered search engines.

**Website:** https://outreachrecruitment.net/
**Topic:** [INSERT TOPIC]
**Primary Keyword:** [INSERT PRIMARY KEYWORD]
**Secondary Keywords:** [INSERT SECONDARY KEYWORDS]
**Target Audience:** International students interested in studying in Malta.
**Language:** English

---

## MANDATORY LINKS & CTAs (MUST APPEAR IN EVERY ARTICLE)

These four links are mandatory. They must appear naturally inside the article body — not just in a footer block. Follow the exact placement rules below.

| Link | URL | Placement Rule |
|---|---|---|
| Apply Now CTA Button | https://apply.outreachstudy.eu/ | **3 times minimum** — after Introduction, mid-article, and before Conclusion. Use a styled CTA button/callout box. Anchor text: "Apply Now", "Start Your Application", "Apply to Study in Malta" |
| Browse Programs | https://outreachrecruitment.net/study-in-malta#programs-table | **2 times minimum** — in the section about programs/courses and in the Conclusion. Anchor text: "browse available programs", "view all study programs in Malta" |
| Study in Malta Guide | https://outreachrecruitment.net/study-in-malta | **2 times minimum** — in Introduction and in Internal Links section. Anchor text: "Study in Malta", "complete guide to studying in Malta" |
| Free Webinar | https://outreachrecruitment.net/webinar-study-in-malta.html | **2 times minimum** — mid-article and in Conclusion. Anchor text: "free webinar", "join our free Study in Malta webinar", "register for the webinar" |
| Malta Study Guide | https://outreachrecruitment.net/malta-study-guide/ | **2 times minimum** — mid-article (in a "further reading" or "related resources" callout) and in Internal Links section. Anchor text: "Malta Study Guide", "full Malta study guide", "read our complete Malta study guide" |

### CTA Button HTML Template (use in article body)

```html
<div class="cta-box" style="background:#1a56db;padding:24px;border-radius:8px;text-align:center;margin:32px 0;">
  <p style="color:#fff;font-size:18px;font-weight:600;margin-bottom:12px;">Ready to Study in Malta?</p>
  <a href="https://apply.outreachstudy.eu/" target="_blank" rel="noopener"
     style="background:#fff;color:#1a56db;padding:12px 28px;border-radius:6px;font-weight:700;text-decoration:none;display:inline-block;">
    Apply Now →
  </a>
</div>
```

### Webinar CTA HTML Template (use in article body)

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

### Programs CTA HTML Template (use in article body)

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

---

## COMPETITOR GAP ANALYSIS — RUN BEFORE WRITING

Before drafting the article, perform a competitor gap analysis for the primary keyword.

**Step 1 — Identify top competitors**

List the top 3–5 pages currently ranking for `[INSERT PRIMARY KEYWORD]` (use search intent + your knowledge of the SERP).

**Step 2 — Analyse what they cover**

For each competitor page, identify:

- Main sections / H2s covered
- Questions answered
- Data, stats, or tables included
- Entities mentioned
- CTA types used
- Word count estimate
- Content gaps (what they missed or covered poorly)

**Step 3 — Gap & depth matrix**

Generate a table like this and use it to plan the article:

| Topic / Section | Competitor 1 | Competitor 2 | Competitor 3 | Our Article |
|---|---|---|---|---|
| [Section name] | ✅ / ❌ / partial | ✅ / ❌ / partial | ✅ / ❌ / partial | **must include** |

**Rule:** Every gap column marked ❌ or "partial" across all competitors is a priority section for our article. Go deeper on those.

**Step 4 — Differentiation angle**

State in one sentence the unique angle this article will take that no competitor currently covers fully:

> *"This article will be the only one that covers [unique angle], including [specific data/section/perspective]."*

Output this full analysis as **Section 0** before the article begins.

---

## KEYWORD CANNIBALIZATION PREVENTION — CHECK BEFORE WRITING

Before generating any article, check the Published Articles Log (at the bottom of this file) to confirm no existing article already targets the same primary keyword.

### Step 1 — Cannibalization check

Search the Published Articles Log for:
- The exact primary keyword
- Close variants (singular/plural, word order swaps)
- Overlapping secondary keywords that another article already owns

### Step 2 — Decision table

| Situation | Action |
|---|---|
| No conflict found | Proceed with generation |
| Existing article targets same keyword, low traffic | **Merge** — expand the existing article instead of creating a new one |
| Existing article targets same keyword, good traffic | **Differentiate** — change the angle, target a longer-tail variant, or make the new article a sub-topic |
| Two cluster articles compete on the same term | **Internal canonicalisation** — add `rel="canonical"` on the weaker page pointing to the stronger |

### Step 3 — Differentiation rule

If a conflict exists and you proceed with a new article, state the differentiation clearly:

> *"Existing article: [title] targets '[keyword]' from angle [X]. This new article targets '[new keyword variant]' from angle [Y] — no cannibalization."*

### Step 4 — Cannibalization output (include in SEO Research section)

```
Cannibalization Check
Primary keyword: [keyword]
Conflict found: YES / NO
Conflicting article (if any): [title + slug]
Resolution: [proceed / merge / differentiate]
Differentiation angle: [explain if applicable]
```

---

## CAN WE RANK? KEYWORD DIFFICULTY ASSESSMENT — CHECK BEFORE WRITING

Before writing, decide whether Outreach Recruitment can realistically rank for `[INSERT PRIMARY KEYWORD]`. Do not create an article for an unwinnable keyword without first selecting a longer-tail entry point.

### Step 1 — Estimate keyword difficulty

Estimate KD using SERP evidence:

- Top 10 results dominated by government, university, or high-authority domains = high KD
- Top 10 results include blogs, agencies, forums, or thin pages = medium/low KD
- SERP has weak freshness, missing tables, poor mobile UX, or shallow answers = opportunity
- Search intent mismatch among top results = opportunity

### Step 2 — Compare against our authority

Use a practical authority estimate:

| SERP Pattern | Ranking Decision |
|---|---|
| Mostly `.gov`, `.edu`, large media, official universities | Target a longer-tail variant first |
| Mixed authority with agencies/blogs ranking | Proceed if our article is deeper and better structured |
| Thin pages, outdated data, weak schema, poor UX | Proceed aggressively |

### Step 3 — Fallback keyword rule

If the keyword is too competitive, automatically propose and use a longer-tail fallback variant before writing.

Examples:

| Too Competitive | Long-Tail Fallback |
|---|---|
| `study in Malta` | `how to study in Malta as an international student` |
| `Malta student visa` | `Malta student visa requirements for non-EU students` |
| `universities in Malta` | `best universities in Malta for international students` |

### Required output

```
Can We Rank?
Primary keyword: [keyword]
Estimated KD: Low / Medium / High
SERP authority level: Low / Medium / High
Our authority fit: Strong / Moderate / Weak
Decision: Proceed / Use fallback
Fallback keyword if needed: [long-tail keyword]
Reason: [1-2 sentences]
```

---

## ABOVE-THE-FOLD CONTENT MODULES

Every article must open with a compact, mobile-first answer stack. On a 375px mobile viewport, the H1, Position Zero paragraph, and first CTA must be visible without scrolling. Do not let a hero image push the H1 below the fold.

### Required order inside `<article><header>`

1. H1
2. Position Zero paragraph, 40-50 words
3. First CTA button or compact CTA link
4. Key Takeaways box
5. Trust bar
6. Author box
7. Table of Contents

### Key Takeaways box

Place this before the introduction. Use 4-5 bullets that answer the article's core questions in plain English.

```html
<aside class="key-takeaways" aria-labelledby="key-takeaways-heading" style="background:#f8fafc;border:1px solid #dbeafe;border-left:4px solid #1a56db;border-radius:8px;padding:18px;margin:24px 0;">
  <h2 id="key-takeaways-heading" style="font-size:20px;margin:0 0 10px;">Key Takeaways</h2>
  <ul style="margin:0;padding-left:20px;">
    <li>[Core answer 1]</li>
    <li>[Core answer 2]</li>
    <li>[Core answer 3]</li>
    <li>[Core answer 4]</li>
  </ul>
</aside>
```

### Trust bar / social proof strip

Place near the top after Key Takeaways. Use only true, approved claims.

```html
<aside class="trust-bar" aria-label="Outreach Recruitment trust signals" style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;background:#ecfdf5;border:1px solid #bbf7d0;border-radius:8px;padding:12px 16px;margin:20px 0;font-size:14px;color:#14532d;">
  <span>Helped 2,000+ students</span>
  <span aria-hidden="true">·</span>
  <span>EU-accredited programs</span>
  <span aria-hidden="true">·</span>
  <span>Free expert guidance</span>
</aside>
```

### Social sharing buttons — no JavaScript

Add after the intro and near the conclusion. Use native share intent URLs only.

```html
<nav class="share-links" aria-label="Share this article" style="display:flex;flex-wrap:wrap;gap:10px;margin:24px 0;">
  <a href="https://wa.me/?text=[ENCODED_TITLE]%20https://outreachrecruitment.net/[slug]" target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://outreachrecruitment.net/[slug]" target="_blank" rel="noopener noreferrer">Share on LinkedIn</a>
  <a href="mailto:?subject=[ENCODED_TITLE]&body=https://outreachrecruitment.net/[slug]">Share by Email</a>
</nav>
```

---

## DATA, STATISTICS & SOURCE STANDARDS

Every article must include at least 3 verifiable statistics with year, source name, and primary source link. Statistics should support the topic, not decorate the article.

### Rules

- Minimum 3 statistics per article
- Every statistic must include: year, figure, source name, and primary link
- No statistic may be older than 3 years unless you add a freshness note explaining why it remains useful
- Prefer official sources: Maltese government, Identity Malta, NSO Malta, Eurostat, EU institutions, universities, official school pages
- Do not cite a secondary blog for a stat when the primary report exists

### Data Sources section template

```html
<section aria-labelledby="data-sources">
  <h2 id="data-sources">Data Sources</h2>
  <ul>
    <li><a href="[primary-source-url]" target="_blank" rel="noopener noreferrer">[Source name]</a> — [statistic], [year]. [Freshness note if older than 3 years.]</li>
    <li><a href="[primary-source-url]" target="_blank" rel="noopener noreferrer">[Source name]</a> — [statistic], [year].</li>
    <li><a href="[primary-source-url]" target="_blank" rel="noopener noreferrer">[Source name]</a> — [statistic], [year].</li>
  </ul>
</section>
```

---

## RESPONSIVE TABLE, IMAGE & PRINT STANDARDS

All comparison tables and data tables must be mobile-safe, accessible, and tested at 375px width.

### Responsive table template

```html
<div class="table-scroll" role="region" aria-labelledby="[table-caption-id]" tabindex="0" style="overflow-x:auto;-webkit-overflow-scrolling:touch;margin:24px 0;">
  <table style="width:100%;border-collapse:collapse;min-width:640px;">
    <caption id="[table-caption-id]" style="text-align:left;font-weight:700;margin-bottom:8px;">[Descriptive table caption]</caption>
    <thead>
      <tr>
        <th scope="col">[Column 1]</th>
        <th scope="col">[Column 2]</th>
        <th scope="col">[Column 3]</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row">[Row label]</th>
        <td>[Value]</td>
        <td>[Value]</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Table rules

- Every table uses `<caption>`, `<thead>`, `<tbody>`, and `<th scope="col">`
- First cell in each row should use `<th scope="row">` where appropriate
- Every table is wrapped in `.table-scroll`
- Test at 375px mobile width: table must scroll horizontally, not break layout or create CLS

### Image captions

Every non-decorative image must use `<figure>` and `<figcaption>`.

```html
<figure>
  <img src="[image].webp" alt="[descriptive alt text]" width="[W]" height="[H]" loading="lazy" />
  <figcaption>[Descriptive caption with useful context, not keyword stuffing.]</figcaption>
</figure>
```

### Print stylesheet

Add a print CSS block to every article.

```html
<style>
@media print {
  nav, .cta-box, .webinar-box, .programs-box, .share-links, .site-header, .site-footer { display:none !important; }
  body { background:#fff !important; color:#111 !important; font-size:12pt; line-height:1.5; }
  a[href]::after { content:" (" attr(href) ")"; font-size:10pt; }
  article::after { content:"Source: https://outreachrecruitment.net/[slug]"; display:block; margin-top:24pt; font-size:10pt; }
}
</style>
```

---

## AUDIENCE SEGMENTATION COMPONENTS

For topics that differ between EU and non-EU students, such as visas, costs, work rights, and residence permits, add CSS-only tabs. No JavaScript.

```html
<section class="audience-tabs" aria-labelledby="audience-tabs-heading">
  <h2 id="audience-tabs-heading">What Applies to You?</h2>
  <input type="radio" id="tab-eu" name="audience-tabs" checked>
  <label for="tab-eu">EU Students</label>
  <input type="radio" id="tab-noneu" name="audience-tabs">
  <label for="tab-noneu">Non-EU Students</label>

  <div class="tab-panel eu-panel">
    <h3 id="eu-students">Rules for EU Students</h3>
    <p>[EU-specific answer.]</p>
  </div>
  <div class="tab-panel noneu-panel">
    <h3 id="non-eu-students">Rules for Non-EU Students</h3>
    <p>[Non-EU-specific answer.]</p>
  </div>
</section>
```

Required CSS:

```html
<style>
.audience-tabs input { position:absolute; opacity:0; }
.audience-tabs label { display:inline-block; padding:10px 14px; border:1px solid #d1d5db; cursor:pointer; }
.tab-panel { display:none; border:1px solid #d1d5db; padding:16px; }
#tab-eu:checked ~ .eu-panel, #tab-noneu:checked ~ .noneu-panel { display:block; }
</style>
```

---

## DESKTOP STICKY CLICKABLE TABLE OF CONTENTS

For articles over 2,000 words, use a CSS-only sticky ToC on desktop. On mobile, keep the ToC inline above the article content. Every ToC item must be clickable and must move the reader directly to the matching section through a real `#anchor` link.

### Layout rules

- Desktop: ToC stays sticky on the left while the reader scrolls the article
- Mobile/tablet: ToC appears inline before the first main section
- The ToC must sit outside the main article body column, not inside a content card
- Add one compact CTA banner directly under the sticky ToC
- Keep article text in a readable column: 680-760px max width
- Do not let the sticky ToC cover the header, footer, or article text
- Add `scroll-margin-top: 110px` to article headings so anchor jumps do not hide headings under the fixed nav

```html
<div class="article-layout">
  <aside class="toc-sidebar" aria-label="Article table of contents">
    <nav aria-label="Table of Contents">
      <h2 class="toc-title">Table of Contents</h2>
      <ol>
        <li><a href="#why-malta">Why Malta?</a></li>
        <li><a href="#student-visa">Student Visa Requirements</a></li>
        <li><a href="#cost-of-living">Cost of Living</a></li>
      </ol>
    </nav>

    <aside class="toc-cta" aria-label="Study in Malta consultation">
      <p><strong>Need help choosing a programme?</strong></p>
      <a href="https://apply.outreachstudy.eu/" aria-label="Apply for free study in Malta guidance">Apply Now</a>
    </aside>
  </aside>

  <div class="article-body">
    <!-- Main article sections go here -->
  </div>
</div>
```

```html
<style>
html { scroll-behavior:smooth; }
.article-body h2,
.article-body h3,
.article-body h4,
.article-body h5 { scroll-margin-top:110px; }

@media (min-width: 1024px) {
  .article-layout {
    display:grid;
    grid-template-columns:260px minmax(0, 740px);
    gap:40px;
    align-items:start;
    justify-content:center;
  }
  .toc-sidebar {
    position:sticky;
    top:96px;
    max-height:calc(100vh - 120px);
    overflow:auto;
  }
  .toc-sidebar nav {
    border:1px solid #e5e7eb;
    border-radius:8px;
    padding:16px;
    background:#fff;
  }
  .toc-title {
    font-size:16px;
    margin:0 0 12px;
  }
  .toc-sidebar a {
    display:block;
    padding:7px 0;
    color:#1a56db;
    text-decoration:none;
  }
  .toc-sidebar a:hover,
  .toc-sidebar a:focus {
    text-decoration:underline;
  }
  .toc-cta {
    margin-top:16px;
    border-radius:8px;
    padding:16px;
    background:#1a56db;
    color:#fff;
  }
  .toc-cta a {
    display:inline-block;
    margin-top:8px;
    background:#fff;
    color:#1a56db;
    padding:10px 14px;
    border-radius:6px;
    font-weight:700;
    text-decoration:none;
  }
}

@media (max-width: 1023px) {
  .article-layout { display:block; }
  .toc-sidebar {
    margin:24px 0;
  }
  .toc-sidebar nav {
    border:1px solid #e5e7eb;
    border-radius:8px;
    padding:16px;
    background:#fff;
  }
  .toc-cta {
    margin-top:12px;
    border-radius:8px;
    padding:16px;
    background:#1a56db;
    color:#fff;
  }
}
</style>
```

### Clickable ToC checklist

- [ ] Every ToC link uses `href="#section-id"`
- [ ] Every linked heading has the exact matching `id="section-id"`
- [ ] ToC click moves directly to the section in desktop and mobile
- [ ] Heading anchor position is visible after click because `scroll-margin-top` is set
- [ ] Sticky ToC stays on the left on desktop
- [ ] CTA banner appears under the ToC and links to `https://apply.outreachstudy.eu/`

---

## ARTICLE DESIGN & READING SPACING

Use spacing to make the article feel calm and easy to read. The reader should never feel that a heading, paragraph, CTA, or list is squeezed into the next element.

### Required spacing rules

- Add extra space between the title/header area and the first body text: `margin-top: 32px`
- Every major section should have `margin-top: 48px`
- Every heading should have `margin-bottom: 14px`
- Paragraphs should have `margin-bottom: 18px`
- CTA boxes should have `margin: 32px 0`
- Before the final conclusion text, add at least `margin-top: 40px`
- After the final paragraph, add `margin-bottom: 40px` before citations, related links, or footer content

```html
<style>
.article-body {
  max-width:740px;
  margin:32px auto 0;
  line-height:1.75;
}
.article-body section {
  margin-top:48px;
}
.article-body h2,
.article-body h3,
.article-body h4,
.article-body h5 {
  margin-top:0;
  margin-bottom:14px;
}
.article-body p {
  margin-bottom:18px;
}
.article-body .cta-box {
  margin:32px 0;
}
.article-body #conclusion {
  margin-top:40px;
}
.article-body #conclusion + p,
.article-body .final-paragraph {
  margin-bottom:40px;
}
</style>
```

---

## NEXT SKILLS TO ADD

Use these when improving the Study in Malta content system further.

### 1. SERP Screenshot Review Skill

Before writing or updating an article, search the target keyword and review the current top results. Record:

- Top 5 ranking page titles
- Content formats used: guide, list, calculator, video, FAQ, official page
- Missing angle Outreach can own
- SERP features visible: AI Overview, PAA, video, image pack, FAQ, local pack

Output:

```text
SERP Review
Keyword: [keyword]
Top formats: [formats]
SERP features: [features]
Best opportunity: [angle]
Risk: [why it may be hard]
Decision: [write/update/target long-tail first]
```

### 2. Visual Asset Brief Skill

Every article must include a short image brief for the hero image and 2-3 supporting visuals. This helps create consistent images from free tools.

```text
Image Brief
Hero image concept: [clear visual idea]
Style: realistic, bright, professional, Malta education theme
Must include: students, laptop/books, Malta street/coast/campus signal
Avoid: fake flags, unreadable text inside image, dark stock-photo look
Size: 1200x630 for OG/hero, 1600x900 for article image
Alt text: [descriptive alt]
Caption: [human-readable caption]
File name: [keyword-rich-file-name.webp]
```

### 3. Free Image Generation Workflow

Use this workflow when you need article images without paid tools.

Recommended free/low-cost tools:

- **Canva Free**: good for hero banners, diagrams, social carousels, and resizing
- **Microsoft Designer / Bing Image Creator**: good for AI-generated education visuals
- **Adobe Express Free**: good for quick branded social graphics
- **Pexels / Unsplash**: good for real photography, but avoid generic stock images
- **Squoosh.app**: compress and convert images to WebP
- **TinyPNG**: compress PNG/JPG before WebP conversion if needed

Required image process:

1. Generate or select the image.
2. Remove fake text/logos if AI generated.
3. Resize to the required dimensions.
4. Export as WebP.
5. Compress.
6. Add `width`, `height`, `alt`, `<figure>`, and `<figcaption>`.
7. Use `fetchpriority="high"` only for the hero image.

Prompt template:

```text
Create a realistic bright editorial photo for an article about studying in Malta in 2026. Show international students with laptops and notebooks in a Mediterranean campus or Valletta-inspired setting. Professional education website style, natural daylight, clean composition, no text, no logos, no fake documents, no flags as the main subject.
```

### 4. Conversion Path Skill

Every article should map CTAs to reader intent.

- Early CTA: soft action, such as free checklist or consultation
- Middle CTA: programme browsing or webinar
- Final CTA: apply now
- Sidebar CTA: sticky desktop support prompt

Output:

```text
CTA Map
Reader stage: awareness / comparison / ready to apply
Top CTA: [text + URL]
Middle CTA: [text + URL]
Final CTA: [text + URL]
Sidebar CTA: [text + URL]
```

### 5. Content Refresh Skill

Every article update must identify what changed and why.

Output:

```text
Refresh Notes
Updated sections: [list]
Old data removed: [list]
New sources added: [list]
Schema updated: yes/no
Revision history entry: [exact text]
Next review date: [YYYY-MM-DD]
```

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

Ensure:

- Natural keyword placement
- High readability
- Fresh content
- Mobile-friendly formatting
- Short paragraphs
- Proper heading hierarchy

### Reading Level Target

- Target **Flesch-Kincaid reading ease score: 60–70** (plain English, accessible to non-native speakers)
- Maximum sentence length: **25 words**
- Avoid passive voice — use active constructions
- No academic jargon without a plain-English definition immediately after
- Self-check: every paragraph should be understandable to a 16-year-old non-native English speaker

### Anchor Text Diversity Rule

- **No two internal links pointing to the same URL may use the same anchor text**
- Vary anchor text naturally: exact match, partial match, branded, and descriptive variations
- Example for `https://outreachrecruitment.net/study-in-malta`:

  | Use | Anchor Text |
  |---|---|
  | 1st mention | "Study in Malta" |
  | 2nd mention | "complete guide to studying in Malta" |
  | 3rd mention | "our Malta study resource" |

### Anchor Link Table of Contents Enforcement

Every H2 and H3 in the article must have a unique `id` attribute. The Table of Contents must link to these `id`s using `#anchor` hrefs. Without this, ToC links are broken — and HowTo schema step anchors won't resolve.

**Heading format:**
```html
<h2 id="malta-student-visa">How to Get a Malta Student Visa</h2>
```

**`id` naming rules:**
- Lowercase, hyphens only — no spaces, no underscores, no special characters
- Match the heading content closely (e.g. `id="cost-of-living"` for "Cost of Living in Malta")
- Must be unique within the page — no two headings may share the same `id`

**ToC entry format:**
```html
<nav aria-label="Table of Contents">
  <ol>
    <li><a href="#malta-student-visa">How to Get a Malta Student Visa</a></li>
    <li><a href="#cost-of-living">Cost of Living in Malta</a></li>
  </ol>
</nav>
```

**ToC enforcement checklist:**
- [ ] Every H2 and H3 has a unique `id`
- [ ] Every ToC entry links to a matching `#id` on the page
- [ ] `id` values match HowTo schema `step.url` fragment anchors
- [ ] No duplicate `id` values anywhere in the document

### Outbound Link Quality Rule

All external links must point **only** to authoritative sources:

- `.gov` — government portals (e.g. Identity Malta, Maltese government)
- `.edu` — educational institutions
- `.eu` — EU institutions (Eurostat, European Commission)
- Established news/research: Times of Malta, Malta Independent, MCAST official site, University of Malta
- Enforce `rel="noopener noreferrer"` on every external link
- **Never link to** low-DA blogs, content farms, or sites without clear authorship
- If a statistic is cited, link to its primary source — not a secondary blog that cited it

---

## PASSAGE RANKING OPTIMIZATION

Google indexes and ranks individual **passages** within a page, not just the page as a whole. Every H2 and H3 section must be able to rank independently.

### Rules — apply to every section

1. **Self-contained summary sentence** — the first sentence of every H2/H3 section must answer the section's question directly, as if the reader landed there with no context. No "As mentioned above…" or "In the previous section…"

2. **Question-answer structure** — phrase every H2/H3 heading as a question or a clear topic statement that implies a question. Example:

   | Weak heading ❌ | Strong heading ✅ |
   |---|---|
   | Student Visa | How to Get a Malta Student Visa |
   | Costs | How Much Does It Cost to Study in Malta? |
   | Accommodation | Where Do International Students Live in Malta? |

3. **40–60 word passage** — immediately after the heading, write a 40–60 word direct answer paragraph. This is the "passage snippet" Google can extract. Keep it clean, no inline links.

4. **No orphan paragraphs** — every paragraph must belong to a named section (H2/H3). No floating paragraphs between headings.

5. **Section length** — each H2 section should be 200–500 words. If a section grows beyond 500 words, break it into H3 subsections, each with their own self-contained summary sentence.

### Self-Contained Section Template

```
## [Question or Topic Heading]

[40–60 word direct answer paragraph — no links, no jargon. Reads as a standalone answer.]

[Expanded content, examples, data, tables, CTAs...]
```

---

## TOPICAL DEPTH SCORE

Before finalising the article, score every major H2 section against the **5Ws + H framework**. Any section scoring below 4/6 must be expanded before publishing.

### Scoring rubric

For each H2 section, check which of these six questions the section answers:

| Question | Passes if… |
|---|---|
| **Who** | Identifies who this applies to (e.g. "international students from non-EU countries") |
| **What** | Explains what the thing is clearly (e.g. "what a student residence permit is") |
| **When** | Gives a timeframe or deadline (e.g. "apply at least 3 months before course start") |
| **Where** | Names a specific place, office, or URL (e.g. "submit at Identity Malta, Valletta") |
| **Why** | Explains the reason or importance (e.g. "required to legally reside and study in Malta") |
| **How** | Gives actionable steps or a process (e.g. numbered steps or a process description) |

### Depth Score table (output per article)

| H2 Section | Who | What | When | Where | Why | How | Score /6 | Action |
|---|---|---|---|---|---|---|---|---|
| [Section name] | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | [n]/6 | Expand / OK |

**Rule:** Score 6/6 = publish-ready. Score 4–5/6 = acceptable. Score ≤ 3/6 = thin content — expand before publishing.

Output this table as part of the **SEO Research section**.

---

## SEMANTIC HTML5 STRUCTURE ENFORCEMENT

Every generated article must use proper HTML5 semantic tags — not `<div>` wrappers for everything. Google's crawler uses semantic structure to understand the document hierarchy.

### Mandatory page skeleton

Every article HTML file must follow this skeleton exactly:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- all meta, schema, styles -->
</head>
<body>

  <!-- Skip to content (accessibility) -->
  <a href="#main-content" class="skip-link" style="position:absolute;top:-40px;left:0;background:#1a56db;color:#fff;padding:8px 16px;z-index:9999;border-radius:0 0 4px 0;text-decoration:none;"
     onfocus="this.style.top='0'">Skip to main content</a>

  <header role="banner">
    <!-- site nav, logo -->
  </header>

  <nav aria-label="Breadcrumb">
    <!-- breadcrumb -->
  </nav>

  <main id="main-content" role="main">
    <article itemscope itemtype="https://schema.org/Article">

      <header>
        <!-- H1, author box, byline, Position Zero block, ToC -->
      </header>

      <section aria-label="Introduction">
        <!-- introduction -->
      </section>

      <!-- Repeat for each H2 topic -->
      <section aria-labelledby="[section-id]">
        <h2 id="[section-id]">[Section Heading]</h2>
        <!-- section content -->
      </section>

      <aside aria-label="Related resources">
        <!-- CTAs, related articles, webinar box -->
      </aside>

      <section aria-label="FAQ">
        <!-- FAQ accordion -->
      </section>

      <footer>
        <!-- cite block, back to blog, author box repeat -->
      </footer>

    </article>
  </main>

  <footer role="contentinfo">
    <!-- site footer -->
  </footer>

</body>
</html>
```

### Rules

- Every `<section>` must have either `aria-label` or `aria-labelledby` pointing to its heading `id`
- `<h1>` appears exactly once per page — inside `<article><header>`
- `<aside>` is used for CTAs, related articles, and callout boxes — not `<div>`
- `<nav>` is used for breadcrumb and ToC — not `<div>`
- `<footer>` inside `<article>` holds the cite block and author repeat
- No `<table>` used for layout — only for actual data

---

## E-E-A-T OPTIMIZATION

Include:

- Author Name: Outreach Recruitment Agency
- Author Bio
- Author Credentials (Recruitment & International Education Specialist, Malta)
- Expert Review Section
- Real Experience Examples
- Trust Signals
- Contact Information Section
- References Section

Generate recommendations for:

- About Page
- Privacy Policy
- Terms and Conditions

### Author Authority Signals (required in every article)

Every article must link the author name to the Outreach Recruitment team page and include social proof:

```html
<div class="author-box" style="display:flex;align-items:flex-start;gap:16px;background:#f9fafb;border-radius:8px;padding:20px;margin:32px 0;">
  <div>
    <p style="font-weight:700;margin-bottom:4px;">
      <a href="https://outreachrecruitment.net/about" rel="author" style="color:#111827;text-decoration:none;">Outreach Recruitment Agency</a>
    </p>
    <p style="font-size:13px;color:#6b7280;margin-bottom:8px;">Recruitment & International Education Specialist, Malta</p>
    <p style="font-size:14px;color:#374151;margin-bottom:8px;">[2–3 sentence author bio linking experience to this specific topic]</p>
    <p style="font-size:13px;">
      <a href="https://www.linkedin.com/company/outreach-recruitment" target="_blank" rel="noopener noreferrer" style="color:#1a56db;">LinkedIn</a>
      &nbsp;·&nbsp;
      <a href="https://outreachrecruitment.net/about" style="color:#1a56db;">About Outreach Recruitment</a>
    </p>
  </div>
</div>
```

**Author authority checklist:**
- [ ] Author name links to `/about` page with `rel="author"`
- [ ] LinkedIn company page linked
- [ ] Author bio is specific to the article topic (not generic)
- [ ] Author schema uses `Organization` for Outreach Recruitment Agency and includes `sameAs` with LinkedIn URL
- [ ] Author box appears above the article introduction

---

## STUDENT TESTIMONIALS / SOCIAL PROOF

Include a testimonials block in every article. Student quotes strengthen E-E-A-T, increase dwell time, improve conversion, and can trigger `Review` rich results in SERP.

### Placement
Insert after the first major content section (after the first H2 body section) and again near the Conclusion.

### Testimonial Block HTML

```html
<div class="testimonials" style="margin:40px 0;" aria-label="Student testimonials">
  <h3 style="font-size:20px;font-weight:700;margin-bottom:20px;">What Students Say About Studying in Malta</h3>

  <div style="display:grid;gap:20px;">

    <blockquote style="background:#f9fafb;border-left:4px solid #1a56db;padding:20px;border-radius:0 8px 8px 0;margin:0;"
                itemscope itemtype="https://schema.org/Review">
      <div itemprop="reviewRating" itemscope itemtype="https://schema.org/Rating">
        <meta itemprop="ratingValue" content="5" />
        <meta itemprop="bestRating" content="5" />
        <span style="color:#f59e0b;font-size:16px;" aria-label="5 out of 5 stars">★★★★★</span>
      </div>
      <p style="font-style:italic;color:#374151;margin:8px 0 12px;" itemprop="reviewBody">"[Student quote — 2–3 sentences. Specific, authentic, topic-relevant.]"</p>
      <footer style="font-size:13px;color:#6b7280;">
        — <span itemprop="author" itemscope itemtype="https://schema.org/Person">
             <span itemprop="name">[Student Name]</span>
           </span>,
        <span itemprop="itemReviewed" itemscope itemtype="https://schema.org/EducationalOrganization">
          <span itemprop="name">[University/Program name]</span>
        </span>, [Year]
      </footer>
    </blockquote>

    <blockquote style="background:#f9fafb;border-left:4px solid #16a34a;padding:20px;border-radius:0 8px 8px 0;margin:0;"
                itemscope itemtype="https://schema.org/Review">
      <div itemprop="reviewRating" itemscope itemtype="https://schema.org/Rating">
        <meta itemprop="ratingValue" content="5" />
        <meta itemprop="bestRating" content="5" />
        <span style="color:#f59e0b;font-size:16px;" aria-label="5 out of 5 stars">★★★★★</span>
      </div>
      <p style="font-style:italic;color:#374151;margin:8px 0 12px;" itemprop="reviewBody">"[Second student quote — different country of origin, different program if possible.]"</p>
      <footer style="font-size:13px;color:#6b7280;">
        — <span itemprop="author" itemscope itemtype="https://schema.org/Person">
             <span itemprop="name">[Student Name]</span>
           </span>, [Country], [Year]
      </footer>
    </blockquote>

  </div>
</div>
```

### Rules for testimonial content

- Minimum 2 testimonials per article, maximum 4
- Each testimonial must be specific to the article topic (visa article → visa experience quotes; accommodation article → housing quotes)
- Include student name, country of origin, program/university, and year
- If real testimonials are not available, write representative quotes that reflect common student experiences — do not fabricate specific identities
- Vary countries of origin across testimonials to reflect international diversity

### `AggregateRating` schema (add to Article schema when testimonials are present)

```json
"aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": "4.9",
  "reviewCount": "47",
  "bestRating": "5",
  "worstRating": "1"
}
```

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

Generate:

- Main Question
- Related Questions
- People Also Ask Questions
- Conversational Queries
- Voice Search Questions

Include:

- Short Answer
- Medium Answer
- Detailed Answer
- Key Takeaways
- Summary Box

### Zero-Click / Position Zero Enforcement

For **every article**, generate a mandatory **Position Zero Block** — a single paragraph placed immediately after the H1, before the Table of Contents. This is Google's #1 candidate for a featured snippet.

**Rules:**
- Exactly **40–50 words** — no more, no less
- Answer the primary keyword question directly in the first sentence
- No links, no bold, no lists — plain prose only
- Use the exact primary keyword phrase naturally within the first 10 words
- Written in third person or instructional tone (not "I" or "we")

**Template:**

```
[PRIMARY KEYWORD — capitalised as a topic, not a heading]

[40–50 word direct answer paragraph. First sentence answers the core question. Second sentence adds the most important qualifying detail. No filler, no marketing language.]
```

**Example** (primary keyword: "study in Malta"):

> Studying in Malta gives international students access to EU-recognised degrees taught in English at some of the Mediterranean's most affordable institutions. Students can enrol in bachelor's, master's, or language programmes and apply for a student residence permit valid for the duration of their course.

**Checklist:**
- [ ] Position Zero Block placed after H1, before Table of Contents
- [ ] Word count: 40–50 words
- [ ] Contains primary keyword in first 10 words
- [ ] No links or formatting — plain prose only
- [ ] Reads as a standalone answer with no prior context needed

---

## FAQ ACCORDION — CSS-ONLY TEMPLATE

Replace all flat-HTML FAQs with this interactive accordion built using native `<details>` + `<summary>` HTML tags. No JavaScript — zero INP impact, CWV-safe, and works on all browsers.

### FAQ Accordion HTML

```html
<section aria-label="Frequently Asked Questions" id="faq">
  <h2 id="faq-heading">Frequently Asked Questions</h2>

  <style>
    .faq-item { border-bottom: 1px solid #e5e7eb; }
    .faq-item summary {
      cursor: pointer;
      padding: 16px 0;
      font-weight: 600;
      font-size: 16px;
      color: #111827;
      list-style: none;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .faq-item summary::-webkit-details-marker { display: none; }
    .faq-item summary::after {
      content: "+";
      font-size: 20px;
      color: #1a56db;
      transition: transform 0.2s;
    }
    .faq-item[open] summary::after {
      content: "−";
    }
    .faq-item .faq-answer {
      padding: 0 0 16px;
      color: #374151;
      line-height: 1.7;
    }
  </style>

  <div class="faq-list">

    <details class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
      <summary itemprop="name">[FAQ Question 1]</summary>
      <div class="faq-answer" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
        <p itemprop="text">[Answer — 2–4 sentences. Plain language. No keyword stuffing.]</p>
      </div>
    </details>

    <details class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
      <summary itemprop="name">[FAQ Question 2]</summary>
      <div class="faq-answer" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
        <p itemprop="text">[Answer]</p>
      </div>
    </details>

    <!-- Repeat for each FAQ item — minimum 5, maximum 10 -->

  </div>
</section>
```

### Rules

- Minimum **5 FAQ items**, maximum **10** per article
- FAQ questions must match People Also Ask questions generated in AEO section
- Each `<details>` block includes microdata `itemscope` attributes — this feeds the FAQPage schema without a separate JSON-LD block
- FAQ section must have `id="faq"` for ToC anchor linking
- Place FAQ section immediately before the Conclusion section

### FAQPage JSON-LD (still required — microdata alone is not enough for rich results)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question 1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer 1]"
      }
    },
    {
      "@type": "Question",
      "name": "[Question 2]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer 2]"
      }
    }
  ]
}
```

---

## AIO (AI OPTIMIZATION)

Optimize for: ChatGPT, Gemini, Claude, Perplexity, Bing Copilot

Generate:

- Topic Summary
- Content Summary
- Key Facts
- Key Statistics
- Entity Recognition
- Topic Relationships
- Expert Insights
- Citations
- Source Attribution

Include:

- Definitions
- Examples
- Comparisons
- FAQs
- Tables
- Lists

Ensure:

- Semantic relevance
- Contextual depth
- Entity coverage
- AI retrieval optimization

---

## GEO (GENERATIVE ENGINE OPTIMIZATION)

Ensure complete topical authority.

Include:

- What Is...
- Why...
- Benefits
- Requirements
- Application Process
- Costs
- Comparison
- Pros and Cons
- Common Mistakes
- Best Practices
- FAQs
- Conclusion

Generate:

- Related Entities
- Entity Relationships
- Topic Map
- Supporting Subtopics
- Knowledge Graph Opportunities

Include:

- Statistics
- Research Data
- Industry Reports
- Expert Quotes

---

## ENTITY SEO

Naturally include and explain these entities:

Malta, European Union, International Students, Student Visa, Higher Education, Bachelor's Degree, Master's Degree, English Language Courses, Tuition Fees, Accommodation, Work Permit, Student Employment, Post-Study Work, Visa Application, Student Residence Permit, Language Schools, Colleges in Malta, Universities in Malta

Include semantic relationships between entities.

---

## NLP / SEMANTIC DENSITY SELF-CHECK

After drafting the article, run a semantic density self-check before finalising. This simulates what tools like Surfer SEO, Clearscope, and MarketMuse grade automatically.

**Step 1 — Generate the top 10 NLP terms**

Based on the primary keyword, list the 10 most semantically related terms that Google's NLP model expects to find in a topically authoritative article. Examples for "study in Malta":

| # | Expected NLP Term | Present in article? | Natural frequency |
|---|---|---|---|
| 1 | student visa Malta | ✅ / ❌ | e.g. 4× |
| 2 | residence permit | ✅ / ❌ | |
| 3 | tuition fees | ✅ / ❌ | |
| 4 | University of Malta | ✅ / ❌ | |
| 5 | MCAST | ✅ / ❌ | |
| 6 | English-taught programmes | ✅ / ❌ | |
| 7 | Schengen area | ✅ / ❌ | |
| 8 | cost of living | ✅ / ❌ | |
| 9 | scholarship | ✅ / ❌ | |
| 10 | international student | ✅ / ❌ | |

**Step 2 — Fix missing terms**

Any term marked ❌ must be added naturally to the article before publishing. Do not stuff — weave in contextually.

**Step 3 — Keyword frequency check**

| Keyword | Target frequency | Actual |
|---|---|---|
| Primary keyword | 1% of total words (e.g. 40× in 4000 words) | |
| Top 3 secondary keywords | 0.3–0.5% each | |

Output this self-check table as part of the **SEO Research section** in the final output.

---

## RICH RESULTS & SCHEMA

Generate JSON-LD schema for:

1. Organization Schema
2. WebSite Schema
3. SearchAction Schema
4. Article Schema
5. BlogPosting Schema
6. FAQPage Schema
7. BreadcrumbList Schema
8. Author Organization Schema
9. EducationalOrganization Schema
10. Course Schema
11. VideoObject Schema
12. ImageObject Schema
13. Review Schema
14. Event Schema
15. LocalBusiness Schema

Provide production-ready JSON-LD.

### Structured data validation — mandatory before delivery

Before marking an article complete, validate every JSON-LD block.

Required checks:

1. Parse every `<script type="application/ld+json">` block as valid JSON.
2. Validate with Schema.org validator: `https://validator.schema.org/`
3. Validate with Google's Rich Results Test: `https://search.google.com/test/rich-results`
4. Fix all errors before delivery.
5. Warnings may remain only if the missing property is genuinely unavailable or optional; explain the reason.

Output this validation table:

| Schema Type | JSON Parse | Schema.org Validator | Rich Results Test | Action |
|---|---|---|---|---|
| Article | Pass / Fail | Pass / Fail | Pass / Warning / Fail | [fix / ok / explain warning] |
| FAQPage | Pass / Fail | Pass / Fail | Pass / Warning / Fail | [fix / ok / explain warning] |
| BreadcrumbList | Pass / Fail | Pass / Fail | Pass / Warning / Fail | [fix / ok / explain warning] |

### HowTo Schema (conditional — use when article contains step-by-step process)

If the article covers any step-by-step process (e.g. applying for a student visa, enrolling in a university, finding accommodation), generate a `HowTo` schema in addition to the standard schemas. This unlocks a distinct SERP rich result showing steps directly in Google.

**Trigger conditions:** apply when the article contains sections like:
- "How to apply for…"
- "Step-by-step guide to…"
- "How to enrol in…"
- "How to get a Malta student visa"

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "[How-to title — e.g. How to Apply for a Malta Student Visa]",
  "description": "[1–2 sentence description of the process]",
  "totalTime": "PT[X]D",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "EUR",
    "value": "[cost if applicable, else omit]"
  },
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "[Step 1 name]",
      "text": "[Clear instruction for step 1 — 1–2 sentences]",
      "url": "https://outreachrecruitment.net/[slug]#step-1"
    },
    {
      "@type": "HowToStep",
      "position": 2,
      "name": "[Step 2 name]",
      "text": "[Clear instruction for step 2]",
      "url": "https://outreachrecruitment.net/[slug]#step-2"
    }
  ]
}
```

**Rules:**
- Each step must have an `id` anchor in the HTML (`id="step-1"`, `id="step-2"`, etc.)
- Minimum 3 steps, maximum 10 steps
- Step names must match the H3 headings in the article exactly
- `totalTime` in ISO 8601 duration format (e.g. `PT30M` = 30 minutes, `P7D` = 7 days)

---

## LOCAL SEO

**Business Details (from contact-us page):**

- Business Name: Outreach Recruitment
- Website: https://outreachrecruitment.net/
- Email: info@outreachrecruitment.net
- Location: Malta
- Focus: Study in Malta, Jobs in Malta

Generate:

- Local SEO recommendations
- Google Business Profile recommendations
- Local citation opportunities
- Map optimization suggestions
- Review acquisition strategy
- Local FAQ section
- Location-based content opportunities

---

## INTERNATIONAL SEO

Generate:

- hreflang recommendations
- Country targeting strategy
- Language targeting strategy
- Subfolder recommendations
- Localization opportunities
- Regional content opportunities
- Country-specific landing page suggestions
- Multilingual SEO recommendations

---

## PROGRAMMATIC SEO — COUNTRY-SPECIFIC VARIANTS

For high-traffic source countries, generate country-specific landing page variants targeting "Study in Malta from [Country]" queries. Each page has a unique angle — do not duplicate the main article.

### Priority source countries

| Country | Primary keyword | Unique angle |
|---|---|---|
| India | Study in Malta from India | Student visa from India, direct flights, Indian community in Malta, IELTS requirements |
| Nigeria | Study in Malta from Nigeria | Nigerian passport visa process, scholarship options, Schengen entry from Nigeria |
| Libya | Study in Malta from Libya | Proximity advantage, Arabic-speaking support, ferry routes, Libyan student community |
| Egypt | Study in Malta from Egypt | EU access from Egypt, Arabic language support, cost comparison vs. Egypt |
| Tunisia | Study in Malta from Tunisia | Schengen visa, French-speaking support, North Africa proximity |
| Italy | Study in Malta from Italy | EU freedom of movement, no visa required, bilingual environment |

### Country page URL pattern

```
https://outreachrecruitment.net/study-in-malta-from-[country]
```

Examples:
```
https://outreachrecruitment.net/study-in-malta-from-india
https://outreachrecruitment.net/study-in-malta-from-nigeria
https://outreachrecruitment.net/study-in-malta-from-libya
```

### Country page content requirements

Each country variant must include these unique sections (not copy-pasted from the main article):
1. Visa process specific to that country's passport holders
2. Flight routes / travel options from that country to Malta
3. Cost comparison (Malta tuition vs. studying in that country)
4. Community and support for students from that country in Malta
5. Country-specific scholarship opportunities
6. Frequently asked questions from students in that country

### `hreflang` for country variants

```html
<link rel="alternate" hreflang="en" href="https://outreachrecruitment.net/[slug]" />
<link rel="alternate" hreflang="en-in" href="https://outreachrecruitment.net/study-in-malta-from-india" />
<link rel="alternate" hreflang="en-ng" href="https://outreachrecruitment.net/study-in-malta-from-nigeria" />
```

---

## MULTILINGUAL INTRO SNIPPET

Include a short multilingual intro block near the bottom of every article (before the Cite section). This captures Arabic and French-language queries in Google AI Overviews and voice search without needing separate translated pages.

### Arabic intro block (80–100 words)

```html
<div lang="ar" dir="rtl" style="background:#fefce8;border-left:4px solid #ca8a04;padding:20px;border-radius:6px;margin:32px 0;font-family:Arial,sans-serif;font-size:15px;line-height:1.8;color:#374151;">
  <p style="font-weight:700;margin-bottom:8px;">للطلاب الناطقين بالعربية</p>
  <p style="margin-bottom:0;">[80–100 word Arabic summary of the article's core topic. Written for Arabic-speaking prospective students. Include: what the article covers, key benefit, and a call to contact Outreach Recruitment. Natural Arabic — not a machine translation.]</p>
</div>
```

### French intro block (80–100 words)

```html
<div lang="fr" style="background:#f0f9ff;border-left:4px solid #0284c7;padding:20px;border-radius:6px;margin:32px 0;font-size:15px;line-height:1.8;color:#374151;">
  <p style="font-weight:700;margin-bottom:8px;">Pour les étudiants francophones</p>
  <p style="margin-bottom:0;">[80–100 word French summary. Same structure: what the article covers, key benefit, CTA to contact Outreach Recruitment. Natural French — not a machine translation.]</p>
</div>
```

### Rules

- Place both blocks together, in order: Arabic first, then French
- Arabic block must use `dir="rtl"` for correct right-to-left rendering
- Both blocks must be original summaries — not translations of the Position Zero paragraph
- Both blocks must mention "Outreach Recruitment" by name and include an implicit or explicit CTA

---

## CONTENT CLUSTER SEO

**Pillar Pages:**

- Study in Malta
- Malta Student Visa
- Universities in Malta
- Cost of Living in Malta

**Cluster Pages:**

- Scholarships in Malta
- Accommodation in Malta
- Work While Studying
- Student Jobs in Malta
- Post-Study Work Opportunities
- Malta Visa Requirements
- English Courses in Malta

Generate:

- Parent Pages
- Child Pages
- Hub Pages
- Internal Linking Strategy
- Topical Authority Map

---

## INTERNAL LINK SILO ENFORCEMENT

Every article must follow a strict silo structure to concentrate PageRank to the right pages and prevent equity from leaking to unrelated content.

### Silo hierarchy

```
Homepage (outreachrecruitment.net/)
    └── Pillar Page (/study-in-malta)
            ├── Cluster Article 1 (/student-accommodation-in-malta)
            ├── Cluster Article 2 (/malta-student-visa-complete-guide)
            ├── Cluster Article 3 (/cost-of-living-in-malta-as-a-student)
            └── ... (all Study in Malta cluster articles)
```

### Per-article linking rules

| Link type | Rule | Minimum |
|---|---|---|
| **Up to pillar** | Every article must link to `/study-in-malta` | 1× (Introduction) |
| **Up to blog index** | Every article must link to `/malta-study-guide` | 1× (back link + related section) |
| **Down to cluster** | Every article must link to at least 2 other cluster articles | 2× minimum |
| **Across cluster** | Cross-links to topically related cluster articles are encouraged | 1–3× |
| **Down to homepage** | Logo/nav link only — no in-body homepage links | 0× in body |

### Click depth rule

No article may be more than **2 clicks from the homepage**:

- Homepage → `/malta-study-guide` → Article = **2 clicks** ✅
- Homepage → `/study-in-malta` → Article = **2 clicks** ✅
- Homepage → some unlinked page → Article = **3 clicks** ❌ — fix by adding to `/malta-study-guide` index

### Silo map output (generate per article)

```
Internal Link Silo Map — [Article Title]
├── Links UP:
│   ├── /study-in-malta (pillar) — anchor: "[anchor text]"
│   └── /malta-study-guide (blog index) — anchor: "[anchor text]"
├── Links DOWN / ACROSS:
│   ├── /[cluster-slug-1] — anchor: "[anchor text]"
│   └── /[cluster-slug-2] — anchor: "[anchor text]"
└── Click depth from homepage: [1 / 2] clicks ✅
```

Output this silo map as part of the **Internal Link Opportunities section**.

---

## CORE WEB VITALS COMPLIANCE

Core Web Vitals are a direct Google ranking factor. Every generated article must follow these rules in its HTML output.

### LCP (Largest Contentful Paint) — target < 2.5s

- [ ] No render-blocking `<script>` tags in `<head>` — move all JS to end of `<body>` or use `defer`/`async`
- [ ] Hero image (if any) must use `<link rel="preload" as="image" href="...">` in `<head>`
- [ ] Critical CSS only in `<style>` in `<head>` — all non-critical CSS loaded async or inline in body
- [ ] No Google Fonts loaded synchronously — use `font-display: swap`

### CLS (Cumulative Layout Shift) — target < 0.1

- [ ] Every `<img>` tag must include explicit `width` and `height` attributes — no exceptions
- [ ] Every embedded iframe (video, map) must have a fixed aspect-ratio wrapper
- [ ] No dynamically injected content above the fold (ads, banners) without reserved space

### INP / FID (Interaction to Next Paint) — target < 200ms

- [ ] No heavy inline JavaScript in the article body
- [ ] All third-party scripts (analytics, chat widgets) loaded with `async` or deferred

### Image rules (apply to every `<img>`)

```html
<!-- Above the fold (hero image) -->
<img src="[slug]-hero.webp" alt="[descriptive alt text]"
     width="1200" height="630" fetchpriority="high" />

<!-- Below the fold (all other images) -->
<img src="[image-name].webp" alt="[descriptive alt text]"
     width="[W]" height="[H]" loading="lazy" />
```

- Use **WebP format** for all images
- Provide `srcset` for responsive images when possible
- Alt text must describe the image content — not the keyword stuffed

### CWV Compliance Checklist (output with every article)

- [ ] No render-blocking scripts in `<head>`
- [ ] All `<img>` tags have `width` and `height`
- [ ] Below-fold images use `loading="lazy"`
- [ ] Hero image uses `fetchpriority="high"`
- [ ] All images in WebP format
- [ ] No synchronous Google Fonts
- [ ] iframes have aspect-ratio wrappers

---

## ACCESSIBILITY (A11Y) RULES

Google's quality raters score accessibility as part of page quality. These rules also expand your reach to users with screen readers and assistive technology.

### Required on every article

```html
<!-- 1. Skip to content link (first element in <body>) -->
<a href="#main-content" class="skip-link"
   style="position:absolute;top:-40px;left:0;background:#1a56db;color:#fff;padding:8px 16px;z-index:9999;border-radius:0 0 4px 0;text-decoration:none;font-weight:600;"
   onfocus="this.style.top='0'" onblur="this.style.top='-40px'">
  Skip to main content
</a>

<!-- 2. Main landmark -->
<main id="main-content" role="main">

<!-- 3. ARIA labels on all CTA buttons -->
<a href="https://apply.outreachstudy.eu/"
   aria-label="Apply to study in Malta — opens application form">Apply Now →</a>

<!-- 4. ARIA labels on all icon/image links -->
<a href="..." aria-label="[Descriptive label — not just 'click here']">...</a>
```

### Accessibility checklist (verify per article)

| Rule | Requirement |
|---|---|
| Skip link | First focusable element — links to `#main-content` |
| `role="main"` | On `<main>` element wrapping article body |
| ARIA labels | All CTA buttons have descriptive `aria-label` |
| Color contrast | Body text: minimum 4.5:1 contrast ratio against background |
| Link contrast | All links: minimum 3:1 contrast against surrounding text |
| Image alt text | Every `<img>` has meaningful `alt` (empty `alt=""` for decorative only) |
| Heading order | `<h1>` → `<h2>` → `<h3>` — no skipped levels |
| Form labels | Any email/input field has an associated `<label>` |
| Language attr | `<html lang="en">` set on every page |
| Focus visible | No `outline: none` on interactive elements |

### Color contrast reference (use these approved values)

| Use | Background | Text | Ratio |
|---|---|---|---|
| Body text | `#ffffff` | `#111827` | 16.8:1 ✅ |
| Secondary text | `#ffffff` | `#374151` | 8.6:1 ✅ |
| Muted text | `#ffffff` | `#6b7280` | 4.6:1 ✅ (just passes) |
| Blue CTA button | `#1a56db` | `#ffffff` | 5.1:1 ✅ |
| Green CTA button | `#16a34a` | `#ffffff` | 4.6:1 ✅ |

---

## CONTENT FRESHNESS PROTOCOL

Google rewards content that stays current. Every article must include freshness signals and a maintenance schedule.

### Update Schedule field (add to every article header comment)

```html
<!--
  CONTENT FRESHNESS
  Published:        [YYYY-MM-DD]
  Last reviewed:    [YYYY-MM-DD]
  Next review due:  [YYYY-MM-DD + 6 months]
  Review triggers:  Malta visa policy change | New university partnership | Tuition fee update | Scholarship deadline change
-->
```

### Freshness triggers — update article immediately when

| Trigger | Action |
|---|---|
| Malta student visa policy changes | Update visa section + dateModified in schema |
| New university or college partnership | Update programs section + add to entity list |
| Tuition fee changes | Update costs section + all fee figures |
| New scholarship announced | Add to scholarships section |
| Malta immigration regulation update | Update legal/requirements section |
| Article drops below position 5 | Full content refresh + competitor gap re-analysis |

### How to signal freshness to Google

1. Update `dateModified` in the Article/BlogPosting schema
2. Update the visible "Last updated" date in the byline:

```html
<p style="color:#6b7280;font-size:14px;margin-bottom:24px;">
  By <strong>Outreach Recruitment Agency</strong> · Published [DATE] · <strong>Updated [DATE]</strong> · [X] min read
</p>
```

3. Add a visible "What's new" note at the top of the article when major changes are made:

```html
<div style="background:#fef9c3;border-left:4px solid #ca8a04;padding:12px 16px;border-radius:4px;margin-bottom:24px;font-size:14px;">
  <strong>Updated [MONTH YEAR]:</strong> [1-sentence summary of what changed — e.g. "Visa fee figures updated to reflect 2025 Identity Malta rates."]
</div>
```

### Freshness checklist (on every update)

- [ ] `dateModified` updated in JSON-LD schema
- [ ] Byline "Updated" date changed
- [ ] "What's new" note added if content changed substantially
- [ ] `<meta name="last-modified">` updated in `<head>`
- [ ] Published Articles Log updated in SKILL-TEMPLATE.md

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

## SERP FEATURE DOMINATION STRATEGY

For every article, explicitly target **multiple SERP features simultaneously** for the same primary keyword. Owning more than one feature per keyword multiplies visibility without needing multiple #1 rankings.

### Target SERP features per article

Generate a per-article feature targeting table:

| SERP Feature | Triggered by | Content element that targets it |
|---|---|---|
| **Featured Snippet (Position Zero)** | Direct answer to primary question | Position Zero Block (40–50 words, after H1) |
| **People Also Ask (PAA) box** | Answering sub-questions in H3s | PAA questions section + H3 self-contained answers |
| **FAQ rich result** | FAQPage JSON-LD schema | FAQ Accordion section + FAQPage schema |
| **HowTo rich result** | HowTo JSON-LD schema | Step-by-step sections + HowTo schema |
| **Video carousel** | VideoObject JSON-LD schema | Video embed / placeholder section |
| **Image pack** | Optimised `<img>` with alt text | Hero image + inline article images |
| **Sitelinks / Breadcrumb** | BreadcrumbList schema | Breadcrumb nav + schema |
| **Review stars** | AggregateRating schema | Testimonials section + AggregateRating schema |
| **Knowledge Panel** | Entity SEO + Organization schema | Entity coverage + Organization/LocalBusiness schema |

### Feature domination map (output per article)

For the specific article being generated, state which features are actively targeted:

```
SERP Feature Domination Map — [Article Title]
Primary keyword: [keyword]

Feature                  | Targeted? | Content element
-------------------------|-----------|------------------------------------------
Featured Snippet         | ✅        | Position Zero Block — line [X] of article
People Also Ask          | ✅        | H3 sections + PAA list
FAQ rich result          | ✅        | FAQ Accordion + FAQPage JSON-LD
HowTo rich result        | ✅ / N/A  | [Step section name] + HowTo JSON-LD
Video carousel           | ✅        | Video placeholder + VideoObject schema
Image pack               | ✅        | [Image file name] — alt: "[alt text]"
Breadcrumb rich result   | ✅        | BreadcrumbList schema — 3 levels
Review stars             | ✅        | Testimonials + AggregateRating schema
Knowledge Panel          | ✅        | Entity list + Organization schema
```

### Priority rule

If time is limited, prioritise in this order:
1. Featured Snippet — highest CTR impact
2. PAA box — captures question-based queries
3. FAQ rich result — extends SERP real estate
4. HowTo — for process-based articles
5. Video carousel — growing SERP presence

---

## OUTPUT FORMAT

Provide the final output in this exact order:

**PRE-WRITING CHECKS**
1. Cannibalization Check — conflict found / resolution
2. Competitor Gap Analysis — gap matrix + differentiation angle
3. SEO Research — keyword strategy + NLP Semantic Density table
4. Search Intent
5. Topical Depth Score — 5Ws+H table per H2 section
6. SERP Feature Domination Map — which features targeted + content elements

**METADATA**
7. SEO Title Options (5)
8. Meta Descriptions (5)
9. URL Slug
10. Position Zero Block (40–50 words, plain prose — placed after H1)

**FULL ARTICLE**
11. Full Article (4000+ words) — must include:
    - Semantic HTML5 skeleton structure
    - Skip-to-content link
    - Author box (above introduction)
    - Position Zero paragraph
    - ToC with `#id` anchor links
    - All passage-optimised H2/H3 sections (self-contained summaries)
    - All 5 mandatory CTAs at correct positions
    - Testimonials block (2× — after first section + near conclusion)
    - Multilingual blocks (Arabic + French)
    - Video placeholder section
    - FAQ Accordion (CSS-only, minimum 5 questions)
    - Content Upgrade CTA
    - Related Articles section
    - Cite This Article block
    - Back to Malta Study Guide links (top + bottom)

**AEO / AI / STRUCTURED DATA**
12. People Also Ask (PAA) questions
13. Voice Search Questions
14. FAQ Section (matches FAQ Accordion in article)
15. Entity Map
16. Schema Markup (JSON-LD) — Article, FAQPage, HowTo (if applicable), VideoObject stub, BreadcrumbList, AggregateRating, Organization

**LINKING & AUTHORITY**
17. Internal Link Silo Map — up/across/down links + click depth
18. Internal Link Opportunities — 5 mandatory links with varied anchor texts
19. External Link Opportunities — authoritative sources only (.gov, .edu, .eu)
20. Content Cluster Map

**STRATEGY**
21. Local SEO Strategy
22. International SEO Strategy
23. Programmatic SEO — country variant suggestions for this topic
24. AI Optimization Recommendations
25. GEO Recommendations
26. CTR Optimization Recommendations

**TECHNICAL**
27. Core Web Vitals Compliance Checklist
28. Accessibility (a11y) Checklist
29. Content Freshness Protocol — update schedule + triggers

**PUBLICATION**
30. Blog Card HTML — for `/malta-study-guide` index page
31. Post-Publish Submission Checklist — GSC, Bing, sitemap, internal linking pass, LinkedIn post

### Malta Study Guide CTA HTML Template (use in article body)

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

- [ ] Apply Now CTA button appears after Introduction
- [ ] Apply Now CTA button appears mid-article (after a key section)
- [ ] Apply Now CTA button appears before Conclusion
- [ ] Browse Programs link appears in the programs/courses section
- [ ] Browse Programs link appears in the Conclusion
- [ ] Study in Malta internal link appears in Introduction
- [ ] Study in Malta internal link appears in Internal Links section
- [ ] Free Webinar link appears mid-article
- [ ] Free Webinar link appears in Conclusion
- [ ] Malta Study Guide link appears mid-article
- [ ] Malta Study Guide link appears in Internal Links section

The article must be comprehensive, factually accurate, authoritative, and optimized for both traditional search engines and AI search engines.

---

## URL ROUTING RULES — MANDATORY

**One rule for all articles — no exceptions.**

Every article generated by this skill, regardless of topic, must use the root-level slug URL:

```
https://outreachrecruitment.net/[slug]
```

### Examples

| Article Topic | Correct URL |
|---|---|
| Student accommodation in Malta | `https://outreachrecruitment.net/student-accommodation-in-malta` |
| Malta student visa guide | `https://outreachrecruitment.net/malta-student-visa-complete-guide` |
| Cost of living in Malta | `https://outreachrecruitment.net/cost-of-living-in-malta-as-a-student` |
| Why Malta for international students | `https://outreachrecruitment.net/why-malta-is-becoming-europes-top-destination` |
| Working while studying in Malta | `https://outreachrecruitment.net/working-while-studying-in-malta` |

### Canonical tag

```html
<link rel="canonical" href="https://outreachrecruitment.net/[slug]" />
```

### og:url

```html
<meta property="og:url" content="https://outreachrecruitment.net/[slug]" />
```

### What NOT to use

| Wrong ❌ | Why |
|---|---|
| `/blog/[slug]` | Deprecated — causes 404 |
| `/malta-study-guide/[slug]` | Deprecated — causes 404 |
| `/study-in-malta/[slug]` | Does not exist |

---

### Breadcrumb Schema (all articles)

Every Study in Malta article must show **3 levels**: Home → Malta Study Guide → Article.

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://outreachrecruitment.net/"},
    {"@type": "ListItem", "position": 2, "name": "Malta Study Guide", "item": "https://outreachrecruitment.net/malta-study-guide"},
    {"@type": "ListItem", "position": 3, "name": "[Article Title]", "item": "https://outreachrecruitment.net/[slug]"}
  ]
}
```

---

## BLOG INDEX — MALTA STUDY GUIDE

**Every new Study in Malta article must be listed in the blog index at:**
`https://outreachrecruitment.net/malta-study-guide`

### Rules

- The article's **canonical URL** is `https://outreachrecruitment.net/[slug]` (root level)
- The article **appears as a card** in the Malta Study Guide blog index at `/malta-study-guide`
- The breadcrumb always shows: **Home → Malta Study Guide → [Article Title]**
- Every article must include a "Back to Malta Study Guide" link in the header and footer

### Back to Blog Index Link (include at top and bottom of every article)

```html
<p style="margin-bottom:24px;">
  <a href="https://outreachrecruitment.net/malta-study-guide" style="color:#1a56db;text-decoration:underline;">
    ← Back to Malta Study Guide
  </a>
</p>
```

### Blog Card HTML (for malta-study-guide index page — generate one per article)

When generating an article, also output a **Blog Card snippet** to be added to the `/malta-study-guide` index:

```html
<div class="blog-card" style="border:1px solid #e5e7eb;border-radius:8px;padding:24px;margin-bottom:20px;">
  <p style="font-size:12px;color:#6b7280;margin-bottom:6px;">[CATEGORY] · [DATE] · [READING TIME] min read</p>
  <h3 style="font-size:20px;font-weight:700;margin-bottom:8px;">
    <a href="https://outreachrecruitment.net/[slug]" style="color:#111827;text-decoration:none;">[Article Title]</a>
  </h3>
  <p style="color:#374151;margin-bottom:16px;">[Meta Description / excerpt — max 155 chars]</p>
  <a href="https://outreachrecruitment.net/[slug]" style="color:#1a56db;font-weight:600;text-decoration:none;">Read article →</a>
</div>
```

---

## SOCIAL META TAGS

Include in every article `<head>`:

```html
<!-- Indexing & snippet control — REQUIRED -->
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />

<!-- Open Graph -->
<meta property="og:title" content="[SEO Title]" />
<meta property="og:description" content="[Meta Description]" />
<meta property="og:url" content="https://outreachrecruitment.net/[slug]" />
<meta property="og:type" content="article" />
<meta property="og:image" content="https://outreachrecruitment.net/images/[slug]-og.jpg" />
<meta property="og:site_name" content="Outreach Recruitment" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="[SEO Title]" />
<meta name="twitter:description" content="[Meta Description]" />
<meta name="twitter:image" content="https://outreachrecruitment.net/images/[slug]-og.jpg" />

<!-- Article metadata -->
<meta property="article:published_time" content="[ISO 8601 DATE]" />
<meta property="article:modified_time" content="[ISO 8601 DATE]" />
<meta property="article:author" content="Outreach Recruitment Agency" />
<meta property="article:section" content="Study in Malta" />
```

---

## ARTICLE HEADER METADATA (required in every article)

Add these fields in the article header or frontmatter:

```html
<meta name="date" content="[YYYY-MM-DD]" />
<meta name="last-modified" content="[YYYY-MM-DD]" />
<meta name="reading-time" content="[X] min read" />
<meta name="author" content="Outreach Recruitment Agency" />
<meta name="category" content="Study in Malta" />
```

Display visibly in the article byline:

```html
<p style="color:#6b7280;font-size:14px;margin-bottom:24px;">
  By <strong>Outreach Recruitment Agency</strong> · [YYYY-MM-DD] · [X] min read
</p>
```

---

## RELATED ARTICLES SECTION

Include a "Related Articles" section near the bottom of every article (before Conclusion), using 3 articles from the Study in Malta cluster:

```html
<div style="background:#f9fafb;border-radius:8px;padding:24px;margin:32px 0;">
  <h3 style="font-size:18px;font-weight:700;margin-bottom:16px;">Related Articles</h3>
  <ul style="list-style:none;padding:0;margin:0;">
    <li style="margin-bottom:12px;"><a href="https://outreachrecruitment.net/[related-slug-1]" style="color:#1a56db;">[Related Article Title 1]</a></li>
    <li style="margin-bottom:12px;"><a href="https://outreachrecruitment.net/[related-slug-2]" style="color:#1a56db;">[Related Article Title 2]</a></li>
    <li style="margin-bottom:12px;"><a href="https://outreachrecruitment.net/[related-slug-3]" style="color:#1a56db;">[Related Article Title 3]</a></li>
  </ul>
  <p style="margin-top:16px;margin-bottom:0;"><a href="https://outreachrecruitment.net/malta-study-guide" style="color:#1a56db;font-weight:600;">View all articles in the Malta Study Guide →</a></p>
</div>
```

---

## CONTENT UPGRADE / LEAD CAPTURE CTA

Include one Content Upgrade CTA per article — placed after the Related Articles section. Offers a downloadable resource in exchange for an email address. Increases dwell time, reduces bounce rate, and builds the mailing list.

### Content Upgrade types (choose the most relevant for each article)

| Article topic | Offer |
|---|---|
| Student visa | "Malta Student Visa Checklist — PDF" |
| Cost of living | "Malta Student Budget Calculator — PDF" |
| Universities | "Malta University Comparison Guide — PDF" |
| Accommodation | "Malta Student Housing Checklist — PDF" |
| Scholarships | "Malta Scholarship Deadlines Calendar — PDF" |
| General study guide | "Complete Malta Study Checklist — PDF" |

### Content Upgrade HTML Block

```html
<div class="content-upgrade" style="background:linear-gradient(135deg,#1e40af,#1a56db);padding:32px;border-radius:12px;text-align:center;margin:40px 0;color:#fff;">
  <p style="font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;opacity:0.85;margin-bottom:8px;">Free Download</p>
  <h3 style="font-size:22px;font-weight:700;margin-bottom:8px;">[Resource Title — e.g. Malta Student Visa Checklist]</h3>
  <p style="opacity:0.9;margin-bottom:24px;font-size:15px;">[1-sentence description of what they get — specific and valuable]</p>

  <form action="https://outreachrecruitment.net/subscribe" method="POST"
        style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;"
        aria-label="Download [Resource Title]">
    <input type="email" name="email" placeholder="Your email address"
           required aria-label="Email address"
           style="padding:12px 16px;border-radius:6px;border:none;font-size:15px;width:260px;color:#111827;" />
    <button type="submit"
            style="background:#fff;color:#1a56db;padding:12px 24px;border-radius:6px;font-weight:700;border:none;cursor:pointer;font-size:15px;"
            aria-label="Download [Resource Title] — free PDF">
      Download Free →
    </button>
  </form>
  <p style="font-size:12px;opacity:0.7;margin-top:12px;margin-bottom:0;">No spam. Unsubscribe at any time.</p>
</div>
```

### Rules

- Every article has exactly **one** Content Upgrade CTA
- The resource must be topically matched to the article (do not offer a generic newsletter)
- Form action URL should point to the Outreach Recruitment mailing list endpoint
- Include `aria-label` on form and submit button for accessibility
- Add `Privacy Policy` link near the form if capturing emails

---

## CITE THIS ARTICLE

Include a "Cite this article" block at the bottom of every article, before the footer. This passively earns backlinks from academic sites, student blogs, and research pages that copy your data.

```html
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin:40px 0;font-size:13px;color:#475569;">
  <p style="font-weight:700;margin-bottom:12px;">Cite this article</p>

  <p style="margin-bottom:8px;"><strong>APA:</strong><br>
  Outreach Recruitment Agency. ([YEAR]). <em>[Article Title]</em>. Outreach Recruitment.
  Retrieved from <a href="https://outreachrecruitment.net/[slug]" style="color:#1a56db;">https://outreachrecruitment.net/[slug]</a></p>

  <p style="margin-bottom:8px;"><strong>MLA:</strong><br>
  Outreach Recruitment Agency. "[Article Title]." <em>Outreach Recruitment</em>, [DAY MON. YEAR],
  outreachrecruitment.net/[slug].</p>

  <p style="margin-bottom:0;"><strong>Chicago:</strong><br>
  Outreach Recruitment Agency. "[Article Title]." Outreach Recruitment. [MONTH DAY, YEAR].
  https://outreachrecruitment.net/[slug].</p>
</div>
```

---

## VIDEO EMBED PLACEHOLDER

Include a video section in every article — even if no video exists yet. This signals multimedia intent to Google and reserves the space for future content.

### If a YouTube video exists

```html
<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:8px;margin:32px 0;">
  <iframe src="https://www.youtube.com/embed/[VIDEO_ID]"
          title="[Video title — must match VideoObject schema name]"
          width="560" height="315"
          style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;"
          loading="lazy" allowfullscreen></iframe>
</div>
```

### If no video exists yet

```html
<div style="background:#f1f5f9;border:2px dashed #cbd5e1;border-radius:8px;padding:32px;text-align:center;margin:32px 0;">
  <p style="font-weight:700;color:#475569;margin-bottom:8px;">Watch: [Article Topic] — Video Guide</p>
  <p style="color:#64748b;font-size:14px;margin-bottom:0;">Video coming soon. <a href="https://outreachrecruitment.net/webinar-study-in-malta.html" style="color:#1a56db;">Join our free webinar</a> for live guidance.</p>
</div>
```

**VideoObject schema stub (always include — even without a real video):**

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Watch: [Article Title] — Video Guide",
  "description": "[Meta description of the article]",
  "thumbnailUrl": "https://outreachrecruitment.net/images/[slug]-video-thumb.jpg",
  "uploadDate": "[YYYY-MM-DD]",
  "publisher": {
    "@type": "Organization",
    "name": "Outreach Recruitment",
    "url": "https://outreachrecruitment.net/"
  }
}
```

---

## PUBLISHED ARTICLES LOG

Track all generated articles here. Update after each generation.

| # | Title | Slug | Date | Status |
|---|---|---|---|---|
| 1 | *(add when first article is generated)* | | | |

---

## POST-PUBLISH SUBMISSION PROTOCOL

Execute this checklist **immediately after every article goes live**. Without it, new articles can take weeks to be crawled and indexed.

### Step-by-step submission

- [ ] **Google Search Console** — Submit URL for indexing
  - Go to Search Console → URL Inspection → enter `https://outreachrecruitment.net/[slug]`
  - Click "Request Indexing"
  - Also submit updated `sitemap.xml` via Settings → Sitemaps if it was regenerated

- [ ] **Bing Webmaster Tools** — Submit URL
  - Go to Bing Webmaster Tools → URL Submission → paste article URL
  - Submit updated sitemap if regenerated

- [ ] **Update sitemap.xml** — Add new article URL with `<lastmod>` date
  ```xml
  <url>
    <loc>https://outreachrecruitment.net/[slug]</loc>
    <lastmod>[YYYY-MM-DD]</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  ```

- [ ] **Update `/malta-study-guide` blog index** — Add the Blog Card HTML generated with this article

- [ ] **LinkedIn post** — Share article with 2–3 key insights + link. Use these hashtags:
  `#StudyInMalta #MaltaStudents #InternationalStudents #MaltaEducation #OutreachRecruitment`

- [ ] **Internal linking pass** — Go to 2–3 existing published articles and add a contextual link pointing TO this new article. This immediately seeds PageRank into it from established pages.

- [ ] **Published Articles Log** — Update the log in this SKILL-TEMPLATE.md file with title, slug, date, status

### Internal linking pass (on publication)

When a new article is published, update these existing articles to link to it:

| Existing article | Where to add link | Anchor text |
|---|---|---|
| `/study-in-malta` (pillar) | Relevant H2 section | Article title or topic phrase |
| `/malta-study-guide` (index) | Blog card | Article title |
| Most topically related cluster article | Related section or inline | Descriptive phrase |

---

## SEARCH CONSOLE KPI TRACKING GUIDE

Monitor these metrics in Google Search Console for every published article. Check at **2 weeks**, **6 weeks**, and **3 months** post-publish.

### KPI dashboard

| Metric | Where in GSC | What to watch |
|---|---|---|
| Impressions | Performance → Search results | Should grow week-over-week |
| Clicks | Performance → Search results | CTR = clicks ÷ impressions |
| Average position | Performance → Search results | Target < 10 within 8 weeks |
| Core Web Vitals | Experience → Core Web Vitals | All URLs should be "Good" |
| Rich results | Enhancements → (FAQ / HowTo / Breadcrumbs) | Should appear within 2–4 weeks |
| Index coverage | Indexing → Pages | Article should be "Indexed" — not "Crawled, not indexed" |

### Diagnostic table — what to do when KPIs signal a problem

| Signal | Diagnosis | Action |
|---|---|---|
| High impressions, low CTR (< 3%) | Title / meta not compelling enough | Rewrite title + meta — test 5 new variants |
| Position 5–15, good CTR | Content needs more depth | Competitor gap re-analysis + expand thin sections |
| Position 1–4, low impressions | Missing SERP features | Add FAQ schema, HowTo schema, improve Position Zero block |
| Zero impressions after 4 weeks | Not indexed | Re-request indexing in GSC; check `noindex` tags |
| "Crawled, not indexed" | Low perceived quality | Add more original data, expand thin sections, improve E-E-A-T |
| CWV flagged "Poor" | Performance issue | Run PageSpeed Insights; fix flagged images / scripts |
| Rich results not appearing | Schema error | Validate schema at schema.org/validator; fix errors |

### Review schedule

| Timeframe | Action |
|---|---|
| 2 weeks post-publish | Check indexing status + first impressions |
| 6 weeks post-publish | Review CTR + position — trigger title/meta rewrite if needed |
| 3 months post-publish | Full performance review — trigger content refresh if position > 10 |
| 6 months post-publish | Scheduled freshness review (per Content Freshness Protocol) |

---

## CONTENT REPURPOSING PACK — GENERATE AFTER ARTICLE

After the article is complete, generate five repurposed assets from the same source content. These are delivered after the HTML article, not inserted inside the article.

### Required repurposed formats

1. **LinkedIn carousel — 10 slides**
   - Slide 1: hook/title
   - Slides 2-8: key lessons, data, steps, mistakes
   - Slide 9: checklist or comparison
   - Slide 10: CTA to article / Apply Now / webinar

2. **YouTube video script — 5 minutes**
   - Hook, intro, 4-6 teaching sections, CTA, outro
   - Include spoken lines, not just bullet points

3. **Email newsletter — 300 words**
   - Subject line
   - Preview text
   - Body copy
   - One primary CTA

4. **WhatsApp / Telegram student community message**
   - 80-120 words
   - Mobile-friendly
   - Direct link to article or application page

5. **Twitter/X thread — 8 posts**
   - Post 1 hook
   - Posts 2-7 value points
   - Post 8 CTA

---

## REVISION HISTORY / CHANGELOG

Every article must include a visible changelog near the bottom, before references or the final CTA.

```html
<section aria-labelledby="revision-history">
  <h2 id="revision-history">Revision History</h2>
  <ul>
    <li><time datetime="[YYYY-MM-DD]">[Month YYYY]</time> — First published.</li>
    <li><time datetime="[YYYY-MM-DD]">[Month YYYY]</time> — [Specific update, e.g. visa fee updated to reflect Identity Malta 2026 rates.]</li>
  </ul>
</section>
```

Rules:

- Every factual update must be recorded.
- Each changelog item must describe what changed, not just "updated."
- Changelog date must match `dateModified` in Article schema for the latest update.

---

## HUMAN WRITER CONTENT BRIEF TEMPLATE

Generate this condensed brief whenever the article may be handed to a human writer.

```markdown
# Content Brief — [Article Title]

Primary keyword: [keyword]
Fallback keyword if needed: [keyword]
Search intent: [informational / commercial / mixed]
Target reader: [student type]
Required word count: 4,000+ words

Mandatory links:
- Apply Now: https://apply.outreachstudy.eu/
- Browse Programs: https://outreachrecruitment.net/study-in-malta#programs-table
- Study in Malta: https://outreachrecruitment.net/study-in-malta
- Webinar: https://outreachrecruitment.net/webinar-study-in-malta.html
- Malta Study Guide: https://outreachrecruitment.net/malta-study-guide/

Required sections:
- H1
- Position Zero paragraph
- Key Takeaways
- Trust bar
- Clickable anchor ToC
- Desktop sticky left ToC
- CTA banner under sticky ToC
- Main H2/H3 outline
- EU vs non-EU tabs if applicable
- At least 3 statistics with primary sources
- Responsive tables
- FAQ section
- Revision history
- References/Data Sources

Schema required:
- Article
- BlogPosting
- FAQPage
- BreadcrumbList
- HowTo if step-by-step

Delivery checks:
- 375px mobile fold passes
- ToC links click and jump to the correct sections
- Desktop sticky ToC stays on the left while scrolling
- Sidebar CTA appears under sticky ToC
- Article spacing is checked between title, headings, body text, and final paragraph
- Tables scroll horizontally on mobile
- JSON-LD validates
- All links verified
```

---

## IMAGE GENERATION SKILL

Every article gets **7 real photographs** fetched automatically from Unsplash / Pexels. No AI-generated images — real photography only. All in-article section images are rendered **full viewport width** using the `figure-full` CSS breakout class.

### Script

```bash
cd "STUDY IN MALTA SKILLS"
python3 generate-article-images.py --auto --slug "[article-slug]" --topic "[Article Title]"
```

Images are saved to `/images/[slug]/` and a ready-to-embed HTML file is written to `/images/[slug]/image-tags.html`.

---

### 7 Image Slots Per Article

| # | Slot | File Name | Size | Role | Loading |
|---|---|---|---|---|---|
| 1 | Hero | `[slug]-hero.webp` + `[slug]-hero-800w.webp` | 1200×630 | Page header + OG image | `fetchpriority="high"` |
| 2 | Section 1 | `[slug]-section-1.webp` | 1200×628 | First H2 section opener | `loading="lazy"` |
| 3 | Section 2 | `[slug]-section-2.webp` | 800×500 | Visa / requirements section | `loading="lazy"` |
| 4 | Section 3 | `[slug]-section-3.webp` | 800×500 | Costs / fees section | `loading="lazy"` |
| 5 | Section 4 | `[slug]-section-4.webp` | 800×500 | Accommodation section | `loading="lazy"` |
| 6 | Section 5 | `[slug]-section-5.webp` | 800×500 | Work / career section | `loading="lazy"` |
| 7 | Section 6 | `[slug]-section-6.webp` | 800×500 | Student life / location | `loading="lazy"` |

---

### Image SEO Requirements

Every image in every article must meet **all** of these standards:

**Alt text**
- Max 120 characters
- Describes what is visually in the photo (not keyword-stuffed)
- Ends with ` — Outreach Recruitment`
- Example: `International students studying in Malta university campus — Outreach Recruitment`

**Caption**
- Full sentence describing the scene
- Ends with `Photo: [Photographer Name] / [Source].`
- Example: `Students attending a university lecture in Malta. Photo: Vitaly Gariev / Unsplash.`

**Figure markup** (required for all non-decorative images)
```html
<figure>
  <img src="/images/[slug]/[slug]-[slot].webp"
       alt="[descriptive alt text] — Outreach Recruitment"
       width="[w]" height="[h]"
       loading="lazy" />
  <figcaption>[Caption]. Photo: [Photographer] / [Source].</figcaption>
</figure>
```

**Hero image** additionally requires:
- `fetchpriority="high"` (not `loading="lazy"`)
- `srcset` pointing to both 800w and 1200w WebP variants
- OG image meta tag updated to point to hero WebP

**Attribution comment** (above every `<figure>`, hidden from users, required for Unsplash/Pexels terms)
```html
<!-- Photo: [Photographer] on [Source] — [photo_url] -->
```

---

### OG / Twitter Image Meta Tags

Replace or add these in `<head>` using the hero image path:

```html
<meta property="og:image" content="https://outreachrecruitment.net/images/[slug]/[slug]-hero.webp" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:image" content="https://outreachrecruitment.net/images/[slug]/[slug]-hero.webp" />
```

---

### Query Strategy

The script auto-selects queries based on the article slug. You can override all 7 queries by passing `queries=[...]` when calling `fetch_images_for_article()` in Python. Default query sets are defined in `QUERY_SETS` in `generate-article-images.py`.

General pattern — one query per major article section:

| Slot | Query Theme |
|---|---|
| Hero | `[country/topic] students university outdoor` |
| Section 1 | `diverse university students lecture hall` |
| Section 2 | `visa passport documents application desk` |
| Section 3 | `student budget planning laptop` |
| Section 4 | `student apartment bedroom Mediterranean` |
| Section 5 | `student working part time cafe` |
| Section 6 | `[city/country] aerial view landmark` |

---

### Where to Place Images in the Article

| Image | Placement in HTML |
|---|---|
| Hero | Immediately inside `<header>` / top of `<main>`, before H1 or styled as the article banner |
| Section 1 | After the first H2 opening paragraph |
| Section 2 | After the H2 for visa / requirements |
| Section 3 | After the H2 for costs / fees |
| Section 4 | After the H2 for accommodation |
| Section 5 | After the H2 for work / career |
| Section 6 | After the H2 for student life, lifestyle, or the city/country |

---

### Full-Width Image Skill

All 6 section images in the article body must break out of the narrow article container and span the **full viewport width**. This is done with the `figure-full` CSS class defined in `assets/brand-overrides.css`.

**Required HTML for every section figure:**

```html
<!-- Photo: [Photographer] on [Source] — [photo_url] -->
<figure class="figure-full" itemscope itemtype="https://schema.org/ImageObject">
  <img src="/images/[slug]/[slug]-section-N.webp"
       alt="[descriptive alt text — max 120 chars] | Outreach Recruitment"
       width="[w]" height="[h]"
       loading="lazy" decoding="async"
       sizes="(max-width: 600px) 100vw, [w]px"
       itemprop="contentUrl" />
  <figcaption itemprop="caption" style="font-size:13px;color:#6b7280;margin-top:8px;">
    [Caption sentence]. Photo: [Photographer] / [Source].
  </figcaption>
</figure>
```

**CSS in `assets/brand-overrides.css`** (already present — do not duplicate):

```css
.cms-article figure.figure-full {
  position: relative;
  width: 100vw;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 56px;
  margin-bottom: 56px;
  max-width: 100vw;
}
.cms-article figure.figure-full img {
  display: block;
  width: 100%;
  height: auto;
  max-height: 620px;
  object-fit: cover;
  border-radius: 0;
}
.cms-article figure.figure-full figcaption {
  text-align: center;
  max-width: 780px;
  margin: 10px auto 0;
  padding: 0 20px;
  font-size: 13px;
  color: #6b7280;
}
```

**Rules:**
- `figure-full` class → **always required** on section images (never use inline margin styles instead)
- Parent container must **not** have `overflow: hidden` (Webflow `.container.tight` does not — safe to use)
- Hero image (`class="media-fill"`) uses its own CSS — do **not** add `figure-full` to the hero
- On mobile (≤767px) `max-height` reduces to 280px to avoid tall images stacking poorly

---

### Image Checklist (per article)

- [ ] Script run: `python3 generate-article-images.py --auto --slug "[slug]" --topic "[title]"`
- [ ] 7 WebP files confirmed in `/images/[slug]/`
- [ ] Hero at exact 16:9 ratio (e.g. 1200×675) to match `cms-featured-media` CSS `aspect-ratio: 16/9`
- [ ] Hero srcset 800w variant confirmed (`[slug]-hero-800w.webp`)
- [ ] `image-tags.html` generated and reviewed
- [ ] All 7 `<figure>` blocks embedded at correct section positions
- [ ] All 6 section figures use `class="figure-full"` (full viewport width)
- [ ] Hero `<img>` uses `fetchpriority="high"` (not `loading="lazy"`)
- [ ] All 6 section images use `loading="lazy"` and `decoding="async"`
- [ ] All `<img>` have explicit `width` and `height`
- [ ] All `<img>` have descriptive `alt` text (max 120 chars, ends with `| Outreach Recruitment`)
- [ ] All images wrapped in `<figure class="figure-full">` + `<figcaption>`
- [ ] All figures have `itemscope itemtype="https://schema.org/ImageObject"`
- [ ] All images have `itemprop="contentUrl"`, figcaptions have `itemprop="caption"`
- [ ] Attribution HTML comments present above each `<figure>`
- [ ] OG / Twitter `og:image` meta tags updated to hero WebP URL
- [ ] `og:image:width` = 1200, `og:image:height` = 675
- [ ] `image-manifest.json` saved in `/images/[slug]/`
- [ ] Images are **real photographs** (Unsplash or Pexels) — never AI-generated

---

## OUTPUT FILE STRUCTURE

Save every generated article as an HTML file at the **project root**:

```
[primary-keyword-slug].html
```

Examples:
```
student-accommodation-in-malta.html
malta-student-visa-complete-guide.html
cost-of-living-in-malta-as-a-student.html
why-malta-is-becoming-europes-top-destination.html
```

Working drafts may be saved to `STUDY IN MALTA SKILLS/generated/` before being moved to the project root.

### OUTPUT CHECKLIST (verify before delivering)

**Pre-writing checks**
- [ ] Can We Rank? keyword difficulty assessment completed; fallback keyword selected if needed
- [ ] Cannibalization Check completed — no keyword conflict, or conflict resolved
- [ ] Competitor Gap Analysis completed — gap matrix + differentiation angle stated
- [ ] Topical Depth Score completed — all H2 sections score ≥ 4/6
- [ ] SERP Feature Domination Map generated

**Structure & URLs**
- [ ] Article saved as `[slug].html` at project root
- [ ] Canonical URL is `https://outreachrecruitment.net/[slug]`
- [ ] Breadcrumb shows: Home → Malta Study Guide → [Article Title]
- [ ] Semantic HTML5 skeleton used (`<article>`, `<section>`, `<aside>`, `<nav>`, `<main>`)
- [ ] Every H2/H3 has a unique `id` attribute matching ToC `#anchor` links
- [ ] Every ToC item is clickable and jumps to the matching section
- [ ] Desktop article layout uses sticky left ToC for articles over 2,000 words
- [ ] Sticky ToC has a compact CTA banner underneath
- [ ] Skip-to-content link is first element in `<body>`

**Head tags**
- [ ] `<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />` present
- [ ] Social meta tags (OG + Twitter Card) included
- [ ] `datePublished` and `dateModified` set in schema
- [ ] Content freshness HTML comment with next review date included

**Article body**
- [ ] Mobile-first fold passes at 375px: H1 + Position Zero paragraph + first CTA visible without scrolling
- [ ] Position Zero Block (40–50 words, plain prose) placed after H1, before ToC
- [ ] Key Takeaways box placed before introduction with 4–5 bullets
- [ ] Trust bar / social proof strip placed near top with only approved true claims
- [ ] Author box appears above introduction — links to `/about` + LinkedIn
- [ ] Every H2/H3 starts with a self-contained 40–60 word summary sentence
- [ ] Article byline shows author + published date + reading time
- [ ] Article spacing rules applied: title-to-body, heading-to-text, section spacing, and final paragraph spacing
- [ ] EU vs non-EU CSS-only tabs included when the topic differs by audience
- [ ] Testimonials block included (2× — after first section + near conclusion)
- [ ] Multilingual blocks included — Arabic (`dir="rtl"`) + French
- [ ] FAQ Accordion (CSS-only `<details>`/`<summary>`) — minimum 5 questions
- [ ] Content Upgrade CTA included — topically matched resource
- [ ] At least 3 verifiable statistics included with year, source name, and primary source link
- [ ] Data Sources section included
- [ ] Revision History / Changelog section included with latest `dateModified`
- [ ] "What's new" note added if this is an update (not first publish)

**CTAs & links**
- [ ] Apply Now CTA button appears 3× (after intro, mid-article, before conclusion)
- [ ] Browse Programs link appears 2×
- [ ] Study in Malta guide link appears 2×
- [ ] Free Webinar link appears 2×
- [ ] Malta Study Guide link appears 2×
- [ ] No two internal links to the same URL use the same anchor text
- [ ] Internal Link Silo Map: links UP to pillar + blog index, DOWN to 2+ cluster articles
- [ ] Click depth from homepage: ≤ 2 clicks
- [ ] All external links: .gov / .edu / .eu / authoritative sources + `rel="noopener noreferrer"`
- [ ] Broken link check: all outbound URLs verified live before delivering
- [ ] Social sharing buttons included: WhatsApp, LinkedIn, Email — no JavaScript

**Images (IMAGE GENERATION SKILL)**
- [ ] `generate-article-images.py` run with `--auto --slug "[slug]" --topic "[title]"`
- [ ] 7 WebP files confirmed in `/images/[slug]/`
- [ ] Hero at exact 16:9 ratio (1200×675), srcset 800w variant confirmed
- [ ] All 7 `<figure>` blocks embedded at correct H2 section positions
- [ ] All 6 section figures use `class="figure-full"` (full viewport width breakout)
- [ ] Hero uses `fetchpriority="high"`, all others `loading="lazy"` + `decoding="async"`
- [ ] OG + Twitter `og:image` meta tags point to hero WebP (`og:image:height` = 675)
- [ ] Attribution HTML comments above every `<figure>`
- [ ] All section figures have `itemscope itemtype="https://schema.org/ImageObject"`
- [ ] Images are real photographs (Unsplash / Pexels) — no AI images

**Media & performance**
- [ ] All `<img>` tags have explicit `width` and `height`
- [ ] Every non-decorative image uses `<figure>` and `<figcaption>`
- [ ] Below-fold images use `loading="lazy"`
- [ ] Hero image uses `fetchpriority="high"`
- [ ] All images in WebP format
- [ ] Video placeholder section included (real embed or placeholder box)
- [ ] No render-blocking scripts in `<head>`
- [ ] All tables use `.table-scroll`, `<caption>`, `<thead>`, and scoped `<th>` cells
- [ ] Tables tested at 375px width; no horizontal page overflow or CLS
- [ ] Print stylesheet included

**Accessibility**
- [ ] Skip-to-content link present
- [ ] All CTA buttons have `aria-label`
- [ ] All images have meaningful `alt` text (or `alt=""` for decorative)
- [ ] Heading order: H1 → H2 → H3 (no skipped levels)
- [ ] Color contrast: body text ≥ 4.5:1, links ≥ 3:1

**Schema**
- [ ] Article / BlogPosting schema
- [ ] FAQPage JSON-LD (matches FAQ Accordion)
- [ ] HowTo schema generated (if step-by-step process present)
- [ ] VideoObject schema stub included
- [ ] BreadcrumbList: 3 levels — Home → Malta Study Guide → Article
- [ ] AggregateRating schema (when testimonials included)
- [ ] Organization / LocalBusiness schema
- [ ] All JSON-LD parses as valid JSON
- [ ] Schema.org validator checked
- [ ] Google Rich Results Test checked
- [ ] Schema warnings explained if caused by unavailable optional data

**Bottom of article**
- [ ] Related Articles section (3 articles + link to blog index)
- [ ] "Cite this article" block (APA, MLA, Chicago)
- [ ] "Back to Malta Study Guide" link at top and bottom

**Publication & tracking**
- [ ] Blog Card HTML generated for `/malta-study-guide` index page
- [ ] Post-Publish Submission Checklist included as output section
- [ ] NLP Semantic Density table included in SEO Research output
- [ ] Published Articles Log updated in this SKILL-TEMPLATE.md file
- [ ] Search Console KPI review dates noted (2 weeks / 6 weeks / 3 months)
- [ ] Content Repurposing Pack generated: LinkedIn carousel, YouTube script, newsletter, WhatsApp/Telegram message, Twitter/X thread
- [ ] Human Writer Content Brief generated when requested or when handing work to a team member
