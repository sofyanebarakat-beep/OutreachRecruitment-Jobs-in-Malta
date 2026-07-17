(function () {
  var STORAGE_KEY = 'or_cookie_consent';

  function hasConsent() {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true';
    } catch (e) {
      return document.cookie.indexOf(STORAGE_KEY + '=true') !== -1;
    }
  }

  function setConsent() {
    try {
      localStorage.setItem(STORAGE_KEY, 'true');
    } catch (e) {
      var expires = new Date();
      expires.setFullYear(expires.getFullYear() + 1);
      document.cookie = STORAGE_KEY + '=true; expires=' + expires.toUTCString() + '; path=/';
    }
  }

  function injectStyles() {
    var style = document.createElement('style');
    style.textContent =
      '#or-cookie-banner{position:fixed;left:0;right:0;bottom:0;z-index:9999;' +
      'display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:16px;' +
      'padding:16px 24px;background:#2C2D2D;color:#fff;' +
      'font-family:inherit;font-size:14px;line-height:1.5;' +
      'box-shadow:0 -2px 12px rgba(0,0,0,0.15);' +
      'transform:translateY(100%);transition:transform 0.4s ease;}' +
      '#or-cookie-banner.is-visible{transform:translateY(0);}' +
      '#or-cookie-banner p{margin:0;max-width:640px;}' +
      '#or-cookie-banner button{flex:0 0 auto;border:none;cursor:pointer;' +
      'background:#442DFA;color:#fff;font-weight:600;font-size:14px;' +
      'padding:10px 28px;border-radius:6px;}' +
      '#or-cookie-banner button:hover{background:#3420c9;}';
    document.head.appendChild(style);
  }

  function showBanner() {
    injectStyles();

    var banner = document.createElement('div');
    banner.id = 'or-cookie-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookie notice');

    var text = document.createElement('p');
    text.textContent =
      'We use cookies to ensure that we give you the best experience on our website. ' +
      'If you continue to use this site we will assume that you are happy with it.';

    var button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Ok';
    button.addEventListener('click', function () {
      setConsent();
      banner.classList.remove('is-visible');
      setTimeout(function () {
        banner.remove();
      }, 400);
    });

    banner.appendChild(text);
    banner.appendChild(button);
    document.body.appendChild(banner);

    requestAnimationFrame(function () {
      banner.classList.add('is-visible');
    });
  }

  function init() {
    if (hasConsent()) return;
    showBanner();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
