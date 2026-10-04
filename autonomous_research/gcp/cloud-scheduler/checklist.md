# Cloud Scheduler — open leads

## Independent cross-review completed 2026-09-28

- [x] Re-open the current official HTTP-token, App Engine, Pub/Sub, run-only, service-agent and audit
      contracts after the rewrite.
- [x] Confirm all four retained H3s distinguish caller authorization, delivery identity, stored
      target behavior, downstream authority and telemetry.

## Authenticated-job update boundary
- [x] Pre-create a limited caller and grant `cloudscheduler.jobs.update` long enough for IAM to
      propagate before creating the disposable test job. Then PATCH only `http_target.uri` while
      omitting the existing OAuth/OIDC fields. Determine whether Scheduler preserves the attached
      identity without reevaluating `iam.serviceAccounts.actAs` or rejects the update on `actAs`.
      **Resolved 2026-09-28:** after the unauthenticated canary proved update permission propagation,
      URI-only PATCH was denied on retained-account actAs; the identical authorized control
      succeeded and preserved the OIDC identity and audience. See `tested.md`.
- [ ] Repeat with `http_target.body`, headers and method in separate update masks, and capture
      `authorizationInfo` for successful and denied requests. Keep the job paused with a far-future
      schedule and delete every resource immediately after the test.
- [x] If URI-only update preserves OIDC without `actAs`, test an endpoint that records the token
      without trusting its audience. Separately test the OAuth path against a harmless read-only
      Google API. Never point a test job at a mutating production target. **Not applicable:** the
      prerequisite failed securely, so no token receiver or dispatch was created.

## Full-view response boundary
- [ ] With a disposable job containing non-secret marker values, compare get/list responses for
      custom roles containing only get or list, then add `cloudscheduler.jobs.fullView`. Record
      exactly which body, header and identity fields are redacted without `fullView`.

## Delivery and telemetry boundaries

- [ ] In a disposable project with an existing App Engine app, verify the documented
      `login: admin` Scheduler delivery path and record the precise request-log fields that identify
      Scheduler. Use an inert handler and delete the job immediately.
- [ ] With a disposable topic and subscription, publish a unique marker through Scheduler and
      confirm that `Publisher.Publish` remains absent even when Pub/Sub Data Access logging is
      enabled, while Scheduler emits `AttemptStarted` and `AttemptFinished`. Remove the job,
      subscription, topic, and temporary audit configuration afterward.
- [ ] Capture a harmless OIDC marker request to determine which claims and HTTP headers appear in
      the receiving service's request log versus Scheduler execution logs. Do not use a privileged
      service account or a production relying-party audience.
- [ ] Compare Scheduler execution logs for a naturally scheduled attempt and `RunJob`; verify that
      the Admin Activity entry, rather than the execution entry alone, is the reliable forced-run
      discriminator.
