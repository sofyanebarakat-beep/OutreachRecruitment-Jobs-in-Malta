/* Outreach Recruitment — select the three jobs highlighted above the job board. */
(() => {
  "use strict";
  const CFG = window.ADMIN_CONFIG || {};
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const today = () => {
    const d = new Date();
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  };

  function isOpen(job) {
    const status = String(job.status || "active").toLowerCase();
    return status !== "closed" && status !== "expired" && (job.valid_through || "9999-12-31") >= today();
  }

  function fallbackSlugs(jobs) {
    return [...jobs]
      .sort((a, b) => Number(Boolean(b.featured)) - Number(Boolean(a.featured)) || String(b.date).localeCompare(String(a.date)))
      .slice(0, 3)
      .map((job) => job.slug);
  }

  window.renderFeaturedJobs = async function (view) {
    view.innerHTML = `<section class="card hero"><div class="kicker">Marketing · Jobs page</div><h1>Featured jobs</h1>
      <p>Choose exactly three open jobs to display in the gold Featured Opportunities section at the top of <a href="/jobs/" target="_blank" rel="noopener">/jobs/</a>.</p></section>
      <section class="card" id="featured-job-manager"><p class="muted" role="status">Loading open jobs and the current selection…</p></section>`;

    const manager = document.querySelector("#featured-job-manager");
    try {
      const store = window.AdminStore;
      if (!store || store.mode !== "supabase" || !store.sb) {
        throw new Error("Connect to the shared Supabase admin to save selections that appear on the public jobs page. Browser-only mode cannot publish changes.");
      }
      const response = await fetch(CFG.JOBS_REGISTRY, { cache: "no-cache" });
      if (!response.ok) throw new Error(`Could not load the job registry (HTTP ${response.status}).`);
      const jobs = (await response.json()).filter(isOpen).sort((a, b) => String(b.date).localeCompare(String(a.date)));
      if (jobs.length < 3) throw new Error(`Only ${jobs.length} open jobs are available; three are required.`);

      const { data, error } = await store.sb.from("jobs_featured").select("slugs").eq("id", "current").maybeSingle();
      if (error) throw new Error(`Could not load the featured-job selection: ${error.message}`);
      const openSlugs = new Set(jobs.map((job) => job.slug));
      let selected = [...new Set((data?.slugs || []).filter((slug) => openSlugs.has(slug)))].slice(0, 3);
      if (selected.length < 3) {
        selected = [...selected, ...fallbackSlugs(jobs).filter((slug) => !selected.includes(slug))].slice(0, 3);
      }

      manager.innerHTML = `
        <div class="section-title"><h2>Choose three jobs</h2><strong id="featured-job-count" aria-live="polite"></strong></div>
        <p class="muted">Selected roles appear in the order shown below. To change the order, unselect a role and select it again.</p>
        <div class="grid c2" style="align-items:end">
          <label>Find an open job<input id="featured-job-search" type="search" placeholder="Search title, category, or location"></label>
          <div><strong>Selected order</strong><ol id="featured-job-selected" class="featured-selected-list"></ol></div>
        </div>
        <div id="featured-job-options" class="featured-job-options" aria-label="Open jobs"></div>
        <div class="section-title" style="margin-top:16px">
          <p id="featured-job-status" class="msg" role="status">Choose three open jobs, then save.</p>
          <button type="button" class="btn primary" id="featured-job-save" disabled>Save featured jobs</button>
        </div>`;

      const options = manager.querySelector("#featured-job-options");
      const count = manager.querySelector("#featured-job-count");
      const selectedList = manager.querySelector("#featured-job-selected");
      const save = manager.querySelector("#featured-job-save");
      const status = manager.querySelector("#featured-job-status");
      const search = manager.querySelector("#featured-job-search");

      options.innerHTML = jobs.map((job) => {
        const searchable = `${job.title} ${job.category} ${job.location}`.toLowerCase();
        return `<label class="featured-job-option" data-search="${esc(searchable)}">
          <input type="checkbox" value="${esc(job.slug)}" ${selected.includes(job.slug) ? "checked" : ""}>
          <span><strong>${esc(job.title)}</strong><small>${esc(job.category)} · ${esc(job.location)}</small></span>
        </label>`;
      }).join("");

      function updateSelection() {
        selectedList.innerHTML = selected.map((slug, index) => {
          const job = jobs.find((item) => item.slug === slug);
          return `<li><span class="featured-order">${index + 1}</span> ${esc(job?.title || slug)}</li>`;
        }).join("");
        count.textContent = `${selected.length} of 3 selected`;
        save.disabled = selected.length !== 3;
        if (selected.length === 3) status.textContent = "Ready to publish. Saving updates the public page without a site rebuild.";
      }

      options.addEventListener("change", (event) => {
        const input = event.target;
        if (!(input instanceof HTMLInputElement) || input.type !== "checkbox") return;
        if (input.checked) {
          if (selected.length === 3) {
            input.checked = false;
            status.textContent = "Select no more than three jobs. Uncheck one before choosing another.";
            status.className = "msg error";
            return;
          }
          selected.push(input.value);
        } else {
          selected = selected.filter((slug) => slug !== input.value);
        }
        status.className = "msg";
        updateSelection();
      });

      search.addEventListener("input", () => {
        const query = search.value.trim().toLowerCase();
        options.querySelectorAll(".featured-job-option").forEach((option) => {
          option.hidden = !option.dataset.search.includes(query);
        });
      });

      save.addEventListener("click", async () => {
        if (selected.length !== 3) return;
        save.disabled = true;
        status.className = "msg";
        status.textContent = "Saving featured jobs…";
        try {
          const { error: saveError } = await store.sb.from("jobs_featured")
            .upsert({ id: "current", slugs: selected }, { onConflict: "id" });
          if (saveError) throw saveError;
          status.className = "msg ok";
          status.textContent = "Saved. The gold Featured Opportunities section on /jobs/ now uses these three jobs.";
        } catch (e) {
          status.className = "msg error";
          status.textContent = `Save failed: ${e.message || e}`;
        } finally {
          save.disabled = selected.length !== 3;
        }
      });

      updateSelection();
    } catch (e) {
      manager.innerHTML = `<h2>Featured jobs unavailable</h2><p class="msg error" role="alert">${esc(e.message || e)}</p>
        <p class="muted">Ensure the featured-jobs database migration has been applied and that you are signed in as an admin.</p>`;
    }
  };
})();
