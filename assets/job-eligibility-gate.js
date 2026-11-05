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
  var saved=null,lastFocus=null;
  try{saved=JSON.parse(sessionStorage.getItem(STORAGE_KEY)||"null");}catch(e){saved=null;}

  var gate=document.createElement("div");
  gate.className="eligibility-gate";gate.hidden=true;
  gate.innerHTML='<div class="eligibility-dialog" role="dialog" aria-modal="true" aria-labelledby="eligibility-title"><button class="eligibility-close" type="button" aria-label="Close eligibility check">×</button><p class="eligibility-eyebrow">Before you apply</p><h2 class="eligibility-title" id="eligibility-title">Check your eligibility</h2><p class="eligibility-intro">This vacancy is currently open to candidates who live in Europe. Search for your current country of residence to continue.</p><form class="eligibility-form"><div class="eligibility-field"><label for="eligibility-country-search">Current country of residence</label><div class="eligibility-country-picker"><input id="eligibility-country-search" type="search" autocomplete="off" placeholder="Search by country" role="combobox" aria-autocomplete="list" aria-controls="eligibility-country-list" aria-expanded="false" required><input id="eligibility-country" name="country" type="hidden"><div class="eligibility-country-list" id="eligibility-country-list" role="listbox" hidden>'+countries.map(function(c){return '<button type="button" role="option" data-country-code="'+c[0]+'" data-country-name="'+c[1]+'">'+c[1]+'</button>';}).join("")+'<p class="eligibility-country-empty" hidden>No country found</p></div></div></div><button class="eligibility-submit" type="submit">Check eligibility and continue</button><p class="eligibility-note">Your selection stays in this browser session. Enter your name and email once in the official application form on the next step.</p><div class="eligibility-result" hidden aria-live="polite"></div></form></div>';
  document.body.appendChild(gate);
  var form=gate.querySelector("form"),countryInput=gate.querySelector("#eligibility-country"),countrySearch=gate.querySelector("#eligibility-country-search"),countryList=gate.querySelector("#eligibility-country-list"),countryOptions=Array.prototype.slice.call(countryList.querySelectorAll("[data-country-code]")),countryEmpty=countryList.querySelector(".eligibility-country-empty"),result=gate.querySelector(".eligibility-result"),closeButton=gate.querySelector(".eligibility-close");

  function eligible(data){return data&&data.country&&data.country!=="OTHER";}
  function openCountryList(){countryList.hidden=false;countrySearch.setAttribute("aria-expanded","true");filterCountries();}
  function closeCountryList(){countryList.hidden=true;countrySearch.setAttribute("aria-expanded","false");}
  function filterCountries(){var query=countrySearch.value.trim().toLowerCase(),visible=0;countryOptions.forEach(function(option){var show=!query||option.getAttribute("data-country-name").toLowerCase().indexOf(query)!==-1;option.hidden=!show;if(show)visible++;});countryEmpty.hidden=visible!==0;}
  function selectCountry(option){countryInput.value=option.getAttribute("data-country-code");countrySearch.value=option.getAttribute("data-country-name");countrySearch.setCustomValidity("");countryOptions.forEach(function(item){item.setAttribute("aria-selected",item===option?"true":"false");});closeCountryList();countrySearch.focus();}
  function openGate(){lastFocus=document.activeElement;result.hidden=true;result.className="eligibility-result";result.innerHTML="";countryInput.value=saved&&saved.country||"";countrySearch.value=countryNames[countryInput.value]||"";countrySearch.setCustomValidity("");gate.hidden=false;document.body.style.overflow="hidden";setTimeout(function(){countrySearch.focus();openCountryList();},0);}
  function closeGate(){closeCountryList();gate.hidden=true;document.body.style.overflow="";if(lastFocus&&lastFocus.focus)lastFocus.focus();}
  function applicationTrigger(){return document.querySelector("[data-job-apply-trigger]");}
  function continueToApplication(){closeGate();var trigger=applicationTrigger();if(trigger)trigger.click();}
  function returnToDescription(){var panel=document.getElementById("job-apply-panel"),description=document.getElementById("job-description-panel");if(panel)panel.hidden=true;if(description)description.hidden=false;document.body.classList.remove("job-apply-open");}
  function showSummary(){
    var panel=document.getElementById("job-apply-panel");if(!panel||!eligible(saved))return;
    var summary=panel.querySelector(".eligibility-summary");
    if(!summary){summary=document.createElement("section");summary.className="eligibility-summary";var header=panel.querySelector(".job-inline-apply-header");if(header)header.insertAdjacentElement("afterend",summary);else panel.insertBefore(summary,panel.firstChild);}
    summary.innerHTML='<div class="eligibility-summary-head"><h2>Eligibility confirmed</h2><button type="button" data-eligibility-change>Change country</button></div><div class="eligibility-summary-grid"><span><strong>Current residence:</strong>'+escapeHtml(countryNames[saved.country]||saved.country)+'</span></div><p class="eligibility-summary-note">Please enter your full name, email and remaining details in the official application form below.</p>';
    summary.querySelector("[data-eligibility-change]").addEventListener("click",openGate);
  }
  function escapeHtml(value){var node=document.createElement("div");node.textContent=value||"";return node.innerHTML;}

  document.addEventListener("click",function(event){
    var trigger=event.target.closest("[data-job-apply-trigger], [data-slow-scroll-target='how-to-apply']");
    if(!trigger)return;
    if(eligible(saved)){if(trigger.hasAttribute("data-slow-scroll-target")){event.preventDefault();event.stopImmediatePropagation();continueToApplication();}else{setTimeout(showSummary,0);}return;}
    event.preventDefault();event.stopImmediatePropagation();openGate();
  },true);
  closeButton.addEventListener("click",closeGate);
  gate.addEventListener("click",function(event){var option=event.target.closest("[data-country-code]");if(option){selectCountry(option);return;}if(event.target===gate)closeGate();else if(!event.target.closest(".eligibility-country-picker"))closeCountryList();});
  countrySearch.addEventListener("focus",openCountryList);
  countrySearch.addEventListener("input",function(){countryInput.value="";countrySearch.setCustomValidity("");openCountryList();});
  countrySearch.addEventListener("keydown",function(event){if(event.key==="ArrowDown"){event.preventDefault();openCountryList();var visible=countryOptions.filter(function(option){return !option.hidden;});if(visible.length)visible[0].focus();}else if(event.key==="Escape"){event.stopPropagation();closeCountryList();}});
  countryList.addEventListener("keydown",function(event){var visible=countryOptions.filter(function(option){return !option.hidden;}),index=visible.indexOf(document.activeElement);if(event.key==="ArrowDown"&&index<visible.length-1){event.preventDefault();visible[index+1].focus();}else if(event.key==="ArrowUp"){event.preventDefault();if(index>0)visible[index-1].focus();else countrySearch.focus();}else if(event.key==="Escape"){event.stopPropagation();closeCountryList();countrySearch.focus();}});
  document.addEventListener("keydown",function(event){if(!gate.hidden&&event.key==="Escape")closeGate();});
  form.addEventListener("submit",function(event){
    event.preventDefault();if(!countryInput.value){countrySearch.setCustomValidity("Please select a country from the list.");countrySearch.reportValidity();openCountryList();return;}if(!form.reportValidity())return;
    saved={country:countryInput.value};
    try{sessionStorage.setItem(STORAGE_KEY,JSON.stringify(saved));}catch(e){}
    if(!eligible(saved)){
      returnToDescription();
      result.hidden=false;result.className="eligibility-result eligibility-result--blocked";
      result.innerHTML='<h3>This role is not available for your location</h3><p>You must currently live in Europe to apply for this vacancy.</p><div class="eligibility-result-actions"><button class="eligibility-secondary" type="button" data-edit-residence>Change country</button><a class="eligibility-secondary" href="/jobs/">Browse other jobs</a></div>';
      result.querySelector("[data-edit-residence]").addEventListener("click",function(){countrySearch.focus();openCountryList();});return;
    }
    continueToApplication();setTimeout(showSummary,0);
  });
  if(location.hash==="#job-apply-panel"&&!eligible(saved)){history.replaceState(null,"",location.pathname+location.search);setTimeout(openGate,0);}else if(location.hash==="#job-apply-panel"){setTimeout(showSummary,0);}
})();
