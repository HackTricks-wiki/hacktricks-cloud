# Cloud Data Fusion research checklist

## Completed documentation checks

- [x] Separate caller, Data Fusion service-agent, namespace design-time, and pipeline VM identities.
- [x] Confirm the current permissions and stages of all predefined Data Fusion roles.
- [x] Verify `roles/datafusion.runner` contains only `datafusion.instances.runtime` and is assigned to the pipeline VM service account.
- [x] Verify caller permissions for pipeline create/run, Preview, namespace service-account configuration, and instance/namespace IAM policy operations.
- [x] Verify the official CDAP deploy/start paths and current `gcloud` instance/namespace IAM commands.
- [x] Verify current Data Fusion and Managed Service for Apache Spark audit methods, classes, default visibility, and LRO status.
- [x] Remove credential theft from privilege escalation and reject the false namespace-runtime-SA chain.
- [x] Reconcile the contradictory current RBAC documentation by expressing the invariant as effective `datafusion.instances.get`, not an assumed explicit or implicit Accessor binding.
- [x] Record the version 6.5 RBAC service-account OAuth scope requirement.

## Safe future validation

- [ ] On an already-existing disposable instance, use custom roles to test the exact four-permission pipeline path: `instances.get`, `namespaces.get`, `pipelines.create`, and `pipelines.execute`. Confirm no caller-side `instances.runtime` requirement. Do not create an instance solely for this test.
- [ ] Run a harmless built-in PySpark pipeline against an already-authorized, least-privileged runtime service account; capture the caller's Data Fusion audit entry, pipeline platform logs, runtime principal, and any `CreateCluster`/`DeleteCluster` LRO pair. Delete the pipeline immediately.
- [ ] Send a harmless direct app-deploy `PUT` on an existing disposable instance and resolve the audit-catalog gap: determine whether a method is emitted despite the absence of a documented deploy handler. Delete the app immediately.
- [ ] Preview a synthetic source readable only by a least-privileged design-time service account. Confirm the result limit, caller audit method, downstream principal, and target-service Data Access entry. Remove the draft/connection immediately.
- [ ] With two disposable principals and a scratch namespace, verify whether namespace `add-iam-policy-binding` requires both `namespaces.getIamPolicy` and `namespaces.setIamPolicy`, and whether a set-only REST replacement succeeds. Restore the exact original policy immediately.
- [ ] Capture namespace IAM audit entries to confirm their exact emitted `protoPayload.methodName`, log class, and default visibility; the current audit catalog lists generic instance IAM methods but does not separately enumerate the namespace permission.
- [ ] Verify the precise audit method emitted by the namespace workload-identity validate/set endpoints. Restore the previous namespace service account immediately.

## Related coverage still to audit

- [x] Rewrite Data Fusion post-exploitation telemetry against the current handler catalog and retain
      only the documented Secure Store value-read boundary.
- [x] Require effective `datafusion.instances.get` as the instance-access boundary for Secure Store
      reads even when the endpoint URL is known, and record the version 6.5 token-scope caveat.
- [ ] On an already-existing disposable instance, capture `pipelineConnections.get` responses for
      synthetic JDBC/SaaS connections and determine which sensitive properties are returned,
      masked or replaced by secure-key references. Delete the connections immediately.
- [ ] Rewrite Data Fusion persistence telemetry for schedules, artifacts, connections, and secure-key changes; current Admin Activity handlers invalidate the blanket “not audited” claims.
- [ ] Re-evaluate the scheduled pipeline and malicious artifact techniques after recording exact artifact-deploy and schedule API schemas on an existing disposable instance.

## Guardrails

- [ ] Never create a Data Fusion instance merely to answer a documentation question; instance provisioning is slow and billable.
- [ ] Never leave pipelines, previews, artifacts, schedules, connections, namespace bindings, compute profiles, clusters, or IAM bindings behind after testing.
- [ ] Do not alter the Data Fusion service-agent role or pipeline VM service-account bindings outside a disposable test project.
