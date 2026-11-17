// Article helpers for the SEO admin: SEO/GEO score, one-click fixes ("Fix it for me"), duplication.
type Row = Record<string, any>;

const SITE = "https://outreachrecruitment.net";
const lower = (s: unknown) => String(s ?? "").toLowerCase();
const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const internalLinks = (body: string) =>
  new Set(String(body || "").match(/https:\/\/(?:www\.)?outreachrecruitment\.net\/[A-Za-z0-9_?=#%&./-]*/g) || []).size;
const externalLinks = (body: string) =>
  new Set(String(body || "").match(/https:\/\/(?!(?:www\.)?outreachrecruitment\.net)[A-Za-z0-9.-]+\/[A-Za-z0-9_?=#%&./-]*/g) || []).size;
const words = (body: string) => String(body || "").replace(/[#>*|[\]()-]/g, " ").split(/\s+/).filter(Boolean).length;

// Official sources by category (same verified list as tools/article_sources_facts.py).
const SOURCES: Record<string, [string, string][]> = {
  "Study in Malta": [
    ["Malta Further and Higher Education Authority (MFHEA)", "https://mfhea.mt/"],
    ["University of Malta", "https://www.um.edu.mt/"],
    ["Identità — Central Visa Unit", "https://identita.gov.mt/central-visa-unit-applicable-fees-and-applications-applicable-fees/"],
  ],
  Employers: [
    ["Department for Industrial and Employment Relations (DIER)", "https://dier.gov.mt/"],
    ["Jobsplus — Malta's public employment service", "https://jobsplus.gov.mt/"],
    ["Eurostat — Labour market statistics", "https://ec.europa.eu/eurostat/web/labour-market"],
  ],
  default: [
    ["Jobsplus — Malta's public employment service", "https://jobsplus.gov.mt/"],
    ["Identità — Single Permit for non-EU nationals", "https://identita.gov.mt/expatriates-unit-main-page/noneu-nationals/employment-related-permits/single-permit/"],
    ["EURES — Living and working in Malta", "https://eures.europa.eu/living-and-working/living-and-working-conditions-europe/living-and-working-conditions-malta_en"],
  ],
};

const LINKS: Record<string, [string, string][]> = {
  "Study in Malta": [
    ["complete guide to studying in Malta", `${SITE}/study-in-malta-complete-guide`],
    ["Study in Malta news and guides", `${SITE}/news-updates?category=study-in-malta`],
    ["jobs in Malta for after your studies", `${SITE}/jobs/`],
  ],
  Employers: [
    ["Outreach Recruitment's employer services", `${SITE}/employers`],
    ["hiring advice for employers in Malta", `${SITE}/news-updates?category=employers`],
    ["request recruitment support", `${SITE}/contact-us`],
  ],
  default: [
    ["current jobs in Malta", `${SITE}/jobs/`],
    ["Jobs in Malta news and vacancy round-ups", `${SITE}/news-updates/jobs-in-malta/`],
    ["how to tailor your CV for jobs in Malta", `${SITE}/tailor-your-cv-for-jobs-in-malta/`],
  ],
};

export const DEFAULT_IMAGES: Record<string, string> = {
  "Jobs in Malta": "/assets/blog-featured/complete-guide-finding-jobs-malta-category.png",
  Employers: "/assets/blog-featured/how-a-recruitment-agency-helps-malta-employers-hire-faster.png",
  Candidates: "/assets/blog-featured/cv-writing-tips-how-to-get-hired-in-malta.png",
  "Study in Malta": "/assets/graduation-malta.jpg",
};

const pick = <T,>(m: Record<string, T>, cat?: string) => m[cat || ""] || m.default;

/** SEO/GEO score 0–100 from clear checks; `missing` lists what to add. */
export function articleScore(v: Row) {
  const body = String(v.body || "");
  const kw = lower(v.focus_keyword);
  const checks: [string, number, boolean][] = [
    ["Quick answer at the top (line starting with >)", 15, /^\s*>\s+\S/.test(body)],
    ["FAQs section with 3+ questions", 10, /^##\s+FAQs\s*$/im.test(body) && (body.split(/^##\s+FAQs\s*$/im)[1] || "").split(/^###\s+/m).length > 3],
    ["2+ official sources", 15, externalLinks(body) >= 2],
    ["3+ internal links", 10, internalLinks(body) >= 3],
    ["Section headings (##)", 5, /^##\s+(?!FAQs)/m.test(body)],
    ["Focus keyword in SEO title", 10, !!kw && lower(v.seo_title).includes(kw)],
    ["Meta description with keyword (50–160 characters)", 10, !!kw && lower(v.meta_description).includes(kw) && String(v.meta_description).length >= 50 && String(v.meta_description).length <= 160],
    ["Named author", 5, !!v.author_name && v.author_name !== "Outreach Recruitment"],
    ["Featured image with alt text", 10, !!v.featured_image_url && !!v.featured_image_alt],
    ["Length 600+ words", 10, words(body) >= 600],
  ];
  const score = checks.reduce((n, [, pts, ok]) => n + (ok ? pts : 0), 0);
  return { score, missing: checks.filter(([, , ok]) => !ok).map(([label]) => label) };
}

export const scoreTone = (n: number) => (n >= 80 ? "green" : n >= 55 ? "amber" : "red");

/** One-click fix for a checklist warning (from validateArticle). Returns the changes, or null if it needs a person. */
export function fixFor(warning: string, v: Row, services: Row[]): Row | null {
  const kw = String(v.focus_keyword || "").trim();
  const title = String(v.title || "").trim();
  const body = String(v.body || "");
  const cat = v.category as string | undefined;
  const w = warning.toLowerCase();
  if (w.startsWith("use a valid url slug"))
    return { slug: title.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80) };
  if (w.includes("seo title") && kw) {
    // Keyword first, never cut mid-phrase: fall back to shorter forms until it fits ~60 characters.
    const options = [
      lower(title).includes(lower(kw)) ? title : `${cap(kw)}: ${title}`,
      `${cap(kw)}: A Practical Guide`,
      cap(kw),
    ];
    const best = options.find((o) => o.length <= 60) || cap(kw);
    return { seo_title: best.length + 23 <= 70 ? `${best} | Outreach Recruitment` : best };
  }
  if (w.includes("meta description") && kw) {
    const firstPara = body.split(/\n\s*\n/).map((p) => p.trim()).find((p) => p && !/^[#>|-]/.test(p)) || "";
    const answer = (body.match(/^\s*>\s*(.+)$/m)?.[1] || v.excerpt || firstPara).replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/\*\*/g, "");
    let d = answer && lower(answer).includes(lower(kw)) ? answer : `${cap(kw)}: ${answer || `practical guidance from Outreach Recruitment in Malta.`}`;
    if (d.length > 155) d = d.slice(0, 152).replace(/\s+\S*$/, "") + "…";
    return { meta_description: d };
  }
  if (w.includes("alt text")) return { featured_image_alt: `${title || cap(kw)} — Outreach Recruitment Malta` };
  if (w.includes("featured image") && !v.featured_image_url) return { featured_image_url: DEFAULT_IMAGES[cat || ""] || DEFAULT_IMAGES.Candidates, featured_image_alt: v.featured_image_alt || `${title} — Outreach Recruitment Malta` };
  if (w.includes("related service") && services.length) {
    const m = services.find((s) => lower(s.name).includes(lower(cat).split(" ")[0])) || services[0];
    return { service_id: m.id };
  }
  if (w.includes("direct-answer")) {
    // Turn the opening paragraph (before the first heading) into the quick answer instead of repeating it.
    const head = body.match(/^##\s/m);
    const intro = head && head.index !== undefined ? body.slice(0, head.index) : body;
    const paras = intro.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
    if (paras.length && !paras[0].startsWith("#")) {
      const quick = paras[0].replace(/\s+/g, " ");
      const rest = [...paras.slice(1)].join("\n\n");
      return { body: `> ${quick}\n\n${rest ? rest + "\n\n" : ""}${body.slice(intro.length).trimStart()}` };
    }
    return { body: `> ${cap(kw || title)}: write a two-sentence answer to the reader's main question here.\n\n${body.trimStart()}` };
  }
  if (w.includes("faqs")) {
    const k = kw || title;
    return { body: `${body.trimEnd()}\n\n## FAQs\n\n### What is the first step with ${k}?\n\nStart with the official requirements and a clear plan, then compare your options before you apply or decide.\n\n### Where can I find current opportunities in Malta?\n\nSee the current vacancies on the [Outreach Recruitment jobs page](${SITE}/jobs/) and check each description for its requirements.\n\n### Should I confirm legal or permit details?\n\nYes. Rules can change and depend on your situation, so confirm work-permit, visa and legal questions with the official authority.\n` };
  }
  if (w.includes("internal links")) {
    const items = pick(LINKS, cat).map(([t, u]) => `- [${cap(t)}](${u})`).join("\n");
    return { body: insertBeforeFaqs(body, `## Related on Outreach Recruitment\n\n${items}`) };
  }
  if (w.includes("external sources") || w.includes("authoritative")) {
    const items = pick(SOURCES, cat).map(([t, u]) => `- [${t}](${u})`).join("\n");
    return { body: insertBeforeFaqs(body, `## Sources\n\n${items}`) };
  }
  return null;
}

function insertBeforeFaqs(body: string, block: string) {
  const m = body.match(/^##\s+FAQs\s*$/im);
  if (!m || m.index === undefined) return `${body.trimEnd()}\n\n${block}\n`;
  return `${body.slice(0, m.index).trimEnd()}\n\n${block}\n\n${body.slice(m.index)}`;
}

/** A fresh draft copied from an existing article. */
export function duplicateOf(r: Row): Row {
  const copy: Row = { ...r };
  for (const k of ["id", "published_at", "published_url", "scheduled_at", "created_at", "updated_at", "approved_by", "quality_score", "quality_notes", "rejection_reason", "validation_results"]) delete copy[k];
  return { ...copy, title: `Copy of ${r.title || "article"}`, slug: `${r.slug || "article"}-copy`.slice(0, 90), status: "draft" };
}

// Named author by category (must match ARTICLE_AUTHORS / the Our Team page).
export const CATEGORY_AUTHOR: Record<string, string> = {
  "Jobs in Malta": "Julián Longan Granados",
  Candidates: "Julián Longan Granados",
  Employers: "Andrea Zambrano",
  "Study in Malta": "Jeraldin Daniela Bohorquez",
};

const firstSentence = (text: string) =>
  text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/\*\*/g, "").replace(/\s+/g, " ").trim().split(/(?<=[.!?])\s/)[0] || "";

/** Key Takeaways list built from the article's own ## sections (AI search engines quote these). */
function keyTakeaways(body: string) {
  const sections = [...body.matchAll(/^##\s+(.+)$/gm)]
    .map((m, i, all) => {
      const end = i + 1 < all.length ? all[i + 1].index : body.length;
      const text = body.slice(m.index! + m[0].length, end).split(/\n\s*\n/).map((p) => p.trim()).find((p) => p && !/^[#>|-]/.test(p)) || "";
      return [m[1].trim(), firstSentence(text)] as [string, string];
    })
    .filter(([h, t]) => t && !/^(faqs|sources|key takeaways|related on)/i.test(h))
    .slice(0, 5);
  return sections.length >= 3 ? `## Key Takeaways\n\n${sections.map(([h, t]) => `- **${h}:** ${t}`).join("\n")}` : "";
}

/**
 * Run after every article generation: makes sure the draft passes every SEO / GEO / AI check
 * (quick answer, Key Takeaways, ## headings, 3+ internal links, 2+ official sources, FAQs, SEO title,
 * meta description 50–160 characters with the keyword, named author, 600+ words).
 */
export function completeArticle(input: Row, services: Row[] = []): Row {
  let v: Row = { ...input };
  const kw = String(v.focus_keyword || "").trim();
  const apply = (warning: string) => {
    const c = fixFor(warning, v, services);
    if (c) v = { ...v, ...c };
  };
  const body = () => String(v.body || "");
  if (!/^\s*>\s+\S/.test(body())) apply("Start with a direct-answer blockquote for AI search and the article template");
  if (!/^##\s+Key Takeaways/im.test(body())) {
    const kt = keyTakeaways(body());
    if (kt) {
      // right after the quick answer (and any intro paragraph), before the first section
      const first = body().search(/^##\s+/m);
      v.body = first === -1 ? `${body().trimEnd()}\n\n${kt}\n` : `${body().slice(0, first).trimEnd()}\n\n${kt}\n\n${body().slice(first)}`;
    }
  }
  if (internalLinks(body()) < 3) apply("Add at least three contextual Outreach Recruitment internal links");
  if (externalLinks(body()) < 2) apply("Cite at least two relevant authoritative external sources");
  if (!/^##\s+FAQs\s*$/im.test(body())) apply("Add an exact ## FAQs section with at least three questions");
  if (words(body()) < 600) {
    const k = kw || String(v.title || "this topic");
    v.body = insertBeforeFaqsExport(body(), `## Next steps\n\nIf you are considering ${k}, start by writing down what you need to know and which decisions depend on it. Compare at least two reliable sources, note any dates or deadlines, and keep copies of the documents you send. When a rule or requirement affects your situation, confirm it with the official authority rather than relying on social-media posts or second-hand advice.\n\nOnce you have the facts, set a simple plan: what you will do this week, what you are waiting for and who to contact if something changes. Outreach Recruitment works with employers and candidates across Malta every day, so if you have a question about roles, hiring or the next stage of a process, our team can point you in the right direction.`);
  }
  if (!kw || !lower(v.seo_title).includes(lower(kw))) apply("Include the focus keyword in the SEO title");
  const md = String(v.meta_description || "");
  if (!kw || !lower(md).includes(lower(kw)) || md.length < 50 || md.length > 160) {
    v.meta_description = "";
    apply("Use the focus keyword naturally in the meta description");
    if (String(v.meta_description).length < 50)
      v.meta_description = `${cap(kw || String(v.title))}: a practical guide from Outreach Recruitment in Malta, with steps, sources and FAQs.`.slice(0, 160);
  }
  if (!v.author_name || v.author_name === "Outreach Recruitment")
    v.author_name = CATEGORY_AUTHOR[v.category] || "Julián Longan Granados";
  if (!v.featured_image_alt && v.title) v.featured_image_alt = `${v.title} — Outreach Recruitment Malta`;
  return v;
}

const insertBeforeFaqsExport = (body: string, block: string) => insertBeforeFaqs(body, block);
