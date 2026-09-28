# Cloud Storage — tested

## 2026-09-28 — post-exploitation visibility and correctness audit

- Rated all 14 retained post-exploitation techniques against current Storage, Batch Operations and
  IAM Credentials audit documentation, including downstream state and application failures.
- Corrected permanent exclusions: Cloud Audit Logs never tracks public-object access or Object
  Lifecycle Management changes. Optional Storage usage logs are the separate source for those events.
- Corrected IP-filter permissions and project-level break-glass scope; bucket versus object restore
  telemetry; HMAC update versus delete; the 12-hour impersonated signed-URL limit; multi-bucket Batch
  Operations and optional transformation logs; and overwrite requirements (`create` + `delete`).
- Corrected recovery semantics: disabling versioning does not delete existing noncurrent versions,
  clearing soft delete does not remove already soft-deleted resources, holds are releasable, and CMEK
  denial becomes permanent only after key-version destruction.
- Qualified observed `request=null` claims because detailed audit logging mode can add request and
  response fields. No cloud resource was created.
