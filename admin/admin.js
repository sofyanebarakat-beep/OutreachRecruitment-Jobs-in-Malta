/* Outreach Recruitment — SEO Admin
 * Static admin for the 120-Day SEO course + KPI tracking.
 * Storage: Supabase when admin/config.js is filled in, otherwise localStorage.
 */
(() => {
  "use strict";
  const CFG = window.ADMIN_CONFIG || {};
  const C = window.COURSE;
  const G = window.COURSE_GUIDANCE || {};
  const M = window.COURSE_METRICS || {};
  const D = window.COURSE_DECISIONS || {};
  const H = window.COURSE_HOWTO || {};
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const DAY = 86400000;
  const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  const parseDate = (s) => { const [y, m, d] = String(s).slice(0, 10).split("-").map(Number); return new Date(y, m - 1, d); };
  const addDays = (s, n) => iso(new Date(parseDate(s).getTime() + n * DAY));
  const today = () => iso(new Date());
  const fmtInt = (n) => (n == null || isNaN(n) ? "–" : Math.round(n).toLocaleString("en-GB"));
  const fmt1 = (n) => (n == null || isNaN(n) ? "–" : (+n).toFixed(1));
  const fmtPct = (n) => (n == null || isNaN(n) ? "–" : (+n).toFixed(2) + "%");
  const num = (v) => { if (v === "" || v == null) return null; const n = Number(String(v).replace(/[%,\s]/g, "")); return isNaN(n) ? null : n; };

  function toast(msg) {
    const t = $("#toast"); t.textContent = msg; t.hidden = false;
    clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), 2600);
  }

  // ─────────────────────────── Storage ───────────────────────────
  const Store = {
    sb: null,
    mode: "local",
    cache: {},
    init() {
      if (CFG.SUPABASE_URL && CFG.SUPABASE_ANON_KEY && window.supabase) {
        this.sb = window.supabase.createClient(CFG.SUPABASE_URL, CFG.SUPABASE_ANON_KEY);
        this.mode = "supabase";
      }
    },
    lsKey: (t) => "seoadmin:" + t,
    lsGet(t) { try { return JSON.parse(localStorage.getItem(this.lsKey(t)) || "[]"); } catch { return []; } },
    lsSet(t, rows) { try { localStorage.setItem(this.lsKey(t), JSON.stringify(rows)); } catch (e) { toast("Browser storage full or blocked"); } },
    async list(t, { force = false } = {}) {
      if (!force && this.cache[t]) return this.cache[t];
      let rows;
      if (this.mode === "supabase") {
        const { data, error } = await this.sb.from(t).select("*").limit(5000);
        if (error) { toast(t + ": " + error.message); rows = []; } else rows = data;
      } else rows = this.lsGet(t);
      this.cache[t] = rows;
      return rows;
    },
    // conflict = column name used to match existing rows (default id)
    async upsert(t, row, conflict = "id") {
      delete this.cache[t];
      if (this.mode === "supabase") {
        const clean = { ...row };
        if (conflict === "id" && !clean.id) delete clean.id;
        delete clean.created_at; delete clean.updated_at;
        const q = clean.id || conflict !== "id"
          ? this.sb.from(t).upsert(clean, { onConflict: conflict })
          : this.sb.from(t).insert(clean);
        const { data, error } = await q.select().single();
        if (error) { toast("Save failed: " + error.message); throw error; }
        return data;
      }
      const rows = this.lsGet(t);
      const key = conflict === "id" ? "id" : conflict;
      const i = row[key] != null ? rows.findIndex((r) => r[key] === row[key]) : -1;
      const now = new Date().toISOString();
      let out;
      if (i >= 0) { out = { ...rows[i], ...row, updated_at: now }; rows[i] = out; }
      else { out = { id: (crypto.randomUUID && crypto.randomUUID()) || String(Date.now() + Math.random()), created_at: now, ...row, updated_at: now }; rows.push(out); }
      this.lsSet(t, rows);
      return out;
    },
    async remove(t, id) {
      delete this.cache[t];
      if (this.mode === "supabase") {
        const { error } = await this.sb.from(t).delete().eq("id", id);
        if (error) { toast("Delete failed: " + error.message); throw error; }
        return;
      }
      this.lsSet(t, this.lsGet(t).filter((r) => r.id !== id));
    },
    async getSetting(key, fallback) {
      const rows = await this.list("seo_settings");
      const r = rows.find((x) => x.key === key);
      return r ? r.value : fallback;
    },
    async setSetting(key, value) { return this.upsert("seo_settings", { key, value }, "key"); },
    async getWeek(n) {
      const rows = await this.list("seo_course_weeks");
      const r = rows.find((x) => x.week === n);
      return r ? r.data || {} : {};
    },
    async setWeek(n, data) { return this.upsert("seo_course_weeks", { week: n, data }, "week"); },
  };

  const ALL_TABLES = ["seo_settings", "seo_kpi_daily", "seo_keywords", "seo_pages", "seo_content", "seo_technical",
    "seo_backlinks", "seo_local", "seo_ai_visibility", "seo_experiments", "seo_sector_opportunities", "seo_alerts",
    "seo_opportunities", "seo_evidence", "seo_decisions", "seo_course_weeks"];
  const CONFLICT = { seo_settings: "key", seo_kpi_daily: "date", seo_keywords: "source_key", seo_pages: "source_key",
    seo_technical: "source_key", seo_experiments: "source_key", seo_sector_opportunities: "sector", seo_alerts: "source_key",
    seo_opportunities: "source_key", seo_course_weeks: "week" };

  // ─────────────────────────── Tracker definitions ───────────────────────────
  const SECTORS = C.sectors.map((s) => s[0]).concat(["General", "Employer", "Other"]);
  const TRACKERS = {
    seo_kpi_daily: {
      title: "Daily KPI tracking", tab: "02 Daily Tracking", weeks: [1, 16], sort: ["date", -1],
      intro: "Automatically filled each morning from Search Console and GA4. CSV import remains available as a fallback.",
      cols: [
        { k: "date", l: "Date", t: "date", req: true },
        { k: "clicks", l: "Clicks", t: "int" },
        { k: "impressions", l: "Impr.", t: "int" },
        { k: "ctr", l: "CTR %", t: "num" },
        { k: "avg_position", l: "Avg pos.", t: "num" },
        { k: "organic_users", l: "Organic users", t: "int" },
        { k: "applications", l: "Applications", t: "int" },
        { k: "employer_leads", l: "Employer leads", t: "int" },
        { k: "ai_referrals", l: "AI referrals", t: "int" },
        { k: "notes", l: "Notes", t: "text", wide: true },
      ],
      aliases: { date: "date", day: "date", clicks: "clicks", impressions: "impressions", ctr: "ctr", position: "avg_position", averageposition: "avg_position", users: "organic_users", totalusers: "organic_users", activeusers: "organic_users", applications: "applications", leads: "employer_leads", employerleads: "employer_leads" },
    },
    seo_keywords: {
      title: "Keywords", tab: "03 Keywords", weeks: [2], sort: ["current_position", 1],
      intro: "One primary target page per important keyword. Paste a GSC “Queries” export to bulk-add (Top queries → keyword, Position → current position).",
      cols: [
        { k: "keyword", l: "Keyword", t: "str", req: true },
        { k: "intent", l: "Intent", t: "sel", o: ["candidate", "employer", "commercial", "informational", "navigational"] },
        { k: "sector", l: "Sector", t: "sel", o: SECTORS },
        { k: "target_url", l: "Target URL", t: "str" },
        { k: "volume", l: "Volume / impr.", t: "int" },
        { k: "baseline_position", l: "Baseline pos.", t: "num" },
        { k: "current_position", l: "Current pos.", t: "num" },
        { k: "target_position", l: "Target pos.", t: "num" },
        { k: "notes", l: "Notes", t: "text", wide: true, hide: true },
      ],
      computed: [{ l: "Δ pos.", f: (r) => (r.baseline_position != null && r.current_position != null ? +(r.baseline_position - r.current_position).toFixed(1) : null), cls: (v) => (v > 0 ? "up" : v < 0 ? "down" : "flat") }],
      aliases: { topqueries: "keyword", query: "keyword", keyword: "keyword", position: "current_position", impressions: "volume", intent: "intent", sector: "sector", targeturl: "target_url" },
      onImport: (r) => { if (r.current_position != null && r.baseline_position == null) r.baseline_position = r.current_position; return r; },
    },
    seo_pages: {
      title: "Pages", tab: "04 Pages", weeks: [3, 5, 8], sort: ["impressions", -1],
      intro: "Page-level performance and the decision for each page. Paste a GSC “Pages” export, or send opportunities here from Live site data.",
      cols: [
        { k: "url", l: "URL", t: "str", req: true },
        { k: "target_query", l: "Target query", t: "str" },
        { k: "clicks", l: "Clicks", t: "int" },
        { k: "impressions", l: "Impr.", t: "int" },
        { k: "ctr", l: "CTR %", t: "num" },
        { k: "position", l: "Pos.", t: "num" },
        { k: "conversions", l: "Conv.", t: "int" },
        { k: "action", l: "Action", t: "sel", o: ["keep", "improve content", "improve title/CTR", "add internal links", "consolidate", "remove/redirect"] },
        { k: "notes", l: "Notes", t: "text", wide: true, hide: true },
      ],
      aliases: { toppages: "url", page: "url", url: "url", clicks: "clicks", impressions: "impressions", ctr: "ctr", position: "position" },
    },
    seo_content: {
      title: "Content", tab: "05 Content", weeks: [6, 7, 13, 14], sort: ["publish_date", -1],
      intro: "Content ideas, clusters, AEO questions and GEO upgrades — from idea to published result.",
      cols: [
        { k: "idea", l: "Idea / question", t: "str", req: true },
        { k: "cluster", l: "Cluster", t: "sel", o: ["Jobs in Malta pillar", ...C.sectors.map((s) => s[0] + " jobs"), "Employer / hiring", "CV & interview", "Relocation & permits", "AEO question", "GEO resource", "Other"] },
        { k: "intent", l: "Intent", t: "sel", o: ["candidate", "employer", "informational", "commercial"] },
        { k: "status", l: "Status", t: "sel", o: ["idea", "brief", "writing", "published", "refresh"] },
        { k: "url", l: "URL", t: "str" },
        { k: "publish_date", l: "Publish/update", t: "date" },
        { k: "results", l: "Results", t: "text", wide: true },
      ],
    },
    seo_technical: {
      title: "Technical", tab: "06 Technical", weeks: [4], sort: ["severity", 1],
      intro: "Technical issues by severity. Critical → High → Medium → Low.",
      cols: [
        { k: "issue", l: "Issue", t: "str", req: true },
        { k: "severity", l: "Severity", t: "sel", o: ["Critical", "High", "Medium", "Low"] },
        { k: "url", l: "Affected URL", t: "str" },
        { k: "owner", l: "Owner", t: "str" },
        { k: "status", l: "Status", t: "sel", o: ["open", "in progress", "fixed", "validated"] },
        { k: "fix_date", l: "Fix date", t: "date" },
        { k: "validation", l: "Validation", t: "text", wide: true },
      ],
      sortRank: { severity: { Critical: 0, High: 1, Medium: 2, Low: 3 } },
    },
    seo_backlinks: {
      title: "Backlinks", tab: "07 Backlinks", weeks: [11, 12], sort: ["relevance", -1],
      intro: "Relevant, legitimate prospects only. Score relevance and legitimacy 1–5.",
      cols: [
        { k: "prospect", l: "Prospect", t: "str", req: true },
        { k: "site_url", l: "Site", t: "str" },
        { k: "relevance", l: "Relevance", t: "sel", o: ["1", "2", "3", "4", "5"], int: true },
        { k: "legitimacy", l: "Legitimacy", t: "sel", o: ["1", "2", "3", "4", "5"], int: true },
        { k: "contact", l: "Contact", t: "str" },
        { k: "status", l: "Status", t: "sel", o: ["prospect", "contacted", "replied", "acquired", "rejected"] },
        { k: "target_url", l: "Target URL", t: "str" },
        { k: "acquired_link", l: "Acquired link", t: "str" },
        { k: "notes", l: "Notes", t: "text", wide: true, hide: true },
      ],
    },
    seo_local: {
      title: "Local", tab: "08 Local", weeks: [9, 10], sort: ["date", -1],
      intro: "Profile, citation, review and location-page actions. Only real, accurate business information.",
      cols: [
        { k: "action", l: "Action", t: "str", req: true },
        { k: "type", l: "Type", t: "sel", o: ["profile", "citation", "review", "NAP check", "location page"] },
        { k: "platform", l: "Platform", t: "str" },
        { k: "status", l: "Status", t: "sel", o: ["todo", "in progress", "done"] },
        { k: "date", l: "Date", t: "date" },
        { k: "url", l: "URL", t: "str" },
        { k: "notes", l: "Notes", t: "text", wide: true },
      ],
    },
    seo_ai_visibility: {
      title: "AI visibility", tab: "09 AI Visibility", weeks: [15], sort: ["date", -1],
      intro: "Fixed question set, dated observations. Repeat on the same schedule; one answer is an anecdote, not a trend.",
      cols: [
        { k: "date", l: "Date", t: "date", req: true },
        { k: "question", l: "Question", t: "str", req: true },
        { k: "engine", l: "Engine", t: "sel", o: ["Google AI Overview", "Google AI Mode", "ChatGPT", "Perplexity", "Gemini", "Copilot", "Claude"] },
        { k: "surfaced", l: "Surfaced", t: "bool" },
        { k: "cited", l: "Cited", t: "bool" },
        { k: "referral_sessions", l: "Referral sessions", t: "int" },
        { k: "competitors", l: "Competitors shown", t: "str" },
        { k: "result", l: "Result / notes", t: "text", wide: true },
      ],
    },
    seo_experiments: {
      title: "Experiments", tab: "10 Experiments", weeks: [3, 8], sort: ["start_date", -1],
      intro: "One change, one hypothesis, before/after data. Review at 7d / 30d / 60d / 90d.",
      cols: [
        { k: "change", l: "Change", t: "str", req: true },
        { k: "hypothesis", l: "Hypothesis", t: "text", wide: true },
        { k: "page", l: "Page", t: "str" },
        { k: "start_date", l: "Start", t: "date" },
        { k: "review_date", l: "Review", t: "date" },
        { k: "before_data", l: "Before", t: "text", hide: true },
        { k: "after_data", l: "After", t: "text", hide: true },
        { k: "conclusion", l: "Conclusion", t: "text", wide: true },
      ],
    },
    seo_sector_opportunities: {
      title: "Sector opportunities", tab: "Week 5 opportunity table", weeks: [5, 10], sort: ["impressions", -1],
      intro: "Automatically combines open jobs with Search Console performance. Prioritise sectors with demand, enough vacancies and a weak/missing landing page.",
      cols: [
        { k: "sector", l: "Sector", t: "str", req: true },
        { k: "open_jobs", l: "Open jobs", t: "int" },
        { k: "sector_page_exists", l: "Sector page?", t: "bool" },
        { k: "url", l: "Sector URL", t: "str" },
        { k: "impressions", l: "Impressions", t: "int" },
        { k: "avg_position", l: "Avg position", t: "num" },
      ],
    },
    seo_alerts: {
      title: "SEO alerts", tab: "Automatic alerts", weeks: [1, 4, 8, 16], sort: ["created_at", -1],
      intro: "Automatic warnings for keyword drops, lost impressions and indexing delays. Mark resolved after investigating.",
      cols: [
        { k: "severity", l: "Severity", t: "sel", o: ["Critical", "High", "Medium", "Low"] },
        { k: "type", l: "Type", t: "str" },
        { k: "message", l: "Alert", t: "text", wide: true, req: true },
        { k: "url", l: "URL", t: "str" },
        { k: "resolved", l: "Resolved", t: "bool" },
      ],
    },
    seo_opportunities: {
      title: "Opportunity inbox", tab: "Guided practice queue", weeks: [2, 3, 4, 5, 8], sort: ["priority", 1],
      intro: "Automatically generated practice opportunities from real Search Console, audit, sector and job data. Choose one focused item, then open Guided practice.",
      cols: [
        { k: "priority", l: "Priority", t: "sel", o: ["Critical", "High", "Medium", "Low"] },
        { k: "category", l: "Category", t: "str" },
        { k: "title", l: "Opportunity", t: "str", req: true },
        { k: "course_week", l: "Week", t: "int" },
        { k: "impact", l: "Impact 1–5", t: "int" },
        { k: "effort", l: "Effort 1–5", t: "int" },
        { k: "url", l: "URL", t: "str" },
        { k: "status", l: "Status", t: "sel", o: ["new", "selected", "in progress", "experiment", "complete", "dismissed"] },
        { k: "explanation", l: "Why it matters", t: "text", wide: true, hide: true },
        { k: "recommended_action", l: "Recommended action", t: "text", wide: true, hide: true },
      ],
      computed: [{ l: "Score", f: (r) => r.impact && r.effort ? Math.round((+r.impact * 20) / Math.max(1, +r.effort)) : null, cls: (v) => v >= 40 ? "up" : v >= 20 ? "flat" : "down" }],
      sortRank: { priority: { Critical: 0, High: 1, Medium: 2, Low: 3 } },
    },
    seo_evidence: {
      title: "Evidence locker", tab: "Course evidence", weeks: [1, 16], sort: ["captured_at", -1],
      intro: "Save proof of practical work here. Link every useful screenshot, export, test, document, published page or commit to its course week.",
      cols: [
        { k: "week", l: "Week", t: "int", req: true },
        { k: "task_index", l: "Task", t: "int" },
        { k: "type", l: "Evidence type", t: "sel", o: ["screenshot", "export", "report", "test", "commit", "published page", "document", "other"] },
        { k: "title", l: "Evidence", t: "str", req: true },
        { k: "url", l: "Link / file URL", t: "str" },
        { k: "captured_at", l: "Date", t: "date" },
        { k: "notes", l: "What this proves", t: "text", wide: true },
      ],
    },
  };

  // ─────────────────────────── KPI helpers ───────────────────────────
  const KPI_KEYS = [
    ["clicks", "Clicks", "sum"], ["impressions", "Impressions", "sum"], ["ctr", "CTR", "ctr"],
    ["avg_position", "Avg. position", "pos"], ["organic_users", "Organic users", "sum"],
    ["applications", "Applications", "sum"], ["employer_leads", "Employer leads", "sum"],
    ["ai_referrals", "AI referral sessions", "sum"],
  ];
  function aggregate(rows, from, to) {
    const r = rows.filter((x) => x.date >= from && x.date <= to);
    const sum = (k) => { const v = r.filter((x) => x[k] != null && x[k] !== ""); return v.length ? v.reduce((a, x) => a + +x[k], 0) : null; };
    const clicks = sum("clicks"), impressions = sum("impressions");
    let pos = null;
    const pr = r.filter((x) => x.avg_position != null && x.avg_position !== "");
    if (pr.length) {
      const w = pr.reduce((a, x) => a + (+x.impressions || 1), 0);
      pos = pr.reduce((a, x) => a + +x.avg_position * (+x.impressions || 1), 0) / w;
    }
    return {
      days: r.length, clicks, impressions,
      ctr: clicks != null && impressions ? (clicks / impressions) * 100 : null,
      avg_position: pos, organic_users: sum("organic_users"),
      applications: sum("applications"), employer_leads: sum("employer_leads"), ai_referrals: sum("ai_referrals"),
    };
  }
  function delta(cur, prev, kind) {
    if (cur == null || prev == null) return { txt: "–", cls: "flat" };
    if (kind === "pos") { const d = prev - cur; return { txt: (d >= 0 ? "▲ " : "▼ ") + Math.abs(d).toFixed(1), cls: d > 0 ? "up" : d < 0 ? "down" : "flat" }; }
    if (kind === "ctr") { const d = cur - prev; return { txt: (d >= 0 ? "+" : "") + d.toFixed(2) + " pts", cls: d > 0 ? "up" : d < 0 ? "down" : "flat" }; }
    if (!prev) return { txt: cur ? "new" : "–", cls: cur ? "up" : "flat" };
    const p = ((cur - prev) / prev) * 100;
    return { txt: (p >= 0 ? "+" : "") + p.toFixed(1) + "%", cls: p > 0 ? "up" : p < 0 ? "down" : "flat" };
  }
  const fmtKpi = (v, kind) => (kind === "ctr" ? fmtPct(v) : kind === "pos" ? fmt1(v) : fmtInt(v));
  const kpiDef = (key) => KPI_KEYS.find(([k]) => k === key) || [key, key, "sum"];
  function suggestedKpiAction(key, cur, prev) {
    const [, label, kind] = kpiDef(key);
    if (cur == null || prev == null) return `Add complete ${label.toLowerCase()} data for both 7-day periods before deciding.`;
    const change = kind === "pos" ? prev - cur : cur - prev;
    if (change > 0) return `Identify what contributed to the ${label.toLowerCase()} improvement; preserve it and test the same pattern on one comparable page.`;
    if (change < 0) return `Investigate the ${label.toLowerCase()} decline by page, query and date; choose one focused corrective action and set a review date.`;
    return `No clear ${label.toLowerCase()} movement yet; keep the test stable, check data completeness and review again at the planned interval.`;
  }
  const REVIEW_DAYS = [7, 30, 30, 21, 30, 30, 30, 30, 30, 60, 60, 60, 30, 30, 30, 90];
  function dataConfidence(cur, prev, keys) {
    const missing = keys.some((k) => cur[k] == null || prev[k] == null);
    const small = keys.some((k) => ["applications", "employer_leads", "ai_referrals"].includes(k) && ((cur[k] || 0) + (prev[k] || 0) < 10));
    if (missing || cur.days < 5 || prev.days < 5) return { label: "Low confidence", cls: "bad", note: "Missing days or KPI values. Complete both periods before making a change." };
    if (cur.days < 7 || prev.days < 7 || small) return { label: "Medium confidence", cls: "warn", note: small ? "Comparable data, but the conversion sample is small." : "One period is incomplete; treat the result as directional." };
    return { label: "High confidence", cls: "good", note: "Both periods contain seven days of comparable data." };
  }
  function patternInsight(cur, prev) {
    if ([cur.impressions, prev.impressions, cur.clicks, prev.clicks].some((v) => v == null)) return "Complete the Search Console comparison before interpreting the pattern.";
    const imp = cur.impressions - prev.impressions, clicks = cur.clicks - prev.clicks;
    const conv = (cur.applications || 0) + (cur.employer_leads || 0) - (prev.applications || 0) - (prev.employer_leads || 0);
    if (imp > 0 && clicks <= 0) return "Visibility increased without more clicks. Inspect ranking position, query intent, title and description.";
    if (clicks > 0 && conv <= 0) return "Clicks increased without more recorded conversions. Inspect landing-page relevance, CTA clarity and tracking.";
    if (clicks <= 0 && conv > 0) return "Conversions improved without more clicks. Identify the pages or journeys with better conversion quality.";
    if (imp > 0 && clicks > 0 && conv > 0) return "Visibility, clicks and conversions moved together. Preserve the change and test it on one comparable page.";
    return "No decisive combined pattern yet. Keep the test stable and review at the recommended interval.";
  }

  // ─────────────────────────── Course helpers ───────────────────────────
  async function courseCtx() {
    const start = await Store.getSetting("course_start", today());
    const day = Math.floor((parseDate(today()) - parseDate(start)) / DAY) + 1;
    const week = Math.min(16, Math.max(1, Math.ceil(day / 7)));
    return { start, day, week, dayInWeek: day >= 1 ? ((day - 1) % 7) : 0 };
  }
  const weekRange = (start, n) => [addDays(start, (n - 1) * 7), addDays(start, n * 7 - 1)];

  async function courseScore() {
    const weeks = await Store.list("seo_course_weeks");
    const byW = Object.fromEntries(weeks.map((w) => [w.week, w.data || {}]));
    let tasksTotal = 0, tasksDone = 0, qMarks = 0, qTotal = 0, reviewed = 0, delivered = 0;
    C.weeks.forEach((w) => {
      const d = byW[w.n] || {};
      tasksTotal += w.tasks.length;
      tasksDone += w.tasks.filter((_, i) => d.tasks?.[i]?.done).length;
      qTotal += w.qcm.length;
      w.qcm.forEach((_, i) => { const m = d.qcm?.[i]?.mark; qMarks += m === "correct" ? 1 : m === "partial" ? 0.5 : 0; });
      if (d.resume?.next || Object.values(d.kpiActions || {}).some(Boolean)) reviewed++;
      if (d.deliverable?.done) delivered++;
    });
    const ctx = await courseCtx();
    const kpi = await Store.list("seo_kpi_daily");
    const end = addDays(ctx.start, 119);
    const elapsed = Math.min(120, Math.max(1, ctx.day));
    const logged = kpi.filter((r) => r.date >= ctx.start && r.date <= end).length;
    const trackingPct = Math.min(1, 0.6 * (logged / elapsed) + 0.4 * (reviewed / Math.max(1, Math.min(16, ctx.week))));
    const w0 = byW[0] || {};
    const monthsDone = [1, 2, 3, 4].filter((m) => w0.months?.[m]?.done).length;
    const finalDone = w0.final?.done ? 1 : 0;
    const parts = {
      qcm: qTotal ? qMarks / qTotal : 0,
      practical: tasksTotal ? tasksDone / tasksTotal : 0,
      tracking: trackingPct,
      monthly: monthsDone / 4,
      final: finalDone,
    };
    const total = Object.entries(C.weights).reduce((a, [k, w]) => a + parts[k] * w, 0);
    return { parts, total, tasksDone, tasksTotal, delivered, logged, elapsed, byW };
  }

  // ─────────────────────────── Charts ───────────────────────────
  function lineChart(points, { format = fmtInt, invert = false } = {}) {
    const id = "c" + Math.random().toString(36).slice(2, 8);
    if (points.length < 2) return `<div class="empty">Need at least 2 days of data to draw a trend.</div>`;
    const W = 640, H = 190, L = 44, R = 10, T = 10, B = 24;
    const ys = points.map((p) => p.y);
    let min = Math.min(...ys), max = Math.max(...ys);
    if (!invert) min = Math.min(0, min);
    if (max === min) max = min + 1;
    const pad = (max - min) * 0.08; if (invert) { min -= pad; } max += pad;
    const x = (i) => L + (i / (points.length - 1)) * (W - L - R);
    const y = (v) => invert ? T + ((v - min) / (max - min)) * (H - T - B) : H - B - ((v - min) / (max - min)) * (H - T - B);
    const ticks = [0, 0.5, 1].map((f) => min + f * (max - min));
    const path = points.map((p, i) => (i ? "L" : "M") + x(i).toFixed(1) + "," + y(p.y).toFixed(1)).join("");
    const area = invert ? "" : `<path class="area" d="${path}L${x(points.length - 1)},${H - B}L${x(0)},${H - B}Z"/>`;
    const xl = [0, Math.floor((points.length - 1) / 2), points.length - 1];
    const svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="trend chart">
      ${ticks.map((t) => `<line class="grid-line" x1="${L}" x2="${W - R}" y1="${y(t)}" y2="${y(t)}"/><text class="axis-label" x="${L - 6}" y="${y(t) + 4}" text-anchor="end">${esc(format(t))}</text>`).join("")}
      ${area}<path class="line" d="${path}"/>
      ${xl.map((i) => `<text class="axis-label" x="${x(i)}" y="${H - 6}" text-anchor="${i === 0 ? "start" : i === points.length - 1 ? "end" : "middle"}">${esc(points[i].x.slice(5))}</text>`).join("")}
      <line class="cross" id="${id}-x" y1="${T}" y2="${H - B}" visibility="hidden"/>
      <circle class="dot" id="${id}-d" r="4.5" visibility="hidden"/>
      <rect id="${id}-hit" x="${L}" y="0" width="${W - L - R}" height="${H}" fill="transparent"/>
    </svg>`;
    setTimeout(() => {
      const hit = document.getElementById(id + "-hit"); if (!hit) return;
      const svgEl = hit.ownerSVGElement, wrap = svgEl.parentElement;
      const tip = wrap.querySelector(".tooltip"), cx = document.getElementById(id + "-x"), dot = document.getElementById(id + "-d");
      const move = (ev) => {
        const rect = svgEl.getBoundingClientRect();
        const px = ((ev.clientX - rect.left) / rect.width) * W;
        const i = Math.max(0, Math.min(points.length - 1, Math.round(((px - L) / (W - L - R)) * (points.length - 1))));
        const X = x(i), Y = y(points[i].y);
        cx.setAttribute("x1", X); cx.setAttribute("x2", X); cx.setAttribute("visibility", "visible");
        dot.setAttribute("cx", X); dot.setAttribute("cy", Y); dot.setAttribute("visibility", "visible");
        tip.hidden = false; tip.textContent = points[i].x + " · " + format(points[i].y);
        tip.style.left = (X / W) * rect.width + "px"; tip.style.top = (Y / H) * rect.height + "px";
      };
      const out = () => { tip.hidden = true; cx.setAttribute("visibility", "hidden"); dot.setAttribute("visibility", "hidden"); };
      hit.addEventListener("mousemove", move); hit.addEventListener("mouseleave", out);
      hit.addEventListener("touchstart", (e) => move(e.touches[0]), { passive: true });
    });
    return `<div class="chart">${svg}<div class="tooltip" hidden></div></div>`;
  }

  // ─────────────────────────── CSV ───────────────────────────
  function parseCSV(text) {
    const rows = []; let row = [], cell = "", q = false;
    text = text.replace(/^﻿/, "");
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
      else if (c === '"') q = true;
      else if (c === "," || c === "\t") { row.push(cell); cell = ""; }
      else if (c === "\n" || c === "\r") { if (c === "\r" && text[i + 1] === "\n") i++; row.push(cell); rows.push(row); row = []; cell = ""; }
      else cell += c;
    }
    if (cell !== "" || row.length) { row.push(cell); rows.push(row); }
    const nonEmpty = rows.filter((r) => r.some((c) => c.trim() !== ""));
    if (!nonEmpty.length) return [];
    const head = nonEmpty[0].map((h) => h.trim());
    return nonEmpty.slice(1).map((r) => Object.fromEntries(head.map((h, i) => [h, (r[i] ?? "").trim()])));
  }
  const toCSV = (cols, rows) => [cols.map((c) => c.l).join(","), ...rows.map((r) => cols.map((c) => { const v = r[c.k] ?? ""; return /[",\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v; }).join(","))].join("\n");
  function download(name, text, type = "text/plain") {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type }));
    a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  const oneColumnCSV = (heading, rows) => [heading, ...rows].map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`).join("\n");
  async function copyPlainText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const area = document.createElement("textarea");
      area.value = text; area.style.position = "fixed"; area.style.opacity = "0";
      document.body.appendChild(area); area.select();
      const copied = document.execCommand("copy");
      area.remove();
      return copied;
    }
  }
  function coerce(col, v) {
    if (v === "" || v == null) return null;
    if (col.t === "int" || col.int) { const n = num(v); return n == null ? null : Math.round(n); }
    if (col.t === "num") return num(v);
    if (col.t === "bool") return v === true || /^(true|yes|1|y)$/i.test(String(v));
    if (col.t === "date") { const d = new Date(v); return isNaN(d) ? String(v).slice(0, 10) : iso(d); }
    return String(v);
  }

  // ─────────────────────────── Modal ───────────────────────────
  function openModal(html, bind) {
    $("#modal-body").innerHTML = html; $("#modal").hidden = false;
    bind && bind($("#modal-body"));
  }
  const closeModal = () => { $("#modal").hidden = true; $("#modal-body").innerHTML = ""; };
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });
  $("#modal").addEventListener("click", (e) => { if (e.target.id === "modal") closeModal(); });

  function fieldHTML(c, v) {
    const name = `name="${c.k}"`, req = c.req ? "required" : "";
    let input;
    if (c.t === "text") input = `<textarea ${name}>${esc(v)}</textarea>`;
    else if (c.t === "sel") input = `<select ${name}><option value=""></option>${c.o.map((o) => `<option ${String(v) === o ? "selected" : ""}>${esc(o)}</option>`).join("")}</select>`;
    else if (c.t === "bool") return `<label><input type="checkbox" ${name} ${v ? "checked" : ""}> ${esc(c.l)}</label>`;
    else {
      const type = c.t === "date" ? "date" : c.t === "int" || c.t === "num" ? "number" : "text";
      const step = c.t === "num" ? 'step="any"' : c.t === "int" ? 'step="1"' : "";
      input = `<input type="${type}" ${step} ${name} ${req} value="${esc(v)}">`;
    }
    return `<label class="${c.wide ? "wide" : ""}">${esc(c.l)}${input}</label>`;
  }
  function editRow(table, row, after) {
    const def = TRACKERS[table];
    const isNew = !row.id;
    openModal(`<form id="edit-form">
      <div class="row spread"><h2>${isNew ? "Add" : "Edit"} · ${esc(def.title)}</h2><button type="button" class="btn ghost" data-close>✕</button></div>
      <div class="form-grid">${def.cols.map((c) => fieldHTML(c, row[c.k])).join("")}</div>
      <div class="row spread"><div>${isNew ? "" : '<button type="button" class="btn danger" data-del>Delete</button>'}</div>
      <div class="row"><button type="button" class="btn" data-close>Cancel</button><button class="btn primary">Save</button></div></div>
    </form>`, (el) => {
      $$("[data-close]", el).forEach((b) => (b.onclick = closeModal));
      const del = $("[data-del]", el);
      if (del) del.onclick = async () => { if (!confirm("Delete this row?")) return; await Store.remove(table, row.id); closeModal(); toast("Deleted"); after(); };
      $("#edit-form", el).onsubmit = async (e) => {
        e.preventDefault();
        const f = e.target, out = isNew ? {} : { id: row.id };
        def.cols.forEach((c) => { const inp = f.elements[c.k]; out[c.k] = c.t === "bool" ? inp.checked : coerce(c, inp.value); });
        const conflict = CONFLICT[table] && isNew ? CONFLICT[table] : "id";
        await Store.upsert(table, out, conflict); closeModal(); toast("Saved"); after();
      };
    });
  }

  function importDialog(table, after) {
    const def = TRACKERS[table];
    openModal(`<div class="row spread"><h2>Import CSV · ${esc(def.title)}</h2><button class="btn ghost" data-close>✕</button></div>
      <p class="muted">Upload or paste a CSV (Search Console / GA4 exports work). Matched columns: ${def.cols.map((c) => esc(c.l)).join(", ")}.${CONFLICT[table] ? ` Rows with an existing <b>${CONFLICT[table]}</b> are updated, not duplicated.` : ""}</p>
      <input type="file" accept=".csv,.tsv,.txt" id="imp-file"><p></p>
      <textarea id="imp-text" placeholder="…or paste CSV here" style="min-height:160px"></textarea>
      <p id="imp-preview" class="muted small"></p>
      <div class="row" style="justify-content:flex-end"><button class="btn" data-close>Cancel</button><button class="btn primary" id="imp-go">Import</button></div>`, (el) => {
      $$("[data-close]", el).forEach((b) => (b.onclick = closeModal));
      $("#imp-file", el).onchange = async (e) => { const f = e.target.files[0]; if (f) $("#imp-text", el).value = await f.text(); preview(); };
      $("#imp-text", el).oninput = preview;
      function mapRows() {
        const raw = parseCSV($("#imp-text", el).value);
        const norm = (h) => h.toLowerCase().replace(/[^a-z0-9]/g, "");
        return raw.map((r) => {
          const o = {};
          for (const [h, v] of Object.entries(r)) {
            const n = norm(h);
            const k = def.aliases?.[n] || def.cols.find((c) => norm(c.k) === n || norm(c.l) === n)?.k;
            if (!k) continue;
            const col = def.cols.find((c) => c.k === k);
            o[k] = coerce(col, v);
          }
          return def.onImport ? def.onImport(o) : o;
        }).filter((o) => def.cols.filter((c) => c.req).every((c) => o[c.k] != null && o[c.k] !== ""));
      }
      function preview() { const rows = mapRows(); $("#imp-preview", el).textContent = rows.length ? `${rows.length} rows ready · columns: ${Object.keys(rows[0]).join(", ")}` : "No importable rows detected yet."; }
      $("#imp-go", el).onclick = async () => {
        const rows = mapRows(); if (!rows.length) return toast("Nothing to import");
        $("#imp-go", el).disabled = true;
        let n = 0;
        for (const r of rows) { try { await Store.upsert(table, r, CONFLICT[table] || "id"); n++; } catch {} }
        closeModal(); toast(`Imported ${n} rows`); after();
      };
    });
  }

  // ─────────────────────────── Views ───────────────────────────
  const view = () => $("#view");

  async function renderDashboard() {
    const [kpi, ctx, score, evidence, experiments] = await Promise.all([Store.list("seo_kpi_daily"), courseCtx(), courseScore(), Store.list("seo_evidence"), Store.list("seo_experiments")]);
    const sorted = [...kpi].sort((a, b) => (a.date < b.date ? -1 : 1));
    const last = sorted.length ? sorted[sorted.length - 1].date : today();
    const cur = aggregate(kpi, addDays(last, -27), last);
    const prev = aggregate(kpi, addDays(last, -55), addDays(last, -28));
    const wk = C.weeks[ctx.week - 1];
    const loggedToday = kpi.some((r) => r.date === today());
    const recent = sorted.filter((r) => r.date >= addDays(last, -89));
    const B = CFG.BASELINE || {};
    const pct = (v) => Math.round(v * 100);
    const status = ctx.day < 1 ? `Starts ${ctx.start}` : ctx.day > 120 ? "Course complete — keep the monthly cycle" : `Day ${ctx.day} of 120`;
    const learningScore = Math.round(((score.parts.qcm + score.parts.practical) / 2) * 100);
    const practiceScore = Math.round(Math.min(1, (score.parts.tracking + score.parts.monthly + Math.min(1, evidence.length / 16) + Math.min(1, experiments.length / 8)) / 4) * 100);
    const comparable = [[cur.clicks, prev.clicks, false], [cur.impressions, prev.impressions, false], [cur.avg_position, prev.avg_position, true], [cur.applications, prev.applications, false], [cur.employer_leads, prev.employer_leads, false]].filter(([a, b]) => a != null && b != null);
    const businessScore = comparable.length ? Math.round(comparable.filter(([a, b, lower]) => lower ? a <= b : a >= b).length / comparable.length * 100) : 0;

    view().innerHTML = `
      <div class="page-head"><div><h1>Dashboard</h1><p class="muted">${esc(C.principle)}</p></div>
        <div class="row"><a class="btn primary" href="#/t/seo_kpi_daily?add=1">${loggedToday ? "Update" : "Log"} today's KPIs</a><a class="btn" href="#/course/${ctx.week}">Open week ${ctx.week}</a></div></div>

      <div class="grid c3">
        <div class="card"><div class="row spread"><h3>Course progress</h3><span class="badge info">${esc(status)}</span></div>
          <div class="progress"><span style="width:${Math.min(100, Math.max(0, (ctx.day / 120) * 100))}%"></span></div>
          <p class="small muted" style="margin-top:8px">Week ${ctx.week}: <b>${esc(wk.title)}</b><br>Today (${C.dailyRhythm.length ? "day " + (ctx.dayInWeek + 1) + " of week" : ""}): ${esc(C.dailyRhythm[ctx.dayInWeek])}</p></div>
        <div class="card"><div class="row spread"><h3>Course score</h3><span class="badge ${score.total >= C.passMark ? "good" : "warn"}">${score.total.toFixed(0)}% · pass ${C.passMark}%</span></div>
          ${Object.entries(C.weights).map(([k, w]) => `<div class="row spread small"><span>${{ qcm: "QCM / knowledge", practical: "Practical tasks", tracking: "Tracking & KPI", monthly: "Monthly projects", final: "Final case study" }[k]} <span class="muted">(${w}%)</span></span><span>${pct(score.parts[k])}%</span></div><div class="progress" style="margin-bottom:6px"><span style="width:${pct(score.parts[k])}%"></span></div>`).join("")}</div>
        <div class="card"><h3>Today's checklist</h3><ul class="checklist">
          <li class="${loggedToday ? "done" : ""}"><span>${loggedToday ? "✅" : "⬜"}</span><span class="txt grow">Daily SEO check — log clicks, impressions, users, applications, leads</span></li>
          <li><span>📘</span><span class="grow">${esc(C.dailyRhythm[ctx.dayInWeek])} — <a href="#/course/${ctx.week}">week ${ctx.week}</a></span></li>
          <li><span>📋</span><span class="grow">${score.tasksDone}/${score.tasksTotal} course tasks done · ${score.delivered}/16 deliverables</span></li>
          <li><span>📈</span><span class="grow">${score.logged} KPI days logged since course start</span></li></ul></div>
      </div>

      <div class="grid c3" style="margin-top:16px">
        <div class="card tile"><div class="label">Learning score</div><div class="value">${learningScore}%</div><div class="delta muted">Knowledge checks and completed learning tasks</div></div>
        <div class="card tile"><div class="label">Practice score</div><div class="value">${practiceScore}%</div><div class="delta muted">Tracking, evidence, deliverables and experiments</div></div>
        <div class="card tile"><div class="label">Business signal</div><div class="value">${businessScore}%</div><div class="delta muted">Share of comparable KPIs moving in the desired direction</div></div>
      </div>

      <h2 style="margin-top:20px">Last 28 days <span class="muted small">(${addDays(last, -27)} → ${last}, vs previous 28)</span></h2>
      ${kpi.length ? "" : `<div class="callout">No KPI data yet. Go to <a href="#/t/seo_kpi_daily">Daily KPI tracking</a> → <b>Import CSV</b> and paste your Search Console “Dates” export to fill the history in one go.</div>`}
      <div class="grid c4">${KPI_KEYS.map(([k, l, kind]) => { const d = delta(cur[k], prev[k], kind); return `<div class="card tile"><div class="label">${l}</div><div class="value">${fmtKpi(cur[k], kind)}</div><div class="delta ${d.cls}">${d.txt}</div></div>`; }).join("")}
        <div class="card tile"><div class="label">Baseline ${esc(B.date || "")} (28d)</div><div class="value">${fmtInt(B.clicks28)}</div><div class="delta muted">clicks · ${fmtInt(B.impressions28)} impr.</div></div></div>

      <div class="grid c2" style="margin-top:16px">
        <div class="card"><h3>Clicks per day</h3>${lineChart(recent.filter((r) => r.clicks != null).map((r) => ({ x: r.date, y: +r.clicks })))}</div>
        <div class="card"><h3>Impressions per day</h3>${lineChart(recent.filter((r) => r.impressions != null).map((r) => ({ x: r.date, y: +r.impressions })))}</div>
        <div class="card"><h3>Average position per day <span class="muted small">(lower is better)</span></h3>${lineChart(recent.filter((r) => r.avg_position != null).map((r) => ({ x: r.date, y: +r.avg_position })), { format: fmt1, invert: true })}</div>
        <div class="card"><h3>Applications per day</h3>${lineChart(recent.filter((r) => r.applications != null).map((r) => ({ x: r.date, y: +r.applications })))}</div>
      </div>
      <div class="card" id="dash-signals"><h3>Decision signals</h3><p class="muted">Loading live site data…</p></div>`;

    const signals = await decisionSignals(cur, prev);
    const el = $("#dash-signals"); if (el) el.innerHTML = `<h3>Decision signals</h3>${signals}`;
  }

  async function decisionSignals(cur, prev) {
    const out = [];
    const live = await loadLive().catch(() => null);
    if (live?.gsc) {
      const g = live.gsc;
      out.push(`<li><b>${g.p4_10.length}</b> job pages at position 4-10 → protect & strengthen (framework #2). <a href="#/live">See list</a></li>`);
      out.push(`<li><b>${g.p11_20.length}</b> job pages at position 11-20 → growth candidates (framework #3).</li>`);
      out.push(`<li><b>${g.lowCtr.length}</b> pages with high impressions and low CTR → check title/snippet (framework #1).</li>`);
    }
    if (cur.clicks != null && prev.clicks && cur.applications != null && prev.applications != null) {
      const t = (cur.clicks - prev.clicks) / prev.clicks, a = prev.applications ? (cur.applications - prev.applications) / prev.applications : 0;
      if (t > 0.1 && a <= 0.02) out.push(`<li><span class="badge warn">Watch</span> Traffic up ${(t * 100).toFixed(0)}% but applications flat → review audience fit and CTA path (framework #4).</li>`);
      if (a > 0.1 && Math.abs(t) < 0.05) out.push(`<li><span class="badge good">Win</span> Applications up with flat traffic → find what lifted conversion and replicate (framework #5).</li>`);
    }
    const tech = (await Store.list("seo_technical")).filter((r) => !["fixed", "validated"].includes(r.status));
    const crit = tech.filter((r) => r.severity === "Critical" || r.severity === "High").length;
    if (tech.length) out.push(`<li><b>${tech.length}</b> open technical issues (${crit} Critical/High). <a href="#/t/seo_technical">Open tracker</a></li>`);
    const exps = (await Store.list("seo_experiments")).filter((r) => r.review_date && r.review_date <= today() && !r.conclusion);
    if (exps.length) out.push(`<li><span class="badge info">Due</span> ${exps.length} experiment(s) due for review. <a href="#/t/seo_experiments">Review</a></li>`);
    return out.length ? `<ul>${out.join("")}</ul>` : `<p class="muted">No signals yet — add data to the trackers.</p>`;
  }

  // ── Live site data (real data from the repo) ──
  let LIVE = null;
  async function loadLive() {
    if (LIVE) return LIVE;
    const [reg, gscTxt, probTxt] = await Promise.all([
      fetch(CFG.JOBS_REGISTRY, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).catch(() => null),
      fetch(CFG.GSC_PAGES_CSV, { cache: "no-cache" }).then((r) => (r.ok ? r.text() : "")).catch(() => ""),
      fetch(CFG.GSC_PROBLEMS_CSV, { cache: "no-cache" }).then((r) => (r.ok ? r.text() : "")).catch(() => ""),
    ]);
    const out = { reg, gsc: null, problems: null };
    if (gscTxt) {
      const rows = parseCSV(gscTxt).filter((r) => r.url).map((r) => ({ ...r, clicks: +r.clicks || 0, impressions: +r.impressions || 0, ctr: (+r.ctr || 0) * 100, position: +r.position || 0 }));
      out.gsc = {
        rows,
        clicks: rows.reduce((a, r) => a + r.clicks, 0),
        impressions: rows.reduce((a, r) => a + r.impressions, 0),
        zero: rows.filter((r) => !r.impressions).length,
        p4_10: rows.filter((r) => r.impressions && r.position >= 4 && r.position <= 10.9).sort((a, b) => b.impressions - a.impressions),
        p11_20: rows.filter((r) => r.impressions && r.position >= 11 && r.position <= 20.9).sort((a, b) => b.impressions - a.impressions),
        lowCtr: rows.filter((r) => r.impressions >= 30 && r.ctr < 2).sort((a, b) => b.impressions - a.impressions),
      };
    }
    if (probTxt) {
      const c = {}; parseCSV(probTxt).forEach((r) => (c[r.problem] = (c[r.problem] || 0) + 1));
      out.problems = Object.entries(c).sort((a, b) => b[1] - a[1]);
    }
    return (LIVE = out);
  }

  async function renderLive() {
    view().innerHTML = `<h1>Live site data</h1><p class="muted">Loading…</p>`;
    LIVE = null;
    const L = await loadLive();
    const reg = L.reg || [];
    const open = reg.filter((j) => !j.status);
    const byCat = {}; open.forEach((j) => (byCat[j.category] = (byCat[j.category] || 0) + 1));
    const cats = Object.entries(byCat).sort((a, b) => b[1] - a[1]);
    const newest = [...open].sort((a, b) => (a.date < b.date ? 1 : -1)).slice(0, 10);
    const g = L.gsc;
    const pageTable = (rows, empty) => rows.length ? `<div class="table-wrap"><table><thead><tr><th>Page</th><th>Top queries</th><th class="num">Clicks</th><th class="num">Impr.</th><th class="num">CTR</th><th class="num">Pos.</th><th></th></tr></thead><tbody>
      ${rows.slice(0, 25).map((r) => `<tr><td><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title || r.slug)}</a></td><td><span class="clip muted">${esc(r.queries || r.top_query)}</span></td><td class="num">${r.clicks}</td><td class="num">${r.impressions}</td><td class="num">${r.ctr.toFixed(1)}%</td><td class="num">${r.position.toFixed(1)}</td><td><button class="btn small" data-track="${esc(r.url)}">Track</button></td></tr>`).join("")}
      </tbody></table></div>` : `<p class="muted">${empty}</p>`;

    view().innerHTML = `
      <div class="page-head"><div><h1>Live site data</h1><p class="muted">Read straight from the repo: <code>tools/jobs_registry.json</code> and the job-sync agent's Search Console exports in <code>reports/</code>. Refreshes whenever those files are pushed.</p></div><button class="btn" id="live-refresh">Reload</button></div>
      <div class="grid c4">
        <div class="card tile"><div class="label">Open jobs</div><div class="value">${fmtInt(open.length)}</div><div class="delta muted">${reg.length} in registry</div></div>
        <div class="card tile"><div class="label">Closed / expired</div><div class="value">${fmtInt(reg.filter((j) => j.status).length)}</div><div class="delta muted">${reg.filter((j) => j.status === "closed").length} closed · ${reg.filter((j) => j.status === "expired").length} expired</div></div>
        <div class="card tile"><div class="label">Featured jobs</div><div class="value">${fmtInt(open.filter((j) => j.featured).length)}</div></div>
        ${g ? `<div class="card tile"><div class="label">Job pages in GSC export</div><div class="value">${fmtInt(g.rows.length)}</div><div class="delta muted">${fmtInt(g.clicks)} clicks · ${fmtInt(g.impressions)} impr.</div></div>
        <div class="card tile"><div class="label">Job pages with 0 impressions</div><div class="value">${fmtInt(g.zero)}</div><div class="delta muted">${g.rows.length ? Math.round((g.zero / g.rows.length) * 100) : 0}% of tracked</div></div>` : ""}
      </div>
      ${g ? `
      <div class="card" style="margin-top:16px"><h3>Position 4-10 — protect & strengthen <span class="badge info">${g.p4_10.length}</span></h3>${pageTable(g.p4_10, "None right now.")}</div>
      <div class="card"><h3>Position 11-20 — near Top-10 growth candidates <span class="badge info">${g.p11_20.length}</span></h3>${pageTable(g.p11_20, "None right now.")}</div>
      <div class="card"><h3>High impressions, low CTR (&lt;2%, ≥30 impr.) <span class="badge warn">${g.lowCtr.length}</span></h3>${pageTable(g.lowCtr, "None right now.")}</div>` : `<div class="card"><p class="muted">GSC export not found at ${esc(CFG.GSC_PAGES_CSV)}.</p></div>`}
      <div class="grid c2">
        <div class="card"><h3>Open jobs by category</h3><div class="table-wrap"><table><thead><tr><th>Category</th><th class="num">Open jobs</th><th>Sector page target</th></tr></thead><tbody>
          ${cats.map(([c, n]) => { const s = C.sectors.find((x) => c.toLowerCase().includes(x[0].toLowerCase().split(" ")[0])); return `<tr><td>${esc(c)}</td><td class="num">${n}</td><td class="muted">${s ? esc(s[1]) : ""}</td></tr>`; }).join("")}</tbody></table></div></div>
        <div class="card"><h3>Indexing / visibility problems</h3>${L.problems ? `<table><tbody>${L.problems.map(([p, n]) => `<tr><td>${esc(p)}</td><td class="num">${n}</td></tr>`).join("")}</tbody></table>` : `<p class="muted">No problems file.</p>`}</div>
      </div>
      <div class="card"><h3>Newest open jobs</h3><div class="table-wrap"><table><thead><tr><th>Date</th><th>Job</th><th>Category</th><th>Location</th></tr></thead><tbody>
        ${newest.map((j) => `<tr><td>${esc(j.date)}</td><td><a href="../jobs/${esc(j.slug)}/" target="_blank">${esc(j.title)}</a></td><td>${esc(j.category)}</td><td>${esc(j.location)}</td></tr>`).join("")}</tbody></table></div></div>`;

    $("#live-refresh").onclick = renderLive;
    $$("[data-track]").forEach((b) => (b.onclick = async () => {
      const r = g.rows.find((x) => x.url === b.dataset.track);
      const existing = (await Store.list("seo_pages")).find((p) => p.url === r.url);
      await Store.upsert("seo_pages", { ...(existing ? { id: existing.id } : {}), url: r.url, target_query: r.top_query || r.target_keyword, clicks: r.clicks, impressions: r.impressions, ctr: +r.ctr.toFixed(2), position: r.position });
      b.textContent = "✓ Tracked"; b.disabled = true; toast("Added to Pages tracker");
    }));
  }

  async function renderDataHub() {
    const tables = ["seo_kpi_daily", "seo_keywords", "seo_pages", "seo_technical", "seo_experiments", "seo_sector_opportunities", "seo_alerts", "seo_opportunities", "seo_evidence"];
    const rows = await Promise.all(tables.map((t) => Store.list(t)));
    const counts = Object.fromEntries(tables.map((t, i) => [t, rows[i].length]));
    const kpi = rows[0].slice().sort((a, b) => String(b.date).localeCompare(String(a.date)));
    const latest = kpi[0];
    const openAlerts = rows[6].filter((x) => !x.resolved).length;
    const openTechnical = rows[3].filter((x) => !["fixed", "validated"].includes(x.status)).length;
    const lastDate = latest?.date || today();
    const cur = aggregate(rows[0], addDays(lastDate, -27), lastDate), prev = aggregate(rows[0], addDays(lastDate, -55), addDays(lastDate, -28));
    const explain = [];
    if (cur.clicks != null && prev.clicks != null) explain.push(`Clicks ${delta(cur.clicks, prev.clicks, "sum").txt} versus the previous comparable 28 days.`);
    if (cur.impressions != null && prev.impressions != null) explain.push(`Impressions ${delta(cur.impressions, prev.impressions, "sum").txt}; compare this with clicks to separate visibility from CTR.`);
    if (cur.applications != null && cur.clicks) explain.push(`${fmtInt(cur.applications)} tracked apply clicks from ${fmtInt(cur.clicks)} organic clicks; verify audience fit if clicks rise but applications do not.`);
    if (openAlerts || openTechnical) explain.push(`${openAlerts} unresolved alerts and ${openTechnical} technical findings need prioritisation before starting lower-impact work.`);
    const cards = [
      ["seo_kpi_daily", "Daily KPIs", counts.seo_kpi_daily, "Search Console and GA4 measurements"],
      ["seo_keywords", "Keywords", counts.seo_keywords, "Queries, intent and ranking movement"],
      ["seo_pages", "Pages", counts.seo_pages, "Landing-page visibility and decisions"],
      ["seo_technical", "Technical", openTechnical, "Open audit findings requiring action"],
      ["seo_experiments", "Experiments", counts.seo_experiments, "Measured page changes and reviews"],
      ["seo_sector_opportunities", "Sector opportunities", counts.seo_sector_opportunities, "Jobs combined with search demand"],
      ["seo_alerts", "Open alerts", openAlerts, "Drops, visibility losses and indexing delays"],
      ["seo_opportunities", "Opportunity inbox", counts.seo_opportunities, "Prioritised real-data practice ideas"],
      ["seo_evidence", "Evidence locker", counts.seo_evidence, "Proof saved from practical work"],
    ];
    view().innerHTML = `<div class="page-head"><div><span class="badge info">Analytics</span><h1>Analytics overview</h1><p class="muted">Automated measurements from Search Console, GA4, site audits and the jobs registry.</p></div><a class="btn" href="#/sync">Check integrations</a></div>
      <div class="stats-grid">
        <div class="stat-card"><span>Storage</span><strong>${Store.mode === "supabase" ? "Supabase" : "Local"}</strong><small>${Store.mode === "supabase" ? "Shared and protected by RLS" : "Only in this browser"}</small></div>
        <div class="stat-card"><span>Latest data date</span><strong>${esc(latest?.date || "No data")}</strong><small>${latest ? `${fmtInt(latest.clicks)} clicks · ${fmtInt(latest.impressions)} impressions` : "Run the automation or import a CSV"}</small></div>
        <div class="stat-card"><span>Action needed</span><strong>${openAlerts + openTechnical}</strong><small>${openAlerts} alerts · ${openTechnical} technical issues</small></div>
      </div>
      <div class="card"><h3>Data workflow</h3><ol><li><b>Collect:</b> Search Console, GA4, the jobs registry, git history and site audits feed the trackers.</li><li><b>Interpret:</b> Use complete, comparable date ranges and connect visibility to applications and employer leads.</li><li><b>Act:</b> Turn one evidence-backed finding into a focused change.</li><li><b>Review:</b> Use Experiments at 7, 30, 60 and 90 days before deciding what worked.</li></ol></div>
      <div class="card"><div class="row spread"><h3>Explain this data</h3><span class="badge info">Evidence-based summary</span></div>${explain.length ? `<ul>${explain.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : `<p class="muted">Not enough comparable KPI data yet. Run the automation until both 28-day periods are complete.</p>`}<p class="small muted">This describes associations, not guaranteed causes. Use a focused experiment before attributing a change to SEO work.</p></div>
      <div class="course-grid">${cards.map(([t, title, count, desc]) => `<a class="week-card" href="#/t/${t}"><div class="row spread"><span class="badge">${fmtInt(count)}</span><span>Open →</span></div><h3>${esc(title)}</h3><p class="muted small">${esc(desc)}</p></a>`).join("")}</div>
      <div class="card"><h3>Other data sources</h3><div class="row"><a class="btn" href="#/live">Live site data</a><a class="btn" href="#/t/seo_content">Content</a><a class="btn" href="#/t/seo_backlinks">Backlinks</a><a class="btn" href="#/t/seo_local">Local</a><a class="btn" href="#/t/seo_ai_visibility">AI visibility</a></div></div>`;
  }

  // ── Organised Learn / Analytics / Workspace views ──
  let AUTOMATION_REPORT = null;
  async function loadAutomationReport(force = false) {
    if (AUTOMATION_REPORT && !force) return AUTOMATION_REPORT;
    const url = CFG.AUTOMATION_REPORT || "../reports/seo-automation-latest.json";
    AUTOMATION_REPORT = await fetch(url + (url.includes("?") ? "&" : "?") + "v=" + Date.now(), { cache: "no-store" })
      .then((r) => r.ok ? r.json() : null).catch(() => null);
    return AUTOMATION_REPORT;
  }

  function freshness(dateValue, expectedDelay = 2) {
    if (!dateValue) return { label: "Insufficient data", cls: "warn", note: "No dated record is available" };
    const age = Math.max(0, Math.floor((parseDate(today()) - parseDate(String(dateValue).slice(0, 10))) / DAY));
    if (age <= expectedDelay + 1) return { label: "Live", cls: "good", note: `${age} day${age === 1 ? "" : "s"} old` };
    if (age <= expectedDelay + 4) return { label: "Delayed", cls: "warn", note: `${age} days old` };
    return { label: "Tracking issue", cls: "bad", note: `${age} days old` };
  }
  const confidenceBadge = (x) => `<span class="badge ${x.cls}" title="${esc(x.note)}">${esc(x.label)}</span>`;
  const opportunityScore = (x) => Math.round(((+x.impact || 1) * 20) / Math.max(1, +x.effort || 1));

  async function renderToday() {
    const ctx = await courseCtx();
    const [kpi, weekData] = await Promise.all([Store.list("seo_kpi_daily"), Store.getWeek(ctx.week)]);
    const week = C.weeks[ctx.week - 1], how = H[ctx.week] || {};
    const latest = [...kpi].sort((a, b) => String(b.date).localeCompare(String(a.date)))[0];
    const next = week.tasks.findIndex((_, i) => !weekData.tasks?.[i]?.done);
    const taskIndex = next < 0 ? week.tasks.length - 1 : next;
    view().innerHTML = `<div class="simple-home">
      <div class="page-head"><div><span class="badge info">Week ${ctx.week}</span><h1>Today</h1><p class="muted">Only one idea and one practical task.</p></div></div>
      <div class="card simple-idea"><span class="eyebrow">The idea</span><h2>${esc(week.title)}</h2><p>${esc(how.plain || week.objective)}</p></div>
      <div class="card simple-action"><span class="eyebrow">Do this now</span><h2>${next < 0 ? "Weekly tasks complete" : `Task ${taskIndex + 1}`}</h2><p>${esc(next < 0 ? "Open the week and write one short result note." : week.tasks[taskIndex])}</p><a class="btn primary" href="#/course/${ctx.week}">${next < 0 ? "Review this week" : "Start this task"} →</a></div>
      <div class="card simple-optional"><b>Optional today:</b> ${latest?.date === today() ? "Results already recorded ✓" : `<a href="#/t/seo_kpi_daily?add=1">Record today’s clicks and applications</a>`}</div>
      <p class="simple-stop">That is enough for today. Do not open the advanced tools unless you need them.</p>
    </div>`;
  }

  async function renderSearchConsole() {
    const [kpi, keywords, pages] = await Promise.all([Store.list("seo_kpi_daily"), Store.list("seo_keywords"), Store.list("seo_pages")]);
    const sorted = [...kpi].filter((x) => x.clicks != null).sort((a, b) => String(a.date).localeCompare(String(b.date)));
    const latest = sorted.at(-1), status = freshness(latest?.date, 2);
    const top10 = keywords.filter((x) => +x.current_position > 0 && +x.current_position <= 10).length;
    const falling = keywords.filter((x) => x.previous_position != null && +x.current_position - +x.previous_position > 3).length;
    view().innerHTML = `<div class="page-head"><div><span class="badge info">Analytics</span><h1>Google Search Console</h1><p class="muted">Search visibility, queries and landing-page performance.</p></div><div>${confidenceBadge(status)} <span class="small muted">${esc(status.note)}</span></div></div>
      <div class="grid c4">${[["Clicks", latest?.clicks], ["Impressions", latest?.impressions], ["CTR", fmtPct(latest?.ctr)], ["Average position", fmt1(latest?.avg_position)]].map(([l, v]) => `<div class="card tile"><div class="label">${l}</div><div class="value">${typeof v === "number" ? fmtInt(v) : v}</div><div class="delta muted">${esc(latest?.date || "No data")}</div></div>`).join("")}</div>
      <div class="grid c2" style="margin-top:16px"><div class="card"><h3>Clicks trend</h3>${lineChart(sorted.slice(-90).map((r) => ({ x: r.date, y: +r.clicks })))}</div><div class="card"><h3>Impressions trend</h3>${lineChart(sorted.slice(-90).map((r) => ({ x: r.date, y: +r.impressions })))}</div></div>
      <div class="grid c3"><a class="week-card" href="#/t/seo_keywords"><span class="badge good">${top10}</span><h3>Top-10 keywords</h3><p class="muted small">${falling} keywords dropped by more than three positions.</p></a><a class="week-card" href="#/t/seo_pages"><span class="badge">${pages.length}</span><h3>Landing pages</h3><p class="muted small">Compare impressions, clicks, CTR and position.</p></a><a class="week-card" href="#/t/seo_sector_opportunities"><span class="badge info">Opportunity</span><h3>Sectors &amp; locations</h3><p class="muted small">Connect search demand to current job supply.</p></a></div>`;
  }

  async function renderGA4() {
    const kpi = [...await Store.list("seo_kpi_daily")].filter((x) => x.organic_users != null).sort((a, b) => String(a.date).localeCompare(String(b.date)));
    const latest = kpi.at(-1), status = freshness(latest?.date, 1);
    const end = latest?.date || today(), total = aggregate(kpi, addDays(end, -27), end);
    const conversion = total.organic_users ? ((total.applications || 0) / total.organic_users) * 100 : null;
    view().innerHTML = `<div class="page-head"><div><span class="badge info">Analytics</span><h1>Google Analytics</h1><p class="muted">Organic audiences and the business actions generated on the website.</p></div><div>${confidenceBadge(status)} <span class="small muted">${esc(status.note)}</span></div></div>
      <div class="grid c4"><div class="card tile"><div class="label">Organic users · 28d</div><div class="value">${fmtInt(total.organic_users)}</div></div><div class="card tile"><div class="label">Apply clicks · 28d</div><div class="value">${fmtInt(total.applications)}</div><div class="delta muted">GA4 event: apply_click</div></div><div class="card tile"><div class="label">Employer leads · 28d</div><div class="value">${fmtInt(total.employer_leads)}</div><div class="delta muted">GA4 event: employer_lead_submit</div></div><div class="card tile"><div class="label">Apply rate</div><div class="value">${conversion == null ? "–" : conversion.toFixed(1) + "%"}</div><div class="delta muted">Apply clicks / organic users</div></div></div>
      <div class="grid c2" style="margin-top:16px"><div class="card"><h3>Organic users</h3>${lineChart(kpi.slice(-90).map((r) => ({ x: r.date, y: +r.organic_users })))}</div><div class="card"><h3>Apply clicks</h3>${lineChart(kpi.slice(-90).filter((r) => r.applications != null).map((r) => ({ x: r.date, y: +r.applications })))}</div></div>
      <div class="card"><h3>How to read this</h3><p>If organic users rise but apply clicks remain flat, check search intent, vacancy relevance and the Apply journey. If applications rise with stable traffic, inspect the pages and calls to action responsible, then test the pattern elsewhere.</p><p class="small muted">Apply clicks measure outbound intent; the external careers platform must provide completed-application data if you need confirmed applications.</p></div>`;
  }

  async function renderWorkspace() {
    const [opportunities, alerts, technical, experiments] = await Promise.all([Store.list("seo_opportunities"), Store.list("seo_alerts"), Store.list("seo_technical"), Store.list("seo_experiments")]);
    const queue = opportunities.filter((x) => !["complete", "dismissed"].includes(x.status)).sort((a, b) => opportunityScore(b) - opportunityScore(a));
    const openAlerts = alerts.filter((x) => !x.resolved), openTech = technical.filter((x) => !["fixed", "validated"].includes(x.status));
    const due = experiments.filter((x) => x.review_date && x.review_date <= today() && !x.conclusion);
    const buckets = [
      ["Immediate", queue.filter((x) => opportunityScore(x) >= 40), "good"],
      ["Plan next", queue.filter((x) => opportunityScore(x) >= 20 && opportunityScore(x) < 40), "info"],
      ["Backlog", queue.filter((x) => opportunityScore(x) < 20), ""],
    ];
    view().innerHTML = `<div class="page-head"><div><span class="badge info">SEO Workspace</span><h1>Priorities</h1><p class="muted">Move from evidence to one focused change, then measure the result.</p></div><a class="btn primary" href="#/practice">Start Practice Mode</a></div>
      <div class="grid c3"><a class="stat-card" href="#/t/seo_alerts"><span>Unresolved alerts</span><strong>${openAlerts.length}</strong><small>Investigate measurement and visibility changes</small></a><a class="stat-card" href="#/t/seo_technical"><span>Open audit findings</span><strong>${openTech.length}</strong><small>Fix Critical and High issues first</small></a><a class="stat-card" href="#/t/seo_experiments"><span>Reviews due</span><strong>${due.length}</strong><small>Complete before drawing conclusions</small></a></div>
      <div class="priority-board">${buckets.map(([label, rows, cls]) => `<section class="priority-column"><div class="row spread"><h3>${label}</h3><span class="badge ${cls}">${rows.length}</span></div>${rows.slice(0, 12).map((x) => `<article class="priority-item"><div class="row spread"><span class="badge ${x.priority === "Critical" ? "bad" : x.priority === "High" ? "warn" : ""}">${esc(x.priority || "New")}</span><span class="priority-score">${opportunityScore(x)}</span></div><b>${esc(x.title)}</b><p class="small muted">${esc(x.recommended_action || x.explanation)}</p><div class="row spread"><span class="small">Impact ${x.impact || "–"} · Effort ${x.effort || "–"}</span><a href="#/practice">Practice →</a></div></article>`).join("") || `<p class="muted small">Nothing here.</p>`}</section>`).join("")}</div>
      <div class="card"><h3>Workspace flow</h3><div class="workflow"><span>Alert or opportunity</span><b>→</b><span>Recommended action</span><b>→</b><span>Practice or experiment</span><b>→</b><span>7/30/60/90-day review</span><b>→</b><span>Lesson learned</span></div></div>`;
  }

  async function renderWeeklyReview() {
    const ctx = await courseCtx(), data = await Store.getWeek(ctx.week);
    data.resume = data.resume || { learned: [], issues: [], next: "" };
    const [from, to] = weekRange(ctx.start, ctx.week), kpi = await Store.list("seo_kpi_daily");
    const cur = aggregate(kpi, from, to), prev = aggregate(kpi, addDays(from, -7), addDays(from, -1));
    view().innerHTML = `<div class="page-head"><div><span class="badge info">Week ${ctx.week}</span><h1>Weekly review</h1><p class="muted">Edit the automatic draft, record what the evidence means, and choose one next priority.</p></div><a class="btn" href="#/course/${ctx.week}">Open full week</a></div>
      <div class="card"><h3>KPI movement</h3><div class="table-wrap"><table><thead><tr><th>KPI</th><th class="num">Previous</th><th class="num">Current</th><th class="num">Change</th></tr></thead><tbody>${KPI_KEYS.map(([k, l, kind]) => { const d = delta(cur[k], prev[k], kind); return `<tr><td>${l}</td><td class="num">${fmtKpi(prev[k], kind)}</td><td class="num">${fmtKpi(cur[k], kind)}</td><td class="num ${d.cls}">${d.txt}</td></tr>`; }).join("")}</tbody></table></div></div>
      <div class="card"><h3>Editable weekly summary</h3><div class="form-grid">${[0, 1, 2].map((i) => `<label>Thing learned ${i + 1}<input data-review-learned="${i}" value="${esc(data.resume.learned?.[i])}"></label>`).join("")}${[0, 1, 2].map((i) => `<label>Issue or opportunity ${i + 1}<input data-review-issue="${i}" value="${esc(data.resume.issues?.[i])}"></label>`).join("")}<label class="wide">One measurable next priority<input id="review-next" value="${esc(data.resume.next)}"></label></div><div class="row spread"><span id="review-state" class="save-state"></span><button id="review-save" class="btn primary">Save weekly review</button></div></div>`;
    $("#review-save").onclick = async () => {
      data.resume.learned = $$('[data-review-learned]').map((x) => x.value); data.resume.issues = $$('[data-review-issue]').map((x) => x.value); data.resume.next = $("#review-next").value;
      await Store.setWeek(ctx.week, data); $("#review-state").textContent = "Saved ✓"; toast("Weekly review saved");
    };
  }

  async function renderSyncCentre() {
    const report = await loadAutomationReport(true), checks = report?.checks || {};
    const items = [
      ["Google Search Console", checks.gsc, checks.gsc?.through ? `Final data through ${checks.gsc.through}` : "Clicks, impressions, queries and pages"],
      ["Google Analytics", checks.ga4, checks.ga4?.property_id ? `Property ${checks.ga4.property_id}` : "Organic users and conversion events"],
      ["Supabase", checks.supabase, Store.mode === "supabase" ? "Admin storage connected" : "Admin is using local browser storage"],
      ["Site audit", checks.audit, checks.audit?.issues != null ? `${fmtInt(checks.audit.issues)} findings checked` : "Technical and on-page scan"],
    ];
    view().innerHTML = `<div class="page-head"><div><span class="badge info">Settings</span><h1>Integrations &amp; sync</h1><p class="muted">Connection health, data freshness and the last automation result.</p></div><button class="btn" id="sync-refresh">Refresh status</button></div>
      <div class="sync-grid">${items.map(([name, check, note]) => `<div class="card sync-card"><span class="status-dot ${check?.ok ? "ok" : "error"}"></span><div><h3>${esc(name)}</h3><p>${check?.ok ? '<span class="badge good">Connected</span>' : '<span class="badge bad">Needs attention</span>'}</p><p class="small muted">${esc(note)}</p></div></div>`).join("")}</div>
      <div class="card"><h3>Last automation run</h3><p><b>${esc(report?.generated_at ? new Date(report.generated_at).toLocaleString() : "No report available")}</b></p>${report?.warnings?.length ? `<ul>${report.warnings.map((x) => `<li class="error">${esc(x)}</li>`).join("")}</ul>` : `<p><span class="badge good">No warnings</span></p>`}<p class="small muted">Search Console final data is normally delayed by about two days. “Connected” means the latest automation call succeeded; it does not mean Google reports are real-time.</p></div>
      <div class="card"><h3>Data confidence labels</h3><div class="row"><span class="badge good">Live</span><span>Expected fresh data is present.</span><span class="badge warn">Delayed</span><span>Data is older than expected.</span><span class="badge bad">Tracking issue</span><span>Investigate the connection or scheduled job.</span></div></div>`;
    $("#sync-refresh").onclick = renderSyncCentre;
  }

  async function renderPractice() {
    const ctx = await courseCtx(), week = C.weeks[ctx.week - 1], guide = G[ctx.week] || {};
    const [data, opportunities, evidence] = await Promise.all([Store.getWeek(ctx.week), Store.list("seo_opportunities"), Store.list("seo_evidence")]);
    const queue = opportunities.filter((x) => +x.course_week === ctx.week && !["complete", "dismissed"].includes(x.status));
    const practice = data.practice || {};
    const selected = queue.find((x) => x.id === practice.opportunity_id) || queue[0];
    const stage = [practice.observation, practice.hypothesis, practice.decision, practice.implementation, practice.review].filter(Boolean).length;
    view().innerHTML = `<div class="page-head"><div><span class="badge info">Week ${ctx.week} laboratory</span><h1>Guided practice</h1><p class="muted">Learn → observe real data → decide → implement → review.</p></div><a class="btn" href="#/course/${ctx.week}">Open lesson</a></div>
      <div class="practice-stage"><span class="${stage >= 1 ? "done" : ""}">1 Observe</span><span class="${stage >= 2 ? "done" : ""}">2 Hypothesise</span><span class="${stage >= 3 ? "done" : ""}">3 Decide</span><span class="${stage >= 4 ? "done" : ""}">4 Implement</span><span class="${stage >= 5 ? "done" : ""}">5 Review</span></div>
      <div class="card"><h3>${esc(week.title)}</h3><p>${esc(guide.why || week.objective)}</p></div>
      <div class="card"><div class="row spread"><h3>Choose a real opportunity</h3><a href="#/t/seo_opportunities">Open full inbox</a></div>
        ${queue.length ? `<select id="practice-opportunity">${queue.map((x) => `<option value="${esc(x.id)}" ${x.id === selected?.id ? "selected" : ""}>${esc(x.priority)} · ${esc(x.title)}</option>`).join("")}</select>
          <div class="callout" style="margin-top:10px"><b>${esc(selected?.title)}</b><br>${esc(selected?.explanation)}<br><span class="small"><b>Recommended:</b> ${esc(selected?.recommended_action)}</span></div>` : `<p class="muted">No automatic Week ${ctx.week} opportunity yet. Use the lesson task or add one in the Opportunity inbox.</p>`}
      </div>
      <div class="card"><h3>Practice record</h3><div class="form-grid">
        <label class="wide">1. What do you observe in the data?<textarea id="p-observation">${esc(practice.observation)}</textarea></label>
        <label class="wide">2. Hypothesis — what do you expect and why?<textarea id="p-hypothesis">${esc(practice.hypothesis)}</textarea></label>
        <label class="wide">3. Decision — what one focused action will you take?<textarea id="p-decision">${esc(practice.decision)}</textarea></label>
        <label class="wide">4. Implementation notes / commit / changed URL<textarea id="p-implementation">${esc(practice.implementation)}</textarea></label>
        <label>Review date<input type="date" id="p-review-date" value="${esc(practice.review_date || addDays(today(), 7))}"></label>
        <label class="wide">5. Review — what happened and what did you learn?<textarea id="p-review">${esc(practice.review)}</textarea></label>
      </div><div class="row spread"><span id="practice-save" class="save-state"></span><button class="btn primary" id="practice-save-btn">Save practice</button></div></div>
      <div class="grid c2"><div class="card"><h3>Implementation checklist</h3><ol>${(guide.steps || week.tasks).map((x) => `<li>${esc(x)}</li>`).join("")}</ol></div>
      <div class="card"><h3>Evidence</h3><p>${evidence.filter((x) => +x.week === ctx.week).length} item(s) saved for Week ${ctx.week}.</p><a class="btn" href="#/t/seo_evidence?add=1">Add evidence</a> <a class="btn" href="#/t/seo_evidence">Open locker</a></div></div>`;
    $("#practice-opportunity")?.addEventListener("change", async (e) => { practice.opportunity_id = e.target.value; data.practice = practice; await Store.setWeek(ctx.week, data); renderPractice(); });
    $("#practice-save-btn").onclick = async () => {
      for (const k of ["observation", "hypothesis", "decision", "implementation", "review"]) practice[k] = $("#p-" + k).value;
      practice.review_date = $("#p-review-date").value; practice.opportunity_id = $("#practice-opportunity")?.value || practice.opportunity_id;
      data.practice = practice; await Store.setWeek(ctx.week, data);
      if (selected) { selected.status = practice.implementation ? "in progress" : "selected"; await Store.upsert("seo_opportunities", selected, "source_key"); }
      $("#practice-save").textContent = "Saved ✓"; toast("Practice saved");
    };
  }

  async function renderDecisions() {
    const ctx = await courseCtx(), item = D[ctx.week];
    if (!item) return (view().innerHTML = `<p>No decision exercise for this week.</p>`);
    const previous = (await Store.list("seo_decisions")).filter((x) => +x.week === ctx.week).sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)))[0];
    view().innerHTML = `<div class="page-head"><div><span class="badge info">Week ${ctx.week}</span><h1>Decision simulator</h1><p class="muted">Use evidence and course principles before seeing the answer.</p></div><a class="btn" href="#/course/${ctx.week}">Review lesson</a></div>
      <div class="card"><h2>${esc(item.scenario)}</h2><div class="decision-options">${item.answers.map((a, i) => `<button class="btn decision-option" data-answer="${i}">${String.fromCharCode(65 + i)}. ${esc(a)}</button>`).join("")}</div><div id="decision-result" style="margin-top:14px">${previous ? `<div class="callout"><b>Previous answer:</b> ${esc(previous.selected_answer)}<br>${esc(previous.reasoning)}</div>` : ""}</div></div>
      <div class="card"><h3>Apply the reasoning</h3><p>After answering, open <a href="#/practice">Guided practice</a> and use the same decision process on a real Outreach Recruitment opportunity.</p></div>`;
    $$("[data-answer]").forEach((button) => button.onclick = async () => {
      const i = +button.dataset.answer, correct = i === item.correct;
      $("#decision-result").innerHTML = `<div class="callout"><b>${correct ? "Correct ✓" : "Not quite"}</b><br>${esc(item.reasoning)}</div>`;
      await Store.upsert("seo_decisions", { week: ctx.week, scenario: item.scenario, selected_answer: item.answers[i], correct_answer: item.answers[item.correct], is_correct: correct, reasoning: item.reasoning });
      toast("Decision saved");
    });
  }

  // ── Generic tracker ──
  async function renderTracker(table, params = new URLSearchParams()) {
    const def = TRACKERS[table];
    let rows = await Store.list(table, { force: true });
    const [sk, dir] = def.sort || ["created_at", -1];
    const rank = def.sortRank?.[sk];
    rows = [...rows].sort((a, b) => {
      let x = a[sk], y = b[sk];
      if (rank) { x = rank[x] ?? 99; y = rank[y] ?? 99; }
      if (x == null) return 1; if (y == null) return -1;
      return (x < y ? -1 : x > y ? 1 : 0) * dir;
    });
    const cols = def.cols.filter((c) => !c.hide);
    const newRowDefaults = () => table === "seo_kpi_daily" ? { date: today() }
      : table === "seo_ai_visibility" ? { date: today() }
      : table === "seo_evidence" ? { captured_at: today(), week: num(params.get("week")) }
      : {};
    const weekLinks = (def.weeks || []).map((n) => `<a href="#/course/${n}">Week ${n}</a>`).join(", ");
    view().innerHTML = `
      <div class="page-head"><div><h1>${esc(def.title)} <span class="badge">${rows.length}</span></h1>
        <p class="muted">${esc(def.intro)}<br><span class="small">Dashboard tab: ${esc(def.tab)} · used in ${weekLinks}</span></p></div>
        <div class="row"><button class="btn primary" id="t-add">Add</button><button class="btn" id="t-imp">Import CSV</button><button class="btn" id="t-exp">Export CSV</button></div></div>
      <div class="card"><input id="t-q" placeholder="Filter…" style="max-width:320px;margin-bottom:10px">
      ${rows.length ? `<div class="table-wrap"><table><thead><tr>${cols.map((c) => `<th class="${["int", "num"].includes(c.t) ? "num" : ""}">${esc(c.l)}</th>`).join("")}${(def.computed || []).map((c) => `<th class="num">${esc(c.l)}</th>`).join("")}</tr></thead>
      <tbody id="t-body">${rows.map((r) => `<tr data-id="${esc(r.id)}" style="cursor:pointer">${cols.map((c) => cell(c, r[c.k])).join("")}${(def.computed || []).map((c) => { const v = c.f(r); return `<td class="num ${c.cls ? c.cls(v) : ""}">${v == null ? "–" : v}</td>`; }).join("")}</tr>`).join("")}</tbody></table></div>`
        : `<div class="empty">No rows yet. Click <b>Add</b> or <b>Import CSV</b>.</div>`}</div>`;
    const reload = () => renderTracker(table);
    $("#t-add").onclick = () => editRow(table, newRowDefaults(), reload);
    $("#t-imp").onclick = () => importDialog(table, reload);
    $("#t-exp").onclick = () => download(table + "-" + today() + ".csv", toCSV(def.cols, rows));
    $$("#t-body tr").forEach((tr) => (tr.onclick = () => editRow(table, rows.find((r) => r.id === tr.dataset.id), reload)));
    $("#t-q").oninput = (e) => { const q = e.target.value.toLowerCase(); $$("#t-body tr").forEach((tr) => (tr.hidden = !tr.textContent.toLowerCase().includes(q))); };
    if (params.get("add")) {
      const existing = table === "seo_kpi_daily" ? rows.find((r) => r.date === today()) : null;
      editRow(table, existing || newRowDefaults(), reload);
    }
  }
  function cell(c, v) {
    if (v == null || v === "") return `<td class="${["int", "num"].includes(c.t) ? "num" : ""} muted">–</td>`;
    if (c.t === "bool") return `<td>${v ? "✅" : "—"}</td>`;
    if (c.t === "int") return `<td class="num">${fmtInt(v)}</td>`;
    if (c.t === "num") return `<td class="num">${(+v).toFixed(c.k === "ctr" ? 2 : 1)}</td>`;
    if (c.k === "severity") return `<td><span class="badge ${v === "Critical" ? "bad" : v === "High" ? "warn" : ""}">${esc(v)}</span></td>`;
    if (c.k === "status") return `<td><span class="badge ${/fixed|validated|done|acquired|published/.test(v) ? "good" : /progress|contacted|replied|writing|brief/.test(v) ? "info" : ""}">${esc(v)}</span></td>`;
    if (/url|link/.test(c.k) && /^https?:/.test(v)) return `<td><a class="clip" href="${esc(v)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${esc(v.replace(/^https?:\/\/(www\.)?/, ""))}</a></td>`;
    return `<td><span class="clip">${esc(v)}</span></td>`;
  }

  // ── Course map ──
  async function renderCourseMap() {
    const [ctx, score, evidence, experiments] = await Promise.all([courseCtx(), courseScore(), Store.list("seo_evidence"), Store.list("seo_experiments")]);
    const w0 = score.byW[0] || {};
    view().innerHTML = `
      <div class="page-head"><div><h1>Course map</h1><p class="muted">${esc(C.title)}</p></div>
        <label style="max-width:220px">Course start date<input type="date" id="c-start" value="${esc(ctx.start)}"></label></div>
      <div class="callout"><b>Main objective:</b> ${esc(C.objective)}<br><span class="small">Every module has five outputs: understanding, a real website task, a measurable KPI, a QCM, and a saved deliverable. A module is not complete until the real task is implemented and recorded.</span></div>
      ${C.months.map((m) => `
        <div class="row spread" style="margin-top:18px"><h2>Month ${m.n}</h2>
          <label class="row" style="margin:0"><input type="checkbox" data-month="${m.n}" ${w0.months?.[m.n]?.done ? "checked" : ""}> Monthly project done</label></div>
        <p class="muted">${esc(m.goal)}</p>
        <div class="grid c4">${m.weeks.map((n) => {
          const w = C.weeks[n - 1], d = score.byW[n] || {};
          const done = w.tasks.filter((_, i) => d.tasks?.[i]?.done).length;
          const hasAction = !!(d.actionPlan?.action || Object.values(d.kpiActions || {}).some(Boolean));
          const hasEvidence = !!(d.deliverable?.link || evidence.some((x) => +x.week === n));
          const hasReview = !!(d.finalDecision?.choice && d.finalDecision?.reason);
          const hasExperiment = experiments.some((x) => String(x.source_key || "").startsWith(`course-week-${n}-`)) || !!d.actionPlan?.experimentId;
          const gates = [done === w.tasks.length, hasAction, hasEvidence, hasReview];
          const [from, to] = weekRange(ctx.start, n);
          return `<a class="card week-card ${n === ctx.week ? "current" : ""}" href="#/course/${n}">
            <div class="row spread"><span class="badge ${d.deliverable?.done ? "good" : n === ctx.week ? "info" : ""}">Week ${n}</span>${n === ctx.week ? '<span class="small up">Do this week</span>' : ""}</div>
            <h3 style="margin-top:8px">${esc(w.title)}</h3>
            <p class="small muted">${esc(w.objective)}</p>
            <div class="progress"><span style="width:${(gates.filter(Boolean).length / gates.length) * 100}%"></span></div>
            <p class="small muted" style="margin:6px 0 0">${done}/${w.tasks.length} simple tasks complete</p></a>`;
        }).join("")}</div>`).join("")}
      <div class="card" style="margin-top:20px"><h3>Final competency checklist</h3><ul class="checklist">
        ${C.competencies.map((c, i) => `<li class="${w0.competencies?.[i] ? "done" : ""}"><input type="checkbox" data-comp="${i}" ${w0.competencies?.[i] ? "checked" : ""}><span class="txt grow">${esc(c)}</span></li>`).join("")}</ul></div>`;

    $("#c-start").onchange = async (e) => { await Store.setSetting("course_start", e.target.value); toast("Start date saved"); renderCourseMap(); };
    const saveW0 = async (fn) => { const d = await Store.getWeek(0); fn(d); await Store.setWeek(0, d); toast("Saved"); };
    $$("[data-month]").forEach((c) => (c.onchange = () => saveW0((d) => { d.months = d.months || {}; d.months[c.dataset.month] = { ...(d.months[c.dataset.month] || {}), done: c.checked }; })));
    $$("[data-comp]").forEach((c) => (c.onchange = () => { c.closest("li").classList.toggle("done", c.checked); saveW0((d) => { d.competencies = d.competencies || {}; d.competencies[c.dataset.comp] = c.checked; }); }));
  }

  // ── Course week ──
  async function renderWeek(n) {
    const ctx = await courseCtx();
    if (n === "today") n = ctx.week;
    n = +n;
    const w = C.weeks[n - 1];
    if (!w) return (view().innerHTML = `<p>Unknown week.</p>`);
    const d = await Store.getWeek(n);
    const guide = G[n] || {};
    const revisionWeek = n > 2 ? C.weeks[n - 3] : null;
    const revisionData = revisionWeek ? await Store.getWeek(n - 2) : {};
    const revisions = revisionWeek ? revisionWeek.qcm.map((q, i) => ({ q, mark: revisionData.qcm?.[i]?.mark }))
      .filter((x) => x.mark === "wrong" || x.mark === "partial") : [];
    const kpi = await Store.list("seo_kpi_daily");
    const [from, to] = weekRange(ctx.start, n);
    const cur = aggregate(kpi, from, to), prev = aggregate(kpi, addDays(from, -7), addDays(from, -1));
    const trKey = { technical_issues: "seo_technical", content_items: "seo_content", local_actions: "seo_local" }[w.tracker] || (TRACKERS[w.tracker] ? w.tracker : "seo_" + w.tracker);
    const tr = TRACKERS[trKey];
    const how = H[n] || {};
    const metricPlan = M[n] || { kpis: KPI_KEYS.map(([k]) => k), question: "What does the data say, and what one action should follow?", source: "Daily KPI tracking", action: "Choose one evidence-based action and set a review date." };
    const focusedKpis = metricPlan.kpis.map((key) => kpiDef(key));
    const confidence = dataConfidence(cur, prev, metricPlan.kpis);
    const reviewDays = REVIEW_DAYS[n - 1] || 30;
    const trackerLink = tr ? `<a class="btn" href="#/t/${trKey}">Open ${esc(tr.title)} tracker →</a>` : w.tracker === "live" ? `<a class="btn" href="#/live">Open Live site data →</a>` : w.tracker === "final" ? `<a class="btn" href="#/final">Open Final case study →</a>` : "";
    const isCurrent = n === ctx.week;
    d.days = d.days || []; d.tasks = d.tasks || {}; d.worksheet = d.worksheet || []; d.qcm = d.qcm || {};
    d.kpiActions = d.kpiActions || {}; d.deliverable = d.deliverable || {}; d.resume = d.resume || { learned: [], issues: [] };
    d.actionPlan = d.actionPlan || { observation: "", segment: "", audience: "", hypothesis: "", action: "", owner: "", reviewDate: addDays(today(), reviewDays), target: "", confidence: "", page: "", query: "" };
    d.finalDecision = d.finalDecision || { choice: "", reason: "" };
    const nextTaskIndex = w.tasks.findIndex((_, i) => !d.tasks[i]?.done);
    const simpleTaskIndex = nextTaskIndex < 0 ? w.tasks.length - 1 : nextTaskIndex;
    const completedTasks = w.tasks.filter((_, i) => d.tasks[i]?.done).length;

    view().innerHTML = `
      <div class="page-head"><div>
        <div class="row"><span class="badge info">Week ${n} of 16</span><span class="badge">${esc(w.track)}</span>${isCurrent ? '<span class="badge good">Current week</span>' : ""}<span class="small muted">${from} → ${to}</span></div>
        <h1 style="margin-top:8px">${esc(w.title)}</h1></div>
        <div class="row">${n > 1 ? `<a class="btn" href="#/course/${n - 1}">← Week ${n - 1}</a>` : ""}${n < 16 ? `<a class="btn" href="#/course/${n + 1}">Week ${n + 1} →</a>` : ""}<span class="save-state" id="save-state"></span></div></div>

      <section id="simple-course" class="simple-course">
        <div class="simple-progress"><span style="width:${(completedTasks / w.tasks.length) * 100}%"></span></div>
        <div class="row spread"><p class="muted">${completedTasks} of ${w.tasks.length} practical tasks complete</p><button class="btn small" type="button" id="show-full-course">Show full course details</button></div>
        <div class="card simple-start"><span class="eyebrow">Start here — one step at a time</span><h2>${nextTaskIndex < 0 ? "You completed the practical tasks" : `Your next task: ${simpleTaskIndex + 1}`}</h2>
          <div class="simple-steps">
            <div><span>1</span><section><b>Learn this</b><p>${esc(how.plain || w.understand)}</p></section></div>
            <div><span>2</span><section><b>Do this now</b><p>${esc(nextTaskIndex < 0 ? "Review your result and add the final evidence for this week." : w.tasks[simpleTaskIndex])}</p>${how.tasks?.[simpleTaskIndex] ? `<details class="howto"><summary>Show exactly how</summary><p>${esc(how.tasks[simpleTaskIndex])}</p></details>` : ""}${trackerLink}</section></div>
            <div><span>3</span><section><b>Write one short note</b><p class="small muted">What did you do? Paste a page, screenshot, document or result link if you have one.</p><textarea id="simple-task-note" placeholder="Example: Updated the hospitality page title. Screenshot: …">${esc(d.tasks[simpleTaskIndex]?.note)}</textarea></section></div>
            <div><span>4</span><section><b>Finish this step</b><p class="small muted">You do not need to study every KPI now. The course will ask you to review ${focusedKpis.map(([, label]) => label).join(", ")} after ${reviewDays} days.</p><button class="btn primary" type="button" id="complete-simple-task">${d.tasks[simpleTaskIndex]?.done ? "Completed ✓" : "Mark task complete"}</button></section></div>
          </div>
        </div>
        <div class="card simple-rule"><b>Your simple rule:</b> learn one idea → do one real task → write one note → stop for today. Return tomorrow for the next task.</div>
      </section>

      <section id="full-course" hidden>
      <div class="callout"><b>Learning objective:</b> ${esc(w.objective)}</div>
      <nav class="course-stage-nav" aria-label="Course week sections">
        ${[["all", "All"], ["learn", "1. Learn"], ["do", "2. Do"], ["measure", "3. Measure"], ["decide", "4. Decide"], ["evidence", "5. Evidence"]].map(([key, label]) => `<button class="btn ${key === "all" ? "primary" : ""}" type="button" data-stage="${key}">${label}</button>`).join("")}
      </nav>
      <section data-stage-panel="learn">
      ${how.plain ? `<div class="card howto-plain"><h3>In simple words</h3><p>${esc(how.plain)}</p>${how.time ? `<p class="small muted">⏱ ${esc(how.time)}</p>` : ""}</div>` : ""}
      ${how.days?.length ? `<div class="card"><h3>What to do each day this week</h3><ol class="lesson-steps">${how.days.map((x, i) => `<li><span class="step-num">${i + 1}</span><div><b>Day ${i + 1}${isCurrent && ctx.dayInWeek === i ? " — today" : ""}:</b> ${esc(x)}</div></li>`).join("")}</ol></div>` : ""}
      <div class="card"><h3>What you need to understand</h3><p>${esc(w.understand)}</p></div>
      ${guide.why ? `<div class="card"><h3>Why this week matters</h3><p>${esc(guide.why)}</p></div>` : ""}
      ${guide.prepare?.length ? `<div class="card"><h3>Before you begin</h3><ul>${guide.prepare.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>` : ""}
      ${guide.steps?.length ? `<div class="card"><h3>Step-by-step practical workflow</h3><ol class="lesson-steps">${guide.steps.map((x, i) => `<li><span class="step-num">${i + 1}</span><div>${esc(x)}</div></li>`).join("")}</ol></div>` : ""}
      </section>

      <section data-stage-panel="do">
      <div class="card"><h3>7-day rhythm</h3><div class="days">${C.dailyRhythm.map((t, i) => `<div class="day ${d.days[i] ? "done" : ""} ${isCurrent && ctx.dayInWeek === i ? "today" : ""}" data-day="${i}"><b>Day ${i + 1}</b><span>${esc(t)}</span><span class="small muted">${addDays(from, i).slice(5)}</span></div>`).join("")}</div></div>

      <div class="card"><div class="row spread"><h3>Hands-on Outreach Recruitment tasks</h3><div class="row"><button class="btn small" type="button" id="copy-task-column">Copy tasks</button><button class="btn small" type="button" id="copy-notion-page">Copy Notion page</button><button class="btn small" type="button" id="download-week-pack">Download weekly pack</button>${trackerLink}</div></div>
        <p class="small muted">Copy or download a single “Task” column for Google Sheets or a Notion table.</p>
        <ul class="checklist">${w.tasks.map((t, i) => `<li class="${d.tasks[i]?.done ? "done" : ""}"><input type="checkbox" data-task="${i}" ${d.tasks[i]?.done ? "checked" : ""}><div class="grow"><div class="txt">Task ${i + 1}. ${esc(t)}</div>${how.tasks?.[i] ? `<details class="howto"><summary>How to do this</summary><p>${esc(how.tasks[i])}</p></details>` : ""}<input class="small" data-tasknote="${i}" placeholder="Notes / evidence / link" value="${esc(d.tasks[i]?.note)}" style="margin-top:4px"></div></li>`).join("")}</ul>
        <details class="notion-exports"><summary>More Google Sheets &amp; Notion exports</summary><div class="export-grid">
          <button class="btn small" type="button" data-copy-export="tasks">Tasks</button>
          <button class="btn small" type="button" data-copy-export="days">Daily plan</button>
          <button class="btn small" type="button" data-copy-export="questions">Questions for notes</button>
          <button class="btn small" type="button" data-copy-export="evidence">Evidence checklist</button>
          <button class="btn small" type="button" data-copy-export="kpis">KPI actions</button>
          <button class="btn small" type="button" data-copy-export="review">Weekly review</button>
          <button class="btn small" type="button" data-copy-export="unfinished">Unfinished tasks</button>
          <button class="btn small" type="button" data-copy-export="action">Action plan</button>
          <button class="btn small" type="button" data-copy-export="portfolio">Portfolio log</button>
          <button class="btn small" type="button" id="copy-all-weeks">All 16 weeks</button>
          <button class="btn small" type="button" id="download-task-column">Tasks CSV</button>
          <a class="btn small" href="notion-templates/outreach-notion-course-pack.zip" download>Download Notion database pack</a>
          <a class="btn small" href="notion-templates/NOTION_IMPORT_GUIDE.md" download>Import guide</a>
        </div><p class="small muted">Each copy option uses one item per row. The database pack includes linked templates for tasks, KPIs, experiments and evidence.</p></details>
      </div>

      <div class="card"><h3>Practice worksheet</h3><div class="form-grid">${C.worksheet.map((q, i) => `<label class="wide">${esc(q)}<textarea data-ws="${i}">${esc(d.worksheet[i])}</textarea></label>`).join("")}</div></div>
      </section>

      <section data-stage-panel="measure">
      <div class="card measurement-plan">
        <div class="row spread"><div><span class="eyebrow">Use data → decide → act</span><h3>Measurement &amp; action guide for Week ${n}</h3></div><a class="btn" href="#/t/seo_kpi_daily">Open KPI data →</a></div>
        <p class="measurement-question"><b>Business question:</b> ${esc(metricPlan.question)}</p>
        <div class="measurement-grid">
          ${focusedKpis.map(([k, l, kind]) => { const dd = delta(cur[k], prev[k], kind); const suggestion = suggestedKpiAction(k, cur[k], prev[k]); return `<article class="metric-action"><div class="row spread"><b>${esc(l)}</b><span class="${dd.cls}">${dd.txt}</span></div><div class="metric-values"><span>Previous <b>${fmtKpi(prev[k], kind)}</b></span><span>Current <b>${fmtKpi(cur[k], kind)}</b></span></div><p>${esc(suggestion)}</p><button class="btn small" type="button" data-use-action="${esc(k)}" data-suggestion="${esc(suggestion)}">Use this action</button></article>`; }).join("")}
        </div>
        <div class="measurement-notes"><p><b>Get the data from:</b> ${esc(metricPlan.source)}</p><p><b>Recommended next move:</b> ${esc(metricPlan.action)}</p><p><b>Recommended review:</b> ${reviewDays} days after implementation</p><p class="small muted"><b>Decision rule:</b> compare equal periods, check page/query detail, and change one main variable at a time. A KPI movement is a signal to investigate, not proof of cause.</p></div>
      </div>

      <div class="card"><div class="row spread"><h3>QCM / Knowledge check</h3><button class="btn small" id="show-guide">Show answer guide</button></div>
        ${w.qcm.map((q, i) => `<div class="qcm"><b>${i + 1}. ${esc(q)}</b>
          <textarea data-qa="${i}" placeholder="Your answer in your own words">${esc(d.qcm[i]?.answer)}</textarea>
          <div class="row" style="margin-top:6px"><span class="small muted">Self-mark after checking the guide:</span>
          <select data-qm="${i}" style="width:auto">${["", "correct", "partial", "wrong"].map((m) => `<option value="${m}" ${d.qcm[i]?.mark === m ? "selected" : ""}>${m || "—"}</option>`).join("")}</select></div></div>`).join("")}
        <div class="answer-guide" id="guide" hidden><b>Answer & revision guide:</b> ${esc(w.answers)}</div></div>

      ${revisions.length ? `<div class="card"><h3>Two-week QCM revision</h3><p class="muted small">Questions marked wrong or partial in Week ${n - 2} are due again.</p><ol>${revisions.map((x) => `<li><b>${esc(x.q)}</b> <span class="badge warn">${esc(x.mark)}</span></li>`).join("")}</ol><a class="btn" href="#/course/${n - 2}">Revise Week ${n - 2} answers →</a></div>` : ""}

      <div class="card"><h3>Weekly KPI review <span class="muted small">(auto from Daily KPI tracking: ${from} → ${to} vs previous 7 days · ${cur.days}/7 days logged)</span></h3>
        <div class="row"><span class="badge ${confidence.cls}">${confidence.label}</span><span class="small muted">${esc(confidence.note)}</span><button class="btn small" type="button" id="toggle-all-kpis">Show all metrics</button></div>
        <p class="pattern-insight"><b>Combined signal:</b> ${esc(patternInsight(cur, prev))}</p>
        <div class="table-wrap"><table><thead><tr><th>KPI</th><th class="num">Previous</th><th class="num">Current</th><th class="num">Change</th><th>Action</th></tr></thead><tbody>
        ${KPI_KEYS.map(([k, l, kind]) => { const dd = delta(cur[k], prev[k], kind); const focused = metricPlan.kpis.includes(k); return `<tr class="${focused ? "kpi-focus" : "kpi-secondary"}"><td>${focused ? '<span class="focus-dot" title="Week focus"></span>' : ""}${l}</td><td class="num">${fmtKpi(prev[k], kind)}</td><td class="num">${fmtKpi(cur[k], kind)}</td><td class="num ${dd.cls}">${dd.txt}</td><td><input data-ka="${k}" value="${esc(d.kpiActions[k])}" placeholder="${focused ? "Record this week's action" : "Optional action"}"></td></tr>`; }).join("")}
        </tbody></table></div>
        ${cur.days < 7 ? `<p class="small muted" style="margin-top:8px">Missing days? <a href="#/t/seo_kpi_daily">Import the GSC Dates export</a>.</p>` : ""}</div>
      </section>

      <section data-stage-panel="decide">
        <div class="card"><div class="row spread"><div><span class="eyebrow">Structured action builder</span><h3>Turn the evidence into one measurable action</h3></div><span class="badge">Review in ${reviewDays} days</span></div>
          <div class="form-grid">
            <label class="wide">Observation — what changed?<textarea data-ap="observation">${esc(d.actionPlan.observation)}</textarea></label>
            <label>Target page<input data-ap="page" value="${esc(d.actionPlan.page)}" placeholder="/page-or-job/"></label>
            <label>Target query<input data-ap="query" value="${esc(d.actionPlan.query)}" placeholder="hospitality jobs Malta"></label>
            <label>Segment / sector<input data-ap="segment" value="${esc(d.actionPlan.segment)}" placeholder="Hospitality, employer, mobile…"></label>
            <label>Audience<select data-ap="audience">${["", "Candidate", "Employer", "Both"].map((x) => `<option ${d.actionPlan.audience === x ? "selected" : ""}>${x || "Select…"}</option>`).join("")}</select></label>
            <label class="wide">Hypothesis — why might it have changed?<textarea data-ap="hypothesis">${esc(d.actionPlan.hypothesis)}</textarea></label>
            <label class="wide">Focused action<textarea data-ap="action">${esc(d.actionPlan.action)}</textarea></label>
            <label>Owner<input data-ap="owner" value="${esc(d.actionPlan.owner)}"></label>
            <label>Review date<input type="date" data-ap="reviewDate" value="${esc(d.actionPlan.reviewDate)}"></label>
            <label>Success target<input data-ap="target" value="${esc(d.actionPlan.target)}" placeholder="e.g. CTR improves by 0.5 points"></label>
            <label>Decision confidence<select data-ap="confidence">${["", "Low", "Medium", "High"].map((x) => `<option ${d.actionPlan.confidence === x ? "selected" : ""}>${x || "Select…"}</option>`).join("")}</select></label>
          </div>
          <div class="row spread"><p class="small muted" id="action-sentence">Complete the fields to create a clear action statement.</p><div class="row"><button class="btn" type="button" id="build-action">Build action sentence</button><button class="btn primary" type="button" id="create-experiment">Create experiment</button></div></div>
        </div>

        <div class="grid c2 example-grid">
          <div class="card"><span class="badge good">Good action</span><p>${esc(metricPlan.action)}</p></div>
          <div class="card"><span class="badge bad">Avoid</span><p>“Improve SEO.” It has no page, evidence, owner, success target or review date.</p></div>
          <div class="card"><span class="badge warn">Misleading interpretation</span><p>A percentage increase from a tiny sample proves the change worked. Always inspect the absolute values and data confidence.</p></div>
          <div class="card"><span class="badge info">Worked example</span><p>${esc(how.example || `Choose one ${focusedKpis[0]?.[1] || "KPI"} signal, make one focused change and review it after ${reviewDays} days.`)}</p></div>
        </div>

        <div class="card"><h3>End-of-week decision</h3><div class="form-grid"><label>Decision<select id="final-choice">${["", "Keep", "Improve", "Expand", "Wait", "Reverse", "Investigate"].map((x) => `<option ${d.finalDecision.choice === x ? "selected" : ""}>${x || "Select…"}</option>`).join("")}</select></label><label class="wide">Evidence-based reason<textarea id="final-reason" placeholder="What evidence supports this decision?">${esc(d.finalDecision.reason)}</textarea></label></div></div>
      </section>

      <section data-stage-panel="evidence">

      <div class="card"><h3>Required deliverable: ${esc(w.deliverable)}</h3>
        <label class="row" style="margin-bottom:8px"><input type="checkbox" id="dl-done" ${d.deliverable.done ? "checked" : ""}> Deliverable completed and saved</label>
        <div class="form-grid"><label>Link to deliverable (doc / sheet / commit / URL)<input id="dl-link" value="${esc(d.deliverable.link)}"></label>
        <label>Notes<input id="dl-notes" value="${esc(d.deliverable.notes)}"></label></div></div>

      ${(guide.evidence?.length || guide.pitfalls?.length) ? `<div class="lesson-columns">
        <div class="card"><div class="row spread"><h3>Evidence to save</h3><a class="btn small" href="#/t/seo_evidence?add=1&week=${n}">Add evidence →</a></div><p class="muted small">This proves the task was completed and makes the final case study easier.</p><ul>${(guide.evidence || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
        <div class="card"><h3>Common mistakes to avoid</h3><ul>${(guide.pitfalls || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
      </div>` : ""}

      ${how.example ? `<div class="card"><h3>Worked example</h3><p>${esc(how.example)}</p></div>` : ""}
      ${how.done ? `<div class="callout"><b>This week is finished when:</b> ${esc(how.done)}</div>` : ""}
      <div class="callout"><b>Definition of done:</b> Complete the practical tasks, implement one action, attach evidence, set a review date, and record an evidence-based end-of-week decision.</div>

      <div class="card"><h3>Weekly résumé</h3><div class="form-grid">
        ${[0, 1, 2].map((i) => `<label>Thing I learned ${i + 1}<input data-rl="${i}" value="${esc(d.resume.learned?.[i])}"></label>`).join("")}
        ${[0, 1, 2].map((i) => `<label>Issue / opportunity ${i + 1}<input data-ri="${i}" value="${esc(d.resume.issues?.[i])}"></label>`).join("")}
        <label class="wide">Next priority<input id="r-next" value="${esc(d.resume.next)}"></label></div></div>
      </section>
      </section>`;

    const state = $("#save-state");
    let timer;
    const save = (immediate) => {
      state.textContent = "Saving…";
      clearTimeout(timer);
      timer = setTimeout(async () => {
        try { await Store.setWeek(n, d); state.textContent = "Saved ✓ " + new Date().toLocaleTimeString().slice(0, 5); }
        catch { state.textContent = "Save failed"; }
      }, immediate ? 0 : 700);
    };
    $("#show-full-course").onclick = () => {
      $("#simple-course").hidden = true;
      $("#full-course").hidden = false;
      $("#full-course").scrollIntoView({ behavior: "smooth", block: "start" });
    };
    const returnToSimple = document.createElement("button");
    returnToSimple.className = "btn small simple-return";
    returnToSimple.type = "button";
    returnToSimple.textContent = "← Simple view";
    returnToSimple.onclick = () => {
      $("#full-course").hidden = true;
      $("#simple-course").hidden = false;
      $("#simple-course").scrollIntoView({ behavior: "smooth", block: "start" });
    };
    $("#full-course").prepend(returnToSimple);
    $("#simple-task-note").oninput = (e) => {
      d.tasks[simpleTaskIndex] = { ...(d.tasks[simpleTaskIndex] || {}), note: e.target.value };
      const detailedNote = $(`[data-tasknote="${simpleTaskIndex}"]`);
      if (detailedNote) detailedNote.value = e.target.value;
      save();
    };
    $("#complete-simple-task").onclick = () => {
      if (d.tasks[simpleTaskIndex]?.done) return toast("This task is already complete. Return tomorrow or open full details for the weekly review.");
      d.tasks[simpleTaskIndex] = { ...(d.tasks[simpleTaskIndex] || {}), done: true };
      save(true);
      toast("Task complete — well done. The next task will appear when you reopen the week.");
      setTimeout(() => renderWeek(n), 500);
    };
    $$("[data-stage]").forEach((button) => (button.onclick = () => {
      const stage = button.dataset.stage;
      $$("[data-stage]").forEach((b) => b.classList.toggle("primary", b === button));
      $$("[data-stage-panel]").forEach((panel) => (panel.hidden = stage !== "all" && panel.dataset.stagePanel !== stage));
      const target = stage === "all" ? $('[data-stage-panel="learn"]') : $(`[data-stage-panel="${stage}"]`);
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
    }));
    const secondaryRows = $$(".kpi-secondary");
    secondaryRows.forEach((row) => (row.hidden = true));
    $("#toggle-all-kpis").onclick = (e) => {
      const show = secondaryRows.some((row) => row.hidden);
      secondaryRows.forEach((row) => (row.hidden = !show));
      e.currentTarget.textContent = show ? "Show focused metrics" : "Show all metrics";
    };
    const taskStatus = (i) => d.tasks[i]?.done ? "Complete" : d.tasks[i]?.note ? "In progress" : "To do";
    const taskColumn = w.tasks.map((task, i) => `Week ${n} · Task ${i + 1} · ${taskStatus(i)} · ${task}`);
    const exportRows = () => ({
      tasks: taskColumn,
      days: C.dailyRhythm.map((item, i) => `Week ${n} · Day ${i + 1} · ${d.days[i] ? "Complete" : "To do"} · ${addDays(from, i)} · ${item}`),
      questions: [...C.worksheet.map((item, i) => `Week ${n} · Note question ${i + 1} · ${item}`), ...w.qcm.map((item, i) => `Week ${n} · Knowledge question ${i + 1} · ${item}`)],
      evidence: (guide.evidence || []).map((item, i) => `Week ${n} · Evidence ${i + 1} · ${item}`),
      kpis: focusedKpis.map(([k, label, kind]) => `Week ${n} · KPI · ${label} · Previous ${fmtKpi(prev[k], kind)} · Current ${fmtKpi(cur[k], kind)} · ${delta(cur[k], prev[k], kind).txt} · Action: ${d.kpiActions[k] || "Waiting for data"}`),
      review: [`Week ${n} · Decision · ${d.finalDecision.choice || "Waiting for data"}`, `Week ${n} · Decision reason · ${d.finalDecision.reason || "Not recorded"}`, `Week ${n} · Next priority · ${d.resume.next || "Not recorded"}`, `Week ${n} · Review date · ${d.actionPlan.reviewDate || addDays(today(), reviewDays)}`],
      unfinished: w.tasks.map((task, i) => ({ task, i })).filter(({ i }) => !d.tasks[i]?.done).map(({ task, i }) => `Week ${n} · Task ${i + 1} · ${taskStatus(i)} · ${task}`),
      action: [`Week ${n} · Observation · ${d.actionPlan.observation || "Not recorded"}`, `Week ${n} · Page · ${d.actionPlan.page || "Not selected"}`, `Week ${n} · Query · ${d.actionPlan.query || "Not selected"}`, `Week ${n} · Hypothesis · ${d.actionPlan.hypothesis || "Not recorded"}`, `Week ${n} · Action · ${d.actionPlan.action || metricPlan.action}`, `Week ${n} · Owner · ${d.actionPlan.owner || "Not assigned"}`, `Week ${n} · Review date · ${d.actionPlan.reviewDate}`, `Week ${n} · Success target · ${d.actionPlan.target || "Not set"}`],
      portfolio: [...w.tasks.map((task, i) => ({ task, i })).filter(({ i }) => d.tasks[i]?.done).map(({ task, i }) => `Week ${n} · Completed task ${i + 1} · ${task}${d.tasks[i]?.note ? ` · Evidence: ${d.tasks[i].note}` : ""}`), ...(d.deliverable.done ? [`Week ${n} · Deliverable · ${w.deliverable} · ${d.deliverable.link || d.deliverable.notes || "Completed"}`] : []), ...(d.finalDecision.choice ? [`Week ${n} · Outcome · ${d.finalDecision.choice} · ${d.finalDecision.reason || "No reason recorded"}`] : [])]
    });
    const notionPage = () => {
      const rows = exportRows();
      const checks = w.tasks.map((task, i) => `- [${d.tasks[i]?.done ? "x" : " "}] ${task}${d.tasks[i]?.note ? ` — ${d.tasks[i].note}` : ""}`).join("\n");
      return `# Week ${n} — ${w.title}\n\n## Objective\n${w.objective}\n\n## Tasks\n${checks}\n\n## Daily plan\n${rows.days.map((x) => `- ${x}`).join("\n")}\n\n## KPI focus\n${rows.kpis.map((x) => `- ${x}`).join("\n")}\n\n## Action\n${rows.action.map((x) => `- ${x}`).join("\n")}\n\n## Evidence\n${rows.evidence.map((x) => `- [ ] ${x}`).join("\n") || "- [ ] Add evidence"}\n\n## Weekly decision\n${rows.review.join("\n")}\n`;
    };
    $("#copy-task-column").onclick = async () => {
      const copied = await copyPlainText(taskColumn.join("\n"));
      toast(copied ? "Task column copied — paste into Sheets or Notion" : "Copy failed; use Download CSV instead");
    };
    $("#copy-notion-page").onclick = async () => toast(await copyPlainText(notionPage()) ? "Notion page copied" : "Copy failed");
    $$("[data-copy-export]").forEach((button) => (button.onclick = async () => {
      const rows = exportRows()[button.dataset.copyExport] || [];
      if (!rows.length) return toast("Nothing to export yet");
      toast(await copyPlainText(rows.join("\n")) ? `${button.textContent} copied as one column` : "Copy failed");
    }));
    $("#copy-all-weeks").onclick = async () => {
      const saved = Object.fromEntries((await Store.list("seo_course_weeks")).map((row) => [+row.week, row.data || {}]));
      const rows = C.weeks.flatMap((week) => week.tasks.map((task, i) => {
        const wd = saved[week.n] || {}, status = wd.tasks?.[i]?.done ? "Complete" : wd.tasks?.[i]?.note ? "In progress" : "To do";
        return `Week ${week.n} · ${week.title} · Task ${i + 1} · ${status} · ${task}`;
      }));
      toast(await copyPlainText(rows.join("\n")) ? "All 16 weeks copied as one column" : "Copy failed");
    };
    $("#download-week-pack").onclick = () => {
      const rows = exportRows(), combined = Object.values(rows).flat();
      download(`course-week-${n}-notion-pack.md`, notionPage(), "text/markdown");
      setTimeout(() => download(`course-week-${n}-one-column.csv`, oneColumnCSV("Item", combined), "text/csv"), 250);
      toast("Weekly Markdown and one-column CSV prepared");
    };
    $("#download-task-column").onclick = () => {
      download(`course-week-${n}-tasks.csv`, oneColumnCSV("Task", taskColumn), "text/csv");
    };
    $$("[data-day]").forEach((el) => (el.onclick = () => { const i = +el.dataset.day; d.days[i] = !d.days[i]; el.classList.toggle("done", d.days[i]); save(true); }));
    $$("[data-task]").forEach((el) => (el.onchange = () => { const i = el.dataset.task; d.tasks[i] = { ...(d.tasks[i] || {}), done: el.checked }; el.closest("li").classList.toggle("done", el.checked); save(true); }));
    $$("[data-tasknote]").forEach((el) => (el.oninput = () => { const i = el.dataset.tasknote; d.tasks[i] = { ...(d.tasks[i] || {}), note: el.value }; save(); }));
    $$("[data-ws]").forEach((el) => (el.oninput = () => { d.worksheet[el.dataset.ws] = el.value; save(); }));
    $$("[data-qa]").forEach((el) => (el.oninput = () => { const i = el.dataset.qa; d.qcm[i] = { ...(d.qcm[i] || {}), answer: el.value }; save(); }));
    $$("[data-qm]").forEach((el) => (el.onchange = () => { const i = el.dataset.qm; d.qcm[i] = { ...(d.qcm[i] || {}), mark: el.value }; save(true); }));
    $$("[data-ka]").forEach((el) => (el.oninput = () => { d.kpiActions[el.dataset.ka] = el.value; save(); }));
    $$("[data-use-action]").forEach((el) => (el.onclick = () => {
      const input = $(`[data-ka="${el.dataset.useAction}"]`);
      if (!input) return;
      input.value = el.dataset.suggestion;
      d.kpiActions[el.dataset.useAction] = el.dataset.suggestion;
      d.actionPlan.observation = `${kpiDef(el.dataset.useAction)[1]}: ${input.closest("tr").children[3].textContent.trim()} versus the previous period.`;
      d.actionPlan.action = el.dataset.suggestion;
      $('[data-ap="observation"]').value = d.actionPlan.observation;
      $('[data-ap="action"]').value = d.actionPlan.action;
      save(true);
      $('[data-stage="decide"]').click();
    }));
    $$("[data-ap]").forEach((el) => {
      const update = () => { d.actionPlan[el.dataset.ap] = el.value; save(); };
      el.oninput = update;
      if (el.tagName === "SELECT") el.onchange = update;
    });
    const actionSentence = () => {
      const a = d.actionPlan;
      return `${a.observation || "The selected KPI changed"} We will ${a.action || "take one focused action"}${a.page ? ` on ${a.page}` : ""}${a.owner ? ` (owner: ${a.owner})` : ""} and review on ${a.reviewDate || addDays(today(), reviewDays)}${a.target ? `; success means ${a.target}` : ""}.`;
    };
    $("#build-action").onclick = () => { $("#action-sentence").textContent = actionSentence(); d.resume.next = actionSentence(); $("#r-next").value = d.resume.next; save(true); };
    $("#create-experiment").onclick = async () => {
      const a = d.actionPlan;
      if (!a.action || !a.hypothesis || !a.reviewDate) return toast("Add an action, hypothesis and review date first");
      const baseline = focusedKpis.map(([k, l, kind]) => `${l}: ${fmtKpi(cur[k], kind)} (previous ${fmtKpi(prev[k], kind)})`).join("; ");
      try {
        const experiment = await Store.upsert("seo_experiments", {
          source_key: `course-week-${n}-${Date.now()}`,
          change: a.action,
          hypothesis: a.hypothesis,
          page: a.page,
          start_date: today(),
          review_date: a.reviewDate,
          before_data: baseline,
          status: "monitoring",
          review_schedule: [a.reviewDate],
          conclusion: `Week ${n}; ${a.audience || "audience not set"}; target: ${a.target || "not set"}`
        }, "source_key");
        d.actionPlan.experimentId = experiment.id || experiment.source_key;
        await Store.setWeek(n, d);
        toast("Experiment created and linked to this week");
        $("#create-experiment").textContent = "Experiment created ✓";
      } catch { toast("Could not create experiment"); }
    };
    $("#final-choice").onchange = (e) => { d.finalDecision.choice = e.target.value; save(true); };
    $("#final-reason").oninput = (e) => { d.finalDecision.reason = e.target.value; save(); };
    $("#dl-done").onchange = (e) => { d.deliverable.done = e.target.checked; save(true); };
    $("#dl-link").oninput = (e) => { d.deliverable.link = e.target.value; save(); };
    $("#dl-notes").oninput = (e) => { d.deliverable.notes = e.target.value; save(); };
    $$("[data-rl]").forEach((el) => (el.oninput = () => { d.resume.learned = d.resume.learned || []; d.resume.learned[el.dataset.rl] = el.value; save(); }));
    $$("[data-ri]").forEach((el) => (el.oninput = () => { d.resume.issues = d.resume.issues || []; d.resume.issues[el.dataset.ri] = el.value; save(); }));
    $("#r-next").oninput = (e) => { d.resume.next = e.target.value; save(); };
    $("#show-guide").onclick = () => { const g = $("#guide"); g.hidden = !g.hidden; };
  }

  // ── Final case study ──
  async function renderFinal() {
    const ctx = await courseCtx();
    const [kpi, kws, links, tech, w0] = await Promise.all([Store.list("seo_kpi_daily"), Store.list("seo_keywords"), Store.list("seo_backlinks"), Store.list("seo_technical"), Store.getWeek(0)]);
    const day1 = aggregate(kpi, addDays(ctx.start, -28), addDays(ctx.start, -1));
    const end = addDays(ctx.start, 119);
    const day120 = aggregate(kpi, addDays(end, -27), end);
    const top10Base = kws.filter((k) => k.baseline_position != null && k.baseline_position <= 10).length;
    const top10Now = kws.filter((k) => k.current_position != null && k.current_position <= 10).length;
    const acquired = links.filter((l) => l.status === "acquired").length;
    const f = w0.final || {};
    const rows = [...KPI_KEYS.map(([k, l, kind]) => [l, fmtKpi(day1[k], kind), fmtKpi(day120[k], kind), delta(day120[k], day1[k], kind), k]),
      ["Top 10 keywords", top10Base, top10Now, delta(top10Now, top10Base, "sum"), "top10"],
      ["Referring domains (acquired)", "0", acquired, delta(acquired, 0, "sum"), "rd"]];
    view().innerHTML = `
      <div class="page-head"><div><h1>Final project — 120-Day SEO Case Study</h1>
        <p class="muted">Day 1 = 28 days before ${ctx.start}. Day 120 = 28 days ending ${end}. Numbers fill in automatically from your trackers.</p></div><span class="save-state" id="save-state"></span></div>
      <div class="card"><h3>Part A — Before</h3><p class="muted small">Baseline Search Console + GA4 data, priority keyword positions, indexed pages and technical issues, applications and employer leads.</p>
        <textarea data-f="partA" placeholder="Summarise the baseline">${esc(f.partA)}</textarea></div>
      <div class="card"><h3>Part B — Work completed</h3>
        <p class="small muted">Tracker totals: ${tech.filter((t) => ["fixed", "validated"].includes(t.status)).length} technical fixes · ${kws.length} keywords mapped · ${acquired} links acquired</p>
        <div class="form-grid">${["Technical fixes", "On-page optimization", "Sector pages and content", "Internal linking", "Local SEO actions", "Backlinks/citations", "AEO/GEO improvements"].map((l, i) => `<label>${l}<textarea data-fb="${i}">${esc(f.partB?.[i])}</textarea></label>`).join("")}</div></div>
      <div class="card"><h3>Part C — After</h3><div class="table-wrap"><table><thead><tr><th>KPI</th><th class="num">Day 1</th><th class="num">Day 120</th><th class="num">Change</th><th>Interpretation</th></tr></thead><tbody>
        ${rows.map(([l, a, b, dd, k]) => `<tr><td>${l}</td><td class="num">${a}</td><td class="num">${b}</td><td class="num ${dd.cls}">${dd.txt}</td><td><input data-fi="${k}" value="${esc(f.interp?.[k])}"></td></tr>`).join("")}</tbody></table></div></div>
      <div class="card"><h3>Part D — Your conclusion</h3><div class="form-grid">
        ${[["worked", "What worked best?"], ["notWorked", "What did not work as expected?"], ["evidence", "What evidence supports the conclusion?"], ["priorities", "What are the next 5 priorities?"], ["objective", "Next 90-day objective"]].map(([k, l]) => `<label class="wide">${l}<textarea data-f="${k}">${esc(f[k])}</textarea></label>`).join("")}</div>
        <label class="row"><input type="checkbox" id="f-done" ${f.done ? "checked" : ""}> Final case study complete</label></div>`;
    const state = $("#save-state"); let timer;
    const data = { ...w0, final: { ...f, partB: f.partB || [], interp: f.interp || {} } };
    const save = () => { state.textContent = "Saving…"; clearTimeout(timer); timer = setTimeout(async () => { await Store.setWeek(0, data); state.textContent = "Saved ✓"; }, 600); };
    $$("[data-f]").forEach((el) => (el.oninput = () => { data.final[el.dataset.f] = el.value; save(); }));
    $$("[data-fb]").forEach((el) => (el.oninput = () => { data.final.partB[el.dataset.fb] = el.value; save(); }));
    $$("[data-fi]").forEach((el) => (el.oninput = () => { data.final.interp[el.dataset.fi] = el.value; save(); }));
    $("#f-done").onchange = (e) => { data.final.done = e.target.checked; save(); };
  }

  function renderPlaybook() {
    view().innerHTML = `<h1>Playbook &amp; KPI decision framework</h1>
      <div class="card"><h3>Sector SEO playbook</h3><p class="muted small">Use this page model for priority sectors. Sections change with search intent and real information — never clone the same text across sectors.</p>
        <div class="table-wrap"><table><thead><tr><th>Sector</th><th>Primary target</th><th>Supporting topics</th></tr></thead><tbody>${C.sectors.map((s) => `<tr><td>${esc(s[0])}</td><td>${esc(s[1])}</td><td class="muted">${esc(s[2])}</td></tr>`).join("")}</tbody></table></div>
        <h3 style="margin-top:14px">Sector page template</h3><ul>${["Primary keyword and search intent", "SEO title and meta description", "H1 and introductory direct answer", "Current vacancies", "Types of roles in the sector", "Skills/experience employers commonly request — only where supported", "Useful Malta-specific context", "Candidate FAQs", "Internal links to jobs and guides", "Application CTA", "Review/update date", "Baseline and follow-up KPI data"].map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
      <div class="card"><h3>SEO KPI decision framework</h3>${C.decisionFramework.map((x, i) => `<p><b>${i + 1}. ${esc(x.t)}</b><br>${esc(x.d)}</p>`).join("")}</div>
      <div class="card"><h3>Core formulas</h3><table><tbody>
        <tr><td>CTR</td><td>Clicks / Impressions × 100</td></tr><tr><td>Organic conversion rate</td><td>Organic conversions / Organic sessions × 100</td></tr>
        <tr><td>Traffic growth</td><td>(Current − Previous) / Previous × 100</td></tr><tr><td>Ranking improvement</td><td>Previous position − Current position (positive = improvement)</td></tr></tbody></table></div>
      <div class="card"><h3>Tools</h3><p>Google Search Console · GA4 · Google Business Profile · PageSpeed Insights · Rich Results Test · Schema.org · Bing Webmaster Tools · Google Trends · Keyword Planner · Screaming Frog (free tier)</p>
        <p class="muted small">Top-10 rankings are a target, not a guarantee. Don't overreact to one-day ranking changes: daily tracking is for observation; weekly and monthly comparisons are for decisions.</p></div>`;
  }

  async function renderSettings() {
    const B = CFG.BASELINE || {};
    view().innerHTML = `<h1>Settings &amp; data</h1>
      <div class="card"><h3>Storage</h3>
        ${Store.mode === "supabase"
          ? `<p><span class="badge good">Supabase connected</span> ${esc(CFG.SUPABASE_URL)}</p><p class="muted">Data is shared across devices and protected by row-level security (admin emails only).</p>`
          : `<p><span class="badge warn">Local mode</span> Data is saved in <b>this browser only</b>. Export a backup regularly.</p>
             <p class="muted">To switch to Supabase: run <code>supabase/admin_schema.sql</code> in the Supabase SQL editor, then fill <code>SUPABASE_URL</code> and <code>SUPABASE_ANON_KEY</code> in <code>admin/config.js</code>. Then use “Copy local data to Supabase” below once.</p>`}
      </div>
      <div class="card"><h3>Backup</h3><div class="row">
        <button class="btn" id="s-export">Export everything (JSON)</button>
        <label class="btn" style="margin:0">Import JSON backup<input type="file" id="s-import" accept=".json" hidden></label>
        ${Store.mode === "supabase" ? `<button class="btn primary" id="s-migrate">Copy local browser data to Supabase</button>` : ""}
      </div><p class="small muted" id="s-msg"></p></div>
      <div class="card"><h3>Baseline (from config)</h3><p>${esc(B.date)} · ${fmtInt(B.clicks28)} clicks · ${fmtInt(B.impressions28)} impressions (28 days, sitewide)</p></div>
      <div class="card"><h3>Theme</h3><div class="row">${["auto", "light", "dark"].map((t) => `<button class="btn" data-theme-set="${t}">${t}</button>`).join("")}</div></div>`;
    $("#s-export").onclick = async () => {
      const out = {}; for (const t of ALL_TABLES) out[t] = await Store.list(t, { force: true });
      download("seo-admin-backup-" + today() + ".json", JSON.stringify(out, null, 2));
    };
    const importAll = async (data) => {
      let n = 0;
      for (const t of ALL_TABLES) for (const r of data[t] || []) {
        const row = { ...r }; if (Store.mode === "supabase" && CONFLICT[t]) delete row.id;
        if (Store.mode === "supabase" && !CONFLICT[t] && row.id && !/^[0-9a-f-]{36}$/i.test(row.id)) delete row.id;
        try { await Store.upsert(t, row, CONFLICT[t] || "id"); n++; } catch {}
      }
      return n;
    };
    $("#s-import").onchange = async (e) => {
      const f = e.target.files[0]; if (!f) return;
      const n = await importAll(JSON.parse(await f.text())); $("#s-msg").textContent = `Imported ${n} rows.`;
    };
    const mig = $("#s-migrate");
    if (mig) mig.onclick = async () => {
      const data = {}; ALL_TABLES.forEach((t) => (data[t] = Store.lsGet(t)));
      const total = Object.values(data).reduce((a, r) => a + r.length, 0);
      if (!total) return ($("#s-msg").textContent = "No local data in this browser.");
      if (!confirm(`Copy ${total} local rows to Supabase?`)) return;
      const n = await importAll(data); $("#s-msg").textContent = `Copied ${n} rows to Supabase.`;
    };
    $$("[data-theme-set]").forEach((b) => (b.onclick = () => setTheme(b.dataset.themeSet)));
  }

  function setTheme(t) {
    if (t === "auto") document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("seoadmin:theme", t); } catch {}
  }

  // ─────────────────────────── Router ───────────────────────────
  async function route() {
    const [path, qs] = (location.hash.replace(/^#\/?/, "") || "today").split("?");
    const params = new URLSearchParams(qs || "");
    $$("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.route === path || (path.startsWith("course/") && a.dataset.route === "course/today" && path === "course/today")));
    window.scrollTo(0, 0);
    try {
      if (path === "today") return await renderToday();
      if (path === "dashboard") return await renderDashboard();
      if (path === "data" || path === "analytics") return await renderDataHub();
      if (path === "search-console") return await renderSearchConsole();
      if (path === "ga4") return await renderGA4();
      if (path === "workspace") return await renderWorkspace();
      if (path === "weekly-review") return await renderWeeklyReview();
      if (path === "sync") return await renderSyncCentre();
      if (path === "practice") return await renderPractice();
      if (path === "decisions") return await renderDecisions();
      if (path === "live") return await renderLive();
      if (path === "course") return await renderCourseMap();
      if (path.startsWith("course/")) return await renderWeek(path.split("/")[1]);
      if (path === "final") return await renderFinal();
      if (path === "playbook") return renderPlaybook();
      if (path === "settings") return await renderSettings();
      if (path.startsWith("t/") && TRACKERS[path.slice(2)]) return await renderTracker(path.slice(2), params);
      view().innerHTML = `<p>Page not found. <a href="#/today">Today</a></p>`;
    } catch (e) {
      console.error(e);
      view().innerHTML = `<div class="card"><h3>Something went wrong</h3><p class="error">${esc(e.message || e)}</p></div>`;
    }
  }

  // ─────────────────────────── Boot ───────────────────────────
  async function boot() {
    try { const t = localStorage.getItem("seoadmin:theme"); if (t) setTheme(t); } catch {}
    let advancedOpen = false;
    try { advancedOpen = localStorage.getItem("seoadmin:advanced-tools") === "open"; } catch {}
    const setAdvanced = (open) => {
      advancedOpen = open;
      $("#advanced-nav").hidden = !open;
      $("#advanced-toggle").textContent = open ? "Hide advanced tools" : "Show advanced tools";
      try { localStorage.setItem("seoadmin:advanced-tools", open ? "open" : "closed"); } catch {}
    };
    $("#advanced-toggle").onclick = () => setAdvanced(!advancedOpen);
    setAdvanced(advancedOpen);
    Store.init();
    $("#mode-badge").textContent = Store.mode === "supabase" ? "Supabase" : "Local mode";
    $("#mode-badge").className = "badge " + (Store.mode === "supabase" ? "good" : "warn");
    if (Store.mode === "supabase") {
      const { data } = await Store.sb.auth.getSession();
      if (!data.session) {
        $("#login").hidden = false;
        $("#login-form").onsubmit = async (e) => {
          e.preventDefault();
          const f = e.target;
          const { error } = await Store.sb.auth.signInWithPassword({ email: f.email.value, password: f.password.value });
          if (error) return ($("#login-error").textContent = error.message);
          location.reload();
        };
        return;
      }
      $("#logout").hidden = false;
      $("#logout").onclick = async () => { await Store.sb.auth.signOut(); location.reload(); };
    }
    $("#app").hidden = false;
    window.addEventListener("hashchange", route);
    route();
  }
  boot();
})();
