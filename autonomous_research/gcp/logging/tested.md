# Cloud Logging — tested and reviewed

## 2026-09-28 — post-exploitation quality and visibility audit

Documentation-only review against current official Google Cloud documentation and local `gcloud` help. No cloud resource, IAM policy, Logging configuration, API state, or credential was changed.

### Result

- Retained 17 actionable techniques and added explicit minimum permissions/prerequisites, Potential Impact, categorical Stealth, and an expandable audit/default-visibility table to every technique.
- Replaced generic or inferred audit statements with the exact current Cloud Logging audit catalog. In particular, `WriteLogEntries` and `TailLogEntries` are explicitly never audited, while `CopyLogEntries` is `DATA_READ` Data Access rather than Admin Activity.
- Corrected retention shrink semantics: expired entries become unavailable but remain recoverable during a seven-day grace period; retention enforcement is eventual.
- Corrected bucket-deletion semantics: active links block deletion; a locked bucket is deletable only after every stored entry fulfills its retention period; and a bucket in `DELETE_REQUESTED` remains recoverable and continues receiving routed entries throughout its seven-day grace period.
- Corrected restricted-field impact: Logging hides configured fields only from readers that lack `logging.fields.access`; authorized Field Accessors remain unaffected, and linked BigQuery datasets don't honor the Logging field-level ACL.
- Corrected bucket-CMEK semantics: CMEK can't be removed after enablement, global buckets aren't eligible, and unavailable keys can make all logs unqueryable and can cause loss beyond the buffering/persistence windows. Key unavailability is not equivalent to immediate crypto-erasure.
- Corrected retroactive-copy requirements and limits: Cloud Storage only, CMEK-enabled source buckets excluded, initiating principal needs destination object creation, operations take at least one hour, and operation history is retained for up to 30 days.
- Corrected linked-dataset access: BigQuery IAM governs queries, but current official guidance also requires `logging.links.list`; a linked dataset exposes all mapped views to an authorized dataset reader, not an individually selected virtual view.
- Corrected view-IAM audit attribution to `google.iam.v1.IAMPolicy.SetIamPolicy`.
- Narrowed `logging.settings.update` from immediate organization-wide blinding to defaults that affect newly created descendant resources only. Existing sinks and buckets aren't retroactively changed.
- Removed the cross-project Cloud Storage sink bucket-name hijack section. Current official Logging behavior marks a sink `bucket_changed_parent_project` when the destination bucket's parent project changes, so the historical sequence is no longer a reliable current technique.

### Official sources used

- https://docs.cloud.google.com/logging/docs/audit-logging
- https://docs.cloud.google.com/logging/docs/access-control
- https://docs.cloud.google.com/logging/docs/audit/configure-data-access
- https://docs.cloud.google.com/logging/docs/buckets
- https://docs.cloud.google.com/logging/docs/field-level-acl
- https://docs.cloud.google.com/logging/docs/routing/managed-encryption-storage
- https://docs.cloud.google.com/logging/docs/routing/copy-logs
- https://docs.cloud.google.com/logging/docs/analyze/query-linked-dataset
- https://docs.cloud.google.com/logging/docs/analyze/data-security-with-analytics
- https://docs.cloud.google.com/logging/docs/default-settings
- https://docs.cloud.google.com/iam/docs/roles-permissions/logging
