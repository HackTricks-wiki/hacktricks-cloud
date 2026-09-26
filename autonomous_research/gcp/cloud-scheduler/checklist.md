# Cloud Scheduler — open leads

## Authenticated-job update boundary
- [ ] Pre-create a limited caller and grant `cloudscheduler.jobs.update` long enough for IAM to
      propagate before creating the disposable test job. Then PATCH only `http_target.uri` while
      omitting the existing OAuth/OIDC fields. Determine whether Scheduler preserves the attached
      identity without reevaluating `iam.serviceAccounts.actAs` or rejects the update on `actAs`.
- [ ] Repeat with `http_target.body`, headers and method in separate update masks, and capture
      `authorizationInfo` for successful and denied requests. Keep the job paused with a far-future
      schedule and delete every resource immediately after the test.
- [ ] If URI-only update preserves OIDC without `actAs`, test an endpoint that records the token
      without trusting its audience. Separately test the OAuth path against a harmless read-only
      Google API. Never point a test job at a mutating production target.

## Full-view response boundary
- [ ] With a disposable job containing non-secret marker values, compare get/list responses for
      custom roles containing only get or list, then add `cloudscheduler.jobs.fullView`. Record
      exactly which body, header and identity fields are redacted without `fullView`.
