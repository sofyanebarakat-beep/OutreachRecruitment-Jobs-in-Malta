const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const listeners = {};
const events = [];
const schema = {
  "@type": "JobPosting",
  title: "Auditor Doctor",
  identifier: { value: "auditor-doctor" },
  occupationalCategory: "Finance & Accounting",
  jobLocation: { address: { addressLocality: "Floriana", addressCountry: "MT" } },
};
const frame = {
  getAttribute(name) {
    return name === "data-src" ? "https://outreach-recruitment-agency.careers-page.com/jobs/external-123/apply" : "";
  },
};
const document = {
  readyState: "complete",
  addEventListener(type, callback) { listeners[type] = callback; },
  querySelectorAll(selector) {
    if (selector === 'script[type="application/ld+json"]') return [{ textContent: JSON.stringify(schema) }];
    if (selector === ".w-form") return [];
    return [];
  },
  querySelector(selector) {
    if (selector === "iframe.outreach-apply-frame") return frame;
    if (selector === ".job-header-meta .job-meta-item") return { textContent: "Finance & Accounting" };
    if (selector === 'iframe[src*="outreachrecruitment.eu/support"]') return {};
    if (selector === "h1") return { textContent: "Auditor Doctor" };
    return null;
  },
  getElementById() { return null; },
};
const window = {
  addEventListener(type, callback) { listeners[type] = callback; },
  gtag(command, name, params) { events.push({ command, name, params }); },
};
const context = {
  document,
  window,
  location: { pathname: "/jobs/auditor-doctor/", href: "https://outreachrecruitment.net/jobs/auditor-doctor/" },
  MutationObserver: function () {},
  getComputedStyle() { return { display: "block" }; },
  HTMLFormElement: function () {},
  Object,
  Array,
  JSON,
  RegExp,
  String,
};

vm.runInNewContext(fs.readFileSync("assets/analytics-events.js", "utf8"), context);

listeners.message({ origin: "https://outreach-recruitment-agency.careers-page.com", data: { success: true } });
assert.equal(events.length, 1);
assert.equal(events[0].name, "apply_click");
assert.equal(events[0].params.job_title, "Auditor Doctor");
assert.equal(events[0].params.job_id, "auditor-doctor");
assert.equal(events[0].params.job_category, "Finance & Accounting");
assert.equal(events[0].params.job_location, "Floriana, MT");
assert.equal(events[0].params.application_stage, "submitted");

listeners.message({ origin: "https://outreach-recruitment-agency.careers-page.com", data: { success: true } });
assert.equal(events.length, 1, "application success must be deduplicated");

listeners.message({ origin: "https://outreachrecruitment.eu", data: { type: "employer_form_success", success: true } });
assert.equal(events.length, 2);
assert.equal(events[1].name, "employer_lead_submit");
assert.equal(events[1].params.lead_type, "employer_recruitment_enquiry");
assert.equal(Object.values(events[1].params).some((value) => /@/.test(String(value))), false, "event must not contain email/PII");

listeners.message({ origin: "https://example.com", data: { type: "employer_form_success", success: true } });
assert.equal(events.length, 2, "untrusted origins must be ignored");

console.log("analytics-events tests passed");
