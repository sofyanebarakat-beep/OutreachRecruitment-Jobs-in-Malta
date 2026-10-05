# GA4 conversion tracking

The site keeps its existing GTM container (`GTM-K8C6D5ZH`) and Google tag
(`G-FK09PDN6TK`). `assets/analytics-events.js` sends these conversion events:

- `apply_click`: only after the trusted `careers-page.com` application iframe
  reports a successful submission. Parameters: `job_title`, `job_id`,
  `job_category`, `job_location`, `application_method`, `application_stage`, and
  `page_location`.
- `employer_lead_submit`: only after a same-origin form displays its Webflow
  success state, or the trusted `outreachrecruitment.eu/support` iframe reports
  a successful submission. Parameters: `lead_type`, `form_name`, and
  `page_location`.

No names, email addresses, telephone numbers, CV data, messages, or other form
values are sent to GA4.

## Employer iframe success contract

The employer form is a separate application on `outreachrecruitment.eu`. After
its database insert succeeds, that application must notify its parent page:

```js
window.parent.postMessage(
  { type: "employer_form_success", success: true },
  "https://outreachrecruitment.net"
);
```

The call belongs immediately after the successful `support_cases` insert, not
on click, validation, form view, email sending, or failed submission. The parent
accepts this message only from HTTPS `outreachrecruitment.eu` origins and sends
no form values to GA4.

In GA4, mark `apply_click` and `employer_lead_submit` as key events. Verify both
with DebugView or Realtime after deploying both the website and iframe change.
