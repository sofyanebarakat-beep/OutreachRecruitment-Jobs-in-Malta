/* Outreach Admin — candidate job-alert subscribers. */
(() => {
  "use strict";
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const date = (v) => v ? new Date(v).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) : "—";
  const euEligibleCountries = new Set("AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS LI NO CH GB MC".split(" "));
  const eligibility = (row) => euEligibleCountries.has(String(row.country_code || "").toUpperCase()) ? "eligible" : "not_eligible";
  const eligibilityLabel = (row) => eligibility(row) === "eligible" ? "Eligible for EU-only vacancies" : "Not eligible for EU-only vacancies";
  let rows = [];

  function csvCell(value) { const s = String(value ?? ""); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; }
  function downloadCsv(items) {
    const fields = ["full_name","email","country_name","country_code","eu_vacancy_eligibility","status","sources","source_jobs","job_category","created_at","last_opt_in_at"];
    items = items.map((row) => ({ ...row, eu_vacancy_eligibility: eligibilityLabel(row) }));
    const csv = [fields.join(","), ...items.map((row) => fields.map((field) => csvCell(Array.isArray(row[field]) ? row[field].join(" | ") : row[field])).join(","))].join("\n");
    const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    link.download = `job-alert-subscribers-${new Date().toISOString().slice(0,10)}.csv`; link.click(); URL.revokeObjectURL(link.href);
  }

  window.renderSubscribers = async function(view, sourceFilter) {
    const footerOnly = sourceFilter === "footer_signup";
    const title = footerOnly ? "Footer job alerts" : "Job alert subscribers";
    const description = footerOnly ? "People who completed the job-alert form in the website footer." : "People who subscribed from the website footer, after applying, or when a role was unavailable for their location.";
    view.innerHTML = `<section class="card hero"><div class="kicker">Candidates · Job alerts</div><h1>${title}</h1><p>${description}</p></section><section class="card"><p class="muted" role="status">Loading subscribers…</p></section>`;
    const store = window.AdminStore;
    if (!store || store.mode !== "supabase" || !store.sb) {
      view.lastElementChild.innerHTML = `<h2>Online database required</h2><p class="msg error">Sign in to the connected admin database to view subscriber data.</p>`; return;
    }
    const { data, error } = await store.sb.from("job_alert_subscribers").select("*").order("last_opt_in_at", { ascending: false });
    if (error) { view.lastElementChild.innerHTML = `<h2>Subscribers unavailable</h2><p class="msg error">${esc(error.message)}</p><p class="muted">Apply the job-alert database migration, then reload this section.</p>`; return; }
    rows = footerOnly ? (data || []).filter((row) => (row.sources || []).includes("footer_signup")) : (data || []);
    const active = rows.filter((r) => r.status === "active").length;
    const blocked = rows.filter((r) => (r.sources || []).includes("location_blocked")).length;
    const applied = rows.filter((r) => (r.sources || []).includes("post_application")).length;
    const footer = rows.filter((r) => (r.sources || []).includes("footer_signup")).length;
    const eligible = rows.filter((r) => eligibility(r) === "eligible").length;
    const notEligible = rows.length - eligible;
    view.innerHTML = `<section class="card hero"><div class="kicker">Candidates · Job alerts</div><h1>${title}</h1><p>${description}</p></section>
      <section class="subscriber-stats"><div class="card"><span>Active subscribers</span><strong>${active}</strong></div><div class="card"><span>Footer signups</span><strong>${footer}</strong></div><div class="card"><span>After application</span><strong>${applied}</strong></div><div class="card"><span>Location blocked</span><strong>${blocked}</strong></div><div class="card"><span>Countries</span><strong>${new Set(rows.map((r) => r.country_code)).size}</strong></div></section>
      <section class="subscriber-eligibility"><button class="card eligible" type="button" data-eligibility-pick="eligible"><span>✓ Eligible for EU-only vacancies</span><strong>${eligible}</strong><small>Current residence meets this vacancy rule</small></button><button class="card not-eligible" type="button" data-eligibility-pick="not_eligible"><span>! Not eligible for EU-only vacancies</span><strong>${notEligible}</strong><small>Keep for worldwide or location-matched roles</small></button></section>
      <section class="card"><div class="subscriber-toolbar"><label>Search<input id="subscriber-search" type="search" placeholder="Name, email, country or job"></label><label>EU-only eligibility<select id="subscriber-eligibility"><option value="all">All eligibility</option><option value="eligible">Eligible</option><option value="not_eligible">Not eligible</option></select></label><label>Status<select id="subscriber-status"><option value="all">All subscribers</option><option value="active">Active</option><option value="unsubscribed">Unsubscribed</option></select></label><button class="btn" id="subscriber-export" type="button">Export CSV</button></div><p id="subscriber-count" class="muted small"></p><div id="subscriber-table"></div></section>`;
    const search = view.querySelector("#subscriber-search"), eligibilityFilter = view.querySelector("#subscriber-eligibility"), status = view.querySelector("#subscriber-status"), table = view.querySelector("#subscriber-table"), count = view.querySelector("#subscriber-count");
    function filtered() { const q = search.value.trim().toLowerCase(); return rows.filter((r) => (status.value === "all" || r.status === status.value) && (eligibilityFilter.value === "all" || eligibility(r) === eligibilityFilter.value) && (!q || [r.full_name,r.email,r.country_name,r.source_job,r.job_category].join(" ").toLowerCase().includes(q))); }
    function draw() {
      const items = filtered(); count.textContent = `${items.length} subscriber${items.length === 1 ? "" : "s"}`;
      const sourceLabel = (source) => source === "footer_signup" ? "Footer signup" : source === "post_application" ? "After applying" : "Location blocked";
      table.innerHTML = items.length ? `<div class="table-wrap"><table><thead><tr><th>Candidate</th><th>Residence</th><th>EU-only eligibility</th><th>Source</th><th>Job/category</th><th>Opted in</th><th>Status</th></tr></thead><tbody>${items.map((r) => `<tr><td><strong>${esc(r.full_name)}</strong><br><a href="mailto:${encodeURIComponent(r.email)}">${esc(r.email)}</a></td><td>${esc(r.country_name)} <span class="muted">${esc(r.country_code)}</span></td><td><span class="subscriber-eligibility-badge ${eligibility(r)}">${eligibility(r) === "eligible" ? "Eligible" : "Not eligible"}</span></td><td>${(r.sources || []).map((s) => `<span class="subscriber-source">${sourceLabel(s)}</span>`).join(" ")}</td><td>${esc(r.source_job || "—")}<br><span class="muted small">${esc(r.job_category || "")}</span></td><td>${date(r.last_opt_in_at)}</td><td><button class="subscriber-status ${r.status}" type="button" data-id="${r.id}" data-status="${r.status}">${r.status === "active" ? "Active" : "Unsubscribed"}</button></td></tr>`).join("")}</tbody></table></div>` : `<div class="empty">No subscribers match these filters.</div>`;
    }
    search.addEventListener("input", draw); eligibilityFilter.addEventListener("change", draw); status.addEventListener("change", draw);
    view.querySelectorAll("[data-eligibility-pick]").forEach((button) => button.addEventListener("click", () => { eligibilityFilter.value = button.dataset.eligibilityPick; draw(); view.querySelector("#subscriber-table").scrollIntoView({ behavior: "smooth", block: "start" }); }));
    view.querySelector("#subscriber-export").addEventListener("click", () => downloadCsv(filtered()));
    table.addEventListener("click", async (event) => {
      const button = event.target.closest("[data-id]"); if (!button) return;
      const next = button.dataset.status === "active" ? "unsubscribed" : "active"; button.disabled = true;
      const { error: updateError } = await store.sb.from("job_alert_subscribers").update({ status: next }).eq("id", button.dataset.id);
      if (updateError) { button.disabled = false; button.textContent = "Could not update"; return; }
      const row = rows.find((item) => item.id === button.dataset.id); if (row) row.status = next; draw();
    });
    draw();
  };
})();
