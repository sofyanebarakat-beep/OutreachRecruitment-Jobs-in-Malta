(function () {
  function initPartnerCarousels() {
    document.querySelectorAll('.marquee').forEach(function (carousel) {
      var track = carousel.querySelector(':scope > .marquee-track');
      if (!track || track.dataset.partnerCarouselReady === 'true') return;
      var lists = Array.prototype.slice.call(track.querySelectorAll(':scope > .marquee-list'));
      if (!lists.length) return;
      if (lists.length === 1) {
        var clone = lists[0].cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        track.appendChild(clone);
      }
      var duration = Number(carousel.getAttribute('data-marquee-speed')) || 20;
      if (duration > 0) track.style.setProperty('--or-partner-carousel-duration', duration + 's');
      track.dataset.partnerCarouselReady = 'true';
      carousel.classList.add('or-partner-carousel');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initPartnerCarousels);
  else initPartnerCarousels();
})();
