(function(){
  "use strict";
  var STORAGE_KEY="or-hotel-manager-eligibility-v3";
  var countryCodes="AF AL DZ AD AO AG AR AM AU AT AZ BS BH BD BB BY BE BZ BJ BT BO BA BW BR BN BG BF BI CV KH CM CA CF TD CL CN CO KM CG CD CR CI HR IQ IE IL IT JM JP JO KZ KE KI KR KW KG LA LV LB LS LR LY LI LT LU MG MW MY MV ML MT MH MR MU MX FM MD MC MN ME MA MZ MM NA NR NP NL NZ NI NE NG MK NO OM PK PW PS PA PG PY PE PH PL PT QA RO RU RW KN LC VC WS SM ST SA SN RS SC SL SG SK SI SB SO ZA SS ES LK SD SR SE CH SY TW TJ TZ TH TL TG TO TT TN TR TM TV UG UA AE GB US UY UZ VU VA VE VN YE ZM ZW XK".split(" ");
  var names=typeof Intl!=="undefined"&&Intl.DisplayNames?new Intl.DisplayNames(["en"],{type:"region"}):null;
  var countries=countryCodes.map(function(code){return[code,code==="XK"?"Kosovo":names?names.of(code):code];}).sort(function(a,b){return a[1].localeCompare(b[1]);});

  function savedResidence(){try{return JSON.parse(sessionStorage.getItem(STORAGE_KEY)||"null");}catch(e){return null;}}
  function render(){
    var panel=document.getElementById("job-apply-panel"),mount=document.getElementById("job-apply-frame-mount");if(!panel||!mount||document.querySelector("[data-job-alert-drawer]"))return;
    var residence=savedResidence()||{};
    var residenceNote=residence.country?'<small class="job-alert-country-note">Same residence selected in your eligibility check.</small>':'';
    var notice=document.createElement("aside");notice.className="job-alert-notice";notice.innerHTML='<div class="job-alert-notice__icon" aria-hidden="true">✓</div><div class="job-alert-notice__copy"><span>Optional</span><strong>Application completed? Stay open to similar opportunities.</strong><p>Join our optional job alerts and we’ll contact you when a suitable role matches your location.</p></div><button type="button" data-open-job-alert>Join job alerts</button>';
    panel.appendChild(notice);
    function placeNotice(){var frameWrap=mount.querySelector(".outreach-apply-frame-wrap");if(frameWrap&&frameWrap.nextElementSibling!==notice)frameWrap.insertAdjacentElement("afterend",notice);}

    var launcher=document.createElement("button");launcher.type="button";launcher.className="job-alert-launcher";launcher.innerHTML='<span aria-hidden="true">✦</span> Applied? Keep me updated';launcher.setAttribute("aria-label","Open the optional job alert form");document.body.appendChild(launcher);

    var overlay=document.createElement("div");overlay.className="job-alert-drawer-overlay";overlay.hidden=true;overlay.setAttribute("data-job-alert-drawer","");
    overlay.innerHTML='<section class="job-alert-drawer" role="dialog" aria-modal="true" aria-labelledby="job-alert-drawer-title"><button class="job-alert-drawer__close" type="button" aria-label="Close job alert form">×</button><div class="job-alert-drawer__icon" aria-hidden="true">✦</div><span class="job-alert-drawer__eyebrow">Optional job alerts</span><h2 id="job-alert-drawer-title">Stay open to similar opportunities</h2><p>Your application is already handled through Manatal. Join our alerts if you would also like to hear about other suitable roles.</p><form class="job-alert-drawer__form"><label><span>Full name</span><input name="full_name" type="text" autocomplete="name" maxlength="120" required></label><label><span>Email address</span><input name="email" type="email" autocomplete="email" maxlength="254" required></label><label><span>Current country of residence</span><select name="country" required><option value="">Choose your country</option>'+countries.map(function(c){return'<option value="'+c[0]+'"'+(residence.country===c[0]?' selected':'')+'>'+c[1]+'</option>';}).join("")+'</select>'+residenceNote+'</label><label class="job-alert-drawer__consent"><input name="consent" type="checkbox" required><span>Yes, keep my details and send me relevant job alerts. I can unsubscribe at any time.</span></label><button class="job-alert-drawer__submit" type="submit">Save my job alert <span aria-hidden="true">→</span></button><p class="job-alert-drawer__status" role="status" aria-live="polite"></p></form><p class="job-alert-drawer__privacy">This does not change or resubmit your application.</p></section>';
    document.body.appendChild(overlay);
    var drawer=overlay.querySelector(".job-alert-drawer"),lastFocus=null;
    function openDrawer(){lastFocus=document.activeElement;overlay.hidden=false;requestAnimationFrame(function(){overlay.classList.add("is-open");});document.body.classList.add("job-alert-drawer-open");setTimeout(function(){drawer.querySelector('input[name="full_name"]').focus();},180);}
    function closeDrawer(){overlay.classList.remove("is-open");document.body.classList.remove("job-alert-drawer-open");setTimeout(function(){overlay.hidden=true;if(lastFocus&&lastFocus.focus)lastFocus.focus();},260);}
    launcher.addEventListener("click",openDrawer);notice.querySelector("[data-open-job-alert]").addEventListener("click",openDrawer);overlay.querySelector(".job-alert-drawer__close").addEventListener("click",closeDrawer);
    var launcherReady=false,launcherTimer=null;
    function updateLauncher(){var applyOpen=document.body.classList.contains("job-apply-open");if(!applyOpen){if(launcherTimer){clearTimeout(launcherTimer);launcherTimer=null;}launcherReady=false;launcher.classList.remove("is-ready");return;}if(launcherReady){launcher.classList.add("is-ready");return;}if(!launcherTimer){launcherTimer=setTimeout(function(){launcherTimer=null;if(document.body.classList.contains("job-apply-open")){launcherReady=true;launcher.classList.add("is-ready");}},10000);}}
    new MutationObserver(function(){placeNotice();updateLauncher();}).observe(mount,{childList:true,subtree:true});new MutationObserver(updateLauncher).observe(panel,{attributes:true,attributeFilter:["hidden"]});setTimeout(function(){placeNotice();updateLauncher();},300);
    overlay.addEventListener("click",function(event){if(event.target===overlay)closeDrawer();});document.addEventListener("keydown",function(event){if(event.key==="Escape"&&!overlay.hidden)closeDrawer();});
    overlay.querySelector("form").addEventListener("submit",function(event){
      event.preventDefault();var form=event.currentTarget;if(!form.reportValidity())return;
      var button=form.querySelector(".job-alert-drawer__submit"),status=form.querySelector("[role=status]"),select=form.elements.country;
      button.disabled=true;button.textContent="Checking your details…";status.textContent="";
      window.OutreachJobAlerts.subscribe({email:form.elements.email.value,fullName:form.elements.full_name.value,countryCode:select.value,countryName:select.options[select.selectedIndex].text,sourceType:"post_application",sourceJob:"Hotel General Manager",sourceUrl:location.href.split("#")[0],jobCategory:"Hospitality"}).then(function(result){
        var duplicate=result&&result.already_subscribed,reactivated=result&&result.reactivated;
        form.innerHTML='<div class="job-alert-drawer__success"><span aria-hidden="true">✓</span><div><strong>'+(duplicate?'You’re already on the list.':reactivated?'Welcome back — your alerts are active.':'You’re on the list.')+'</strong><p>'+(duplicate?'No duplicate was created. We’ll continue sending relevant opportunities to this email.':'We’ll let you know when another suitable opportunity becomes available.')+'</p></div></div>';
        notice.querySelector("strong").textContent=duplicate?'You are already subscribed to job alerts.':'Your job alerts are active.';notice.querySelector("button").textContent="View confirmation";
      }).catch(function(error){button.disabled=false;button.innerHTML='Save my job alert <span aria-hidden="true">→</span>';status.textContent=error.message||"We couldn’t save your alert. Please try again.";status.classList.add("is-error");});
    });
  }
  render();
})();
