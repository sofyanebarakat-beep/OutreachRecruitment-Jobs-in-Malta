const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class TestElement {
  constructor(tagName, innerHTML) {
    this.tagName = tagName.toUpperCase();
    this.innerHTML = innerHTML;
    this.textContent = innerHTML.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
    this.children = [...innerHTML.matchAll(/<([a-z][\w-]*)\b[^>]*>/gi)].map((match) => ({ tagName: match[1].toUpperCase() }));
    this.firstElementChild = this.children[0] || null;
  }
  closest() { return null; }
}

class TestDOMParser {
  parseFromString(html) {
    const elements = [...html.matchAll(/<(h[1-5]|p|li)\b[^>]*>([\s\S]*?)<\/\1>/gi)]
      .map((match) => new TestElement(match[1], match[2]));
    return { body: { firstChild: { querySelectorAll: () => elements } } };
  }
}

const window = {};
const factsById = {};
vm.runInNewContext(fs.readFileSync("admin/marketing.js", "utf8"), {
  window,
  DOMParser: TestDOMParser,
  fetch: async (url) => ({ json: async () => factsById[url.match(/[0-9a-f-]{36}/i)[0]] }),
  localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
});

const job = { title: "Software Developer", slug: "software-developer", category: "IT & Technology" };
const description = (offer) => `<p>Our client is looking for a Software Developer.</p>
  <h2>Responsibilities</h2><ul><li>Build new product features.</li><li>Collaborate with the engineering team.</li>
  <li>Support product testing and troubleshooting.</li></ul>
  <h2>Requirements</h2><ul><li>Experience building web applications.</li><li>Strong communication skills.</li></ul>
  ${offer}`;

(async () => {
  const withOfferId = "12345678-1234-1234-1234-123456789abc";
  factsById[withOfferId] = {
    description_html: description("<h2>What Our Client Offers</h2><ul><li>Hybrid working.</li><li>Training and development.</li></ul>"),
    city: "St. Julian's",
    employment_type: "Full-time",
    work_mode: "Hybrid",
    salary: { min: 32000, max: 35000, unit: "YEAR" },
  };
  const withOffer = await window.MarketingKit.jobValues({
    ...job,
    location: "St. Julian's, Malta",
    apply_url: `https://careers.example/${withOfferId}`,
  });
  assert.match(withOffer.intro, /About this role/);
  assert.match(withOffer.intro, /build new product features/i);
  assert.match(withOffer.intro, /What Our Client Offers/);
  assert.match(withOffer.intro, /Hybrid working/);
  assert.match(withOffer.intro, /Training and development/);
  assert.match(withOffer.hook, /Software Developer/);
  assert.doesNotMatch(withOffer.hook, /St\. Julian's|\bin\b/);
  assert.match(withOffer.job_highlights, /€32,000–€35,000 per year/);
  assert.match(withOffer.job_highlights, /Hybrid/);
  assert.match(withOffer.intro, /Key responsibilities include: Build new product features; Collaborate with the engineering team; Support product testing and troubleshooting/);
  assert.ok(withOffer.intro.match(/🔎 \*\*About this role:\*\*([\s\S]*?)(?=\n\n|$)/)[1].length > 100);
  assert.doesNotMatch(withOffer.intro, /A good fit if/);
  assert.match(withOffer.apply_prompt, /Apply|application/);

  const withoutOfferId = "abcdef12-1234-1234-1234-123456789abc";
  factsById[withoutOfferId] = { description_html: description("") };
  const withoutOffer = await window.MarketingKit.jobValues({ ...job, apply_url: `https://careers.example/${withoutOfferId}` });
  assert.match(withoutOffer.intro, /About this role/);
  assert.doesNotMatch(withoutOffer.intro, /What Our Client Offers/);
  assert.doesNotMatch(withoutOffer.intro, /undefined|null/);
  assert.equal(withoutOffer.job_highlights, "");
  assert.doesNotMatch(withoutOffer.job_highlights, /Competitive salary/);
  assert.doesNotMatch(withoutOffer.intro, /A good fit if/);

  const noRequirementsId = "abcdef12-9876-1234-1234-123456789abc";
  factsById[noRequirementsId] = { description_html: "<p>Our client is looking for a Software Developer.</p>" };
  const noRequirements = await window.MarketingKit.jobValues({
    ...job,
    apply_url: `https://careers.example/${noRequirementsId}`,
  });
  assert.doesNotMatch(noRequirements.intro, /A good fit if/);

  const jobSlugs = ["developer-one", "developer-two", "developer-three", "developer-four", "developer-five"];
  const variants = await Promise.all(jobSlugs.map((slug) => window.MarketingKit.jobValues({ ...job, slug }, null)));
  const hooks = new Set(variants.map((values) => values.hook));
  const applyPrompts = new Set(variants.map((values) => values.apply_prompt));
  assert.ok(hooks.size > 1, "different jobs rotate through distinct role-specific hooks");
  assert.ok(applyPrompts.size > 1, "different jobs rotate through distinct application prompts");

  console.log("admin marketing caption tests passed");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
