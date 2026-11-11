(() => {
  const carousel = document.querySelector("[data-team-hero]");
  if (!carousel) return;

  const slides = Array.from(carousel.querySelectorAll(".team-hero-slide"));
  const controls = carousel.querySelector(".team-hero-controls");
  const previous = carousel.querySelector("[data-team-hero-prev]");
  const next = carousel.querySelector("[data-team-hero-next]");
  const pause = carousel.querySelector("[data-team-hero-pause]");
  if (slides.length < 2 || !controls || !previous || !next || !pause) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let index = 0;
  let playing = !reducedMotion.matches;
  let timer;

  function show(nextIndex) {
    index = (nextIndex + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      slide.classList.toggle("is-active", i === index);
      slide.setAttribute("aria-hidden", i === index ? "false" : "true");
    });
  }

  function schedule() {
    window.clearTimeout(timer);
    if (!playing || document.hidden || carousel.matches(":hover") || carousel.contains(document.activeElement)) return;
    timer = window.setTimeout(() => {
      show(index + 1);
      schedule();
    }, 5000);
  }

  function updatePauseButton() {
    pause.textContent = playing ? "Ⅱ" : "▶";
    pause.setAttribute("aria-label", playing ? "Pause team slideshow" : "Play team slideshow");
  }

  previous.addEventListener("click", () => { show(index - 1); schedule(); });
  next.addEventListener("click", () => { show(index + 1); schedule(); });
  pause.addEventListener("click", () => {
    playing = !playing;
    updatePauseButton();
    schedule();
  });
  carousel.addEventListener("mouseenter", schedule);
  carousel.addEventListener("mouseleave", schedule);
  carousel.addEventListener("focusin", schedule);
  carousel.addEventListener("focusout", () => window.setTimeout(schedule, 0));
  document.addEventListener("visibilitychange", schedule);
  reducedMotion.addEventListener("change", (event) => {
    if (event.matches) playing = false;
    updatePauseButton();
    schedule();
  });

  updatePauseButton();
  controls.hidden = false;
  schedule();
})();
