(function(){
  "use strict";
  var STORAGE_KEY="or-hotel-manager-eligibility-v3";
  var countryCodes="AF AL DZ AD AO AG AR AM AU AT AZ BS BH BD BB BY BE BZ BJ BT BO BA BW BR BN BG BF BI CV KH CM CA CF TD CL CN CO KM CG CD CR CI HR IQ IE IL IT JM JP JO KZ KE KI KR KW KG LA LV LB LS LR LY LI LT LU MG MW MY MV ML MT MH MR MU MX FM MD MC MN ME MA MZ MM NA NR NP NL NZ NI NE NG MK NO OM PK PW PS PA PG PY PE PH PL PT QA RO RU RW KN LC VC WS SM ST SA SN RS SC SL SG SK SI SB SO ZA SS ES LK SD SR SE CH SY TW TJ TZ TH TL TG TO TT TN TR TM TV UG UA AE GB US UY UZ VU VA VE VN YE ZM ZW XK".split(" ");
  var names=typeof Intl!=="undefined"&&Intl.DisplayNames?new Intl.DisplayNames(["en"],{type:"region"}):null;
  var countries=countryCodes.map(function(code){return[code,code==="XK"?"Kosovo":names?names.of(code):code];}).sort(function(a,b){return a[1].localeCompare(b[1]);});

  function savedResidence(){try{return JSON.parse(sessionStorage.getItem(STORAGE_KEY)||"null");}catch(e){return null;}}
  function render(){
    var panel=document.getElementById("job-apply-panel"),mount=document.getElementById("job-apply-frame-mount");if(!panel||!mount||panel.querySelector("[data-after-apply-alert]"))return;
    var residence=savedResidence()||{};
    var section=document.createElement("section");section.className="after-apply-alert";section.setAttribute("data-after-apply-alert","");
    section.innerHTML='<div class="after-apply-alert__glow" aria-hidden="true"></div><div class="after-apply-alert__icon" aria-hidden="true">✦</div><div class="after-apply-alert__copy"><span class="after-apply-alert__eyebrow">Optional · after your application</span><h2>Keep your profile open to future opportunities</h2><p>Complete your Manatal application below, then optionally join our alert list. We’ll email you when another suitable role is available for your current location.</p></div><form class="after-apply-alert__form"><div class="after-apply-alert__fields"><label><span>Full name</span><input name="full_name" type="text" autocomplete="name" maxlength="120" required></label><label><span>Email address</span><input name="email" type="email" autocomplete="email" maxlength="254" required></label><label><span>Current country of residence</span><select name="country" required><option value="">Choose your country</option>'+countries.map(function(c){return'<option value="'+c[0]+'"'+(residence.country===c[0]?' selected':'')+'>'+c[1]+'</option>';}).join("")+'</select></label></div><label class="after-apply-alert__consent"><input name="consent" type="checkbox" required><span>Yes, keep my details and send me relevant job alerts. I can unsubscribe at any time.</span></label><button type="submit">Keep me updated <span aria-hidden="true">→</span></button><p class="after-apply-alert__status" role="status" aria-live="polite"></p></form>';
    panel.insertBefore(section,mount);
    requestAnimationFrame(function(){section.classList.add("is-visible");});
    section.querySelector("form").addEventListener("submit",function(event){
      event.preventDefault();var form=event.currentTarget;if(!form.reportValidity())return;
      var button=form.querySelector("button"),status=form.querySelector("[role=status]"),select=form.elements.country;
      button.disabled=true;button.textContent="Saving your alert…";status.textContent="";
      window.OutreachJobAlerts.subscribe({email:form.elements.email.value,fullName:form.elements.full_name.value,countryCode:select.value,countryName:select.options[select.selectedIndex].text,sourceType:"post_application",sourceJob:"Hotel General Manager",sourceUrl:location.href.split("#")[0],jobCategory:"Hospitality"}).then(function(){
        form.innerHTML='<div class="after-apply-alert__success"><span aria-hidden="true">✓</span><div><strong>You’re on the list.</strong><p>We’ll let you know when another suitable opportunity becomes available.</p></div></div>';
      }).catch(function(error){button.disabled=false;button.innerHTML='Keep me updated <span aria-hidden="true">→</span>';status.textContent=error.message||"We couldn’t save your alert. Please try again.";status.classList.add("is-error");});
    });
  }
  render();
})();
