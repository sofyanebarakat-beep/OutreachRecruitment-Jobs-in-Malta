/* Detailed teaching notes for each week of the practical SEO course. */
window.COURSE_GUIDANCE = {
  1: {
    why: "Every later decision depends on trustworthy measurement. This week separates visibility in Google from behaviour on the website and connects both to applications and employer enquiries.",
    prepare: ["Confirm Search Console property access", "Confirm GA4 receives page_view events", "Write down the course start date before changing pages"],
    steps: ["Record the previous 28 days as the untouched baseline.", "Map candidate and employer journeys from search to conversion.", "Test apply_click and employer_lead_submit in GA4 Realtime.", "Check that daily Search Console and GA4 rows reach the Data section.", "Write one business question each KPI can answer."],
    evidence: ["Baseline screenshot/export", "GA4 Realtime event test", "Completed Daily KPI rows", "Journey map"],
    pitfalls: ["Treating traffic as the final outcome", "Comparing incomplete date ranges", "Changing pages before saving the baseline"]
  },
  2: {
    why: "Keyword research reveals what candidates and employers actually need. Intent determines whether a query deserves a job page, sector page, service page or guide.",
    prepare: ["Open the Keywords tracker", "Review the latest Search Console queries", "List candidate and employer audiences separately"],
    steps: ["Group real queries by candidate, employer, commercial and informational intent.", "Create sector clusters and identify long-tail Malta queries.", "Assign one preferred page to each important query.", "Flag queries with no suitable page and pages competing for the same intent.", "Prioritise by business value, impressions and realistic ranking opportunity."],
    evidence: ["Labelled keyword set", "Keyword-to-page map", "Cannibalisation list", "Priority keyword shortlist"],
    pitfalls: ["Choosing keywords only by volume", "Mixing employer and candidate intent", "Creating several pages for the same search intent"]
  },
  3: {
    why: "On-page SEO makes page purpose obvious to users and search engines. Internal links show relationships and guide visitors toward useful next actions.",
    prepare: ["Choose five priority pages", "Record their current titles, H1s and GSC data", "Open the Pages tracker"],
    steps: ["Match each page to one primary intent.", "Rewrite title, description and H1 as a coherent promise.", "Improve the opening answer and CTA without keyword stuffing.", "Add descriptive internal links from relevant guides and sector pages.", "Commit the change so the experiment tracker can measure it."],
    evidence: ["Before/after copy", "Internal-link list", "Git commit", "Experiment baseline"],
    pitfalls: ["Repeating the exact keyword unnaturally", "Using vague anchor text", "Changing many unrelated variables in one experiment"]
  },
  4: {
    why: "Recruitment sites change quickly. Technical errors can leave expired jobs indexed, hide live roles, split signals between duplicate URLs or invalidate Google Jobs eligibility.",
    prepare: ["Open Technical and Alerts", "Review the automated audit", "Select representative live and closed jobs"],
    steps: ["Check robots, sitemap and canonical consistency.", "Validate JobPosting fields and expiry dates.", "Review duplicate .html/folder routes and redirect behaviour.", "Prioritise Critical and High issues before cosmetic findings.", "Rerun the audit and save validation evidence."],
    evidence: ["Issue list with severity", "Rich Results test", "Fixed/validated rows", "Before/after HTTP or schema result"],
    pitfalls: ["Deleting URLs without redirects", "Keeping expired jobs in the sitemap", "Marking an issue fixed without retesting"]
  },
  5: {
    why: "Sector pages connect job supply with sector-level demand. The best next sector is supported by both Search Console opportunity and enough live vacancies.",
    prepare: ["Open Sector opportunities", "Check job counts and GSC impressions", "Review existing sector pages"],
    steps: ["Rank sectors by demand, jobs and current position.", "Choose a sector with a clear content gap.", "Define candidate intent and useful Malta-specific information.", "Build or improve the page and link its live jobs.", "Record the page baseline and review date."],
    evidence: ["Opportunity table", "Selected-sector rationale", "Published sector page", "Experiment row"],
    pitfalls: ["Choosing only the largest sector", "Publishing a page with no live jobs", "Copying generic text between sectors"]
  },
  6: {
    why: "Topic clusters build depth around a sector and make it easier for users and crawlers to move between guidance, sector pages and vacancies.",
    prepare: ["Choose one priority sector", "List its existing pages", "Review orphan and sector-link audit findings"],
    steps: ["Choose a central pillar page.", "Group supporting questions by journey stage.", "Map links from guides to the pillar, pillar to jobs and jobs back to relevant guidance.", "Create briefs for missing supporting content.", "Rerun the link audit after implementation."],
    evidence: ["Cluster map", "Content briefs", "New internal links", "Reduced orphan findings"],
    pitfalls: ["Creating content without a pillar", "Linking every page to everything", "Using near-duplicate supporting articles"]
  },
  7: {
    why: "Employer searches have lower volume but higher commercial value. Clear proof, process and conversion paths turn visibility into qualified hiring enquiries.",
    prepare: ["Review employer queries", "Audit service/employer pages", "Test employer_lead_submit"],
    steps: ["Map employer pain points to commercial queries.", "Explain the recruitment process and relevant proof.", "Create a focused CTA and working enquiry path.", "Add employer FAQs and supporting internal links.", "Compare organic employer leads with traffic."],
    evidence: ["Employer keyword map", "Improved commercial page", "Successful GA4 lead event", "Lead baseline"],
    pitfalls: ["Writing only for candidates", "Using unsupported claims", "Counting newsletter submissions as employer leads"]
  },
  8: {
    why: "Refreshing a proven page is often more valuable than publishing another weak page. Decisions should follow evidence: keep, improve, merge, redirect or remove.",
    prepare: ["Sort Pages by impressions", "Find high-impression/low-CTR pages", "Find overlapping or declining content"],
    steps: ["Classify pages by performance and intent fit.", "Select refresh candidates with measurable upside.", "Improve accuracy, structure, answers and internal links.", "Consolidate only where intent genuinely overlaps.", "Measure the change as an experiment."],
    evidence: ["Content inventory", "Decision assigned per page", "Refresh diff", "Review schedule"],
    pitfalls: ["Refreshing solely because content is old", "Deleting pages with links or traffic", "Judging results after only a few days"]
  },
  9: {
    why: "Local SEO helps Malta employers and candidates confirm that the business is real, relevant and accessible. Consistent business information reduces ambiguity.",
    prepare: ["Confirm official name, address and phone", "Open Google Business Profile", "Open the Local tracker"],
    steps: ["Audit business details across owned profiles.", "Complete appropriate categories, services and description.", "Link to the most relevant website destination.", "Create a legitimate review process without incentives.", "Record corrections and review growth."],
    evidence: ["NAP master record", "Profile screenshots", "Citation corrections", "Review-process document"],
    pitfalls: ["Creating fake locations", "Inconsistent contact details", "Buying or incentivising reviews"]
  },
  10: {
    why: "Location content is useful only when real job supply or service relevance supports it. Location data should guide priorities rather than produce doorway pages.",
    prepare: ["Review registry locations", "Compare location queries", "Check existing Malta location pages"],
    steps: ["Rank locations by open jobs and real demand.", "Choose locations with distinct, supportable value.", "Add useful local context and current vacancies.", "Build consistent citations where the business is genuinely represented.", "Measure each location page separately."],
    evidence: ["Location opportunity list", "Published or improved page", "Citation record", "Page baseline"],
    pitfalls: ["Mass-producing thin location pages", "Claiming offices that do not exist", "Leaving location pages without current jobs"]
  },
  11: {
    why: "Relevant links can strengthen authority and discovery, but manipulative link building creates risk. Quality and legitimacy matter more than raw quantity.",
    prepare: ["Define target pages", "List Malta and sector-relevant organisations", "Open Backlinks"],
    steps: ["Score prospects for relevance and legitimacy.", "Find a real reason each site may reference the resource.", "Write personalised, transparent outreach.", "Track replies and acquired links.", "Verify the live link, destination and anchor context."],
    evidence: ["Qualified prospect list", "Outreach examples", "Response log", "Verified acquired links"],
    pitfalls: ["Buying bulk links", "Using identical outreach", "Chasing authority metrics without relevance"]
  },
  12: {
    why: "Digital PR earns attention by publishing something genuinely useful or newsworthy, not by asking for links without a reason.",
    prepare: ["Review internal data you may publish safely", "Choose one audience", "Identify journalists or organisations that cover it"],
    steps: ["Define one evidence-led story or resource.", "Validate the data and document methodology.", "Create a clear landing page with quotable findings.", "Build a targeted media list and pitch angles.", "Track coverage, links and referral outcomes."],
    evidence: ["Asset concept", "Methodology", "Published resource", "Coverage/outreach tracker"],
    pitfalls: ["Publishing confidential data", "Making claims the data cannot support", "Sending the same pitch to unrelated contacts"]
  },
  13: {
    why: "Answer Engine Optimization makes important answers easy to find, understand and reuse while keeping the page helpful for humans.",
    prepare: ["Collect real candidate and employer questions", "Choose pages already relevant to them", "Check existing FAQs"],
    steps: ["Place a direct answer near each question.", "Support the answer with accurate detail and next steps.", "Use headings and lists where they improve comprehension.", "Add FAQ schema only when matching visible content.", "Test structured data and monitor query changes."],
    evidence: ["Question map", "Improved answer blocks", "Schema validation", "GSC query baseline"],
    pitfalls: ["Adding hidden schema-only answers", "Giving legal/visa claims without verification", "Writing for snippets instead of users"]
  },
  14: {
    why: "Generative systems favour clear entities, consistent facts and well-supported information. GEO work improves source quality rather than trying to manipulate an AI answer.",
    prepare: ["Audit organisation facts", "Identify pages with unique expertise", "List claims needing sources"],
    steps: ["Make organisation and service descriptions consistent.", "Add authorship, dates and evidence where appropriate.", "Strengthen original, Malta-specific explanations.", "Use structured headings and descriptive internal links.", "Document manual AI observations without treating them as rankings."],
    evidence: ["Entity/fact sheet", "Source upgrades", "Updated expert pages", "Dated AI observations"],
    pitfalls: ["Inventing statistics", "Presenting AI output as proof", "Repeating generic summaries with no original value"]
  },
  15: {
    why: "AI visibility is volatile and partly unobservable. A fixed, repeatable question set plus referral data creates a defensible benchmark.",
    prepare: ["Choose fixed questions and engines", "Confirm AI referral collection", "Open AI visibility"],
    steps: ["Run the same prompts in a clean, repeatable way.", "Record whether Outreach is surfaced or cited.", "Record cited competitors and answer characteristics.", "Compare manual observations with GA4 AI referrals.", "Repeat on schedule before drawing conclusions."],
    evidence: ["Dated prompt set", "Screenshots/notes", "Citation observations", "AI referral sessions"],
    pitfalls: ["Changing prompts every test", "Treating one answer as a trend", "Confusing a brand mention with a citation"]
  },
  16: {
    why: "The final analysis turns 120 days of activity into evidence: what changed, what moved, what did not, and what deserves the next 90 days.",
    prepare: ["Check daily data completeness", "Review experiments and validated fixes", "Open the Final case study"],
    steps: ["Compare equivalent Day 1 and Day 120 windows.", "Separate correlation from changes with plausible evidence.", "Summarise wins, failures and unresolved limitations.", "Choose five priorities using impact and effort.", "Define measurable targets and review dates for the next 90 days."],
    evidence: ["Before/after KPI table", "Completed experiment conclusions", "Final case study", "90-day roadmap"],
    pitfalls: ["Comparing unequal date ranges", "Claiming causation without evidence", "Creating a roadmap without owners or review dates"]
  }
};
