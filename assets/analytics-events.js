(function () {
  "use strict";

  function send(name, params) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", name, Object.assign({ transport_type: "beacon" }, params || {}));
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[href]");
    if (!link) return;
    var href = link.href || "";
    var label = (link.textContent || "").trim().replace(/\s+/g, " ").slice(0, 120);
    if (/careers-page\.com\/jobs\/.+\/apply/i.test(href)) {
      send("apply_click", {
        event_category: "Jobs",
        event_label: label || document.title,
        job_url: href,
        page_location: location.href
      });
    }
    if (/chatgpt\.com|perplexity\.ai|gemini\.google\.com/i.test(href)) {
      send("ai_outbound_click", { link_url: href, page_location: location.href });
    }
  }, true);

  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    var id = ((form.id || "") + " " + (form.getAttribute("name") || "") + " " +
      (form.getAttribute("data-name") || "")).toLowerCase();
    if (/newsletter|email-form/.test(id)) return;
    if (/employer|contact|enquiry|inquiry|partner|client/.test(id + " " + location.pathname.toLowerCase())) {
      send("employer_lead_submit", {
        event_category: "Employer Lead",
        event_label: form.getAttribute("data-name") || form.id || document.title,
        page_location: location.href
      });
    }
  }, true);
})();
