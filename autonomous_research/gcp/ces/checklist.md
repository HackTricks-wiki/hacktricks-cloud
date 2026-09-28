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

- [x] API Hub design review: accepting a target account without caller actAs is expected delegation
      through the plugin hosting account, which must hold Token Creator. The sharper update/applyConfig,
      callback-authentication and missing-audit hypotheses are now in `api-hub/checklist.md`.
- [ ] Run those API Hub controls only in an already-provisioned disposable project; provisioning the
      current lab would leave an Apigee organization in seven-day soft-delete/cooldown state.
- [ ] Storage Batch Operations: submit a cross-project `dryRun` with a service-agent-readable source
      bucket but a caller lacking bucket/object read. A nonzero hidden-object count/byte total would
      establish a deputy disclosure; a caller-permission denial is the expected secure result.
- [x] Audit Manager project-scope control: `EnrollResource` with `validateOnly=true` rejected a
      caller lacking bucket access on `storage.buckets.getIamPolicy` even though the service agent
      had object-create; the identical request succeeded with caller Storage Admin. This is secure.
- [ ] Audit Manager strict cross-project case: repeat only at a prepared folder/organization scope,
      because cross-project destinations are not the documented project-scope contract. Keep a 2xx
      without caller bucket access private-first and do not create a real enrollment.
