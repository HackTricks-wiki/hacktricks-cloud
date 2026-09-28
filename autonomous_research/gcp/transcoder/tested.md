# Transcoder — tested research

## 2026-09-28 — post-exploitation documentation and schema audit

No Transcoder job, Cloud Storage object, bucket, IAM policy, or other cloud resource was created or
changed. Current Google Cloud access-control, role, API, and audit catalogs and local read-only
`gcloud transcoder jobs create --help` output were used.

### Retained book technique

- `transcoder.jobs.create` can re-host a known supported media object readable by the Transcoder
  service agent into a destination writable by that agent and readable by the attacker. The useful
  cross-project variant grants the victim service agent object-create on an attacker-owned bucket.

### Material corrections

- Consolidated in-project and external-destination descriptions into one security boundary.
- Required the exact source object name: `roles/transcoder.serviceAgent` includes object get/create/
  delete but not object list.
- Bounded the impact to supported media and transformed/lossy output, not arbitrary-object or
  byte-for-byte extraction.
- Used Google's documented per-bucket `roles/storage.objectAdmin` grant for the external sink rather
  than claiming that an unvalidated object-creator-only grant is operationally sufficient.
- Corrected `CreateJob` from Admin Activity to `DATA_WRITE` Data Access, disabled by default. The
  Transcoder audit catalog also classifies job/template deletes as Data Access, not Admin Activity.
- Preserved the distinction between the victim project's off-default job/object audit events and an
  external bucket IAM grant logged in the attacker-controlled bucket project.

### Removed or folded

- Removed the duplicate external-bucket H3 and folded that destination into the retained technique.
- Removed job/template deletion as destructive-only denial of service.
- Removed the unrelated negative survey of Speech, Vision, Video Intelligence, and Translation; it
  belongs in those services' research ledgers rather than a Transcoder attack technique.

### Official evidence used

- https://docs.cloud.google.com/transcoder/docs/access-control
- https://docs.cloud.google.com/iam/docs/roles-permissions/transcoder
- https://docs.cloud.google.com/transcoder/docs/how-to/jobs
- https://docs.cloud.google.com/transcoder/docs/how-to/audit-logging
- https://docs.cloud.google.com/storage/docs/audit-logging

## 2026-09-28 — reciprocal cross-review

No cloud resource was read or mutated. A separate documentation pass checked current official
access-control and role catalogs, the audit catalog, the job guide, and local
`gcloud transcoder jobs create --help` output.

- Confirmed the shown default-template CLI invocation accepts input/output URIs and requires only
  `transcoder.jobs.create` at the Transcoder API boundary.
- Clarified that object-create is the fresh-prefix runtime minimum; collisions with existing output
  names can require replacement access, while Google's documented per-bucket grant remains
  `roles/storage.objectAdmin`.
- Revalidated `CreateJob` as off-default `DATA_WRITE` Data Access, not Admin Activity, and preserved
  the separate attacker-project `storage.buckets.setIamPolicy` telemetry boundary.
- The single retained service-agent media re-hosting chain remains useful; destructive deletion and
  duplicate external-destination H3s remain excluded.
