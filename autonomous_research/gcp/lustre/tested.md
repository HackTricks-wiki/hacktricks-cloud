# Managed Lustre privilege-escalation audit

## 2026-09-28 - documentation and local CLI audit

No API, instance, transfer, bucket, IAM policy, service account, or other cloud resource was created
or changed. The review used current official Managed Lustre REST, IAM, transfer, audit, and Cloud
Storage documentation plus local GA `gcloud lustre` help and generated client schemas.

### Retained result

One bounded privilege transition remains: a principal with both Managed Lustre transfer permissions
can use the default service agent's pre-existing read grant on a Cloud Storage source that the
principal cannot read. Import stages those objects in the file system, and export to an
attacker-controlled bucket recovers them without VPC mount access.

Required boundaries recorded in the page:

- caller: `lustre.instances.importData`, `lustre.instances.exportData`, and
  `lustre.operations.get` only when waiting through the synchronous CLI;
- source: the default service agent has bucket-scoped `roles/storage.objectViewer` or equivalent;
- destination: the same agent has `roles/storage.objectUser`, which an attacker can grant on an
  attacker-owned bucket;
- active instance, available capacity, valid paths, no conflicting transfer, and perimeter/policy
  compatibility; a protected transfer needs the bucket project in the same perimeter or an egress
  rule for the Managed Lustre service agent.

The impact is data access through that transfer identity only. No credential, token, IAM binding, or
general service-account impersonation is obtained.

### Removed or folded claims

- Instance list/get is enumeration, not privilege escalation.
- Export of data already authorized by `lustre.instances.exportData` is post-exploitation
  exfiltration, not a new privilege boundary by itself.
- Import from an attacker-controlled source is poisoning/post-exploitation.
- Instance deletion is destructive denial of service.
- The optional `serviceAccount` request field does not itself provide a token. Current service docs
  describe the selected transfer identity but do not enumerate its secondary caller-side attachment
  check, so no unverified `iam.serviceAccounts.actAs` minimum is asserted as a separate technique.

### Telemetry corrections

- `google.cloud.lustre.v1.Lustre.ImportData` is a `DATA_WRITE` Data Access LRO, not Admin Activity.
- `google.cloud.lustre.v1.Lustre.ExportData` is a `DATA_READ` Data Access LRO, not Admin Activity.
- Both transfer audit logs are off by default. Cloud Storage object reads/writes are also Data Access
  and off by default, but occur in the bucket-owning projects under the service-agent identity.
- `DeleteInstance` remains an always-on Admin Activity LRO.
- The current Managed Lustre audit catalog documents `GetInstance` as `ADMIN_READ` Data Access but
  does not list `ListInstances` or the operations helper methods. The page does not invent coverage.

### Local surface checks

- The GA CLI accepts `instances import-data` and `instances export-data`, with
  `--gcs-path-uri`, `--lustre-path`, `--service-account`, and `--async`.
- The v1 schema exposes only bounded instance management and transfer operations; no workload-code
  execution or instance IAM-policy method was found.

### Independent reciprocal review

Confirmed the bounded source-bucket privilege crossing, caller/service-agent permissions, helper
polling boundary, telemetry and impact. Added an explicit cleanup constraint: transfer APIs cannot
remove imported files, so validation needs a disposable instance or isolated path and mount-based
cleanup; exporting `/` from a shared instance can disclose unrelated data.
