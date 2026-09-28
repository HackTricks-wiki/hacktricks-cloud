# Gemini Enterprise for Customer Experience / CX Agent Studio — tested

## 2026-09-28 — retained tool service-account authorization probe blocked by eligibility

- Read current CES discovery revision `20260924`. A standalone OpenAPI tool can store arbitrary
  OpenAPI server URLs plus `apiAuthentication.serviceAccountAuthConfig.serviceAccount` and OAuth
  scopes. CES exchanges an access token for that account and sends it in the request Authorization
  header. The documented PATCH supports a field mask and names only `ces.tools.update`; current
  public schemas do not state a caller `iam.serviceAccounts.actAs` check.
- Designed a private-first test that changes only `openApiTool.openApiSchema` while omitting the
  retained authentication object. The target is a zero-role service account, the CES service agent
  alone receives Token Creator on it, and the updater receives CES Tools Editor but no actAs. A
  Google-owned `userinfo` endpoint can return the service-account email through `executeTool`, so no
  token needs to leave Google or enter a custom receiver log.
- The current lab project is not eligible to create CES applications. After enabling the API and
  creating its service identity, the Owner control received HTTP 403 on `CreateApp`:
  `Write access to project ... was denied`. The Admin Activity record was
  `google.cloud.ces.v1.AgentService.CreateApp`; `authorizationInfo` showed
  `ces.apps.create` **granted=true**. This isolates the blocker to a separate product write-access
  entitlement, not IAM propagation or missing application permission.
- Because no app or tool existed, the retained-identity PATCH boundary remains untested. Do not add
  it to the book or classify it as a vulnerability from the schema alone.
- Two bounded setup attempts were cleaned. Independent verification found zero active test service
  accounts, CES service agent, project IAM references, cached credentials, Cloud Asset matches or
  enabled CES API. No app, tool, receiver, token capture or billable execution was created.

