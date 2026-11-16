// Weekly "new jobs in Malta" round-up, built from the Job Sync reports
// (/reports/daily-sync/<date>.json, the same data as /admin/#/jobsync) and the
// open-jobs registry (/tools/jobs_registry.json). Every job links to its page.

export const SITE = "https://outreachrecruitment.net";
export const JOBS_CATEGORY = "Jobs in Malta";
export const CATEGORIES = [
  JOBS_CATEGORY,
  "Candidates",
  "Employers",
  "Study in Malta",
];

export type WeeklyJob = {
  slug: string;
  title: string;
  city: string;
  salary: string;
  category: string;
  url: string;
  opened: string; // YYYY-MM-DD the job appeared in Job Sync (or registry date)
  isNew: boolean; // opened during the article week
};

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const iso = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const human = (d: Date) => `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
const addDays = (d: Date, n: number) => {
  const x = new Date(d);
  x.setDate(x.getDate() + n);
  return x;
};

/** Monday (local Malta date) of the week that contains `from`. */
export function mondayOf(from = new Date()) {
  const d = new Date(from.getFullYear(), from.getMonth(), from.getDate());
  return addDays(d, -((d.getDay() + 6) % 7));
}

/** Slug for the week's article — leads with the "jobs in malta" keyword. */
export function weeklySlug(monday: Date) {
  return `jobs-in-malta-this-week-${monday.getDate()}-${MONTHS[monday.getMonth()].toLowerCase()}-${monday.getFullYear()}`;
}

// The public site serves the data; on localhost (vite dev) read it from the live site.
const dataBase = () =>
  /outreachrecruitment\.net$/.test(location.hostname) ? "" : SITE;

async function getJson(path: string) {
  const r = await fetch(`${dataBase()}${path}?t=${Date.now()}`, {
    cache: "no-store",
  });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}

/** Sector landing pages that exist on the site; other sectors use the filtered /jobs/ list. */
const CATEGORY_PAGES: Record<string, string> = {
  Hospitality: "/hospitality-jobs-in-malta",
  "Engineering & Maintenance": "/engineering-jobs-in-malta",
  "Finance & Accounting": "/finance-jobs-in-malta",
  Construction: "/construction-jobs-in-malta",
  "Customer Service": "/customer-service-jobs-in-malta",
  "IT & Technology": "/it-jobs-in-malta",
  "Marine & Shipping": "/marine-jobs-in-malta",
  Sales: "/sales-jobs-in-malta",
  Insurance: "/insurance-jobs-in-malta",
  Retail: "/retail-jobs-in-malta",
  Manufacturing: "/manufacturing-jobs-in-malta",
};
export const categoryUrl = (category: string) =>
  SITE +
  (CATEGORY_PAGES[category] ||
    `/jobs/?category=${encodeURIComponent(category)}`);

/** Job-seeker resources linked from every weekly article (all verified live pages). */
const RESOURCES: [string, string, string][] = [
  ["Malta salary calculator", "/salary-calculator-malta", "estimate your net monthly pay after tax and social security from any gross salary"],
  ["CV writing tips for Malta", "/cv-writing-tips-how-to-get-hired-in-malta/", "what Malta employers look for in a CV"],
  ["Tailor your CV for jobs in Malta", "/tailor-your-cv-for-jobs-in-malta/", "adapt one CV to each vacancy"],
  ["Common interview questions in Malta", "/how-to-answer-common-interview-questions-in-malta/", "prepare strong answers before the interview"],
  ["Documents you need to apply", "/what-documents-do-i-need-to-apply-for-a-job-in-malta/", "the paperwork to have ready"],
  ["Best industries hiring in Malta", "/best-industries-hiring-in-malta-right-now/", "where demand is growing"],
];

const cityOf = (loc: string) =>
  String(loc || "Malta")
    .replace(/,\s*Malta$/i, "")
    .trim() || "Malta";

/**
 * Jobs that opened in the 7 days ending on `monday` (inclusive), still open now.
 * Topped up with the newest open jobs when fewer than `min` are new.
 */
export async function detectWeeklyJobs(monday: Date, min = 5) {
  const start = iso(addDays(monday, -6)),
    end = iso(monday);
  const registry: any[] = await getJson("/tools/jobs_registry.json");
  const open = registry.filter(
    (j) => !["closed", "expired"].includes(j.status),
  );
  const bySlug = new Map(open.map((j) => [j.slug, j]));

  // 1. Job Sync: "created" + "reopened" on each day of the week.
  const seen = new Map<string, string>();
  let syncDays = 0;
  try {
    const index: any[] = await getJson("/reports/daily-sync/index.json");
    const days = index
      .map((d) => d.date)
      .filter((d: string) => d >= start && d <= end);
    const reports = await Promise.all(
      days.map((d: string) =>
        getJson(`/reports/daily-sync/${d}.json`).catch(() => null),
      ),
    );
    for (const r of reports) {
      if (!r) continue;
      syncDays++;
      for (const j of [...(r.created || []), ...(r.reopened || [])])
        if (j.slug && !seen.has(j.slug)) seen.set(j.slug, r.date);
    }
  } catch {
    /* fall back to registry dates below */
  }
  // 2. Registry posting date inside the week (catches days without a report).
  for (const j of open)
    if (j.date >= start && j.date <= end && !seen.has(j.slug))
      seen.set(j.slug, j.date);

  const toJob = (j: any, opened: string, isNew: boolean): WeeklyJob => ({
    slug: j.slug,
    title: j.title,
    city: cityOf(j.location),
    salary: j.salary || "",
    category: j.category || "",
    url: `${SITE}/jobs/${j.slug}/`,
    opened,
    isNew,
  });
  const fresh = [...seen.entries()]
    .filter(([slug]) => bySlug.has(slug)) // drop anything closed since
    .map(([slug, opened]) => toJob(bySlug.get(slug), opened, true))
    .sort(
      (a, b) =>
        Number(!!b.salary) - Number(!!a.salary) ||
        b.opened.localeCompare(a.opened),
    );
  const topUp = open
    .filter((j) => !seen.has(j.slug))
    .sort((a, b) => String(b.date).localeCompare(String(a.date)))
    .slice(0, Math.max(0, min - fresh.length))
    .map((j) => toJob(j, j.date, false));
  const byCategory = new Map<string, number>();
  for (const j of open)
    if (j.category)
      byCategory.set(j.category, (byCategory.get(j.category) || 0) + 1);
  return {
    byCategory,
    start,
    end,
    syncDays,
    totalOpen: open.length,
    newJobs: fresh,
    jobs: [...fresh, ...topUp],
  };
}

/** ≤ 160 characters, always containing "jobs in Malta"; drops examples that don't fit. */
function metaDescription(when: string, examples: string[], total: number) {
  for (let k = Math.min(3, examples.length); k >= 0; k--) {
    const list = k ? `: ${examples.slice(0, k).join(", ")} and more` : "";
    const text = `New jobs in Malta for the week of ${when}${list}. ${total}+ open now — see salaries and apply.`;
    if (text.length <= 160 || k === 0) return text;
  }
  return "";
}

/** Article fields for the week, ready to insert into seo_articles. */
export async function buildWeeklyJobsArticle(monday = mondayOf()) {
  const w = await detectWeeklyJobs(monday);
  const n = w.newJobs.length,
    total = w.totalOpen,
    when = human(monday),
    from = human(addDays(monday, -6));
  const count = n ? `${n} New Opening${n === 1 ? "" : "s"}` : `${total}+ Open Positions`;
  const title = `New Jobs in Malta This Week: ${count} | ${when}`;
  const line = (j: WeeklyJob) =>
    `- **[${j.title}](${j.url})** — ${j.city}${j.salary ? ` · ${j.salary}` : ""}${j.category ? ` · [${j.category} jobs](${categoryUrl(j.category)})` : ""}. [View the job and apply](${j.url})`;
  // This week's sectors first, then the rest by number of open jobs.
  const catList = [...w.byCategory.entries()].sort(
    (a, b) =>
      Number(w.jobs.some((j) => j.category === b[0])) -
        Number(w.jobs.some((j) => j.category === a[0])) || b[1] - a[1],
  );
  const sectors = [...new Set(w.jobs.map((j) => j.category).filter(Boolean))];
  const towns = [...new Set(w.jobs.map((j) => j.city))];
  const examples = w.jobs.slice(0, 3).map((j) => j.title);

  const body = [
    `> **This week:** ${n ? `${n} new job${n === 1 ? "" : "s"} in Malta opened between ${from} and ${when}` : `our team is recruiting for ${total}+ jobs in Malta`}, and ${total}+ positions are open in total across different industries. Each role below links to its full job page with the salary and the apply button. Only candidates currently residing in Malta will be considered.`,
    `A new week means new opportunities, fresh goals and exciting career possibilities. Whether you are ready for your next step up or looking for a change of industry, now is a good time to see which jobs in Malta are hiring.`,
    `## ${n ? "New jobs in Malta this week" : "Featured jobs in Malta this week"}`,
    `${n ? `These roles were added to our [jobs in Malta](${SITE}/jobs/) page during the past seven days` : `Here are some of the roles our team is recruiting for right now`}. Click a job to read the full description and apply directly:`,
    w.newJobs.map(line).join("\n"),
    n && w.jobs.length > n
      ? `### Still hiring\n\n${w.jobs.filter((j) => !j.isNew).map(line).join("\n")}`
      : !n
        ? w.jobs.map(line).join("\n")
        : "",
    `Salaries are shown as published by the employer and are gross amounts. Use our [Malta salary calculator](${SITE}/salary-calculator-malta) to estimate what you would take home each month after tax and social security.`,
    `## Explore all ${total}+ open jobs in Malta`,
    `These ${w.jobs.length} roles are just a start.${sectors.length ? ` This week's openings cover ${sectors.slice(0, 6).join(", ").toLowerCase()}` : ""}${towns.length ? `${sectors.length ? "," : " Openings are"} based in ${towns.slice(0, 6).join(", ")}` : ""}. Browse the [full list of jobs in Malta](${SITE}/jobs/) and filter by sector to find the opportunity that matches your skills and experience. Every weekly round-up is also saved in our [Jobs in Malta news](${SITE}/news-updates/jobs-in-malta/).`,
    `## Browse jobs in Malta by category`,
    `Looking for a specific field? Open a category to see every vacancy in it:`,
    catList
      .map(
        ([c, k]) =>
          `- [${c} jobs in Malta](${categoryUrl(c)}) — ${k} open position${k === 1 ? "" : "s"}`,
      )
      .join("\n"),
    `## Who can apply`,
    `For these vacancies, only candidates currently residing in Malta will be considered. Make sure your CV is up to date before you apply and that you have your documents ready.`,
    `## Useful resources for job seekers in Malta`,
    RESOURCES.map(
      ([t, u, d]) => `- **[${t}](${SITE}${u})** — ${d}.`,
    ).join("\n"),
    `## Sources and further reading`,
    `- [Jobsplus — Malta's public employment service](https://jobsplus.gov.mt/)\n- [Identità — official residence and work-permit information](https://identita.gov.mt/)`,
    `## FAQs`,
    `### How often are new jobs in Malta added?\n\nOur vacancies are updated every day, and every Monday we publish a round-up of the jobs in Malta that opened during the previous week.`,
    `### Who can apply for these jobs in Malta?\n\nOnly candidates currently residing in Malta will be considered for these vacancies. Requirements for each role are listed on its job page.`,
    `### How much will I take home from a salary in Malta?\n\nSalaries on our job pages are gross. Enter the amount in our [Malta salary calculator](${SITE}/salary-calculator-malta) to estimate your net monthly pay after income tax and social security contributions.`,
    `### How do I apply?\n\nOpen the job you are interested in, read the full description and use the apply button on the job page. You can also browse all ${total}+ open positions on our [jobs page](${SITE}/jobs/).`,
    `## Ready for your next career move?`,
    `Discover our latest [job openings in Malta](${SITE}/jobs/) and apply now. New roles are added every week.`,
  ]
    .filter(Boolean)
    .join("\n\n");

  return {
    title,
    slug: weeklySlug(monday),
    category: JOBS_CATEGORY,
    focus_keyword: "jobs in Malta",
    secondary_keywords: [
      "new jobs in Malta this week",
      "job vacancies in Malta",
      "latest jobs in Malta",
    ],
    seo_title: `Jobs in Malta This Week: ${count} (${monday.getDate()} ${MONTHS[monday.getMonth()].slice(0, 3)} ${monday.getFullYear()})`,
    meta_description: metaDescription(when, examples, total),
    excerpt: `${n ? `${n} new jobs in Malta opened this week` : `${total}+ jobs in Malta are open this week`}${examples.length ? `, including ${examples.join(", ")}` : ""}. See salaries and apply online.`,
    body,
    related_jobs: w.jobs,
    internal_links: [
      `${SITE}/jobs/`,
      ...w.jobs.map((j) => j.url),
      ...catList.map(([c]) => categoryUrl(c)),
      ...RESOURCES.map(([, u]) => SITE + u),
    ],
    suggested_image_prompt: `Professional editorial photograph for a "new jobs in Malta this week" article: diverse professionals in a bright Malta office or hotel, Mediterranean light, blue brand accents, no text, 1200 × 630 pixels.`,
    featured_image_alt: `New jobs in Malta this week — ${when}`,
    language: "English",
    indexable: true,
    template_style: "editorial",
    detection: { start: w.start, end: w.end, syncDays: w.syncDays, newJobs: n, totalOpen: total },
  };
}
