# Cloud Storage privilege-escalation research

## 2026-09-28 — documentation audit

No live cloud resources were created or modified. The privilege-escalation page was reconciled against current Cloud Storage, Managed Airflow, Cloud Build, IAM, Organization Policy, and audit-logging documentation.

- Retained four high-value primitives: bucket/managed-folder IAM self-grant, HMAC creation for an in-project service account, Managed Airflow DAG injection, and poisoning of a genuinely unpinned Cloud Build `StorageSource`.
- Folded bucket and managed-folder IAM into one resource-scoped self-grant technique. Managed folders are not HNS-only; they can exist in flat-namespace or hierarchical-namespace buckets, but require uniform bucket-level access.
- Distinguished raw `setIamPolicy` API minimums from non-destructive additive gcloud helpers. Bucket `add-iam-policy-binding` needs `buckets.get`, `getIamPolicy`, `setIamPolicy`, and `update`; managed-folder policy management needs `getIamPolicy` and `setIamPolicy`.
- Removed object `setIamPolicy` as a standalone privesc technique. It updates object ACLs, is disabled by uniform bucket-level access, and the documented `gcloud storage objects add/get/set-iam-policy` commands do not exist in the current CLI.
- Bounded HMAC impact to the target service account's Cloud Storage XML API authority. It is not a general Google API credential. `storage.hmacKeys.create` is project-scoped and the documented create method has no `iam.serviceAccounts.actAs` requirement.
- Added the relevant HMAC blockers: service-account key-creation organization policy and the Storage authentication-type restriction.
- Corrected Composer logging: direct DAG-bucket writes are Cloud Storage `DATA_WRITE`, disabled by default; there is no Composer Admin Activity event merely for the object upload. Airflow streaming logs and downstream API audit records are separate signals.
- Bounded Cloud Build poisoning to automation that submits a known reusable `.zip`/`.tar.gz` `StorageSource` with omitted `generation`, plus build steps that execute/package/trust the source. A pinned generation is not affected; changing an archived `cloudbuild.yaml` is not enough when build steps were already supplied to the API. The page does not claim an undocumented post-`CreateBuild` race window.
- Corrected current Cloud Build identity semantics. Builds may use a user-specified account, the Compute Engine default account, or the legacy Cloud Build account; no default identity was assumed to have Editor/Owner.
- Reclassified ordinary object read/write as post-exploitation or as a prerequisite, not a standalone identity escalation.
- Removed historical Cloud Functions and App Engine staging races because current official documentation does not establish that a mutable, unpinned object is consumed after the attacker-visible write window.
- Removed GCR bucket poisoning as a live technique because Container Registry writes are no longer available; Artifact Registry does not expose a project Cloud Storage backing bucket.

## 2026-09-28 — independent cross-review

No cloud resources were accessed or changed. The four retained primitives, commands, permission boundaries, impacts, and references were independently checked against current official Cloud Storage, IAM, Managed Airflow, Cloud Build, and Cloud Monitoring contracts.

- Clarified that a one-permission raw IAM-policy replacement is deliberately destructive. Preserving bindings and IAM Conditions requires `getIamPolicy`, policy version 3, and the policy `etag`.
- Corrected the HMAC organization-policy prerequisite: `storage.restrictAuthTypes` blocks service-account HMAC creation/use only when its denied values cover service-account or all signed HMAC requests. Also recorded the ten-non-deleted-key service-account limit.
- Completed the HMAC authentication metric labels and its 60-second sampling/up-to-210-second visibility delay.
- Qualified Managed Airflow application logging: collection is enabled by default, but a particular log entry remains conditional on DAG parsing/execution and can be affected by ingestion or routing configuration.
- Split Cloud Build audit visibility by invocation path. Direct build creation uses `CloudBuild.CreateBuild`, manual trigger runs use `CloudBuild.RunBuildTrigger`, retries use `CloudBuild.RetryBuild`, and the documented webhook receiver methods do not produce audit logs; the three audited methods are long-running operations that normally emit start and completion records.
- Added the documented reliable retry path: retrying an original `StorageSource` that omitted `generation` resolves the current object, whereas a pinned original source attempts to reuse its original generation.
