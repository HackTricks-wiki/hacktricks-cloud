# Parallelstore privilege-escalation audit

## 2026-09-28 - documentation and local CLI audit

No API, instance, transfer, bucket, IAM policy, service account, or other cloud resource was created
or changed. The review used current official IAM role, generated audit, VPC Service Controls, service
agent, Cloud Storage, and API schema material plus local GA `gcloud parallelstore` help.

### Retained result

One bounded privilege transition remains: a principal with both Parallelstore transfer permissions
can import objects from a Cloud Storage source readable by the default Parallelstore service agent
but not by the principal, then export the staged files to an attacker-controlled bucket.

Required boundaries recorded in the page:

- caller: `parallelstore.instances.importData`, `parallelstore.instances.exportData`, and
  `parallelstore.operations.get` only for synchronous polling;
- source: the Parallelstore service agent has the transfer documentation's bucket-scoped
  `roles/storage.admin` grant;
- destination: the same agent has the documented bucket role, which an attacker can grant on an
  attacker-owned bucket;
- active instance, sufficient capacity, valid paths, no conflicting transfer, and perimeter/policy
  compatibility.

The result is bounded data access through the transfer service. It does not grant an IAM role,
produce service-account credentials, or authorize arbitrary API calls.

### Removed or folded claims

- Get/list is enumeration.
- Export of file-system content already authorized by `parallelstore.instances.exportData` is
  post-exploitation exfiltration unless it follows the stronger-identity import.
- Attacker-controlled import is poisoning/post-exploitation.
- Delete is destructive denial of service.
- The caller-selectable service-account field is not presented as generic impersonation. The
  service docs expose the field but do not publish the exact secondary authorization check.

### Telemetry corrections

- `google.cloud.parallelstore.v1.Parallelstore.ExportData` is `ADMIN_READ` Data Access, an LRO, and
  off by default; it is not Admin Activity.
- `google.cloud.parallelstore.v1.Parallelstore.ImportData` is an `ADMIN_WRITE` Admin Activity LRO and
  is on by default.
- `google.longrunning.Operations.GetOperation` is `ADMIN_READ` Data Access and off by default.
- Source and destination Cloud Storage object access is Data Access, off by default, and attributed
  to the transfer identity in each bucket's project.
- Get/list are `ADMIN_READ` Data Access; delete is an Admin Activity LRO.

### Current-documentation caveat and local checks

- As of this review, several English Parallelstore guide and audit URLs redirect to the Managed
  Lustre overview even though localized official pages, the Parallelstore API, IAM role catalog,
  client libraries, pricing, monitoring metrics, restricted VIP, and VPC-SC integration remain
  current. Direct localized transfer/audit pages and the current v1 schema were used for exact
  contracts; the book avoids the redirecting English links.
- The installed GA CLI accepts `instances import-data` and `instances export-data`; the prior page's
  flags match the current surface.
- The service role contains project-scoped instance/operation permissions. No per-instance
  `getIamPolicy`/`setIamPolicy`, arbitrary workload execution, or credential-returning method was
  found.

### Independent reciprocal review

Confirmed the bounded source-bucket privilege crossing, caller/service-agent permissions, helper
polling boundary, telemetry and impact. Clarified that bucket-scoped `roles/storage.admin` is the
documented supported transfer grant rather than a proven least-privilege object-permission set, and
added the disposable-path plus mount-cleanup requirement for imported files.
