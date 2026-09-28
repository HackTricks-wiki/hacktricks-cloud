# Storage Transfer Service — tested research

## 2026-09-28 — post-exploitation documentation and schema audit

No transfer job, bucket, IAM policy, transfer agent, or other cloud resource was created or
modified. This pass used current Google Cloud access-control, API, audit-log, transfer-log, and
service-account documentation plus local read-only `gcloud transfer ... --help` output.

### Retained book techniques

- Create and explicitly run a managed-agent job to copy an agent-readable GCS source to an
  attacker-controlled destination (`storagetransfer.jobs.create` + `.run`).
- Repoint an existing managed-agent job's destination and run it, reusing already-delegated source
  access (`storagetransfer.jobs.update` + `.run`).

### Material corrections

- The managed service-agent role is Pub/Sub-oriented and does not itself grant project-wide Storage
  access. GCS source/destination permissions must already exist or be granted separately.
- Bounded the overwrite-always fresh-prefix sink to `storage.buckets.get` plus
  `storage.objects.create` (represented by legacy bucket reader + object creator); other overwrite
  and deletion modes require additional object get/list/delete permissions.
- Job creation alone was not described as immediate execution. The explicit command path needs both
  `jobs.create` and `jobs.run`; a create-only principal can use an enabled schedule instead.
- Job mutation was bounded to managed-agent jobs or user-managed identities for which `actAs` is
  satisfied. It is not an arbitrary-service-account bypass.
- Local SDK source confirms `gcloud transfer jobs update` always calls `GetTransferJob` before
  `Patch`, so the provided helper requires `jobs.get` even though a direct known-field API patch can
  have the narrower update/run control-plane boundary.
- Corrected telemetry to the current audit catalog: create/update/run are `ADMIN_WRITE` Admin
  Activity; get/list are `ADMIN_READ` Data Access. Per-object Storage activity is Data Access, and
  Storage Transfer `FIND`/`COPY`/`DELETE` activity records exist only when job logging requests them.
- Recorded the audit-catalog nuance that `UpdateTransferJob` lists both update and delete permission
  types because deletion uses the update surface; ordinary configuration updates are documented as
  authorized by `storagetransfer.jobs.update`.

### Removed or folded

- Removed HTTP URL-list ingress as a standalone post-exploitation technique. It imports public,
  attacker-chosen content but does not inherently disclose data, gain a foothold, or cross a useful
  authorization boundary.
- Removed `deleteObjectsFromSourceAfterTransfer` and delete/stop/cancel variants as destructive-only
  availability impact.
- Removed the earlier claim that `jobs.run` replays a user-managed-SA job without `actAs`. The
  current delegation guide says user-managed accounts are restricted to users creating or
  triggering jobs, while the audit/IAM method tables expose only `jobs.run`; without a fresh
  minimum-role test this conflict is not strong enough to publish.
- Folded the external-sink variant into each applicable data-copy technique instead of duplicating
  it as another H3.

### Official evidence used

- https://docs.cloud.google.com/storage-transfer/docs/access-control
- https://docs.cloud.google.com/storage-transfer/docs/cloud-storage-to-cloud-storage
- https://docs.cloud.google.com/storage-transfer/docs/delegate-service-agent-permissions
- https://docs.cloud.google.com/storage-transfer/docs/audit-logging
- https://docs.cloud.google.com/storage-transfer/docs/transfer-logs
- https://docs.cloud.google.com/storage/docs/audit-logging

## 2026-09-28 — reciprocal cross-review

No cloud resource was read or mutated. A separate documentation pass rechecked current official
permissions, sink/source requirements, audit classifications, local gcloud help, and installed SDK
command source.

- Confirmed the displayed create path uses `--do-not-run` followed by the asynchronous `jobs run`
  command, so its exact caller boundary is `jobs.create` + `jobs.run` without operation polling.
- Confirmed `gcloud transfer jobs update` unconditionally calls `GetTransferJob` before `Patch`, so
  the helper needs `jobs.get` in addition to the narrower direct-API update/run boundary.
- Revalidated fresh-prefix sink access as bucket get + object create, and create/update/run as
  always-on `ADMIN_WRITE` Admin Activity while get and object I/O remain off-default Data Access.
- No retained technique, command, citation, or duplicate/usefulness decision required a book edit.
