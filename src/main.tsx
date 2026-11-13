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
  X,
} from "lucide-react";
import "./styles.css";

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
  const extras = [
    "Create a simple tracker containing the opportunity, closing date, documents submitted and next follow-up date. This prevents duplicate applications and helps you respond promptly.",
    "Prepare examples that explain what you did, how you approached a problem and what result you achieved. Specific examples are more useful than broad claims.",
    "Review your public professional profile and make sure its dates and experience are consistent with your CV. Remove outdated or misleading information.",
    "Before an interview, reread the description and prepare questions about the work itself. Avoid focusing only on information that has not yet been confirmed.",
    "Keep personal documents secure. Submit sensitive information only through an official, verified process when it is genuinely required.",
  ];
  let i = 0;
  while (body.split(/\s+/).length < targetWords - 80) {
    body += `\n\n### Practical action ${i + 1}\n\n${extras[i % extras.length]} Relate this step directly to ${safeKeyword} and record what you learn before continuing.`;
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
    [open, setOpen] = useState(false);
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
    ["Published", count("published"), "articles"],
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

function Campaigns() {
  const state = useRows("seo_campaigns");
  const [edit, setEdit] = useState<Row | null>(null);
  return (
    <>
      <ListHeader
        title="SEO campaigns"
        action="Create automated campaign"
        onAction={() =>
          setEdit({
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
      />
      {state.loading ? (
        <TableLoader />
      ) : (
        <Cards
          rows={state.rows}
          empty="No campaigns yet."
          render={(r) => (
            <>
              <div>
                <span className={`badge ${statusTone[r.status]}`}>
                  {r.status}
                </span>
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
    if (data.auto_generate && data.status === "active") {
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
          Automatically create related keywords and article drafts
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
    const { error: insertError } = await sb.from("seo_articles").insert({
      ...data,
      focus_keyword: r.keyword,
      topic_id: r.id,
      service_id: r.service_id,
      campaign_id: r.campaign_id,
      status: "generated",
      language: "English",
      created_by: (await sb.auth.getUser()).data.user?.id,
    });
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
          <button onClick={syncGsc} disabled={syncing}>
            {syncing ? <Loader2 className="spin" /> : <Search />} Find ideas
            from Google
          </button>
          <button
            className="primary"
            onClick={() =>
              setEdit({ status: "idea", intent: "informational", priority: 50 })
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
                <th>Intent</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Suggested article</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {state.rows.map((r) => (
                <tr key={r.id}>
                  <td>
                    <strong>{r.keyword}</strong>
                    <small>{r.target_location || "Malta"}</small>
                  </td>
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
                  <td colSpan={6}>
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

function Articles({ review = false }: { review?: boolean }) {
  const state = useRows("seo_articles"),
    [edit, setEdit] = useState<Row | null>(null);
  const rows = review
    ? state.rows.filter((r) => r.status === "review")
    : state.rows;
  async function status(r: Row, s: string) {
    if (s === "approved" && validateArticle(r).length) {
      alert("Cannot publish:\n• " + validateArticle(r).join("\n• "));
      return;
    }
    await sb
      .from("seo_articles")
      .update({ status: s, updated_at: new Date().toISOString() })
      .eq("id", r.id);
    state.load();
  }
  return (
    <>
      <ListHeader
        title={review ? "Articles awaiting review" : "Article library"}
        action={review ? undefined : "Create article"}
        onAction={() =>
          setEdit({
            status: "draft",
            language: "English",
            indexable: true,
            author_name: "Outreach Recruitment",
            template_style: "editorial",
          })
        }
      />
      {state.loading ? (
        <TableLoader />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Article</th>
                <th>Service / keyword</th>
                <th>Quality</th>
                <th>Status</th>
                <th>Schedule</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>
                    <strong>{r.title || "Untitled"}</strong>
                    <small>/{r.slug || "no-slug"}</small>
                  </td>
                  <td>{r.focus_keyword || "—"}</td>
                  <td>
                    <b className="score">{r.quality_score || 0}</b>
                  </td>
                  <td>
                    <span className={`badge ${statusTone[r.status]}`}>
                      {r.status}
                    </span>
                  </td>
                  <td>{date(r.scheduled_at)}</td>
                  <td className="actions">
                    <button onClick={() => setEdit(r)}>
                      Edit text / image
                    </button>
                    {review ? (
                      <>
                        <button onClick={() => status(r, "approved")}>
                          <Check /> Publish now
                        </button>
                        <button
                          className="danger"
                          onClick={() => status(r, "rejected")}
                        >
                          Reject
                        </button>
                      </>
                    ) : (
                      <>
                        {["generated", "draft", "review"].includes(
                          r.status,
                        ) && (
                          <button
                            className="primary"
                            onClick={() => status(r, "approved")}
                          >
                            <Globe2 /> Publish now
                          </button>
                        )}
                        {r.status === "scheduled" && (
                          <span className="badge purple">
                            Auto-publishes {date(r.scheduled_at)}
                          </span>
                        )}
                      </>
                    )}
                  </td>
                </tr>
              ))}
              {!rows.length && (
                <tr>
                  <td colSpan={6}>
                    <Empty
                      text={
                        review
                          ? "Nothing is waiting for review."
                          : "No articles yet."
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
  const [v, setV] = useState(row),
    [busy, setBusy] = useState(false),
    [msg, setMsg] = useState(""),
    [generating, setGenerating] = useState(false),
    [targetWords, setTargetWords] = useState(1200);
  const services = useRows("seo_services");
  const set = (k: string, x: any) =>
    setV((current: Row) => ({ ...current, [k]: x }));
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const payload = {
      ...v,
      slug: v.slug || slugify(v.title),
      status:
        v.scheduled_at && v.status !== "published" ? "scheduled" : v.status,
      updated_at: new Date().toISOString(),
    };
    const { error } = await sb.from("seo_articles").upsert(payload);
    setBusy(false);
    error ? setMsg(error.message) : saved();
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
    setV((current: Row) => ({ ...current, ...data }));
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
      setV((current: Row) => ({
        ...current,
        ...data,
        status: "generated",
      }));
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
    >
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
            <strong>Publishing checklist</strong>
            {warnings.map((w) => (
              <p key={w}>• {w}</p>
            ))}
          </div>
        )}
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
        <FormActions busy={busy} close={close} />
      </form>
    </Modal>
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
          k === "notes" || k === "objective" ? (
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
}: {
  title: string;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <div className="toolbar">
      <div>
        <h2>{title}</h2>
        <p>Securely stored in Supabase and restricted to administrators.</p>
      </div>
      {action && (
        <button className="primary" onClick={onAction}>
          + {action}
        </button>
      )}
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
  children,
}: {
  title: string;
  close: () => void;
  large?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div
      className="modal-bg"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) close();
      }}
    >
      <section className={large ? "modal large" : "modal"}>
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
