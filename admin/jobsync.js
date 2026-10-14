/* Admin › Marketing › Job Sync — the daily careers-page ⇄ website sync report.
 * Reads the reports the daily agent (tools/daily_job_sync.py) pushes every morning:
 *   ../reports/daily-sync/index.json        one summary line per day
 *   ../reports/daily-sync/<YYYY-MM-DD>.json the full report of that day
 */
(() => {
  "use strict";
  const BASE = "../reports/daily-sync/";
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (v) => (v === null || v === undefined || isNaN(v) ? "—" : (+v).toLocaleString("en-GB"));
  const longDate = (d) => new Date(d + "T12:00:00").toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  const get = async (path) => {
    const r = await fetch(BASE + path + "?t=" + Date.now(), { cache: "no-store" });
    if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
    return r.json();
  };

  function subjectLine(r) {
    const inSync = r.site_open_after === r.ats_advertised;
    const opened = (r.created || []).length + (r.reopened || []).length;
    return `Daily Job sync ${r.date}: ${inSync ? "✅ In sync" : "⚠️ Not in sync"} — careers page ${fmt(r.ats_advertised)} / website ${fmt(r.site_open_after)} ` +
      `(+${opened} opened, -${(r.closed || []).length} closed` + ((r.updated || []).length ? `, ${(r.updated || []).length} updated` : "") + ")";
  }

  function jobList(rows, empty, opts = {}) {
    if (!rows || !rows.length) return `<p class="muted" style="margin:0">${empty}</p>`;
    return `<ul class="sync-list">${rows.map((j) => {
      const link = j.url || j.ats_url;
      const title = link ? `<a href="${esc(link)}" target="_blank" rel="noopener">${esc(j.title)}</a>` : esc(j.title);
      const meta = [j.city, j.salary_label].filter(Boolean).map(esc).join(" · ");
      const detail = opts.detail && (j.changes?.length || j.reason)
        ? `<details><summary class="small">${opts.detailLabel || "Details"}</summary><ul class="small">${
            (j.changes || [j.reason]).map((c) => `<li>${esc(c)}</li>`).join("")}</ul></details>`
        : j.reason ? `<div class="small" style="color:var(--warn)">${esc(j.reason)}</div>` : "";
      return `<li>${title}${meta ? ` <span class="muted small">— ${meta}</span>` : ""}${detail}</li>`;
    }).join("")}</ul>`;
  }

  function housekeeping(r) {
    const out = [], ls = r.listings || {}, g = r.google || {}, pc = r.page_check || {}, sc = r.salary_coverage || {};
    if (pc.open_checked) out.push(`Daily page check: <strong>${pc.ok} of ${pc.open_checked}</strong> open job pages pass every check` +
      (pc.fixing_today ? `; repairing ${pc.fixing_today} today` : "") + (pc.queued ? `, ${pc.queued} queued` : ""));
    if (sc.open) out.push(`Salary shown on <strong>${sc.with_salary} of ${sc.open}</strong> open jobs (${Math.round((100 * sc.with_salary) / sc.open)}%)`);
    if ((r.salary_synced || []).length) out.push(`Salary updated from the careers page: ${r.salary_synced.map(esc).join("; ")}`);
    const hub = Object.values(ls.hub_cards || {});
    const rep = hub.reduce((a, h) => a + (h.replaced || 0), 0), rem = hub.reduce((a, h) => a + (h.removed || 0), 0);
    if (rep || rem) out.push(`Hub/homepage cards for closed jobs: ${rep} replaced with open jobs, ${rem} removed`);
    if (ls.carousel_swaps) out.push(`"Similar jobs" cards updated: ${ls.carousel_swaps}`);
    if (ls.pages_marked_closed || ls.pages_reopened) out.push(`Pages switched to "Position Closed": ${ls.pages_marked_closed || 0}; reopened: ${ls.pages_reopened || 0}`);
    if ((ls.merged || []).length) out.push(`Duplicate entries merged: ${ls.merged.map((m) => esc(m.dropped.join(", ") + " → " + m.keep)).join("; ")}`);
    if ((ls.categorised || []).length) out.push(`Category set automatically for ${ls.categorised.length} job(s)`);
    if (ls.itemlist_items) out.push(`Google job list on /jobs rebuilt: ${ls.itemlist_items} open jobs`);
    if (g.sent) out.push(`Google notified about ${g.ok}/${g.sent} changed page(s)${g.sitemap ? `; jobs sitemap ${esc(g.sitemap)}` : ""}`);
    return out;
  }

  function historyTable(index, current) {
    return `<div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Status</th><th class="num">Careers page</th><th class="num">Website</th>
        <th class="num">Opened</th><th class="num">Closed</th><th class="num">Updated</th><th class="num">Attention</th><th>Live</th></tr></thead>
      <tbody>${index.map((d) => `<tr${d.date === current ? ' class="row-current"' : ""}>
        <td><a href="#/jobsync/${esc(d.date)}">${esc(d.date)}</a></td>
        <td>${d.in_sync ? `<span class="status good">✅ In sync</span>` : `<span class="status warn">⚠️ Not in sync</span>`}</td>
        <td class="num">${fmt(d.ats)}</td><td class="num">${fmt(d.site_before)} → ${fmt(d.site_after)}</td>
        <td class="num">${d.opened ? "+" + d.opened : "0"}</td><td class="num">${d.closed ? "-" + d.closed : "0"}</td>
        <td class="num">${fmt(d.updated)}</td><td class="num">${d.attention ? `<strong>${d.attention}</strong>` : "0"}</td>
        <td>${d.live_ok === true ? "✅" : d.live_ok === false ? "⚠️" : "—"}</td></tr>`).join("")}</tbody></table></div>`;
  }

  window.renderJobSync = async function (view, date) {
    view.innerHTML = `<div class="card"><p class="muted" style="margin:0">Loading the job sync report…</p></div>`;
    let index, r;
    try {
      index = await get("index.json");
      const pick = date && index.some((d) => d.date === date) ? date : index[0]?.date;
      if (!pick) throw new Error("No reports yet");
      r = await get(pick + ".json");
    } catch (e) {
      view.innerHTML = `<div class="card"><h2>No job sync report found</h2><p class="muted">${esc(e.message)}. The report appears here
        every morning after the 07:00 sync.</p></div>`;
      return;
    }
    const inSync = r.site_open_after === r.ats_advertised, lv = r.live || {}, gc = r.google_check || {};
    const attention = [...(r.failed || []), ...(r.held || [])];
    const isLatest = r.date === index[0].date;
    const notes = [...(r.notes || []), ...(r.salary_notes || [])];
    const hk = housekeeping(r);
    const at = (r.created || []).length + (r.reopened || []).length;

    view.innerHTML = `
      <section class="card hero">
        <div class="kicker">Marketing · Job Sync${isLatest ? " · latest" : ""}</div>
        <h1>${esc(longDate(r.date))}</h1>
        <p class="sync-subject">${esc(subjectLine(r))}</p>
      </section>

      <section class="grid-4">
        <div class="card kpi-card"><div class="label">Open on careers page</div><div class="value">${fmt(r.ats_advertised)}</div>
          <div class="sub">Source of truth</div></div>
        <div class="card kpi-card"><div class="label">Website now</div><div class="value">${fmt(r.site_open_after)}</div>
          <div class="sub">was ${fmt(r.site_open_before)} before the sync</div>
          ${inSync ? `<span class="status good">✅ In sync</span>` : `<span class="status warn">⚠️ ${fmt(Math.abs(r.site_open_after - r.ats_advertised))} difference</span>`}</div>
        <div class="card kpi-card"><div class="label">Changes today</div><div class="value">+${at} / -${(r.closed || []).length}</div>
          <div class="sub">opened / closed · ${(r.updated || []).length} updated</div></div>
        <div class="card kpi-card"><div class="label">Live website</div><div class="value">${lv.count != null ? fmt(lv.count) : "—"}</div>
          <div class="sub">${lv.ok ? "Matches — the change is live" : lv.count != null ? `Expected ${fmt(lv.expected)} — deploy may be delayed` : "Not checked"}</div>
          ${lv.ok ? `<span class="status good">✅ Live</span>` : lv.count != null ? `<span class="status warn">⚠️ Check</span>` : ""}</div>
      </section>

      ${attention.length ? `<section class="card" style="border-color:var(--warn)"><h2>⚠️ Needs your attention (${attention.length})</h2>
        ${jobList(attention, "")}</section>` : ""}

      <section class="sync-grid">
        <div class="card"><h2>🆕 New jobs published (${(r.created || []).length})</h2>${jobList(r.created, "None today.", { detail: true, detailLabel: "Why" })}</div>
        <div class="card"><h2>🔒 Closed (${(r.closed || []).length})</h2>${jobList(r.closed, "None today.")}</div>
        <div class="card"><h2>♻️ Reopened (${(r.reopened || []).length})</h2>${jobList(r.reopened, "None today.")}</div>
        <div class="card"><h2>✏️ Updated (${(r.updated || []).length})</h2>${jobList(r.updated, "No job changed.", { detail: true, detailLabel: "What changed" })}</div>
      </section>

      ${notes.length ? `<section class="card"><h2>Notes</h2><ul>${notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul></section>` : ""}

      ${gc.checked || gc.error ? `<section class="card"><h2>🔎 Google check — new jobs 2+ days after publishing</h2>
        <p>${(gc.ok || []).length} of ${gc.checked || 0} checked are indexed and showing in Google Jobs ✅</p>
        ${(gc.flagged || []).length ? jobList(gc.flagged.map((f) => ({ ...f, reason: f.reason })), "") : ""}
        ${gc.error ? `<p class="small" style="color:var(--warn)">${esc(gc.error)}</p>` : ""}</section>` : ""}

      ${hk.length ? `<section class="card"><h2>Site housekeeping</h2><ul class="small" style="color:var(--text-2)">${hk.map((h) => `<li>${h}</li>`).join("")}</ul></section>` : ""}

      <section class="card">
        <div class="section-title"><h2>All daily reports</h2><span class="muted small">A new report arrives every morning (sync 07:00, email 09:00 Malta)</span></div>
        ${historyTable(index, r.date)}
        <p class="small muted" style="margin-top:8px">Git: ${esc(r.git || "—")}</p>
      </section>`;
  };
})();
