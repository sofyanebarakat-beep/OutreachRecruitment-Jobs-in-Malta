# Outreach Recruitment — Notion course workspace

Import the four CSV files as four full-page databases in Notion.

## Recommended import order

1. **Course Tasks** — import `notion-course-tasks.csv`
2. **KPI Tracker** — import `notion-kpi-tracker.csv`
3. **Actions & Experiments** — import `notion-actions-experiments.csv`
4. **Evidence** — import `notion-evidence.csv`

## Convert property types

- Week, Impact, Effort, Review interval days: Number
- Due date, Date, Start date, Review date: Date
- Status, Priority, Track, KPI, Direction, Audience, Confidence, Decision, Type: Select
- Evidence URL, Course URL, URL or file: URL
- Task ID, KPI Record ID, Experiment ID, Evidence ID: Text (keep unique)

## Create database relationships

Notion cannot create relations during CSV import. After import, add these Relation properties manually:

- Actions & Experiments → Course Tasks, matched using **Related Task ID**
- Evidence → Course Tasks, matched using **Related Task ID**
- Evidence → Actions & Experiments, matched using **Related Experiment ID**
- KPI Tracker → Actions & Experiments, using a new relation named **Related Experiment**

Keep the ID text columns after linking. They make future exports/imports safe even if task wording changes.

## Recommended views

### Course Tasks
- Today: Status is not Complete and Due date is today or earlier
- By week: board grouped by Week
- Blocked: add Blocker select and filter where it is not empty
- Portfolio: Status is Complete and Evidence URL is not empty

### KPI Tracker
- Current week: filter Week
- Needs action: Confidence is Medium or High and Action is not empty
- Waiting for data: Current value is empty

### Actions & Experiments
- Review queue: Review date is today or earlier and Status is Monitoring
- Decisions: board grouped by Decision

## Suggested formulas

Create a formula property **Priority Score** in Course Tasks:

`if(or(empty(prop("Impact")), empty(prop("Effort"))), 0, round(prop("Impact") * 20 / max(prop("Effort"), 1)))`

Create a formula property **Change %** in KPI Tracker for metrics where higher is better:

`if(or(empty(prop("Previous value")), prop("Previous value") == 0), 0, round((prop("Current value") - prop("Previous value")) / prop("Previous value") * 1000) / 10)`

For Average Position, use Previous value minus Current value instead.

## Connection status

The CSV pack works immediately. A live two-way connection requires connecting the Notion integration, choosing the target page/databases, and approving write access.
