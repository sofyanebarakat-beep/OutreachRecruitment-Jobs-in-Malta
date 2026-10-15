/* Admin › Marketing › Social Media — title + subtitle + caption generator.
 *
 * One tab per content pillar. Each generator returns { title, subtitle, caption }:
 *   title    — the headline for the picture (short)
 *   subtitle — the line under it on the picture
 *   caption  — the post text (**bold** → 𝗯𝗼𝗹𝗱 for social, <strong> for email), link + hashtags
 * Live data: ../tools/jobs_registry.json (open jobs, sectors, salaries, publish dates).
 * Salary maths = the same 2026 tax bands / Class 1 SSC as /salary-calculator-malta.
 */
(() => {
  "use strict";
  const SITE = "https://outreachrecruitment.net";
  const K = () => window.MarketingKit;
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const eur = (n, d = 0) => "€" + (+n).toLocaleString("en-GB", { minimumFractionDigits: d, maximumFractionDigits: d });
  const pickIndex = (n, prev) => { if (n <= 1) return 0; let i; do { i = Math.floor(Math.random() * n); } while (i === prev); return i; };

  const TAGS = {
    base: "#OutreachRecruitment #Malta",
    employers: "#HiringInMalta #RecruitmentMalta #MaltaBusiness #TalentAcquisition #EmployersMalta",
    candidates: "#JobsInMalta #CareerTips #JobSearch #MaltaJobs #WorkInMalta",
    study: "#StudyInMalta #StudyAbroad #InternationalStudents #MaltaStudents #EducationMalta",
    salary: "#SalaryMalta #NetSalary #JobsInMalta #MaltaJobs #CareerTips",
    jobs: "#JobsInMalta #MaltaJobs #Hiring #NowHiring #WorkInMalta",
    quotes: "#MondayMotivation #CareerGrowth #WorkInMalta #Motivation",
    myths: "#MythVsFact #CareerTips #JobsInMalta #RecruitmentMalta",
    polls: "#Poll #JobsInMalta #WorkInMalta #CareerTalk",
  };

  // ── content banks (title ≤ ~45 chars for the picture, subtitle ≤ ~90) ──────
  const EMPLOYERS = [
    { t: "Hiring in Malta? We've got you covered", s: "Pre-screened candidates, faster shortlists, less admin for your team",
      b: "Finding the right people takes time you don't always have. **Outreach Recruitment** sources, screens and shortlists candidates for you — so you only meet the people worth meeting.\n\nRight now we're recruiting for **{open} open roles across {sectors} sectors** in Malta & Gozo.",
      cta: "📩 Tell us who you need:", url: "/employers" },
    { t: "Temporary or permanent hire?", s: "The right staffing model saves you time and money",
      b: "Seasonal peak, project deadline or a long-term gap in your team? Each needs a different hiring approach.\n\n✅ **Temporary** — fast cover, flexible cost\n✅ **Permanent** — long-term fit, lower turnover\n\nNot sure which suits you? We'll help you decide.",
      cta: "📖 Read the guide:", url: "/blog/permanent-vs-temporary-recruitment-malta" },
    { t: "Hire faster. Hire better.", s: "How a recruitment agency shortens your time-to-hire in Malta",
      b: "Every week a role stays empty costs your business. A specialist recruiter brings a ready talent pool, structured screening and market salary insight — so you fill roles faster, with fewer surprises.",
      cta: "📖 How it works:", url: "/blog/how-a-recruitment-agency-helps-malta-employers-hire-faster" },
    { t: "Your job ad is losing candidates", s: "5 fixes for job descriptions that actually attract applicants",
      b: "Vague titles, no salary, endless requirement lists… good candidates scroll past. Clear titles, honest pay ranges and a short, specific role summary make a real difference to how many people apply.",
      cta: "📖 Practical checklist:", url: "/blog/practical-checklist-writing-better-job-descriptions-malta" },
    { t: "Why employers trust Outreach Recruitment", s: "Local market knowledge · screened candidates · ongoing support",
      b: "From hospitality and construction to finance and IT, Malta's employers work with us because we understand their sector, their timelines and the talent market.\n\n🤝 Let's build your team together.",
      cta: "👉 Partner with us:", url: "/employers" },
    { t: "Stop losing candidates mid-process", s: "Slow replies are the #1 reason good applicants walk away",
      b: "Long silences between interview stages cost you your best candidates — they accept other offers. Quick feedback, clear next steps and fewer rounds keep them engaged.",
      cta: "📖 Reduce drop-off:", url: "/blog/reduce-candidate-drop-off-during-recruitment" },
    { t: "Structured interviews = better hires", s: "Same questions, clear scoring, fairer decisions",
      b: "Gut-feel interviews lead to costly hiring mistakes. Asking every candidate the same role-specific questions — and scoring answers against clear criteria — makes your decisions faster and fairer.",
      cta: "📖 Learn more:", url: "/blog/how-structured-interviews-improve-hiring-decisions" },
  ];
  const CANDIDATES = [
    { t: "5 CV mistakes to avoid in Malta", s: "Small fixes that get you more interview calls",
      b: "❌ No phone number or wrong email\n❌ The same CV for every job\n❌ Long paragraphs instead of results\n❌ Spelling mistakes\n❌ Missing work-permit / EU status\n\nFix these and recruiters will notice you faster.",
      cta: "📖 Full guide:", url: "/blog/common-cv-mistakes-malta-job-application" },
    { t: "Ace your next interview in Malta", s: "What employers really ask — and how to answer",
      b: "Prepare 3 short stories about your experience, research the company, and have 2 questions ready for the interviewer. Confidence comes from preparation.",
      cta: "📖 Common questions & answers:", url: "/blog/how-to-answer-common-interview-questions-in-malta" },
    { t: "Documents you need to apply", s: "Have these ready before you hit 'Apply'",
      b: "📄 Updated CV\n🪪 ID card or passport\n🎓 Certificates & qualifications\n📝 References\n🛂 Work permit / residence documents (if non-EU)\n\nBeing prepared speeds up your application.",
      cta: "📖 Complete checklist:", url: "/blog/what-documents-do-i-need-to-apply-for-a-job-in-malta" },
    { t: "Tailor your CV for every job", s: "One CV does not fit all — here's how to adapt it in 10 minutes",
      b: "Match your CV to the job ad: mirror the key skills, move the most relevant experience to the top, and add numbers that prove your results.",
      cta: "📖 Step by step:", url: "/blog/tailor-your-cv-for-jobs-in-malta" },
    { t: "After the interview: follow up!", s: "The simple email that keeps you top of mind",
      b: "Send a short thank-you within 24 hours: thank them for their time, repeat why you're a great fit, and say you look forward to hearing back. It works.",
      cta: "📖 Templates & timing:", url: "/blog/how-to-follow-up-after-job-interview-malta" },
    { t: "Looking for a job in Malta?", s: "{open} open positions — new roles added every week",
      b: "Hospitality, construction, finance, IT, marine and more — **Outreach Recruitment** has **{open} open positions** across Malta & Gozo right now. Apply online in minutes.",
      cta: "🌐 Browse all jobs:", url: "/jobs" },
    { t: "Prepare your references", s: "Who to ask — and what to tell them",
      b: "Choose recent managers who know your work, ask their permission first, and tell them which job you've applied for so they can highlight the right skills.",
      cta: "📖 Read more:", url: "/blog/prepare-references-job-application-malta" },
  ];
  const STUDY = [
    { t: "Why study in Malta?", s: "English-speaking · EU country · Mediterranean lifestyle",
      b: "🇲🇹 English is an official language\n🇪🇺 An EU member state\n☀️ Sunshine most of the year\n🎓 Courses from English to business, IT and healthcare\n\nMalta is becoming one of Europe's favourite student destinations.",
      cta: "📖 Complete guide:", url: "/study-in-malta-complete-guide" },
    { t: "Malta student visa: step by step", s: "From acceptance letter to arrival — what to prepare",
      b: "1️⃣ Choose your course and school\n2️⃣ Get your acceptance letter\n3️⃣ Prepare your documents\n4️⃣ Apply for the visa\n5️⃣ Plan your arrival\n\nWe guide you through every step.",
      cta: "📖 Visa guide:", url: "/malta-student-visa-complete-guide" },
    { t: "Cost of living for students in Malta", s: "Rent, food, transport — plan your budget before you arrive",
      b: "Knowing your monthly costs makes your study year stress-free. Our guide breaks down rent, groceries, transport and everyday expenses so you can plan with confidence.",
      cta: "📖 See the breakdown:", url: "/cost-of-living-in-malta-as-a-student" },
    { t: "Study English in Malta", s: "Learn in an English-speaking country — by the sea",
      b: "Improve your English while living it every day. English courses in Malta combine classes with real-life practice — at work, in shops and with friends from all over the world.",
      cta: "📖 English courses:", url: "/malta-study-guide/english-language-courses-in-malta" },
    { t: "How to apply to study in Malta", s: "A simple step-by-step guide for international students",
      b: "Choosing a course, checking entry requirements, applying and preparing your documents — it's easier than you think when you know the steps.",
      cta: "📖 Step-by-step guide:", url: "/how-to-apply-to-study-in-malta-a-step-by-step-guide" },
    { t: "Study now, work later in Malta", s: "Build skills, experience and your future career",
      b: "Studying in Malta is the first step to an international career. Learn, build your network and discover the opportunities waiting for you.",
      cta: "📖 Study in Malta for international students:", url: "/study-in-malta-for-international-students" },
  ];
  const QUOTES = [
    { q: "The only way to do great work is to love what you do.", a: "Steve Jobs" },
    { q: "Your next job should not just pay you. It should grow you.", a: "" },
    { q: "Every expert was once a beginner. Apply anyway.", a: "" },
    { q: "Great teams aren't found. They're built — one right hire at a time.", a: "" },
    { q: "Don't wait for the perfect job. Prepare for it.", a: "" },
    { q: "Talent wins games, but teamwork wins championships.", a: "Michael Jordan" },
    { q: "Your CV opens the door. Your attitude gets you the job.", a: "" },
    { q: "A new week is a new chance to take the next step in your career.", a: "" },
  ];
  const MYTHS = [
    { m: "Recruitment agencies charge candidates.", f: "Our service is free for candidates — employers pay for recruitment.", url: "/blog/what-to-expect-from-a-recruitment-agency-in-malta", tags: "candidates" },
    { m: "You need perfect English to work in Malta.", f: "Many roles need good communication, not perfection — and some value other languages too.", url: "/blog/language-requirements-customer-service-jobs-malta", tags: "candidates" },
    { m: "A longer CV looks more impressive.", f: "Recruiters prefer 1–2 clear pages focused on results.", url: "/blog/cv-writing-tips-how-to-get-hired-in-malta", tags: "candidates" },
    { m: "Agencies only send employers random CVs.", f: "We screen, interview and shortlist — you only meet suitable candidates.", url: "/blog/inside-the-outreach-recruitment-hiring-process", tags: "employers" },
    { m: "Temporary staff aren't worth training.", f: "The right temporary hire keeps your business running at peak times — and many become permanent.", url: "/blog/when-to-use-temporary-recruitment-support-malta", tags: "employers" },
    { m: "Applying to more jobs means more interviews.", f: "Tailored applications get far more replies than mass-sending one CV.", url: "/blog/tailor-your-cv-for-jobs-in-malta", tags: "candidates" },
  ];
  const POLLS = [
    { q: "What matters most to you in a new job?", o: ["💶 Salary", "⏰ Flexible hours", "📈 Career growth", "🤝 Great team"] },
    { q: "How do you usually find a new job?", o: ["🌐 Job websites", "🤝 Recruitment agency", "👥 Friends & network", "💼 LinkedIn"] },
    { q: "Employers: what's your biggest hiring challenge?", o: ["⏳ Time to hire", "🎯 Finding skills", "💶 Salary expectations", "🔁 Staff turnover"] },
    { q: "Would you prefer…", o: ["🏢 Office", "🏠 Remote", "🔀 Hybrid"] },
    { q: "How long should a job interview process take?", o: ["1 week", "2 weeks", "3–4 weeks", "It depends"] },
  ];
  const HUBS = {
    "Construction": "/construction-jobs-in-malta", "Hospitality": "/hospitality-jobs-in-malta",
    "Engineering & Maintenance": "/engineering-jobs-in-malta", "Finance & Accounting": "/finance-jobs-in-malta",
    "Insurance": "/insurance-jobs-in-malta", "IT & Technology": "/it-jobs-in-malta", "Manufacturing": "/manufacturing-jobs-in-malta",
    "Marine & Shipping": "/marine-jobs-in-malta", "Retail": "/retail-jobs-in-malta", "Sales": "/sales-jobs-in-malta",
    "Customer Service": "/customer-service-jobs-in-malta",
  };

  // ── salary maths (same as /salary-calculator-malta, 2026) ─────────────────
  const TAX_BANDS = {
    single: [[0, 9100, 0], [9100, 14500, 0.15], [14500, 60000, 0.25], [60000, Infinity, 0.35]],
    married: [[0, 12700, 0], [12700, 21200, 0.15], [21200, 60000, 0.25], [60000, Infinity, 0.35]],
    parent: [[0, 10500, 0], [10500, 15800, 0.15], [15800, 60000, 0.25], [60000, Infinity, 0.35]],
  };
  const annualTax = (g, st) => TAX_BANDS[st].reduce((t, [f, to, r]) => t + (g > f ? (Math.min(g, to) - f) * r : 0), 0);
  const weeklySSC = (w) => (w <= 229.44 ? 22.94 : w <= 559.30 ? w * 0.10 : 54.43);
  function netSalary(grossAnnual, status) {
    const tax = annualTax(grossAnnual, status), ssc = weeklySSC(grossAnnual / 52) * 52;
    const net = grossAnnual - tax - ssc;
    return { tax, ssc, net, netMonth: net / 12, grossMonth: grossAnnual / 12 };
  }

  // ── data ──────────────────────────────────────────────────────────────────
  let jobs = null;
  async function loadJobs() {
    if (jobs) return jobs;
    const reg = await (await fetch("../tools/jobs_registry.json?t=" + Date.now(), { cache: "no-store" })).json();
    jobs = reg.filter((j) => !/closed|expired/i.test(j.status || ""));
    return jobs;
  }
  const cityOf = (j) => String(j.location || "").split(",")[0].trim();
  const sectorsOf = (js) => {
    const m = new Map();
    for (const j of js) if (j.category && j.category !== "General") m.set(j.category, (m.get(j.category) || 0) + 1);
    return [...m.entries()].sort((a, b) => b[1] - a[1]);
  };
  const fillVars = (t, v) => t.replace(/\{(\w+)\}/g, (_, k) => v[k] ?? "");
  const tagsFor = (...keys) => [...new Set(keys.flatMap((k) => (TAGS[k] || k).split(" ")).concat(TAGS.base.split(" ")))].join(" ");
  const caption = (lines) => lines.filter((l) => l !== null && l !== undefined && l !== "").join("\n\n");

  // ── generators ────────────────────────────────────────────────────────────
  const TABS = [
    { id: "employers", label: "👔 Employers", hint: "Hiring tips and your services for businesses in Malta." },
    { id: "candidates", label: "🙋 Candidates", hint: "CV, interview and job-search tips — each linking to a blog guide." },
    { id: "study", label: "🎓 Study in Malta", hint: "Student visa, cost of living and why Malta — linking to your study guides." },
    { id: "salary", label: "💶 Salary calculator", hint: "“€X gross = €Y net per month” — same maths as /salary-calculator-malta." },
    { id: "newjobs", label: "🆕 New jobs this week", hint: "A round-up of the jobs published in the last 7 days (or the latest ones)." },
    { id: "sector", label: "🏭 Jobs by sector", hint: "Open jobs in one sector, linking to its hub page." },
    { id: "quotes", label: "💬 Quotes", hint: "Motivational quotes for Monday posts and stories." },
    { id: "myths", label: "💡 Myth vs Fact", hint: "Bust a common job-search or hiring myth." },
    { id: "polls", label: "📊 Poll", hint: "An engagement question with answer options (use the platform's poll feature)." },
    { id: "holidays", label: "📅 Malta holidays & events", hint: "Every month: Malta public holidays, recurring events, international days and hiring moments — each with a ready post." },
  ];
  const now = new Date();
  const state = { tab: "employers", idx: {}, salary: 24000, status: "single", sector: "",
    year: now.getFullYear(), month: now.getMonth() + 1, cal: 0 };
  const KIND = { holiday: ["🇲🇹", "Public holiday"], event: ["🎉", "Malta event"], day: ["🌍", "International day"], season: ["📌", "This month"] };
  const monthName = (y, m) => new Date(Date.UTC(y, m - 1, 15)).toLocaleDateString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });
  const niceDate = (d) => new Date(d + "T12:00:00Z").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
  const calItems = () => window.MaltaCalendar.forMonth(state.year, state.month);

  function bankPost(bank, key, tagKey, vars) {
    const i = state.idx[key] ?? 0, it = bank[i];
    return {
      title: fillVars(it.t, vars), subtitle: fillVars(it.s, vars),
      caption: caption([`**${fillVars(it.t, vars)}**`, fillVars(it.b, vars), `${it.cta} ${SITE}${it.url}`, tagsFor(tagKey)]),
      pos: `${i + 1} / ${bank.length}`,
    };
  }

  function generate(js) {
    const vars = { open: js.length, sectors: sectorsOf(js).length };
    switch (state.tab) {
      case "employers": return bankPost(EMPLOYERS, "employers", "employers", vars);
      case "candidates": return bankPost(CANDIDATES, "candidates", "candidates", vars);
      case "study": return bankPost(STUDY, "study", "study", vars);
      case "salary": {
        const g = +state.salary || 0, r = netSalary(g, state.status);
        const statusLabel = { single: "single", married: "married", parent: "parent" }[state.status];
        const matching = js.filter((j) => j.salary).slice(0, 3);
        return {
          title: `${eur(g)} gross = ${eur(r.netMonth)} net/month`,
          subtitle: `Your estimated take-home pay in Malta (2026, ${statusLabel} rates)`,
          caption: caption([
            `💶 **How much is ${eur(g)} a year in Malta — after tax?**`,
            `Gross: **${eur(r.grossMonth)}/month**\nIncome tax: −${eur(r.tax / 12)}/month\nSocial security: −${eur(r.ssc / 12)}/month\n👉 **Net: ${eur(r.netMonth)}/month** (${eur(r.net)} a year)`,
            "Estimate based on Malta's 2026 tax bands and standard Class 1 social security. Your exact payslip may differ.",
            `🧮 Try your own salary: ${SITE}/salary-calculator-malta`,
            matching.length ? `💼 Jobs with a published salary: ${SITE}/jobs` : "",
            tagsFor("salary"),
          ]),
        };
      }
      case "newjobs": {
        const weekAgo = new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10);
        let list = js.filter((j) => String(j.date || "") >= weekAgo).sort((a, b) => String(b.date).localeCompare(String(a.date)));
        const thisWeek = list.length > 0;
        if (!thisWeek) list = [...js].sort((a, b) => String(b.date || "").localeCompare(String(a.date || ""))).slice(0, 6);
        list = list.slice(0, 8);
        return {
          title: thisWeek ? `${list.length} new job${list.length > 1 ? "s" : ""} this week` : "Latest jobs in Malta",
          subtitle: list.slice(0, 3).map((j) => j.title).join(" · ") + (list.length > 3 ? " & more" : ""),
          caption: caption([
            `🆕 **${thisWeek ? "NEW JOBS THIS WEEK" : "LATEST JOBS"} IN MALTA** 🇲🇹`,
            list.map((j) => `▶️ **${j.title}** — ${cityOf(j)}${j.salary ? ` · ${j.salary}` : ""}\n${SITE}/jobs/${j.slug}/`).join("\n\n"),
            `💼 **More Jobs:** ${SITE}/jobs`,
            tagsFor("jobs"),
          ]),
          pick: thisWeek ? `${list.length} published since ${weekAgo}` : "No jobs published in the last 7 days — showing the latest",
        };
      }
      case "sector": {
        const secs = sectorsOf(js);
        if (!state.sector || !secs.some(([c]) => c === state.sector)) state.sector = secs[0]?.[0] || "";
        const inSec = js.filter((j) => j.category === state.sector);
        const word = state.sector.split("&")[0].trim();
        const url = SITE + (HUBS[state.sector] || "/jobs");
        return {
          title: `${inSec.length} open ${word} job${inSec.length > 1 ? "s" : ""} in Malta`,
          subtitle: inSec.slice(0, 3).map((j) => j.title).join(" · ") + (inSec.length > 3 ? " & more" : ""),
          caption: caption([
            `🏭 **${word.toUpperCase()} JOBS IN MALTA**`,
            `**Outreach Recruitment** is hiring for **${inSec.length} ${word.toLowerCase()} role${inSec.length > 1 ? "s" : ""}** right now:`,
            inSec.slice(0, 6).map((j) => `▶️ ${j.title} — ${cityOf(j)}${j.salary ? ` · ${j.salary}` : ""}`).join("\n"),
            `🌐 **See all ${word.toLowerCase()} jobs:** ${url}`,
            tagsFor("jobs", "#" + K().camel(word) + "Jobs"),
          ]),
        };
      }
      case "quotes": {
        const i = state.idx.quotes ?? 0, it = QUOTES[i];
        return {
          title: `“${it.q}”`, subtitle: it.a ? `— ${it.a}` : "— Outreach Recruitment",
          caption: caption([`💬 “${it.q}”${it.a ? `\n— ${it.a}` : ""}`, "Ready for your next step? We're here to help. 🙌",
            `🌐 **Open jobs:** ${SITE}/jobs`, tagsFor("quotes")]),
          pos: `${i + 1} / ${QUOTES.length}`,
        };
      }
      case "myths": {
        const i = state.idx.myths ?? 0, it = MYTHS[i];
        return {
          title: "Myth vs Fact", subtitle: `❌ ${it.m}`,
          caption: caption([`💡 **MYTH vs FACT**`, `❌ **Myth:** ${it.m}\n✅ **Fact:** ${it.f}`, `📖 Learn more: ${SITE}${it.url}`, tagsFor("myths", it.tags)]),
          pos: `${i + 1} / ${MYTHS.length}`,
        };
      }
      case "holidays": {
        const items = calItems();
        if (!items.length) return { title: "", subtitle: "", caption: "", pick: "Nothing this month" };
        const it = items[Math.min(state.cal, items.length - 1)];
        const v = { ...vars, year: state.year };
        const cta = it.url === "/jobs" ? "🌐 Open jobs in Malta:" : it.url === "/employers" ? "📩 Hire with us:" : "📖 Read more:";
        return {
          title: fillVars(it.title, v), subtitle: fillVars(it.subtitle, v),
          caption: caption([`**${fillVars(it.title, v)}**`, fillVars(it.body, v), `${cta} ${SITE}${it.url}`, tagsFor(it.tags)]),
          pick: it.date ? `${KIND[it.kind][1]} · ${niceDate(it.date)}` : `${KIND[it.kind][1]} · ${it.when}`,
          warn: it.kind === "event" ? `Dates change every year (${it.when}). Confirm the date before posting.` : "",
        };
      }
      case "polls": {
        const i = state.idx.polls ?? 0, it = POLLS[i];
        return {
          title: it.q, subtitle: it.o.join("  ·  "),
          caption: caption([`📊 **${it.q}**`, it.o.map((o, n) => `${String.fromCharCode(65 + n)}) ${o}`).join("\n"),
            "Vote in the poll or tell us in the comments 👇", tagsFor("polls")]),
          pos: `${i + 1} / ${POLLS.length}`,
        };
      }
    }
  }
  const BANK_SIZE = { employers: EMPLOYERS.length, candidates: CANDIDATES.length, study: STUDY.length, quotes: QUOTES.length, myths: MYTHS.length, polls: POLLS.length };

  // ── view ──────────────────────────────────────────────────────────────────
  window.renderSocial = async function (view) {
    view.innerHTML = `<div class="card"><p class="muted" style="margin:0">Loading…</p></div>`;
    let js;
    try { js = await loadJobs(); }
    catch (e) { view.innerHTML = `<div class="card"><h2>Could not load the jobs</h2><p class="muted">${esc(e.message)}</p></div>`; return; }
    const tab = TABS.find((t) => t.id === state.tab);
    const post = generate(js);
    const secs = sectorsOf(js);

    const controls = state.tab === "salary"
      ? `<div class="form-grid" style="margin-bottom:12px">
          <label>Gross salary per year (€)<input type="number" id="so-salary" min="1000" step="500" value="${state.salary}"></label>
          <label>Tax status<select id="so-status">${[["single", "Single"], ["married", "Married"], ["parent", "Parent"]]
            .map(([v, l]) => `<option value="${v}" ${v === state.status ? "selected" : ""}>${l}</option>`).join("")}</select></label>
          <div class="form-actions" style="align-self:end">${[18000, 24000, 30000, 40000, 55000].map((v) => `<button class="chip-btn small" data-sal="${v}">${eur(v)}</button>`).join("")}</div>
        </div>`
      : state.tab === "holidays"
      ? (() => {
          const items = calItems();
          return `<div class="form-actions" style="margin-bottom:10px">
              <button class="btn small" id="cal-prev" aria-label="Previous month">‹</button>
              <strong style="min-width:150px;text-align:center">${esc(monthName(state.year, state.month))}</strong>
              <button class="btn small" id="cal-next" aria-label="Next month">›</button>
              <button class="btn small ghost" id="cal-today">This month</button></div>
            <div class="cal-list">${items.length ? items.map((it, i) => `<button class="cal-item ${i === Math.min(state.cal, items.length - 1) ? "active" : ""}" data-cal="${i}">
                <span class="cal-when">${it.date ? esc(niceDate(it.date)) : it.kind === "event" ? "Date varies" : "Any day"}</span>
                <span class="cal-name">${KIND[it.kind][0]} ${esc(it.name)}</span>
                <span class="cal-kind">${KIND[it.kind][1]}</span></button>`).join("")
              : `<div class="empty">No holidays or events this month.</div>`}</div>`;
        })()
      : state.tab === "sector"
      ? `<div class="mk-chips" style="margin-bottom:12px">${secs.map(([c, n]) => `<button class="chip-btn ${c === state.sector ? "active" : ""}" data-sector="${esc(c)}">${esc(c)} (${n})</button>`).join("")}</div>`
      : "";

    view.innerHTML = `
      <section class="card hero">
        <div class="kicker">Marketing · Social Media</div>
        <h1>Social media posts</h1>
        <p>Pick a content type, then copy the title and subtitle for your picture and the caption for the post.</p>
      </section>
      <div class="tabs" role="tablist">${TABS.map((t) => `<button class="tab ${t.id === state.tab ? "active" : ""}" data-tab="${t.id}" role="tab">${t.label}</button>`).join("")}</div>
      <section class="card">
        <div class="section-title"><h2>${tab.label}</h2>
          <div class="form-actions">${post.pos || post.pick ? `<span class="muted small">${esc(post.pos ? "Idea " + post.pos : post.pick)}</span>` : ""}
            ${BANK_SIZE[state.tab] ? `<button class="btn small" id="so-next">🔀 Generate another</button>` : ""}</div></div>
        <p class="muted small">${tab.hint}</p>
        ${post.warn ? `<p class="status warn" style="margin:0 0 10px">⚠ ${esc(post.warn)}</p>` : ""}
        ${controls}
        <div class="so-fields">
          <div class="so-field"><div class="so-label">Title <span class="muted small">(headline on the picture)</span></div>
            <div class="so-title" id="so-title" contenteditable="true">${esc(post.title)}</div>
            <button class="btn small" data-copy="title">Copy title</button></div>
          <div class="so-field"><div class="so-label">Subtitle <span class="muted small">(line under it)</span></div>
            <div class="so-subtitle" id="so-subtitle" contenteditable="true">${esc(post.subtitle)}</div>
            <button class="btn small" data-copy="subtitle">Copy subtitle</button></div>
        </div>
        <div class="so-label" style="margin-top:14px">Caption</div>
        <div class="mk-actions">
          <button class="btn primary" id="so-copy-social">📱 Copy caption for social media</button>
          <button class="btn" id="so-copy-email">📧 Copy for email</button>
          <button class="btn ghost" id="so-copy-all">Copy title + subtitle + caption</button>
        </div>
        <div class="mk-preview" id="so-preview">${K().toHTML(post.caption)}</div>
        <details><summary class="small">Edit caption (use **double stars** for bold)</summary>
          <textarea id="so-caption" rows="14" style="margin-top:8px;font-family:ui-monospace,Menlo,monospace;font-size:.85rem">${esc(post.caption)}</textarea></details>
        <p class="small muted" style="margin:8px 0 0"><span id="so-count">${K().toSocial(post.caption).length}</span> characters · LinkedIn 3,000 · Instagram 2,200 · X 280</p>
      </section>`;

    $$(".tab", view).forEach((b) => (b.onclick = () => { state.tab = b.dataset.tab; window.renderSocial(view); }));
    const next = $("#so-next", view);
    if (next) next.onclick = () => { state.idx[state.tab] = pickIndex(BANK_SIZE[state.tab], state.idx[state.tab] ?? 0); window.renderSocial(view); };
    const go = (dm) => { let m = state.month + dm, y = state.year; if (m < 1) { m = 12; y--; } if (m > 12) { m = 1; y++; } state.month = m; state.year = y; state.cal = 0; window.renderSocial(view); };
    if ($("#cal-prev", view)) {
      $("#cal-prev", view).onclick = () => go(-1); $("#cal-next", view).onclick = () => go(1);
      $("#cal-today", view).onclick = () => { state.year = now.getFullYear(); state.month = now.getMonth() + 1; state.cal = 0; window.renderSocial(view); };
      $$("[data-cal]", view).forEach((b) => (b.onclick = () => { state.cal = +b.dataset.cal; window.renderSocial(view); }));
    }
    $$("[data-sector]", view).forEach((b) => (b.onclick = () => { state.sector = b.dataset.sector; window.renderSocial(view); }));
    $$("[data-sal]", view).forEach((b) => (b.onclick = () => { state.salary = +b.dataset.sal; window.renderSocial(view); }));
    const sal = $("#so-salary", view), st = $("#so-status", view);
    if (sal) sal.onchange = () => { state.salary = Math.max(0, +sal.value || 0); window.renderSocial(view); };
    if (st) st.onchange = () => { state.status = st.value; window.renderSocial(view); };

    const ta = $("#so-caption", view);
    ta.oninput = () => { $("#so-preview", view).innerHTML = K().toHTML(ta.value); $("#so-count", view).textContent = K().toSocial(ta.value).length; };
    const text = (id) => $(id, view).textContent.trim();
    $$("[data-copy]", view).forEach((b) => (b.onclick = (e) => K().copyText(text("#so-" + b.dataset.copy), e.currentTarget)));
    $("#so-copy-social", view).onclick = (e) => K().copyText(K().toSocial(ta.value), e.currentTarget);
    $("#so-copy-email", view).onclick = (e) => K().copyRich(ta.value, e.currentTarget);
    $("#so-copy-all", view).onclick = (e) => K().copyText(`${text("#so-title")}\n${text("#so-subtitle")}\n\n${K().toSocial(ta.value)}`, e.currentTarget);
  };
})();
