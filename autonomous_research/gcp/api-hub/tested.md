# API Hub — tested

## 2026-09-28 — plugin identity model and testability review

- Reviewed public API Hub discovery revision `20260922`, the current plugin protobuf, IAM catalog, provisioning guide and audit-log matrix. User-defined plugins have a hosting-service account; plugin instances can reference Secret Manager versions and a target Google service account. The documented design grants the hosting account `secretmanager.versions.access` and `iam.serviceAccounts.getAccessToken` on those targets.
- A plugin-instance creator not having caller `iam.serviceAccounts.actAs` is therefore not by itself a vulnerability. The expected boundary is the hosting account's Secret Accessor/Token Creator delegation. A useful negative control must prove the hosting account lacks those target grants and determine whether API Hub nevertheless resolves a secret or mints/forwards a target token.
- Current schemas expose a sharper permission mismatch. IAM contains `apihub.plugininstances.applyConfig`, and update documentation says authentication/additional configuration should use `ApplyPluginInstanceConfig`; however, neither current discovery nor the public protobuf exposes that RPC, while gcloud's instance update accepts authentication and additional-config flags. A restricted caller with `plugininstances.update` but not `applyConfig` should be tested against `authConfig`, `additionalConfig`, `actions.serviceAccount` and wildcard update masks.
- The official API Hub audit matrix was updated 2026-09-24 but lists only plugin enable, disable and get. It omits current create/delete plugin, create/update/delete instance and execute-action methods. Whether these operations truly lack Cloud Audit Logs is a high-priority observability test; absence must be measured with an actual lifecycle, not inferred from the table.
- The lab has neither `apihub.googleapis.com` nor `apigee.googleapis.com` enabled and no API Hub Cloud Asset. Provisioning would create an Apigee organization whose teardown remains soft-deleted and prevents reprovisioning for seven days. No live fixture was created because that residue cannot satisfy the mandatory cleanup contract. No book or vulnerability claim was made.

### Primary references

- <https://apihub.googleapis.com/$discovery/rest?version=v1>
- <https://github.com/googleapis/googleapis/blob/master/google/cloud/apihub/v1/plugin_service.proto>
- <https://docs.cloud.google.com/apigee/docs/reference/apis/apihub/rest/v1/projects.locations.plugins>
- <https://docs.cloud.google.com/apigee/docs/reference/apis/apihub/rest/v1/projects.locations.plugins.instances>
- <https://docs.cloud.google.com/apigee/docs/reference/apis/apihub/rest/v1/projects.locations.plugins.instances/executeAction>
- <https://docs.cloud.google.com/apigee/docs/apihub/audit-logging-apihub>
- <https://docs.cloud.google.com/apigee/docs/apihub/provision>
- <https://docs.cloud.google.com/iam/docs/roles-permissions/apihub>
