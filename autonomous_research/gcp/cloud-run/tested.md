# Cloud Run — tested

## 2026-09-26 — post-exploitation permission and audit drift review
- Corrected an outdated absolute claim that service/job/revision reads and `RunJob` can never be
  attributed. The current Cloud Run audit table maps the reads to Data Access `ADMIN_READ` and
  `RunJob` to `DATA_WRITE`; both remain disabled by default. Preserved the earlier contrary live
  observation as a reason for defenders to validate delivery, not as the documented contract.
- Corrected the image-recovery workflow to use the immutable v1 revision `status.imageDigest` and
  export the assembled container filesystem. `spec.containers[].image` can retain the input tag and
  is not itself proof of the digest that the revision serves.
- Corrected the nonexistent `vpcaccess.connectors.use` permission. Attaching an existing connector
  relies on `vpcaccess.connectors.get` plus `compute.networks.access`; the supported predefined
  grant is `roles/vpcaccess.user`, with Compute Viewer also documented for deployment tooling.
- Added exact minimum permissions and categorical stealth ratings to all five post-exploitation
  techniques, and removed the overclaim that deletion erases Cloud Audit/request/container logs.
- The lab currently contains no Cloud Run services. Enumeration was read-only; no service,
  connector, image or other infrastructure was created.

## 2026-09-26 — `run.locations.exportImage` source-registry bypass
- Created a custom role containing exactly `run.locations.exportImage`; GCP accepted the permission even though it is absent from the common Cloud Run/basic predefined roles. A caller with only that role successfully called `ExportImage` and `ExportStatus` for a known revision without `run.revisions.get` or any Artifact Registry permission.
- Destination authorization is evaluated as the source project's Cloud Run service agent, not the caller: giving the caller `roles/artifactregistry.writer` did not allow upload; removing that grant and granting Writer only to `service-<SOURCE_PROJECT_NUMBER>@serverless-robot-prod.iam.gserviceaccount.com` succeeded.
- The destination must be a package path (`<REGION>-docker.pkg.dev/<PROJECT>/<REPO>/<PACKAGE>`). A bare repository URL completed with `failed to upload to Artifact Registry`; the package path returned `successfully uploaded image`, a digest, and a generated tag.
- Repeated the export from a revision referencing the resulting private Artifact Registry image. The stripped caller still exported it successfully without source-repository read access, confirming that Cloud Run exports its cached immutable copy.
- The project had no Cloud Run Data Access audit configuration, and neither successful `ExportImage` nor `ExportStatus` produced a matching audit entry. The official audit table classifies both as `DATA_READ` under `run.locations.exportImage`.
- Deleted the service (including the failed control revision), destination repository and copied packages, test service account/key, project binding, custom role, isolated gcloud configuration, and local key file; verified the resources/binding/file absent. The custom role remains only as a normal soft-deleted IAM tombstone.

## 2026-09-26 — Worker Pool update boundary and audit shape
- Deployed a minimum-size, one-instance worker pool with the Compute default service account. A caller granted a custom role containing only `run.workerpools.update` directly on that pool, with no `iam.serviceAccounts.actAs`, attempted a v2 patch limited to `template.containers`. The request was denied specifically on `iam.serviceAccounts.actAs` for the unchanged default service account. Separate IAM audit entries recorded the failed `actAs` checks.
- Corrected the book's audit resource type from `cloud_run_revision` to the live `cloud_run_worker_pool` type (`worker_pool_name`, `location`, `project_id` labels).
- Current `gcloud run worker-pools deploy` is GA and creates a missing pool through `UpdateWorkerPool` with `allowMissing:true`. The live Admin Activity entry checked both `run.workerpools.update` and `run.workerpools.create`; a rule limited to `CreateWorkerPool` misses this CLI path.
- Deleted the worker pool immediately after the boundary test, then removed the resource/project bindings, test service account/key, custom role, isolated gcloud configuration, and local key file. Verified the pool, active identity/binding, and file absent; only the normal soft-deleted custom-role tombstone remains.

## 2026-09-26 — instance update / service-identity boundary
- Created a disposable Cloud Run instance in `us-west1` with a dedicated service account. The caller had a custom role containing **only** `run.instances.update` and no `iam.serviceAccounts.actAs` on the instance identity. Direct v2 `PATCH` with `updateMask=containers` attempted to add one inert environment variable without changing the service identity. Result: HTTP `403 PERMISSION_DENIED`, `Permission 'iam.serviceaccounts.actAs' denied on service account ...`. This rules out the unchanged-identity update bypass for the preview instance resource.
- Confirmed Cloud Audit: `google.cloud.run.v2.Instances.UpdateInstance` in `cloudaudit.googleapis.com/activity`, caller set to the limited service account, `status.code=7`, status message naming the denied `actAs`. Owner creation emitted `google.cloud.run.v1.Instances.CreateInstance` in Admin Activity and `/Instances.CreateInstance` as an unattributed System Event.
- Removed the instance and test IAM bindings/service accounts/custom role; the cleanup script verified the instance was absent. This is a negative boundary result, so no separate attack technique was added. The existing Cloud Run update technique now mentions the instance variant and the log shape.

## 2026-09-26 — system-managed Agent Identity update boundary
- Enabled Agent Registry and App Hub APIs solely for this test. The first preview `agent-identity` service failed to start because its workload-certificate volume could not mount; deleted it and disabled both APIs. Retried with Google's supported `--no-identity-certificate` option, and the service deployed successfully. Its Knative revision had `run.googleapis.com/identity-type: agent-identity`, while `spec.template.spec.serviceAccountName` still named the project's Compute Engine default service account.
- A separate caller had **only** `run.services.update`. A direct v2 `PATCH` changing only `template.containers` to add an inert environment variable returned HTTP 403: `Permission 'iam.serviceaccounts.actAs' denied on service account <PROJECT_NUMBER>-compute@developer.gserviceaccount.com`. The existing agent identity did not create an `actAs`-free update path. Cloud Audit logged `google.cloud.run.v2.Services.UpdateService` in Admin Activity with the limited caller, `status.code=7`, and the denied service account.
- Both disposable services and their test IAM bindings, caller accounts, and custom roles were removed. Agent Registry and App Hub APIs were disabled again; no Cloud Run service from this probe remains. This is a negative result, not a book technique.
