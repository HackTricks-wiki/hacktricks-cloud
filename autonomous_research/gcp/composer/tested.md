# Cloud Composer privilege-escalation research

## 2026-09-28 — documentation and local CLI audit

No cloud resources were accessed, created, or modified. The page was reconciled against current Cloud Composer access-control, REST, audit-logging, Cloud Storage, Secret Manager, and IAM documentation. Relevant `gcloud composer environments create`, `update`, and `run` help surfaces were checked locally.

- Reduced the page to four independent, high-value escalation boundaries: create an environment over a chosen identity using a prepopulated custom bucket; install attacker-controlled Python with `composer.environments.update`; use `executeAirflowCommand` for Airflow secrets or already-present code; and inject a DAG through direct bucket write.
- Corrected environment creation: `composer.environments.create` plus `iam.serviceAccounts.actAs` selects an identity but does not alone submit code. The deterministic chain additionally needs a writable, eligible custom bucket, prepopulated DAG, and Composer Worker access for the environment service account.
- Corrected `actAs` wording. Composer predefined roles do not provide the separate service-account attachment permission; `roles/iam.serviceAccountUser` is the standard predefined grant. The earlier statement that only Editor and Owner contain it was misleading.
- Replaced the brittle `PYTHONWARNINGS`/`BROWSER` environment-variable reverse shell with Google's documented custom-PyPI execution boundary. The direct PATCH minimum is `composer.environments.update`; the gcloud wrapper can add `composer.environments.get`. The image-build identity can be a configured/default Cloud Build account, the environment account, or the legacy Cloud Build account, so the page no longer assumes every installation phase runs under one identity.
- Bounded `executeAirflowCommand`: it can expose Airflow connections/variables and run code already available to Airflow, but does not itself upload an arbitrary new DAG. Both execute and poll calls use `composer.environments.executeAirflowCommand`; their exact v1/v1beta1 audit methods are always-on Admin Activity.
- Corrected connection-secret telemetry. A Secret Manager-backed lookup can generate `AccessSecretVersion` Data Access, disabled by default; metadata-database values do not generate that method.
- Corrected bucket-write minimums and visibility. A new DAG object needs `storage.objects.create`; overwrite also needs `storage.objects.delete`. Object writes are Cloud Storage `DATA_WRITE` and disabled by default, with no Composer Admin Activity event merely for the upload.
- Added exact long-running-operation semantics for environment create/update and distinguished configurable Composer/Airflow application logs and conditional downstream-service audit records from Cloud Composer control-plane audit logs.
- Reconciled the current CLI helpers with the raw authorization boundaries. `gcloud composer environments create --async` submits without a preliminary environment read or operation poll; synchronous create and update polling require `composer.operations.get`, while Composer explicitly excludes `google.longrunning.Operations.GetOperation` from audit logging. The update and Airflow-run wrappers do perform `GetEnvironment`, which is disabled-by-default Data Access.
- Recorded the legacy Composer service-account attachment exception: organizations still subject to the older behavior must enforce `constraints/composer.enforceServiceAccountActAsCheck`; where the constraint is unavailable, Google states that the `actAs` check is already enforced.
- Reconciled package build and runtime identities without treating them as interchangeable. Composer 2 documents default/legacy Cloud Build service-account behavior and an environment-service-account fallback, while Composer 3 says the environment account builds component images but still documents Cloud Build access for private repositories. Added the always-on Cloud Build `CreateBuild` event and the disabled-by-default Artifact Registry Docker upload/download Data Access methods as conditional downstream telemetry.
- Added the Airflow 2.4.0 boundary for the direct execute/poll API. Older `gcloud composer environments run` behavior falls back to `kubectl` and has separate connectivity and Kubernetes authorization requirements. Confirmed that execute and poll share `composer.environments.executeAirflowCommand`, and corrected the polling cursor to start at line 1 and advance to one more than the highest returned line number.

## Folded or rejected material

- DAG download and source-code retrieval are reconnaissance or post-exploitation, not privilege escalation.
- Snapshot save is exfiltration; snapshot load is a more complex form of environment update and did not add an independent privilege boundary.
- Plugin upload was folded into the bucket-write boundary. Plugin synchronization/loading is version- and component-dependent and is less deterministic than a DAG.
- Uploading arbitrary files into `data/` has no automatic execution contract and was removed as a standalone technique.
- Opening the Airflow web-server network ACL expands exposure but does not bypass Airflow authentication or independently grant stronger privileges.
- `composer.dags.execute` only triggers an existing workflow; impact is entirely conditional on that DAG and was retained as a prerequisite nuance rather than a generic escalation primitive.
- Composer 3 user-workload Secret/ConfigMap mutations and service-agent-role IAM permissions were not kept as Composer-specific standalone techniques because they are conditional workload inputs or duplicate generic IAM self-grant boundaries.
- Direct GKE worker-pod access for Composer 1/2 belongs to Kubernetes/Container post-exploitation and duplicates the GKE coverage.
