# Dialogflow CX — research ledger

## 2026-09-28 — post-exploitation audit

- Consolidated two update variants into one retained-secret redirect boundary: change only the
  generic webhook URI for Secret Manager-backed headers, or only the OAuth token endpoint for an
  existing client-credentials configuration.
- Added the required pre-existing routed webhook, service-agent secret access, HTTPS/reachability,
  VPC Service Controls and invocation conditions. `webhooks.update` alone neither creates a secret
  grant nor causes a webhook to fire.
- Corrected telemetry: current official documentation classifies `UpdateWebhook`, `CreateWebhook`
  and `DetectIntent` as `DATA_WRITE` Data Access, disabled by default—not Admin Activity.
- Removed the service-agent ID-token claim. The documented audience is the entire webhook URL
  excluding query parameters. Capturing a token at a controlled URL does not make it replayable to
  an unrelated Cloud Run/IAP/API audience; access-token authentication is discontinued.
- This pass used current official webhook schema/authentication, IAM, audit and logging references.
  It created no agent, webhook, route, session, receiver, IAM grant or other cloud state.

## 2026-09-28 — reciprocal review and taxonomy split

- Expanded the retained external-secret redirect to the full current authentication surface:
  retained request headers, Secret Manager-backed Basic auth, and third-party OAuth client secrets.
  A URI-only or token-endpoint-only field mask preserves unrelated authentication fields.
- Moved configured-service-account access-token capture to a dedicated Dialogflow privilege-
  escalation page and added it to `SUMMARY.md`. The current v3 schema says Dialogflow obtains an
  OAuth token for `serviceAccountAuthConfig.serviceAccount` and sends it in the Authorization
  header; the Dialogflow service agent must already be Token Creator on that account.
- Kept the published sufficient caller set conservative: `dialogflow.webhooks.update` plus
  `iam.serviceAccounts.actAs` on the retained account. Whether URI-only updates skip the unchanged
  account's `actAs` recheck remains an explicit disposable live-test question, not a claimed bypass.
- Added the documented authentication-priority prerequisite so a higher-priority header, Basic or
  third-party OAuth configuration cannot silently replace the configured-service-account token path.
- Reconfirmed `UpdateWebhook` and `DetectIntent` as off-by-default `DATA_WRITE` Dialogflow Data
  Access operations, and `GenerateAccessToken` as off-by-default `ADMIN_READ` IAM Credentials Data
  Access when that backend mint emits the documented method. No cloud state or receiver was used.
