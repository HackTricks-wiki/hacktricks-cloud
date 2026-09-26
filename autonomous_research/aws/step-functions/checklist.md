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
- [ ] `InvokeHTTPEndpoint` request/response and EventBridge connection-secret boundaries: inspect whether
  a caller can redirect or extract authenticated HTTP material without the corresponding connection access.
- [ ] Distributed Map redrive/update concurrency boundaries: check whether `UpdateMapRun` can exceed
  documented failure/concurrency limits or affect a sibling Map Run.
