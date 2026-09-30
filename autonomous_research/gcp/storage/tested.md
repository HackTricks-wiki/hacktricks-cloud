# Cloud Storage — tested

## 2026-09-28 — Batch Operations execution identities and dry-run boundary

- Reconciled two simultaneously valid results. The live destructive prefix job re-checked the caller's transform permission, but current troubleshooting also assigns bucket-list/manifest runtime failures to the job-project Storage Batch Operations service agent. Only the newer project-source/CEL section explicitly says it processes objects with caller credentials. The book now documents the caller check plus service-agent runtime requirement instead of claiming the service agent is never involved.
- Current `CreateJob` documentation names only `storagebatchoperations.jobs.create`; the dedicated Admin role contains no `storage.*` permissions. Dry run returns aggregate object count and prefix-selected bytes without transforming data, leaving a narrower hypothesis: can it disclose those aggregates through service-agent access before or without the real transform's caller check?
- The lab Storage Intelligence configuration is `INHERIT` with effective edition `NONE`, and the Batch Operations API/service identity are absent. No job was launched: enabling the one-time 30-day trial consumes persistent eligibility and can auto-convert, so it cannot meet the mandatory cleanup contract. The exact prepared-fixture negative/positive-control matrix is in `checklist.md`.
- Discovery revision `20260916` describes a one-bucket `BucketList`, while the 2026-09-24 guide and current gcloud support up to 1,000 enrolled buckets across projects. Use one bucket for the future identity test and treat the documentation/schema difference as rollout drift, not an auth finding.

## 2026-09-28 — post-exploitation visibility and correctness audit

- Rated all 14 retained post-exploitation techniques against current Storage, Batch Operations and IAM Credentials audit documentation, including downstream state and application failures.
- Corrected permanent exclusions: Cloud Audit Logs never tracks public-object access or Object Lifecycle Management changes. Optional Storage usage logs are the separate source for those events.
- Corrected IP-filter permissions and project-level break-glass scope; bucket versus object restore telemetry; HMAC update versus delete; the 12-hour impersonated signed-URL limit; multi-bucket Batch Operations and optional transformation logs; and overwrite requirements (`create` + `delete`).
- Corrected recovery semantics: disabling versioning does not delete existing noncurrent versions, clearing soft delete does not remove already soft-deleted resources, holds are releasable, and CMEK denial becomes permanent only after key-version destruction.
- Qualified observed `request=null` claims because detailed audit logging mode can add request and response fields. No cloud resource was created.
