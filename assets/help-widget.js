/* Outreach Recruitment — Help Center support bubble + pop-up.
   Requests are saved through the Supabase RPC submit_help_request_v2 and read in /admin → Help Center Inbox.
   window.OutreachHelp.open("Jobs in Malta" | "Hire" | "Study in Malta" | "General") opens it from other buttons. */
(function () {
  "use strict";
  if (window.__orHelpWidget) return;
  window.__orHelpWidget = true;
  var API = "https://atcitaqyraeqngcsaeun.supabase.co";
  var KEY = "sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY";
  var DIAL = {"AF":93,"AL":355,"DZ":213,"AD":376,"AO":244,"AG":1,"AR":54,"AM":374,"AU":61,"AT":43,"AZ":994,"BS":1,"BH":973,"BD":880,"BB":1,"BY":375,"BE":32,"BZ":501,"BJ":229,"BT":975,"BO":591,"BA":387,"BW":267,"BR":55,"BN":673,"BG":359,"BF":226,"BI":257,"CV":238,"KH":855,"CM":237,"CA":1,"CF":236,"TD":235,"CL":56,"CN":86,"CO":57,"KM":269,"CG":242,"CD":243,"CR":506,"CI":225,"HR":385,"CU":53,"CY":357,"CZ":420,"DK":45,"DJ":253,"DM":1,"DO":1,"EC":593,"EG":20,"SV":503,"GQ":240,"ER":291,"EE":372,"SZ":268,"ET":251,"FJ":679,"FI":358,"FR":33,"GA":241,"GM":220,"GE":995,"DE":49,"GH":233,"GR":30,"GD":1,"GT":502,"GN":224,"GW":245,"GY":592,"HT":509,"HN":504,"HU":36,"IS":354,"IN":91,"ID":62,"IR":98,"IQ":964,"IE":353,"IL":972,"IT":39,"JM":1,"JP":81,"JO":962,"KZ":7,"KE":254,"KI":686,"KP":850,"KR":82,"KW":965,"KG":996,"LA":856,"LV":371,"LB":961,"LS":266,"LR":231,"LY":218,"LI":423,"LT":370,"LU":352,"MG":261,"MW":265,"MY":60,"MV":960,"ML":223,"MT":356,"MH":692,"MR":222,"MU":230,"MX":52,"FM":691,"MD":373,"MC":377,"MN":976,"ME":382,"MA":212,"MZ":258,"MM":95,"NA":264,"NR":674,"NP":977,"NL":31,"NZ":64,"NI":505,"NE":227,"NG":234,"MK":389,"NO":47,"OM":968,"PK":92,"PW":680,"PS":970,"PA":507,"PG":675,"PY":595,"PE":51,"PH":63,"PL":48,"PT":351,"QA":974,"RO":40,"RU":7,"RW":250,"KN":1,"LC":1,"VC":1,"WS":685,"SM":378,"ST":239,"SA":966,"SN":221,"RS":381,"SC":248,"SL":232,"SG":65,"SK":421,"SI":386,"SB":677,"SO":252,"ZA":27,"SS":211,"ES":34,"LK":94,"SD":249,"SR":597,"SE":46,"CH":41,"SY":963,"TW":886,"TJ":992,"TZ":255,"TH":66,"TL":670,"TG":228,"TO":676,"TT":1,"TN":216,"TR":90,"TM":993,"TV":688,"UG":256,"UA":380,"AE":971,"GB":44,"US":1,"UY":598,"UZ":998,"VU":678,"VA":39,"VE":58,"VN":84,"YE":967,"ZM":260,"ZW":263,"XK":383};
  var names = window.Intl && Intl.DisplayNames ? new Intl.DisplayNames(["en"], { type: "region" }) : null;
  var flag = function (c) { return c.replace(/./g, function (l) { return String.fromCodePoint(127397 + l.charCodeAt(0)); }); };
  var COUNTRIES = Object.keys(DIAL).map(function (c) { return { code: c, name: c === "XK" ? "Kosovo" : (names ? names.of(c) : c), dial: DIAL[c], flag: flag(c) }; })
    .sort(function (a, b) { return a.name.localeCompare(b.name); });
  var byCode = {}; COUNTRIES.forEach(function (c) { byCode[c.code] = c; });
  var esc = function (v) { var d = document.createElement("div"); d.textContent = v == null ? "" : v; return d.innerHTML; };

  var css = "" +
    ".orh-bubble{position:fixed;right:22px;bottom:22px;z-index:99990;width:62px;height:62px;border-radius:50%;border:0;background:#442DFA;color:#fff;display:grid;place-items:center;cursor:pointer;box-shadow:0 12px 30px rgba(68,45,250,.35);transition:transform .25s ease}" +
    ".orh-bubble:hover{transform:scale(1.06)}.orh-bubble svg{width:28px;height:28px}" +
    ".orh-panel{position:fixed;right:22px;bottom:96px;z-index:99991;width:min(420px,calc(100vw - 32px));height:min(660px,calc(100vh - 120px));display:flex;flex-direction:column;background:#fff;border-radius:22px;box-shadow:0 24px 60px rgba(16,16,30,.25);overflow:hidden;font-family:'BDO Grotesk',Arial,sans-serif;color:#1c2623;opacity:0;transform:translateY(14px) scale(.98);pointer-events:none;transition:opacity .25s ease,transform .25s ease}" +
    ".orh-panel *{box-sizing:border-box}.orh-panel.open{opacity:1;transform:none;pointer-events:auto}.orh-panel.big{width:min(720px,calc(100vw - 32px));height:calc(100vh - 120px)}" +
    ".orh-head{display:flex;align-items:center;gap:12px;padding:16px 18px;background:#f4f2ff;border-bottom:1px solid #e4e0ff}" +
    ".orh-logo{width:38px;height:38px;border-radius:10px;background:#442DFA;display:grid;place-items:center;color:#fff;flex:none}.orh-logo svg{width:20px;height:20px}" +
    ".orh-head strong{flex:1;font-size:18px}.orh-head button{background:none;border:0;color:#1c2623;cursor:pointer;padding:6px;border-radius:8px;display:grid;place-items:center}.orh-head button:hover{background:#e9e5ff}.orh-head svg{width:20px;height:20px}" +
    ".orh-body{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:10px;-webkit-overflow-scrolling:touch}" +
    ".orh-msg{background:#f3f3f3;border-radius:14px;padding:14px 16px;line-height:1.5;margin:0}" +
    ".orh-opt{display:flex;justify-content:space-between;align-items:center;gap:10px;width:100%;text-align:left;padding:15px 16px;border-radius:14px;border:1px solid #ececec;background:#fafafa;font:inherit;font-size:16px;color:#1c2623;cursor:pointer;text-decoration:none;transition:border-color .2s,background .2s}" +
    ".orh-opt:hover{border-color:#442DFA;background:#f4f2ff}.orh-opt span{color:#442DFA;font-size:20px}.orh-opt small{display:block;color:#666;font-size:13px;margin-top:2px}" +
    ".orh-link{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:16px;border-radius:14px;background:#442DFA;color:#fff!important;text-decoration:none;font-weight:600}.orh-link small{display:block;font-weight:400;opacity:.85;font-size:13px;margin-top:3px}.orh-link span{font-size:22px}" +
    ".orh-or{display:flex;align-items:center;gap:10px;color:#888;font-size:13px;margin:4px 0}.orh-or::before,.orh-or::after{content:'';flex:1;height:1px;background:#e5e5e5}" +
    ".orh-form{display:flex;flex-direction:column;gap:10px}.orh-form label{display:flex;flex-direction:column;gap:5px;font-size:13px;font-weight:600;min-width:0}" +
    ".orh-in{width:100%;min-width:0;font:inherit;font-size:16px;font-weight:400;padding:11px 13px;border:1px solid #d9d9d9;border-radius:12px;color:#1c2623;background:#fff;text-align:left}" +
    ".orh-in:focus,.orh-pick:focus{outline:2px solid #442DFA;border-color:#442DFA}textarea.orh-in{resize:vertical}" +
    ".orh-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}" +
    ".orh-pick{display:flex;align-items:center;gap:8px;width:100%;min-width:0;font:inherit;font-size:16px;font-weight:400;padding:11px 13px;border:1px solid #d9d9d9;border-radius:12px;background:#fff;color:#1c2623;cursor:pointer;text-align:left}" +
    ".orh-pick .ph{color:#8a8a8a}.orh-pick .v{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.orh-pick::after{content:'';border:5px solid transparent;border-top-color:#666;margin-top:5px}" +
    ".orh-phone{display:flex;gap:8px}.orh-phone .orh-pick{width:auto;flex:none;padding-right:10px}.orh-phone .orh-in{flex:1}" +
    ".orh-list{position:absolute;inset:0;z-index:5;display:flex;flex-direction:column;background:#fff}" +
    ".orh-list-head{display:flex;gap:8px;align-items:center;padding:14px 14px 10px;border-bottom:1px solid #eee}.orh-list-head input{flex:1}" +
    ".orh-list-head button{background:none;border:0;font:inherit;color:#442DFA;font-weight:600;cursor:pointer;padding:8px}" +
    ".orh-list ul{list-style:none;margin:0;padding:6px;overflow-y:auto;flex:1;-webkit-overflow-scrolling:touch}" +
    ".orh-list li button{display:flex;align-items:center;gap:12px;width:100%;padding:11px 12px;border:0;border-radius:10px;background:none;font:inherit;font-size:16px;color:#1c2623;cursor:pointer;text-align:left}" +
    ".orh-list li button:hover,.orh-list li button:focus{background:#f4f2ff;outline:none}.orh-list .f{font-size:22px;line-height:1}.orh-list .d{margin-left:auto;color:#777;font-size:14px}" +
    ".orh-topic{display:inline-flex;align-self:flex-start;padding:5px 11px;border-radius:999px;background:#442DFA;color:#fff;font-size:12px;font-weight:600;letter-spacing:.04em;text-transform:uppercase}" +
    ".orh-back{align-self:flex-start;background:none;border:0;color:#442DFA;cursor:pointer;font:inherit;font-size:14px;padding:0}" +
    ".orh-send{display:flex;align-items:center;justify-content:center;gap:8px;padding:14px;border:0;border-radius:999px;background:#442DFA;color:#fff;font:inherit;font-weight:600;font-size:16px;cursor:pointer}.orh-send:disabled{opacity:.6;cursor:wait}" +
    ".orh-err{color:#b91c1c;font-size:14px;margin:0}.orh-ok{text-align:center;padding:24px 10px}.orh-ok b{display:block;font-size:20px;margin:10px 0 6px}.orh-ok svg{width:54px;height:54px;color:#16a34a}" +
    ".orh-foot{padding:10px 16px 14px;text-align:center;font-size:12px;color:#777;border-top:1px solid #eee}" +
    "@media(max-width:560px){.orh-panel,.orh-panel.big{inset:0;width:100%;height:100%;height:100dvh;border-radius:0;bottom:0;right:0}.orh-row{grid-template-columns:minmax(0,1fr)}" +
    ".orh-bubble{right:14px;bottom:14px}.orh-panel.open~.orh-bubble{display:none}.orh-head [data-a=big]{display:none}}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

  var I = {
    chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    expand: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>',
    restart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
    ok: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m8 12.5 2.5 2.5L16 9.5"/></svg>'
  };

  var bubble = document.createElement("button");
  bubble.className = "orh-bubble"; bubble.type = "button"; bubble.setAttribute("aria-label", "Open Help Center chat"); bubble.innerHTML = I.chat;
  var panel = document.createElement("section");
  panel.className = "orh-panel"; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", "Help Center");
  panel.innerHTML = '<div class="orh-head"><span class="orh-logo">' + I.chat + '</span><strong>Help Center</strong>' +
    '<button type="button" data-a="home" aria-label="Start again" title="Start again">' + I.restart + '</button>' +
    '<button type="button" data-a="big" aria-label="Expand" title="Expand">' + I.expand + '</button>' +
    '<button type="button" data-a="close" aria-label="Close">' + I.x + '</button></div>' +
    '<div class="orh-body" aria-live="polite"></div><div class="orh-foot">Our team replies by email, usually within one working day.</div>';
  document.body.appendChild(panel); document.body.appendChild(bubble);
  var body = panel.querySelector(".orh-body");

  /* ---------- country picker (flag + name, or flag + dial code for phones) ---------- */
  function picker(name, label, phone) {
    return '<button type="button" class="orh-pick" data-pick="' + name + '"' + (phone ? ' data-phone="1"' : '') + ' aria-label="' + esc(label) + '">' +
      '<span class="f"></span><span class="v ph">' + (phone ? "Code" : "Select country") + '</span></button><input type="hidden" name="' + name + '">';
  }
  function setPick(btn, c) {
    btn.querySelector(".f").textContent = c.flag;
    var v = btn.querySelector(".v"); v.classList.remove("ph");
    v.textContent = btn.hasAttribute("data-phone") ? "+" + c.dial : c.name;
    btn.nextElementSibling.value = btn.hasAttribute("data-phone") ? c.code : c.name;
  }
  function openList(btn) {
    var phone = btn.hasAttribute("data-phone");
    var box = document.createElement("div"); box.className = "orh-list";
    box.innerHTML = '<div class="orh-list-head"><input class="orh-in" type="search" placeholder="Search country' + (phone ? ' or code' : '') + '…" aria-label="Search country"><button type="button">Cancel</button></div><ul role="listbox"></ul>';
    var ul = box.querySelector("ul"), q = box.querySelector("input");
    function draw() {
      var s = q.value.trim().toLowerCase().replace(/^\+/, "");
      var rank = function (c) { var n = c.name.toLowerCase(); return !s ? 0 : n.indexOf(s) === 0 || c.code.toLowerCase() === s || String(c.dial) === s ? 0 : n.indexOf(" " + s) > -1 ? 1 : 2; };
      ul.innerHTML = COUNTRIES.filter(function (c) { return !s || c.name.toLowerCase().indexOf(s) > -1 || String(c.dial).indexOf(s) === 0 || c.code.toLowerCase() === s; })
        .sort(function (a, b) { return rank(a) - rank(b); })
        .map(function (c) { return '<li><button type="button" data-c="' + c.code + '"><span class="f">' + c.flag + '</span>' + esc(c.name) + (phone ? '<span class="d">+' + c.dial + '</span>' : '') + '</button></li>'; }).join("") ||
        '<li style="padding:14px;color:#777">No country found</li>';
    }
    q.addEventListener("input", draw);
    box.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      if (b.hasAttribute("data-c")) setPick(btn, byCode[b.getAttribute("data-c")]);
      box.remove(); btn.focus();
    });
    draw(); panel.appendChild(box); setTimeout(function () { q.focus(); }, 30);
  }

  /* ---------- screens ---------- */
  function home() {
    body.innerHTML = '<p class="orh-msg">Hi! 👋 Welcome to the Outreach Recruitment Help Center. How can we help you today?</p>' +
      '<button type="button" class="orh-opt" data-go="Jobs in Malta"><div>Find a job in Malta<small>See open jobs and apply online</small></div><span aria-hidden="true">›</span></button>' +
      '<button type="button" class="orh-opt" data-go="Hire"><div>Hire staff in Malta<small>Tell us who you need — we will contact you</small></div><span aria-hidden="true">›</span></button>' +
      '<button type="button" class="orh-opt" data-go="Study in Malta"><div>Study in Malta<small>Courses, visas and free guidance</small></div><span aria-hidden="true">›</span></button>' +
      '<button type="button" class="orh-opt" data-go="General"><div>Ask another question<small>Our team will reply by email</small></div><span aria-hidden="true">›</span></button>';
  }
  var back = '<button type="button" class="orh-back" data-a="home">← Back</button>';
  var F = {
    name: '<label>Full name<input class="orh-in" name="full_name" autocomplete="name" maxlength="120" required></label>',
    email: '<label>Email address<input class="orh-in" name="email" type="email" inputmode="email" autocomplete="email" maxlength="254" required></label>',
    phone: '<label>Phone number<div class="orh-phone">' + picker("phone_cc", "Country code", true) + '<input class="orh-in" name="phone_num" type="tel" inputmode="tel" autocomplete="tel-national" maxlength="16" placeholder="Phone number" required></div></label>',
    loc: '<div class="orh-row"><label>Current location' + picker("current_location", "Current location") + '</label><label>Nationality' + picker("nationality", "Nationality") + '</label></div>'
  };
  function formHtml(fields, sendLabel) {
    return '<form class="orh-form" novalidate>' + fields + '<input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">' +
      '<p class="orh-err" role="alert"></p><button class="orh-send" type="submit">' + sendLabel + '</button></form>';
  }
  function screen(topic) {
    if (topic === "Jobs in Malta") {
      body.innerHTML = back + '<span class="orh-topic">Jobs in Malta</span><p class="orh-msg">You can see every open job and apply online in a few minutes.</p>' +
        '<a class="orh-link" href="/jobs/"><div>Browse jobs &amp; apply<small>All open positions in Malta</small></div><span aria-hidden="true">→</span></a>' +
        '<div class="orh-or">or ask us a question</div>' +
        formHtml(F.name + F.email + F.loc + '<label>Your job<input class="orh-in" name="job_title" maxlength="120" placeholder="e.g. Chef, Accountant, Driver" required></label>' +
          '<label>Your question<textarea class="orh-in" name="message" rows="3" maxlength="4000" required></textarea></label>', "Send question");
    } else if (topic === "Hire") {
      body.innerHTML = back + '<span class="orh-topic">Hire staff</span>' +
        '<a class="orh-link" href="/employers"><div>Our recruitment services<small>How we help employers in Malta hire</small></div><span aria-hidden="true">→</span></a>' +
        '<p class="orh-msg">Or fill in your details here and our team will contact you.</p>' +
        formHtml(F.name + F.email + F.phone + '<label>Company<input class="orh-in" name="company" autocomplete="organization" maxlength="120" required></label>' +
          '<label>Which roles do you need? <span style="font-weight:400;color:#777">(optional)</span><textarea class="orh-in" name="message" rows="2" maxlength="4000"></textarea></label>', "Contact me");
    } else if (topic === "Study in Malta") {
      body.innerHTML = back + '<span class="orh-topic">Study in Malta</span>' +
        '<a class="orh-link" href="/study-in-malta"><div>Study in Malta guide<small>Courses, visas, costs and how to apply</small></div><span aria-hidden="true">→</span></a>' +
        '<p class="orh-msg">Want free guidance? Leave your details and a study advisor will contact you.</p>' +
        formHtml(F.name + F.email + F.phone + F.loc +
          '<label>What do you want to study?<select class="orh-in" name="study_level" required><option value="">Choose one</option><option>English language course</option><option>Diploma / vocational course</option><option>Bachelor’s degree</option><option>Master’s degree</option><option>Not sure yet</option></select></label>' +
          '<label>When do you want to start?<select class="orh-in" name="start_when"><option value="">Choose one</option><option>As soon as possible</option><option>In 3–6 months</option><option>In 6–12 months</option><option>Next year or later</option></select></label>' +
          '<label>Anything else? <span style="font-weight:400;color:#777">(optional)</span><textarea class="orh-in" name="message" rows="2" maxlength="4000"></textarea></label>', "Get free guidance");
    } else {
      topic = "General";
      body.innerHTML = back + '<span class="orh-topic">Question</span>' +
        formHtml(F.name + F.email + F.loc + '<label>Your job<input class="orh-in" name="job_title" maxlength="120" placeholder="e.g. Chef, Student, HR Manager" required></label>' +
          '<label>Your question<textarea class="orh-in" name="message" rows="4" maxlength="4000" required></textarea></label>', "Send question");
    }
    var f = body.querySelector("form"); if (f) wire(f, topic);
  }
  function wire(f, topic) {
    var err = f.querySelector(".orh-err"), btn = f.querySelector(".orh-send"), label = btn.textContent;
    var first = f.querySelector("input.orh-in"); if (first && window.innerWidth > 560) first.focus();
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (f.elements.website.value) return;
      var val = function (n) { return f.elements[n] ? String(f.elements[n].value || "").trim() : ""; };
      var need = [].slice.call(f.querySelectorAll("[required]")).map(function (el) { return el.name; });
      if (f.querySelector('[data-pick="current_location"]')) need.push("current_location", "nationality");
      if (f.querySelector('[data-pick="phone_cc"]')) need.push("phone_cc");
      var missing = need.filter(function (n) { return !val(n); });
      if (missing.length) { err.textContent = "Please fill in every required field."; return; }
      if (!f.elements.email.checkValidity()) { err.textContent = "Please enter a valid email address."; return; }
      var phone = "";
      if (f.elements.phone_cc) {
        var digits = val("phone_num").replace(/[^0-9]/g, "").replace(/^0+/, "");
        if (digits.length < 6) { err.textContent = "Please enter a valid phone number."; return; }
        phone = "+" + byCode[val("phone_cc")].dial + " " + digits;
      }
      var details = {};
      ["study_level", "start_when"].forEach(function (n) { if (val(n)) details[n] = val(n); });
      btn.disabled = true; btn.textContent = "Sending…"; err.textContent = "";
      fetch(API + "/rest/v1/rpc/submit_help_request_v2", {
        method: "POST",
        headers: { "Content-Type": "application/json", apikey: KEY, Authorization: "Bearer " + KEY },
        body: JSON.stringify({ p: { topic: topic, full_name: val("full_name"), email: val("email"), phone: phone, company: val("company"),
          current_location: val("current_location"), nationality: val("nationality"), job_title: val("job_title"),
          message: val("message") || (details.study_level ? "Study in Malta: " + details.study_level : ""), page_url: location.href.split("#")[0], details: details } })
      }).then(function (r) {
        if (r.ok) return r.json();
        return r.json().catch(function () { return {}; }).then(function (b) {
          var m = b.message || "";
          if (r.status === 404 || /could not find|does not exist/i.test(m)) m = "Our form is being set up. Please email us at hr@outreachrecruitment.net in the meantime.";
          throw new Error(m || "We couldn't send your request. Please try again.");
        });
      }).then(function () {
        var thanks = topic === "Hire" ? "Thank you — our team will contact you shortly" : topic === "Study in Malta" ? "Thank you — a study advisor will contact you" : "Thank you — your question was sent";
        body.innerHTML = '<div class="orh-ok">' + I.ok + '<b>' + thanks + '</b><p>We will reply to ' + esc(val("email")) + '.</p></div>' +
          '<button type="button" class="orh-opt" data-a="home">Back to the start<span aria-hidden="true">›</span></button>';
      }).catch(function (x) { btn.disabled = false; btn.textContent = label; err.textContent = x.message; });
    });
  }

  function toggle(open) {
    panel.classList.toggle("open", open); bubble.setAttribute("aria-expanded", open);
    if (open && !body.innerHTML) home();
    document.documentElement.style.overflow = open && window.innerWidth <= 560 ? "hidden" : "";
  }
  bubble.addEventListener("click", function () { toggle(!panel.classList.contains("open")); });
  panel.addEventListener("click", function (e) {
    var t = e.target.closest("[data-a],[data-go],[data-pick]"); if (!t) return;
    if (t.hasAttribute("data-pick")) { openList(t); return; }
    var a = t.getAttribute("data-a");
    if (a === "close") toggle(false); else if (a === "big") panel.classList.toggle("big"); else if (a === "home") home();
    else if (t.hasAttribute("data-go")) screen(t.getAttribute("data-go"));
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape" || !panel.classList.contains("open")) return;
    var list = panel.querySelector(".orh-list"); if (list) list.remove(); else toggle(false);
  });
  window.OutreachHelp = { open: function (topic) { toggle(true); if (topic) screen(topic); else home(); } };
  document.addEventListener("click", function (e) {
    var l = e.target.closest('a[href="#help-chat"]'); if (!l) return;
    e.preventDefault(); window.OutreachHelp.open(l.getAttribute("data-topic") || "");
  });
})();
