# Dialogflow CX — research ledger

## 2026-09-28 — post-exploitation audit

- Consolidated two update variants into one retained-secret redirect boundary: change only the generic webhook URI for Secret Manager-backed headers, or only the OAuth token endpoint for an existing client-credentials configuration.
- Added the required pre-existing routed webhook, service-agent secret access, HTTPS/reachability, VPC Service Controls and invocation conditions. `webhooks.update` alone neither creates a secret grant nor causes a webhook to fire.
- Corrected telemetry: current official documentation classifies `UpdateWebhook`, `CreateWebhook` and `DetectIntent` as `DATA_WRITE` Data Access, disabled by default—not Admin Activity.
- Removed the service-agent ID-token claim. The documented audience is the entire webhook URL excluding query parameters. Capturing a token at a controlled URL does not make it replayable to an unrelated Cloud Run/IAP/API audience; access-token authentication is discontinued.
- This pass used current official webhook schema/authentication, IAM, audit and logging references. It created no agent, webhook, route, session, receiver, IAM grant or other cloud state.

## 2026-09-28 — reciprocal review and taxonomy split

- Expanded the retained external-secret redirect to the full current authentication surface:
  retained request headers, Secret Manager-backed Basic auth, and third-party OAuth client secrets. A URI-only or token-endpoint-only field mask preserves unrelated authentication fields.
- Moved configured-service-account access-token capture to a dedicated Dialogflow privilege-escalation page and added it to `SUMMARY.md`. The current v3 schema says Dialogflow obtains an OAuth token for `serviceAccountAuthConfig.serviceAccount` and sends it in the Authorization header; the Dialogflow service agent must already be Token Creator on that account.
- Kept the published sufficient caller set conservative: `dialogflow.webhooks.update` plus `iam.serviceAccounts.actAs` on the retained account. Whether URI-only updates skip the unchanged account's `actAs` recheck remains an explicit disposable live-test question, not a claimed bypass.
- Added the documented authentication-priority prerequisite so a higher-priority header, Basic or third-party OAuth configuration cannot silently replace the configured-service-account token path.
- Reconfirmed `UpdateWebhook` and `DetectIntent` as off-by-default `DATA_WRITE` Dialogflow Data Access operations, and `GenerateAccessToken` as off-by-default `ADMIN_READ` IAM Credentials Data Access when that backend mint emits the documented method. No cloud state or receiver was used.

## 2026-09-28 — configured-service-account live authorization test

- Enabled Dialogflow only for the duration of an isolated fixture, created a disposable CX agent, zero-role target service account, test caller and service-agent Token Creator grant, and used an ephemeral receiver plus one zero-role Cloud Run control service. No real secret was created or accessed.
- Creating a webhook with `serviceAccountAuthConfig` and either the external receiver or the controlled `run.app` URL returned `400 INVALID_ARGUMENT`: service-account authentication is only supported for Google APIs. The external receiver never received a Google credential.
- A flexible GET webhook targeting `https://storage.googleapis.com/storage/v1/b` was accepted. A principal holding `roles/dialogflow.admin` and Service Usage Consumer, but no access on the configured target account, then attempted a field-masked URI-only update to a nonexistent Secret Manager access URL. The request returned `400 INVALID_ARGUMENT` and explicitly said the caller lacked permission to act as the retained service account.
- After granting that same principal `roles/iam.serviceAccountUser` on the target account, the identical URI-only PATCH returned HTTP 200. This proves the current backend rechecks `iam.serviceAccounts.actAs` even when `serviceAccountAuthConfig` is omitted from the update body.
- The provisional token-capture privilege-escalation page and SUMMARY entry were removed. The valid external-header/Basic/OAuth secret redirect remains post-exploitation because those authentication modes do allow non-Google HTTPS receivers and do not attach a Google service account.
- Cleanup deleted the agent, Cloud Run service, receiver, all test/service-agent identities, the temporary service-account key and local gcloud configuration, removed every temporary IAM binding, and restored Dialogflow to disabled. Verification found zero active test service accounts, project IAM references, Cloud Run services, local key/config files, or enabled Dialogflow API state.
