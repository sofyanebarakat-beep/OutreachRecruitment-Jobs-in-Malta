(() => {
  "use strict";
  const SUPABASE_URL = "https://atcitaqyraeqngcsaeun.supabase.co";
  const SUPABASE_KEY = "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY";
  const LIMIT = 5;

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
    const filter = document.getElementById("opening-jobs-filter");
    if (!grid || !filter) return;
    const cards = cardsBySlug();
    const chosen = [...new Set(slugs)].filter((slug) => cards.has(slug)).slice(0, LIMIT);
    fallbackSlugs(cards).forEach((slug) => {
      if (chosen.length < LIMIT && !chosen.includes(slug)) chosen.push(slug);
    });
    if (!chosen.length) return;

    let section = document.getElementById("opening-featured-jobs");
    if (!section) {
      section = document.createElement("section");
      section.className = "opening-featured-section";
      section.id = "opening-featured-jobs";
      section.setAttribute("aria-labelledby", "opening-featured-title");
      filter.parentNode.insertBefore(section, filter);
    }
    section.innerHTML = `<div class="opening-featured-heading">
      <div><h2 id="opening-featured-title">Featured opportunities</h2>
      <p>${loadError ? "Showing highlighted open roles while the curated selection is unavailable." : "Five hand-picked roles to explore first."}</p></div>
      <span class="opening-featured-badge">Top 5 jobs</span>
    </div><div class="opening-featured-grid"></div>`;
    const featuredGrid = section.querySelector(".opening-featured-grid");
    chosen.forEach((slug) => {
      const clone = cards.get(slug).cloneNode(true);
      clone.removeAttribute("data-opening-job");
      clone.removeAttribute("data-job-slug");
      clone.removeAttribute("hidden");
      clone.classList.add("opening-job-card--gold");
      featuredGrid.appendChild(clone);
    });
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
        throw new Error("No saved five-job selection was found");
      }
      showFeatured(slugs, false);
    })
    .catch((error) => {
      console.error("Could not load curated featured jobs:", error);
      showFeatured(fallback, true);
    });
})();
