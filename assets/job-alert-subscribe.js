(function(){
  "use strict";
  var URL="https://atcitaqyraeqngcsaeun.supabase.co";
  var KEY="sb_publishable_cpLonCcSvdifHfBvdtlDWQ_cblbcgKY";
  window.OutreachJobAlerts={
    subscribe:function(data){
      return fetch(URL+"/rest/v1/rpc/subscribe_job_alert_v2",{
        method:"POST",
        headers:{"Content-Type":"application/json","apikey":KEY,"Authorization":"Bearer "+KEY},
        body:JSON.stringify({
          p_email:data.email,
          p_full_name:data.fullName,
          p_country_code:data.countryCode,
          p_country_name:data.countryName,
          p_source_type:data.sourceType,
          p_source_job:data.sourceJob||null,
          p_source_url:data.sourceUrl||location.href.split("#")[0],
          p_job_category:data.jobCategory||null
        })
      }).then(function(response){
        if(response.ok)return response.json();
        return response.json().catch(function(){return{};}).then(function(body){throw new Error(body.message||"We couldn't save your alert. Please try again.");});
      });
    }
  };
})();
