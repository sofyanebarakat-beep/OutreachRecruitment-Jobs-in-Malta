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

  // ── your own ideas (Supabase seo_settings "social_ideas" when signed in, else this browser) ──
  const IDEAS_KEY = "social_ideas", LS_IDEAS = "admin:social-ideas";
  let ideas = null;
  async function loadIdeas() {
    if (ideas) return ideas;
    const S = window.AdminStore;
    try {
      if (S?.mode === "supabase" && S.sb) {
        const { data, error } = await S.sb.from("seo_settings").select("value").eq("key", IDEAS_KEY).maybeSingle();
        if (!error) { ideas = data?.value || {}; return ideas; }
      }
    } catch {}
    try { ideas = JSON.parse(localStorage.getItem(LS_IDEAS) || "{}"); } catch { ideas = {}; }
    return ideas;
  }
  async function saveIdeas() {
    const S = window.AdminStore;
    if (S?.mode === "supabase" && S.sb) {
      const { error } = await S.sb.from("seo_settings").upsert({ key: IDEAS_KEY, value: ideas, updated_at: new Date().toISOString() });
      if (!error) return "online";
    }
    try { localStorage.setItem(LS_IDEAS, JSON.stringify(ideas)); } catch {}
    return "this browser";
  }
  const BUILTIN = { employers: EMPLOYERS, candidates: CANDIDATES, study: STUDY, quotes: QUOTES, myths: MYTHS, polls: POLLS };
  const bankFor = (tab) => [...(BUILTIN[tab] || []), ...((ideas || {})[tab] || []).map((x) => ({ ...x, own: true }))];

  // ── FAQ questions from the site (built daily by tools/build_social_faqs.py) ──
  let faqData = null;
  async function loadFaqs() {
    if (faqData) return faqData;
    try { faqData = await (await fetch("faq-posts.json?t=" + Date.now(), { cache: "no-store" })).json(); }
    catch { faqData = { general: [], jobs: [] }; }
    return faqData;
  }

  // ── hashtag sets ──────────────────────────────────────────────────────────
  const HS_KEY = "admin:social-hashsets";
  const hashChoice = () => { try { return JSON.parse(localStorage.getItem(HS_KEY) || "{}"); } catch { return {}; } };
  function hashSets(js) {
    const sets = [["auto", "Default for this tab", ""], ["candidates", "Candidates", TAGS.candidates], ["employers", "Employers", TAGS.employers],
      ["students", "Students", TAGS.study], ["jobs", "Jobs", TAGS.jobs]];
    for (const [c] of sectorsOf(js)) {
      const w = c.split("&")[0].trim();
      sets.push(["sector:" + c, `Sector: ${c}`, `#${K().camel(w)}Jobs #${K().camel(w)}Malta #JobsInMalta #MaltaJobs #Hiring #WorkInMalta`]);
    }
    sets.push(["none", "No hashtags", ""]);
    return sets;
  }
  function applyHashSet(text, key, js) {
    if (!key || key === "auto") return text;
    const set = hashSets(js).find(([k]) => k === key);
    if (!set) return text;
    const blocks = text.split(/\n{2,}/);
    if (blocks.length && blocks[blocks.length - 1].trim().startsWith("#")) blocks.pop();
    if (key !== "none") blocks.push(tagsFor(set[2]));
    return blocks.join("\n\n");
  }

  // ── dates ─────────────────────────────────────────────────────────────────
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const todayISO = ymd(now);
  const dayNumber = Math.floor(new Date(todayISO + "T00:00:00Z").getTime() / 864e5);
  const KIND = { holiday: ["🇲🇹", "Public holiday"], event: ["🎉", "Malta event"], day: ["🌍", "International day"], season: ["📌", "This month"] };
  const monthName = (y, m) => new Date(Date.UTC(y, m - 1, 15)).toLocaleDateString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });
  const niceDate = (d) => new Date(d + "T12:00:00Z").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
  function comingUp(days = 7) {
    const out = [], end = ymd(new Date(now.getTime() + days * 864e5));
    const months = new Set([`${now.getFullYear()}-${now.getMonth() + 1}`, `${new Date(now.getTime() + days * 864e5).getFullYear()}-${new Date(now.getTime() + days * 864e5).getMonth() + 1}`]);
    for (const ym of months) {
      const [y, m] = ym.split("-").map(Number);
      window.MaltaCalendar.forMonth(y, m).forEach((it, i) => { if (it.date && it.date >= todayISO && it.date <= end) out.push({ ...it, y, m, i }); });
    }
    return out.sort((a, b) => a.date.localeCompare(b.date));
  }

  // ── tabs + weekly plan ────────────────────────────────────────────────────
  const TABS = [
    { id: "employers", label: "👔 Employers", hint: "Hiring tips and your services for businesses in Malta." },
    { id: "candidates", label: "🙋 Candidates", hint: "CV, interview and job-search tips — each linking to a blog guide." },
    { id: "study", label: "🎓 Study in Malta", hint: "Student visa, cost of living and why Malta — linking to your study guides." },
    { id: "jobday", label: "⭐ Job of the day", hint: "One open job a day, rotating so every job gets promoted in turn." },
    { id: "newjobs", label: "🆕 New jobs this week", hint: "A round-up of the jobs published in the last 7 days (or the latest ones)." },
    { id: "sector", label: "🏭 Jobs by sector", hint: "Open jobs in one sector, linking to its hub page." },
    { id: "salary", label: "💶 Salary calculator", hint: "“€X gross = €Y net per month” — same maths as /salary-calculator-malta." },
    { id: "faq", label: "❓ FAQ posts", hint: "Quick Q&A posts from the questions on your website (refreshed daily)." },
    { id: "quotes", label: "💬 Quotes", hint: "Motivational quotes for Monday posts and stories." },
    { id: "myths", label: "💡 Myth vs Fact", hint: "Bust a common job-search or hiring myth." },
    { id: "polls", label: "📊 Poll", hint: "An engagement question with answer options (use the platform's poll feature)." },
    { id: "holidays", label: "📅 Malta holidays & events", hint: "Every month: Malta public holidays, recurring events, international days and hiring moments — each with a ready post." },
  ];
  // Sunday = 0 … Saturday = 6
  const PLAN = { 1: "quotes", 2: "newjobs", 3: "candidates", 4: "employers", 5: "polls", 6: "jobday", 0: "study" };
  const DAYNAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const tabLabel = (id) => TABS.find((t) => t.id === id)?.label || id;
  const state = { tab: null, idx: {}, salary: 24000, status: "single", sector: "", year: now.getFullYear(), month: now.getMonth() + 1,
    cal: 0, jobShift: 0, faqMode: "general", faqIdx: 0 };

  // ── generators ────────────────────────────────────────────────────────────
  function bankPost(tab, tagKey, vars) {
    const bank = bankFor(tab);
    const i = Math.min(state.idx[tab] ?? 0, bank.length - 1), it = bank[i];
    const t = fillVars(it.t, vars), sub = fillVars(it.s || "", vars), url = it.url || "/jobs";
    return { title: t, subtitle: sub, own: it.own, ownIndex: it.own ? i - (BUILTIN[tab] || []).length : -1,
      caption: caption([`**${t}**`, fillVars(it.b || "", vars), `${it.cta || "👉 Learn more:"} ${url.startsWith("http") ? url : SITE + url}`, tagsFor(tagKey)]),
      pos: `${i + 1} / ${bank.length}${it.own ? " · your idea" : ""}` };
  }

  async function generate(js) {
    const vars = { open: js.length, sectors: sectorsOf(js).length };
    switch (state.tab) {
      case "employers": return bankPost("employers", "employers", vars);
      case "candidates": return bankPost("candidates", "candidates", vars);
      case "study": return bankPost("study", "study", vars);
      case "jobday": {
        const order = [...js].sort((a, b) => a.slug.localeCompare(b.slug));
        const i = (((dayNumber + state.jobShift) % order.length) + order.length) % order.length, job = order[i];
        const v = await K().jobValues(job);
        return {
          title: `Job of the day: ${job.title}`, subtitle: `📍 ${v.city}, Malta · 💶 ${v.salary}`,
          caption: caption([`⭐ **JOB OF THE DAY: ${job.title}**`, `📍 ${v.city}, Malta · 🕒 ${v.job_type} · 💶 ${v.salary}`, v.intro,
            `🌐 **Apply now:** ${v.apply_url}`, `💼 **More Jobs:** ${v.more_jobs_url}`, v.hashtags]),
          pick: state.jobShift ? `Another job (${i + 1} of ${order.length})`
            : `Today's pick — ${i + 1} of ${order.length}; every open job is featured once every ${order.length} days`,
        };
      }
      case "newjobs": {
        const weekAgo = ymd(new Date(now.getTime() - 7 * 864e5));
        let list = js.filter((j) => String(j.date || "") >= weekAgo).sort((a, b) => String(b.date).localeCompare(String(a.date)));
        const thisWeek = list.length > 0;
        if (!thisWeek) list = [...js].sort((a, b) => String(b.date || "").localeCompare(String(a.date || ""))).slice(0, 6);
        list = list.slice(0, 8);
        return {
          title: thisWeek ? `${list.length} new job${list.length > 1 ? "s" : ""} this week` : "Latest jobs in Malta",
          subtitle: list.slice(0, 3).map((j) => j.title).join(" · ") + (list.length > 3 ? " & more" : ""),
          caption: caption([`🆕 **${thisWeek ? "NEW JOBS THIS WEEK" : "LATEST JOBS"} IN MALTA** 🇲🇹`,
            list.map((j) => `▶️ **${j.title}** — ${cityOf(j)}${j.salary ? ` · ${j.salary}` : ""}\n${SITE}/jobs/${j.slug}/`).join("\n\n"),
            `💼 **More Jobs:** ${SITE}/jobs`, tagsFor("jobs")]),
          pick: thisWeek ? `${list.length} published since ${weekAgo}` : "No jobs published in the last 7 days — showing the latest",
        };
      }
      case "sector": {
        const secs = sectorsOf(js);
        if (!state.sector || !secs.some(([c]) => c === state.sector)) state.sector = secs[0]?.[0] || "";
        const inSec = js.filter((j) => j.category === state.sector), word = state.sector.split("&")[0].trim();
        const url = SITE + (HUBS[state.sector] || "/jobs");
        return {
          title: `${inSec.length} open ${word} job${inSec.length > 1 ? "s" : ""} in Malta`,
          subtitle: inSec.slice(0, 3).map((j) => j.title).join(" · ") + (inSec.length > 3 ? " & more" : ""),
          caption: caption([`🏭 **${word.toUpperCase()} JOBS IN MALTA**`,
            `**Outreach Recruitment** is hiring for **${inSec.length} ${word.toLowerCase()} role${inSec.length > 1 ? "s" : ""}** right now:`,
            inSec.slice(0, 6).map((j) => `▶️ ${j.title} — ${cityOf(j)}${j.salary ? ` · ${j.salary}` : ""}`).join("\n"),
            `🌐 **See all ${word.toLowerCase()} jobs:** ${url}`, tagsFor("jobs", "#" + K().camel(word) + "Jobs")]),
        };
      }
      case "salary": {
        const g = +state.salary || 0, r = netSalary(g, state.status);
        return {
          title: `${eur(g)} gross = ${eur(r.netMonth)} net/month`,
          subtitle: `Your estimated take-home pay in Malta (2026, ${state.status} rates)`,
          caption: caption([`💶 **How much is ${eur(g)} a year in Malta — after tax?**`,
            `Gross: **${eur(r.grossMonth)}/month**\nIncome tax: −${eur(r.tax / 12)}/month\nSocial security: −${eur(r.ssc / 12)}/month\n👉 **Net: ${eur(r.netMonth)}/month** (${eur(r.net)} a year)`,
            "Estimate based on Malta's 2026 tax bands and standard Class 1 social security. Your exact payslip may differ.",
            `🧮 Try your own salary: ${SITE}/salary-calculator-malta`, tagsFor("salary")]),
        };
      }
      case "faq": {
        const d = await loadFaqs(), list = state.faqMode === "job" ? d.jobs : d.general;
        if (!list.length) return { title: "", subtitle: "", caption: "", pick: "No questions found" };
        const i = state.faqIdx % list.length, it = list[i];
        let first = "";  // at least ~50 characters of the answer ("Yes." alone is not a subtitle)
        for (const sn of it.a.match(/[^.!?]+[.!?]+/g) || [it.a]) { first += sn; if (first.trim().length >= 50) break; }
        first = first.trim();
        const isJob = state.faqMode === "job";
        const link = isJob ? `${SITE}/jobs/${it.slug}/` : SITE + it.url;
        return {
          title: it.q, subtitle: first.length > 110 ? first.slice(0, 107).replace(/\s+\S*$/, "") + "…" : first,
          caption: caption([`❓ **${it.q}**`, `✅ ${it.a}`, isJob ? `💼 **${it.title}** — 🌐 **Apply now:** ${link}` : `👉 **Find out more:** ${link}`,
            tagsFor(isJob ? "jobs" : /stud/i.test(it.q) ? "study" : /hire|business|source/i.test(it.q) ? "employers" : "candidates")]),
          pos: `${i + 1} / ${list.length}${isJob ? ` · ${it.title}` : it.pages ? ` · on ${it.pages} pages` : ""}`,
        };
      }
      case "quotes": {
        const bank = bankFor("quotes"), i = Math.min(state.idx.quotes ?? 0, bank.length - 1), it = bank[i];
        return { title: `“${it.q}”`, subtitle: it.a ? `— ${it.a}` : "— Outreach Recruitment", own: it.own, ownIndex: it.own ? i - QUOTES.length : -1,
          caption: caption([`💬 “${it.q}”${it.a ? `\n— ${it.a}` : ""}`, "Ready for your next step? We're here to help. 🙌", `🌐 **Open jobs:** ${SITE}/jobs`, tagsFor("quotes")]),
          pos: `${i + 1} / ${bank.length}${it.own ? " · your idea" : ""}` };
      }
      case "myths": {
        const bank = bankFor("myths"), i = Math.min(state.idx.myths ?? 0, bank.length - 1), it = bank[i];
        return { title: "Myth vs Fact", subtitle: `❌ ${it.m}`, own: it.own, ownIndex: it.own ? i - MYTHS.length : -1,
          caption: caption([`💡 **MYTH vs FACT**`, `❌ **Myth:** ${it.m}\n✅ **Fact:** ${it.f}`, `📖 Learn more: ${SITE}${it.url || "/jobs"}`, tagsFor("myths", it.tags || "")]),
          pos: `${i + 1} / ${bank.length}${it.own ? " · your idea" : ""}` };
      }
      case "polls": {
        const bank = bankFor("polls"), i = Math.min(state.idx.polls ?? 0, bank.length - 1), it = bank[i];
        return { title: it.q, subtitle: it.o.join("  ·  "), own: it.own, ownIndex: it.own ? i - POLLS.length : -1,
          caption: caption([`📊 **${it.q}**`, it.o.map((o, n) => `${String.fromCharCode(65 + n)}) ${o}`).join("\n"), "Vote in the poll or tell us in the comments 👇", tagsFor("polls")]),
          pos: `${i + 1} / ${bank.length}${it.own ? " · your idea" : ""}` };
      }
      case "holidays": {
        const items = window.MaltaCalendar.forMonth(state.year, state.month);
        if (!items.length) return { title: "", subtitle: "", caption: "", pick: "Nothing this month" };
        const it = items[Math.min(state.cal, items.length - 1)], v = { ...vars, year: state.year };
        const cta = it.url === "/jobs" ? "🌐 Open jobs in Malta:" : it.url === "/employers" ? "📩 Hire with us:" : "📖 Read more:";
        return { title: fillVars(it.title, v), subtitle: fillVars(it.subtitle, v),
          caption: caption([`**${fillVars(it.title, v)}**`, fillVars(it.body, v), `${cta} ${SITE}${it.url}`, tagsFor(it.tags)]),
          pick: it.date ? `${KIND[it.kind][1]} · ${niceDate(it.date)}` : `${KIND[it.kind][1]} · ${it.when}`,
          warn: it.kind === "event" ? `Dates change every year (${it.when}). Confirm the date before posting.` : "" };
      }
    }
    return { title: "", subtitle: "", caption: "" };
  }
  const ROTATE = { employers: 1, candidates: 1, study: 1, quotes: 1, myths: 1, polls: 1 };
  const OWN_FIELDS = {
    employers: [["t", "Title"], ["s", "Subtitle"], ["b", "Caption text", "textarea"], ["url", "Link (e.g. /employers)"]],
    candidates: [["t", "Title"], ["s", "Subtitle"], ["b", "Caption text", "textarea"], ["url", "Link (e.g. /jobs)"]],
    study: [["t", "Title"], ["s", "Subtitle"], ["b", "Caption text", "textarea"], ["url", "Link (e.g. /study-in-malta-complete-guide)"]],
    quotes: [["q", "Quote"], ["a", "Author (optional)"]],
    myths: [["m", "Myth"], ["f", "Fact"], ["url", "Link (optional)"]],
    polls: [["q", "Question"], ["o", "Options — one per line", "textarea"]],
  };

  // ── today card ────────────────────────────────────────────────────────────
  function todayCard() {
    const dow = now.getDay();
    const special = window.MaltaCalendar.forMonth(now.getFullYear(), now.getMonth() + 1)
      .map((it, i) => ({ ...it, i })).filter((it) => it.date === todayISO);
    const up = comingUp(7).filter((it) => it.date > todayISO);
    const order = [1, 2, 3, 4, 5, 6, 0];
    return `<section class="card today-card">
      <div class="section-title"><h2>📌 Today's post · ${DAYNAMES[dow]} ${esc(niceDate(todayISO).replace(/^\w+ /, ""))}</h2></div>
      ${special.length
        ? special.map((it) => `<div class="today-main"><span>${KIND[it.kind][0]} <strong>${esc(it.name)}</strong> today — post this first.</span>
            <button class="btn primary small" data-open-cal="${now.getFullYear()}-${now.getMonth() + 1}-${it.i}">Open the post</button></div>`).join("")
          + `<p class="small muted" style="margin:6px 0 0">Planned for ${DAYNAMES[dow]}: ${tabLabel(PLAN[dow])} — <a href="#" data-open-tab="${PLAN[dow]}">open</a> if you also want to post it.</p>`
        : `<div class="today-main"><span>Planned for ${DAYNAMES[dow]}: <strong>${tabLabel(PLAN[dow])}</strong></span>
            <button class="btn primary small" data-open-tab="${PLAN[dow]}">Open today's post</button></div>`}
      <div class="week-strip">${order.map((d) => `<button class="week-day ${d === dow ? "today" : ""}" data-open-tab="${PLAN[d]}">
        <span>${DAYNAMES[d].slice(0, 3)}</span><span>${tabLabel(PLAN[d])}</span></button>`).join("")}</div>
      ${up.length ? `<div class="coming-up"><strong class="small">Coming up (next 7 days)</strong>${up.map((it) => `
        <button class="cal-item" data-open-cal="${it.y}-${it.m}-${it.i}"><span class="cal-when">${esc(niceDate(it.date))}</span>
          <span class="cal-name">${KIND[it.kind][0]} ${esc(it.name)}</span><span class="cal-kind">Prepare →</span></button>`).join("")}</div>`
        : `<p class="small muted" style="margin:8px 0 0">No Malta holidays or international days in the next 7 days.</p>`}
    </section>`;
  }

  // ── view ──────────────────────────────────────────────────────────────────
  window.renderSocial = async function (view) {
    view.innerHTML = `<div class="card"><p class="muted" style="margin:0">Loading…</p></div>`;
    let js;
    try { js = await loadJobs(); await loadIdeas(); }
    catch (e) { view.innerHTML = `<div class="card"><h2>Could not load the jobs</h2><p class="muted">${esc(e.message)}</p></div>`; return; }
    if (!state.tab) state.tab = PLAN[now.getDay()];
    const tab = TABS.find((t) => t.id === state.tab);
    const post = await generate(js);
    const hsKey = hashChoice()[state.tab] || "auto";
    post.caption = applyHashSet(post.caption, hsKey, js);
    const secs = sectorsOf(js);

    let controls = "";
    if (state.tab === "salary") controls = `<div class="form-grid" style="margin-bottom:12px">
        <label>Gross salary per year (€)<input type="number" id="so-salary" min="1000" step="500" value="${state.salary}"></label>
        <label>Tax status<select id="so-status">${[["single", "Single"], ["married", "Married"], ["parent", "Parent"]]
          .map(([v, l]) => `<option value="${v}" ${v === state.status ? "selected" : ""}>${l}</option>`).join("")}</select></label>
        <div class="form-actions" style="align-self:end">${[18000, 24000, 30000, 40000, 55000].map((v) => `<button class="chip-btn small" data-sal="${v}">${eur(v)}</button>`).join("")}</div></div>`;
    else if (state.tab === "sector") controls = `<div class="mk-chips" style="margin-bottom:12px">${secs.map(([c, n]) => `<button class="chip-btn ${c === state.sector ? "active" : ""}" data-sector="${esc(c)}">${esc(c)} (${n})</button>`).join("")}</div>`;
    else if (state.tab === "faq") controls = `<div class="mk-chips" style="margin-bottom:12px">
        <button class="chip-btn ${state.faqMode === "general" ? "active" : ""}" data-faq="general">General questions</button>
        <button class="chip-btn ${state.faqMode === "job" ? "active" : ""}" data-faq="job">Questions about open jobs</button></div>`;
    else if (state.tab === "holidays") {
      const items = window.MaltaCalendar.forMonth(state.year, state.month), up = comingUp(7);
      controls = `${up.length ? `<div class="coming-up" style="margin-bottom:12px"><strong class="small">⏰ Coming up (next 7 days)</strong>${up.map((it) => `
          <button class="cal-item" data-open-cal="${it.y}-${it.m}-${it.i}"><span class="cal-when">${esc(niceDate(it.date))}</span>
          <span class="cal-name">${KIND[it.kind][0]} ${esc(it.name)}</span><span class="cal-kind">Prepare →</span></button>`).join("")}</div>` : ""}
        <div class="form-actions" style="margin-bottom:10px">
          <button class="btn small" id="cal-prev" aria-label="Previous month">‹</button>
          <strong style="min-width:150px;text-align:center">${esc(monthName(state.year, state.month))}</strong>
          <button class="btn small" id="cal-next" aria-label="Next month">›</button>
          <button class="btn small ghost" id="cal-today">This month</button></div>
        <div class="cal-list">${items.length ? items.map((it, i) => `<button class="cal-item ${i === Math.min(state.cal, items.length - 1) ? "active" : ""}" data-cal="${i}">
            <span class="cal-when">${it.date ? esc(niceDate(it.date)) : it.kind === "event" ? "Date varies" : "Any day"}</span>
            <span class="cal-name">${KIND[it.kind][0]} ${esc(it.name)}</span><span class="cal-kind">${KIND[it.kind][1]}</span></button>`).join("")
          : `<div class="empty">No holidays or events this month.</div>`}</div>`;
    }
    const canNext = ROTATE[state.tab] || state.tab === "faq" || state.tab === "jobday";
    const ownForm = OWN_FIELDS[state.tab] ? `<details class="own-idea"><summary class="small">➕ Add your own idea to this tab</summary>
        <form id="own-form" class="form-grid" style="margin-top:10px">${OWN_FIELDS[state.tab].map(([k, l, type]) => type === "textarea"
          ? `<label style="grid-column:1/-1">${l}<textarea name="${k}" rows="4" ${k === "url" ? "" : "required"}></textarea></label>`
          : `<label ${k === "b" || k === "q" || k === "m" || k === "f" ? 'style="grid-column:1/-1"' : ""}>${l}<input name="${k}" ${/url|^a$/.test(k) ? "" : "required"}></label>`).join("")}
          <div class="form-actions" style="grid-column:1/-1"><button class="btn primary" type="submit">Save idea</button>
            <span class="small muted">Saved ${window.AdminStore?.mode === "supabase" ? "online" : "in this browser"}; it appears with the built-in ideas.</span></div></form></details>` : "";

    view.innerHTML = `
      <section class="card hero">
        <div class="kicker">Marketing · Social Media</div>
        <h1>Social media posts</h1>
        <p>Pick a content type, then copy the title and subtitle for your picture and the caption for the post.</p>
      </section>
      ${todayCard()}
      <div class="tabs" role="tablist">${TABS.map((t) => `<button class="tab ${t.id === state.tab ? "active" : ""}" data-tab="${t.id}" role="tab">${t.label}</button>`).join("")}</div>
      <section class="card">
        <div class="section-title"><h2>${tab.label}</h2>
          <div class="form-actions">${post.pos || post.pick ? `<span class="muted small">${esc(post.pos ? "Idea " + post.pos : post.pick)}</span>` : ""}
            ${post.own ? `<button class="btn small ghost" id="own-del">🗑 Delete this idea</button>` : ""}
            ${canNext ? `<button class="btn small" id="so-next">🔀 ${state.tab === "jobday" ? "Another job" : "Generate another"}</button>` : ""}</div></div>
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
        <div class="section-title" style="margin-top:14px"><div class="so-label">Caption</div>
          <label class="hash-pick small">Hashtags <select id="so-hash">${hashSets(js).map(([k, l]) => `<option value="${esc(k)}" ${k === hsKey ? "selected" : ""}>${esc(l)}</option>`).join("")}</select></label></div>
        <div class="mk-actions">
          <button class="btn primary" id="so-copy-social">📱 Copy caption for social media</button>
          <button class="btn" id="so-copy-email">📧 Copy for email</button>
          <button class="btn ghost" id="so-copy-all">Copy title + subtitle + caption</button>
        </div>
        <div class="mk-preview" id="so-preview">${K().toHTML(post.caption)}</div>
        <details><summary class="small">Edit caption (use **double stars** for bold)</summary>
          <textarea id="so-caption" rows="14" style="margin-top:8px;font-family:ui-monospace,Menlo,monospace;font-size:.85rem">${esc(post.caption)}</textarea></details>
        <p class="small muted" style="margin:8px 0 0"><span id="so-count">${K().toSocial(post.caption).length}</span> characters · LinkedIn 3,000 · Instagram 2,200 · X 280</p>
        ${ownForm}
      </section>`;

    const rerender = () => window.renderSocial(view);
    const openTab = (t) => { state.tab = t; rerender(); };
    $$("[data-tab]", view).forEach((b) => (b.onclick = () => openTab(b.dataset.tab)));
    $$("[data-open-tab]", view).forEach((b) => (b.onclick = (e) => { e.preventDefault(); openTab(b.dataset.openTab); }));
    $$("[data-open-cal]", view).forEach((b) => (b.onclick = () => {
      const [y, m, i] = b.dataset.openCal.split("-").map(Number);
      Object.assign(state, { tab: "holidays", year: y, month: m, cal: i }); rerender();
    }));
    const next = $("#so-next", view);
    if (next) next.onclick = () => {
      if (state.tab === "jobday") state.jobShift++;
      else if (state.tab === "faq") state.faqIdx = pickIndex((state.faqMode === "job" ? faqData.jobs : faqData.general).length, state.faqIdx);
      else state.idx[state.tab] = pickIndex(bankFor(state.tab).length, state.idx[state.tab] ?? 0);
      rerender();
    };
    $$("[data-faq]", view).forEach((b) => (b.onclick = () => { state.faqMode = b.dataset.faq; state.faqIdx = 0; rerender(); }));
    $$("[data-sector]", view).forEach((b) => (b.onclick = () => { state.sector = b.dataset.sector; rerender(); }));
    $$("[data-sal]", view).forEach((b) => (b.onclick = () => { state.salary = +b.dataset.sal; rerender(); }));
    const sal = $("#so-salary", view), st = $("#so-status", view);
    if (sal) sal.onchange = () => { state.salary = Math.max(0, +sal.value || 0); rerender(); };
    if (st) st.onchange = () => { state.status = st.value; rerender(); };
    const go = (dm) => { let m = state.month + dm, y = state.year; if (m < 1) { m = 12; y--; } if (m > 12) { m = 1; y++; } Object.assign(state, { month: m, year: y, cal: 0 }); rerender(); };
    if ($("#cal-prev", view)) {
      $("#cal-prev", view).onclick = () => go(-1); $("#cal-next", view).onclick = () => go(1);
      $("#cal-today", view).onclick = () => { Object.assign(state, { year: now.getFullYear(), month: now.getMonth() + 1, cal: 0 }); rerender(); };
      $$("[data-cal]", view).forEach((b) => (b.onclick = () => { state.cal = +b.dataset.cal; rerender(); }));
    }
    $("#so-hash", view).onchange = (e) => {
      const c = hashChoice(); c[state.tab] = e.target.value;
      try { localStorage.setItem(HS_KEY, JSON.stringify(c)); } catch {}
      rerender();
    };
    const of = $("#own-form", view);
    if (of) of.onsubmit = async (e) => {
      e.preventDefault();
      const f = Object.fromEntries(new FormData(of));
      const item = state.tab === "polls" ? { q: f.q.trim(), o: f.o.split("\n").map((x) => x.trim()).filter(Boolean) }
        : Object.fromEntries(Object.entries(f).map(([k, v]) => [k, String(v).trim()]).filter(([, v]) => v));
      if (item.url && !item.url.startsWith("/") && !item.url.startsWith("http")) item.url = "/" + item.url;
      ideas[state.tab] = [...(ideas[state.tab] || []), item];
      const where = await saveIdeas();
      state.idx[state.tab] = bankFor(state.tab).length - 1;
      rerender();
      setTimeout(() => { const b = document.getElementById("banner"); if (b) { b.textContent = `Idea saved ${where}`; b.hidden = false; setTimeout(() => (b.hidden = true), 2500); } }, 50);
    };
    const del = $("#own-del", view);
    if (del) del.onclick = async () => {
      if (!confirm("Delete this idea?")) return;
      ideas[state.tab].splice(post.ownIndex, 1);
      await saveIdeas(); state.idx[state.tab] = 0; rerender();
    };

    const ta = $("#so-caption", view);
    ta.oninput = () => { $("#so-preview", view).innerHTML = K().toHTML(ta.value); $("#so-count", view).textContent = K().toSocial(ta.value).length; };
    const text = (id) => $(id, view).textContent.trim();
    $$("[data-copy]", view).forEach((b) => (b.onclick = (e) => K().copyText(text("#so-" + b.dataset.copy), e.currentTarget)));
    $("#so-copy-social", view).onclick = (e) => K().copyText(K().toSocial(ta.value), e.currentTarget);
    $("#so-copy-email", view).onclick = (e) => K().copyRich(ta.value, e.currentTarget);
    $("#so-copy-all", view).onclick = (e) => K().copyText(`${text("#so-title")}\n${text("#so-subtitle")}\n\n${K().toSocial(ta.value)}`, e.currentTarget);
  };
})();
