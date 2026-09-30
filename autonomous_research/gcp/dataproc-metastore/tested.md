# Dataproc Metastore research tested

## 2026-09-28 documentation audit

Scope was current official Google Cloud documentation, Dataproc Metastore REST/RPC and audit references, local Google Cloud CLI 586.0.0 help, and local CLI source inspection. No Google Cloud resource, identity, IAM policy, API state, or data was created or changed.

### Retained and consolidated techniques

- Export the metadata catalog to a caller-selected Cloud Storage bucket.
- Run read-only backend SQL through `QueryMetadata` and recover its artifact-bucket results.
- Overwrite catalog metadata through a compatible metadata import or backup restore.
- Surgically repoint a database, table, or partition location through `AlterMetadataResourceLocation`.

### Material corrections

- Reclassified `ExportMetadata`, `QueryMetadata`, `CreateMetadataImport`, `RestoreService`, and `AlterMetadataResourceLocation` from always-on Admin Activity to off-by-default Data Access, using their exact v1 audit method names and permission types.
- Added `google.longrunning.Operations.GetOperation` as Data Access `ADMIN_READ`, required by synchronous helper workflows but avoided by the asynchronous examples where the CLI supports `--async`.
- Corrected export authorization: both the caller and Dataproc Metastore service agent need `storage.objects.create` on the destination. Export is therefore not a caller-authorization-bypassing confused deputy.
- Bounded export to metadata. It does not export Hive internal-table data and does not grant access to referenced warehouse objects.
- Corrected direct query/mutation role drift. `roles/metastore.metadataQueryAdmin` contains `metastore.services.queryMetadata`, and `roles/metastore.metadataMutateAdmin` contains `metastore.services.mutateMetadata`; these permissions are not Owner-only.
- Replaced the obsolete alpha query example with the current GA command and the documented `SELECT * FROM TBLS;` catalog query.
- Documented the actual current CLI query flow: start `QueryMetadata`, poll the LRO, read the result manifest, and read the first result object with the caller's Cloud Storage client. This separates core RPC authorization from follow-up `metastore.operations.get` and `storage.objects.get` accesses.
- Consolidated import and restore as catalog-overwrite variants. Import requires `metastore.imports.create` plus source `storage.objects.get` for caller and service agent. Restore requires `metastore.services.restore`; a named backup also requires `metastore.backups.use`, while `backupLocation` must contain valid backup artifacts rather than arbitrary content. Google documents `roles/storage.objectUser` for service-agent access to scheduled-backup artifacts and does not publish a smaller exact permission subset.
- Bounded catalog poisoning: changing a warehouse location does not move data or change Cloud Storage IAM. Downstream content poisoning additionally requires compatible attacker content and pre-existing consumer read access to that location.
- Added service request/system logs, retained import/export/restore history, persistent query result objects, Cloud Storage Data Access events, and downstream workload failures as signals without claiming undocumented one-to-one platform-log mappings.

### Removed or folded headings

- `metastore.services.setIamPolicy` self-grant: genuine IAM privilege escalation, not post-exploitation. The old whole-catalog claim was also not bounded by the gRPC-versus-Thrift metadata IAM model.
- Kerberos/config discovery through `services.get`: useful enumeration, but not a distinct post-exploitation technique. Secret Manager access remains separately authorized.
- Disable deletion protection and delete service/backups: destructive denial of service with strong Admin Activity telemetry, below the page's useful post-exploitation bar.
- Separate import and restore headings: folded because both are validated catalog-overwrite workflows; their different authorization prerequisites and audit methods remain explicit.
- Separate table-property and move-table calls: folded into the shared `metastore.services.mutateMetadata` boundary; direct LOCATION repointing is the higher-value variant.

### Official sources reviewed

- Dataproc Metastore export, import, restore, administrator-interface, IAM-role, logging, and audit-logging documentation.
- v1 REST/RPC contracts for restore, export, query, mutation, imports, and long-running operations.
- Cloud Storage audit-logging contract for object reads/writes.
- Local `gcloud metastore services` help and the installed `query_metadata.py` command implementation.

## 2026-09-28 independent cross-review

- Reconfirmed that export evaluates `storage.objects.create` for both the caller and the target service's Dataproc Metastore service agent; the service agent performs the destination-object write.
- Reconfirmed that import requires `storage.objects.get` for both caller and service agent, whereas the restore REST contract evaluates caller IAM on the target service and, only for the named-backup branch, on the backup. `backupLocation` runtime object access is by the service agent under Google's documented `roles/storage.objectUser` grant.
- Clarified that fully qualified named backups can cross service, project, and region through the CLI/API, while a short backup ID is resolved under the target service.
- Reconfirmed from the installed GA command implementation that `query-metadata` polls the LRO and reads the result manifest plus first result object using the caller's Storage client; additional result object names remain in the manifest.
- Clarified the two distinct location fields for mutation: the regional service selector and the replacement `gs://` catalog URI. Database, table, and partition resource names remain relative to the selected service.
- Reconfirmed exact v1 audit methods and permission types, off-by-default Data Access visibility, two-entry LRO behavior (with the documented immediate-completion exception), and the exported `metastore.googleapis.com/requests` and `metastore.googleapis.com/system` platform streams.
- No live cloud call or resource mutation was performed.
