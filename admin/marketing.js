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
  const TPL_KEY = "admin:marketing-template", GEN_KEY = "admin:marketing-generic-template";
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const store = { get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
                  set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };

  const DEFAULT_TEMPLATE = `🚨 **WE'RE HIRING: {title}** 🚨

📍 **Location:** {city}, Malta
🕒 **Job type:** {job_type}
💶 **Salary:** {salary}

{intro}

✅ **What you'll do**
{responsibilities}

🎯 **What we're looking for**
{requirements}

🎁 **What's on offer**
{offer}

🌐 **Apply now:** {apply_url}
💼 **More Jobs:** {more_jobs_url}

{hashtags}`;

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

  function jobValues(job, facts) {
    const d = parseDescription(facts?.description_html, facts?.description_text);
    const salary = job.salary || salaryLabel(facts?.salary) || "Competitive salary";
    const type = [facts?.employment_type || job.employment_type || "Full-time", facts?.work_mode || job.work_mode || "On-site"]
      .filter(Boolean).join(" · ");
    return {
      title: job.title, city: cityOf(job, facts), job_type: type, salary,
      intro: firstSentences(d.intro.join(" ")),
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
  async function copyRich(text, btn) {
    const html = toHTML(text), plain = toPlain(text);
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
        <button class="tab ${state.tab === "generic" ? "active" : ""}" data-tab="generic" role="tab">Generic post</button>
        <button class="tab ${state.tab === "template" ? "active" : ""}" data-tab="template" role="tab">Templates</button>
      </div>
      <div id="mk-body"></div>`;
    $$(".tab", view).forEach((b) => (b.onclick = () => { state.tab = b.dataset.tab; window.renderMarketing(view); }));
    const body = $("#mk-body", view);

    if (state.tab === "template") return renderTemplates(body, view);

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
          ${previewCard(text)}
        </section>`;
      $$(".mk-pick input", body).forEach((cb) => (cb.onchange = () => {
        const set = new Set(state.picks); cb.checked ? set.add(cb.value) : set.delete(cb.value);
        state.picks = jobs.map((j) => j.slug).filter((s) => set.has(s)).slice(0, 10); window.renderMarketing(view);
      }));
      wireFilter(body); wirePreview(body);
      return;
    }

    // Job post
    const job = jobs.find((j) => j.slug === state.slug) || jobs[0];
    const facts = await factsFor(job);
    const text = fill(store.get(TPL_KEY) || DEFAULT_TEMPLATE, jobValues(job, facts));
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
        ${previewCard(text)}
      </section>`;
    $$("[data-slug]", body).forEach((b) => (b.onclick = () => { state.slug = b.dataset.slug; window.renderMarketing(view); }));
    wireFilter(body); wirePreview(body);
  };

  function previewCard(text) {
    return `<div class="card mk-preview-card">
      <div class="section-title"><h2>Post</h2><span class="muted small">Edit below — the preview updates</span></div>
      <div class="mk-actions">
        <button class="btn primary" id="mk-copy-email">📧 Copy for email</button>
        <button class="btn" id="mk-copy-social">📱 Copy for social media</button>
      </div>
      <div class="mk-preview" id="mk-preview">${toHTML(text)}</div>
      <details><summary class="small">Edit text (use **double stars** for bold)</summary>
        <textarea id="mk-text" rows="16" style="margin-top:8px;font-family:ui-monospace,Menlo,monospace;font-size:.85rem">${esc(text)}</textarea></details>
      <p class="small muted" style="margin:8px 0 0"><span id="mk-count">${toSocial(text).length}</span> characters · LinkedIn limit 3,000 · Instagram 2,200</p>
    </div>`;
  }
  function wirePreview(root) {
    const ta = $("#mk-text", root), pv = $("#mk-preview", root), cnt = $("#mk-count", root);
    ta.oninput = () => { pv.innerHTML = toHTML(ta.value); cnt.textContent = toSocial(ta.value).length; };
    $("#mk-copy-email", root).onclick = (e) => copyRich(ta.value, e.currentTarget);
    $("#mk-copy-social", root).onclick = (e) => copyText(toSocial(ta.value), e.currentTarget);
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
          <p class="small muted">Placeholders: ${ph(["title", "city", "job_type", "salary", "intro", "responsibilities", "requirements", "offer", "apply_url", "more_jobs_url", "hashtags", "category"])}.
            A paragraph whose placeholders are all empty is left out. <code>**text**</code> = bold.</p>
          <textarea id="tpl-job" rows="22" style="font-family:ui-monospace,Menlo,monospace;font-size:.85rem">${esc(store.get(TPL_KEY) || DEFAULT_TEMPLATE)}</textarea>
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
})();
