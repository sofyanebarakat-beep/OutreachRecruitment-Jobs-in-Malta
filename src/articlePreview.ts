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
  const lines = md.replace(/\r\n?/g, "\n").split("\n");
  let i = 0;
  while (i < lines.length) {
    const t = lines[i].trim();
    if (!t) { i++; continue; }
    const h = t.match(/^(#{1,6})\s+(.+)$/);
    if (h) {
      const lvl = Math.min(4, Math.max(3, h[1].length));
      out.push(`<h${lvl}>${inline(h[2])}</h${lvl}>`);
      i++;
      continue;
    }
    if (/^(-{3,}|\*{3,})$/.test(t)) { i++; continue; }
    if (t.startsWith(">")) {
      const q: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith(">")) q.push(lines[i++].trim().replace(/^>\s?/, ""));
      out.push(`<div class="note-box">${inline(q.join(" "))}</div>`);
      continue;
    }
    if (/^<(p|div|ul|ol|table|h[1-6]|section|figure|img|blockquote)\b/i.test(t)) {
      const raw: string[] = [];
      while (i < lines.length && lines[i].trim()) raw.push(lines[i++]);
      out.push(raw.join("\n"));
      continue;
    }
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
    while (i < lines.length && lines[i].trim() && !/^([-*]\s+|\d+\.\s+|\||#{1,6}\s|>)/.test(lines[i].trim())) para.push(lines[i++].trim());
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
  const body = String(v.body || "").replace(/\r\n?/g, "\n");
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
  // Text before the first ## heading (intro paragraphs) — or the whole article if it has no ## headings.
  const firstH2 = rest.search(/^##\s+/m);
  const intro = firstH2 === -1 ? rest : rest.slice(0, firstH2);
  if (intro.trim()) parts.push(`<section>${blocks(intro)}</section>`);
  if (!sections.length) problems.push("Add section headings (## Heading) so the article gets a table of contents.");
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

// Live article pages used as the preview shell (same header, footer, styles and scripts as the website).
const SHELLS = ["/moving-to-malta-for-work/", "/how-to-hire-hospitality-staff-malta/", "/call-centre-salary-malta/"];

const ORIGIN = location.origin.includes("outreachrecruitment.net") || location.hostname === "localhost" ? location.origin : "https://outreachrecruitment.net";
let cache: Promise<{ shell: string; team: Row[] }> | null = null;

function loadShell() {
  cache ??= (async () => {
    let shell = "";
    for (const path of SHELLS) {
      try {
        const r = await fetch(ORIGIN + path, { cache: "no-store" });
        if (r.ok) { shell = await r.text(); break; }
      } catch { /* try the next one */ }
    }
    let team: Row[] = [];
    try {
      const d = await (await fetch(ORIGIN + "/tools/team_data.json", { cache: "no-store" })).json();
      team = [d.ceo, ...d.members];
    } catch { /* the byline falls back to the plain name */ }
    if (!shell) cache = null;
    return { shell, team };
  })();
  return cache;
}

export async function openArticlePreview(win: Window, v: Row, checklist: string[]) {
  const html = await buildPreviewHtml(v, checklist, true);
  if (!html) {
    win.document.body.innerHTML = "<p style='font:15px Arial;padding:24px'>Could not load the website template for the preview. Check your connection and try again.</p>";
    return;
  }
  win.location.href = URL.createObjectURL(new Blob([html], { type: "text/html" }));
}

/** Full preview page (live website template + the draft). `panel` adds the floating preview panel. */
export async function buildPreviewHtml(v: Row, checklist: string[], panel: boolean): Promise<string> {
  const { shell, team } = await loadShell();
  if (!shell) return "";
  const origin = ORIGIN;

  const who = team.find((p) => p?.name?.toLowerCase() === String(v.author_name || "").toLowerCase());
  const { html: body, problems } = renderArticleBody(v);
  const words = String(v.body || "").replace(/[#>*|[\]()-]/g, " ").split(/\s+/).filter(Boolean).length;
  const mins = Math.max(1, Math.ceil(words / 200));
  const when = new Date(v.scheduled_at || v.published_at || Date.now()).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
  const cat = v.category || "Blog";
  const avatar = who ? who.avatar || who.photo : "";
  const byline = who
    ? `<span><a class="od-byline" href="/our-team"><img src="${esc(avatar)}" alt="${esc(who.name)}" width="36" height="36"/><span class="od-byline-text"><b>${esc(who.name)}</b><small>${esc(who.role)}</small></span></a></span>`
    : `<span>${esc(v.author_name || "Outreach Recruitment")}</span>`;
  const authorBox = who
    ? `<div class="od-author"><img src="${esc(avatar)}" alt="${esc(who.name)}" width="56" height="56"/><div><strong>Written by ${esc(who.name)}</strong><span class="od-author-role">${esc(who.role)} · Outreach Recruitment</span><p>${esc(who.bio || "")}</p></div></div>`
    : `<div class="od-author"><img src="/assets/job-card-logo.jpg" alt="Outreach Recruitment" width="56" height="56"/><div><strong>Written by Outreach Recruitment</strong><p>Recruitment specialists in Malta helping employers hire and candidates find work.</p></div></div>`;
  const notes = [...problems, ...checklist.filter((c) => !problems.some((p) => p.toLowerCase().includes(c.toLowerCase().slice(0, 12))))];

  const doc = new DOMParser().parseFromString(shell, "text/html");
  const $ = (sel: string) => doc.querySelector(sel);
  const base = doc.createElement("base");
  base.href = origin + "/";
  doc.head.prepend(base);
  doc.title = `Preview: ${v.seo_title || v.title || "Untitled article"}`;
  doc.head.insertAdjacentHTML("beforeend", '<meta name="robots" content="noindex">');
  if ($(".od-crumbs b")) $(".od-crumbs b")!.textContent = cat;
  if ($(".od-tag")) $(".od-tag")!.textContent = cat;
  const meta = $(".od-section .od-meta");
  if (meta) meta.innerHTML = `${byline}<i></i><span>${esc(when)}</span><i></i><span>${mins} min read</span>`;
  if ($(".od-title")) $(".od-title")!.textContent = v.title || "Untitled article";
  const img = $(".od-image");
  if (img) {
    img.className = "od-image";
    img.innerHTML = v.featured_image_url
      ? `<img src="${esc(v.featured_image_url)}" alt="${esc(v.featured_image_alt)}" width="1200" height="630"/>`
      : '<div style="display:grid;place-items:center;aspect-ratio:1200/630;background:#f1f0fb;color:#6b6493;font-weight:600;border:2px dashed #cfc9f5;border-radius:12px">No featured image yet — upload one before publishing</div>';
  }
  const odBody = $("#odBody");
  if (odBody) odBody.outerHTML = body;
  const author = $(".od-end .od-author");
  if (author) author.outerHTML = authorBox;
  // The draft is not published yet: share buttons would share the shell article, so hide them.
  doc.querySelectorAll(".od-share").forEach((n) => n.remove());

  const fix = notes.length
    ? `<details class="pv-fix"><summary>${notes.length} thing${notes.length > 1 ? "s" : ""} to fix before publishing</summary><ul>${notes.map((p) => `<li>${esc(p)}</li>`).join("")}</ul></details>`
    : '<span class="pv-ok">✓ Ready to publish</span>';
  doc.head.insertAdjacentHTML("beforeend", `<style id="pv-style">
.pv-panel{position:fixed;left:16px;right:16px;bottom:12px;z-index:100000;max-width:760px;margin:0 auto;background:#1c2623;color:#fff;border-radius:16px;box-shadow:0 20px 50px rgba(0,0,0,.35);font:14px/1.45 "BDO Grotesk",Arial,sans-serif;padding:14px 16px}
.pv-top{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.pv-top b{background:#442DFA;border-radius:999px;padding:4px 10px;font-size:11px;letter-spacing:1px;text-transform:uppercase}
.pv-top button{margin-left:auto;background:#fff;color:#1c2623;border:0;border-radius:999px;padding:7px 14px;font-weight:600;cursor:pointer}
.pv-google{margin-top:10px;background:#fff;border-radius:10px;padding:10px 12px;font-family:Arial,sans-serif}
.pv-google small{color:#4d5156;font-size:12px}.pv-google strong{display:block;color:#1a0dab;font-size:17px;font-weight:400;margin:2px 0}.pv-google span{color:#4d5156;font-size:13px}
.pv-fix{margin-top:10px}.pv-fix summary{cursor:pointer;color:#ffd27a;font-weight:600}.pv-fix ul{margin:6px 0 0;padding-left:18px;color:#f3e3c3}
.pv-ok{display:inline-block;margin-top:10px;color:#9ff0b5;font-weight:600}
.pv-panel.min .pv-google,.pv-panel.min .pv-fix,.pv-panel.min .pv-ok{display:none}
#or-cookie-banner{display:none!important}
@media(max-width:600px){.pv-top span{display:none}}
</style>`);
  if (panel) doc.body.insertAdjacentHTML("beforeend", `<div class="pv-panel min" id="pvPanel"><div class="pv-top"><b>Preview</b><span>Not published — visitors cannot see this page.${notes.length ? ` <em style="color:#ffd27a;font-style:normal">${notes.length} to fix</em>` : ` <em style="color:#9ff0b5;font-style:normal">ready to publish</em>`}</span>
<button type="button" onclick="document.getElementById('pvPanel').classList.toggle('min')">Google preview &amp; checklist</button><button type="button" onclick="window.close()">Close</button></div>
<div class="pv-google"><small>outreachrecruitment.net › ${esc(v.slug || "")}</small><strong>${esc(v.seo_title || v.title || "Add an SEO title")}</strong><span>${esc(v.meta_description || "Add a meta description — Google shows it under the title.")}</span></div>${fix}</div>`);

  return "<!doctype html>\n" + doc.documentElement.outerHTML;
}
