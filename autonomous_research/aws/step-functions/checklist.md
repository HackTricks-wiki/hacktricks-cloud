# Step Functions attack ideas

- [x] Same-account Activity callback-token binding: wrong Region, cross-execution marker, mutation,
  success/failure replay, heartbeat, and expiry tested. Boundaries held. See
  `callback-token-binding-2026-09-26.md`.
- [x] Activity polling plus callback workflow hijack: previously verified and published in the
  Step Functions post-exploitation page.
- [x] CloudTrail data-event classification: `GetActivityTask`, `StartSyncExecution`, and
  `InvokeHTTPEndpoint` documented as opt-in data events. See `cloudtrail-data-events-2026-09-26.md`.
- [ ] Cross-account callback-token rejection: test only when a second account is explicitly authorized.
- [ ] Callback-token binding across `.waitForTaskToken` SDK integrations: revisit only with a security
  hypothesis beyond the Activity behavior already tested.
- [x] Dynamic HTTP Task endpoint: verified that `states:StartExecution` alone can redirect a fixed
  EventBridge Connection's API key to a controlled endpoint when execution input supplies `ApiEndpoint`
  and the execution role does not constrain `states:HTTPEndpoint`. See
  `http-task-dynamic-endpoint-2026-09-26.md`.
- [x] `TestState` + exact-role `iam:PassRole` HTTP oracle without `states:RevealSecrets`: no-PassRole denied,
  positive caller made a real request and disclosed the canary Connection API key to the collector. See
  `teststate-http-connection-2026-09-26.md`.
- [ ] HTTP Task endpoint-condition redirect: allow endpoint A only, make A redirect to B, and verify that
  connection credentials are not forwarded outside the IAM-approved endpoint.
- [ ] OAuth `UpdateConnection` authorization-endpoint-only replacement: verify omitted stored client
  parameters are not reused against a newly supplied authorization endpoint.
- [ ] Distributed Map redrive/update concurrency boundaries: check whether `UpdateMapRun` can exceed
  documented failure/concurrency limits or affect a sibling Map Run.
