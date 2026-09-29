# Cloud Data Fusion research log

## 2026-09-28 — privilege-escalation documentation audit

Scope was documentation and local read-only inspection only. No Data Fusion instance was created, no API was enabled, and no cloud resource or IAM policy was changed. Data Fusion instances and pipeline clusters can be costly, so all runtime hypotheses remain explicitly separated from the current documented contracts.

### Evidence inspected

- Current official Cloud Data Fusion access-control, RBAC permission matrix, service-account, namespace-service-account, CDAP REST, Preview, platform-logging, and audit-logging documentation.
- Current official Managed Service for Apache Spark audit-logging documentation.
- Current CDAP `PreviewHttpHandler` and `PreviewManager` source was inspected to verify `/previews`, `/status`, and `/tracers/{tracer}` paths and that the start response serializes an `ApplicationId` whose `application` field is the preview identifier.
- Local `gcloud beta data-fusion ... --help` output.
- Live predefined-role metadata read with `gcloud iam roles describe` for `roles/datafusion.admin`, `accessor`, `viewer`, `developer`, `operator`, `editor`, `runner`, `serviceAgent`, and the basic Editor/Owner roles. These role-description reads did not mutate cloud state.

### Retained privilege boundaries

1. **Pipeline execution as the configured VM service account.** The minimum caller path is instance access (`datafusion.instances.get`) plus `datafusion.namespaces.get`, `datafusion.pipelines.create`, and `datafusion.pipelines.execute`. A built-in PySpark/Scala program avoids requiring artifact upload. The Data Fusion service agent—not the caller—must already be authorized to act as the runtime service account. Impact is bounded to that runtime identity and its network reachability.
2. **Preview through the design-time identity.** `datafusion.pipelines.preview` can read source samples using the Data Fusion service agent, or the configured per-namespace service account on supported RBAC instances. The normal preview is the first 100 rows and sinks are not written. This is a useful read boundary, not general control of the service-account identity.
3. **Instance/namespace IAM self-grant.** `datafusion.instances.setIamPolicy` or `datafusion.namespaces.setIamPolicy` is sufficient for direct policy replacement. Policy-preserving `gcloud ... add-iam-policy-binding` also needs the corresponding `getIamPolicy`. The primitive is mainly relevant to custom/split roles because current Data Fusion Admin and Owner already contain the broader Data Fusion permissions.

### Corrected or rejected claims

- **Rejected:** `datafusion.instances.runtime` as a caller-side gate for the CDAP `apiEndpoint`. Google documents `roles/datafusion.runner` for the pipeline VM service account so it can communicate with Data Fusion runtime services. Developer and Operator are intentionally useful data-plane roles without this permission.
- **Rejected:** a per-namespace service account as the pipeline runtime identity. On 6.10.0+ RBAC instances it is a design-time identity for Preview, Wrangler, and validation. Runtime identity is selected through the instance authorization setting or compute profile.
- **Rejected:** `datafusion.namespaces.setServiceAccount + iam.serviceAccounts.actAs` as a generic run-as escalation. The documented REST flow uses Workload Identity from the internal namespace KSA to the design-time GSA. It requires the KSA's `roles/iam.workloadIdentityUser` binding and does not change the pipeline VM service account.
- **Moved out of privilege escalation:** `datafusion.secureKeys.getSecret` is useful credential post-exploitation, but the value might or might not confer additional privilege. It is already covered on the post-exploitation page.
- **Rejected:** “default compute service account is usually Editor.” Automatic Editor grants are not guaranteed; impact must follow the effective IAM policy.
- **Rejected:** blanket “CDAP calls are not Cloud Audit events.” The current Data Fusion audit catalog explicitly covers application, artifact, namespace, preview, profile, program, secure-store, and SCM handlers.
- **Corrected:** the CLI does expose `gcloud beta data-fusion get-iam-policy`, `set-iam-policy`, and add/remove binding commands, including `--namespace`.
- **Corrected:** IAM policy audit method names are documented as generic `GetIamPolicy` and `SetIamPolicy`, not `google.cloud.datafusion.v1.DataFusion.SetIamPolicy`; neither is an LRO.

### Telemetry findings

- `google.cloud.datafusion.v1.DataFusion.GetInstance`: Data Access, default off, non-LRO.
- `ProgramLifecycleHttpHandler.performAction`: Admin Activity, default on, non-LRO.
- `PreviewHttpHandler.start`, `getStatus`, `getTracersData`, `getPreviewLogsNext`, and `getPreviewLogsPrev`: Admin Activity, default on, non-LRO. The current catalog classifies the retrieval calls as Admin Activity because they require the `ADMIN_WRITE`-typed `datafusion.pipelines.preview` permission.
- Managed Service for Apache Spark `ClusterController.CreateCluster` and `DeleteCluster`: Admin Activity, default on, LROs. They are conditional on use of an ephemeral cluster profile.
- Instance `SetIamPolicy`: Admin Activity, default on, non-LRO. Instance `GetIamPolicy`: Data Access, default off, non-LRO. The catalog does not separately enumerate namespace IAM permissions; the official v1beta1 endpoint uses standard IAM methods, with namespace `setIamPolicy` typed `ADMIN_WRITE` and `getIamPolicy` typed `ADMIN_READ`.
- `PipelineV2` pipeline logs and Data Fusion service logs are platform logs. Cloud Logging is enabled by default from Data Fusion 6.11.0 but can be disabled.
- The current generated audit catalog does not document a method for the direct `PUT /v3/namespaces/.../apps/...` deployment endpoint. The book records this as **no documented audit guarantee**, not as proof that no log can ever exist.

### Related-page review

The post-exploitation and persistence pages contain valuable hypotheses but predate the current data-plane audit catalog. Their blanket “no Cloud Audit event” statements, Dataproc-only terminology, missing per-technique prerequisites, and namespace-SA runtime wording require dedicated rewrites. They were not silently treated as evidence for the privilege-escalation page.

## 2026-09-28 — independent cross-review

- Rechecked all three retained boundaries against the current access-control, RBAC overview/matrix, service-account, Preview, REST, audit-catalog, and platform-logging contracts and local `gcloud beta data-fusion` help/source. No cloud resource was accessed or mutated.
- Corrected the instance-access prerequisite. Current Google pages conflict: the RBAC overview says Accessor is implicitly assigned with any other Data Fusion RBAC role, while the role matrix and setup guide still say to grant Accessor separately. The book now states the invariant—effective `datafusion.instances.get`—and requires verification rather than claiming either binding behavior universally.
- Added the documented OAuth-scope caveat for service-account tokens against version 6.5 RBAC instances: `userinfo.email` plus `cloud-platform` or `servicecontrol`.
- Tightened namespace IAM telemetry. The official audit catalog documents `GetIamPolicy`/`SetIamPolicy` only against instance permissions. The namespace REST surface and permission types are official, but they do not prove an emitted method or default log class, so those fields remain an explicit live-capture gap.
- Revalidated caller/runtime separation: pipeline create/start is authorized to the caller through RBAC; the Data Fusion service agent holds `iam.serviceAccounts.actAs` on the selected pipeline VM service account; `roles/datafusion.runner` belongs to that runtime service account. Preview instead uses the design-time service agent or supported per-namespace design-time service account.

## 2026-09-28 — post-exploitation page audit

- Retained only direct namespace secure-key value retrieval. Its documented permission set is effective `datafusion.instances.get` plus `datafusion.namespaces.get` and `datafusion.secureKeys.getSecret`; `.list` is needed only for key-name discovery.
- Corrected the old CDAP logging claim: the current official catalog explicitly classifies `SecureStoreHandler.get`/`.list` and `DataFusion.GetInstance` as off-by-default `ADMIN_READ` Data Access methods.
- Demoted `pipelineConnections.get` credential theft. Connections store useful configuration and may contain credentials, but the current public contract does not establish cleartext sensitive- field responses for every plugin; an exact plugin/response test remains required.
- Removed pipeline exfiltration from post-exploitation because a pipeline running under a stronger configured identity is already the retained Data Fusion run-as privilege escalation. Removed the duplicate tampering and destructive instance delete/restart headings under the no-garbage rule.
- No Data Fusion instance, endpoint, pipeline, secure key, connection, IAM policy or logging setting was accessed or changed during this documentation-only pass.

## 2026-09-28 — reciprocal review of post-exploitation

- Corrected the secure-store prerequisite to include effective `datafusion.instances.get` even when the `apiEndpoint` is already known. Current setup/role-matrix pages require the Accessor boundary; the RBAC overview separately says another RBAC assignment implicitly supplies it, so the page now states the invariant permission instead of assuming how it was granted.
- Added the documented version 6.5 service-account token scopes: `userinfo.email` plus `cloud-platform` or `servicecontrol`. Reconfirmed `datafusion.namespaces.get` and `datafusion.secureKeys.getSecret` for a known value, with `.list` only for discovery.
- Rechecked `SecureStoreHandler.get`/`.list` and `DataFusion.GetInstance` as non-LRO, off-by-default `ADMIN_READ` Data Access methods. No instance or secure key was accessed.
