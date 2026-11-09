(() => {
  "use strict";
  const SUPABASE_URL = "https://atcitaqyraeqngcsaeun.supabase.co";
  const SUPABASE_KEY = "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY";
  const LIMIT = 6;

  function cardsBySlug() {
    return new Map(
      [...document.querySelectorAll("#opening-jobs-grid [data-opening-job][data-job-slug]")]
        .map((card) => [card.dataset.jobSlug, card])
        .filter(([slug]) => slug)
    );
  }

  function fallbackSlugs(cards) {
    const rows = [...cards.values()];
    return rows
      .sort((a, b) => Number(b.dataset.featured === "true") - Number(a.dataset.featured === "true")
        || String(b.dataset.date).localeCompare(String(a.dataset.date)))
      .slice(0, LIMIT)
      .map((card) => card.dataset.jobSlug);
  }

  function showFeatured(slugs, loadError) {
    const grid = document.getElementById("opening-jobs-grid");
    if (!grid) return;
    const cards = cardsBySlug();
    const chosen = [...new Set(slugs)].filter((slug) => cards.has(slug)).slice(0, LIMIT);
    fallbackSlugs(cards).forEach((slug) => {
      if (chosen.length < LIMIT && !chosen.includes(slug)) chosen.push(slug);
    });
    if (!chosen.length) return;

    cards.forEach((card, slug) => {
      card.dataset.featured = String(chosen.includes(slug));
      card.classList.remove("opening-job-card--gold");
      card.querySelector(".opening-featured-label")?.remove();
    });
    chosen.forEach((slug) => {
      const card = cards.get(slug);
      card.classList.add("opening-job-card--gold");
      const link = card.querySelector(".opening-job-link");
      if (link && !link.querySelector(".opening-featured-label")) {
        const label = document.createElement("span");
        label.className = "opening-featured-label";
        label.textContent = loadError ? "Featured" : "Featured role";
        link.insertBefore(label, link.firstChild);
      }
    });
    const chosenCards = new Set(chosen.map((slug) => cards.get(slug)));
    const firstOtherCard = [...grid.children].find((child) => !chosenCards.has(child)) || null;
    chosen.forEach((slug) => grid.insertBefore(cards.get(slug), firstOtherCard));

    const featuredTab = document.querySelector('[data-opening-tab="featured"]');
    const featuredCount = featuredTab?.querySelector("span");
    if (featuredCount) featuredCount.textContent = String(chosen.length);
    if (featuredTab?.classList.contains("is-active")) featuredTab.click();
  }

  async function loadSelection() {
    const url = `${SUPABASE_URL}/rest/v1/jobs_featured?id=eq.current&select=slugs`;
    const response = await fetch(url, {
      headers: { apikey: SUPABASE_KEY },
      cache: "no-store",
    });
    if (!response.ok) throw new Error(`Featured selection request failed (HTTP ${response.status})`);
    const rows = await response.json();
    if (!Array.isArray(rows)) throw new Error("Featured selection response was invalid");
    return rows[0]?.slugs;
  }

  const cards = cardsBySlug();
  if (!cards.size) return;
  const fallback = fallbackSlugs(cards);
  showFeatured(fallback, false);
  loadSelection()
    .then((slugs) => {
      if (!Array.isArray(slugs) || slugs.length !== LIMIT) {
        throw new Error("No saved six-job selection was found");
      }
      showFeatured(slugs, false);
    })
    .catch((error) => {
      console.error("Could not load curated featured jobs:", error);
      showFeatured(fallback, true);
    });
})();
