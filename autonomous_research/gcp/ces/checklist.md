# Gemini Enterprise for Customer Experience / CX Agent Studio — open ideas

## OpenAPI tool retained identity

- [ ] In an explicitly CES-write-enabled disposable project, create a standalone OpenAPI tool with
      service-account auth and a zero-role target account. Give the CES service agent Token Creator
      on that account, but give the updater only `ces.tools.update` and no actAs.
- [ ] PATCH only `openApiTool.openApiSchema`, omitting `apiAuthentication`. Secure outcomes are a
      retained-account actAs denial or clearing authentication. If the PATCH succeeds and preserves
      auth, execute once against Google `userinfo` and retain only the returned synthetic email—not
      the bearer token. Treat a missing recheck private-first until intended delegation is resolved.
- [ ] Use an authorized actAs positive control only after a denial. Capture CES Admin Activity,
      IAM Credentials token-mint telemetry, execute-tool logging and the downstream Google API call.
- [ ] Delete the app/tool, target/updater accounts and CES service agent; remove every binding and
      disable CES only if initially disabled. Verify active IAM, API, CES and Cloud Asset inventory.

## Other newly surfaced managed-deputy candidates

- [ ] API Hub user-defined plugin: determine whether a plugin-instance creator can select a
      caller-controlled hosting service plus a pre-authorized token service account without the
      caller having actAs. Bound the plugin protocol first and use a zero-role account.
- [ ] Storage Batch Operations: submit a cross-project `dryRun` with a service-agent-readable source
      bucket but a caller lacking bucket/object read. A nonzero hidden-object count/byte total would
      establish a deputy disclosure; a caller-permission denial is the expected secure result.
- [ ] Audit Manager: call `EnrollResource` with `validateOnly=true` and a cross-project destination
      writable by the service agent but not the caller. Do not create a real enrollment unless the
      validation unexpectedly omits the documented caller-write check.

