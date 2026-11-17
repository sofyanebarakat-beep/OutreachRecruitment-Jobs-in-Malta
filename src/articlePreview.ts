// Article preview: renders a dashboard article (Markdown body) the way the website publisher
// (SEO Emp and Candidates/automation/publish_article.py) builds it, inside the live blog layout
// (/assets/blog-article.css), so editors can check it before publishing.

type Row = Record<string, any>;

const esc = (s: unknown) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const CTAS: Record<string, [string, string, string, string][]> = {
  Employer: [
    ["Need support filling a role in Malta?", "Outreach Recruitment can help you shortlist engaged, pre-vetted candidates and manage communication through every stage of the process.", "Request recruitment support", "/contact-us.html"],
    ["Ready to fill your next role in Malta?", "Speak to Outreach Recruitment about sourcing, screening, and keeping candidates engaged from first contact to offer.", "View employer services", "/employers.html"],
  ],
  Candidate: [
    ["Browse jobs in Malta now", "See current vacancies across every sector Outreach Recruitment recruits for.", "Browse jobs in Malta", "/jobs/"],
    ["Ready to apply?", "Register your interest with Outreach Recruitment and get matched with current openings in Malta.", "Register your interest", "/jobs/people-connector.html"],
  ],
  JobsInMalta: [
    ["See what's hiring right now", "Browse live vacancies across Malta's industries.", "Browse jobs in Malta", "/jobs/"],
    ["Find your next role", "Register your interest and get matched with current openings across Malta.", "Register your interest", "/jobs/people-connector.html"],
  ],
};

function pillar(category?: string) {
  const c = String(category || "").toLowerCase();
  if (c.includes("jobs in malta")) return "JobsInMalta";
  if (c.includes("employer")) return "Employer";
  return "Candidate";
}

function inline(text: string) {
  const links: string[] = [];
  let s = esc(text.trim()).replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, label, url) => {
    const external = /^https?:\/\//.test(url) && !/^https?:\/\/(www\.)?outreachrecruitment\.net/.test(url);
    links.push(`<a href="${url}"${external ? ' target="_blank" rel="noopener"' : ""}>${label}</a>`);
    return `\u0000${links.length - 1}\u0000`;
  });
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");
  return s.replace(/\u0000(\d+)\u0000/g, (_m, i) => links[Number(i)]);
}

function table(lines: string[]) {
  const rows = lines
    .filter((l) => !/^\s*\|?[\s:|-]+\|?\s*$/.test(l))
    .map((l) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
  if (!rows.length) return "";
  const [head, ...body] = rows;
  return (
    '<div class="article-table-wrap"><table class="check-table"><thead><tr>' +
    head.map((c) => `<th>${inline(c)}</th>`).join("") +
    "</tr></thead><tbody>" +
    body.map((r) => "<tr>" + r.map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>").join("") +
    "</tbody></table></div>"
  );
}

function blocks(md: string) {
  const out: string[] = [];
  const lines = md.split("\n");
  let i = 0;
  while (i < lines.length) {
    const t = lines[i].trim();
    if (!t) { i++; continue; }
    if (t.startsWith("|")) {
      const b: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) b.push(lines[i++]);
      out.push(table(b));
      continue;
    }
    const list = /^[-*]\s+/.test(t) ? { re: /^[-*]\s+/, tag: "ul" } : /^\d+\.\s+/.test(t) ? { re: /^\d+\.\s+/, tag: "ol" } : null;
    if (list) {
      const items: string[] = [];
      while (i < lines.length && list.re.test(lines[i].trim())) items.push(lines[i++].trim().replace(list.re, ""));
      out.push(`<${list.tag}>` + items.map((x) => `<li>${inline(x)}</li>`).join("") + `</${list.tag}>`);
      continue;
    }
    const para: string[] = [];
    while (i < lines.length && lines[i].trim() && !/^([-*]\s+|\d+\.\s+|\|)/.test(lines[i].trim())) para.push(lines[i++].trim());
    if (para.length) out.push(`<p>${inline(para.join(" "))}</p>`);
  }
  return out.join("\n");
}

function split(body: string, marker: string) {
  const re = new RegExp(`^${marker}\\s+(.+)$`, "gm");
  const m = [...body.matchAll(re)];
  return m.map((x, i) => [x[1].trim(), body.slice(x.index! + x[0].length, i + 1 < m.length ? m[i + 1].index : body.length)] as [string, string]);
}

export function renderArticleBody(v: Row) {
  const problems: string[] = [];
  const body = String(v.body || "");
  const lines = body.split("\n");
  let i = 0;
  while (i < lines.length && !lines[i].trim()) i++;
  const quote: string[] = [];
  while (i < lines.length && lines[i].trim().startsWith(">")) quote.push(lines[i++].trim().replace(/^>\s?/, ""));
  const rest = lines.slice(i).join("\n");
  const parts: string[] = [];
  if (quote.length) parts.push(`<section><div class="answer-box"><strong>Quick answer:</strong> ${inline(quote.join(" "))}</div></section>`);
  else problems.push("The article should start with a short “quick answer” (a line beginning with >).");

  const images = new Map<string, Row>();
  for (const im of v.section_images || []) if (im?.url) images.set(String(im.heading || "").trim().toLowerCase(), im);
  const ctas = CTAS[pillar(v.category)];
  const sections = split(rest, "##");
  if (!sections.length) problems.push("Add at least one section heading (## Heading).");
  let n = 0, faq = "";
  for (const [h, content] of sections) {
    const key = h.toLowerCase();
    if (key === "faqs") {
      const qs = split(content, "###");
      if (qs.length < 3) problems.push(`The FAQs section has ${qs.length} question(s) — at least 3 are needed to publish.`);
      faq = '<section class="article-faq-section"><h2>FAQs</h2><div class="faq-list">' +
        qs.map(([q, a]) => `<div class="faq-item or-open"><div class="faq-item-top"><h3 class="text-large strong">${esc(q)}</h3></div>` +
          `<div class="faq-item-bottom"><div class="faq-item-text-wrapper"><p class="text-medium">${inline(a.split("\n").map((l) => l.trim()).filter(Boolean).join(" "))}</p></div></div></div>`).join("") +
        "</div></section>";
      continue;
    }
    if (key === "key takeaways") { parts.push(`<section><h2>${inline(h)}</h2>${blocks(content)}</section>`); continue; }
    n++;
    const subs = split(content, "###");
    const pre = content.includes("###") ? content.slice(0, content.indexOf("###")) : content;
    const im = images.get(key);
    parts.push("<section>" + `<h2>${inline(h)}</h2>` +
      (im ? `<figure class="article-section-image"><img src="${esc(im.url)}" alt="${esc(im.alt)}"/>${im.caption ? `<figcaption>${esc(im.caption)}</figcaption>` : ""}</figure>` : "") +
      blocks(pre) + subs.map(([sh, sc]) => `<h3>${inline(sh)}</h3>${blocks(sc)}`).join("") + "</section>");
    if (n === 2) { const [ch, cp, cl, chref] = ctas[0]; parts.push(`<div class="cta-box"><h2>${esc(ch)}</h2><p>${esc(cp)}</p><a href="${chref}">${esc(cl)}</a></div>`); }
  }
  if (sections.length && !faq) problems.push("Add a “## FAQs” section with at least 3 questions (### Question).");
  parts.push(faq);
  const [ch, cp, cl, chref] = ctas[ctas.length - 1];
  parts.push(`<div class="cta-box"><h2>${esc(ch)}</h2><p>${esc(cp)}</p><a href="${chref}">${esc(cl)}</a></div>`);
  const headings = sections.map(([h]) => h).filter((h) => h.toLowerCase() !== "faqs");
  return { html: `<article class="cms-article od-rich" id="odBody"><div class="w-richtext">${parts.join("\n")}</div></article>`, problems, headings };
}

export async function openArticlePreview(win: Window, v: Row, checklist: string[]) {
  let team: Row[] = [];
  try {
    const d = await (await fetch("/tools/team_data.json", { cache: "no-store" })).json();
    team = [d.ceo, ...d.members];
  } catch { /* preview still works without author photos */ }
  const who = team.find((p) => p.name?.toLowerCase() === String(v.author_name || "").toLowerCase());
  const { html: body, problems, headings } = renderArticleBody(v);
  const words = String(v.body || "").replace(/[#>*|[\]()-]/g, " ").split(/\s+/).filter(Boolean).length;
  const mins = Math.max(1, Math.ceil(words / 200));
  const when = new Date(v.scheduled_at || v.published_at || Date.now()).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  const byline = who
    ? `<span class="pv-by"><img src="${esc(who.avatar || who.photo)}" alt=""/><span><b>${esc(who.name)}</b><small>${esc(who.role)}</small></span></span>`
    : `<span>${esc(v.author_name || "Outreach Recruitment")}</span>`;
  const notes = [...problems, ...checklist.filter((c) => !problems.some((p) => p.toLowerCase().includes(c.toLowerCase().slice(0, 12))))];
  const url = `https://outreachrecruitment.net/${esc(v.slug || "your-article")}/`;
  const doc = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Preview: ${esc(v.seo_title || v.title || "Untitled article")}</title>
<link rel="stylesheet" href="https://cdn.prod.website-files.com/6996b31b0e199fa8510adf4f/css/people-work-webflow-108-template.webflow.shared.6c8c6beff.css">
<link rel="stylesheet" href="/assets/brand-overrides.css"><link rel="stylesheet" href="/assets/blog-article.css">
<style>
body{margin:0;background:#fff}
html{font-kerning:normal;text-rendering:optimizeLegibility;-webkit-text-size-adjust:100%} body{margin:0;background:#ffffff;color:#2c2d2d;-webkit-font-smoothing:antialiased} .cms-article .w-richtext > section{margin:0 0 3rem;scroll-margin-top:120px} .cms-article .w-richtext h2{margin:0 0 1rem;line-height:1.15} .cms-article .w-richtext h3{margin:1.75rem 0 .75rem;line-height:1.25} .cms-article .w-richtext p{margin:0 0 1.15rem;line-height:1.75} .cms-article .w-richtext ul{margin-top:.85rem;margin-bottom:1.35rem} .cms-article .w-richtext li{margin-bottom:.7rem;line-height:1.65} .answer-box,.note-box,.source-list{border:1px solid rgba(68,45,250,.16);border-radius:12px;background:#fff;padding:1.45rem;margin-bottom:2rem} .note-box{background:#f8f7ff;border-left:4px solid #442dfa} .cta-box{border-radius:12px;background:#2c2d2d;color:#fff;padding:1.6rem;margin:2.2rem 0} .cta-box h2,.cta-box p{color:#fff} .cta-box a{display:inline-flex;margin-top:.35rem;background:#fff;color:#2c2d2d;border-radius:999px;padding:.75rem 1.1rem;font-weight:700;text-decoration:none} .article-table-wrap{overflow-x:auto;margin-top:1.25rem;border:1px solid rgba(44,45,45,.14);border-radius:12px;background:#fff} .check-table{width:100%;border-collapse:collapse;min-width:720px;margin:0} .check-table th,.check-table td{padding:1rem 1.1rem;text-align:left;vertical-align:top;border-bottom:1px solid rgba(44,45,45,.12)} .check-table th{background:#2c2d2d;color:#fff;font-weight:700} .check-table tbody tr:nth-child(even){background:#f7f5ef} .check-table tbody tr:last-child td{border-bottom:0} .article-faq-section .faq-list{display:grid;gap:12px;margin-top:1.25rem} .article-faq-section .faq-item{border:1px solid rgba(44,45,45,.14);border-radius:12px;background:#fff;overflow:hidden} .article-faq-section .faq-item-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1.1rem 1.25rem;cursor:pointer} .article-faq-section .faq-item-bottom{display:grid;grid-template-rows:0fr;transition:grid-template-rows 240ms ease} .article-faq-section .faq-item.or-open .faq-item-bottom{grid-template-rows:1fr} .article-faq-section .faq-item-text-wrapper{overflow:hidden;padding:0 1.25rem} .article-faq-section .faq-item-text-wrapper p{padding-bottom:1.15rem;margin-bottom:0} .article-faq-section .minus{display:none} .article-faq-section .faq-item.or-open .plus{display:none} .article-faq-section .faq-item.or-open .minus{display:block} .related-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin-top:1.25rem} .related-grid .article-card{background:#fff;border:1px solid rgba(44,45,45,.12);border-radius:12px;overflow:hidden;text-decoration:none;color:inherit} .related-grid img{width:100%;aspect-ratio:400/210;object-fit:cover;display:block} .related-grid .article-card-content{padding:1rem} @media(max-width:767px){.related-grid{grid-template-columns:1fr}}
.od-rich .faq-item{margin:0}.article-faq-section .faq-list{margin-left:0}
.pv-bar{position:sticky;top:0;z-index:50;background:#1c2623;color:#fff;font:14px/1.45 "BDO Grotesk",Arial,sans-serif;padding:12px 20px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.pv-bar b{background:#442DFA;border-radius:999px;padding:4px 10px;font-size:12px;letter-spacing:1px;text-transform:uppercase}
.pv-bar button{margin-left:auto;background:#fff;color:#1c2623;border:0;border-radius:999px;padding:8px 14px;font-weight:600;cursor:pointer}
.pv-google{max-width:640px;margin:28px auto 0;padding:16px 20px;border:1px solid #e6e6e6;border-radius:12px;font-family:Arial,sans-serif}
.pv-google small{color:#4d5156;font-size:12px}.pv-google h3{color:#1a0dab;font-size:19px;font-weight:400;margin:4px 0}.pv-google p{color:#4d5156;font-size:14px;line-height:1.5;margin:0}
.pv-notes{max-width:1200px;margin:20px auto 0;padding:14px 18px;border-radius:12px;background:#fff7e6;border:1px solid #f5d38b;font:14px/1.5 "BDO Grotesk",Arial,sans-serif;color:#5c3d00}
.pv-notes strong{display:block;margin-bottom:4px}
.pv-by{display:inline-flex;align-items:center;gap:10px}.pv-by img{width:36px;height:36px;border-radius:50%;object-fit:cover}
.pv-by span{display:flex;flex-direction:column;line-height:1.2}.pv-by b{color:#0c0407;font-size:14px}.pv-by small{color:#442dfa;font-size:12px}
.od-image-empty{display:grid;place-items:center;aspect-ratio:1200/630;background:#f1f0fb;color:#6b6493;font:600 15px "BDO Grotesk",Arial,sans-serif;border:2px dashed #cfc9f5;border-radius:12px}
.od-rich .faq-item-bottom{grid-template-rows:1fr}.od-rich .faq-item-text-wrapper{overflow:visible}
</style></head><body>
<div class="pv-bar"><b>Preview</b><span>This is how the article will look on the website. It is not published and visitors cannot see it.</span><button onclick="window.close()">Close preview</button></div>
<div class="pv-google"><small>outreachrecruitment.net › ${esc(v.slug || "")}</small><h3>${esc(v.seo_title || v.title || "Add an SEO title")}</h3><p>${esc(v.meta_description || "Add a meta description — this is the text Google shows under the title.")}</p></div>
${notes.length ? `<div class="pv-notes"><strong>Before you publish (${notes.length})</strong>${notes.map((p) => `• ${esc(p)}`).join("<br>")}</div>` : ""}
<main class="main"><section class="od-section"><div class="od-container"><div class="od-layout"><div class="od-left">
<nav class="od-crumbs"><a href="/blog/">&larr; Back to Blog</a><span>/</span><a href="/">Home</a><span>/</span><b>${esc(v.category || "Blog")}</b></nav>
<div class="od-tag">${esc(v.category || "Blog")}</div>
<div class="od-meta">${byline}<i></i><span>${esc(when)}</span><i></i><span>${mins} min read</span></div>
<h1 class="od-title">${esc(v.title || "Untitled article")}</h1>
<div class="od-image">${v.featured_image_url ? `<img src="${esc(v.featured_image_url)}" alt="${esc(v.featured_image_alt)}" style="height:auto"/>` : '<div class="od-image-empty">No featured image yet — upload one before publishing</div>'}</div>
${body}
</div><aside class="od-right"><details class="od-side-block od-toc" open><summary>On this page</summary><ol>${headings.map((h) => `<li><a>${inline(h)}</a></li>`).join("")}</ol></details></aside></div></div></section></main>
<p style="text-align:center;color:#888;font:13px Arial,sans-serif;margin:40px 0">Will be published at ${url}</p>
</body></html>`;
  win.document.open();
  win.document.write(doc);
  win.document.close();
}
