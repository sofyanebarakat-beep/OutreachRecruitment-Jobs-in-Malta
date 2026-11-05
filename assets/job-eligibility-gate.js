(function(){
  "use strict";
  var STORAGE_KEY="or-hotel-manager-eligibility";
  var countryCodes="AF AL DZ AD AO AG AR AM AU AT AZ BS BH BD BB BY BE BZ BJ BT BO BA BW BR BN BG BF BI CV KH CM CA CF TD CL CN CO KM CG CD CR CI HR CU CY CZ DK DJ DM DO EC EG SV GQ ER EE SZ ET FJ FI FR GA GM GE DE GH GR GD GT GN GW GY HT HN HU IS IN ID IR IQ IE IL IT JM JP JO KZ KE KI KP KR KW KG LA LV LB LS LR LY LI LT LU MG MW MY MV ML MT MH MR MU MX FM MD MC MN ME MA MZ MM NA NR NP NL NZ NI NE NG MK NO OM PK PW PS PA PG PY PE PH PL PT QA RO RU RW KN LC VC WS SM ST SA SN RS SC SL SG SK SI SB SO ZA SS ES LK SD SR SE CH SY TW TJ TZ TH TL TG TO TT TN TR TM TV UG UA AE GB US UY UZ VU VA VE VN YE ZM ZW XK".split(" ");
  var europeCodes="AL AD AM AT AZ BY BE BA BG HR CY CZ DK EE FI FR GE DE GR HU IS IE IT XK KZ LV LI LT LU MT MD MC ME NL MK NO PL PT RO RU SM RS SK SI ES SE CH TR UA GB VA".split(" ");
  var displayNames=typeof Intl!=="undefined"&&Intl.DisplayNames?new Intl.DisplayNames(["en"],{type:"region"}):null;
  function flag(code){return code.replace(/./g,function(letter){return String.fromCodePoint(127397+letter.charCodeAt(0));});}
  var countries=countryCodes.map(function(code){var name=code==="XK"?"Kosovo":displayNames?displayNames.of(code):code;return [code,flag(code)+" "+name];}).sort(function(a,b){return a[1].slice(a[1].indexOf(" ")+1).localeCompare(b[1].slice(b[1].indexOf(" ")+1));});
  var countryNames={};countries.forEach(function(c){countryNames[c[0]]=c[1];});
  var saved=null,lastFocus=null;
  try{saved=JSON.parse(sessionStorage.getItem(STORAGE_KEY)||"null");}catch(e){saved=null;}

  var gate=document.createElement("div");
  gate.className="eligibility-gate";gate.hidden=true;
  gate.innerHTML='<div class="eligibility-dialog" role="dialog" aria-modal="true" aria-labelledby="eligibility-title"><button class="eligibility-close" type="button" aria-label="Close eligibility check">×</button><p class="eligibility-eyebrow">Before you apply</p><h2 class="eligibility-title" id="eligibility-title">Check your eligibility</h2><p class="eligibility-intro">This vacancy is currently open to candidates who live in Europe. Search for your current country of residence to continue.</p><form class="eligibility-form"><div class="eligibility-field"><label for="eligibility-country-search">Current country of residence</label><div class="eligibility-country-picker"><input id="eligibility-country-search" type="search" autocomplete="off" placeholder="Search by country" role="combobox" aria-autocomplete="list" aria-controls="eligibility-country-list" aria-expanded="false" required><input id="eligibility-country" name="country" type="hidden"><div class="eligibility-country-list" id="eligibility-country-list" role="listbox" hidden>'+countries.map(function(c){return '<button type="button" role="option" data-country-code="'+c[0]+'" data-country-name="'+c[1]+'">'+c[1]+'</button>';}).join("")+'<p class="eligibility-country-empty" hidden>No country found</p></div></div></div><div class="eligibility-result" hidden aria-live="polite"></div><button class="eligibility-submit" type="submit" disabled>Choose your country to continue</button><p class="eligibility-note">Your selection stays in this browser session. Enter your name and email once in the official application form on the next step.</p></form></div>';
  document.body.appendChild(gate);
  var form=gate.querySelector("form"),countryInput=gate.querySelector("#eligibility-country"),countrySearch=gate.querySelector("#eligibility-country-search"),countryList=gate.querySelector("#eligibility-country-list"),countryOptions=Array.prototype.slice.call(countryList.querySelectorAll("[data-country-code]")),countryEmpty=countryList.querySelector(".eligibility-country-empty"),result=gate.querySelector(".eligibility-result"),submitButton=gate.querySelector(".eligibility-submit"),closeButton=gate.querySelector(".eligibility-close");
  var neighbourhood=document.getElementById("neighbourhood-desc");if(neighbourhood){var locationSection=neighbourhood.closest(".stack");if(locationSection)locationSection.remove();}

  function eligible(data){return data&&europeCodes.indexOf(data.country)!==-1;}
  function openCountryList(){countryList.hidden=false;countrySearch.setAttribute("aria-expanded","true");filterCountries();}
  function closeCountryList(){countryList.hidden=true;countrySearch.setAttribute("aria-expanded","false");}
  function filterCountries(){var query=countrySearch.value.trim().toLowerCase(),visible=0;countryOptions.forEach(function(option){var show=!query||option.getAttribute("data-country-name").toLowerCase().indexOf(query)!==-1;option.hidden=!show;if(show)visible++;});countryEmpty.hidden=visible!==0;}
  function browserCountry(){var locales=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language];for(var i=0;i<locales.length;i++){var region="";try{region=typeof Intl.Locale!=="undefined"?new Intl.Locale(locales[i]).region:"";}catch(e){}if(!region){var match=String(locales[i]||"").match(/[-_]([A-Za-z]{2})$/);region=match?match[1].toUpperCase():"";}if(countryNames[region])return region;}return "";}
  function showEligibilityResult(code,suggested){var data={country:code},label=countryNames[code]||code;result.hidden=false;if(eligible(data)){result.className="eligibility-result eligibility-result--allowed";result.innerHTML='<h3>You can apply for this role</h3><p>'+(suggested?'Suggested from your browser settings: '+escapeHtml(label)+'. Please change it if this is not your current residence.':'Your selected residence, '+escapeHtml(label)+', meets the location requirement.')+'</p>';submitButton.disabled=false;submitButton.textContent="Continue to application";}else{result.className="eligibility-result eligibility-result--blocked";result.innerHTML='<h3>This role is not available for your location</h3><p>'+(suggested?'Your browser suggests '+escapeHtml(label)+'. ':'')+'You must currently live in Europe to apply for this vacancy.</p>';submitButton.disabled=true;submitButton.textContent="Not eligible for this role";returnToDescription();}}
  function selectCountry(option,suggested){var code=option.getAttribute("data-country-code");countryInput.value=code;countrySearch.value=option.getAttribute("data-country-name");countrySearch.setCustomValidity("");countryOptions.forEach(function(item){item.setAttribute("aria-selected",item===option?"true":"false");});showEligibilityResult(code,!!suggested);closeCountryList();countrySearch.focus();}
  function openGate(){lastFocus=document.activeElement;result.hidden=true;result.className="eligibility-result";result.innerHTML="";submitButton.disabled=true;submitButton.textContent="Choose your country to continue";var code=saved&&saved.country||browserCountry();var option=code&&countryList.querySelector('[data-country-code="'+code+'"]');countryInput.value="";countrySearch.value="";countrySearch.setCustomValidity("");gate.hidden=false;document.body.style.overflow="hidden";if(option)selectCountry(option,!saved);setTimeout(function(){countrySearch.focus();openCountryList();},0);}
  function closeGate(){closeCountryList();gate.hidden=true;document.body.style.overflow="";if(lastFocus&&lastFocus.focus)lastFocus.focus();}
  function applicationTrigger(){return document.querySelector("[data-job-apply-trigger]");}
  function continueToApplication(){closeGate();var trigger=applicationTrigger();if(trigger)trigger.click();}
  function returnToDescription(){var panel=document.getElementById("job-apply-panel"),description=document.getElementById("job-description-panel");if(panel)panel.hidden=true;if(description)description.hidden=false;document.body.classList.remove("job-apply-open");}
  function showSummary(){
    var panel=document.getElementById("job-apply-panel");if(!panel||!eligible(saved))return;
    var summary=panel.querySelector(".eligibility-summary");
    if(!summary){summary=document.createElement("section");summary.className="eligibility-summary";var headerText=panel.querySelector(".job-inline-apply-header .text");var existingIntro=headerText&&headerText.querySelector(".text-medium");if(existingIntro)existingIntro.remove();if(headerText)headerText.appendChild(summary);else panel.insertBefore(summary,panel.firstChild);}
    summary.innerHTML='<div class="eligibility-summary-head"><h2>Eligibility confirmed</h2></div><p class="eligibility-summary-lead">Apply now — if you\'re a match, we\'ll be in touch to arrange an interview.</p><div class="eligibility-summary-grid"><span><strong>Current residence:</strong>'+escapeHtml(countryNames[saved.country]||saved.country)+'</span></div><p class="eligibility-summary-note">Please enter your full name, email and remaining details in the official application form below.</p>';
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
  countrySearch.addEventListener("input",function(){countryInput.value="";countrySearch.setCustomValidity("");result.hidden=true;submitButton.disabled=true;submitButton.textContent="Choose your country to continue";openCountryList();});
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
      result.innerHTML='<h3>This role is not available for your location</h3><p>You must currently live in Europe to apply for this vacancy.</p><div class="eligibility-result-actions"><a class="eligibility-secondary" href="/jobs/">Browse other jobs</a></div>';return;
    }
    continueToApplication();setTimeout(showSummary,0);
  });
  if(location.hash==="#job-apply-panel"&&!eligible(saved)){history.replaceState(null,"",location.pathname+location.search);setTimeout(openGate,0);}else if(location.hash==="#job-apply-panel"){setTimeout(showSummary,0);}
})();
