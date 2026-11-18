/* Outreach Recruitment — Help Center support bubble + pop-up.
   Questions are saved through the Supabase RPC submit_help_request and read in /admin → Help Center Inbox. */
(function () {
  "use strict";
  if (window.__orHelpWidget) return;
  window.__orHelpWidget = true;
  var URL = "https://atcitaqyraeqngcsaeun.supabase.co";
  var KEY = "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY";
  var TOPICS = [
    ["Jobs in Malta", "Find a job in Malta"],
    ["Hire", "Hire staff in Malta"],
    ["Study in Malta", "Study in Malta"]
  ];
  var COUNTRIES = "Afghanistan|Albania|Algeria|Argentina|Armenia|Australia|Austria|Azerbaijan|Bangladesh|Belarus|Belgium|Bolivia|Bosnia and Herzegovina|Brazil|Bulgaria|Cameroon|Canada|Chile|China|Colombia|Costa Rica|Croatia|Cuba|Cyprus|Czechia|Denmark|Dominican Republic|Ecuador|Egypt|El Salvador|Eritrea|Estonia|Ethiopia|Finland|France|Georgia|Germany|Ghana|Greece|Guatemala|Honduras|Hungary|Iceland|India|Indonesia|Iran|Iraq|Ireland|Israel|Italy|Ivory Coast|Jamaica|Japan|Jordan|Kazakhstan|Kenya|Kosovo|Kyrgyzstan|Latvia|Lebanon|Libya|Lithuania|Luxembourg|Malaysia|Mali|Malta|Mexico|Moldova|Montenegro|Morocco|Nepal|Netherlands|New Zealand|Nicaragua|Nigeria|North Macedonia|Norway|Pakistan|Palestine|Panama|Paraguay|Peru|Philippines|Poland|Portugal|Romania|Russia|Rwanda|Saudi Arabia|Senegal|Serbia|Sierra Leone|Singapore|Slovakia|Slovenia|Somalia|South Africa|South Korea|Spain|Sri Lanka|Sudan|Sweden|Switzerland|Syria|Tajikistan|Tanzania|Thailand|Tunisia|Turkey|Turkmenistan|Uganda|Ukraine|United Arab Emirates|United Kingdom|United States|Uruguay|Uzbekistan|Venezuela|Vietnam|Yemen|Zambia|Zimbabwe".split("|");

  var css = "" +
    ".orh-bubble{position:fixed;right:22px;bottom:22px;z-index:99990;width:62px;height:62px;border-radius:50%;border:0;background:#442DFA;color:#fff;display:grid;place-items:center;cursor:pointer;box-shadow:0 12px 30px rgba(68,45,250,.35);transition:transform .25s ease}" +
    ".orh-bubble:hover{transform:scale(1.06)}.orh-bubble svg{width:28px;height:28px}" +
    ".orh-panel{position:fixed;right:22px;bottom:96px;z-index:99991;width:min(400px,calc(100vw - 32px));height:min(620px,calc(100vh - 120px));display:flex;flex-direction:column;background:#fff;border-radius:22px;box-shadow:0 24px 60px rgba(16,16,30,.25);overflow:hidden;font-family:'BDO Grotesk',Arial,sans-serif;color:#1c2623;opacity:0;transform:translateY(14px) scale(.98);pointer-events:none;transition:opacity .25s ease,transform .25s ease}" +
    ".orh-panel.open{opacity:1;transform:none;pointer-events:auto}.orh-panel.big{width:min(720px,calc(100vw - 32px));height:calc(100vh - 120px)}" +
    ".orh-head{display:flex;align-items:center;gap:12px;padding:16px 18px;background:#f4f2ff;border-bottom:1px solid #e4e0ff}" +
    ".orh-logo{width:38px;height:38px;border-radius:10px;background:#442DFA;display:grid;place-items:center;color:#fff;flex:none}.orh-logo svg{width:20px;height:20px}" +
    ".orh-head strong{flex:1;font-size:18px}.orh-head button{background:none;border:0;color:#1c2623;cursor:pointer;padding:6px;border-radius:8px;display:grid;place-items:center}.orh-head button:hover{background:#e9e5ff}.orh-head svg{width:20px;height:20px}" +
    ".orh-body{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:10px}" +
    ".orh-msg{background:#f3f3f3;border-radius:14px;padding:14px 16px;line-height:1.5}" +
    ".orh-opt{display:flex;justify-content:space-between;align-items:center;width:100%;text-align:left;padding:15px 16px;border-radius:14px;border:1px solid #ececec;background:#fafafa;font:inherit;font-size:16px;color:#1c2623;cursor:pointer;transition:border-color .2s,background .2s}" +
    ".orh-opt:hover{border-color:#442DFA;background:#f4f2ff}.orh-opt span{color:#442DFA;font-size:20px}" +
    ".orh-form{display:flex;flex-direction:column;gap:10px}.orh-form label{display:flex;flex-direction:column;gap:5px;font-size:13px;font-weight:600}" +
    ".orh-form label{min-width:0}.orh-form input,.orh-form textarea{width:100%;box-sizing:border-box;min-width:0;font:inherit;font-size:15px;font-weight:400;padding:11px 13px;border:1px solid #d9d9d9;border-radius:12px;color:#1c2623;background:#fff}" +
    ".orh-form input:focus,.orh-form textarea:focus{outline:2px solid #442DFA;border-color:#442DFA}" +
    ".orh-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}.orh-topic{display:inline-flex;align-self:flex-start;padding:5px 11px;border-radius:999px;background:#442DFA;color:#fff;font-size:12px;font-weight:600;letter-spacing:.04em;text-transform:uppercase}" +
    ".orh-back{align-self:flex-start;background:none;border:0;color:#442DFA;cursor:pointer;font:inherit;font-size:14px;padding:0}" +
    ".orh-send{display:flex;align-items:center;justify-content:center;gap:8px;padding:13px;border:0;border-radius:999px;background:#442DFA;color:#fff;font:inherit;font-weight:600;font-size:16px;cursor:pointer}.orh-send:disabled{opacity:.6;cursor:wait}" +
    ".orh-err{color:#b91c1c;font-size:14px;margin:0}.orh-ok{text-align:center;padding:30px 10px}.orh-ok b{display:block;font-size:20px;margin:10px 0 6px}.orh-ok svg{width:54px;height:54px;color:#16a34a}" +
    ".orh-foot{padding:10px 16px 14px;text-align:center;font-size:12px;color:#777;border-top:1px solid #eee}" +
    "@media(max-width:520px){.orh-panel{right:8px;left:8px;bottom:88px;width:auto;height:calc(100vh - 110px)}.orh-row{grid-template-columns:1fr}.orh-bubble{right:14px;bottom:14px}}";
  var s = document.createElement("style"); s.textContent = css; document.head.appendChild(s);

  var ICON_CHAT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/></svg>';
  var ICON_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  var ICON_EXPAND = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>';
  var ICON_NEW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>';
  var ICON_OK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m8 12.5 2.5 2.5L16 9.5"/></svg>';
  var esc = function (v) { var d = document.createElement("div"); d.textContent = v || ""; return d.innerHTML; };

  var bubble = document.createElement("button");
  bubble.className = "orh-bubble"; bubble.type = "button"; bubble.setAttribute("aria-label", "Open Help Center chat");
  bubble.innerHTML = ICON_CHAT;
  var panel = document.createElement("section");
  panel.className = "orh-panel"; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", "Help Center");
  panel.innerHTML = '<div class="orh-head"><span class="orh-logo">' + ICON_CHAT + '</span><strong>Help Center</strong>' +
    '<button type="button" data-a="new" aria-label="Start again" title="Start again">' + ICON_NEW + '</button>' +
    '<button type="button" data-a="big" aria-label="Expand" title="Expand">' + ICON_EXPAND + '</button>' +
    '<button type="button" data-a="close" aria-label="Close">' + ICON_X + '</button></div>' +
    '<div class="orh-body" aria-live="polite"></div>' +
    '<div class="orh-foot">Our team replies by email, usually within one working day.</div>' +
    '<datalist id="orh-countries">' + COUNTRIES.map(function (c) { return '<option value="' + esc(c) + '">'; }).join("") + '</datalist>';
  document.body.appendChild(panel); document.body.appendChild(bubble);
  var body = panel.querySelector(".orh-body");

  function home() {
    body.innerHTML = '<div class="orh-msg">Hi! 👋 Welcome to the Outreach Recruitment Help Center. How can we help you today?</div>' +
      TOPICS.map(function (t) { return '<button type="button" class="orh-opt" data-topic="' + t[0] + '">' + esc(t[1]) + '<span aria-hidden="true">›</span></button>'; }).join("") +
      '<button type="button" class="orh-opt" data-topic="General">Ask another question<span aria-hidden="true">›</span></button>';
  }
  function form(topic) {
    var label = topic === "General" ? "Question" : topic;
    body.innerHTML = '<button type="button" class="orh-back" data-a="home">← Back</button><span class="orh-topic">' + esc(label) + '</span>' +
      '<form class="orh-form" novalidate>' +
      '<label>Full name<input name="full_name" autocomplete="name" maxlength="120" required></label>' +
      '<label>Email address<input name="email" type="email" autocomplete="email" maxlength="254" required></label>' +
      '<div class="orh-row"><label>Current location<input name="current_location" list="orh-countries" autocomplete="country-name" maxlength="120" placeholder="e.g. Malta" required></label>' +
      '<label>Nationality<input name="nationality" list="orh-countries" maxlength="120" required></label></div>' +
      '<label>Your job<input name="job_title" maxlength="120" placeholder="e.g. Chef, Accountant, Student" required></label>' +
      '<label>Your question<textarea name="message" rows="4" maxlength="4000" required></textarea></label>' +
      '<input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">' +
      '<p class="orh-err" role="alert"></p><button class="orh-send" type="submit">Send question</button></form>';
    var f = body.querySelector("form"), err = f.querySelector(".orh-err"), btn = f.querySelector(".orh-send");
    f.elements.full_name.focus();
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (f.elements.website.value) return;
      var missing = ["full_name", "email", "current_location", "nationality", "job_title", "message"].filter(function (n) { return !f.elements[n].value.trim(); });
      if (missing.length || !f.elements.email.checkValidity()) { err.textContent = "Please fill in every field with a valid email address."; return; }
      btn.disabled = true; btn.textContent = "Sending…"; err.textContent = "";
      fetch(URL + "/rest/v1/rpc/submit_help_request", {
        method: "POST",
        headers: { "Content-Type": "application/json", apikey: KEY, Authorization: "Bearer " + KEY },
        body: JSON.stringify({ p_full_name: f.elements.full_name.value, p_email: f.elements.email.value, p_current_location: f.elements.current_location.value,
          p_nationality: f.elements.nationality.value, p_job_title: f.elements.job_title.value, p_topic: topic, p_message: f.elements.message.value,
          p_page_url: location.href.split("#")[0] })
      }).then(function (r) {
        if (r.ok) return r.json();
        return r.json().catch(function () { return {}; }).then(function (b) {
          var m = b.message || "";
          if (r.status === 404 || /could not find|does not exist/i.test(m)) m = "Our question form is being set up. Please email us at hr@outreachrecruitment.net in the meantime.";
          throw new Error(m || "We couldn't send your question. Please try again.");
        });
      }).then(function () {
        body.innerHTML = '<div class="orh-ok">' + ICON_OK + '<b>Thank you — your question was sent</b><p>We will reply to ' + esc(f.elements.email.value) + ' as soon as possible.</p></div>' +
          '<button type="button" class="orh-opt" data-a="home">Ask another question<span aria-hidden="true">›</span></button>';
      }).catch(function (x) {
        btn.disabled = false; btn.textContent = "Send question";
        err.textContent = x.message || "We couldn't send your question. Please try again.";
      });
    });
  }
  function toggle(open) { panel.classList.toggle("open", open); bubble.setAttribute("aria-expanded", open); if (open && !body.innerHTML) home(); }
  bubble.addEventListener("click", function () { toggle(!panel.classList.contains("open")); });
  panel.addEventListener("click", function (e) {
    var t = e.target.closest("[data-a],[data-topic]"); if (!t) return;
    var a = t.getAttribute("data-a");
    if (a === "close") toggle(false); else if (a === "big") panel.classList.toggle("big"); else if (a === "new" || a === "home") home();
    else if (t.hasAttribute("data-topic")) form(t.getAttribute("data-topic"));
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && panel.classList.contains("open")) toggle(false); });
  // Links like <a href="#help-chat" data-topic="Hire"> open the pop-up (used on the Help Center pages).
  document.addEventListener("click", function (e) {
    var l = e.target.closest('a[href="#help-chat"]'); if (!l) return;
    e.preventDefault(); toggle(true); var tp = l.getAttribute("data-topic"); if (tp) form(tp);
  });
})();
