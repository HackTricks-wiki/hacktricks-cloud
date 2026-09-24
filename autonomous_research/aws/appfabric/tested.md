# AppFabric — tested

Zero prior wiki coverage. Now: `aws-services/aws-appfabric-enum.md` (enum + post-ex).

## GetAppAuthorization credential-leak — DISPROVEN (documented as a defensive negative)

- Hypothesis: `GetAppAuthorization`/`ListAppAuthorizations` might return the stored SaaS OAuth2
  token / API key → cross-SaaS credential theft.
- Result: **NO.** The `credential` (oauth2Credential / apiKeyCredential) is an **input-only** member
  of `CreateAppAuthorization`/`UpdateAppAuthorization`; the `AppAuthorization` output shape has only
  app/tenant/authType/status/persona/authUrl. Confirmed from the botocore model. Recorded in the
  page as an explicit defensive note (no credential-theft vector via the API).

## CreateIngestionDestination log-redirect — VERIFIED (authz gate) / mechanism from docs

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1 (AppFabric usable — empty list, no error).
- **Setup:** created an app bundle; created a role with an inline policy granting **only**
  `appfabric:CreateIngestionDestination`; assumed it and called `create-ingestion-destination`
  against the real bundle + a bogus ingestion ARN + an attacker-bucket destination.
- **Result:** `ValidationException: The specified ingestion does not exist` — i.e. **authorization
  PASSED** (resource error, not AccessDenied). Confirms the IAM gate is that single action, **no
  `iam:PassRole`** (AppFabric delivers via the AWSServiceRoleForAppFabric SLR).
- **End-to-end NOT run:** `CreateIngestion` requires a pre-existing **app authorization** (real
  OAuth to a SaaS tenant: Slack/Google/etc.) — `ValidationException: create an app authorization
  ... before creating an ingestion`. That precondition needs a real SaaS connection (not
  feasible/authorized), so log-flow-to-attacker-bucket is documented from AWS docs, honestly scoped
  (per the /goal precondition exception) — the page does NOT claim end-to-end verification.
- **Teardown:** role + app bundle deleted, verified (empty list-app-bundles, NoSuchEntity on role).
- **Disposition:** NET-NEW page. Technique = redirect/exfil of SaaS audit logs + SOC-blinding via
  Update/Delete/StopIngestion. Committed + wired into SUMMARY.
