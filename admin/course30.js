/* Outreach Admin — Course + KPI sections for the 30-day SEO & KPI course.
 *
 * Storage: Supabase (project in config.js), locked by RLS to emails in public.admin_users.
 *   seo_settings  key "course30"  → course progress, day notes, baseline, priority keywords, KPI check-ins
 *   seo_kpi_daily (read-only here) → daily Search Console totals written by tools/seo_course_automation.py
 *   seo_keywords  (read-only here) → live keyword positions, source_key "gsc:<keyword>"
 * If the database cannot be reached the admin can run in browser-only mode (localStorage) and
 * copy that data to the database later.
 */
(() => {
  "use strict";
  const CFG = window.ADMIN_CONFIG || {};
  const C = window.COURSE30;
  const LOCAL_KEY = "course30:settings";
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const today = () => new Date().toISOString().slice(0, 10);
  const num = (v) => (v === "" || v === null || v === undefined || isNaN(+v) ? null : +v);
  const fmt = (v, d = 0) => (v === null || v === undefined || isNaN(v) ? "—" : (+v).toLocaleString("en-GB", { maximumFractionDigits: d, minimumFractionDigits: d }));
  const pct = (a, b) => (a === null || b === null || !b ? null : ((a - b) / b) * 100);
  const daysAgo = (n) => new Date(Date.now() - n * 864e5).toISOString().slice(0, 10);

  function defaults() {
    return {
      start_date: today(),
      completed: [1],
      day_notes: {},
      baseline: {
        date: CFG.BASELINE?.date || "", clicks28: CFG.BASELINE?.clicks28 ?? null,
        impressions28: CFG.BASELINE?.impressions28 ?? null, ctr: null, position: null,
        verified: false, note: C.baselineWarning,
      },
      keywords: [
        ...C.day1Keywords.map((k) => ({ ...k })),
        ...C.focusKeywords
          .map((k) => k.toLowerCase())
          .filter((k) => !C.day1Keywords.some((d) => d.keyword === k))
          .map((k) => ({ keyword: k, priority: "High", baseline_position: null })),
      ],
      checkins: [],
    };
  }

  // ── Storage ───────────────────────────────────────────────────────────────
  const Store = {
    mode: "local", sb: null, settings: null, auto: [], live: {},
    async load() {
      let s = null;
      if (this.mode === "supabase") {
        const { data, error } = await this.sb.from("seo_settings").select("value").eq("key", "course30").maybeSingle();
        if (error) throw error;
        s = data?.value || null;
      } else {
        try { s = JSON.parse(localStorage.getItem(LOCAL_KEY) || "null"); } catch { s = null; }
      }
      this.settings = { ...defaults(), ...(s || {}) };
      if (!s) await this.save();
      await this.loadAuto();
    },
    async save() {
      if (this.mode === "supabase") {
        const { error } = await this.sb.from("seo_settings").upsert({ key: "course30", value: this.settings, updated_at: new Date().toISOString() });
        if (error) throw error;
      } else {
        localStorage.setItem(LOCAL_KEY, JSON.stringify(this.settings));
      }
    },
    async loadAuto() {
      this.auto = []; this.live = {};
      if (this.mode !== "supabase") return;
      const daily = await this.sb.from("seo_kpi_daily").select("date,clicks,impressions,avg_position")
        .gte("date", daysAgo(150)).order("date");
      if (!daily.error) this.auto = daily.data || [];
      const keys = this.settings.keywords.map((k) => "gsc:" + k.keyword.toLowerCase());
      if (keys.length) {
        const kw = await this.sb.from("seo_keywords").select("source_key,current_position,volume,notes").in("source_key", keys);
        if (!kw.error) for (const r of kw.data || []) this.live[r.source_key.slice(4)] = r;
      }
    },
  };
  window.AdminStore = Store; // shared with marketing.js / images.js (same signed-in Supabase client)
  const save = async (msg) => {
    try { await Store.save(); if (msg) toast(msg); }
    catch (e) { toast("Could not save: " + (e.message || e), true); }
  };

  // ── Derived numbers ───────────────────────────────────────────────────────
  // Rolling 28-day totals from the automation's daily Search Console rows.
  function autoSeries() {
    const rows = Store.auto.filter((r) => r.clicks !== null || r.impressions !== null);
    const byDate = new Map(rows.map((r) => [r.date, r]));
    const out = [];
    for (const r of rows) {
      let c = 0, i = 0, pw = 0, n = 0;
      for (let k = 0; k < 28; k++) {
        const d = new Date(new Date(r.date).getTime() - k * 864e5).toISOString().slice(0, 10);
        const x = byDate.get(d);
        if (!x) continue;
        n++; c += x.clicks || 0; i += x.impressions || 0; pw += (x.avg_position || 0) * (x.impressions || 0);
      }
      if (n >= 25) out.push({ date: r.date, clicks28: c, impressions28: i, ctr: i ? (c / i) * 100 : null, position: i ? pw / i : null, source: "Search Console (auto)" });
    }
    return out;
  }
  function series() {
    const manual = Store.settings.checkins.map((c) => ({ ...c, source: "Check-in" }));
    const auto = autoSeries();
    const map = new Map();
    for (const p of [...auto, ...manual]) map.set(p.date, { ...(map.get(p.date) || {}), ...Object.fromEntries(Object.entries(p).filter(([, v]) => v !== null && v !== "")) });
    return [...map.values()].sort((a, b) => a.date.localeCompare(b.date));
  }
  function latest() {
    const s = series();
    const last = (field) => { for (let i = s.length - 1; i >= 0; i--) if (s[i][field] !== undefined && s[i][field] !== null) return { value: s[i][field], date: s[i].date, source: s[i].source }; return null; };
    return { clicks: last("clicks28"), impressions: last("impressions28"), ctr: last("ctr"), position: last("position"),
      applications: last("applications"), leads: last("employer_leads"), users: last("organic_users") };
  }
  function keywordRows() {
    return Store.settings.keywords.map((k) => {
      const live = Store.live[k.keyword.toLowerCase()];
      const current = num(k.manual_position) ?? (live ? num(live.current_position) : null);
      const impressions = num(k.manual_impressions) ?? (live ? num(live.volume) : null) ?? num(k.baseline_impressions);
      return { ...k, current, impressions, liveNote: live?.notes || "", top10: current !== null && current <= 10 };
    });
  }
  const completedSet = () => new Set(Store.settings.completed || []);
  const currentDay = () => { const done = completedSet(); for (let d = 1; d <= 30; d++) if (!done.has(d)) return d; return 30; };
  const phaseOf = (day) => C.phases.find((p) => day >= p.days[0] && day <= p.days[1]);

  // ── Course section ────────────────────────────────────────────────────────
  let selectedDay = null;
  function renderCourse() {
    const s = Store.settings, done = completedSet(), cur = currentDay(), ph = phaseOf(cur);
    selectedDay = selectedDay || cur;
    const kw = keywordRows().filter((k) => C.day1Keywords.some((d) => d.keyword === k.keyword));
    const pctDone = Math.round((done.size / 30) * 100);
    $("#view").innerHTML = `
      <section class="card hero">
        <div class="kicker">${esc(C.subtitle)}</div>
        <h1>${esc(C.title)}</h1>
        <p>Day ${cur} of 30 · ${esc(ph?.label || "")} — ${esc(ph?.title || "")}</p>
      </section>

      <section class="card next">
        <div class="section-title"><h2>Today · Day ${cur}</h2><span class="muted small">${done.size}/30 lessons done</span></div>
        ${cur === C.nextStep.day ? `<p><strong>${esc(C.nextStep.title)}.</strong> ${esc(C.nextStep.text)}</p>` : `<p><strong>${esc(ph.title)}.</strong> ${esc(ph.summary)}</p>`}
        <div class="progress" aria-label="Course progress ${pctDone}%"><span style="width:${pctDone}%"></span></div>
        <div class="form-actions"><button class="btn primary" id="finish-today">Mark Day ${cur} as done</button>
          <a class="btn" href="#/kpi">Record today's KPIs</a></div>
      </section>

      <section class="card">
        <div class="section-title"><h2>30-day plan</h2><span class="muted small">Click a day to open it</span></div>
        <div class="day-grid" role="list">
          ${Array.from({ length: 30 }, (_, i) => i + 1).map((d) => `<button class="day ${done.has(d) ? "done" : ""} ${d === cur ? "today" : ""}" data-day="${d}" role="listitem"
            aria-label="Day ${d}${done.has(d) ? ", done" : ""}${d === cur ? ", today" : ""}">${done.has(d) ? "✓" : d}</button>`).join("")}
        </div>
        <div id="day-panel" style="margin-top:14px"></div>
      </section>

      <section class="card">
        <h2>1. Main objective</h2>
        <p>${esc(C.objective)}</p>
        <p class="muted">We will focus on ranking these keywords in Google's Top 10:</p>
        <ul class="chips">${C.focusKeywords.map((k) => `<li class="chip">${esc(k)}</li>`).join("")}</ul>
      </section>

      <section class="card">
        <h2>2. Daily course structure</h2>
        <div class="table-wrap"><table>
          <thead><tr><th>Activity</th><th class="num">Duration</th><th>Objective</th></tr></thead>
          <tbody>${C.dailyStructure.map((r) => `<tr><td>${esc(r.activity)}</td><td class="num">${r.minutes} min</td><td>${esc(r.objective)}</td></tr>`).join("")}
          <tr><td><strong>Total</strong></td><td class="num"><strong>60 min</strong></td><td>One lesson daily</td></tr></tbody>
        </table></div>
      </section>

      <section>
        <h2 style="margin:4px 0 10px">3. Your 30-day learning plan</h2>
        <div class="grid-2">
          ${C.phases.map((p) => `<article class="card phase ${p === ph ? "current" : ""}">
            <span class="days">${esc(p.label)}${p.label.startsWith("Days") ? "" : ` · Days ${p.days[0]}–${p.days[1]}`}${p === ph ? " · current" : ""}</span>
            <h3>${esc(p.title)}</h3>
            <p class="small" style="margin:0">${esc(p.summary)}</p>
            <div class="small muted">KPIs</div>
            <ul>${p.kpis.map((k) => `<li>${esc(k)}</li>`).join("")}</ul>
          </article>`).join("")}
        </div>
      </section>

      <section class="card">
        <h2>4. Your current progress</h2>
        <p class="muted">Keywords recorded from Google Search Console on Day 1${Object.keys(Store.live).length ? " · current positions update automatically" : ""}.</p>
        <div class="table-wrap"><table>
          <thead><tr><th>Keyword</th><th class="num">Day 1 position</th><th class="num">Current position</th><th>Priority</th></tr></thead>
          <tbody>${kw.map((k) => `<tr><td>${esc(k.keyword)}</td><td class="num">${fmt(k.baseline_position, 1)}</td>
            <td class="num">${fmt(k.current, 1)}</td><td>${esc(k.priority)}</td></tr>`).join("")}</tbody>
        </table></div>
        <p style="margin-top:10px">${esc(C.firstOpportunity)}</p>
        ${s.baseline.verified ? "" : `<p class="status warn">⚠ ${esc(C.baselineWarning)}</p>`}
      </section>

      <section class="card">
        <h2>5. Course success KPIs</h2>
        <p class="muted">${esc(C.targetsNote)}</p>
        <div class="grid-4">${C.targets.map((t) => `<div class="card kpi-card" style="background:var(--surface-2)">
          <div class="value">${esc(t.value)}</div><div class="label">${esc(t.label)}</div></div>`).join("")}</div>
        <div class="form-actions"><a class="btn" href="#/kpi">Track these in KPI →</a></div>
      </section>

      <section class="card">
        <h2>6. Tools we will use</h2>
        <ul>${C.tools.map((t) => `<li><strong>${esc(t.name)}</strong> — ${esc(t.use)}</li>`).join("")}</ul>
        <p><strong>Your next step: Day ${C.nextStep.day} — ${esc(C.nextStep.title)}.</strong> ${esc(C.nextStep.text)}</p>
      </section>`;

    const panel = () => {
      const d = selectedDay, p = phaseOf(d), isDone = completedSet().has(d);
      $("#day-panel").innerHTML = `<div class="card" style="background:var(--surface-2)">
        <div class="section-title"><h3>Day ${d} · ${esc(p.label)} — ${esc(p.title)}</h3>
          <span class="status ${isDone ? "good" : "none"}">${isDone ? "✓ Done" : "Not done yet"}</span></div>
        <p class="small">${esc(p.summary)}</p>
        <label>My notes for Day ${d}<textarea id="day-note" rows="3" placeholder="What did you learn, change and measure?">${esc(Store.settings.day_notes[d] || "")}</textarea></label>
        <div class="form-actions">
          <button class="btn primary" id="toggle-day">${isDone ? "Mark as not done" : "Mark as done"}</button>
          <button class="btn" id="save-note">Save notes</button>
        </div></div>`;
      $("#toggle-day").onclick = async () => {
        const set = completedSet();
        set.has(d) ? set.delete(d) : set.add(d);
        Store.settings.completed = [...set].sort((a, b) => a - b);
        Store.settings.day_notes[d] = $("#day-note").value;
        await save(set.has(d) ? `Day ${d} marked as done` : `Day ${d} marked as not done`);
        renderCourse();
      };
      $("#save-note").onclick = async () => { Store.settings.day_notes[d] = $("#day-note").value; await save("Notes saved"); };
    };
    $$(".day").forEach((b) => (b.onclick = () => { selectedDay = +b.dataset.day; panel(); }));
    $("#finish-today").onclick = async () => {
      const set = completedSet(); set.add(cur);
      Store.settings.completed = [...set].sort((a, b) => a - b);
      selectedDay = null;
      await save(`Day ${cur} done — well done!`);
      renderCourse();
    };
    panel();
  }

  // ── KPI section ───────────────────────────────────────────────────────────
  function status(cur, target, base, isCount = false) {
    if (cur === null || target === null) return `<span class="status none">No data yet</span>`;
    if (cur >= target) return `<span class="status good">✓ Target reached</span>`;
    if (isCount) return cur > 0 ? `<span class="status warn">↗ In progress</span>` : `<span class="status none">Not yet</span>`;
    if (base !== null && cur > base) return `<span class="status warn">↗ Improving</span>`;
    return `<span class="status bad">↘ Below baseline</span>`;
  }
  function kpiCard(label, value, sub, progress, statusHtml) {
    const w = Math.max(0, Math.min(100, progress ?? 0));
    return `<div class="card kpi-card"><div class="label">${label}</div><div class="value">${value}</div>
      <div class="sub">${sub}</div><div class="progress"><span style="width:${w}%"></span></div>${statusHtml}</div>`;
  }

  function renderKPI() {
    const s = Store.settings, b = s.baseline, L = latest(), kws = keywordRows();
    const tClicks = b.clicks28 ? Math.round(b.clicks28 * 1.2) : null;
    const tImpr = b.impressions28 ? Math.round(b.impressions28 * 1.3) : null;
    const priority = kws.filter((k) => k.priority !== "Maintain");
    const top10 = priority.filter((k) => k.top10).length;
    const lessons = completedSet().size;
    const prog = (cur, base, target) => (cur === null || base === null || target === null || target === base ? 0 : ((cur - base) / (target - base)) * 100);
    const cVal = L.clicks?.value ?? null, iVal = L.impressions?.value ?? null;
    const ser = series();

    $("#view").innerHTML = `
      <section class="card hero">
        <div class="kicker">Course KPIs · 90-day targets</div>
        <h1>KPI tracking</h1>
        <p>Baseline ${b.date ? `from ${esc(b.date)}` : "not set"} ${b.verified ? "· verified ✓" : "· needs verification"} · latest data ${esc(L.clicks?.date || L.impressions?.date || "—")}</p>
      </section>

      <section class="grid-4">
        ${kpiCard("Organic clicks (28 days)", fmt(cVal), `Baseline ${fmt(b.clicks28)} · target ${fmt(tClicks)} (+20%)` + (cVal !== null && b.clicks28 ? ` · ${pct(cVal, b.clicks28) >= 0 ? "+" : ""}${fmt(pct(cVal, b.clicks28), 1)}%` : ""), prog(cVal, b.clicks28, tClicks), status(cVal, tClicks, b.clicks28))}
        ${kpiCard("Google impressions (28 days)", fmt(iVal), `Baseline ${fmt(b.impressions28)} · target ${fmt(tImpr)} (+30%)` + (iVal !== null && b.impressions28 ? ` · ${pct(iVal, b.impressions28) >= 0 ? "+" : ""}${fmt(pct(iVal, b.impressions28), 1)}%` : ""), prog(iVal, b.impressions28, tImpr), status(iVal, tImpr, b.impressions28))}
        ${kpiCard("Priority keywords in Top 10", `${top10} / 5`, `${priority.length} priority keywords tracked`, (top10 / 5) * 100, status(top10, 5, 0, true))}
        ${kpiCard("Daily lessons completed", `${lessons} / 30`, `Next: Day ${currentDay()}`, (lessons / 30) * 100, status(lessons, 30, 0, true))}
      </section>

      <section class="grid-4">
        ${[["CTR", L.ctr ? fmt(L.ctr.value, 2) + "%" : "—", b.ctr !== null && b.ctr !== undefined ? `Baseline ${fmt(b.ctr, 2)}%` : ""],
           ["Average position", L.position ? fmt(L.position.value, 1) : "—", b.position ? `Baseline ${fmt(b.position, 1)}` : ""],
           ["Applications", fmt(L.applications?.value), "Latest check-in"],
           ["Employer leads", fmt(L.leads?.value), "Latest check-in"]]
          .map(([l, v, sub]) => `<div class="card kpi-card"><div class="label">${l}</div><div class="value" style="font-size:1.4rem">${v}</div><div class="sub">${sub}</div></div>`).join("")}
      </section>

      <section class="grid-2">
        <div class="card"><h2>Organic clicks · last 28 days</h2><div class="chart" id="chart-clicks"></div></div>
        <div class="card"><h2>Google impressions · last 28 days</h2><div class="chart" id="chart-impr"></div></div>
      </section>

      <section class="card">
        <div class="section-title"><h2>Record a check-in</h2><span class="muted small">Copy the "last 28 days" totals from Search Console${Store.auto.length ? " — clicks and impressions also arrive automatically" : ""}</span></div>
        <form id="checkin" class="form-grid">
          <label>Date<input type="date" name="date" value="${today()}" required></label>
          <label>Clicks (28 days)<input type="number" name="clicks28" min="0"></label>
          <label>Impressions (28 days)<input type="number" name="impressions28" min="0"></label>
          <label>CTR %<input type="number" step="0.01" name="ctr" min="0"></label>
          <label>Avg position<input type="number" step="0.1" name="position" min="0"></label>
          <label>Organic users (GA4)<input type="number" name="organic_users" min="0"></label>
          <label>Applications<input type="number" name="applications" min="0"></label>
          <label>Employer leads<input type="number" name="employer_leads" min="0"></label>
          <label style="grid-column:1/-1">Notes<input type="text" name="notes" placeholder="What changed? Which lesson/day?"></label>
          <div class="form-actions" style="grid-column:1/-1"><button class="btn primary" type="submit">Save check-in</button></div>
        </form>
      </section>

      <section class="card">
        <div class="section-title"><h2>Priority keywords</h2><span class="muted small">Target: 5 priority keywords in Google's Top 10${Object.keys(Store.live).length ? " · positions update daily from Search Console" : ""}</span></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Keyword</th><th>Priority</th><th class="num">Day 1</th><th class="num">Current</th><th class="num">Change</th><th class="num">Impressions</th><th>Top 10</th><th></th></tr></thead>
          <tbody>${kws.map((k, i) => {
            const ch = k.baseline_position !== null && k.current !== null ? k.baseline_position - k.current : null;
            return `<tr><td>${esc(k.keyword)}${k.liveNote ? `<div class="muted small">${esc(k.liveNote)}</div>` : ""}</td>
              <td><select data-i="${i}" data-f="priority" class="inline-input">${["High", "Medium", "Low", "Maintain"].map((p) => `<option ${p === k.priority ? "selected" : ""}>${p}</option>`).join("")}</select></td>
              <td class="num">${fmt(k.baseline_position, 1)}</td>
              <td class="num"><input class="inline-input" type="number" step="0.1" data-i="${i}" data-f="manual_position" value="${k.manual_position ?? ""}" placeholder="${fmt(k.current, 1)}" aria-label="Current position for ${esc(k.keyword)}"></td>
              <td class="num">${ch === null ? "—" : (ch > 0 ? "▲ " : ch < 0 ? "▼ " : "") + fmt(Math.abs(ch), 1)}</td>
              <td class="num">${fmt(k.impressions)}</td>
              <td>${k.current === null ? `<span class="status none">—</span>` : k.top10 ? `<span class="status good">✓ Top 10</span>` : `<span class="status warn">Not yet</span>`}</td>
              <td><button class="btn ghost small" data-del="${i}" aria-label="Remove ${esc(k.keyword)}">✕</button></td></tr>`;
          }).join("")}</tbody>
        </table></div>
        <form id="add-kw" class="form-actions" style="margin-top:10px">
          <input name="keyword" placeholder="Add a keyword" required style="max-width:280px">
          <input name="baseline_position" type="number" step="0.1" placeholder="Position now" style="max-width:140px">
          <select name="priority" style="max-width:130px"><option>High</option><option>Medium</option><option>Low</option><option>Maintain</option></select>
          <button class="btn" type="submit">Add</button>
        </form>
      </section>

      <section class="card">
        <h2>Baseline</h2>
        ${b.verified ? "" : `<p class="status warn">⚠ ${esc(b.note || C.baselineWarning)}</p>`}
        <form id="baseline" class="form-grid" style="margin-top:10px">
          <label>Baseline date<input type="date" name="date" value="${esc(b.date)}"></label>
          <label>Clicks (28 days)<input type="number" name="clicks28" value="${b.clicks28 ?? ""}"></label>
          <label>Impressions (28 days)<input type="number" name="impressions28" value="${b.impressions28 ?? ""}"></label>
          <label>CTR %<input type="number" step="0.01" name="ctr" value="${b.ctr ?? ""}"></label>
          <label>Avg position<input type="number" step="0.1" name="position" value="${b.position ?? ""}"></label>
          <label style="align-self:end;display:flex;gap:8px;align-items:center;font-weight:600"><input type="checkbox" name="verified" ${b.verified ? "checked" : ""} style="width:auto"> Verified in Search Console</label>
          <div class="form-actions" style="grid-column:1/-1"><button class="btn primary" type="submit">Save baseline</button>
            <span class="muted small">Targets are calculated from this: clicks +20%, impressions +30%.</span></div>
        </form>
      </section>

      <section class="card">
        <div class="section-title"><h2>History</h2>
          <div class="form-actions"><button class="btn small" id="export">Download CSV</button>
          ${Store.mode === "supabase" && localStorage.getItem(LOCAL_KEY) ? `<button class="btn small primary" id="migrate">Copy browser data to the database</button>` : ""}</div></div>
        ${ser.length ? `<div class="table-wrap"><table>
          <thead><tr><th>Date</th><th class="num">Clicks 28d</th><th class="num">Impr. 28d</th><th class="num">CTR</th><th class="num">Position</th><th class="num">Apps</th><th class="num">Leads</th><th>Source</th><th></th></tr></thead>
          <tbody>${ser.slice().reverse().slice(0, 60).map((r) => `<tr><td>${esc(r.date)}</td><td class="num">${fmt(r.clicks28)}</td><td class="num">${fmt(r.impressions28)}</td>
            <td class="num">${r.ctr ? fmt(r.ctr, 2) + "%" : "—"}</td><td class="num">${fmt(r.position, 1)}</td><td class="num">${fmt(r.applications)}</td>
            <td class="num">${fmt(r.employer_leads)}</td><td class="small muted">${esc(r.source || "")}${r.notes ? " · " + esc(r.notes) : ""}</td>
            <td>${s.checkins.some((c) => c.date === r.date) ? `<button class="btn ghost small" data-del-checkin="${esc(r.date)}" aria-label="Delete check-in ${esc(r.date)}">✕</button>` : ""}</td></tr>`).join("")}</tbody>
        </table></div>` : `<div class="empty">No KPI data yet. Record your first check-in above${Store.mode === "supabase" ? ", or wait for the daily Search Console import" : ""}.</div>`}
      </section>`;

    lineChart($("#chart-clicks"), ser.filter((r) => r.clicks28 !== undefined && r.clicks28 !== null).map((r) => ({ date: r.date, v: r.clicks28 })), tClicks, "Target +20%");
    lineChart($("#chart-impr"), ser.filter((r) => r.impressions28 !== undefined && r.impressions28 !== null).map((r) => ({ date: r.date, v: r.impressions28 })), tImpr, "Target +30%");

    $("#checkin").onsubmit = async (e) => {
      e.preventDefault();
      const f = Object.fromEntries(new FormData(e.target));
      const row = { date: f.date, notes: f.notes.trim() };
      for (const k of ["clicks28", "impressions28", "ctr", "position", "organic_users", "applications", "employer_leads"]) row[k] = num(f[k]);
      if (row.ctr === null && row.clicks28 && row.impressions28) row.ctr = +((row.clicks28 / row.impressions28) * 100).toFixed(2);
      s.checkins = [...s.checkins.filter((c) => c.date !== row.date), row].sort((a, b) => a.date.localeCompare(b.date));
      await save("Check-in saved"); renderKPI();
    };
    $("#baseline").onsubmit = async (e) => {
      e.preventDefault();
      const f = new FormData(e.target);
      Object.assign(s.baseline, { date: f.get("date"), clicks28: num(f.get("clicks28")), impressions28: num(f.get("impressions28")),
        ctr: num(f.get("ctr")), position: num(f.get("position")), verified: f.get("verified") === "on" });
      await save("Baseline saved"); renderKPI();
    };
    $("#add-kw").onsubmit = async (e) => {
      e.preventDefault();
      const f = new FormData(e.target), keyword = String(f.get("keyword")).trim().toLowerCase();
      if (!keyword || s.keywords.some((k) => k.keyword === keyword)) return toast("That keyword is already tracked", true);
      s.keywords.push({ keyword, priority: f.get("priority"), baseline_position: num(f.get("baseline_position")) });
      await save("Keyword added"); await Store.loadAuto(); renderKPI();
    };
    $$("[data-f]").forEach((el) => (el.onchange = async () => {
      const k = s.keywords[+el.dataset.i];
      k[el.dataset.f] = el.dataset.f === "priority" ? el.value : num(el.value);
      await save("Saved"); renderKPI();
    }));
    $$("[data-del]").forEach((el) => (el.onclick = async () => {
      const k = s.keywords[+el.dataset.del];
      if (!confirm(`Stop tracking “${k.keyword}”?`)) return;
      s.keywords.splice(+el.dataset.del, 1); await save("Keyword removed"); renderKPI();
    }));
    $$("[data-del-checkin]").forEach((el) => (el.onclick = async () => {
      if (!confirm(`Delete the check-in of ${el.dataset.delCheckin}?`)) return;
      s.checkins = s.checkins.filter((c) => c.date !== el.dataset.delCheckin); await save("Check-in deleted"); renderKPI();
    }));
    $("#export").onclick = () => {
      const cols = ["date", "clicks28", "impressions28", "ctr", "position", "organic_users", "applications", "employer_leads", "source", "notes"];
      const csv = [cols.join(","), ...ser.map((r) => cols.map((c) => `"${String(r[c] ?? "").replace(/"/g, '""')}"`).join(","))].join("\n");
      const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(new Blob([csv], { type: "text/csv" })), download: `course-kpi-${today()}.csv` });
      a.click(); URL.revokeObjectURL(a.href);
    };
    const mig = $("#migrate");
    if (mig) mig.onclick = async () => {
      let local; try { local = JSON.parse(localStorage.getItem(LOCAL_KEY)); } catch { local = null; }
      if (!local) return;
      s.completed = [...new Set([...(s.completed || []), ...(local.completed || [])])].sort((a, b) => a - b);
      s.day_notes = { ...(local.day_notes || {}), ...s.day_notes };
      const byDate = new Map([...(local.checkins || []), ...s.checkins].map((c) => [c.date, c]));
      s.checkins = [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date));
      for (const k of local.keywords || []) if (!s.keywords.some((x) => x.keyword === k.keyword)) s.keywords.push(k);
      await save("Browser data copied to the database");
      localStorage.removeItem(LOCAL_KEY); renderKPI();
    };
  }

  // ── Line chart (single series + dashed target, crosshair tooltip) ─────────
  function lineChart(el, pts, target, targetLabel) {
    if (pts.length < 2) {
      el.innerHTML = `<div class="empty">${pts.length ? "One data point so far — the trend appears after the next check-in." : "No data yet."}</div>`;
      return;
    }
    const W = 640, H = 220, m = { l: 52, r: 16, t: 14, b: 26 };
    const xs = pts.map((p) => new Date(p.date).getTime()), vs = pts.map((p) => p.v);
    let lo = Math.min(...vs, target ?? Infinity), hi = Math.max(...vs, target ?? -Infinity);
    const pad = (hi - lo) * 0.12 || hi * 0.1 || 1; lo = Math.max(0, lo - pad); hi += pad;
    const x = (t) => m.l + ((t - xs[0]) / (xs[xs.length - 1] - xs[0] || 1)) * (W - m.l - m.r);
    const y = (v) => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);
    const ticks = Array.from({ length: 4 }, (_, i) => lo + ((hi - lo) * i) / 3);
    const short = (d) => new Date(d).toLocaleDateString("en-GB", { day: "numeric", month: "short" });
    const path = pts.map((p, i) => `${i ? "L" : "M"}${x(xs[i]).toFixed(1)},${y(p.v).toFixed(1)}`).join("");
    const last = pts[pts.length - 1];
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Trend from ${short(pts[0].date)} to ${short(last.date)}, latest ${fmt(last.v)}">
      <g class="grid">${ticks.map((t) => `<line x1="${m.l}" x2="${W - m.r}" y1="${y(t)}" y2="${y(t)}"/>`).join("")}</g>
      <g class="axis">${ticks.map((t) => `<text x="${m.l - 8}" y="${y(t) + 4}" text-anchor="end">${fmt(t)}</text>`).join("")}
        <text x="${m.l}" y="${H - 6}">${short(pts[0].date)}</text><text x="${W - m.r}" y="${H - 6}" text-anchor="end">${short(last.date)}</text></g>
      ${target ? `<line class="target" x1="${m.l}" x2="${W - m.r}" y1="${y(target)}" y2="${y(target)}"/><text class="target-label" x="${m.l + 6}" y="${y(target) - 6}" text-anchor="start">${targetLabel} · ${fmt(target)}</text>` : ""}
      <path class="series" d="${path}"/>
      <circle class="dot" cx="${x(xs[xs.length - 1])}" cy="${y(last.v)}" r="4.5"/>
      <line class="crosshair" y1="${m.t}" y2="${H - m.b}" visibility="hidden"/>
      <circle class="dot hover-dot" r="4.5" visibility="hidden"/>
      <rect x="${m.l}" y="0" width="${W - m.l - m.r}" height="${H}" fill="transparent" class="hit"/>
    </svg><div class="tip" hidden></div>`;
    const svg = $("svg", el), tip = $(".tip", el), ch = $(".crosshair", el), hd = $(".hover-dot", el);
    const show = (evt) => {
      const r = svg.getBoundingClientRect(), px = ((evt.clientX - r.left) / r.width) * W;
      let best = 0; xs.forEach((t, i) => { if (Math.abs(x(t) - px) < Math.abs(x(xs[best]) - px)) best = i; });
      const p = pts[best], cx = x(xs[best]), cy = y(p.v);
      ch.setAttribute("x1", cx); ch.setAttribute("x2", cx); ch.setAttribute("visibility", "visible");
      hd.setAttribute("cx", cx); hd.setAttribute("cy", cy); hd.setAttribute("visibility", "visible");
      tip.hidden = false; tip.innerHTML = `<strong>${fmt(p.v)}</strong> · ${short(p.date)}`;
      const left = (cx / W) * r.width; tip.style.left = Math.min(Math.max(0, left - 50), r.width - 120) + "px"; tip.style.top = (cy / H) * r.height - 44 + "px";
    };
    const hide = () => { tip.hidden = true; ch.setAttribute("visibility", "hidden"); hd.setAttribute("visibility", "hidden"); };
    $(".hit", el).addEventListener("pointermove", show);
    $(".hit", el).addEventListener("pointerleave", hide);
  }

  // ── Shell: routing, toast, theme, auth ────────────────────────────────────
  function toast(msg, isError) {
    const b = $("#banner");
    b.textContent = msg; b.hidden = false;
    b.style.background = isError ? "var(--bad-bg)" : "var(--good-bg)"; b.style.color = isError ? "var(--bad)" : "var(--good)";
    clearTimeout(toast.t); toast.t = setTimeout(() => (b.hidden = true), 3500);
  }
  function route() {
    const h = location.hash;
    if (h && !h.startsWith("#/")) return; // auth tokens in the hash — leave them to Supabase
    const [r, param] = (h.slice(2) || "jobsync").split("?")[0].split("/");
    $$("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.route === r));
    if (r === "jobsync") window.renderJobSync($("#view"), param);
    else if (r === "marketing") window.renderMarketing($("#view"));
    else if (r === "social") window.renderSocial($("#view"));
    else (r === "kpi" ? renderKPI : renderCourse)();
    $("#view").focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }
  function show(id) { $$(".screen, #app").forEach((el) => (el.hidden = el.id !== id)); }
  async function startApp() {
    show("app");
    const badge = $("#mode-badge");
    badge.textContent = Store.mode === "supabase" ? "Saved online" : "This browser only";
    badge.className = "badge " + (Store.mode === "supabase" ? "good" : "warn");
    $("#sign-out").hidden = Store.mode !== "supabase";
    try { await Store.load(); }
    catch (e) { $("#view").innerHTML = `<div class="card"><h2>Could not load your data</h2><p>${esc(e.message || e)}</p></div>`; return; }
    if (!location.hash.startsWith("#/")) history.replaceState(null, "", "#/jobsync");
    route();
  }
  function initTheme() {
    let t = null; try { t = localStorage.getItem("admin:theme"); } catch {}
    if (t) document.documentElement.dataset.theme = t;
    $("#theme-toggle").onclick = () => {
      const dark = document.documentElement.dataset.theme
        ? document.documentElement.dataset.theme === "dark"
        : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem("admin:theme", next); } catch {}
      route();
    };
  }
  async function reachable() {
    try {
      const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 6000);
      const r = await fetch(CFG.SUPABASE_URL + "/auth/v1/health", { headers: { apikey: CFG.SUPABASE_ANON_KEY }, signal: ctl.signal });
      clearTimeout(t); return r.ok;
    } catch { return false; }
  }
  async function enterIfAdmin() {
    const { data, error } = await Store.sb.from("admin_users").select("email").limit(1);
    if (error || !data?.length) {
      await Store.sb.auth.signOut();
      show("screen-login");
      const m = $("#login-msg"); m.className = "msg error"; m.textContent = "This account does not have admin access.";
      return;
    }
    startApp();
  }

  async function init() {
    initTheme();
    window.addEventListener("hashchange", () => { if (!$("#app").hidden) route(); });
    $("#use-local").onclick = () => { Store.mode = "local"; startApp(); };
    if (!CFG.SUPABASE_URL || !CFG.SUPABASE_ANON_KEY || !window.supabase) { Store.mode = "local"; return startApp(); }
    if (!(await reachable())) return show("screen-offline");

    Store.sb = window.supabase.createClient(CFG.SUPABASE_URL, CFG.SUPABASE_ANON_KEY);
    Store.mode = "supabase";
    Store.sb.auth.onAuthStateChange((event) => { if (event === "PASSWORD_RECOVERY") show("screen-reset"); });

    $("#login-form").onsubmit = async (e) => {
      e.preventDefault();
      const f = e.target, m = $("#login-msg");
      m.className = "msg"; m.textContent = "Signing in…";
      const { error } = await Store.sb.auth.signInWithPassword({ email: f.email.value.trim(), password: f.password.value });
      if (error) { m.className = "msg error"; m.textContent = error.message; return; }
      m.textContent = ""; enterIfAdmin();
    };
    $("#forgot").onclick = async () => {
      const email = $("#login-form").email.value.trim(), m = $("#login-msg");
      if (!email) { m.className = "msg error"; m.textContent = "Type your email first."; return; }
      const { error } = await Store.sb.auth.resetPasswordForEmail(email, { redirectTo: location.origin + location.pathname });
      m.className = error ? "msg error" : "msg ok";
      m.textContent = error ? error.message : "Check your inbox for the password link.";
    };
    $("#reset-form").onsubmit = async (e) => {
      e.preventDefault();
      const m = $("#reset-msg");
      const { error } = await Store.sb.auth.updateUser({ password: e.target.password.value });
      if (error) { m.className = "msg error"; m.textContent = error.message; return; }
      history.replaceState(null, "", location.pathname + "#/jobsync");
      enterIfAdmin();
    };
    $("#sign-out").onclick = async () => { await Store.sb.auth.signOut(); show("screen-login"); };

    const { data } = await Store.sb.auth.getSession();
    if (/type=recovery/.test(location.hash)) return show("screen-reset");
    if (data.session) enterIfAdmin(); else show("screen-login");
  }
  init();
})();
