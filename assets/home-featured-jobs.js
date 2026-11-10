(() => {
  "use strict";
  const SUPABASE_URL = "https://atcitaqyraeqngcsaeun.supabase.co";
  const SUPABASE_KEY = "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY";
  const LIMIT = 6;
  const grid = document.querySelector(".or-open-roles .opening-jobs-centered-grid");
  if (!grid) return;

  async function load() {
    const sel = await fetch(`${SUPABASE_URL}/rest/v1/jobs_featured?id=eq.current&select=slugs`, {
      headers: { apikey: SUPABASE_KEY },
      cache: "no-store",
    });
    if (!sel.ok) throw new Error("featured selection unavailable");
    const slugs = (await sel.json())[0]?.slugs;
    if (!Array.isArray(slugs) || !slugs.length) throw new Error("no featured selection");

    const page = await fetch("/jobs/", { cache: "no-store" });
    if (!page.ok) throw new Error("jobs page unavailable");
    const doc = new DOMParser().parseFromString(await page.text(), "text/html");
    const bySlug = new Map(
      [...doc.querySelectorAll("[data-opening-job][data-job-slug]")].map((c) => [c.dataset.jobSlug, c])
    );
    const cards = slugs
      .map((s) => bySlug.get(s))
      .filter((c) => c && !c.querySelector(".opening-job-link--closed"))
      .slice(0, LIMIT);
    if (!cards.length) throw new Error("no matching jobs");

    grid.replaceChildren(
      ...cards.map((c) => {
        const card = document.importNode(c, true);
        card.classList.add("opening-job-card--centered");
        card.dataset.featured = "true";
        return card;
      })
    );
  }

  load().catch((e) => console.warn("Homepage featured jobs: using built-in list.", e));
})();
