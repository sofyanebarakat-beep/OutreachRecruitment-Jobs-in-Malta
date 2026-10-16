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
  <h2>Responsibilities</h2><ul><li>Build new product features.</li><li>Collaborate with the engineering team.</li></ul>
  ${offer}`;

(async () => {
  const withOfferId = "12345678-1234-1234-1234-123456789abc";
  factsById[withOfferId] = {
    description_html: description("<h2>What Our Client Offers</h2><ul><li>Hybrid working.</li><li>Training and development.</li></ul>"),
  };
  const withOffer = await window.MarketingKit.jobValues({ ...job, apply_url: `https://careers.example/${withOfferId}` });
  assert.match(withOffer.intro, /About this role/);
  assert.match(withOffer.intro, /build new product features/i);
  assert.match(withOffer.intro, /What Our Client Offers/);
  assert.match(withOffer.intro, /Hybrid working/);
  assert.match(withOffer.intro, /Training and development/);

  const withoutOfferId = "abcdef12-1234-1234-1234-123456789abc";
  factsById[withoutOfferId] = { description_html: description("") };
  const withoutOffer = await window.MarketingKit.jobValues({ ...job, apply_url: `https://careers.example/${withoutOfferId}` });
  assert.match(withoutOffer.intro, /About this role/);
  assert.doesNotMatch(withoutOffer.intro, /What Our Client Offers/);
  assert.doesNotMatch(withoutOffer.intro, /undefined|null/);

  console.log("admin marketing caption tests passed");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
