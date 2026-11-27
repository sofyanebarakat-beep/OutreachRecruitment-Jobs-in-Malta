import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { createClient, Session } from "@supabase/supabase-js";
import {
  Activity,
  BarChart3,
  BookOpen,
  Bot,
  BriefcaseBusiness,
  CalendarDays,
  Check,
  ChevronRight,
  CircleDollarSign,
  FileText,
  Gauge,
  Globe2,
  KeyRound,
  LayoutDashboard,
  Loader2,
  LogOut,
  Menu,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Tags,
  Trash2,
  Eye,
  EyeOff,
  Copy,
  Wand2,
  PanelRight,
  X,
} from "lucide-react";
import "./styles.css";
import { openArticlePreview, buildPreviewHtml } from "./articlePreview";
import { articleScore, scoreTone, fixFor, duplicateOf, completeArticle, TIP_PLACEHOLDER, cleanBody } from "./articleTools";
import {
  CATEGORIES,
  JOBS_CATEGORY,
  buildWeeklyJobsArticle,
  mondayOf,
  weeklySlug,
} from "./weeklyJobs";

const SUPABASE_URL =
  import.meta.env.VITE_SUPABASE_URL ||
  "https://atcitaqyraeqngcsaeun.supabase.co";
const SUPABASE_KEY =
  import.meta.env.VITE_SUPABASE_ANON_KEY ||
  "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY";
const sb = createClient(SUPABASE_URL, SUPABASE_KEY);

type Row = Record<string, any>;
type Section = {
  id: string;
  label: string;
  icon: React.ElementType;
  table?: string;
  description: string;
};
const sections: Section[] = [
  {
    id: "dashboard",
    label: "SEO Dashboard",
    icon: LayoutDashboard,
    description: "Live publishing, campaign and budget overview",
  },
  {
    id: "services",
    label: "Services SEO",
    icon: BriefcaseBusiness,
    table: "seo_services",
    description: "Manage search-ready service landing pages",
  },
  {
    id: "campaigns",
    label: "Campaigns",
    icon: Gauge,
    table: "seo_campaigns",
    description: "Plan content by service, market and objective",
  },
  {
    id: "keywords",
    label: "Keywords & Topics",
    icon: Tags,
    table: "seo_topics",
    description: "Approve topics and turn demand into article drafts",
  },
  {
    id: "articles",
    label: "Articles",
    icon: FileText,
    table: "seo_articles",
    description: "Create, review, schedule and publish content",
  },
  {
    id: "published",
    label: "Published",
    icon: Globe2,
    table: "seo_articles",
    description: "Live articles: republish, check performance or take offline",
  },
  {
    id: "calendar",
    label: "Content Calendar",
    icon: CalendarDays,
    description: "Scheduled, published and failed content",
  },
  {
    id: "review",
    label: "Weekly Review",
    icon: ShieldCheck,
    description: "Approve only complete, validated articles",
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: BarChart3,
    description: "Search Console and GA4 performance",
  },
  {
    id: "budget",
    label: "API Budget",
    icon: CircleDollarSign,
    table: "seo_api_budgets",
    description: "Control monthly AI spend and hard stops",
  },
  {
    id: "logs",
    label: "Automation Logs",
    icon: Activity,
    table: "seo_automation_logs",
    description: "Generation, publishing and analytics job history",
  },
  {
    id: "social",
    label: "Social Approval Queue",
    icon: Bot,
    table: "seo_social_posts",
    description: "Review platform-ready copy generated for published articles",
  },
  {
    id: "settings",
    label: "Website Settings",
    icon: Settings,
    table: "seo_business_settings",
    description: "Business, SEO and integration configuration",
  },
];
const ARTICLE_AUTHORS = [
  "Outreach Recruitment",
  "Nikolai Calleja",
  "Andrea Zambrano",
  "Katheryn Gonzalez Andrade",
  "Jeraldin Daniela Bohorquez",
  "Julián Longan Granados",
  "Soufiane Barakat",
];
const statusTone: Record<string, string> = {
  active: "green",
  approved: "green",
  published: "green",
  completed: "green",
  draft: "grey",
  planning: "blue",
  generated: "blue",
  review: "amber",
  scheduled: "purple",
  paused: "amber",
  rejected: "red",
  failed: "red",
};
const money = (v: number) =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: "EUR" }).format(
    v || 0,
  );
const date = (v: string) =>
  v
    ? new Intl.DateTimeFormat("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }).format(new Date(v))
    : "—";
const slugify = (v: string) =>
  v
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");

/** Real columns of public.seo_articles. Generators also return helper fields
 * (entities, external_sources, social_posts…) that must never be sent to the table. */
const ARTICLE_COLUMNS = new Set(
  "id,title,slug,excerpt,focus_keyword,secondary_keywords,seo_title,meta_description,canonical_url,og_title,og_description,og_image_url,twitter_card,indexable,service_id,campaign_id,topic_id,language,body,featured_image_url,featured_image_alt,featured_image_width,featured_image_height,section_images,faqs,internal_links,schema_json,status,scheduled_at,published_at,published_url,rejection_reason,quality_score,quality_notes,created_by,approved_by,created_at,updated_at,suggested_image_prompt,social_copy,validation_results,auto_selected,author_name,template_style,category,related_jobs,entities,external_sources,social_posts".split(","),
);
function articleRow(v: Row): Row {
  const out: Row = {};
  for (const [k, x] of Object.entries(v))
    if (ARTICLE_COLUMNS.has(k) && x !== undefined) out[k] = x;
  // AI generator returns social_posts; the table stores them as social_copy.
  if (v.social_posts && !Object.keys(v.social_copy || {}).length)
    out.social_copy = v.social_posts;
  return out;
}

function freeArticleDraft(title: string, keyword: string, targetWords: number) {
  const safeTitle = title.trim() || `A Practical Guide to ${keyword}`;
  const safeKeyword = keyword.trim() || "jobs in Malta";
  const sections = [
    `> ${safeKeyword} requires careful research, a relevant application and confirmation from reliable sources. This guide gives candidates practical steps, trusted Malta resources and realistic next actions without promising employment, admission, visas or a particular outcome.`,
    `## Introduction to ${safeKeyword}\n\nPeople researching **${safeKeyword}** often need clear, practical information before deciding what to do next. This guide explains the main considerations, useful preparation steps and questions to ask. It is designed to help readers make an informed decision without promising a particular employment, study or immigration outcome.`,
    `## Understand Your Goal\n\nStart by defining the type of opportunity you want, the experience you can demonstrate and the location or working arrangement that suits you. A focused search is easier to manage than applying to every available option. Review each opportunity carefully and compare its responsibilities with your real skills, qualifications and availability.`,
    `## Research Opportunities Carefully\n\nUse reputable sources and read the complete description before applying. Check the role, location, working pattern and requested experience. Requirements can differ between employers and may change, so confirm important details with the employer or the appropriate official authority instead of relying on assumptions or outdated social-media posts.`,
    `## Prepare a Focused Application\n\nAdapt your CV and supporting information to the opportunity. Put the most relevant experience near the top, use clear examples and check that your contact details are correct. Avoid copying claims that you cannot support. A concise application that responds to the actual requirements is usually more useful than a long generic document.`,
    `## Use Outreach Recruitment Resources\n\nReview current opportunities on the [Outreach Recruitment jobs page](https://outreachrecruitment.net/jobs/), explore relevant guidance on the [News Updates page](https://outreachrecruitment.net/news-updates), and understand [Outreach Recruitment's services](https://outreachrecruitment.net/service). Only apply for opportunities that match your background, and use the official application instructions shown on the vacancy page.`,
    `## Questions to Ask Before Moving Forward\n\n- What experience and qualifications are essential?\n- Where is the opportunity based?\n- What documents are requested during the application?\n- What are the next stages of the selection process?\n- Which details should be confirmed with an official authority?\n\nKeeping a written checklist makes it easier to compare options and follow up professionally.`,
    `## Avoid Common Mistakes\n\nDo not submit incomplete contact details, make unsupported claims or pay anyone who promises a guaranteed outcome. Take time to proofread your application and keep copies of important communication. If a requirement is unclear, ask for clarification before making a financial or relocation decision.`,
    `## Sources and further reading\n\n- [Jobsplus — Malta's public employment service](https://jobsplus.gov.mt/)\n- [Identità — official Malta residence and immigration information](https://identita.gov.mt/)\n- [Your Europe — working in another EU country](https://europa.eu/youreurope/citizens/work/index_en.htm)`,
    `## FAQs\n\n### Where should I look for current opportunities?\n\nStart with the official Outreach Recruitment vacancies page and other reputable employer sources. Availability changes regularly, so check the publication date and current status.\n\n### Does applying guarantee an interview or offer?\n\nNo. Applications are assessed against the requirements of each opportunity, and no legitimate recruitment service can guarantee selection.\n\n### Should I verify legal or permit information?\n\nYes. Rules depend on personal circumstances and can change. Confirm legal, visa, study or work-permit questions with the relevant official authority.`,
    `## Conclusion\n\nA successful search for **${safeKeyword}** starts with careful research, an honest and relevant application, and realistic expectations. Verify important requirements, then review [current Outreach Recruitment opportunities](https://outreachrecruitment.net/jobs/) when you are ready to take the next step.`,
  ];
  let body = sections.join("\n\n");
  const extras: [string, string][] = [
    ["Keep a simple tracker", "Note each opportunity, its closing date, the documents you sent and the date to follow up. It stops duplicate applications and helps you reply quickly when someone gets in touch."],
    ["Prepare real examples", "Have two or three short examples ready: what the situation was, what you did and the result. Specific examples are far more convincing than general claims."],
    ["Check your online profile", "Make sure your LinkedIn profile matches your CV — the same job titles, dates and skills. Employers in Malta often look at both before they call."],
    ["Get ready for the conversation", "Read the description again before any call or interview and prepare two questions about the work itself, the team and the next steps."],
    ["Protect your personal documents", "Only share ID, passport or bank details through an official, verified process, and only when they are genuinely needed."],
  ];
  let i = 0;
  while (body.split(/\s+/).length < targetWords - 80 && i < extras.length) {
    body = body.replace(/\n## FAQs/, `\n## ${extras[i][0]}\n\n${extras[i][1]}\n\n## FAQs`);
    i++;
  }
  return {
    title: safeTitle,
    slug: slugify(safeTitle),
    excerpt: `A practical, reliable guide to ${safeKeyword}, including research, preparation, applications and useful next steps.`,
    seo_title: `${safeTitle} | Outreach Recruitment`,
    meta_description: `Learn about ${safeKeyword} with practical preparation steps, application guidance and reliable resources from Outreach Recruitment.`,
    body,
    suggested_image_prompt: `Professional editorial photograph for “${safeTitle}”, Malta setting, people-focused, natural blue brand accents, clean composition, no text, 1200 × 630 pixels.`,
    internal_links: [
      "https://outreachrecruitment.net/jobs/",
      "https://outreachrecruitment.net/news-updates",
      "https://outreachrecruitment.net/service",
    ],
    external_sources: [
      "https://jobsplus.gov.mt/",
      "https://identita.gov.mt/",
      "https://europa.eu/youreurope/citizens/work/index_en.htm",
    ],
    status: "generated",
  };
}

/**
 * Create the Monday "new jobs in Malta" draft for a weekly campaign, unless this
 * week's article already exists. The draft waits in Weekly Review for the
 * featured image and a human "Publish now".
 */
async function ensureWeeklyJobsDraft(campaign: Row, monday = mondayOf()) {
  const slug = weeklySlug(monday);
  const { data: existing, error: lookupError } = await sb
    .from("seo_articles")
    .select("id,status")
    .eq("slug", slug)
    .maybeSingle();
  if (lookupError) throw new Error(lookupError.message);
  if (existing) return { created: false, slug, newJobs: 0, totalOpen: 0 };
  const { detection, ...article } = await buildWeeklyJobsArticle(monday);
  const { error } = await sb.from("seo_articles").insert(articleRow(completeArticle({
    ...article,
    category: campaign.category || JOBS_CATEGORY,
    campaign_id: campaign.id,
    service_id: campaign.service_id,
    author_name: campaign.author_name || "Outreach Recruitment",
    status: "review",
    auto_selected: true,
    quality_notes: `Detected from Job Sync ${detection.start} → ${detection.end}: ${detection.newJobs} new opening(s), ${detection.totalOpen} open in total (${detection.syncDays} daily report(s) read). Add the featured image, then Publish now.`,
    created_by: (await sb.auth.getUser()).data.user?.id,
  })));
  if (error) throw new Error(error.message);
  await sb.from("seo_automation_logs").insert({
    job_name: "Weekly Jobs in Malta draft",
    status: "success",
    message: `/${slug}/ · ${detection.newJobs} new jobs · ${detection.totalOpen} open`,
    ended_at: new Date().toISOString(),
  });
  return {
    created: true,
    slug,
    newJobs: detection.newJobs,
    totalOpen: detection.totalOpen,
  };
}

/** Runs once per admin visit: Monday–Wednesday, create any missing weekly drafts. */
let weeklyCheckDone = false;
async function autoWeeklyJobsDrafts() {
  if (weeklyCheckDone) return [];
  weeklyCheckDone = true;
  const day = new Date().getDay(); // 1 = Monday
  if (day < 1 || day > 3) return [];
  const { data } = await sb
    .from("seo_campaigns")
    .select("*")
    .eq("campaign_type", "weekly_new_jobs")
    .eq("status", "active")
    .eq("auto_generate", true);
  const out = [];
  for (const c of data || []) {
    if (c.start_date && c.start_date > new Date().toISOString().slice(0, 10))
      continue;
    try {
      const r = await ensureWeeklyJobsDraft(c);
      if (r.created) out.push(r);
    } catch (e) {
      console.warn("Weekly jobs draft failed", e);
    }
  }
  return out;
}

function App() {
  const [session, setSession] = useState<Session | null>(null),
    [checking, setChecking] = useState(true);
  useEffect(() => {
    sb.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setChecking(false);
    });
    return sb.auth.onAuthStateChange((_e, s) => setSession(s)).data.subscription
      .unsubscribe;
  }, []);
  if (checking) return <FullLoader />;
  return session ? <Admin session={session} /> : <Login />;
}

function Login() {
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [busy, setBusy] = useState(false),
    [msg, setMsg] = useState("");
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg("");
    const { error } = await sb.auth.signInWithPassword({ email, password });
    setBusy(false);
    if (error) setMsg(error.message);
  }
  return (
    <main className="login">
      <section className="login-card">
        <div className="logo">
          <span>OR</span>
          <div>
            Outreach Recruitment<small>SEO Control Centre</small>
          </div>
        </div>
        <div className="login-copy">
          <p className="eyebrow">Protected admin</p>
          <h1>Grow qualified traffic with content you control.</h1>
          <p>
            Manage campaigns, articles, service pages and live search
            performance in one secure workspace.
          </p>
        </div>
        <form onSubmit={submit}>
          <label>
            Email address
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </label>
          {msg && <p className="error">{msg}</p>}
          <button className="primary full" disabled={busy}>
            {busy ? <Loader2 className="spin" /> : <KeyRound />} Sign in
            securely
          </button>
        </form>
        <p className="fine">
          Access is restricted to approved Outreach Recruitment administrators.
        </p>
      </section>
    </main>
  );
}

function Admin({ session }: { session: Session }) {
  const initial = location.hash.replace("#/", "") || "dashboard";
  const [route, setRoute] = useState(
      sections.some((s) => s.id === initial) ? initial : "dashboard",
    ),
    [open, setOpen] = useState(false),
    [notice, setNotice] = useState("");
  useEffect(() => {
    autoWeeklyJobsDrafts().then((made) => {
      if (made.length)
        setNotice(
          made
            .map(
              (r) =>
                `New Jobs in Malta draft ready: /${r.slug}/ (${r.newJobs} new jobs this week). Open Weekly Review, add the featured image and publish.`,
            )
            .join(" "),
        );
    });
  }, []);
  useEffect(() => {
    const fn = () => setRoute(location.hash.replace("#/", "") || "dashboard");
    addEventListener("hashchange", fn);
    return () => removeEventListener("hashchange", fn);
  }, []);
  const current = sections.find((s) => s.id === route)!;
  return (
    <div className="shell">
      <aside className={open ? "sidebar open" : "sidebar"}>
        <div className="brand-row">
          <div className="logo inverse">
            <span>OR</span>
            <div>
              Outreach<small>SEO Control Centre</small>
            </div>
          </div>
          <button className="icon mobile" onClick={() => setOpen(false)}>
            <X />
          </button>
        </div>
        <nav>
          {sections.map(({ id, label, icon: Icon }) => (
            <a
              key={id}
              href={`#/${id}`}
              className={route === id ? "active" : ""}
              onClick={() => setOpen(false)}
            >
              <Icon />
              {label}
              <ChevronRight />
            </a>
          ))}
        </nav>
        <div className="side-foot">
          <div className="avatar">
            {session.user.email?.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <strong>Administrator</strong>
            <small>{session.user.email}</small>
          </div>
          <button
            className="icon inverse-button"
            title="Sign out"
            onClick={() => sb.auth.signOut()}
          >
            <LogOut />
          </button>
        </div>
      </aside>
      <div className="workspace">
        <header>
          <button className="icon mobile" onClick={() => setOpen(true)}>
            <Menu />
          </button>
          <div>
            <p className="eyebrow">Outreach Recruitment</p>
            <h1>{current.label}</h1>
            <p>{current.description}</p>
          </div>
          <a className="site-link" href="/" target="_blank">
            <Globe2 /> View website
          </a>
        </header>
        <main>
          {notice && (
            <p className="notice" role="status">
              <Sparkles /> {notice}{" "}
              <a href="#/review" onClick={() => setNotice("")}>
                Open Weekly Review
              </a>
            </p>
          )}
          <Route section={current} />
        </main>
      </div>
    </div>
  );
}

function Route({ section }: { section: Section }) {
  if (section.id === "dashboard") return <Dashboard />;
  if (section.id === "analytics") return <Analytics />;
  if (section.id === "calendar") return <Calendar />;
  if (section.id === "review") return <Articles review />;
  if (section.id === "articles") return <Articles />;
  if (section.id === "published") return <Articles live />;
  if (section.id === "services") return <Services />;
  if (section.id === "campaigns") return <Campaigns />;
  if (section.id === "keywords") return <Topics />;
  if (section.id === "budget") return <Budget />;
  if (section.id === "social") return <SocialQueue />;
  if (section.id === "settings") return <Autopilot />;
  return <DataList section={section} />;
}

function useRows(table: string) {
  const [rows, setRows] = useState<Row[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState("");
  const load = async () => {
    setLoading(true);
    const { data, error } = await sb
      .from(table)
      .select("*")
      .order("updated_at", { ascending: false })
      .limit(500);
    setRows(data || []);
    setError(error?.message || "");
    setLoading(false);
  };
  useEffect(() => {
    load();
  }, [table]);
  return { rows, loading, error, load, setRows };
}

function Dashboard() {
  const [data, setData] = useState<Record<string, Row[]>>({}),
    [loading, setLoading] = useState(true);
  async function load() {
    setLoading(true);
    const names = [
      "seo_campaigns",
      "seo_articles",
      "seo_services",
      "seo_api_budgets",
      "seo_automation_logs",
    ];
    const out = await Promise.all(
      names.map((n) => sb.from(n).select("*").limit(500)),
    );
    setData(Object.fromEntries(names.map((n, i) => [n, out[i].data || []])));
    setLoading(false);
  }
  useEffect(() => {
    load();
  }, []);
  const articles = data.seo_articles || [],
    count = (s: string) => articles.filter((a) => a.status === s).length,
    budget = (data.seo_api_budgets || [])[0] || {},
    spend = Number(budget.current_spend || 0),
    limit = Number(budget.monthly_limit || 0),
    reserved = Number(budget.reserved_spend || 0);
  const cards = [
    [
      "Active campaigns",
      (data.seo_campaigns || []).filter((x) => x.status === "active").length,
      "campaigns",
    ],
    ["Total articles", articles.length, "articles"],
    ["Draft articles", count("draft"), "articles"],
    ["Awaiting review", count("review"), "review"],
    ["Approved", count("approved"), "review"],
    ["Scheduled", count("scheduled"), "calendar"],
    ["Published", count("published"), "published"],
    [
      "Failed jobs",
      (data.seo_automation_logs || []).filter((x) => x.status === "failed")
        .length,
      "logs",
    ],
    ["Total services", (data.seo_services || []).length, "services"],
    ["Monthly AI spend", money(spend), "budget"],
  ];
  return (
    <>
      {loading && <LoadingBar />}
      <div className="toolbar">
        <div>
          <h2>Good {new Date().getHours() < 12 ? "morning" : "afternoon"}</h2>
          <p>Your live SEO publishing operation at a glance.</p>
        </div>
        <button onClick={load}>
          <RefreshCw /> Refresh dashboard
        </button>
      </div>
      <div className="metric-grid">
        {cards.map(([label, value, href]) => (
          <a href={`#/${href}`} className="metric" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <small>
              View details <ChevronRight />
            </small>
          </a>
        ))}
      </div>
      <div className="split">
        <section className="panel">
          <PanelHead
            icon={Activity}
            title="Recent automation"
            sub="Latest generation, publishing and data sync activity"
          />
          <LogTable rows={(data.seo_automation_logs || []).slice(0, 6)} />
        </section>
        <section className="panel">
          <PanelHead
            icon={CircleDollarSign}
            title="API budget"
            sub="This month's controlled AI usage"
          />
          <div className="budget-body">
            <div className="budget-total">
              <span>Remaining budget</span>
              <strong>{money(Math.max(0, limit - spend - reserved))}</strong>
              <small>of {money(limit)} monthly limit</small>
            </div>
            <div className="progress">
              <i
                style={{
                  width: `${limit ? Math.min(100, ((spend + reserved) / limit) * 100) : 0}%`,
                }}
              />
            </div>
            <dl>
              <div>
                <dt>Current spend</dt>
                <dd>{money(spend)}</dd>
              </div>
              <div>
                <dt>Reserved</dt>
                <dd>{money(reserved)}</dd>
              </div>
              <div>
                <dt>Warning at</dt>
                <dd>{budget.warning_threshold || 80}%</dd>
              </div>
            </dl>
            {budget.hard_stop && (
              <div className="notice">
                <ShieldCheck /> Hard stop is enabled
              </div>
            )}
            <a className="button-link" href="#/budget">
              Manage budget
            </a>
          </div>
        </section>
      </div>
    </>
  );
}

function Services() {
  const state = useRows("seo_services");
  const [edit, setEdit] = useState<Row | null>(null),
    [syncing, setSyncing] = useState(false);
  async function sync() {
    setSyncing(true);
    try {
      const catalog = await fetch("/assets/seo-service-catalog.json", {
        cache: "no-store",
      }).then((r) => {
        if (!r.ok) throw new Error("Service catalogue is unavailable");
        return r.json();
      });
      const rows = (catalog.services || []).map((r: Row) => ({
        ...r,
        updated_at: new Date().toISOString(),
      }));
      const { error } = await sb
        .from("seo_services")
        .upsert(rows, { onConflict: "slug" });
      if (error) throw error;
      alert(`${rows.length} website service pages synchronized.`);
      state.load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Service synchronization failed");
    } finally {
      setSyncing(false);
    }
  }
  return (
    <>
      <div className="toolbar">
        <div>
          <h2>Service pages</h2>
          <p>
            Import titles, descriptions and keywords directly from the live
            website catalogue.
          </p>
        </div>
        <div className="toolbar-actions">
          <button onClick={sync} disabled={syncing}>
            {syncing ? <Loader2 className="spin" /> : <RefreshCw />} Sync from
            website
          </button>
          <button
            className="primary"
            onClick={() =>
              setEdit({ status: "active", priority: 50, indexable: true })
            }
          >
            + Add service
          </button>
        </div>
      </div>
      {state.loading ? (
        <TableLoader />
      ) : (
        <Cards
          rows={state.rows}
          empty="No service pages yet."
          render={(r) => (
            <>
              <div>
                <span className={`badge ${statusTone[r.status]}`}>
                  {r.status}
                </span>
                <h3>{r.name}</h3>
                <p>/{r.slug}</p>
              </div>
              <div className="card-meta">
                <span>
                  Main keyword<strong>{r.main_keyword || "—"}</strong>
                </span>
                <span>
                  Location<strong>{r.target_location || "Malta"}</strong>
                </span>
                <span>
                  Priority<strong>{r.priority || 50}/100</strong>
                </span>
              </div>
              <button onClick={() => setEdit(r)}>Edit service</button>
            </>
          )}
        />
      )}{" "}
      {edit && (
        <ServiceModal
          row={edit}
          close={() => setEdit(null)}
          saved={() => {
            setEdit(null);
            state.load();
          }}
        />
      )}
    </>
  );
}

function ServiceModal({
  row,
  close,
  saved,
}: {
  row: Row;
  close: () => void;
  saved: () => void;
}) {
  const [v, setV] = useState(row),
    [busy, setBusy] = useState(false),
    [msg, setMsg] = useState("");
  const set = (k: string, x: any) => setV({ ...v, [k]: x });
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const payload = {
      ...v,
      slug: v.slug || slugify(v.name),
      updated_at: new Date().toISOString(),
    };
    const { error } = await sb.from("seo_services").upsert(payload);
    setBusy(false);
    error ? setMsg(error.message) : saved();
  }
  return (
    <Modal title={row.id ? "Edit service" : "Create service"} close={close}>
      <form className="form-grid" onSubmit={save}>
        <Field
          label="Service name"
          required
          value={v.name}
          onChange={(x) => {
            set("name", x);
            if (!row.id) set("slug", slugify(x));
          }}
        />
        <Field
          label="URL slug"
          required
          value={v.slug}
          onChange={(x) => set("slug", slugify(x))}
        />
        <Field
          label="Main keyword"
          required
          value={v.main_keyword}
          onChange={(x) => set("main_keyword", x)}
        />
        <Field
          label="Target location"
          value={v.target_location}
          onChange={(x) => set("target_location", x)}
        />
        <Field
          label="SEO title"
          className="wide"
          value={v.seo_title}
          onChange={(x) => set("seo_title", x)}
        />
        <Area
          label="Meta description"
          className="wide"
          value={v.meta_description}
          onChange={(x) => set("meta_description", x)}
        />
        <Area
          label="Short description"
          className="wide"
          value={v.short_description}
          onChange={(x) => set("short_description", x)}
        />
        <Area
          label="Full page content"
          className="wide"
          rows={8}
          value={v.content}
          onChange={(x) => set("content", x)}
        />
        <Field
          label="Secondary keywords (comma separated)"
          className="wide"
          value={
            (v.secondary_keywords || []).join?.(", ") || v.secondary_keywords
          }
          onChange={(x) =>
            set(
              "secondary_keywords",
              x
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean),
            )
          }
        />
        <Field
          label="Image URL"
          value={v.featured_image_url}
          onChange={(x) => set("featured_image_url", x)}
        />
        <Field
          label="Image alt text"
          value={v.image_alt}
          onChange={(x) => set("image_alt", x)}
        />
        <Field
          label="SEO priority (1–100)"
          type="number"
          value={v.priority}
          onChange={(x) => set("priority", Number(x))}
        />
        <Select
          label="Status"
          value={v.status}
          options={["active", "inactive"]}
          onChange={(x) => set("status", x)}
        />
        <label className="check wide">
          <input
            type="checkbox"
            checked={v.indexable ?? true}
            onChange={(e) => set("indexable", e.target.checked)}
          />{" "}
          Allow search engines to index this page
        </label>
        <div className="serp wide">
          <small>outreachrecruitment.net › {v.slug || "service"}</small>
          <h3>{v.seo_title || v.name || "SEO title preview"}</h3>
          <p>
            {v.meta_description ||
              v.short_description ||
              "Your meta description will appear here."}
          </p>
        </div>
        {msg && <p className="error wide">{msg}</p>}
        <FormActions busy={busy} close={close} />
      </form>
    </Modal>
  );
}

const WEEKLY_JOBS_PRESET: Row = {
  name: "Jobs in Malta — New openings every Monday",
  category: JOBS_CATEGORY,
  campaign_type: "weekly_new_jobs",
  status: "active",
  language: "English",
  target_location: "Malta",
  objective:
    'Rank for "jobs in Malta" and "new jobs in Malta this week": every Monday publish a round-up of the jobs that opened in the past 7 days (detected from Job Sync), each linked to its job page.',
  articles_per_month: 5,
  publish_days: ["Monday"],
  publish_time: "09:00",
  auto_generate: true,
  target_words: 800,
  author_name: "Outreach Recruitment",
};

function Campaigns() {
  const state = useRows("seo_campaigns");
  const services = useRows("seo_services");
  const [edit, setEdit] = useState<Row | null>(null),
    [running, setRunning] = useState<string | null>(null),
    [filter, setFilter] = useState("All categories");
  const hasWeekly = state.rows.some(
    (r) => r.campaign_type === "weekly_new_jobs",
  );
  const rows =
    filter === "All categories"
      ? state.rows
      : state.rows.filter((r) => (r.category || "Candidates") === filter);
  function weeklyPreset() {
    const service = services.rows.find((s) =>
      /jobs in malta/i.test(`${s.name} ${s.main_keyword}`),
    );
    setEdit({
      ...WEEKLY_JOBS_PRESET,
      service_id: service?.id,
      start_date: new Date().toISOString().slice(0, 10),
    });
  }
  async function runWeekly(r: Row) {
    setRunning(r.id);
    try {
      const res = await ensureWeeklyJobsDraft(r);
      alert(
        res.created
          ? `Draft created: /${res.slug}/\n${res.newJobs} new jobs this week · ${res.totalOpen} open in total.\n\nOpen Articles (or Weekly Review), add the featured image and publish.`
          : `This week's article (/${res.slug}/) already exists — open it in Articles.`,
      );
    } catch (e: any) {
      alert(`Could not create the weekly article: ${e.message}`);
    }
    setRunning(null);
  }
  return (
    <>
      <ListHeader
        title="SEO campaigns"
        action="Create automated campaign"
        onAction={() =>
          setEdit({
            category: "Candidates",
            campaign_type: "standard",
            status: "active",
            language: "English",
            target_location: "Malta and Europe",
            articles_per_month: 8,
            publish_days: ["Tuesday", "Friday"],
            publish_time: "09:00",
            auto_generate: true,
            target_words: 1200,
            author_name: "Outreach Recruitment",
            start_date: new Date().toISOString().slice(0, 10),
          })
        }
      >
        <label className="inline-filter">
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            {["All categories", ...CATEGORIES].map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>
        {!hasWeekly && (
          <button onClick={weeklyPreset}>
            <BriefcaseBusiness /> Jobs in Malta weekly campaign
          </button>
        )}
      </ListHeader>
      {state.loading ? (
        <TableLoader />
      ) : (
        <Cards
          rows={rows}
          empty="No campaigns yet."
          render={(r) => (
            <>
              <div>
                <span className={`badge ${statusTone[r.status]}`}>
                  {r.status}
                </span>{" "}
                <span className="badge purple">
                  {r.category || "Candidates"}
                </span>
                {r.campaign_type === "weekly_new_jobs" && (
                  <span className="badge green">Weekly new jobs</span>
                )}
                <h3>{r.name}</h3>
                <p>{r.objective}</p>
              </div>
              <div className="card-meta">
                <span>
                  Monthly<strong>{r.articles_per_month} articles</strong>
                </span>
                <span>
                  Schedule
                  <strong>
                    {(r.publish_days || []).join(", ")} ·{" "}
                    {String(r.publish_time || "09:00").slice(0, 5)}
                  </strong>
                </span>
                <span>
                  Autopilot<strong>{r.auto_generate ? "On" : "Off"}</strong>
                </span>
              </div>
              <button onClick={() => setEdit(r)}>Edit automation</button>
              {r.campaign_type === "weekly_new_jobs" && (
                <button
                  className="ai"
                  disabled={running === r.id}
                  onClick={() => runWeekly(r)}
                >
                  {running === r.id ? <Loader2 className="spin" /> : <Sparkles />}{" "}
                  Create this week's article now
                </button>
              )}
            </>
          )}
        />
      )}{" "}
      {edit && (
        <CampaignModal
          row={edit}
          close={() => setEdit(null)}
          saved={() => {
            setEdit(null);
            state.load();
          }}
        />
      )}
    </>
  );
}

function CampaignModal({
  row,
  close,
  saved,
}: {
  row: Row;
  close: () => void;
  saved: () => void;
}) {
  const [v, setV] = useState(row),
    [busy, setBusy] = useState(false),
    [msg, setMsg] = useState("");
  const services = useRows("seo_services"),
    days = [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
      "Sunday",
    ];
  const set = (k: string, x: any) =>
    setV((current: Row) => ({ ...current, [k]: x }));
  function toggleDay(day: string) {
    const current = v.publish_days || [];
    set(
      "publish_days",
      current.includes(day)
        ? current.filter((x: string) => x !== day)
        : [...current, day],
    );
  }
  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!(v.publish_days || []).length) {
      setMsg("Choose at least one publishing weekday.");
      return;
    }
    setBusy(true);
    const schedule = `${v.publish_days.join(", ")} at ${v.publish_time} Malta time`;
    const { data, error } = await sb
      .from("seo_campaigns")
      .upsert({
        ...v,
        publishing_schedule: schedule,
        updated_at: new Date().toISOString(),
      })
      .select()
      .single();
    if (error) {
      setMsg(error.message);
      setBusy(false);
      return;
    }
    if (
      data.campaign_type === "weekly_new_jobs" &&
      data.auto_generate &&
      data.status === "active"
    ) {
      try {
        await ensureWeeklyJobsDraft(data);
      } catch (e: any) {
        setMsg(
          `Campaign saved. This week's draft could not be created yet: ${e.message}`,
        );
        setBusy(false);
        return;
      }
    } else if (data.auto_generate && data.status === "active") {
      const service = services.rows.find((s) => s.id === data.service_id),
        base = service?.main_keyword || data.name;
      const ideas = [
        `how to ${base}`,
        `${base} guide`,
        `${base} requirements`,
        `${base} mistakes to avoid`,
        `${base} checklist`,
        `${base} for beginners`,
        `${base} questions answered`,
        `${base} practical tips`,
        `choosing ${base}`,
        `${base} in Malta`,
        `what to know about ${base}`,
        `${base} step by step`,
      ].slice(0, Math.min(30, data.articles_per_month));
      const { error: topicError } = await sb.from("seo_topics").upsert(
        ideas.map((keyword: string, i: number) => ({
          keyword,
          category: data.category,
          target_location: data.target_location,
          intent: i < 2 ? "commercial" : "informational",
          priority: 90 - i * 3,
          status: "idea",
          suggested_title: keyword.replace(/\b\w/g, (c: string) =>
            c.toUpperCase(),
          ),
          campaign_id: data.id,
          service_id: data.service_id,
          notes: "Automatically created from campaign settings",
        })),
        { onConflict: "keyword,target_location", ignoreDuplicates: true },
      );
      if (topicError) {
        setMsg(
          `Campaign saved, but topics could not be created: ${topicError.message}`,
        );
        setBusy(false);
        return;
      }
      const { error: generationError } = await sb.functions.invoke(
        "generate-seo-content",
        {
          body: {
            action: "campaign_drafts",
            campaign_id: data.id,
            count: Math.min(5, data.articles_per_month),
          },
        },
      );
      if (generationError) {
        setMsg(
          `Campaign and topics saved. Draft generation will retry automatically: ${generationError.message}`,
        );
        setBusy(false);
        return;
      }
    }
    setBusy(false);
    saved();
  }
  return (
    <Modal
      title={row.id ? "Edit automated campaign" : "Create automated campaign"}
      close={close}
    >
      <form className="form-grid" onSubmit={save}>
        <Field
          label="Campaign name"
          required
          className="wide"
          value={v.name}
          onChange={(x) => set("name", x)}
        />
        <Select
          label="Category (where articles are saved)"
          value={v.category || "Candidates"}
          options={CATEGORIES}
          onChange={(x) => set("category", x)}
        />
        <label>
          Campaign type
          <select
            value={v.campaign_type || "standard"}
            onChange={(e) => {
              const weekly = e.target.value === "weekly_new_jobs";
              setV((c: Row) => ({
                ...c,
                campaign_type: e.target.value,
                ...(weekly
                  ? {
                      category: JOBS_CATEGORY,
                      publish_days: ["Monday"],
                      articles_per_month: 5,
                      target_words: 800,
                    }
                  : {}),
              }));
            }}
          >
            <option value="standard">Keyword articles</option>
            <option value="weekly_new_jobs">
              Weekly new jobs round-up (from Job Sync)
            </option>
          </select>
        </label>
        {v.campaign_type === "weekly_new_jobs" && (
          <p className="hint wide">
            Every Monday a draft is built from the jobs that opened in the
            past 7 days on <a href="/admin/#/jobsync">Job Sync</a>. Each job is
            linked to its page on /jobs/, the slug starts with
            “jobs-in-malta-this-week-…”, and the article is filed under{" "}
            <strong>Jobs in Malta</strong> on /news-updates/jobs-in-malta/. You
            only add the featured image and click Publish now.
          </p>
        )}
        <label>
          Related service
          <select
            required
            value={v.service_id || ""}
            onChange={(e) => set("service_id", e.target.value)}
          >
            <option value="">Select a service</option>
            {services.rows.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
        <Field
          label="Target location"
          value={v.target_location}
          onChange={(x) => set("target_location", x)}
        />
        <Area
          label="Campaign objective"
          className="wide"
          value={v.objective}
          onChange={(x) => set("objective", x)}
        />
        <Field
          label="Start date"
          type="date"
          value={v.start_date}
          onChange={(x) => set("start_date", x)}
        />
        <Field
          label="Articles per month"
          type="number"
          value={v.articles_per_month}
          onChange={(x) => set("articles_per_month", Math.max(1, Number(x)))}
        />
        <div className="wide">
          <span className="field-label">Publishing weekdays</span>
          <div className="day-picker">
            {days.map((day) => (
              <button
                type="button"
                className={
                  (v.publish_days || []).includes(day) ? "selected" : ""
                }
                onClick={() => toggleDay(day)}
                key={day}
              >
                {day.slice(0, 3)}
              </button>
            ))}
          </div>
        </div>
        <Field
          label="Publishing time (Malta)"
          type="time"
          value={String(v.publish_time || "09:00").slice(0, 5)}
          onChange={(x) => set("publish_time", x)}
        />
        <Select
          label="Target words"
          value={String(v.target_words || 1200)}
          options={["800", "1200", "1600", "2000"]}
          onChange={(x) => set("target_words", Number(x))}
        />
        <Select
          label="Written by"
          value={v.author_name || "Outreach Recruitment"}
          options={ARTICLE_AUTHORS}
          onChange={(x) => set("author_name", x)}
        />
        <Select
          label="Status"
          value={v.status}
          options={["planning", "active", "paused", "completed"]}
          onChange={(x) => set("status", x)}
        />
        <label className="check wide">
          <input
            type="checkbox"
            checked={v.auto_generate ?? true}
            onChange={(e) => set("auto_generate", e.target.checked)}
          />{" "}
          {v.campaign_type === "weekly_new_jobs"
            ? "Automatically create the Monday draft from new Job Sync openings"
            : "Automatically create related keywords and article drafts"}
        </label>
        <Area
          label="Notes"
          className="wide"
          value={v.notes}
          onChange={(x) => set("notes", x)}
        />
        {msg && <p className="error wide">{msg}</p>}
        <FormActions busy={busy} close={close} />
      </form>
    </Modal>
  );
}
function Topics() {
  const state = useRows("seo_topics"),
    [filter, setFilter] = useState("All categories"),
    [edit, setEdit] = useState<Row | null>(null),
    [syncing, setSyncing] = useState(false),
    [generating, setGenerating] = useState<string | null>(null);
  async function syncGsc() {
    setSyncing(true);
    const { data, error } = await sb
      .from("seo_keywords")
      .select("keyword,intent,current_position,volume")
      .order("volume", { ascending: false })
      .limit(100);
    if (error) {
      alert(error.message);
      setSyncing(false);
      return;
    }
    const rows = (data || []).map((r) => ({
      keyword: r.keyword,
      intent: [
        "informational",
        "commercial",
        "transactional",
        "local",
      ].includes(r.intent)
        ? r.intent
        : "informational",
      target_location: "Malta",
      priority: Math.max(
        1,
        Math.min(100, Math.round(100 - Number(r.current_position || 50))),
      ),
      status: "idea",
      suggested_title: r.keyword.replace(/\b\w/g, (x: string) =>
        x.toUpperCase(),
      ),
      notes: `Automatically imported from Google Search Console · ${r.volume || 0} impressions · position ${r.current_position || "—"}`,
    }));
    const { error: saveError } = await sb.from("seo_topics").upsert(rows, {
      onConflict: "keyword,target_location",
      ignoreDuplicates: true,
    });
    setSyncing(false);
    if (saveError) alert(saveError.message);
    else {
      alert(
        `${rows.length} Search Console keywords checked for new content opportunities.`,
      );
      state.load();
    }
  }
  async function generate(r: Row) {
    if (r.status !== "approved") {
      alert("Approve this topic before generating an article draft.");
      return;
    }
    setGenerating(r.id);
    const data = freeArticleDraft(
      r.suggested_title || `A Practical Guide to ${r.keyword}`,
      r.keyword,
      1200,
    );
    const { error: insertError } = await sb.from("seo_articles").insert(
      articleRow(completeArticle({
        ...data,
        focus_keyword: r.keyword,
        topic_id: r.id,
        service_id: r.service_id,
        campaign_id: r.campaign_id,
        category: r.category,
        status: "generated",
        language: "English",
        created_by: (await sb.auth.getUser()).data.user?.id,
      })),
    );
    if (insertError) alert(insertError.message);
    else {
      await sb
        .from("seo_topics")
        .update({ status: "drafted", updated_at: new Date().toISOString() })
        .eq("id", r.id);
      alert(
        "Article draft generated. It must be reviewed and approved before publishing.",
      );
      state.load();
    }
    setGenerating(null);
  }
  return (
    <>
      <div className="toolbar">
        <div>
          <h2>Keywords and content topics</h2>
          <p>
            Turn real Search Console demand into approved, human-reviewed
            article drafts.
          </p>
        </div>
        <div className="toolbar-actions">
          <label className="inline-filter">
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              {["All categories", ...CATEGORIES].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </label>
          <button onClick={syncGsc} disabled={syncing}>
            {syncing ? <Loader2 className="spin" /> : <Search />} Find ideas
            from Google
          </button>
          <button
            className="primary"
            onClick={() =>
              setEdit({
                status: "idea",
                intent: "informational",
                priority: 50,
                category:
                  filter === "All categories" ? JOBS_CATEGORY : filter,
              })
            }
          >
            + Add topic
          </button>
        </div>
      </div>
      {state.loading ? (
        <TableLoader />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Keyword</th>
                <th>Category</th>
                <th>Intent</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Suggested article</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {state.rows
                .filter(
                  (r) => filter === "All categories" || r.category === filter,
                )
                .map((r) => (
                <tr key={r.id}>
                  <td>
                    <strong>{r.keyword}</strong>
                    <small>{r.target_location || "Malta"}</small>
                  </td>
                  <td>{r.category || "—"}</td>
                  <td>{r.intent}</td>
                  <td>{r.priority}/100</td>
                  <td>
                    <span className={`badge ${statusTone[r.status]}`}>
                      {r.status}
                    </span>
                  </td>
                  <td>{r.suggested_title || "—"}</td>
                  <td className="actions">
                    <button onClick={() => setEdit(r)}>Edit</button>
                    <button
                      className="ai"
                      onClick={() => generate(r)}
                      disabled={generating === r.id || r.status !== "approved"}
                    >
                      {generating === r.id ? (
                        <Loader2 className="spin" />
                      ) : (
                        <Sparkles />
                      )}{" "}
                      Generate draft
                    </button>
                  </td>
                </tr>
              ))}
              {!state.rows.length && (
                <tr>
                  <td colSpan={7}>
                    <Empty text="No content topics yet." />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      {edit && (
        <GenericModal
          table="seo_topics"
          row={edit}
          fields={[
            "keyword",
            "category",
            "suggested_title",
            "target_location",
            "priority",
            "notes",
          ]}
          statuses={["idea", "approved", "drafted", "rejected"]}
          extra="intent"
          close={() => setEdit(null)}
          saved={() => {
            setEdit(null);
            state.load();
          }}
        />
      )}
    </>
  );
}

async function deleteArticle(v: Row): Promise<boolean> {
  const live = v.status === "published";
  const ok = confirm(
    `Delete “${v.title || "this article"}”?\n\n` +
      (live
        ? `This removes it from the dashboard only. The page is already published, so it stays live at /${v.slug}/. To remove the page from the website, use “Take offline” first.`
        : "The article and its images in this dashboard will be removed. This cannot be undone."),
  );
  if (!ok) return false;
  const { error } = await sb.from("seo_articles").delete().eq("id", v.id);
  if (error) {
    alert(`Could not delete the article: ${error.message}`);
    return false;
  }
  return true;
}

function previewArticle(v: Row) {
  // Open the tab synchronously (popup blockers), then fill it.
  const win = window.open("", "_blank");
  if (!win) {
    alert("Your browser blocked the preview window. Allow pop-ups for this site and try again.");
    return;
  }
  win.document.write("<p style='font:15px Arial;padding:24px'>Preparing the preview…</p>");
  openArticlePreview(win, v, validateArticle(v));
}

/** Status shown in the list, including the website-only states. */
function articleState(r: Row): { label: string; tone: string } {
  if (r.status === "rejected" && r.published_url) return { label: "going offline", tone: "amber" };
  if (r.status === "rejected" && String(r.quality_notes || "").startsWith("Taken offline")) return { label: "offline", tone: "red" };
  return { label: r.status, tone: statusTone[r.status] };
}

function OfflineDialog({ article, others, close, done }: { article: Row; others: Row[]; close: () => void; done: () => void }) {
  const [target, setTarget] = useState(others[0]?.published_url || "https://outreachrecruitment.net/news-updates");
  const [busy, setBusy] = useState(false);
  async function go() {
    setBusy(true);
    const { error } = await sb
      .from("seo_articles")
      .update({ status: "rejected", canonical_url: target, updated_at: new Date().toISOString() })
      .eq("id", article.id);
    setBusy(false);
    if (error) alert(`Could not take the article offline: ${error.message}`);
    else {
      alert("Done. Within 15 minutes the page is removed from the website and its address redirects to the page you chose.");
      done();
    }
  }
  return (
    <Modal title="Take article offline" close={close}>
      <div className="form-grid">
        <p className="wide">
          <strong>{article.title}</strong> will be removed from the website, the blog page, the sitemap and News &amp; Updates.
          Anyone who opens <code>/{article.slug}/</code> is sent to the page below, so no link breaks.
        </p>
        <label className="wide">
          Redirect visitors to
          <select value={target} onChange={(e) => setTarget(e.target.value)}>
            {others.map((o) => (
              <option key={o.id} value={o.published_url}>
                {o.title}
              </option>
            ))}
            <option value="https://outreachrecruitment.net/news-updates">News &amp; Updates page</option>
            <option value="https://outreachrecruitment.net/jobs/">Jobs in Malta page</option>
          </select>
        </label>
        <div className="form-actions wide">
          <button type="button" onClick={close}>Cancel</button>
          <button type="button" className="danger" onClick={go} disabled={busy}>
            {busy ? <Loader2 className="spin" /> : <Globe2 />} Take offline
          </button>
        </div>
      </div>
    </Modal>
  );
}

function Articles({ review = false, live = false }: { review?: boolean; live?: boolean }) {
  const state = useRows("seo_articles"),
    [edit, setEdit] = useState<Row | null>(null),
    [offline, setOffline] = useState<Row | null>(null),
    [filter, setFilter] = useState("All categories"),
    [weekly, setWeekly] = useState(false),
    [selected, setSelected] = useState<Set<string>>(new Set()),
    [bulkWhen, setBulkWhen] = useState(""),
    [busy, setBusy] = useState(false);
  const rows = (
    review
      ? state.rows.filter((r) => r.status === "review")
      : live
        ? state.rows.filter((r) => r.status === "published")
        : state.rows.filter((r) => r.status !== "published")
  ).filter((r) => filter === "All categories" || r.category === filter);
  const chosen = rows.filter((r) => selected.has(r.id));
  const toggle = (id: string) =>
    setSelected((cur) => {
      const n = new Set(cur);
      n.has(id) ? n.delete(id) : n.add(id);
      return n;
    });
  async function weeklyArticle() {
    setWeekly(true);
    const { data: camp } = await sb
      .from("seo_campaigns")
      .select("*")
      .eq("campaign_type", "weekly_new_jobs")
      .order("created_at")
      .limit(1)
      .maybeSingle();
    if (!camp) {
      alert(
        "Create the Jobs in Malta weekly campaign first (Campaigns → Jobs in Malta weekly campaign).",
      );
      setWeekly(false);
      return;
    }
    try {
      const res = await ensureWeeklyJobsDraft(camp);
      if (!res.created)
        alert(`This week's article (/${res.slug}/) already exists.`);
      await state.load();
    } catch (e: any) {
      alert(`Could not create the weekly article: ${e.message}`);
    }
    setWeekly(false);
  }
  async function status(r: Row, s: string) {
    if (s === "approved" && validateArticle(r).length) {
      alert("Cannot publish yet. Open the article and fix:\n• " + validateArticle(r).join("\n• "));
      return;
    }
    const { error } = await sb
      .from("seo_articles")
      .update({ status: s, updated_at: new Date().toISOString() })
      .eq("id", r.id);
    if (error) alert(`Could not update the article: ${error.message}`);
    else if (s === "approved")
      alert(
        r.status === "published"
          ? "Republishing. Within 15 minutes the live page is updated and shows today as “Updated”."
          : "Approved. The website publisher runs every 15 minutes — the article will be live shortly.",
      );
    state.load();
  }
  async function duplicate(r: Row) {
    const { error } = await sb.from("seo_articles").insert(articleRow(duplicateOf(r)));
    if (error) alert(`Could not duplicate the article: ${error.message}`);
    state.load();
  }
  async function bulk(kind: "publish" | "schedule" | "category" | "delete", value?: string) {
    if (!chosen.length) return;
    const ids = chosen.map((r) => r.id);
    let error: any = null,
      note = "";
    setBusy(true);
    if (kind === "publish") {
      const ready = chosen.filter((r) => !validateArticle(r).length);
      const skipped = chosen.length - ready.length;
      if (ready.length)
        ({ error } = await sb.from("seo_articles").update({ status: "approved", updated_at: new Date().toISOString() }).in("id", ready.map((r) => r.id)));
      note = `${ready.length} article(s) will be published within 15 minutes.` + (skipped ? ` ${skipped} skipped — they still have items to fix.` : "");
    } else if (kind === "schedule") {
      if (!value) { setBusy(false); return alert("Choose a date and time first."); }
      ({ error } = await sb.from("seo_articles").update({ status: "scheduled", scheduled_at: new Date(value).toISOString(), updated_at: new Date().toISOString() }).in("id", ids));
      note = `${ids.length} article(s) scheduled for ${new Date(value).toLocaleString()}.`;
    } else if (kind === "category") {
      ({ error } = await sb.from("seo_articles").update({ category: value || null, updated_at: new Date().toISOString() }).in("id", ids));
      note = `Category changed for ${ids.length} article(s).`;
    } else {
      const live = chosen.filter((r) => r.status === "published").length;
      if (!confirm(`Delete ${ids.length} article(s) from the dashboard?` + (live ? `\n\n${live} of them are published and stay live on the website — use “Take offline” to remove a page.` : "") + "\n\nThis cannot be undone.")) {
        setBusy(false);
        return;
      }
      ({ error } = await sb.from("seo_articles").delete().in("id", ids));
      note = `${ids.length} article(s) deleted.`;
    }
    setBusy(false);
    if (error) alert(`Could not update the articles: ${error.message}`);
    else alert(note);
    setSelected(new Set());
    state.load();
  }
  const published = state.rows.filter((r) => r.status === "published" && r.published_url);
  return (
    <>
      <ListHeader
        title={review ? "Articles awaiting review" : live ? `Published articles (${rows.length})` : "Article library"}
        action={review || live ? undefined : "Create article"}
        onAction={() =>
          setEdit({
            category: filter === "All categories" ? undefined : filter,
            status: "draft",
            language: "English",
            indexable: true,
            author_name: "Outreach Recruitment",
            template_style: "editorial",
          })
        }
      >
        <label className="inline-filter">
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            {["All categories", ...CATEGORIES].map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>
        {!live && (
          <button className="ai" onClick={weeklyArticle} disabled={weekly}>
            {weekly ? <Loader2 className="spin" /> : <BriefcaseBusiness />} This
            week's Jobs in Malta article
          </button>
        )}
      </ListHeader>
      {chosen.length > 0 && (
        <div className="bulk-bar">
          <strong>{chosen.length} selected</strong>
          <button className="primary" disabled={busy} onClick={() => bulk("publish")}>
            {live ? <><RefreshCw /> Republish</> : <><Globe2 /> Publish</>}
          </button>
          <span className="bulk-group">
            <input type="datetime-local" value={bulkWhen} onChange={(e) => setBulkWhen(e.target.value)} aria-label="Schedule date and time" />
            <button disabled={busy} onClick={() => bulk("schedule", bulkWhen)}>
              <CalendarDays /> Schedule
            </button>
          </span>
          <select defaultValue="" disabled={busy} onChange={(e) => { if (e.target.value) bulk("category", e.target.value === "—" ? "" : e.target.value); e.target.value = ""; }} aria-label="Change category">
            <option value="" disabled>Change category…</option>
            {[...CATEGORIES, "—"].map((c) => (
              <option key={c} value={c}>{c === "—" ? "No category" : c}</option>
            ))}
          </select>
          <button className="danger" disabled={busy} onClick={() => bulk("delete")}>
            <Trash2 /> Delete
          </button>
          <button className="link" onClick={() => setSelected(new Set())}>Clear selection</button>
        </div>
      )}
      {live && <CheckupPanel rows={state.rows} onEdit={setEdit} />}
      {state.loading ? (
        <TableLoader />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th className="check-col">
                  <input
                    type="checkbox"
                    aria-label="Select all articles"
                    checked={rows.length > 0 && chosen.length === rows.length}
                    onChange={(e) => setSelected(e.target.checked ? new Set(rows.map((r) => r.id)) : new Set())}
                  />
                </th>
                <th>Article</th>
                <th>Service / keyword</th>
                <th>SEO / GEO score</th>
                <th>Status</th>
                <th>{live ? "Published" : "Schedule"}</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => {
                const sc = articleScore(r);
                const st = articleState(r);
                return (
                  <tr key={r.id} className={selected.has(r.id) ? "selected" : ""}>
                    <td className="check-col">
                      <input type="checkbox" aria-label={`Select ${r.title || "article"}`} checked={selected.has(r.id)} onChange={() => toggle(r.id)} />
                    </td>
                    <td>
                      <strong>{r.title || "Untitled"}</strong>
                      <small>/{r.slug || "no-slug"}</small>
                    </td>
                    <td>
                      {r.focus_keyword || "—"}
                      <small>
                        {r.category || "No category"}
                        {(r.related_jobs || []).length
                          ? ` · ${r.related_jobs.length} linked jobs`
                          : ""}
                      </small>
                    </td>
                    <td className="score-cell">
                      <b className={`score-pill ${scoreTone(sc.score)}`}>{sc.score}</b>
                      {sc.missing.length > 0 && (
                        <details className="score-missing">
                          <summary>{sc.missing.length} to improve</summary>
                          <ul>{sc.missing.map((m) => <li key={m}>{m}</li>)}</ul>
                        </details>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${st.tone}`}>{st.label}</span>
                    </td>
                    <td>{live ? date(r.published_at || r.updated_at) : date(r.scheduled_at)}</td>
                    <td className="actions">
                      <button onClick={() => setEdit(r)}>Edit</button>
                      <button onClick={() => previewArticle(r)}>
                        <Eye /> Preview
                      </button>
                      <button onClick={() => duplicate(r)} title="Make a copy as a new draft">
                        <Copy /> Duplicate
                      </button>
                      {review ? (
                        <>
                          <button onClick={() => status(r, "approved")}>
                            <Check /> Publish now
                          </button>
                          <button className="danger" onClick={() => status(r, "rejected")}>
                            Reject
                          </button>
                        </>
                      ) : (
                        <>
                          {["generated", "draft", "review"].includes(r.status) && (
                            <button className="primary" onClick={() => status(r, "approved")}>
                              <Globe2 /> Publish now
                            </button>
                          )}
                          {r.status === "published" && (
                            <>
                              <button className="primary" onClick={() => status(r, "approved")} title="Update the live page with the latest saved changes">
                                <RefreshCw /> Republish
                              </button>
                              <button onClick={() => setOffline(r)} title="Remove the page from the website and redirect its address">
                                <EyeOff /> Take offline
                              </button>
                            </>
                          )}
                          {r.status === "scheduled" && (
                            <span className="badge purple">
                              Auto-publishes {date(r.scheduled_at)}
                            </span>
                          )}
                        </>
                      )}
                      <button
                        className="danger icon-action"
                        title="Delete article"
                        aria-label={`Delete article: ${r.title || "Untitled"}`}
                        onClick={async () => {
                          if (await deleteArticle(r)) state.load();
                        }}
                      >
                        <Trash2 />
                      </button>
                    </td>
                  </tr>
                );
              })}
              {!rows.length && (
                <tr>
                  <td colSpan={7}>
                    <Empty
                      text={
                        review
                          ? "Nothing is waiting for review."
                          : live
                            ? "No published articles yet."
                            : "No unpublished articles. Published ones are in the Published tab."
                      }
                    />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      {edit && (
        <ArticleModal
          row={edit}
          close={() => setEdit(null)}
          saved={() => {
            setEdit(null);
            state.load();
          }}
        />
      )}
      {offline && (
        <OfflineDialog
          article={offline}
          others={published.filter((o) => o.id !== offline.id)}
          close={() => setOffline(null)}
          done={() => {
            setOffline(null);
            state.load();
          }}
        />
      )}
    </>
  );
}

function ArticleModal({
  row,
  close,
  saved,
}: {
  row: Row;
  close: () => void;
  saved: () => void;
}) {
  const [v, setV] = useState<Row>(() => (row.body ? { ...row, body: cleanBody(row.body) } : row)),
    [busy, setBusy] = useState(false),
    [msg, setMsg] = useState(""),
    [generating, setGenerating] = useState(false),
    [targetWords, setTargetWords] = useState(1200),
    [live, setLive] = useState(window.innerWidth >= 1200),
    [previewHtml, setPreviewHtml] = useState("");
  const services = useRows("seo_services");
  const frame = React.useRef<HTMLIFrameElement>(null);
  // Live preview: rebuild the website-template preview shortly after typing stops.
  useEffect(() => {
    if (!live) return;
    const t = setTimeout(async () => {
      const html = await buildPreviewHtml(v, validateArticle(v), false);
      const y = frame.current?.contentWindow?.scrollY || 0;
      setPreviewHtml(html.replace("</body>", `<script>addEventListener("load",()=>scrollTo(0,${Math.round(y)}))</script></body>`));
    }, 700);
    return () => clearTimeout(t);
  }, [v, live]);
  const set = (k: string, x: any) =>
    setV((current: Row) => ({ ...current, [k]: x }));
  async function save(e: React.FormEvent, republish = false) {
    e.preventDefault();
    if (republish && validateArticle(v).length) {
      setMsg("Fix the items in the publishing checklist before republishing.");
      return;
    }
    setBusy(true);
    const payload = {
      ...v,
      slug: v.slug || slugify(v.title),
      status: republish
        ? "approved"
        : v.scheduled_at && v.status !== "published"
          ? "scheduled"
          : v.status,
      updated_at: new Date().toISOString(),
    };
    const { error } = await sb
      .from("seo_articles")
      .upsert(articleRow(payload));
    setBusy(false);
    if (error) return setMsg(error.message);
    if (republish) alert("Saved. Within 15 minutes the live page is updated and shows today as “Updated”.");
    saved();
  }
  function fix(w: string) {
    const changes = fixFor(w, v, services.rows);
    if (changes) setV((cur: Row) => ({ ...cur, ...changes }));
  }
  // The human review can't be automated: take the user to the review panel and highlight it.
  function openReview() {
    const el = document.getElementById("article-review");
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.classList.remove("flash");
    void el.offsetWidth;
    el.classList.add("flash");
    (el.querySelector("input[type=checkbox]:not(:checked)") as HTMLInputElement | null)?.focus({ preventScroll: true });
  }
  function fixAll() {
    let cur = v;
    for (const w of validateArticle(cur)) {
      const changes = fixFor(w, cur, services.rows);
      if (changes) cur = { ...cur, ...changes };
    }
    setV(cur);
  }
  async function remove() {
    setBusy(true);
    const done = await deleteArticle({ ...v, id: row.id });
    setBusy(false);
    if (done) saved();
  }
  async function generate() {
    setGenerating(true);
    setMsg("");
    if (!v.title?.trim() || !v.focus_keyword?.trim()) {
      setMsg("Add an article title and focus keyword first.");
      setGenerating(false);
      return;
    }
    const data = freeArticleDraft(v.title, v.focus_keyword, targetWords);
    setV((current: Row) => completeArticle({ ...current, ...data }, services.rows));
    setGenerating(false);
  }
  async function generateConnected() {
    if (!v.title?.trim() || !v.focus_keyword?.trim()) {
      setMsg("Add an article title and focus keyword first.");
      return;
    }
    setGenerating(true);
    setMsg("");
    const { data, error } = await sb.functions.invoke("generate-seo-content", {
      body: {
        action: "article",
        title: v.title,
        keyword: v.focus_keyword,
        tone: "professional",
        language: v.language || "English",
        target_words: targetWords,
      },
    });
    setGenerating(false);
    if (error)
      setMsg(
        `Connected AI unavailable: ${error.message}. You can still use Generate free article.`,
      );
    else
      setV((current: Row) =>
        completeArticle({ ...current, ...data, status: "generated" }, services.rows),
      );
  }
  const warnings = validateArticle(v);
  const articleHeadings = Array.from(
    String(v.body || "").matchAll(/^##\s+(.+)$/gm),
    (match) => match[1].trim(),
  );
  return (
    <Modal
      title={row.id ? "Edit article" : "Create article"}
      close={close}
      large
      wide={live}
    >
      <div className={live ? "editor-split" : ""}>
      <form className="form-grid" onSubmit={save}>
        <Field
          label="Article title"
          required
          className="wide"
          value={v.title}
          onChange={(x) => {
            set("title", x);
            if (!row.id) set("slug", slugify(x));
          }}
        />
        <Field
          label="Slug"
          required
          value={v.slug}
          onChange={(x) => set("slug", slugify(x))}
        />
        <Field
          label="Focus keyword"
          required
          value={v.focus_keyword}
          onChange={(x) => set("focus_keyword", x)}
        />
        <label>
          Related service
          <select
            required
            value={v.service_id || ""}
            onChange={(e) => set("service_id", e.target.value || null)}
          >
            <option value="">Select a service</option>
            {services.rows.map((service) => (
              <option key={service.id} value={service.id}>
                {service.name}
              </option>
            ))}
          </select>
        </label>
        <Select
          label="Written by"
          value={v.author_name || "Outreach Recruitment"}
          options={ARTICLE_AUTHORS}
          onChange={(x) => set("author_name", x)}
        />
        <Select
          label="Category (where it is saved on the website)"
          value={v.category || "—"}
          options={["—", ...CATEGORIES]}
          onChange={(x) => set("category", x === "—" ? null : x)}
        />
        {(v.related_jobs || []).length > 0 && (
          <div className="wide hint">
            <strong>
              Linked open jobs ({v.related_jobs.length}) — detected from Job
              Sync
            </strong>
            <ul className="linked-jobs">
              {v.related_jobs.map((j: Row) => (
                <li key={j.slug}>
                  <a href={j.url} target="_blank" rel="noopener">
                    {j.title}
                  </a>{" "}
                  — {j.city}
                  {j.salary ? ` · ${j.salary}` : ""}
                  {j.isNew ? " · new this week" : " · still hiring"}
                </li>
              ))}
            </ul>
          </div>
        )}
        <Field
          label="SEO title"
          className="wide"
          value={v.seo_title}
          onChange={(x) => set("seo_title", x)}
        />
        <Area
          label="Meta description"
          className="wide"
          value={v.meta_description}
          onChange={(x) => set("meta_description", x)}
        />
        <Area
          label="Excerpt"
          className="wide"
          value={v.excerpt}
          onChange={(x) => set("excerpt", x)}
        />
        <Area
          label="Article body (Markdown)"
          className="wide editor"
          rows={16}
          value={v.body}
          onChange={(x) => set("body", x)}
        />
        {articleHeadings.length > 0 && (
          <div className="wide section-images">
            <h3>Images inside article sections</h3>
            <p>Upload an optional image beneath any H2 section.</p>
            {articleHeadings.map((heading) => {
              const current = (v.section_images || []).find(
                (image: Row) => image.heading === heading,
              );
              const update = (changes: Row) => {
                const others = (v.section_images || []).filter(
                  (image: Row) => image.heading !== heading,
                );
                set("section_images", [
                  ...others,
                  { heading, ...(current || {}), ...changes },
                ]);
              };
              return (
                <div className="section-image-row" key={heading}>
                  <strong>{heading}</strong>
                  <ImageUploader
                    label={`Image below “${heading}”`}
                    value={current?.url}
                    alt={current?.alt}
                    onUploaded={(url, width, height) =>
                      update({ url, width, height })
                    }
                  />
                  <Field
                    label="Alt text"
                    value={current?.alt}
                    onChange={(alt) => update({ alt })}
                  />
                  <Field
                    label="Optional caption"
                    value={current?.caption}
                    onChange={(caption) => update({ caption })}
                  />
                  {current?.url && (
                    <button
                      type="button"
                      className="danger"
                      onClick={() =>
                        set(
                          "section_images",
                          (v.section_images || []).filter(
                            (image: Row) => image.heading !== heading,
                          ),
                        )
                      }
                    >
                      Remove section image
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
        {v.suggested_image_prompt && (
          <Area
            label="Suggested image brief"
            className="wide"
            value={v.suggested_image_prompt}
            onChange={(x) => set("suggested_image_prompt", x)}
          />
        )}
        <ImageUploader
          value={v.featured_image_url}
          alt={v.featured_image_alt}
          onUploaded={(url, width, height) =>
            setV({
              ...v,
              featured_image_url: url,
              featured_image_width: width,
              featured_image_height: height,
            })
          }
        />
        <Field
          label="Featured image alt text"
          value={v.featured_image_alt}
          onChange={(x) => set("featured_image_alt", x)}
        />
        <Select
          label="Language"
          value={v.language}
          options={["English", "French", "Italian"]}
          onChange={(x) => set("language", x)}
        />
        <Select
          label="Status"
          value={v.status}
          options={[
            "draft",
            "generated",
            "review",
            "approved",
            "scheduled",
            "published",
            "rejected",
            "failed",
          ]}
          onChange={(x) => set("status", x)}
        />
        <Field
          label="Scheduled publication"
          type="datetime-local"
          value={v.scheduled_at?.slice?.(0, 16)}
          onChange={(x) => set("scheduled_at", x || null)}
        />
        <Field
          label="Canonical URL"
          value={v.canonical_url}
          onChange={(x) => set("canonical_url", x)}
        />
        <label>
          Target article length
          <select
            value={targetWords}
            onChange={(e) => setTargetWords(Number(e.target.value))}
          >
            <option value="800">About 800 words</option>
            <option value="1200">About 1,200 words</option>
            <option value="1600">About 1,600 words</option>
            <option value="2000">About 2,000 words</option>
          </select>
        </label>
        {warnings.length > 0 && (
          <div className="validation wide">
            <div className="validation-head">
              <strong>Publishing checklist ({warnings.length})</strong>
              {warnings.some((w) => fixFor(w, v, services.rows)) && (
                <button type="button" className="ai" onClick={fixAll}>
                  <Wand2 /> Fix everything I can
                </button>
              )}
            </div>
            {warnings.map((w) => {
              const can = !!fixFor(w, v, services.rows);
              return (
                <p key={w} className="check-item">
                  <span>• {w}</span>
                  {can ? (
                    <button type="button" className="link" onClick={() => fix(w)}>
                      <Wand2 /> Fix it for me
                    </button>
                  ) : w.includes("Before you publish") ? (
                    <button type="button" className="link" onClick={openReview}>
                      <ShieldCheck /> Review now
                    </button>
                  ) : (
                    <em>needs you</em>
                  )}
                </p>
              );
            })}
            <small>Automatic fixes are a starting point — read them and adjust the wording before publishing.</small>
          </div>
        )}
        <ReviewPanel v={v} setV={setV} />
        <div className="wide ai-row">
          <button
            type="button"
            className="ai"
            onClick={generate}
            disabled={generating}
          >
            {generating ? <Loader2 className="spin" /> : <Sparkles />} Generate
            free article
          </button>
          <button
            type="button"
            onClick={generateConnected}
            disabled={generating}
          >
            <Bot /> Generate with Gemini / Groq
          </button>
          <span>
            Connected AI falls back automatically; free generation always
            remains available.
          </span>
        </div>
        {msg && <p className="error wide">{msg}</p>}
        <div className="form-actions wide article-actions">
          {row.id && (
            <button type="button" className="danger" onClick={remove} disabled={busy}>
              <Trash2 /> Delete article
            </button>
          )}
          <span className="spacer" />
          <button type="button" onClick={close}>
            Cancel
          </button>
          <button type="button" onClick={() => setLive(!live)} title="Show the website preview beside the editor">
            <PanelRight /> {live ? "Hide live preview" : "Live preview"}
          </button>
          <button type="button" onClick={() => previewArticle(v)}>
            <Eye /> Open in new tab
          </button>
          <button className={row.status === "published" ? "" : "primary"} disabled={busy}>
            {busy ? <Loader2 className="spin" /> : <Check />} Save changes
          </button>
          {row.status === "published" && (
            <button type="button" className="primary" disabled={busy} onClick={(e) => save(e as any, true)}>
              <RefreshCw /> Save &amp; republish
            </button>
          )}
        </div>
      </form>
      {live && (
        <aside className="live-preview" aria-label="Live website preview">
          <div className="live-preview-bar">
            <span>Live preview — updates as you type</span>
            <small>outreachrecruitment.net/{v.slug || "your-article"}/</small>
          </div>
          {previewHtml ? (
            <iframe ref={frame} title="Article preview" srcDoc={previewHtml} />
          ) : (
            <div className="live-preview-loading"><Loader2 className="spin" /> Loading the website template…</div>
          )}
        </aside>
      )}
      </div>
    </Modal>
  );
}

function humanReview(v: Row): Row | null {
  const r = (Array.isArray(v.validation_results) ? v.validation_results : []).find((x: any) => x?.type === "human_review");
  return r && r.checks?.facts && r.checks?.faqs && r.checks?.author ? r : null;
}

function ReviewPanel({ v, setV }: { v: Row; setV: (f: (cur: Row) => Row) => void }) {
  const done = humanReview(v);
  const [checks, setChecks] = useState({ facts: false, faqs: false, author: false });
  const [by, setBy] = useState(ARTICLE_AUTHORS.find((a) => a !== "Outreach Recruitment") || "");
  const others = (Array.isArray(v.validation_results) ? v.validation_results : []).filter((x: any) => x?.type !== "human_review");
  if (done)
    return (
      <div className="review-panel wide done" id="article-review">
        <strong>✓ Reviewed by {done.by} on {new Date(done.at).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })}</strong>
        <span>Facts, FAQs and author checked. The live article shows this review to readers and Google.</span>
        <button type="button" className="link" onClick={() => setV((cur) => ({ ...cur, validation_results: others }))}>Review again</button>
      </div>
    );
  const all = checks.facts && checks.faqs && checks.author;
  const box = (k: keyof typeof checks, label: string) => (
    <label className="review-check">
      <input type="checkbox" checked={checks[k]} onChange={(e) => setChecks({ ...checks, [k]: e.target.checked })} /> {label}
    </label>
  );
  return (
    <div className="review-panel wide" id="article-review">
      <strong>Before you publish</strong>
      <span>A person must check the article before it goes live. The review is recorded and shown on the article.</span>
      {box("facts", "I checked the facts, figures, salaries and rules against the sources")}
      {box("faqs", "I read the FAQs and the quick answer — they are correct and well written")}
      {box("author", "The author is right, and the author tip is in their own words")}
      <div className="review-row">
        <label>
          Reviewed by
          <select value={by} onChange={(e) => setBy(e.target.value)}>
            {ARTICLE_AUTHORS.filter((a) => a !== "Outreach Recruitment").map((a) => <option key={a}>{a}</option>)}
          </select>
        </label>
        {!all && (
          <button type="button" onClick={() => setChecks({ facts: true, faqs: true, author: true })}>
            I checked all three
          </button>
        )}
        <button type="button" className="primary" disabled={!all || !by} title={all ? "" : "Tick the three checks above first"}
          onClick={() => setV((cur) => ({ ...cur, validation_results: [...others, { type: "human_review", by, at: new Date().toISOString(), checks }] }))}>
          <ShieldCheck /> Mark as reviewed
        </button>
      </div>
      <small>{all ? "Now click “Mark as reviewed”, then “Save changes” (or “Save & republish”)." : "Tick the three checks, click “Mark as reviewed”, then “Save changes”."}</small>
    </div>
  );
}

function CheckupPanel({ rows, onEdit }: { rows: Row[]; onEdit: (r: Row) => void }) {
  const [data, setData] = useState<Row | null>(null);
  useEffect(() => {
    fetch(`/reports/article-checkup.json?t=${Date.now()}`).then((r) => (r.ok ? r.json() : null)).then(setData).catch(() => setData(null));
  }, []);
  if (!data) return null;
  const flagged = (data.articles || []).filter((a: Row) => a.flags?.length);
  const label: Record<string, string> = { "low-ctr": "Few clicks", "page-two": "Page 2", "not-found": "Barely shown" };
  return (
    <details className="checkup">
      <summary>
        <Gauge /> 30-day check-up — {flagged.length} article{flagged.length === 1 ? "" : "s"} need attention
        <small>Google Search Console, {data.period} · updated every Monday</small>
      </summary>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Article</th><th>Top search</th><th>Impressions</th><th>Clicks</th><th>CTR</th><th>Position</th><th>What to do</th><th></th></tr></thead>
          <tbody>
            {flagged.map((a: Row) => {
              const row = rows.find((r) => r.slug === a.slug);
              return (
                <tr key={a.slug}>
                  <td><strong>{a.title}</strong><small>{a.flags.map((f: string) => label[f] || f).join(" · ")} · live {a.days_live} days</small></td>
                  <td>{a.top_query || "—"}</td>
                  <td>{a.impressions}</td>
                  <td>{a.clicks}</td>
                  <td>{a.ctr}%</td>
                  <td>{a.position || "—"}</td>
                  <td className="advice">{a.advice.join(" ")}</td>
                  <td>{row ? <button onClick={() => onEdit(row)}>Edit</button> : <a href={a.url} target="_blank" rel="noopener">Open page</a>}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </details>
  );
}

function validateArticle(v: Row) {
  const w = [];
  if (!v.title) w.push("Add a title");
  if (!v.slug || !/^[-a-z0-9]+$/.test(v.slug)) w.push("Use a valid URL slug");
  if (!v.focus_keyword) w.push("Add a focus keyword");
  if (
    v.focus_keyword &&
    !v.seo_title?.toLowerCase().includes(v.focus_keyword.toLowerCase())
  )
    w.push("Include the focus keyword in the SEO title");
  if (
    v.focus_keyword &&
    !v.meta_description?.toLowerCase().includes(v.focus_keyword.toLowerCase())
  )
    w.push("Use the focus keyword naturally in the meta description");
  if (!v.featured_image_url) w.push("Add a featured image");
  if (!v.featured_image_alt) w.push("Add featured-image alt text");
  if (!v.service_id) w.push("Select a related service");
  if (!/^#{2,3}\s/m.test(v.body || "")) w.push("Add useful H2/H3 headings");
  if (!/^>\s+\S/m.test(v.body || ""))
    w.push(
      "Start with a direct-answer blockquote for AI search and the article template",
    );
  if (!/^##\s+FAQs\s*$/im.test(v.body || ""))
    w.push("Add an exact ## FAQs section with at least three questions");
  const internalLinks = String(v.body || "").match(
    /https:\/\/(?:www\.)?outreachrecruitment\.net\/[A-Za-z0-9_?=#%&./-]*/g,
  );
  if (new Set(internalLinks || []).size < 3)
    w.push("Add at least three contextual Outreach Recruitment internal links");
  const authorityLinks = String(v.body || "").match(
    /https:\/\/(?!(?:www\.)?outreachrecruitment\.net)[A-Za-z0-9.-]+\/[A-Za-z0-9_?=#%&./-]*/g,
  );
  if (new Set(authorityLinks || []).size < 2)
    w.push("Cite at least two relevant authoritative external sources");
  if (!/\*\*Who this is for:?\*\*/i.test(v.body || ""))
    w.push("Add a “Who this is for” line");
  if (String(v.body || "").includes(TIP_PLACEHOLDER))
    w.push("Write the author tip — replace the placeholder with the author's own words");
  if (!humanReview(v))
    w.push("Complete the “Before you publish” review (facts, FAQs, author)");
  return w;
}

function Calendar() {
  const { rows, loading } = useRows("seo_articles");
  const scheduled = rows
    .filter((r) => ["scheduled", "published", "failed"].includes(r.status))
    .sort((a, b) =>
      String(a.scheduled_at || a.published_at).localeCompare(
        String(b.scheduled_at || b.published_at),
      ),
    );
  return (
    <>
      <ListHeader title="Publishing calendar" />
      <div className="calendar-grid">
        {loading ? (
          <TableLoader />
        ) : (
          scheduled.map((r) => (
            <article className="calendar-item" key={r.id}>
              <time>{date(r.scheduled_at || r.published_at)}</time>
              <span className={`badge ${statusTone[r.status]}`}>
                {r.status}
              </span>
              <h3>{r.title}</h3>
              <p>{r.focus_keyword}</p>
            </article>
          ))
        )}
        {!loading && !scheduled.length && (
          <Empty text="No scheduled or published articles yet." />
        )}
      </div>
    </>
  );
}

function Analytics() {
  const { rows, loading, load } = useRows("seo_kpi_daily");
  const latest =
    [...rows].sort((a, b) => String(b.date).localeCompare(String(a.date)))[0] ||
    {};
  const metrics = [
    ["Organic clicks", latest.clicks],
    ["Impressions", latest.impressions],
    ["Average position", latest.avg_position],
    [
      "Click-through rate",
      latest.ctr != null ? `${Number(latest.ctr).toFixed(2)}%` : "—",
    ],
    ["Organic users", latest.organic_users],
    ["Leads", (latest.applications || 0) + (latest.employer_leads || 0)],
  ];
  return (
    <>
      <div className="toolbar">
        <div>
          <h2>Search performance</h2>
          <p>
            Automatically imported from your existing Google Search Console and
            GA4 connection.
          </p>
        </div>
        <button onClick={load}>
          <RefreshCw /> Refresh data
        </button>
      </div>
      <div className="integration-ok">
        <Check /> Live data source: existing daily SEO automation{" "}
        <small>Latest record {date(latest.date)}</small>
      </div>
      {loading ? (
        <TableLoader />
      ) : (
        <>
          <div className="metric-grid six">
            {metrics.map(([l, v]) => (
              <div className="metric" key={l}>
                <span>{l}</span>
                <strong>{v ?? "—"}</strong>
                <small>Latest daily record</small>
              </div>
            ))}
          </div>
          <section className="panel">
            <PanelHead
              icon={BarChart3}
              title="Recent performance"
              sub="Search Console and Analytics daily records"
            />
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Clicks</th>
                    <th>Impressions</th>
                    <th>CTR</th>
                    <th>Position</th>
                    <th>Organic users</th>
                    <th>Conversions</th>
                  </tr>
                </thead>
                <tbody>
                  {rows
                    .sort((a, b) =>
                      String(b.date).localeCompare(String(a.date)),
                    )
                    .slice(0, 30)
                    .map((r) => (
                      <tr key={r.id}>
                        <td>{date(r.date)}</td>
                        <td>{r.clicks ?? "—"}</td>
                        <td>{r.impressions ?? "—"}</td>
                        <td>{r.ctr ?? "—"}%</td>
                        <td>{r.avg_position ?? "—"}</td>
                        <td>{r.organic_users ?? "—"}</td>
                        <td>
                          {(r.applications || 0) + (r.employer_leads || 0)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </>
  );
}

function Budget() {
  const state = useRows("seo_api_budgets"),
    row = state.rows[0] || {
      month: new Date().toISOString().slice(0, 7),
      monthly_limit: 100,
      current_spend: 0,
      reserved_spend: 0,
      warning_threshold: 80,
      hard_stop: true,
    };
  const [v, setV] = useState<Row>(row);
  useEffect(() => {
    if (state.rows[0]) setV(state.rows[0]);
  }, [state.loading]);
  async function save(e: React.FormEvent) {
    e.preventDefault();
    await sb
      .from("seo_api_budgets")
      .upsert(
        { ...v, updated_at: new Date().toISOString() },
        { onConflict: "month" },
      );
    state.load();
    alert("Budget controls saved");
  }
  return (
    <section className="panel narrow">
      <PanelHead
        icon={CircleDollarSign}
        title="Monthly API budget"
        sub="AI generation stops automatically when the configured limit is exhausted"
      />
      <form className="form-grid pad" onSubmit={save}>
        <Field
          label="Budget month"
          type="month"
          value={v.month}
          onChange={(x) => setV({ ...v, month: x })}
        />
        <Field
          label="Monthly limit (€)"
          type="number"
          value={v.monthly_limit}
          onChange={(x) => setV({ ...v, monthly_limit: Number(x) })}
        />
        <Field
          label="Current spend (€)"
          type="number"
          value={v.current_spend}
          onChange={(x) => setV({ ...v, current_spend: Number(x) })}
        />
        <Field
          label="Reserved spend (€)"
          type="number"
          value={v.reserved_spend}
          onChange={(x) => setV({ ...v, reserved_spend: Number(x) })}
        />
        <Field
          label="Warning threshold (%)"
          type="number"
          value={v.warning_threshold}
          onChange={(x) => setV({ ...v, warning_threshold: Number(x) })}
        />
        <label className="check">
          <input
            type="checkbox"
            checked={!!v.hard_stop}
            onChange={(e) => setV({ ...v, hard_stop: e.target.checked })}
          />{" "}
          Hard-stop AI requests when exhausted
        </label>
        <button className="primary wide">Save budget controls</button>
      </form>
    </section>
  );
}

function Autopilot() {
  const state = useRows("seo_automation_settings"),
    [v, setV] = useState<Row>({
      id: "autopilot",
      enabled: true,
      drafts_per_run: 2,
      auto_topic_selection: true,
      auto_internal_links: true,
      auto_social_drafts: true,
      auto_indexing_request: true,
      publish_hour: 9,
    });
  useEffect(() => {
    if (state.rows[0]) setV(state.rows[0]);
  }, [state.loading]);
  async function save() {
    const { error } = await sb
      .from("seo_automation_settings")
      .upsert({ ...v, updated_at: new Date().toISOString() });
    error ? alert(error.message) : alert("SEO Autopilot settings saved");
  }
  return (
    <div className="split">
      <section className="panel">
        <PanelHead
          icon={Bot}
          title="SEO Autopilot"
          sub="Research → draft → your review → publish → measure"
        />
        <div className="autopilot">
          <label className="switch">
            <input
              type="checkbox"
              checked={!!v.enabled}
              onChange={(e) => setV({ ...v, enabled: e.target.checked })}
            />
            <span>
              {v.enabled ? "Automation is running" : "Automation is paused"}
            </span>
          </label>
          <Field
            label="Drafts per generation run"
            type="number"
            value={v.drafts_per_run}
            onChange={(x) => setV({ ...v, drafts_per_run: Number(x) })}
          />
          {[
            ["auto_topic_selection", "Select topics from Google automatically"],
            ["auto_internal_links", "Suggest and validate internal links"],
            ["auto_social_drafts", "Prepare social and newsletter copy"],
            ["auto_indexing_request", "Prepare Google indexing requests"],
          ].map(([k, l]) => (
            <label className="check" key={k}>
              <input
                type="checkbox"
                checked={!!v[k]}
                onChange={(e) => setV({ ...v, [k]: e.target.checked })}
              />
              {l}
            </label>
          ))}
          <button className="primary" onClick={save}>
            Save automation settings
          </button>
        </div>
      </section>
      <section className="panel">
        <PanelHead
          icon={ShieldCheck}
          title="Your only required actions"
          sub="Everything else runs automatically"
        />
        <div className="review-steps">
          <p>
            <b>1</b> Review or change the generated text
          </p>
          <p>
            <b>2</b> Approve or replace the suggested image
          </p>
          <p>
            <b>3</b> Select Publish now or a scheduled date
          </p>
          <p>
            <Check /> News Updates, sitemap, social copy and performance reviews
            follow automatically
          </p>
        </div>
      </section>
    </div>
  );
}

function SocialQueue() {
  const state = useRows("seo_social_posts");
  async function update(id: string, status: string) {
    await sb
      .from("seo_social_posts")
      .update({ status, updated_at: new Date().toISOString() })
      .eq("id", id);
    state.load();
  }
  return (
    <>
      <ListHeader title="Social and newsletter approval queue" />
      <div className="record-grid">
        {state.rows.map((post) => (
          <article className="record" key={post.id}>
            <div>
              <span className={`badge ${statusTone[post.status]}`}>
                {post.platform}
              </span>
              <h3>
                {post.status === "review" ? "Ready for review" : post.status}
              </h3>
              <p>{post.content}</p>
            </div>
            <div className="toolbar-actions">
              <button onClick={() => update(post.id, "rejected")}>
                Reject
              </button>
              <button
                className="primary"
                onClick={() => update(post.id, "approved")}
              >
                <Check /> Approve copy
              </button>
            </div>
          </article>
        ))}
        {!state.loading && !state.rows.length && (
          <Empty text="No social drafts are waiting." />
        )}
      </div>
    </>
  );
}

function SimpleCrud({
  table,
  title,
  action,
  defaults,
  fields,
  statuses,
  extra,
}: {
  table: string;
  title: string;
  action: string;
  defaults: Row;
  fields: string[];
  statuses: string[];
  extra?: string;
}) {
  const state = useRows(table),
    [edit, setEdit] = useState<Row | null>(null);
  return (
    <>
      <ListHeader
        title={title}
        action={action}
        onAction={() => setEdit(defaults)}
      />
      {state.loading ? (
        <TableLoader />
      ) : (
        <Cards
          rows={state.rows}
          empty={`No ${title.toLowerCase()} yet.`}
          render={(r) => (
            <>
              <div>
                <span className={`badge ${statusTone[r.status]}`}>
                  {r.status}
                </span>
                <h3>{r.name || r.keyword}</h3>
                <p>{r.objective || r.suggested_title || r.notes}</p>
              </div>
              <div className="card-meta">
                <span>
                  Location<strong>{r.target_location || "Malta"}</strong>
                </span>
                <span>
                  Updated<strong>{date(r.updated_at)}</strong>
                </span>
              </div>
              <button onClick={() => setEdit(r)}>Edit</button>
            </>
          )}
        />
      )}{" "}
      {edit && (
        <GenericModal
          table={table}
          row={edit}
          fields={fields}
          statuses={statuses}
          extra={extra}
          close={() => setEdit(null)}
          saved={() => {
            setEdit(null);
            state.load();
          }}
        />
      )}
    </>
  );
}
function GenericModal({
  table,
  row,
  fields,
  statuses,
  extra,
  close,
  saved,
}: {
  table: string;
  row: Row;
  fields: string[];
  statuses: string[];
  extra?: string;
  close: () => void;
  saved: () => void;
}) {
  const [v, setV] = useState(row),
    [busy, setBusy] = useState(false),
    [msg, setMsg] = useState("");
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const { error } = await sb
      .from(table)
      .upsert({ ...v, updated_at: new Date().toISOString() });
    setBusy(false);
    error ? setMsg(error.message) : saved();
  }
  return (
    <Modal title={row.id ? "Edit record" : "Create record"} close={close}>
      <form className="form-grid" onSubmit={save}>
        {fields.map((k) =>
          k === "category" ? (
            <Select
              key={k}
              label="Category"
              value={v.category || "—"}
              options={["—", ...CATEGORIES]}
              onChange={(x) => setV({ ...v, category: x === "—" ? null : x })}
            />
          ) : k === "notes" || k === "objective" ? (
            <Area
              key={k}
              label={label(k)}
              className="wide"
              value={v[k]}
              onChange={(x) => setV({ ...v, [k]: x })}
            />
          ) : (
            <Field
              key={k}
              label={label(k)}
              type={
                k.includes("date")
                  ? "date"
                  : k.includes("month")
                    ? "number"
                    : "text"
              }
              required={["name", "keyword"].includes(k)}
              value={v[k]}
              onChange={(x) =>
                setV({
                  ...v,
                  [k]:
                    k === "priority" || k === "articles_per_month"
                      ? Number(x)
                      : x,
                })
              }
            />
          ),
        )}
        {extra && (
          <Select
            label={label(extra)}
            value={v[extra]}
            options={["informational", "commercial", "transactional", "local"]}
            onChange={(x) => setV({ ...v, [extra]: x })}
          />
        )}
        <Select
          label="Status"
          value={v.status}
          options={statuses}
          onChange={(x) => setV({ ...v, status: x })}
        />
        {msg && <p className="error wide">{msg}</p>}
        <FormActions busy={busy} close={close} />
      </form>
    </Modal>
  );
}

function DataList({ section }: { section: Section }) {
  const state = useRows(section.table!);
  return (
    <>
      <ListHeader title={section.label} />
      {state.loading ? (
        <TableLoader />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name / key</th>
                <th>Status / value</th>
                <th>Message</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {state.rows.map((r) => (
                <tr key={r.id || r.key}>
                  <td>
                    <strong>{r.job_name || r.key || r.name}</strong>
                  </td>
                  <td>{r.status || String(r.value ?? "").slice(0, 80)}</td>
                  <td>{r.message || r.error_details || "—"}</td>
                  <td>{date(r.updated_at || r.started_at)}</td>
                </tr>
              ))}
              {!state.rows.length && (
                <tr>
                  <td colSpan={4}>
                    <Empty text="No records yet." />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
function LogTable({ rows }: { rows: Row[] }) {
  return (
    <div className="log-list">
      {rows.length ? (
        rows.map((r) => (
          <div key={r.id}>
            <span className={`dot ${statusTone[r.status] || "blue"}`} />
            <div>
              <strong>{r.job_name}</strong>
              <p>{r.message || r.error_details || "Completed"}</p>
            </div>
            <time>{date(r.started_at)}</time>
          </div>
        ))
      ) : (
        <Empty text="No automation activity yet." />
      )}
    </div>
  );
}
function Cards({
  rows,
  empty,
  render,
}: {
  rows: Row[];
  empty: string;
  render: (r: Row) => React.ReactNode;
}) {
  return (
    <div className="record-grid">
      {rows.map((r) => (
        <article className="record" key={r.id}>
          {render(r)}
        </article>
      ))}
      {!rows.length && <Empty text={empty} />}
    </div>
  );
}
function ListHeader({
  title,
  action,
  onAction,
  children,
}: {
  title: string;
  action?: string;
  onAction?: () => void;
  children?: React.ReactNode;
}) {
  return (
    <div className="toolbar">
      <div>
        <h2>{title}</h2>
        <p>Securely stored in Supabase and restricted to administrators.</p>
      </div>
      <div className="toolbar-actions">
        {children}
        {action && (
          <button className="primary" onClick={onAction}>
            + {action}
          </button>
        )}
      </div>
    </div>
  );
}
function PanelHead({
  icon: Icon,
  title,
  sub,
}: {
  icon: React.ElementType;
  title: string;
  sub: string;
}) {
  return (
    <div className="panel-head">
      <span>
        <Icon />
      </span>
      <div>
        <h2>{title}</h2>
        <p>{sub}</p>
      </div>
    </div>
  );
}
function Modal({
  title,
  close,
  large = false,
  wide = false,
  children,
}: {
  title: string;
  close: () => void;
  large?: boolean;
  wide?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div
      className="modal-bg"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) close();
      }}
    >
      <section className={wide ? "modal large wide" : large ? "modal large" : "modal"}>
        <header>
          <h2>{title}</h2>
          <button className="icon" onClick={close}>
            <X />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}
function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false,
  className = "",
}: {
  label: string;
  value: any;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
  className?: string;
}) {
  return (
    <label className={className}>
      {label}
      <input
        type={type}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        required={required}
      />
    </label>
  );
}
function Area({
  label,
  value,
  onChange,
  rows = 3,
  className = "",
}: {
  label: string;
  value: any;
  onChange: (v: string) => void;
  rows?: number;
  className?: string;
}) {
  return (
    <label className={className}>
      {label}
      <textarea
        rows={rows}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: any;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <label>
      {label}
      <select
        value={value || options[0]}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o}>{o}</option>
        ))}
      </select>
    </label>
  );
}
function ImageUploader({
  label = "Featured image · 1200 × 630 recommended",
  value,
  alt,
  onUploaded,
}: {
  label?: string;
  value?: string;
  alt?: string;
  onUploaded: (url: string, width: number, height: number) => void;
}) {
  const [busy, setBusy] = useState(false);
  async function upload(file?: File) {
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type))
      return alert("Use JPEG, PNG or WebP.");
    if (file.size > 5 * 1024 * 1024)
      return alert("Image must be 5 MB or smaller.");
    setBusy(true);
    const ext = file.name.split(".").pop()?.toLowerCase() || "jpg";
    const path = `articles/${crypto.randomUUID()}.${ext}`;
    const { error } = await sb.storage
      .from("seo-content")
      .upload(path, file, { contentType: file.type });
    if (error) {
      setBusy(false);
      return alert(error.message);
    }
    const dimensions = await new Promise<{ width: number; height: number }>(
      (resolve) => {
        const image = new Image();
        image.onload = () =>
          resolve({ width: image.width, height: image.height });
        image.onerror = () => resolve({ width: 0, height: 0 });
        image.src = URL.createObjectURL(file);
      },
    );
    const { data } = sb.storage.from("seo-content").getPublicUrl(path);
    onUploaded(data.publicUrl, dimensions.width, dimensions.height);
    setBusy(false);
  }
  return (
    <label>
      {label}
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={(e) => upload(e.target.files?.[0])}
      />
      <small>{busy ? "Uploading securely…" : "Maximum 5 MB"}</small>
      {value && <img className="upload-preview" src={value} alt={alt || ""} />}
    </label>
  );
}
function FormActions({ busy, close }: { busy: boolean; close: () => void }) {
  return (
    <div className="form-actions wide">
      <button type="button" onClick={close}>
        Cancel
      </button>
      <button className="primary" disabled={busy}>
        {busy ? <Loader2 className="spin" /> : <Check />} Save changes
      </button>
    </div>
  );
}
function Empty({ text }: { text: string }) {
  return (
    <div className="empty">
      <BookOpen />
      <strong>{text}</strong>
      <p>Create the first record to get started.</p>
    </div>
  );
}
function FullLoader() {
  return (
    <div className="full-loader">
      <Loader2 className="spin" />
      <p>Opening SEO Control Centre…</p>
    </div>
  );
}
function TableLoader() {
  return (
    <div className="table-loader">
      <Loader2 className="spin" /> Loading records…
    </div>
  );
}
function LoadingBar() {
  return <div className="loading-bar" />;
}
function label(k: string) {
  return k.replaceAll("_", " ").replace(/^./, (x) => x.toUpperCase());
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
