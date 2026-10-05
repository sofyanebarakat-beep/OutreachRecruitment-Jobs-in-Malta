#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const { execFileSync } = require("child_process");

const root = path.resolve(__dirname, "..");
const context = { window: {} };
vm.createContext(context);
for (const file of ["admin/course-data.js", "admin/course-metrics.js"]) {
  vm.runInContext(fs.readFileSync(path.join(root, file), "utf8"), context, { filename: file });
}
const course = context.window.COURSE;
const metrics = context.window.COURSE_METRICS;
const output = path.join(root, "admin/notion-templates");
fs.mkdirSync(output, { recursive: true });

const reviewDays = [7, 30, 30, 21, 30, 30, 30, 30, 30, 60, 60, 60, 30, 30, 30, 90];
const csv = (rows) => rows.map((row) => row.map((value) => {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}).join(",")).join("\n") + "\n";

const taskRows = [["Task ID", "Task", "Week", "Week title", "Track", "Status", "Owner", "Due date", "Priority", "Impact", "Effort", "KPI focus", "Review date", "Evidence URL", "Notes", "Course URL"]];
for (const week of course.weeks) {
  week.tasks.forEach((task, index) => taskRows.push([
    `SEO-W${String(week.n).padStart(2, "0")}-T${String(index + 1).padStart(2, "0")}`,
    task, week.n, week.title, week.track, "To do", "", "", "Medium", "", "",
    metrics[week.n].kpis.join(", "), "", "", "", `https://outreachrecruitment.net/admin/#/course/${week.n}`
  ]));
}

const kpiRows = [["KPI Record ID", "Date", "Week", "KPI", "Current value", "Previous value", "Change", "Target", "Direction", "Data source", "Page", "Query", "Audience", "Confidence", "Action", "Review date", "Evidence URL", "Notes"]];
const directions = { clicks: "Increase", impressions: "Increase", ctr: "Increase", avg_position: "Decrease", organic_users: "Increase", applications: "Increase", employer_leads: "Increase", ai_referrals: "Increase" };
for (const week of course.weeks) for (const key of metrics[week.n].kpis) kpiRows.push([
  `KPI-W${String(week.n).padStart(2, "0")}-${key.toUpperCase()}`, "", week.n, key, "", "", "", "", directions[key], metrics[week.n].source, "", "", "", "Low", metrics[week.n].action, "", "", metrics[week.n].question
]);

const actionRows = [["Experiment ID", "Name", "Week", "Related Task ID", "Status", "Observation", "Hypothesis", "Action", "Page", "Query", "Audience", "Owner", "Start date", "Review interval days", "Review date", "Success target", "Confidence", "Decision", "Evidence URL", "Notes"]];
for (const week of course.weeks) actionRows.push([
  `EXP-W${String(week.n).padStart(2, "0")}-001`, `${week.title} experiment`, week.n, "", "Planned", "", "", metrics[week.n].action, "", "", "", "", "", reviewDays[week.n - 1], "", "", "Low", "Wait", "", ""
]);

const evidenceRows = [["Evidence ID", "Name", "Week", "Related Task ID", "Related Experiment ID", "Type", "Date", "URL or file", "What this proves", "Status", "Notes"]];
for (const week of course.weeks) evidenceRows.push([
  `EVD-W${String(week.n).padStart(2, "0")}-001`, `${week.title} evidence`, week.n, "", `EXP-W${String(week.n).padStart(2, "0")}-001`, "Screenshot", "", "", "", "Needed", ""
]);

fs.writeFileSync(path.join(output, "notion-course-tasks.csv"), csv(taskRows));
fs.writeFileSync(path.join(output, "notion-kpi-tracker.csv"), csv(kpiRows));
fs.writeFileSync(path.join(output, "notion-actions-experiments.csv"), csv(actionRows));
fs.writeFileSync(path.join(output, "notion-evidence.csv"), csv(evidenceRows));

const guide = `# Outreach Recruitment — Notion course workspace\n\nImport the four CSV files as four full-page databases in Notion.\n\n## Recommended import order\n\n1. **Course Tasks** — import \`notion-course-tasks.csv\`\n2. **KPI Tracker** — import \`notion-kpi-tracker.csv\`\n3. **Actions & Experiments** — import \`notion-actions-experiments.csv\`\n4. **Evidence** — import \`notion-evidence.csv\`\n\n## Convert property types\n\n- Week, Impact, Effort, Review interval days: Number\n- Due date, Date, Start date, Review date: Date\n- Status, Priority, Track, KPI, Direction, Audience, Confidence, Decision, Type: Select\n- Evidence URL, Course URL, URL or file: URL\n- Task ID, KPI Record ID, Experiment ID, Evidence ID: Text (keep unique)\n\n## Create database relationships\n\nNotion cannot create relations during CSV import. After import, add these Relation properties manually:\n\n- Actions & Experiments → Course Tasks, matched using **Related Task ID**\n- Evidence → Course Tasks, matched using **Related Task ID**\n- Evidence → Actions & Experiments, matched using **Related Experiment ID**\n- KPI Tracker → Actions & Experiments, using a new relation named **Related Experiment**\n\nKeep the ID text columns after linking. They make future exports/imports safe even if task wording changes.\n\n## Recommended views\n\n### Course Tasks\n- Today: Status is not Complete and Due date is today or earlier\n- By week: board grouped by Week\n- Blocked: add Blocker select and filter where it is not empty\n- Portfolio: Status is Complete and Evidence URL is not empty\n\n### KPI Tracker\n- Current week: filter Week\n- Needs action: Confidence is Medium or High and Action is not empty\n- Waiting for data: Current value is empty\n\n### Actions & Experiments\n- Review queue: Review date is today or earlier and Status is Monitoring\n- Decisions: board grouped by Decision\n\n## Suggested formulas\n\nCreate a formula property **Priority Score** in Course Tasks:\n\n\`if(or(empty(prop("Impact")), empty(prop("Effort"))), 0, round(prop("Impact") * 20 / max(prop("Effort"), 1)))\`\n\nCreate a formula property **Change %** in KPI Tracker for metrics where higher is better:\n\n\`if(or(empty(prop("Previous value")), prop("Previous value") == 0), 0, round((prop("Current value") - prop("Previous value")) / prop("Previous value") * 1000) / 10)\`\n\nFor Average Position, use Previous value minus Current value instead.\n\n## Connection status\n\nThe CSV pack works immediately. A live two-way connection requires connecting the Notion integration, choosing the target page/databases, and approving write access.\n`;
fs.writeFileSync(path.join(output, "NOTION_IMPORT_GUIDE.md"), guide);
const packFiles = ["notion-course-tasks.csv", "notion-kpi-tracker.csv", "notion-actions-experiments.csv", "notion-evidence.csv", "NOTION_IMPORT_GUIDE.md"];
const archive = path.join(output, "outreach-notion-course-pack.zip");
if (fs.existsSync(archive)) fs.unlinkSync(archive);
execFileSync("zip", ["-j", "-q", archive, ...packFiles.map((file) => path.join(output, file))]);
console.log(`Created ${taskRows.length - 1} tasks, ${kpiRows.length - 1} KPI rows, ${actionRows.length - 1} experiments and ${evidenceRows.length - 1} evidence rows.`);
