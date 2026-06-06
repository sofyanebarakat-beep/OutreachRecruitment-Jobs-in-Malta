(function () {
  var doc = document;
  var root = doc.documentElement;

  root.classList.add('or-enhanced');

  function all(selector, scope) {
    return Array.prototype.slice.call((scope || doc).querySelectorAll(selector));
  }

  function closest(element, selector) {
    while (element && element !== doc) {
      if (element.matches && element.matches(selector)) return element;
      element = element.parentNode;
    }
    return null;
  }

  function initReveals() {
    var items = all('[data-gsap-scroll], .heading-h1, .heading-h2, .heading-h3, .polaroid-card');
    if (!items.length) return;

    if (!('IntersectionObserver' in window)) {
      items.forEach(function (item) { item.classList.add('or-in-view'); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('or-in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    items.forEach(function (item, index) {
      item.style.setProperty('--or-delay', Math.min(index % 8, 7) * 45 + 'ms');
      observer.observe(item);
    });
  }

  function initNav() {
    var currentPath = window.location.pathname.replace(/\/$/, '') || '/';
    all('.navigation-link, .nav-item, .nav-logo-link').forEach(function (link) {
      var href = link.getAttribute('href');
      if (!href || href.charAt(0) !== '/') return;
      var linkPath = href.replace(/\/$/, '') || '/';
      var isCurrent = linkPath === currentPath;
      link.classList.toggle('w--current', isCurrent);
      if (isCurrent) {
        link.setAttribute('aria-current', 'page');
      } else {
        link.removeAttribute('aria-current');
      }
    });

    all('.w-nav').forEach(function (nav) {
      var button = nav.querySelector('.w-nav-button');
      var menu = nav.querySelector('.w-nav-menu');
      var overlay = nav.querySelector('.navigation-overlay');
      if (!button || !menu) return;

      function setOpen(open) {
        nav.classList.toggle('or-nav-open', open);
        button.classList.toggle('w--open', open);
        menu.classList.toggle('w--open', open);
        if (overlay) overlay.classList.toggle('w--open', open);
        button.setAttribute('aria-expanded', open ? 'true' : 'false');
      }

      button.setAttribute('aria-expanded', 'false');
      button.addEventListener('click', function () {
        setOpen(!nav.classList.contains('or-nav-open'));
      });
      if (overlay) overlay.addEventListener('click', function () { setOpen(false); });
      all('a', menu).forEach(function (link) {
        link.addEventListener('click', function () { setOpen(false); });
      });
    });

    all('.w-dropdown').forEach(function (dropdown) {
      var toggle = dropdown.querySelector('.w-dropdown-toggle');
      var panel = dropdown.querySelector('.w-dropdown-list');
      if (!toggle || !panel) return;

      function setOpen(open) {
        dropdown.classList.toggle('w--open', open);
        toggle.classList.toggle('w--open', open);
        panel.classList.toggle('w--open', open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      }

      toggle.setAttribute('aria-expanded', 'false');
      dropdown.addEventListener('mouseenter', function () { setOpen(true); });
      dropdown.addEventListener('mouseleave', function () { setOpen(false); });
      toggle.addEventListener('click', function (event) {
        event.preventDefault();
        setOpen(!dropdown.classList.contains('w--open'));
      });
    });
  }

  function initSliders() {
    all('.w-slider').forEach(function (slider) {
      var slides = all('.w-slide:not(.is-clone)', slider);
      if (slides.length < 2) return;
      var index = Math.max(0, slides.findIndex(function (slide) {
        return slide.classList.contains('w-active');
      }));
      var delay = Number(slider.getAttribute('data-delay')) || 3500;
      var prev = slider.querySelector('.w-slider-arrow-left');
      var next = slider.querySelector('.w-slider-arrow-right');

      function show(nextIndex) {
        index = (nextIndex + slides.length) % slides.length;
        slides.forEach(function (slide, slideIndex) {
          var active = slideIndex === index;
          slide.classList.toggle('or-slide-active', active);
          slide.classList.toggle('w-active', active);
          slide.setAttribute('aria-hidden', active ? 'false' : 'true');
        });
      }

      show(index);
      if (prev) prev.addEventListener('click', function () { show(index - 1); });
      if (next) next.addEventListener('click', function () { show(index + 1); });
      if (slider.getAttribute('data-autoplay') === 'true') {
        window.setInterval(function () { show(index + 1); }, delay);
      }
    });
  }

  function initFeatureSliders() {
    all('.feature-slider').forEach(function (slider) {
      function removeClones() {
        all('.w-slide.is-clone', slider).forEach(function (clone) {
          clone.remove();
        });
      }

      removeClones();

      if ('MutationObserver' in window) {
        var observer = new MutationObserver(removeClones);
        observer.observe(slider, { childList: true, subtree: true });
      }
    });
  }

  function initMarquees() {
    all('.marquee-track, [data-marquee="left"], [data-marquee="right"], [data-marquee="track"]').forEach(function (track) {
      if (track.classList.contains('or-marquee-ready')) return;
      var lists = all(':scope > .marquee-list', track);
      if (lists.length === 1) {
        track.appendChild(lists[0].cloneNode(true));
      }
      track.classList.add('or-marquee-ready');

      var direction = track.getAttribute('data-marquee');
      if (track.classList.contains('right') || direction === 'right') {
        track.classList.add('or-marquee-right');
      } else {
        track.classList.add('or-marquee-left');
      }

      var wrap = closest(track, '[data-marquee-speed]');
      if (wrap) {
        var speed = Number(wrap.getAttribute('data-marquee-speed'));
        if (speed > 0) track.style.setProperty('--or-marquee-duration', speed + 's');
      }
    });
  }

  function initParallax() {
    var items = all('[data-parallax], .case-study-compact-card-content.floating, .quote-block.floating');
    if (!items.length) return;

    var ticking = false;
    function update() {
      ticking = false;
      var height = window.innerHeight || 1;
      items.forEach(function (item) {
        var rect = item.getBoundingClientRect();
        if (rect.bottom < -120 || rect.top > height + 120) return;
        var strengthName = item.getAttribute('data-parallax') || 'soft';
        var strength = strengthName === 'strong' ? 34 : strengthName === 'medium' ? 22 : 14;
        var progress = (rect.top + rect.height / 2 - height / 2) / height;
        item.style.setProperty('--or-parallax-y', (progress * -strength).toFixed(2) + 'px');
      });
    }

    function requestUpdate() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    window.addEventListener('scroll', requestUpdate, { passive: true });
    window.addEventListener('resize', requestUpdate);
    update();
  }

  function initHomeSlides() {
    var slides = all('.home-test-slide');
    if (slides.length < 2) return;
    var index = Math.max(0, slides.findIndex(function (slide) {
      return slide.classList.contains('is-active');
    }));

    function show(nextIndex) {
      index = (nextIndex + slides.length) % slides.length;
      slides.forEach(function (slide, slideIndex) {
        slide.classList.toggle('is-active', slideIndex === index);
      });
    }

    show(index);
    window.setInterval(function () { show(index + 1); }, 4500);
  }

  function initTabs() {
    all('.w-tabs').forEach(function (tabs) {
      var links = all('.w-tab-link', tabs);
      var panes = all('.w-tab-pane', tabs);
      if (!links.length || !panes.length) return;

      function activate(name) {
        links.forEach(function (link) {
          link.classList.toggle('w--current', link.getAttribute('data-w-tab') === name);
        });
        panes.forEach(function (pane) {
          pane.classList.toggle('w--tab-active', pane.getAttribute('data-w-tab') === name);
        });
      }

      links.forEach(function (link) {
        link.addEventListener('click', function (event) {
          event.preventDefault();
          activate(link.getAttribute('data-w-tab'));
        });
      });
      activate((links.find(function (link) { return link.classList.contains('w--current'); }) || links[0]).getAttribute('data-w-tab'));
    });
  }

  function initFaqs() {
    all('.faq-item').forEach(function (item) {
      var top = item.querySelector('.faq-item-top');
      if (!top) return;
      top.addEventListener('click', function () {
        item.classList.toggle('or-open');
      });
    });
  }

  function initPreviewSwitchers() {
    all('.frame, .careers-sector-frame').forEach(function (frame) {
      var items = all('.preview-item', frame);
      var media = all('.preview-media-item', frame);
      if (!items.length || !media.length) return;

      function activate(index) {
        items.forEach(function (item, itemIndex) {
          item.classList.toggle('is-active', itemIndex === index);
          item.setAttribute('aria-selected', itemIndex === index ? 'true' : 'false');
        });
        media.forEach(function (item, itemIndex) {
          item.classList.toggle('is-active', itemIndex === index);
        });
      }

      items.forEach(function (item, index) {
        item.addEventListener('click', function () { activate(index); });
        item.addEventListener('keydown', function (event) {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            activate(index);
          }
        });
      });
      activate(Math.max(0, items.findIndex(function (item) { return item.classList.contains('is-active'); })));
    });
  }

  function initCounters() {
    all('[data-count-to]').forEach(function (counter) {
      var target = Number(counter.getAttribute('data-count-to')) || 0;
      var started = false;

      function run() {
        if (started) return;
        started = true;
        var start = performance.now();
        function tick(now) {
          var progress = Math.min((now - start) / 900, 1);
          counter.textContent = String(Math.round(target * progress));
          if (progress < 1) window.requestAnimationFrame(tick);
        }
        window.requestAnimationFrame(tick);
      }

      if (!('IntersectionObserver' in window)) {
        run();
        return;
      }

      var observer = new IntersectionObserver(function (entries) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) {
          run();
          observer.disconnect();
        }
      });
      observer.observe(counter);
    });
  }

  function initVideoControls() {
    all('[data-w-bg-video-control]').forEach(function (button) {
      var id = button.getAttribute('aria-controls');
      var video = id && doc.getElementById(id);
      if (!video) video = closest(button, '.w-background-video') && closest(button, '.w-background-video').querySelector('video');
      if (!video) return;

      button.addEventListener('click', function () {
        if (video.paused) {
          video.play().catch(function () {});
          button.querySelectorAll('.play-state').forEach(function (item) { item.hidden = false; });
          button.querySelectorAll('.pause-state').forEach(function (item) { item.hidden = true; });
        } else {
          video.pause();
          button.querySelectorAll('.play-state').forEach(function (item) { item.hidden = true; });
          button.querySelectorAll('.pause-state').forEach(function (item) { item.hidden = false; });
        }
      });
    });
  }

  function initForms() {
    all('form').forEach(function (form) {
      form.addEventListener('submit', function (event) {
        var block = closest(form, '.w-form');
        if (!block) return;
        event.preventDefault();
        var success = block.querySelector('.w-form-done');
        var error = block.querySelector('.w-form-fail');
        if (success) success.style.display = 'block';
        if (error) error.style.display = 'none';
        form.style.display = 'none';
      });
    });
  }

  function init() {
    initReveals();
    initNav();
    initFeatureSliders();
    initSliders();
    initMarquees();
    initTabs();
    initFaqs();
    initPreviewSwitchers();
    initCounters();
    initVideoControls();
    initParallax();
    initHomeSlides();
    initForms();
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
