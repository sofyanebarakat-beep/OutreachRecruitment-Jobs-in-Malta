// Outreach Recruitment — SEO & KPI Course (30 days · 1 hour daily · Learn + Practice + Measure)
// Content for the admin "Course" section. Progress and KPI data are stored separately
// (Supabase seo_settings key "course30" + seo_kpi_daily / seo_keywords).
window.COURSE30 = {
  title: "Outreach Recruitment — SEO & KPI Course",
  subtitle: "30 Days · 1 Hour Daily · Learn + Practice + Measure",
  objective:
    "Improve the Google rankings of outreachrecruitment.net, attract more organic visitors, " +
    "and generate more job applications and employer enquiries.",
  focusKeywords: [
    "Recruitment Agencies Malta",
    "Jobs in Malta",
    "Hospitality Jobs in Malta",
    "Recruitment Agency Malta",
    "Construction Jobs Malta",
    "Jobs in Malta for Foreigners",
  ],
  dailyStructure: [
    { activity: "Theory", minutes: 15, objective: "Learn one SEO concept" },
    { activity: "Practice", minutes: 25, objective: "Apply it to the real website" },
    { activity: "QCM", minutes: 10, objective: "Test your knowledge" },
    { activity: "KPI tracking", minutes: 10, objective: "Measure and record progress" },
  ],
  phases: [
    {
      id: "w1", label: "Week 1", days: [1, 7], title: "Keyword Research & Google Rankings",
      summary: "Understand Google Search Console, find ranking opportunities, analyze search intent, select keywords, and improve SEO titles.",
      kpis: ["Clicks", "Impressions", "CTR", "Average position", "Number of priority keywords"],
    },
    {
      id: "w2", label: "Week 2", days: [8, 14], title: "On-Page SEO",
      summary: "Improve headings, content quality, internal links, job listings, hospitality pages, and employer pages.",
      kpis: ["Optimized pages", "Relevant internal links", "Organic landing-page clicks"],
    },
    {
      id: "w3", label: "Week 3", days: [15, 21], title: "Backlinks & Website Authority",
      summary: "Analyze competitors, identify quality backlinks, improve business citations, publish useful content, and promote it.",
      kpis: ["Relevant referring domains", "Content impressions", "Referral traffic"],
    },
    {
      id: "w4", label: "Week 4", days: [22, 28], title: "Advanced SEO & Performance",
      summary: "Fix keyword cannibalization, improve CTR, validate job structured data, update pages, and analyze conversions.",
      kpis: ["Keyword positions", "Organic clicks", "Applications", "Employer leads"],
    },
    {
      id: "final", label: "Days 29–30", days: [29, 30], title: "Final Audit & Growth Plan",
      summary: "Evaluate results, complete your SEO assessment, and prepare the next 60-day strategy.",
      kpis: ["Overall organic growth", "Priority keyword progress", "Completed improvements"],
    },
  ],
  // Day 1 progress recorded from Google Search Console
  day1Keywords: [
    { keyword: "outreach recruitment", baseline_position: 1.0, priority: "Maintain" },
    { keyword: "recruitment agencies malta", baseline_position: 9.6, priority: "High", baseline_impressions: 274 },
    { keyword: "hospitality jobs in malta", baseline_position: 10.6, priority: "High" },
    { keyword: "best recruitment agencies in malta", baseline_position: 7.4, priority: "Medium" },
  ],
  firstOpportunity:
    "Your first ranking opportunity is “recruitment agencies malta”, which has 274 recorded impressions " +
    "and an average position of 9.6.",
  baselineWarning:
    "Your overall website baseline still needs verification because the reported clicks, impressions, and CTR do not match.",
  targets: [
    { id: "clicks", value: "+20%", label: "Organic clicks", pct: 20 },
    { id: "impressions", value: "+30%", label: "Google impressions", pct: 30 },
    { id: "top10", value: "5", label: "Priority keywords reaching Top 10", count: 5 },
    { id: "lessons", value: "30", label: "Daily lessons completed", count: 30 },
  ],
  targetsNote: "Initial 90-day growth targets. These are working targets, not guaranteed outcomes.",
  tools: [
    { name: "Google Search Console", use: "rankings and keywords" },
    { name: "Google Analytics 4", use: "organic visitors and conversions" },
    { name: "Google Sheets", use: "KPI tracking" },
    { name: "Google Search", use: "competitor analysis" },
  ],
  nextStep: {
    day: 2,
    title: "Keyword Research",
    text: "Identify 20 relevant keywords, select 10 ranking opportunities, and decide which five Outreach Recruitment pages to improve first.",
  },
};
