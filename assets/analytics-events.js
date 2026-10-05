(function () {
  "use strict";

  var sent = Object.create(null);

  function clean(value, limit) {
    return String(value == null ? "" : value).trim().replace(/\s+/g, " ").slice(0, limit || 100);
  }

  function sendOnce(name, key, params) {
    var dedupeKey = name + ":" + key;
    if (sent[dedupeKey]) return;
    sent[dedupeKey] = true;
    var safe = { transport_type: "beacon" };
    Object.keys(params || {}).forEach(function (param) {
      var value = params[param];
      if (value !== "" && value != null) safe[param] = value;
    });
    if (typeof window.gtag === "function") {
      window.gtag("event", name, safe);
    } else {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push(Object.assign({ event: name }, safe));
    }
  }

  function parseMessage(raw) {
    if (raw && typeof raw === "object") return raw;
    if (typeof raw !== "string") return null;
    try { return JSON.parse(raw); } catch (_) { return { type: raw }; }
  }

  function successSignal(data, subject) {
    if (!data || typeof data !== "object") return false;
    var words = [data.type, data.event, data.action, data.status, data.message]
      .filter(Boolean).join(" ").toLowerCase();
    var completed = data.success === true || data.submitted === true ||
      /success|complete|completed|thank|received/.test(words);
    return completed && ((data.success === true || data.submitted === true) ||
      new RegExp(subject).test(words + " " + (data.form || "") + " " + (data.formType || "")));
  }

  function jobData() {
    var schema = null;
    document.querySelectorAll('script[type="application/ld+json"]').forEach(function (node) {
      if (schema) return;
      try {
        var parsed = JSON.parse(node.textContent || "{}");
        var entries = Array.isArray(parsed) ? parsed : [parsed];
        schema = entries.find(function (entry) { return entry && entry["@type"] === "JobPosting"; }) || null;
      } catch (_) {}
    });
    var template = document.getElementById("job-apply-frame-template");
    var frame = document.querySelector("iframe.outreach-apply-frame") ||
      (template && template.content && template.content.querySelector("iframe.outreach-apply-frame"));
    var applyUrl = frame ? (frame.getAttribute("data-src") || frame.getAttribute("src") || "") : "";
    var idMatch = applyUrl.match(/\/jobs\/([^/]+)\/apply/i);
    var category = document.querySelector(".job-header-meta .job-meta-item");
    var locationValue = schema && schema.jobLocation && schema.jobLocation.address;
    if (locationValue && typeof locationValue === "object") {
      locationValue = [locationValue.addressLocality, locationValue.addressCountry].filter(Boolean).join(", ");
    }
    return {
      job_title: clean(schema && schema.title || document.querySelector("h1") && document.querySelector("h1").textContent || document.title, 100),
      job_id: clean(schema && schema.identifier && schema.identifier.value || idMatch && idMatch[1] || location.pathname.replace(/^\/jobs\/?|\/$/g, ""), 100),
      job_category: clean(schema && schema.occupationalCategory || category && category.textContent, 100),
      job_location: clean(locationValue, 100),
      application_method: frame ? "embedded_form" : "external_form",
      page_location: location.href
    };
  }

  function trackApplicationSuccess() {
    var details = jobData();
    if (!details.job_id && !/^\/jobs\//.test(location.pathname)) return;
    details.application_stage = "submitted";
    sendOnce("apply_click", details.job_id || location.pathname, details);
  }

  function trackEmployerSuccess(source) {
    sendOnce("employer_lead_submit", location.pathname, {
      lead_type: "employer_recruitment_enquiry",
      form_name: clean(source || "employer_support_form", 100),
      page_location: location.href
    });
  }

  // Opening a form is not a conversion. Emit only after a trusted embedded
  // application or employer-support form reports a successful submission.
  window.addEventListener("message", function (event) {
    var data = parseMessage(event.data);
    if (/^https:\/\/([a-z0-9-]+\.)?careers-page\.com$/i.test(event.origin) &&
        successSignal(data, "submit|application|candidate|apply")) {
      trackApplicationSuccess();
    }
    if (/^https:\/\/([a-z0-9-]+\.)?outreachrecruitment\.eu$/i.test(event.origin) &&
        document.querySelector('iframe[src*="outreachrecruitment.eu/support"]') &&
        successSignal(data, "submit|support|contact|employer|lead|enquiry|inquiry|form")) {
      trackEmployerSuccess(data && (data.form || data.formType || data.type));
    }
  });

  // Support same-origin/Webflow employer forms if one is added later. Observe
  // the success panel instead of counting a submit attempt or validation error.
  function watchEmployerForms() {
    document.querySelectorAll(".w-form").forEach(function (wrapper) {
      var form = wrapper.querySelector("form");
      var done = wrapper.querySelector(".w-form-done");
      if (!form || !done || /newsletter|email-form/i.test((form.id || "") + " " + (form.name || ""))) return;
      var identity = [form.id, form.name, form.getAttribute("data-name"), location.pathname].filter(Boolean).join(" ");
      if (!/employer|contact|enquiry|inquiry|partner|client/i.test(identity)) return;
      new MutationObserver(function () {
        if (getComputedStyle(done).display !== "none" && done.getClientRects().length) {
          trackEmployerSuccess(form.getAttribute("data-name") || form.id || "employer_form");
        }
      }).observe(done, { attributes: true, attributeFilter: ["class", "style", "hidden"] });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", watchEmployerForms);
  else watchEmployerForms();

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[href]");
    if (!link) return;
    var href = link.href || "";
    if (/chatgpt\.com|perplexity\.ai|gemini\.google\.com/i.test(href)) {
      sendOnce("ai_outbound_click", href, { link_url: href, page_location: location.href });
    }
  }, true);
})();
