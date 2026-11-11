(() => {
  const carousel = document.querySelector("[data-team-carousel]");
  if (!carousel) return;

  const track = carousel.querySelector("[data-team-carousel-track]");
  const previous = carousel.querySelector("[data-team-carousel-prev]");
  const next = carousel.querySelector("[data-team-carousel-next]");
  const viewport = carousel.querySelector(".or-team-carousel-viewport");
  if (!track || !previous || !next || !viewport) return;

  const items = Array.from(track.children);
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let visibleCount = 0;
  let index = 0;
  let timer;
  let isPaused = false;

  function currentVisibleCount() {
    return parseInt(getComputedStyle(carousel).getPropertyValue("--team-visible"), 10) || 1;
  }

  function positionTrack(animate = true) {
    const firstItem = track.children[0];
    if (!firstItem) return;
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    const offset = firstItem.getBoundingClientRect().width + gap;
    track.style.transition = animate ? "" : "none";
    track.style.transform = `translateX(${-index * offset}px)`;
    if (!animate) {
      requestAnimationFrame(() => {
        track.style.transition = "";
      });
    }
  }

  function rebuild() {
    const newVisibleCount = currentVisibleCount();
    if (newVisibleCount === visibleCount && track.children.length) {
      positionTrack(false);
      return;
    }
    visibleCount = newVisibleCount;
    track.replaceChildren(...items);

    const leadingClones = items.slice(-visibleCount).map((item) => item.cloneNode(true));
    const trailingClones = items.slice(0, visibleCount).map((item) => item.cloneNode(true));
    for (const clone of [...leadingClones, ...trailingClones]) {
      clone.setAttribute("aria-hidden", "true");
      clone.dataset.carouselClone = "true";
    }
    track.prepend(...leadingClones);
    track.append(...trailingClones);
    index = visibleCount;
    positionTrack(false);
  }

  function move(direction) {
    index += direction;
    positionTrack();
  }

  function handleTransitionEnd(event) {
    if (event.target !== track) return;
    const firstRealItem = visibleCount;
    const afterLastRealItem = firstRealItem + items.length;
    if (index >= afterLastRealItem) {
      index = firstRealItem;
      positionTrack(false);
    } else if (index < firstRealItem) {
      index = afterLastRealItem - 1;
      positionTrack(false);
    }
  }

  function stopTimer() {
    window.clearTimeout(timer);
    timer = undefined;
  }

  function scheduleNext() {
    stopTimer();
    if (isPaused || reducedMotion.matches || document.hidden) return;
    timer = window.setTimeout(() => {
      move(1);
      scheduleNext();
    }, 5000);
  }

  previous.addEventListener("click", () => {
    move(-1);
    scheduleNext();
  });
  next.addEventListener("click", () => {
    move(1);
    scheduleNext();
  });
  track.addEventListener("transitionend", handleTransitionEnd);
  carousel.addEventListener("mouseenter", () => {
    isPaused = true;
    stopTimer();
  });
  carousel.addEventListener("mouseleave", () => {
    isPaused = false;
    scheduleNext();
  });
  carousel.addEventListener("focusin", () => {
    isPaused = true;
    stopTimer();
  });
  carousel.addEventListener("focusout", (event) => {
    if (!carousel.contains(event.relatedTarget)) {
      isPaused = false;
      scheduleNext();
    }
  });
  document.addEventListener("visibilitychange", scheduleNext);
  reducedMotion.addEventListener?.("change", scheduleNext);

  let resizeFrame;
  new ResizeObserver(() => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(rebuild);
  }).observe(viewport);

  rebuild();
  scheduleNext();
})();
