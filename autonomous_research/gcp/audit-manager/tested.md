# Audit Manager — tested

## 2026-09-28 — `validateOnly` enforces destination-bucket authority

- Current v1 discovery exposes synchronous `EnrollResource` at
  `POST /v1/{scope}:enrollResource`. With `validateOnly=true`, the service performs schema, IAM and
  destination validation without applying an enrollment, creating an enrollment resource, consuming
  report quota or generating a report.
- Tested the project scope `projects/gcp-labs-eqd4ny8d/locations/global` with an isolated caller that
  had `roles/auditmanager.admin` and Service Usage Consumer but no Storage role. The Audit Manager
  service agent separately had bucket-level `roles/storage.objectCreator`, establishing that the
  managed deputy could create an object while the caller could not.
- Storage `testIamPermissions` returned an empty permission set for the caller. After the new Beta
  Audit Manager role propagated, `validateOnly` returned HTTP 403 and explicitly identified missing
  caller permission `storage.buckets.getIamPolicy`. Granting that same caller documented bucket-level
  `roles/storage.admin` made the otherwise identical request return HTTP 200 with `{}`.
- This rejects the same-project confused-deputy hypothesis: Audit Manager did not substitute the
  service agent's object-create authority for the caller's destination authorization. It is expected
  secure behavior, not a book technique or vulnerability report.
- The stricter cross-project case remains open. Google documents cross-project destinations only for
  folder or organization enrollment, so it needs an already-prepared disposable hierarchical scope;
  a project-scope result must not be presented as proof of that separate boundary.

### Observed telemetry

| Event | Observed Cloud Audit Log evidence |
| --- | --- |
| Role-propagation retries | Admin Activity `google.cloud.auditmanager.v1.AuditManager.EnrollResource`; `auditmanager.locations.enrollResource` was `granted=false`; status code 7. |
| No-Storage negative control | Same Admin Activity method; `auditmanager.locations.enrollResource` was `granted=true`; status code 7 named missing `storage.buckets.getIamPolicy`. |
| Storage Admin positive control | Same Admin Activity method; authorization was `granted=true`; empty status indicated success. |
| Request visibility | Logged request retained only the request type and project/global scope. The destination and `validateOnly` value were absent in the observed Admin Activity entries. |

### Fixture and cleanup notes

- Early bounded attempts never reached the product boundary: one used the credential-source quota
  project for IAM Credentials, one hit fresh-key propagation, and one reached Audit Manager before
  the new Beta role propagated. The final harness waited on the specific outer permission denial
  before classifying the Storage result.
- Every exit path removed the bucket, caller, temporary key/config, bucket and project IAM bindings,
  Audit Manager service agent and API enablement because none existed at baseline. Independent live
  inventory found zero test service accounts, buckets, IAM references, cached configurations, enabled
  Audit Manager API or service agent. Cloud Asset Search temporarily retained three deleted key
  records after authoritative IAM deletion; recheck index convergence separately.

### Primary references

- <https://docs.cloud.google.com/audit-manager/docs/enroll-resource>
- <https://docs.cloud.google.com/audit-manager/docs/troubleshoot-enrollment-issues>
- <https://docs.cloud.google.com/audit-manager/docs/access-control>
- <https://docs.cloud.google.com/audit-manager/docs/audit-logging>
- <https://docs.cloud.google.com/audit-manager/docs/configure-vpcsc>
- <https://cloud.google.com/iam/docs/roles-permissions/auditmanager>
