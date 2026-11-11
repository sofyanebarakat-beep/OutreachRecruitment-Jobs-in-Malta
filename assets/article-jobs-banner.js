(() => {
  const banners = document.querySelectorAll(".article-jobs-banner");
  if (!banners.length) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function countUp(element) {
    const target = Number(element.dataset.countUp);
    if (!Number.isFinite(target)) return;
    if (reducedMotion.matches) {
      element.textContent = `+${target}`;
      return;
    }

    const duration = 1100;
    const startedAt = performance.now();

    function update(now) {
      const progress = Math.min((now - startedAt) / duration, 1);
      const eased = 1 - (1 - progress) ** 3;
      element.textContent = `+${Math.round(target * eased)}`;
      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = `+${target}`;
        element.closest(".article-jobs-banner-count")?.classList.add("is-counted");
      }
    }

    element.textContent = "+0";
    requestAnimationFrame(update);
  }

  if (!("IntersectionObserver" in window)) {
    for (const banner of banners) {
      banner.classList.add("is-visible");
      const counter = banner.querySelector("[data-count-up]");
      if (counter) countUp(counter);
    }
    return;
  }

  const observer = new IntersectionObserver((entries, currentObserver) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;

      const banner = entry.target;
      banner.classList.add("is-visible");
      const counter = banner.querySelector("[data-count-up]");
      if (counter) countUp(counter);
      currentObserver.unobserve(banner);
    }
  }, { threshold: 0.1 });

  for (const banner of banners) observer.observe(banner);
})();
