/* Outreach Admin — Help Center Inbox: questions sent from the support pop-up on /help-center. */
(() => {
  "use strict";
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const when = (v) => v ? new Date(v).toLocaleString("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";
  const STATUS = { new: "New", in_progress: "In progress", answered: "Answered", closed: "Closed" };
  const csvCell = (v) => { const s = String(v ?? ""); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  let rows = [];

  window.renderHelpdesk = async function (view) {
    view.innerHTML = `<section class="card hero"><div class="kicker">Support · Help Center</div><h1>Help Center Inbox</h1>
      <p>Questions sent from the support chat on the Help Center pages. Reply by email, then mark them answered.</p></section>
      <section class="card"><p class="muted" role="status">Loading questions…</p></section>`;
    const store = window.AdminStore;
    if (!store || store.mode !== "supabase" || !store.sb) {
      view.lastElementChild.innerHTML = `<h2>Online database required</h2><p class="msg error">Sign in to the connected admin database to read Help Center questions.</p>`; return;
    }
    const { data, error } = await store.sb.from("help_requests").select("*").order("created_at", { ascending: false }).limit(1000);
    if (error) {
      view.lastElementChild.innerHTML = `<h2>Help Center inbox not set up yet</h2><p class="msg error">${esc(error.message)}</p>
        <p>Run <code>supabase/migrations/20261118150000_help_center_requests_v2.sql</code> once in the Supabase SQL Editor, then reload this page.</p>`;
      return;
    }
    rows = data || [];
    const count = (s) => rows.filter((r) => r.status === s).length;
    view.innerHTML = `<section class="card hero"><div class="kicker">Support · Help Center</div><h1>Help Center Inbox</h1>
      <p>Questions sent from the support chat on the Help Center pages. Reply by email, then mark them answered.</p></section>
      <section class="subscriber-stats"><div class="card"><span>New</span><strong>${count("new")}</strong></div><div class="card"><span>In progress</span><strong>${count("in_progress")}</strong></div>
        <div class="card"><span>Answered</span><strong>${count("answered")}</strong></div><div class="card"><span>Total</span><strong>${rows.length}</strong></div></section>
      <section class="card"><div class="subscriber-toolbar">
        <input type="search" id="hd-q" placeholder="Search name, email, question…">
        <select id="hd-status"><option value="">All statuses</option>${Object.entries(STATUS).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
        <select id="hd-topic"><option value="">All topics</option><option>Jobs in Malta</option><option>Hire</option><option>Study in Malta</option><option>General</option></select>
        <button class="btn" type="button" id="hd-csv">Download CSV</button></div><div id="hd-list"></div></section>`;
    const list = view.querySelector("#hd-list"), q = view.querySelector("#hd-q"), st = view.querySelector("#hd-status"), tp = view.querySelector("#hd-topic");
    function filtered() {
      const s = q.value.trim().toLowerCase();
      return rows.filter((r) => (!st.value || r.status === st.value) && (!tp.value || r.topic === tp.value) &&
        (!s || [r.full_name, r.email, r.phone, r.company, r.message, r.job_title, r.nationality, r.current_location].join(" ").toLowerCase().includes(s)));
    }
    function draw() {
      const items = filtered();
      list.innerHTML = items.length ? items.map((r) => `<article class="hd-item ${r.status}">
        <header><div><strong>${esc(r.full_name)}</strong> <span class="hd-topic">${esc(r.topic)}</span><br>
          <a href="mailto:${esc(r.email)}?subject=${encodeURIComponent("Your question to Outreach Recruitment")}">${esc(r.email)}</a></div>
          <div class="hd-meta">${when(r.created_at)}</div></header>
        <dl>${[["Phone", r.phone ? `<a href="tel:${esc(String(r.phone).replace(/\s/g, ""))}">${esc(r.phone)}</a>` : ""], ["Company", esc(r.company)],
          ["Current location", esc(r.current_location)], ["Nationality", esc(r.nationality)], ["Job", esc(r.job_title)],
          ["Wants to study", esc((r.details || {}).study_level)], ["Start", esc((r.details || {}).start_when)]]
          .filter(([, v]) => v).map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join("")}</dl>
        ${r.message ? `<p class="hd-msg">${esc(r.message)}</p>` : ""}
        <footer><select data-id="${r.id}" class="hd-set">${Object.entries(STATUS).map(([k, v]) => `<option value="${k}" ${r.status === k ? "selected" : ""}>${v}</option>`).join("")}</select>
          <a class="btn primary" href="mailto:${esc(r.email)}?subject=${encodeURIComponent("Your question to Outreach Recruitment")}&body=${encodeURIComponent(`Hi ${r.full_name.split(" ")[0]},\n\nThank you for contacting Outreach Recruitment${r.message ? `:\n> ${r.message}` : "."}\n\n`)}">Reply by email</a>
          ${r.page_url ? `<span class="muted small">Sent from ${esc(r.page_url.replace("https://outreachrecruitment.net", ""))}</span>` : ""}</footer></article>`).join("")
        : `<div class="empty">No questions match these filters.</div>`;
    }
    [q, st, tp].forEach((el) => el.addEventListener("input", draw));
    list.addEventListener("change", async (e) => {
      const sel = e.target.closest(".hd-set"); if (!sel) return;
      const { error } = await store.sb.from("help_requests").update({ status: sel.value, updated_at: new Date().toISOString() }).eq("id", sel.dataset.id);
      if (error) { alert(`Could not update: ${error.message}`); return; }
      const r = rows.find((x) => x.id === sel.dataset.id); if (r) r.status = sel.value; draw();
    });
    view.querySelector("#hd-csv").addEventListener("click", () => {
      const f = ["created_at", "topic", "full_name", "email", "phone", "company", "current_location", "nationality", "job_title", "study_level", "start_when", "message", "status", "page_url"];
      const csv = [f.join(","), ...filtered().map((r) => f.map((k) => csvCell(r[k] ?? (r.details || {})[k])).join(","))].join("\n");
      const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
      a.download = `help-center-questions-${new Date().toISOString().slice(0, 10)}.csv`; a.click(); URL.revokeObjectURL(a.href);
    });
    draw();
  };
})();
