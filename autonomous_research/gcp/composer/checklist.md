# Cloud Composer privilege-escalation checklist

## Published and documentation-validated

- [x] Environment creation with a selected service account: separate `create`, `actAs`, code-introduction, bucket eligibility, and worker-access prerequisites.
- [x] Environment update through attacker-controlled PyPI dependency: exact raw PATCH minimum, bounded execution context, LRO logging, and gcloud wrapper caveat.
- [x] Airflow CLI execution: connection/variable retrieval, existing-DAG execution boundary, REST execute/poll flow, and Secret Manager telemetry.
- [x] Existing environment bucket DAG injection: new-object versus overwrite permissions, scheduling caveat, and Cloud Storage/Composer log boundary.
- [x] Exact v1 and v1beta1 Composer audit methods, classes, default visibility, application logs, and downstream conditional signals.
- [x] Legacy `constraints/composer.enforceServiceAccountActAsCheck` exception and the current enforced-by-default attachment boundary.
- [x] Raw REST versus current `gcloud` helper reads and LRO polling, including Composer's explicit `GetOperation` audit exclusion.
- [x] Composer 2/3 package-build identity nuances and conditional Cloud Build/Artifact Registry telemetry.
- [x] Airflow 2.4.0 direct-API gate, older `kubectl` fallback, shared execute/poll permission, and exact line cursor behavior.

## Reviewed and rejected/folded

- [x] DAG download/source read — recon or post-exploitation.
- [x] Snapshot save/load — exfiltration or duplicate update control.
- [x] Plugin upload — duplicate bucket-write boundary and less deterministic than DAG injection.
- [x] `data/` upload — no documented automatic execution sink.
- [x] Web-server allow-all — exposure change, not authentication bypass.
- [x] `composer.dags.execute` — only conditionally useful existing workflow invocation.
- [x] User-workload secrets/config maps — conditional workload inputs and dominated by stronger permissions in relevant roles.
- [x] Composer 1/2 GKE pod pivot — Kubernetes post-exploitation, not a distinct Composer IAM primitive.

## Open research leads

- [ ] Test current Composer 3 behavior when a custom-bucket DAG exists before environment creation, including first-parse timing and exact application log categories, in a disposable authorized lab.
- [ ] Measure which PyPI build/import phase first executes attacker-controlled package code across supported Composer 2 and 3 images and whether build egress restrictions materially bound the primitive.
- [ ] Verify exact Airflow CLI output redaction and Secret Manager access/caching behavior for each supported secrets-backend configuration.
- [ ] Explore whether any current documented Composer field consumes attacker-controlled environment variables in a deterministic executable startup hook without relying on interpreter quirks.
- [ ] Revisit Composer 3 user-workload resource mutation if a common operator or default workload consumes those objects across a demonstrable privilege boundary.
