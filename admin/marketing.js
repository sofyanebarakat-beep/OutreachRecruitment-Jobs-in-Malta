/* Admin › Marketing › Email Marketing — ready-to-paste job posts.
 *
 * Builds a post for one job (or a generic round-up of several) from:
 *   ../tools/jobs_registry.json                 open jobs, their website address, category
 *   ../tools/ats_snapshots/<uuid>.json          the careers-page description (fact sheet)
 *   ../reports/daily-sync/index.json + <date>   which jobs were published today
 * The wording comes from an editable template (saved in this browser). Two copy buttons:
 *   email  → rich text (real bold) for email-marketing tools
 *   social → plain text with Unicode 𝗯𝗼𝗹𝗱 for Facebook / LinkedIn / Instagram
 */
(() => {
  "use strict";
  const SITE = "https://outreachrecruitment.net";
  const MORE_JOBS = SITE + "/jobs";
  const UUID_RE = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/;
  const TPL_KEY = "admin:marketing-template:v2", GEN_KEY = "admin:marketing-generic-template", FORMAT_KEY = "admin:marketing-picture-format";
  const PICTURE_FORMATS = {
    square: { label: "Instagram / Facebook", width: 1080, height: 1080 },
    story: { label: "Story", width: 1080, height: 1920 },
    linkedin: { label: "LinkedIn landscape", width: 1200, height: 627 },
  };
  const LEGACY_JOB_CTAS = [
    "👉 **Ready for your next step? Apply today!**",
    "🚀 **Your next opportunity could start here. Apply today!**",
  ];
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const store = { get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
                  set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };

  const DEFAULT_TEMPLATE = `🚨 **{hook}** 🚨
💼 **WE'RE HIRING: {title}**
📍 {job_highlights}

{intro}

🚀 **{apply_prompt}**

🌐 **Apply now:** {apply_url}
💼 **More Jobs:** {more_jobs_url}

{hashtags}`;
  const jobTemplate = () => {
    let template = store.get(TPL_KEY) || DEFAULT_TEMPLATE;
    template = template
      .replace(/^🚨 \*\*WE'RE HIRING: \{title\}\*\* 🚨$/m, "🚨 **{hook}** 🚨\n💼 **WE'RE HIRING: {title}**")
      .replace(/^📍 \{city\}, Malta · 🕒 \{job_type\} · 💶 \{salary\}$/m, "📍 {job_highlights}")
      .replace(/\n{0,2}\{good_fit\}\n?/g, "");
    return LEGACY_JOB_CTAS.reduce(
      (current, cta) => current.replace(cta, "🚀 **{apply_prompt}**"),
      template
    );
  };

  const DEFAULT_GENERIC = `🇲🇹 **NEW JOBS IN MALTA THIS WEEK** 🇲🇹

Looking for your next role? Outreach Recruitment is hiring for **{count} open positions** across Malta & Gozo. Here are some of the latest:

{job_list}

👉 Tap a link above to apply.
💼 **More Jobs:** {more_jobs_url}

#JobsInMalta #MaltaJobs #Hiring #RecruitmentMalta #WorkInMalta #OutreachRecruitment`;

  // ── text helpers ──────────────────────────────────────────────────────────
  const BOLD = (ch) => {
    const c = ch.codePointAt(0);
    if (c >= 65 && c <= 90) return String.fromCodePoint(0x1d5d4 + c - 65);
    if (c >= 97 && c <= 122) return String.fromCodePoint(0x1d5ee + c - 97);
    if (c >= 48 && c <= 57) return String.fromCodePoint(0x1d7ec + c - 48);
    return ch;
  };
  const toSocial = (t) => t.replace(/\*\*(.+?)\*\*/g, (_, s) => [...s].map(BOLD).join(""));
  const toPlain = (t) => t.replace(/\*\*(.+?)\*\*/g, "$1");
  const linkify = (s) => s.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1">$1</a>');
  const toHTML = (t) => `<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.55;color:#161616">` +
    t.split(/\n{2,}/).map((block) => `<p style="margin:0 0 14px">${linkify(esc(block)).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br>")}</p>`).join("") + `</div>`;
  const MALTESE = { "Ħ": "H", "ħ": "h", "Ż": "Z", "ż": "z", "Ċ": "C", "ċ": "c", "Ġ": "G", "ġ": "g" };
  const camel = (s) => String(s || "").replace(/[ĦħŻżĊċĠġ]/g, (c) => MALTESE[c]).normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .replace(/['’]/g, "").replace(/&/g, " ")
    .split(/[^A-Za-z0-9]+/).filter(Boolean).map((w) => w[0].toUpperCase() + w.slice(1).toLowerCase()).join("");
  const cityOf = (job, facts) => (facts?.city || String(job.location || "").split(",")[0] || "Malta").trim();
  const firstSentences = (text, max = 300) => {
    const parts = String(text).replace(/\s+/g, " ").trim().match(/[^.!?]+[.!?]+/g) || [String(text)];
    let out = "";
    for (const p of parts) { if ((out + p).length > max && out) break; out += p; }
    return out.trim();
  };

  // Split the careers-page description (HTML) into intro / responsibilities / requirements / offer.
  function parseDescription(html, text) {
    const doc = new DOMParser().parseFromString(`<div>${html || ""}</div>`, "text/html");
    const sec = { intro: [], responsibilities: [], requirements: [], offer: [] };
    let cur = "intro";
    const kind = (h) => {
      h = h.toLowerCase();
      if (/offer|benefit|package|we provide|perks|why join/.test(h)) return "offer";
      if (/require|qualif|skills|looking for|profile|ideal|you have|candidate|experience/.test(h)) return "requirements";
      if (/responsib|duties|role|you will|what you'?ll do|tasks|job description|day to day/.test(h)) return "responsibilities";
      return null;
    };
    for (const el of doc.body.firstChild.querySelectorAll("h1,h2,h3,h4,h5,p,li")) {
      const t = el.textContent.replace(/\s+/g, " ").trim();
      if (!t) continue;
      const isHeading = /^H\d$/.test(el.tagName) || (el.tagName === "P" && el.children.length === 1 && el.firstElementChild.tagName === "STRONG" && t.length < 60);
      if (isHeading) { const k = kind(t); if (k) { cur = k; continue; } }
      if (el.tagName === "LI") { (cur === "intro" ? sec.responsibilities : sec[cur]).push(t); }
      else if (el.closest("li") === null) {
        if (cur === "intro") sec.intro.push(t);
        else if (!/interested candidates|submit (your|their) cv|apply now/i.test(t)) sec[cur].push(t);
      }
    }
    if (!html && text) sec.intro = [text];
    return sec;
  }

  function salaryLabel(s) {
    if (!s) return "";
    const unit = { HOUR: "per hour", DAY: "per day", WEEK: "per week", MONTH: "per month", YEAR: "per year" }[s.unit] || "";
    const f = (v) => "€" + (+v).toLocaleString("en-GB", { maximumFractionDigits: v < 100 ? 2 : 0 });
    return `${s.min === s.max ? f(s.min) : f(s.min) + "–" + f(s.max)} ${unit}`.trim();
  }
  const bullets = (items, max = 5) => items.slice(0, max).map((i) => "• " + i.replace(/\s*[.;]$/, "")).join("\n");

  function hashtags(job, facts) {
    const cat = String(job.category || "").split("&")[0].trim();
    const tags = ["JobsInMalta", "MaltaJobs", "Hiring", camel(job.title), camel(cityOf(job, facts)) + "Jobs",
      cat && cat !== "General" ? camel(cat) + "Jobs" : "", "RecruitmentMalta", "WorkInMalta", "OutreachRecruitment"];
    return [...new Set(tags.filter((t) => t && t.length > 3))].map((t) => "#" + t).join(" ");
  }

  function fill(template, values) {
    // Drop a paragraph whose placeholders are all empty (e.g. no "What's on offer" section).
    return template.split(/\n{2,}/).map((block) => {
      const keys = [...block.matchAll(/\{(\w+)\}/g)].map((m) => m[1]);
      if (keys.length && keys.every((k) => !String(values[k] ?? "").trim())) return null;
      return block.replace(/\{(\w+)\}/g, (_, k) => values[k] ?? "");
    }).filter((b) => b !== null).join("\n\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  const reEsc = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const sentencesOf = (t) => String(t).replace(/\s+/g, " ").trim().match(/[^.!?]+[.!?]+/g) || (t ? [String(t)] : []);
  function variantFor(job, choices, offset = 0) {
    const seed = String(job.slug || job.title || "");
    let hash = (2166136261 + offset) >>> 0;
    for (const char of seed) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619) >>> 0;
    return choices[hash % choices.length];
  }
  function jobHook(job) {
    const title = job.title;
    return variantFor(job, [
      `Ready for your next move as a ${title}?`,
      `Could this ${title} role be your next opportunity?`,
      `Looking for a new opportunity? Explore this ${title} role.`,
    ]);
  }
  function applyPrompt(job) {
    return variantFor(job, [
      `Think this ${job.title} role could be right for you? Apply today.`,
      `Ready to take the next step? Apply for the ${job.title} role today.`,
      "Interested in this opportunity? Send your application today.",
    ], 17);
  }
  function jobHighlights(job, facts, salary) {
    const highlights = [];
    if (salary) highlights.push(`💶 ${salary}`);
    const workMode = String(facts?.work_mode || job.work_mode || "").trim();
    if (/hybrid|remote/i.test(workMode)) highlights.push(`🏠 ${workMode}`);
    const location = String(facts?.city || job.location || "").split(",")[0].trim();
    if (location) highlights.push(`📍 ${location}`);
    return highlights.slice(0, 2).join(" · ");
  }
  const SECTOR_CLIENT = {
    "Hospitality": "a well-established hospitality business in Malta", "Construction": "a leading construction company in Malta",
    "Marine & Shipping": "a respected marine company in Malta", "Finance & Accounting": "an established finance firm in Malta",
    "Insurance": "a well-known insurance company in Malta", "IT & Technology": "a growing technology company in Malta",
    "Customer Service": "an international company based in Malta", "Logistics": "an established logistics company in Malta",
    "Retail": "a well-known retail business in Malta", "Sales": "a growing company in Malta",
    "Wellness": "a premium wellness business in Malta", "Healthcare": "a respected healthcare provider in Malta",
  };

  // Build a concise, fact-based introduction from the role and careers-page description.
  function introText(job, facts, d) {
    const title = job.title, city = cityOf(job, facts);
    const intro = sentencesOf(d.intro.join(" "));
    const all = [...intro, ...sentencesOf(d.responsibilities.join(". "))];
    const first = intro[0] || "";

    let client = (first.match(/^our client,?\s+(.+?),\s+(?:is|are)\s+(?:currently\s+)?(?:looking|seeking|searching|hiring|recruiting)/i) || [])[1]
      || (d.intro.join(" ").match(/our client(?: is|,)\s+(an?\s+[^,.;]+)/i) || [])[1] || "";
    client = client.trim() || SECTOR_CLIENT[job.category] || "a well-established company in Malta";
    let qual = (first.match(new RegExp("(an?\\s+[^.,]{0,60}?)\\s*" + reEsc(title), "i")) || [])[1] || "";
    if (!qual || /our client/i.test(qual) || qual.split(" ").length > 8) qual = /^[aeiou]/i.test(title) ? "an" : "a";
    const where = city && !new RegExp(reEsc(city), "i").test(client) ? ` in ${city}` : "";
    const p1 = `**Outreach Recruitment** is recruiting on behalf of our client, ${client}, who is looking for ${qual.trim()} **${title}** to join their team${where}.`;

    const roleRaw = all.find((t) => /successful candidate|you will|will be responsible|responsible for|will assist|will support|will join/i.test(t) && t !== first);
    let roleDetail = roleRaw ? roleRaw.trim()
      .replace(/^the successful candidates? will be/i, "You'll be").replace(/^the successful candidates? will/i, "You'll")
      .replace(/^the (?:role|position) (?:will )?(?:involves?|includes?)/i, "You'll be").replace(/^you will/i, "You'll") : "";
    const responsibilities = [...all.filter((text) => text !== first && text !== roleRaw).flatMap(sentencesOf), ...d.responsibilities]
      .map((item) => item.replace(/[\s.;]+$/, "").trim())
      .filter((item, index, items) => items.findIndex((candidate) => candidate.toLowerCase() === item.toLowerCase()) === index)
      .filter((item) => !/interested candidates|submit (your|their) cv|apply now/i.test(item))
      .filter((item) => !roleDetail.toLowerCase().includes(item.toLowerCase()));
    if (responsibilities.length) {
      const extra = responsibilities.slice(0, roleDetail ? 3 : 3).join("; ");
      roleDetail = roleDetail
        ? `${roleDetail.replace(/\s*[.;]$/, "")} Other responsibilities include: ${extra}.`
        : `Key responsibilities include: ${extra}.`;
    }

    const p2 = roleDetail ? `🔎 **About this role:** ${roleDetail}` : "";
    const perks = d.offer.filter((o) => !/full[- ]time|salary|employment with|interested candidates/i.test(o)).slice(0, 2)
      .map((o) => o.replace(/\s*[.;]$/, ""));
    const p3 = perks.length ? `**What Our Client Offers**\n${bullets(perks, 2)}` : "";
    return [p1, p2, p3].filter(Boolean).join("\n\n");
  }

  function jobValues(job, facts) {
    const d = parseDescription(facts?.description_html, facts?.description_text);
    const salary = job.salary || salaryLabel(facts?.salary);
    const city = cityOf(job, facts);
    return {
      title: job.title, city, job_type: [facts?.employment_type || job.employment_type, facts?.work_mode || job.work_mode].filter(Boolean).join(" · "), salary,
      hook: jobHook(job), job_highlights: jobHighlights(job, facts, salary), apply_prompt: applyPrompt(job),
      intro: introText(job, facts, d), short_intro: firstSentences(d.intro.join(" ")),
      responsibilities: bullets(d.responsibilities), requirements: bullets(d.requirements), offer: bullets(d.offer, 4),
      apply_url: `${SITE}/jobs/${job.slug}/`, more_jobs_url: MORE_JOBS, hashtags: hashtags(job, facts),
      category: job.category || "",
    };
  }

  // ── data ──────────────────────────────────────────────────────────────────
  const cache = { jobs: null, newToday: [], reportDate: "", facts: {} };
  async function loadJobs() {
    if (cache.jobs) return;
    const reg = await (await fetch("../tools/jobs_registry.json?t=" + Date.now(), { cache: "no-store" })).json();
    const open = reg.filter((j) => !/closed|expired/i.test(j.status || ""));
    cache.jobs = open.sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
    try {
      const idx = await (await fetch("../reports/daily-sync/index.json?t=" + Date.now(), { cache: "no-store" })).json();
      const latest = idx[0]?.date;
      if (latest) {
        const rep = await (await fetch(`../reports/daily-sync/${latest}.json?t=` + Date.now(), { cache: "no-store" })).json();
        cache.reportDate = latest;
        cache.newToday = (rep.created || []).map((c) => c.slug).filter(Boolean);
      }
    } catch { /* no report yet */ }
  }
  async function factsFor(job) {
    const m = UUID_RE.exec(job.apply_url || "");
    if (!m) return null;
    if (!(m[0] in cache.facts)) {
      try { cache.facts[m[0]] = await (await fetch(`../tools/ats_snapshots/${m[0]}.json`)).json(); }
      catch { cache.facts[m[0]] = null; }
    }
    return cache.facts[m[0]];
  }

  // ── copy ──────────────────────────────────────────────────────────────────
  async function copyRich(text, btn, imgUrl = "") {
    const pic = imgUrl ? `<p style="margin:0 0 14px"><img src="${esc(imgUrl)}" alt="" style="max-width:100%;height:auto;border-radius:8px;display:block"></p>` : "";
    const html = pic ? toHTML(text).replace(/^(<div[^>]*>)/, `$1${pic}`) : toHTML(text), plain = toPlain(text);
    try {
      await navigator.clipboard.write([new ClipboardItem({ "text/html": new Blob([html], { type: "text/html" }), "text/plain": new Blob([plain], { type: "text/plain" }) })]);
    } catch {
      const div = Object.assign(document.createElement("div"), { innerHTML: html, contentEditable: "true" });
      div.style.cssText = "position:fixed;left:-9999px"; document.body.appendChild(div);
      const r = document.createRange(); r.selectNodeContents(div); const s = getSelection(); s.removeAllRanges(); s.addRange(r);
      document.execCommand("copy"); s.removeAllRanges(); div.remove();
    }
    flash(btn);
  }
  async function copyText(text, btn) {
    try { await navigator.clipboard.writeText(text); }
    catch { const ta = Object.assign(document.createElement("textarea"), { value: text }); document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove(); }
    flash(btn);
  }
  const flash = (btn) => { const t = btn.textContent; btn.textContent = "✓ Copied"; btn.disabled = true; setTimeout(() => { btn.textContent = t; btn.disabled = false; }, 1600); };

  // ── view ──────────────────────────────────────────────────────────────────
  let state = { tab: "job", slug: null, picks: [] };

  window.renderMarketing = async function (view) {
    view.innerHTML = `<div class="card"><p class="muted" style="margin:0">Loading open jobs…</p></div>`;
    try { await loadJobs(); }
    catch (e) { view.innerHTML = `<div class="card"><h2>Could not load the jobs</h2><p class="muted">${esc(e.message)}</p></div>`; return; }
    const jobs = cache.jobs, isNew = (s) => cache.newToday.includes(s);
    if (!state.slug) state.slug = cache.newToday[0] || jobs[0]?.slug;
    if (!state.picks.length) state.picks = jobs.slice(0, 6).map((j) => j.slug);

    view.innerHTML = `
      <section class="card hero">
        <div class="kicker">Marketing · Email Marketing</div>
        <h1>Job posts, ready to paste</h1>
        <p>Built from the careers-page description. Copy for your email tool (real bold) or for social media (𝗯𝗼𝗹𝗱 letters).</p>
      </section>

      <div class="tabs" role="tablist">
        <button class="tab ${state.tab === "job" ? "active" : ""}" data-tab="job" role="tab">Job post</button>
        <button class="tab ${state.tab === "picture" ? "active" : ""}" data-tab="picture" role="tab">Generate picture</button>
        <button class="tab ${state.tab === "generic" ? "active" : ""}" data-tab="generic" role="tab">Generic post</button>
        <button class="tab ${state.tab === "template" ? "active" : ""}" data-tab="template" role="tab">Templates</button>
      </div>
      <div id="mk-body"></div>`;
    $$(".tab", view).forEach((b) => (b.onclick = () => { state.tab = b.dataset.tab; window.renderMarketing(view); }));
    const body = $("#mk-body", view);

    if (state.tab === "template") return renderTemplates(body, view);

    if (state.tab === "picture") {
      const job = jobs.find((j) => j.slug === state.slug) || jobs[0];
      const facts = await factsFor(job);
      const details = jobValues(job, facts);
      const parsed = parseDescription(facts?.description_html, facts?.description_text);
      const requirements = [...new Set([...parsed.requirements, ...parsed.responsibilities])].slice(0, 5);
      body.innerHTML = `
        <section class="mk-layout">
          <div class="card">
            <h2>Choose a job</h2>
            <p class="muted small">The title, job details and 4–5 requirements update automatically.</p>
            <input id="mk-filter" placeholder="Search ${jobs.length} open jobs…" style="margin-bottom:8px">
            <div class="mk-picklist">${jobs.map((j) => `<button class="mk-job ${j.slug === job.slug ? "active" : ""}" data-slug="${esc(j.slug)}">
              <span>${esc(j.title)}</span><span class="muted small">${esc(String(j.location || "").split(",")[0])}${isNew(j.slug) ? " · New today" : ""}</span></button>`).join("")}</div>
          </div>
          ${pictureGeneratorCard(job, details, requirements)}
        </section>`;
      $$("[data-slug]", body).forEach((b) => (b.onclick = () => { state.slug = b.dataset.slug; window.renderMarketing(view); }));
      wireFilter(body);
      wirePictureGenerator(body, job, details, requirements);
      return;
    }

    if (state.tab === "generic") {
      const picked = state.picks.map((s) => jobs.find((j) => j.slug === s)).filter(Boolean);
      const list = picked.map((j) => `▶️ **${j.title}** — ${String(j.location || "").split(",")[0]}${j.salary ? ` · ${j.salary}` : ""}\n${SITE}/jobs/${j.slug}/`).join("\n\n");
      const text = fill(store.get(GEN_KEY) || DEFAULT_GENERIC, { job_list: list, count: jobs.length, more_jobs_url: MORE_JOBS });
      body.innerHTML = `
        <section class="mk-layout">
          <div class="card">
            <h2>Choose the jobs</h2>
            <p class="muted small">Tick up to 10 jobs for the round-up (newest first).</p>
            <input id="mk-filter" placeholder="Search jobs…" style="margin-bottom:8px">
            <div class="mk-picklist">${jobs.map((j) => `<label class="mk-pick"><input type="checkbox" value="${esc(j.slug)}" ${state.picks.includes(j.slug) ? "checked" : ""}>
              <span>${esc(j.title)} <span class="muted small">— ${esc(String(j.location || "").split(",")[0])}</span>${isNew(j.slug) ? ' <span class="status good">New today</span>' : ""}</span></label>`).join("")}</div>
          </div>
          ${previewCard(text, "the generic round-up")}
        </section>`;
      $$(".mk-pick input", body).forEach((cb) => (cb.onchange = () => {
        const set = new Set(state.picks); cb.checked ? set.add(cb.value) : set.delete(cb.value);
        state.picks = jobs.map((j) => j.slug).filter((s) => set.has(s)).slice(0, 10); window.renderMarketing(view);
      }));
      wireFilter(body); wirePreview(body, "generic");
      return;
    }

    // Job post
    const job = jobs.find((j) => j.slug === state.slug) || jobs[0];
    const facts = await factsFor(job);
    const text = fill(jobTemplate(), jobValues(job, facts));
    const todays = jobs.filter((j) => isNew(j.slug));
    body.innerHTML = `
      ${todays.length ? `<section class="card"><h2>🆕 Published today${cache.reportDate ? ` (${esc(cache.reportDate)})` : ""}</h2>
        <div class="mk-chips">${todays.map((j) => `<button class="chip-btn ${j.slug === job.slug ? "active" : ""}" data-slug="${esc(j.slug)}">${esc(j.title)}</button>`).join("")}</div></section>` : ""}
      <section class="mk-layout">
        <div class="card">
          <h2>Choose a job</h2>
          <input id="mk-filter" placeholder="Search ${jobs.length} open jobs…" style="margin-bottom:8px">
          <div class="mk-picklist">${jobs.map((j) => `<button class="mk-job ${j.slug === job.slug ? "active" : ""}" data-slug="${esc(j.slug)}">
            <span>${esc(j.title)}</span><span class="muted small">${esc(String(j.location || "").split(",")[0])}${isNew(j.slug) ? " · New today" : ""}</span></button>`).join("")}</div>
          <p class="small muted" style="margin-top:10px">Source: <a href="${esc((facts?.ats_url) || "#")}" target="_blank" rel="noopener">careers-page description</a>${facts ? "" : " (not available — basic post)"}
            · Website: <a href="${SITE}/jobs/${esc(job.slug)}/" target="_blank" rel="noopener">/jobs/${esc(job.slug)}/</a></p>
        </div>
        ${previewCard(text, job.title)}
      </section>`;
    $$("[data-slug]", body).forEach((b) => (b.onclick = () => { state.slug = b.dataset.slug; window.renderMarketing(view); }));
    wireFilter(body); wirePreview(body, job.slug);
  };

  function previewCard(text, pictureFor) {
    return `<div class="card mk-preview-card">
      <div class="section-title"><h2>Post</h2><span class="muted small">Edit below — the preview updates</span></div>
      <div class="mk-actions">
        <button class="btn primary" id="mk-copy-email">📧 Copy for email</button>
        <button class="btn" id="mk-copy-social">📱 Copy for social media</button>
      </div>
      <div class="mk-image-panel">
        <div class="section-title"><h3>🖼️ Picture for ${esc(pictureFor)}</h3><span class="muted small" id="mk-img-mode"></span></div>
        <div class="mk-actions">
          <label class="btn small" for="mk-upload">⬆️ Upload picture</label>
          <input type="file" id="mk-upload" accept="image/png,image/jpeg,image/webp,image/gif" multiple hidden>
          <button class="btn small" id="mk-img-copy" hidden>📋 Copy picture</button>
          <a class="btn small" id="mk-img-download" hidden download>⬇️ Download</a>
          <button class="btn small ghost" id="mk-img-none" hidden>No picture</button>
        </div>
        <div class="mk-library" id="mk-library"><span class="muted small">Loading your pictures…</span></div>
        <p class="small muted" id="mk-img-note" style="margin:6px 0 0"></p>
      </div>
      <div class="mk-preview" id="mk-preview"><div id="mk-preview-img"></div><div id="mk-preview-text">${toHTML(text)}</div></div>
      <details><summary class="small">Edit text (use **double stars** for bold)</summary>
        <textarea id="mk-text" rows="16" style="margin-top:8px;font-family:ui-monospace,Menlo,monospace;font-size:.85rem">${esc(text)}</textarea></details>
      <p class="small muted" style="margin:8px 0 0"><span id="mk-count">${toSocial(text).length}</span> characters · LinkedIn limit 3,000 · Instagram 2,200</p>
    </div>`;
  }

  function pictureGeneratorCard(job, details, requirements) {
    const savedFormat = store.get(FORMAT_KEY);
    const format = PICTURE_FORMATS[savedFormat] ? savedFormat : "square";
    const dimensions = PICTURE_FORMATS[format];
    return `<div class="card mk-picture-card">
      <div class="section-title"><div><h2>Social media picture</h2><p class="muted small" id="mk-gen-size" style="margin:3px 0 0">${esc(dimensions.label)} · ${dimensions.width} × ${dimensions.height} · fixed Outreach format</p></div></div>
      <div class="mk-format-picker" role="group" aria-label="Picture format">
        ${Object.entries(PICTURE_FORMATS).map(([key, item]) => `<button class="mk-format ${key === format ? "active" : ""}" data-format="${key}" type="button"><strong>${esc(item.label)}</strong><span>${item.width} × ${item.height}</span></button>`).join("")}
      </div>
      <div class="mk-actions">
        <label class="btn small" for="mk-gen-upload">⬆️ Add background</label>
        <input type="file" id="mk-gen-upload" accept="image/png,image/jpeg,image/webp" hidden>
        <button class="btn small" id="mk-gen-copy">📋 Copy picture</button>
        <button class="btn primary small" id="mk-gen-download">⬇️ Download PNG</button>
      </div>
      <div class="mk-gen-backgrounds" id="mk-gen-backgrounds"><span class="muted small">Loading job backgrounds…</span></div>
      <p class="small muted" id="mk-gen-note">The selected background is saved for ${esc(job.title)} only.</p>
      <div class="mk-canvas-wrap" data-format="${format}"><canvas id="mk-gen-canvas" width="${dimensions.width}" height="${dimensions.height}" aria-label="Generated social media post for ${esc(job.title)}"></canvas></div>
      ${requirements.length ? "" : `<p class="status warn">No detailed requirements were found, so the design will use the available role details.</p>`}
    </div>`;
  }

  const loadCanvasImage = (url) => new Promise((resolve, reject) => {
    const im = new Image();
    if (!url.startsWith("blob:")) im.crossOrigin = "anonymous";
    im.onload = () => resolve(im); im.onerror = () => reject(new Error("Could not load this image")); im.src = url;
  });
  const roundRect = (ctx, x, y, w, h, r) => {
    ctx.beginPath(); ctx.roundRect(x, y, w, h, r); return ctx;
  };
  function canvasLines(ctx, text, maxWidth, maxLines = 2) {
    const words = String(text).replace(/<[^>]*>/g, "").replace(/&amp;/g, "&").split(/\s+/).filter(Boolean), lines = [];
    let line = "";
    for (const word of words) {
      const next = line ? line + " " + word : word;
      if (ctx.measureText(next).width <= maxWidth || !line) line = next;
      else { lines.push(line); line = word; if (lines.length === maxLines - 1) break; }
    }
    if (line && lines.length < maxLines) lines.push(line);
    if (lines.length === maxLines && words.join(" ").length > lines.join(" ").length) {
      while (ctx.measureText(lines[maxLines - 1] + "…").width > maxWidth) lines[maxLines - 1] = lines[maxLines - 1].replace(/\s+\S*$/, "");
      lines[maxLines - 1] += "…";
    }
    return lines;
  }
  function fitCanvasFont(ctx, text, maxWidth, start, min, weight = 800) {
    let size = start;
    do { ctx.font = `${weight} ${size}px Arial, Helvetica, sans-serif`; size -= 2; } while (ctx.measureText(text).width > maxWidth && size >= min);
  }
  async function drawSquareArtwork(canvas, job, details, requirements, background) {
    const ctx = canvas.getContext("2d"), W = 1080, H = 1080;
    ctx.clearRect(0, 0, W, H);
    if (background) {
      const scale = Math.max(W / background.width, H / background.height), dw = background.width * scale, dh = background.height * scale;
      ctx.drawImage(background, (W - dw) / 2, (H - dh) / 2, dw, dh);
    } else { ctx.fillStyle = "#f4f0ee"; ctx.fillRect(0, 0, W, H); }
    const fade = ctx.createLinearGradient(0, 0, W, H);
    fade.addColorStop(0, "rgba(255,255,255,.98)"); fade.addColorStop(.62, "rgba(255,255,255,.92)"); fade.addColorStop(1, "rgba(255,255,255,.38)");
    ctx.fillStyle = fade; ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = "rgba(255,255,255,.93)"; roundRect(ctx, 44, 34, 992, 1012, 34).fill();
    try {
      const logo = await loadCanvasImage("../assets/outreach-recruitment-logo.svg");
      const lh = 74, lw = Math.min(360, logo.width * (lh / logo.height)); ctx.drawImage(logo, 58, 52, lw, lh);
    } catch { ctx.fillStyle = "#4527f5"; ctx.font = "900 45px Arial"; ctx.fillText("OUTREACH", 58, 108); }

    ctx.fillStyle = "#14121a"; ctx.font = "900 49px Arial, Helvetica, sans-serif"; ctx.fillText("WE ARE HIRING IN MALTA 🇲🇹", 58, 180);
    ctx.fillStyle = "#fb2427"; roundRect(ctx, 54, 206, 972, 104, 5).fill();
    ctx.fillStyle = "#fff"; fitCanvasFont(ctx, job.title.toUpperCase(), 900, 47, 27, 900);
    ctx.fillText(job.title.toUpperCase(), 84, 274);

    let y = 365;
    const reqs = requirements.slice(0, 5);
    ctx.font = "700 23px Arial, Helvetica, sans-serif";
    for (const requirement of reqs) {
      ctx.fillStyle = "#4727fa"; ctx.beginPath(); ctx.moveTo(72, y - 15); ctx.lineTo(100, y); ctx.lineTo(72, y + 15); ctx.lineTo(82, y); ctx.lineTo(61, y + 15); ctx.closePath(); ctx.fill();
      ctx.fillStyle = "#20202a";
      const lines = canvasLines(ctx, requirement.replace(/\s*[.;]$/, ""), 855, 2);
      lines.forEach((line, i) => ctx.fillText(line, 118, y + i * 28 + 8));
      y += lines.length > 1 ? 64 : 50;
    }

    const detailY = 755, purple = "#4727fa";
    const badges = [`📍 ${details.city}, Malta`, details.salary, details.job_type].filter(Boolean).slice(0, 3);
    badges.forEach((label, i) => {
      ctx.font = "800 25px Arial, Helvetica, sans-serif";
      const width = Math.min(900, ctx.measureText(label).width + 48);
      ctx.fillStyle = purple; roundRect(ctx, 58, detailY + i * 63, width, 50, 3).fill();
      ctx.fillStyle = "#fff"; ctx.fillText(label, 78, detailY + 34 + i * 63);
    });

    ctx.fillStyle = "#fb2427"; roundRect(ctx, 44, 968, 992, 78, 8).fill();
    ctx.fillStyle = "#fff"; ctx.font = "800 23px Arial, Helvetica, sans-serif"; ctx.fillText("More information: outreachrecruitment.net", 70, 1017);
    ctx.fillStyle = purple; roundRect(ctx, 770, 982, 238, 51, 28).fill();
    ctx.fillStyle = "#fff"; ctx.font = "italic 900 28px Arial, Helvetica, sans-serif"; ctx.fillText("APPLY NOW", 806, 1017);
  }
  function drawCover(ctx, image, width, height) {
    if (!image) { ctx.fillStyle = "#f4f0ee"; ctx.fillRect(0, 0, width, height); return; }
    const scale = Math.max(width / image.width, height / image.height), dw = image.width * scale, dh = image.height * scale;
    ctx.drawImage(image, (width - dw) / 2, (height - dh) / 2, dw, dh);
  }
  async function drawSocialPicture(canvas, job, details, requirements, background, format) {
    if (format === "square") return drawSquareArtwork(canvas, job, details, requirements, background);
    const artwork = document.createElement("canvas"); artwork.width = 1080; artwork.height = 1080;
    await drawSquareArtwork(artwork, job, details, requirements, background);
    const ctx = canvas.getContext("2d"), W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H); drawCover(ctx, background, W, H);
    if (format === "story") {
      ctx.fillStyle = "rgba(255,255,255,.22)"; ctx.fillRect(0, 0, W, H);
      ctx.drawImage(artwork, 0, 420, 1080, 1080);
      ctx.fillStyle = "rgba(255,255,255,.94)"; roundRect(ctx, 260, 1540, 560, 74, 37).fill();
      ctx.fillStyle = "#4727fa"; ctx.font = "italic 900 34px Arial, Helvetica, sans-serif"; ctx.textAlign = "center"; ctx.fillText("APPLY NOW", 540, 1589); ctx.textAlign = "left";
    } else {
      const gradient = ctx.createLinearGradient(0, 0, W, 0);
      gradient.addColorStop(0, "rgba(255,255,255,.99)"); gradient.addColorStop(.62, "rgba(255,255,255,.94)"); gradient.addColorStop(1, "rgba(255,255,255,.10)");
      ctx.fillStyle = gradient; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "rgba(255,255,255,.94)"; roundRect(ctx, 24, 22, 780, 583, 24).fill();
      try {
        const logo = await loadCanvasImage("../assets/outreach-recruitment-logo.svg");
        const lh = 48, lw = Math.min(260, logo.width * (lh / logo.height)); ctx.drawImage(logo, 48, 38, lw, lh);
      } catch { ctx.fillStyle = "#4527f5"; ctx.font = "900 32px Arial"; ctx.fillText("OUTREACH", 48, 76); }
      ctx.fillStyle = "#14121a"; ctx.font = "900 31px Arial, Helvetica, sans-serif"; ctx.fillText("WE ARE HIRING IN MALTA 🇲🇹", 48, 125);
      ctx.fillStyle = "#fb2427"; roundRect(ctx, 44, 146, 736, 72, 4).fill();
      ctx.fillStyle = "#fff"; fitCanvasFont(ctx, job.title.toUpperCase(), 680, 35, 22, 900); ctx.fillText(job.title.toUpperCase(), 70, 193);
      ctx.font = "700 18px Arial, Helvetica, sans-serif";
      let ly = 260;
      for (const requirement of requirements.slice(0, 5)) {
        ctx.fillStyle = "#4727fa"; ctx.beginPath(); ctx.moveTo(53, ly - 9); ctx.lineTo(72, ly); ctx.lineTo(53, ly + 9); ctx.lineTo(59, ly); ctx.lineTo(45, ly + 9); ctx.closePath(); ctx.fill();
        ctx.fillStyle = "#20202a"; const lines = canvasLines(ctx, requirement.replace(/\s*[.;]$/, ""), 675, 1); ctx.fillText(lines[0] || "", 88, ly + 6); ly += 43;
      }
      ctx.font = "800 17px Arial, Helvetica, sans-serif";
      const landscapeBadges = [`📍 ${details.city}, Malta`, details.salary, details.job_type].filter(Boolean);
      let bx = 46;
      landscapeBadges.forEach((label) => { const bw = Math.min(235, ctx.measureText(label).width + 28); ctx.fillStyle = "#4727fa"; roundRect(ctx, bx, 491, bw, 39, 3).fill(); ctx.fillStyle = "#fff"; ctx.fillText(label, bx + 13, 517); bx += bw + 9; });
      ctx.fillStyle = "#fb2427"; roundRect(ctx, 24, 548, 780, 57, 8).fill();
      ctx.fillStyle = "#fff"; ctx.font = "800 17px Arial, Helvetica, sans-serif"; ctx.fillText("More information: outreachrecruitment.net", 48, 583);
      ctx.fillStyle = "rgba(71,39,250,.96)"; roundRect(ctx, 858, 500, 292, 72, 36).fill();
      ctx.fillStyle = "#fff"; ctx.font = "italic 900 32px Arial, Helvetica, sans-serif"; ctx.textAlign = "center"; ctx.fillText("APPLY NOW", 1004, 547); ctx.textAlign = "left";
    }
  }
  function wirePictureGenerator(root, job, details, requirements) {
    const I = window.AdminImages, canvas = $("#mk-gen-canvas", root), note = $("#mk-gen-note", root), key = job.slug;
    let images = [], background = null, drawVersion = 0, format = PICTURE_FORMATS[store.get(FORMAT_KEY)] ? store.get(FORMAT_KEY) : "square";
    const isCurrent = () => canvas.isConnected && $("#mk-gen-canvas", root) === canvas;
    const draw = async () => {
      const version = ++drawVersion;
      let bitmap = null;
      try { if (background) bitmap = await loadCanvasImage(background.url); }
      catch (e) { if (isCurrent()) note.textContent = e.message + ". Choose another background."; }
      if (isCurrent() && version === drawVersion) await drawSocialPicture(canvas, job, details, requirements, bitmap, format);
    };
    const paintBackgrounds = () => {
      if (!isCurrent()) return;
      background = images.find((im) => im.id === I.pickFor(key)) || null;
      $("#mk-gen-backgrounds", root).innerHTML = images.length ? images.map((im) => `<button class="mk-gen-bg ${background?.id === im.id ? "active" : ""}" data-id="${esc(im.id)}" title="Use ${esc(im.name)} as the background"><img src="${esc(im.url)}" alt="${esc(im.name)}"></button>`).join("") : `<span class="muted small">Add the first background for this job.</span>`;
      $$(".mk-gen-bg", root).forEach((button) => (button.onclick = () => { I.setPick(key, button.dataset.id); paintBackgrounds(); }));
      note.textContent = background ? `Using “${background.name}” for ${job.title}.` : `Add or choose a background for ${job.title}.`;
      draw();
    };
    $("#mk-gen-upload", root).onchange = async (e) => {
      const file = e.target.files[0]; if (!file) return;
      note.textContent = "Saving the background…";
      try { const id = await I.add(file); images = await I.list(); if (!isCurrent()) return; I.setPick(key, id); paintBackgrounds(); }
      catch (err) { if (isCurrent()) note.textContent = "Could not save the background: " + (err.message || err); }
      e.target.value = "";
    };
    $$(".mk-format", root).forEach((button) => (button.onclick = () => {
      format = button.dataset.format;
      const dimensions = PICTURE_FORMATS[format];
      store.set(FORMAT_KEY, format); canvas.width = dimensions.width; canvas.height = dimensions.height;
      $(".mk-canvas-wrap", root).dataset.format = format;
      $("#mk-gen-size", root).textContent = `${dimensions.label} · ${dimensions.width} × ${dimensions.height} · fixed Outreach format`;
      $$(".mk-format", root).forEach((item) => item.classList.toggle("active", item === button));
      draw();
    }));
    $("#mk-gen-download", root).onclick = () => {
      const a = Object.assign(document.createElement("a"), { download: `${job.slug}-${format}.png`, href: canvas.toDataURL("image/png") }); a.click();
    };
    $("#mk-gen-copy", root).onclick = async (e) => {
      try { const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png")); await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]); flash(e.currentTarget); }
      catch { alert("Your browser blocked copying the picture — use Download PNG instead."); }
    };
    (async () => { try { await I.init(); images = await I.list(); } catch (err) { note.textContent = "Picture library unavailable: " + (err.message || err); } paintBackgrounds(); })();
  }
  function wirePreview(root, key) {
    const ta = $("#mk-text", root), pv = $("#mk-preview-text", root), cnt = $("#mk-count", root);
    const I = window.AdminImages;
    let images = [], current = null;
    // The body element is reused when another job is selected. Ignore a previous job's
    // image request if it finishes after its preview has already been replaced.
    const isCurrentPreview = () => ta.isConnected && $("#mk-text", root) === ta;
    ta.oninput = () => { pv.innerHTML = toHTML(ta.value); cnt.textContent = toSocial(ta.value).length; };
    $("#mk-copy-email", root).onclick = (e) => copyRich(ta.value, e.currentTarget, current?.online ? current.url : "");
    $("#mk-copy-social", root).onclick = (e) => copyText(toSocial(ta.value), e.currentTarget);

    const paint = () => {
      if (!isCurrentPreview()) return;
      current = images.find((im) => im.id === I.postPickFor(key)) || null;
      const postPicks = I.postPicks();
      const availableImages = images.filter((im) => !Object.entries(postPicks).some(([jobKey, id]) => jobKey !== key && id === im.id));
      $("#mk-library", root).innerHTML = availableImages.length
        ? availableImages.map((im) => `<div class="mk-thumb ${current?.id === im.id ? "active" : ""}">
            <button class="mk-thumb-pick" data-id="${esc(im.id)}" title="Use this picture"><img src="${esc(im.url)}" alt="${esc(im.name)}" loading="lazy"></button>
            <button class="mk-thumb-del" data-del="${esc(im.id)}" aria-label="Delete ${esc(im.name)}">✕</button></div>`).join("")
        : `<span class="muted small">${images.length ? "No pictures available for this job yet — upload one here." : "No pictures yet — upload one for this job."}</span>`;
      $("#mk-preview-img", root).innerHTML = current ? `<img src="${esc(current.url)}" alt="" class="mk-preview-pic">` : "";
      for (const id of ["#mk-img-copy", "#mk-img-download", "#mk-img-none"]) $(id, root).hidden = !current;
      if (current) { const a = $("#mk-img-download", root); a.href = current.url; a.download = current.name || "picture"; }
      $("#mk-img-mode", root).textContent = I.mode === "online" ? "Saved online" : "Saved in this browser";
      $("#mk-img-note", root).textContent = current && !current.online
        ? "This picture is saved in this browser, so it is not included in “Copy for email” — use Copy picture or Download, then add it in your email tool."
          + (window.AdminStore?.mode === "supabase" ? " To save pictures online, run supabase/marketing_storage.sql once in Supabase → SQL Editor." : "")
        : current ? "This picture belongs to this job and is included at the top of “Copy for email”." : "No picture is assigned to this job. Its post will show without an image until you upload or choose one here.";
      $$(".mk-thumb-pick", root).forEach((b) => (b.onclick = () => { I.setPostPick(key, b.dataset.id); paint(); }));
      $$(".mk-thumb-del", root).forEach((b) => (b.onclick = async () => {
        if (!confirm("Delete this picture from your library?")) return;
        try { await I.remove(b.dataset.del); images = await I.list(); paint(); } catch (e) { alert("Could not delete: " + (e.message || e)); }
      }));
    };
    $("#mk-upload", root).onchange = async (e) => {
      const files = [...e.target.files]; if (!files.length) return;
      $("#mk-img-note", root).textContent = `Saving ${files.length} picture(s)…`;
      try {
        let last = null;
        for (const f of files) last = await I.add(f);
        images = await I.list();
        if (!isCurrentPreview()) return;
        I.setPostPick(key, last); paint();
      } catch (err) {
        if (isCurrentPreview()) $("#mk-img-note", root).textContent = "Could not save the picture: " + (err.message || err);
      }
      e.target.value = "";
    };
    $("#mk-img-none", root).onclick = () => { I.setPostPick(key, null); paint(); };
    $("#mk-img-copy", root).onclick = async (e) => {
      try { await navigator.clipboard.write([new ClipboardItem({ "image/png": I.pngBlob(current.url) })]); flash(e.currentTarget); }
      catch (err) { alert("Your browser blocked copying the picture — use Download instead."); }
    };
    (async () => {
      try { await I.init(); images = await I.list(); } catch (err) { I.note = "Picture library unavailable: " + (err.message || err); }
      paint();
    })();
  }
  function wireFilter(root) {
    const f = $("#mk-filter", root);
    if (f) f.oninput = () => { const q = f.value.toLowerCase(); $$(".mk-job, .mk-pick", root).forEach((el) => (el.hidden = !el.textContent.toLowerCase().includes(q))); };
  }

  function renderTemplates(body, view) {
    const ph = (list) => list.map((p) => `<code>{${p}}</code>`).join(" ");
    body.innerHTML = `
      <section class="grid-2">
        <div class="card"><h2>Job post template</h2>
          <p class="small muted">Placeholders: ${ph(["title", "city", "job_type", "salary", "hook", "job_highlights", "intro", "apply_prompt", "short_intro", "responsibilities", "requirements", "offer", "apply_url", "more_jobs_url", "hashtags", "category"])}.
            A paragraph whose placeholders are all empty is left out. <code>**text**</code> = bold.</p>
          <textarea id="tpl-job" rows="22" style="font-family:ui-monospace,Menlo,monospace;font-size:.85rem">${esc(jobTemplate())}</textarea>
          <div class="form-actions"><button class="btn primary" id="tpl-job-save">Save</button><button class="btn" id="tpl-job-reset">Reset to default</button></div></div>
        <div class="card"><h2>Generic post template</h2>
          <p class="small muted">Placeholders: ${ph(["job_list", "count", "more_jobs_url"])}.</p>
          <textarea id="tpl-gen" rows="22" style="font-family:ui-monospace,Menlo,monospace;font-size:.85rem">${esc(store.get(GEN_KEY) || DEFAULT_GENERIC)}</textarea>
          <div class="form-actions"><button class="btn primary" id="tpl-gen-save">Save</button><button class="btn" id="tpl-gen-reset">Reset to default</button></div></div>
      </section>`;
    const saved = (btn) => { const t = btn.textContent; btn.textContent = "✓ Saved"; setTimeout(() => (btn.textContent = t), 1400); };
    $("#tpl-job-save", body).onclick = (e) => { store.set(TPL_KEY, $("#tpl-job", body).value); saved(e.currentTarget); };
    $("#tpl-gen-save", body).onclick = (e) => { store.set(GEN_KEY, $("#tpl-gen", body).value); saved(e.currentTarget); };
    $("#tpl-job-reset", body).onclick = () => { try { localStorage.removeItem(TPL_KEY); } catch {} renderTemplates(body, view); };
    $("#tpl-gen-reset", body).onclick = () => { try { localStorage.removeItem(GEN_KEY); } catch {} renderTemplates(body, view); };
  }

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  // Shared with social.js
  window.MarketingKit = { toSocial, toHTML, toPlain, copyRich, copyText, camel, esc,
    // Values for one job's post (intro, salary, apply link, hashtags…) — used by Social › Job of the day
    jobValues: async (job) => jobValues(job, await factsFor(job)) };
})();
