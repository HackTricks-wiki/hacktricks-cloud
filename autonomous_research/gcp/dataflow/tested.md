# Dataflow privilege-escalation research ledger

## 2026-09-28 — official-documentation and local SDK audit

This pass used current official Google Cloud, Cloud Storage, Compute Engine, IAM, and Apache Beam documentation plus read-only inspection of Google Cloud SDK 586.0.0. It did not call cloud APIs or create, modify, or delete cloud resources.

### Retained privilege-escalation primitives

1. **Trusted-object poisoning.** Google now documents Dataflow shadow resource poisoning directly:
   modification of a template, metadata object, staged dependency, or Python UDF can cause a later job or newly autoscaled worker to execute attacker code as the worker service account. Replacing an existing live object generation requires `storage.objects.create` and `storage.objects.delete`; `storage.objects.update` changes metadata and is not a content-write substitute. `storage.objects.get` is optional for blind replacement.
2. **Job creation plus service-account attachment.** A caller with the regional Flex Template permissions, including `dataflow.jobs.create` and `iam.serviceAccounts.actAs`, can choose the worker service account. `gcloud dataflow yaml run --yaml-pipeline` delivers inline Python through Google's public YAML Flex Template, avoiding a separate attacker-built container or write to a victim code bucket. Exploitation remains bounded by the exact attached account, runtime/service- agent configuration, staging access, network, organization policy, and perimeter.

### Removed or folded from the privilege-escalation page

- **Direct SSH/metadata access to Dataflow workers:** a generic Compute Engine instance compromise, already covered by the Compute privilege-escalation page. It is not a Dataflow authorization boundary and additionally depends on network, OS Login, and worker lifecycle conditions.
- **`dataflow.jobs.updateContents` as arbitrary in-flight code replacement:** false. The current job update method changes state or supported runtime parameters. Updating pipeline code launches a replacement job and therefore returns to the `dataflow.jobs.create` boundary.
- **Snapshots, cancel, drain, and snapshot deletion:** availability impact and recovery-point destruction, not privilege escalation. They do not execute code with a new identity.
- **Job descriptions exposing pipeline options:** reconnaissance/post-exploitation disclosure, not privilege escalation. The current Dataflow audit reference also lists GetJob among methods that do not produce audit logs, so the old Data-Access-log assertion was removed.
- **Inline YAML as a separate H3:** folded into job create plus `actAs`; it is the payload-delivery mechanism for the same run-as boundary, not an independent permission primitive.
- **Flooding input to force autoscaling:** omitted as noisy, operationally risky, and unnecessary to establish the poisoning primitive.

### Material corrections

- Added `resourcemanager.projects.get` and `storage.buckets.get` to the regional Flex Template launch minimum, with `storage.buckets.create` only when the default staging bucket must be made.
- Separated caller authorization from worker, service-agent, staging, network, quota, API, and cross-project prerequisites.
- Corrected the cross-project worker-account contract: explicit Dataflow and Compute service-agent grants are required and `iam.disableCrossProjectServiceAccountUsage` must not be enforced.
- Removed the claim that a default Compute Engine service account necessarily has Editor. Newer organizations disable that automatic grant by default, and existing organizations can do so.
- Bounded poisoning to objects that are actually fetched after modification. It does not silently rewrite every already-running worker.
- Replaced the access-token exfiltration example with a harmless metadata-email proof and retained the general impact explanation.

### Telemetry conclusions

- Dataflow records `protoPayload.methodName="dataflow.jobs.create"` as non-LRO Admin Activity and enables it by default. This is the exact documented method string, including for a job launched through the Flex Template surface.
- The regional/template lookup of `resourcemanager.projects.get` is Data Access `ADMIN_READ` and is not on by default.
- Cloud Storage object create/delete/get operations are Data Access and are not enabled by default; Cloud Audit Logs does not track public-object access.
- Worker provisioning can produce always-on Compute Engine Admin Activity such as `v1.compute.instances.insert`; workload API calls are attributed to the worker service account and follow the called service's audit defaults.
- Metadata-server requests have no standalone Cloud Audit Log. Dataflow worker/application logs, object versions, job state, and downstream audit records remain useful signals.

### Local inspection performed

- `gcloud dataflow yaml run --help` confirmed `--yaml-pipeline`, `--service-account-email`, `--staging-location`, and `--temp-location`.
- The installed SDK source confirmed that the YAML command launches the regional public `Yaml_Template` through the Flex Templates launch endpoint and passes the inline YAML as a template parameter.
- Apache Beam's current YAML reference confirmed `MapToFields` Python callables and `LogForTesting`.

## 2026-09-28 — independent cross-review

A separate root review re-opened the current regional Flex Template authorization contract, Dataflow worker/service-agent guidance, cross-project attachment requirements, shadow-resource poisoning guidance, and Dataflow audit reference. It independently confirmed the five conditional launch permissions, both service-agent roles in the worker-account project, the organization-policy constraint, the object replacement boundary, and the documented non-LRO `dataflow.jobs.create` method. No additional book correction was required.

## 2026-09-28 — post-exploitation deduplication

Removed the standalone “Dataflow export from other services” H3. Its supposed minimum—job creation plus `actAs` on a worker with stronger source access—is the exact retained run-as-service-account privilege escalation, while a worker with no stronger access cannot create a confused-deputy read. Selecting a BigQuery, Bigtable, Pub/Sub or Storage export template is an impact/payload of that chain. When the caller already holds both source read and destination write, the template performs ordinary authorized transfer and adds no distinct boundary.

The old section also omitted regional Flex Template helper, staging, worker/service-agent, cross-project, network, policy and perimeter prerequisites and used a reasoned rather than current documented audit method. Those exact boundaries remain centralized in the privilege-escalation page and ledger. This was documentation-only; no job, bucket, object, account, binding or API state was created or changed.

## 2026-09-28 — reciprocal post-exploitation review

- Reopened the current regional Flex Template reference and confirmed its explicit launch permissions: `dataflow.jobs.create`, `resourcemanager.projects.get`, `iam.serviceAccounts.actAs`, `storage.buckets.get`, and conditional `storage.buckets.create`.
- Confirmed the no-garbage taxonomy decision. A worker with stronger source access is the existing run-as-service-account privilege escalation; a caller already holding source read and sink write merely performs authorized transfer. Neither case justifies a duplicate Dataflow post-exploitation H3.
- Reconfirmed that worker/service-agent, staging, network, organization-policy, quota and perimeter dependencies remain centralized on the privilege-escalation page. No book correction or cloud mutation was needed.
