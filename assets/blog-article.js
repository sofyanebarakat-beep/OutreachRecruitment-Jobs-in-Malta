(function () {
  var body = document.getElementById('odBody');
  if (!body) return;

  var bar = document.getElementById('odProgress');
  var cta = document.getElementById('odCtaBar');

  function onScroll() {
    var h = document.documentElement.scrollHeight - innerHeight;
    var p = h > 0 ? scrollY / h : 0;
    if (bar) bar.style.width = p * 100 + '%';
    if (cta) cta.classList.toggle('is-visible', p > 0.3 && p < 0.92);
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Table of contents built from the article headings
  var toc = document.getElementById('odToc');
  if (toc) {
    var heads = [].slice.call(body.querySelectorAll('h2')).filter(function (h) {
      return !h.closest('.cta-box, aside, nav, .faq-list');
    });
    if (heads.length < 3) {
      heads = [].slice.call(body.querySelectorAll('h2, h5')).filter(function (h) {
        return h.textContent.replace(/[\s\u200d]/g, '') && !h.closest('.cta-box, aside, nav');
      });
    }
    if (heads.length < 3) {
      toc.parentNode.removeChild(toc);
    } else {
      var list = toc.querySelector('ol');
      var used = {};
      heads.forEach(function (h, i) {
        var id = h.id || h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'section-' + i;
        while (used[id]) id += '-' + i;
        used[id] = 1;
        h.id = id;
        h.style.scrollMarginTop = '110px';
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = '#' + id;
        a.textContent = h.textContent.trim();
        li.appendChild(a);
        list.appendChild(li);
      });
      if (innerWidth < 992) toc.removeAttribute('open');

      if ('IntersectionObserver' in window) {
        var links = [].slice.call(list.querySelectorAll('a'));
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) {
            if (en.isIntersecting) {
              links.forEach(function (l) {
                l.classList.toggle('is-active', l.getAttribute('href') === '#' + en.target.id);
              });
            }
          });
        }, { rootMargin: '-120px 0px -70% 0px' });
        heads.forEach(function (h) { io.observe(h); });
      }
    }
  }

  // Copy-link button
  var copy = document.querySelector('[data-od-copy]');
  if (copy) {
    copy.addEventListener('click', function () {
      var done = copy.getAttribute('data-done') || 'Copied!';
      var label = copy.textContent;
      function ok() { copy.textContent = done; setTimeout(function () { copy.textContent = label; }, 1800); }
      if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(ok);
      else {
        var t = document.createElement('textarea');
        t.value = location.href; document.body.appendChild(t); t.select();
        try { document.execCommand('copy'); ok(); } catch (e) {}
        document.body.removeChild(t);
      }
    });
  }
})();
