/* Outreach Admin — Help Center: inbox (notes, reply templates, client flag), dashboard,
   missed searches and the questions published on /help-center (Supabase help_faqs). */
(() => {
  "use strict";
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const when = (v) => v ? new Date(v).toLocaleString("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";
  const STATUS = { new: "New", in_progress: "In progress", answered: "Answered", closed: "Closed" };
  const TEAM = ["Nikolai Calleja", "Andrea Zambrano", "Katherin", "Jeraldin Daniela Bohorquez", "Julián Longan Granados", "Soufiane Barakat"];
  const TOPIC_OWNER = { Hire: "Andrea Zambrano", "Study in Malta": "Jeraldin Daniela Bohorquez", "Jobs in Malta": "Julián Longan Granados", General: "Katherin" };
  const CAT = { "jobs-in-malta": "Jobs in Malta", hire: "Hire", "study-in-malta": "Study in Malta" };
  const TOPIC_CAT = { "Jobs in Malta": "jobs-in-malta", Hire: "hire", "Study in Malta": "study-in-malta", General: "jobs-in-malta" };
  const DEFAULT_TEMPLATES = [
    { name: "How to apply", body: "Thank you for your interest in working in Malta.\n\nYou can see every open position and apply online here: https://outreachrecruitment.net/jobs/\nOpen the job that matches your experience, read the requirements and click Apply. Our team reviews every application and contacts shortlisted candidates." },
    { name: "Work permit", body: "Thank you for your question about work permits.\n\nIf you are not an EU citizen, your future employer applies for a Single Permit with Identità once you have a job offer. You can read the official information here: https://identita.gov.mt/expatriates-unit-main-page/noneu-nationals/employment-related-permits/single-permit/\nPlease note that many of our current vacancies are only open to candidates who already live in Malta." },
    { name: "Study visa", body: "Thank you for your interest in studying in Malta.\n\nOur Study in Malta guide explains courses, costs and the visa process: https://outreachrecruitment.net/study-in-malta\nA study advisor will contact you to understand your plans and suggest the right options." },
    { name: "Hire — we will call you", body: "Thank you for contacting Outreach Recruitment.\n\nWe would be happy to help you hire. A member of our team will contact you shortly to understand the roles, timing and requirements. You can also read about our services here: https://outreachrecruitment.net/employers" },
    { name: "Residents only", body: "Thank you for your message.\n\nAt the moment our vacancies are only open to candidates who currently live in Malta. We recommend subscribing to our job alerts so we can let you know when a suitable role opens." },
  ];
  const csvCell = (v) => { const s = String(v ?? ""); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const slugify = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80);
  let rows = [], templates = DEFAULT_TEMPLATES, sb = null, tab = "inbox";

  async function loadTemplates() {
    const { data } = await sb.from("seo_settings").select("value").eq("key", "help_reply_templates").maybeSingle();
    if (data && Array.isArray(data.value) && data.value.length) templates = data.value;
  }
  async function saveTemplates() {
    const { error } = await sb.from("seo_settings").upsert({ key: "help_reply_templates", value: templates, updated_at: new Date().toISOString() });
    if (error) alert(`Could not save the templates: ${error.message}`);
  }
  const mailto = (r, text) => `mailto:${encodeURIComponent(r.email)}?subject=${encodeURIComponent("Your request to Outreach Recruitment")}&body=${encodeURIComponent(`Hi ${String(r.full_name).split(" ")[0]},\n\n${text}\n\nKind regards,\n${r.assigned_to || "Outreach Recruitment"}\nOutreach Recruitment`)}`;

  window.refreshHireInboxCount = async function () {
    const store = window.AdminStore;
    const badge = document.querySelector("#hire-inbox-count");
    if (!badge || !store || store.mode !== "supabase" || !store.sb) return;
    const { count, error } = await store.sb.from("help_requests").select("id", { count: "exact", head: true }).eq("topic", "Hire").eq("status", "new");
    if (error) return;
    const total = count || 0;
    badge.textContent = String(total);
    badge.setAttribute("aria-label", `${total} new Hire ${total === 1 ? "enquiry" : "enquiries"}`);
  };

  window.renderHelpdesk = async function (view, topicFilter = "") {
    if (topicFilter) tab = "inbox";
    view.innerHTML = `<section class="card hero"><div class="kicker">Support · Help Center</div><h1>Help Center</h1><p>Loading…</p></section>`;
    const store = window.AdminStore;
    if (!store || store.mode !== "supabase" || !store.sb) {
      view.innerHTML += `<section class="card"><h2>Online database required</h2><p class="msg error">Sign in to the connected admin database to use the Help Center inbox.</p></section>`; return;
    }
    sb = store.sb;
    const { data, error } = await sb.from("help_requests").select("*").order("created_at", { ascending: false }).limit(2000);
    if (error) {
      view.innerHTML = `<section class="card hero"><div class="kicker">Support · Help Center</div><h1>Help Center</h1></section><section class="card"><h2>Help Center inbox not set up yet</h2><p class="msg error">${esc(error.message)}</p>
        <p>Run <code>supabase/migrations/20261118150000_help_center_requests_v2.sql</code> and then <code>20261118180000_help_center_v3.sql</code> in the Supabase SQL Editor, then reload this page.</p></section>`;
      return;
    }
    rows = data || [];
    const hireCount = rows.filter((r) => r.topic === "Hire" && r.status === "new").length;
    const hireBadge = document.querySelector("#hire-inbox-count");
    if (hireBadge) {
      hireBadge.textContent = String(hireCount);
      hireBadge.setAttribute("aria-label", `${hireCount} new Hire ${hireCount === 1 ? "enquiry" : "enquiries"}`);
    }
    await loadTemplates();
    const newCount = rows.filter((r) => r.status === "new").length;
    view.innerHTML = `<section class="card hero"><div class="kicker">Support · Help Center</div><h1>Help Center</h1>
      <p>Requests from the Help Center pop-up. Reply by email, keep notes, and turn common questions into Help Center articles.</p>
      <div class="hd-tabs" role="tablist">${[["inbox", `Inbox${newCount ? ` (${newCount} new)` : ""}`], ["insights", "Dashboard"], ["faqs", "Help Center questions"], ["misses", "Searches with no results"], ["templates", "Reply templates"]]
        .map(([k, l]) => `<button type="button" role="tab" data-tab="${k}" class="${tab === k ? "on" : ""}">${l}</button>`).join("")}</div></section>
      <section id="hd-panel"></section>`;
    view.querySelectorAll("[data-tab]").forEach((b) => b.addEventListener("click", () => { tab = b.dataset.tab; window.renderHelpdesk(view); }));
    const panel = view.querySelector("#hd-panel");
    ({ inbox: inbox, insights: insights, faqs: faqsTab, misses: missesTab, templates: templatesTab })[tab](panel, view, topicFilter);
  };

  /* ---------------- Inbox ---------------- */
  function inbox(panel, view, topicFilter = "") {
    const count = (s) => rows.filter((r) => r.status === s).length;
    panel.innerHTML = `<section class="subscriber-stats"><div class="card"><span>New</span><strong>${count("new")}</strong></div><div class="card"><span>In progress</span><strong>${count("in_progress")}</strong></div>
        <div class="card"><span>Answered</span><strong>${count("answered")}</strong></div><div class="card"><span>Total</span><strong>${rows.length}</strong></div></section>
      <section class="card"><div class="subscriber-toolbar">
        <input type="search" id="hd-q" placeholder="Search name, email, phone, company, question…">
        <select id="hd-status"><option value="">All statuses</option>${Object.entries(STATUS).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
        <select id="hd-topic"><option value="">All topics</option><option>Jobs in Malta</option><option>Hire</option><option>Study in Malta</option><option>General</option><option value="fraud">Fraud reports</option></select>
        <button class="btn" type="button" id="hd-csv">Download CSV</button></div><div id="hd-list"></div></section>`;
    const list = panel.querySelector("#hd-list"), q = panel.querySelector("#hd-q"), st = panel.querySelector("#hd-status"), tp = panel.querySelector("#hd-topic");
    if (topicFilter) tp.value = topicFilter;
    const filtered = () => {
      const s = q.value.trim().toLowerCase();
      return rows.filter((r) => (!st.value || r.status === st.value) && (!tp.value || (tp.value === "fraud" ? (r.details || {}).type === "fraud_report" : r.topic === tp.value)) &&
        (!s || [r.full_name, r.email, r.phone, r.company, r.message, r.job_title, r.nationality, r.current_location, r.admin_notes].join(" ").toLowerCase().includes(s)));
    };
    const overdue = (r) => r.status === "new" && Date.now() - new Date(r.created_at) > 24 * 3600e3;
    function draw() {
      const items = filtered();
      list.innerHTML = items.length ? items.map((r) => {
        const d = r.details || {};
        const facts = [["Phone", r.phone ? `<a href="tel:${esc(String(r.phone).replace(/\s/g, ""))}">${esc(r.phone)}</a>` : ""], ["Company", esc(r.company)],
          ["Current location", esc(r.current_location)], ["Nationality", esc(r.nationality)], ["Job", esc(r.job_title)],
          ["Wants to study", esc(d.study_level)], ["Start", esc(d.start_when)], ["Contacted via", esc(d.channel)], ["Name / number used", esc(d.sender)]]
          .filter(([k, v]) => v && !(d.type === "fraud_report" && ["Current location", "Nationality", "Job"].includes(k)));
        return `<article class="hd-item ${r.status}${overdue(r) ? " overdue" : ""}" data-id="${r.id}">
        <header><div><strong>${esc(r.full_name)}</strong> ${(r.details || {}).type === "fraud_report" ? '<span class="hd-topic hd-fraud">⚠️ Fraud report</span>' : `<span class="hd-topic">${esc(r.topic)}</span>`}${overdue(r) ? ' <span class="hd-late">Waiting over 24 h</span>' : ""}${r.converted ? ' <span class="hd-client">Client</span>' : ""}${(r.details || {}).auto_reply === "abroad" ? ' <span class="hd-late" style="background:#eef0f5;color:#475069">Auto-replied – abroad</span>' : ""}<br>
          <a href="${mailto(r, "")}">${esc(r.email)}</a></div><div class="hd-meta">${when(r.created_at)}${r.answered_at ? `<br>Answered ${when(r.answered_at)}` : ""}</div></header>
        <dl>${facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join("")}</dl>
        ${r.message ? `<p class="hd-msg">${esc(r.message)}</p>` : ""}
        <label class="hd-notes">Internal notes <span class="muted small">(only visible to the team)</span><textarea rows="2" data-notes>${esc(r.admin_notes || "")}</textarea></label>
        <footer>
          <select data-set="status">${Object.entries(STATUS).map(([k, v]) => `<option value="${k}" ${r.status === k ? "selected" : ""}>${v}</option>`).join("")}</select>
          <select data-set="assigned_to"><option value="">Assign to…</option>${TEAM.map((t) => `<option ${(r.assigned_to || "") === t ? "selected" : ""}>${t}</option>`).join("")}</select>
          <select data-reply><option value="">Reply with template…</option>${templates.map((t, i) => `<option value="${i}">${esc(t.name)}</option>`).join("")}</select>
          <a class="btn primary" href="${mailto(r, "")}">Reply by email</a>
          ${r.topic === "Hire" ? `<label class="hd-conv"><input type="checkbox" data-converted ${r.converted ? "checked" : ""}> Became a client</label>` : ""}
          <button class="btn" type="button" data-faq>Turn into Help Center article</button>
          <button class="btn" type="button" data-save-notes hidden>Save notes</button>
        </footer></article>`;
      }).join("") : `<div class="empty">No requests match these filters.</div>`;
    }
    async function update(id, patch) {
      const { error } = await sb.from("help_requests").update(patch).eq("id", id);
      if (error) { alert(`Could not update: ${error.message}`); return false; }
      Object.assign(rows.find((x) => x.id === id) || {}, patch);
      window.refreshHireInboxCount();
      return true;
    }
    [q, st, tp].forEach((el) => el.addEventListener("input", draw));
    list.addEventListener("change", async (e) => {
      const item = e.target.closest(".hd-item"); if (!item) return;
      const id = item.dataset.id, r = rows.find((x) => x.id === id);
      if (e.target.matches("[data-set]")) {
        const field = e.target.dataset.set;
        const patch = { [field]: e.target.value || null };
        if (field === "status" && ["answered", "closed"].includes(e.target.value) && !r.answered_at) patch.answered_at = new Date().toISOString();
        if (await update(id, patch)) draw();
      } else if (e.target.matches("[data-reply]")) {
        const t = templates[+e.target.value]; e.target.value = ""; if (!t) return;
        location.href = mailto(r, t.body);
        if (r.status === "new") { await update(id, { status: "in_progress" }); draw(); }
      } else if (e.target.matches("[data-converted]")) {
        await update(id, { converted: e.target.checked }); draw();
      }
    });
    list.addEventListener("input", (e) => { if (e.target.matches("[data-notes]")) e.target.closest(".hd-item").querySelector("[data-save-notes]").hidden = false; });
    list.addEventListener("click", async (e) => {
      const item = e.target.closest(".hd-item"); if (!item) return;
      const r = rows.find((x) => x.id === item.dataset.id);
      if (e.target.matches("[data-save-notes]")) {
        if (await update(r.id, { admin_notes: item.querySelector("[data-notes]").value.trim() || null })) { e.target.hidden = true; e.target.textContent = "Save notes"; }
      } else if (e.target.matches("[data-faq]")) {
        faqEditor(view, { category: TOPIC_CAT[r.topic] || "jobs-in-malta", question: r.message ? r.message.split("\n")[0].slice(0, 160) : "", answer: "", source_request_id: r.id, status: "draft", author_name: r.assigned_to || TOPIC_OWNER[r.topic] || "" });
      }
    });
    panel.querySelector("#hd-csv").addEventListener("click", () => {
      const f = ["created_at", "topic", "full_name", "email", "phone", "company", "current_location", "nationality", "job_title", "study_level", "start_when", "message", "status", "assigned_to", "converted", "answered_at", "admin_notes", "page_url"];
      const csv = [f.join(","), ...filtered().map((r) => f.map((k) => csvCell(r[k] ?? (r.details || {})[k])).join(","))].join("\n");
      const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
      a.download = `help-center-requests-${new Date().toISOString().slice(0, 10)}.csv`; a.click(); URL.revokeObjectURL(a.href);
    });
    draw();
  }

  /* ---------------- Dashboard ---------------- */
  function insights(panel) {
    const weeks = [];
    const monday = (d) => { const x = new Date(d); x.setHours(0, 0, 0, 0); x.setDate(x.getDate() - ((x.getDay() + 6) % 7)); return x; };
    for (let i = 7; i >= 0; i--) { const m = monday(Date.now()); m.setDate(m.getDate() - 7 * i); weeks.push(m); }
    const topics = ["Jobs in Malta", "Hire", "Study in Malta", "General"];
    const per = weeks.map((w) => { const end = new Date(w); end.setDate(end.getDate() + 7); const inW = rows.filter((r) => new Date(r.created_at) >= w && new Date(r.created_at) < end);
      return { w, total: inW.length, by: Object.fromEntries(topics.map((t) => [t, inW.filter((r) => r.topic === t).length])) }; });
    const max = Math.max(1, ...per.map((p) => p.total));
    const top = (field) => Object.entries(rows.reduce((m, r) => { if (r[field]) m[r[field]] = (m[r[field]] || 0) + 1; return m; }, {})).sort((a, b) => b[1] - a[1]).slice(0, 8);
    const answered = rows.filter((r) => r.answered_at);
    const avgH = answered.length ? answered.reduce((s, r) => s + (new Date(r.answered_at) - new Date(r.created_at)), 0) / answered.length / 3600e3 : null;
    const hire = rows.filter((r) => r.topic === "Hire"), conv = hire.filter((r) => r.converted).length;
    const colors = { "Jobs in Malta": "#442DFA", Hire: "#0f766e", "Study in Malta": "#b45309", General: "#6b7280" };
    panel.innerHTML = `<section class="subscriber-stats"><div class="card"><span>Requests (last 8 weeks)</span><strong>${per.reduce((s, p) => s + p.total, 0)}</strong></div>
        <div class="card"><span>Average reply time</span><strong>${avgH == null ? "—" : avgH < 48 ? `${avgH.toFixed(1)} h` : `${(avgH / 24).toFixed(1)} days`}</strong></div>
        <div class="card"><span>Hire requests → clients</span><strong>${conv} / ${hire.length}</strong></div>
        <div class="card"><span>Waiting over 24 h</span><strong>${rows.filter((r) => r.status === "new" && Date.now() - new Date(r.created_at) > 864e5).length}</strong></div></section>
      <section class="card"><h2>Requests per week by topic</h2>
        <div class="hd-legend">${topics.map((t) => `<span><i style="background:${colors[t]}"></i>${t}</span>`).join("")}</div>
        <div class="hd-bars">${per.map((p) => `<div class="hd-bar" title="${p.total} requests"><div class="hd-stack" style="height:${(p.total / max) * 160}px">${topics.map((t) => p.by[t] ? `<i style="flex:${p.by[t]};background:${colors[t]}"></i>` : "").join("")}</div>
          <b>${p.total}</b><small>${p.w.toLocaleDateString("en-GB", { day: "numeric", month: "short" })}</small></div>`).join("")}</div></section>
      <div class="hd-two"><section class="card"><h2>Top nationalities</h2>${tableOf(top("nationality"))}</section><section class="card"><h2>Top current locations</h2>${tableOf(top("current_location"))}</section></div>`;
  }
  const tableOf = (pairs) => pairs.length ? `<table><tbody>${pairs.map(([k, n]) => `<tr><td>${esc(k)}</td><td style="text-align:right"><b>${n}</b></td></tr>`).join("")}</tbody></table>` : `<p class="muted">No data yet.</p>`;

  /* ---------------- Help Center questions (help_faqs) ---------------- */
  async function faqsTab(panel, view) {
    panel.innerHTML = `<section class="card"><p class="muted">Loading…</p></section>`;
    const { data, error } = await sb.from("help_faqs").select("*").order("updated_at", { ascending: false });
    if (error) { panel.innerHTML = `<section class="card"><h2>Not set up yet</h2><p class="msg error">${esc(error.message)}</p><p>Run <code>supabase/migrations/20261118180000_help_center_v3.sql</code> in the Supabase SQL Editor.</p></section>`; return; }
    panel.innerHTML = `<section class="card"><div class="row" style="justify-content:space-between;align-items:center"><div><h2>Help Center questions</h2>
      <p class="muted small">Published questions replace the placeholder questions of their category on /help-center. The website updates automatically within about an hour.</p></div>
      <button class="btn primary" type="button" id="hd-new-faq">Add question</button></div>
      ${(data || []).length ? `<div class="table-wrap"><table><thead><tr><th>Question</th><th>Category</th><th>Status</th><th>Updated</th><th></th></tr></thead><tbody>
        ${data.map((f, i) => `<tr><td><strong>${esc(f.question)}</strong><br><span class="muted small">/help-center/question/${esc(f.slug)}/</span></td><td>${CAT[f.category]}</td>
          <td><span class="badge ${f.status === "published" ? "ok" : "warn"}">${f.status}</span></td><td>${when(f.updated_at)}</td><td><button class="btn" data-edit="${i}">Edit</button></td></tr>`).join("")}</tbody></table></div>`
        : `<div class="empty">No questions yet. Use “Turn into Help Center article” on a request in the inbox, or “Add question”.</div>`}</section>`;
    panel.querySelector("#hd-new-faq").addEventListener("click", () => faqEditor(view, { category: "jobs-in-malta", question: "", answer: "", status: "draft", author_name: "" }));
    panel.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () => faqEditor(view, data[+b.dataset.edit])));
  }
  function faqEditor(view, f) {
    const bg = document.createElement("div"); bg.className = "hd-modal-bg";
    bg.innerHTML = `<div class="hd-modal card" role="dialog" aria-label="Help Center question"><h2>${f.id ? "Edit" : "New"} Help Center question</h2>
      <label>Category<select name="category">${Object.entries(CAT).map(([k, v]) => `<option value="${k}" ${f.category === k ? "selected" : ""}>${v}</option>`).join("")}</select></label>
      <label>Question<input name="question" maxlength="200" value="${esc(f.question)}" placeholder="e.g. Can I apply if I don't live in Malta yet?"></label>
      <label>Answer <span class="muted small">— short paragraphs; “- ” for lists; [text](https://link) for links</span><textarea name="answer" rows="10">${esc(f.answer)}</textarea></label>
      <div class="row"><label>Author<select name="author_name"><option value="">Outreach Recruitment</option>${TEAM.map((t) => `<option ${f.author_name === t ? "selected" : ""}>${t}</option>`).join("")}</select></label>
      <label>Status<select name="status"><option value="draft" ${f.status !== "published" ? "selected" : ""}>Draft</option><option value="published" ${f.status === "published" ? "selected" : ""}>Published</option></select></label></div>
      <p class="msg error" data-err hidden></p>
      <div class="row" style="justify-content:space-between">${f.id ? `<button class="btn danger" type="button" data-del>Delete</button>` : "<span></span>"}
        <div class="row"><button class="btn" type="button" data-close>Cancel</button><button class="btn primary" type="button" data-save>Save</button></div></div></div>`;
    document.body.appendChild(bg);
    const $ = (n) => bg.querySelector(`[name="${n}"]`), err = bg.querySelector("[data-err]");
    const close = () => bg.remove();
    bg.addEventListener("click", async (e) => {
      if (e.target === bg || e.target.matches("[data-close]")) close();
      if (e.target.matches("[data-del]") && confirm("Delete this Help Center question? It disappears from the website at the next update.")) {
        const { error } = await sb.from("help_faqs").delete().eq("id", f.id); if (error) { err.textContent = error.message; err.hidden = false; return; }
        close(); tab = "faqs"; window.renderHelpdesk(view);
      }
      if (e.target.matches("[data-save]")) {
        const row = { category: $("category").value, question: $("question").value.trim(), answer: $("answer").value.trim(), status: $("status").value,
          author_name: $("author_name").value || null, updated_at: new Date().toISOString() };
        if (row.question.length < 8 || row.answer.length < 20) { err.textContent = "Write a question and an answer (at least a couple of sentences)."; err.hidden = false; return; }
        if (!f.id) { row.slug = slugify(row.question) || `question-${Date.now()}`; if (f.source_request_id) row.source_request_id = f.source_request_id; }
        const { error } = f.id ? await sb.from("help_faqs").update(row).eq("id", f.id) : await sb.from("help_faqs").insert(row);
        if (error) { err.textContent = /duplicate/i.test(error.message) ? "A question with a very similar title already exists." : error.message; err.hidden = false; return; }
        close(); tab = "faqs"; window.renderHelpdesk(view);
      }
    });
    setTimeout(() => $("question").focus(), 30);
  }

  /* ---------------- Missed searches ---------------- */
  async function missesTab(panel) {
    panel.innerHTML = `<section class="card"><p class="muted">Loading…</p></section>`;
    const since = new Date(Date.now() - 90 * 864e5).toISOString();
    const { data, error } = await sb.from("help_search_misses").select("query,created_at").gte("created_at", since).order("created_at", { ascending: false }).limit(5000);
    if (error) { panel.innerHTML = `<section class="card"><h2>Not set up yet</h2><p class="msg error">${esc(error.message)}</p><p>Run <code>supabase/migrations/20261118180000_help_center_v3.sql</code>.</p></section>`; return; }
    const agg = Object.values((data || []).reduce((m, r) => { (m[r.query] ||= { q: r.query, n: 0, last: r.created_at }).n++; return m; }, {})).sort((a, b) => b.n - a.n);
    panel.innerHTML = `<section class="card"><h2>Searches with no results (last 90 days)</h2>
      <p class="muted small">What visitors searched for on /help-center without finding an answer — the best list of questions to write next.</p>
      ${agg.length ? `<div class="table-wrap"><table><thead><tr><th>Search</th><th>Times</th><th>Last searched</th></tr></thead><tbody>${agg.slice(0, 200).map((a) => `<tr><td>${esc(a.q)}</td><td><b>${a.n}</b></td><td>${when(a.last)}</td></tr>`).join("")}</tbody></table></div>`
        : `<div class="empty">No missed searches yet.</div>`}</section>`;
  }

  /* ---------------- Reply templates ---------------- */
  function templatesTab(panel) {
    panel.innerHTML = `<section class="card"><h2>Reply templates</h2><p class="muted small">Used by “Reply with template…” in the inbox. The greeting and signature are added automatically.</p>
      <div id="hd-tpl">${templates.map((t, i) => `<div class="hd-tpl" data-i="${i}"><input value="${esc(t.name)}" data-k="name" aria-label="Template name"><textarea rows="5" data-k="body" aria-label="Template text">${esc(t.body)}</textarea>
        <button class="btn danger" type="button" data-rm>Remove</button></div>`).join("")}</div>
      <div class="row"><button class="btn" type="button" id="hd-add-tpl">Add template</button><button class="btn primary" type="button" id="hd-save-tpl">Save templates</button>
      <button class="btn" type="button" id="hd-reset-tpl">Restore defaults</button><span class="muted small" id="hd-tpl-msg"></span></div></section>`;
    const read = () => [...panel.querySelectorAll(".hd-tpl")].map((d) => ({ name: d.querySelector('[data-k="name"]').value.trim(), body: d.querySelector('[data-k="body"]').value.trim() })).filter((t) => t.name && t.body);
    panel.querySelector("#hd-add-tpl").addEventListener("click", () => { templates = [...read(), { name: "New template", body: "" }]; templatesTab(panel); });
    panel.querySelector("#hd-reset-tpl").addEventListener("click", () => { if (confirm("Replace your templates with the defaults?")) { templates = DEFAULT_TEMPLATES; templatesTab(panel); } });
    panel.querySelector("#hd-tpl").addEventListener("click", (e) => { if (e.target.matches("[data-rm]")) { e.target.closest(".hd-tpl").remove(); } });
    panel.querySelector("#hd-save-tpl").addEventListener("click", async () => { templates = read(); await saveTemplates(); panel.querySelector("#hd-tpl-msg").textContent = "Saved."; });
  }
})();
