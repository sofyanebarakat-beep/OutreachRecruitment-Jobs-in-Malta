(function(){
  "use strict";
  var STORAGE_KEY="or-hotel-manager-eligibility";
  var countries=[
    ["AL","🇦🇱 Albania"],["AD","🇦🇩 Andorra"],["AM","🇦🇲 Armenia"],["AT","🇦🇹 Austria"],["AZ","🇦🇿 Azerbaijan"],
    ["BY","🇧🇾 Belarus"],["BE","🇧🇪 Belgium"],["BA","🇧🇦 Bosnia and Herzegovina"],["BG","🇧🇬 Bulgaria"],["HR","🇭🇷 Croatia"],
    ["CY","🇨🇾 Cyprus"],["CZ","🇨🇿 Czechia"],["DK","🇩🇰 Denmark"],["EE","🇪🇪 Estonia"],["FI","🇫🇮 Finland"],
    ["FR","🇫🇷 France"],["GE","🇬🇪 Georgia"],["DE","🇩🇪 Germany"],["GR","🇬🇷 Greece"],["HU","🇭🇺 Hungary"],
    ["IS","🇮🇸 Iceland"],["IE","🇮🇪 Ireland"],["IT","🇮🇹 Italy"],["XK","🇽🇰 Kosovo"],["LV","🇱🇻 Latvia"],
    ["LI","🇱🇮 Liechtenstein"],["LT","🇱🇹 Lithuania"],["LU","🇱🇺 Luxembourg"],["MT","🇲🇹 Malta"],["MD","🇲🇩 Moldova"],
    ["MC","🇲🇨 Monaco"],["ME","🇲🇪 Montenegro"],["NL","🇳🇱 Netherlands"],["MK","🇲🇰 North Macedonia"],["NO","🇳🇴 Norway"],
    ["PL","🇵🇱 Poland"],["PT","🇵🇹 Portugal"],["RO","🇷🇴 Romania"],["RU","🇷🇺 Russia"],["SM","🇸🇲 San Marino"],["RS","🇷🇸 Serbia"],
    ["SK","🇸🇰 Slovakia"],["SI","🇸🇮 Slovenia"],["ES","🇪🇸 Spain"],["SE","🇸🇪 Sweden"],["CH","🇨🇭 Switzerland"],
    ["TR","🇹🇷 Türkiye"],["UA","🇺🇦 Ukraine"],["GB","🇬🇧 United Kingdom"],["VA","🇻🇦 Vatican City"],["OTHER","🌍 Outside Europe"]
  ];
  var countryNames={};countries.forEach(function(c){countryNames[c[0]]=c[1];});
  var saved=null,pendingTrigger=null,lastFocus=null;
  try{saved=JSON.parse(sessionStorage.getItem(STORAGE_KEY)||"null");}catch(e){saved=null;}

  var gate=document.createElement("div");
  gate.className="eligibility-gate";gate.hidden=true;
  gate.innerHTML='<div class="eligibility-dialog" role="dialog" aria-modal="true" aria-labelledby="eligibility-title"><button class="eligibility-close" type="button" aria-label="Close eligibility check">×</button><p class="eligibility-eyebrow">Before you apply</p><h2 class="eligibility-title" id="eligibility-title">Check your eligibility</h2><p class="eligibility-intro">This vacancy is currently open to candidates who live in Europe. Enter your details to continue.</p><form class="eligibility-form"><div class="eligibility-field"><label for="eligibility-name">Full name</label><input id="eligibility-name" name="name" type="text" autocomplete="name" required maxlength="100"></div><div class="eligibility-field"><label for="eligibility-email">Email address</label><input id="eligibility-email" name="email" type="email" autocomplete="email" required maxlength="160"></div><div class="eligibility-field"><label for="eligibility-country">Current country of residence</label><select id="eligibility-country" name="country" required><option value="">Select your country</option>'+countries.map(function(c){return '<option value="'+c[0]+'">'+c[1]+'</option>';}).join("")+'</select></div><button class="eligibility-submit" type="submit">Check eligibility and continue</button><p class="eligibility-note">Your details stay in this browser session and are shown on the next step. They are not submitted to Outreach Recruitment by this check.</p><div class="eligibility-result" hidden aria-live="polite"></div></form></div>';
  document.body.appendChild(gate);
  var form=gate.querySelector("form"),nameInput=gate.querySelector("#eligibility-name"),emailInput=gate.querySelector("#eligibility-email"),countryInput=gate.querySelector("#eligibility-country"),result=gate.querySelector(".eligibility-result"),closeButton=gate.querySelector(".eligibility-close");

  function eligible(data){return data&&data.country&&data.country!=="OTHER";}
  function openGate(trigger){pendingTrigger=trigger||pendingTrigger;lastFocus=document.activeElement;result.hidden=true;result.className="eligibility-result";result.innerHTML="";if(saved){nameInput.value=saved.name||"";emailInput.value=saved.email||"";countryInput.value=saved.country||"";}gate.hidden=false;document.body.style.overflow="hidden";setTimeout(function(){nameInput.focus();},0);}
  function closeGate(){gate.hidden=true;document.body.style.overflow="";if(lastFocus&&lastFocus.focus)lastFocus.focus();}
  function applicationTrigger(){return document.querySelector("[data-job-apply-trigger]");}
  function continueToApplication(){closeGate();var trigger=applicationTrigger();if(trigger)trigger.click();}
  function showSummary(){
    var panel=document.getElementById("job-apply-panel");if(!panel||!eligible(saved))return;
    var summary=panel.querySelector(".eligibility-summary");
    if(!summary){summary=document.createElement("section");summary.className="eligibility-summary";var header=panel.querySelector(".job-inline-apply-header");if(header)header.insertAdjacentElement("afterend",summary);else panel.insertBefore(summary,panel.firstChild);}
    summary.innerHTML='<div class="eligibility-summary-head"><h2>Your eligibility details</h2><button type="button" data-eligibility-change>Change details</button></div><div class="eligibility-summary-grid"><span><strong>Name:</strong>'+escapeHtml(saved.name)+'</span><span><strong>Email:</strong>'+escapeHtml(saved.email)+'</span><span><strong>Residence:</strong>'+escapeHtml(countryNames[saved.country]||saved.country)+'</span></div><p class="eligibility-summary-note">These details are saved only for this browser session. Please complete the official application form below.</p>';
    summary.querySelector("[data-eligibility-change]").addEventListener("click",function(){openGate(applicationTrigger());});
  }
  function escapeHtml(value){var node=document.createElement("div");node.textContent=value||"";return node.innerHTML;}

  document.addEventListener("click",function(event){
    var trigger=event.target.closest("[data-job-apply-trigger], [data-slow-scroll-target='how-to-apply']");
    if(!trigger)return;
    if(eligible(saved)){if(trigger.hasAttribute("data-slow-scroll-target")){event.preventDefault();event.stopImmediatePropagation();continueToApplication();}else{setTimeout(showSummary,0);}return;}
    event.preventDefault();event.stopImmediatePropagation();openGate(trigger);
  },true);
  closeButton.addEventListener("click",closeGate);
  gate.addEventListener("click",function(event){if(event.target===gate)closeGate();});
  document.addEventListener("keydown",function(event){if(!gate.hidden&&event.key==="Escape")closeGate();});
  form.addEventListener("submit",function(event){
    event.preventDefault();if(!form.reportValidity())return;
    saved={name:nameInput.value.trim(),email:emailInput.value.trim(),country:countryInput.value};
    try{sessionStorage.setItem(STORAGE_KEY,JSON.stringify(saved));}catch(e){}
    if(!eligible(saved)){
      result.hidden=false;result.className="eligibility-result eligibility-result--blocked";
      result.innerHTML='<h3>This role is not available for your location</h3><p>You must currently live in Europe to apply for this vacancy.</p><div class="eligibility-result-actions"><button class="eligibility-secondary" type="button" data-edit-residence>Change country</button><a class="eligibility-secondary" href="/jobs/">Browse other jobs</a></div>';
      result.querySelector("[data-edit-residence]").addEventListener("click",function(){countryInput.focus();});return;
    }
    continueToApplication();setTimeout(showSummary,0);
  });
  if(location.hash==="#job-apply-panel"&&!eligible(saved)){history.replaceState(null,"",location.pathname+location.search);setTimeout(function(){openGate(applicationTrigger());},0);}else if(location.hash==="#job-apply-panel"){setTimeout(showSummary,0);}
})();
