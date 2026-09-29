# BigLake / Lakehouse research checklist

## Completed documentation checks

- [x] Separate BigQuery Cloud Storage BigLake tables from both Lakehouse runtime catalog and BigLake metastore (classic).
- [x] Verify current stable `gcloud biglake iceberg` catalog, namespace, table, and IAM commands.
- [x] Verify BigQuery connection delegation and table query minimum permissions.
- [x] Verify current predefined Lakehouse role contents and resource-level IAM inheritance.
- [x] Verify credential-vending response fields, identity boundary, and prefix/expiration limits.
- [x] Verify current Iceberg REST CommitTable path and exact audit method.
- [x] Verify classic table location field, PATCH permission, resource path, and exact audit method.
- [x] Reconcile BigQuery, BigLake, and Cloud Storage audit defaults and LRO boundaries.
- [x] Remove destructive-only, duplicate, and permission-name-only techniques.
- [x] Correct enum links and current command syntax.
- [x] Cross-review IAM helpers for version-3, `etag`, condition, and unrelated-binding preservation; ensure only an unconditional target-role binding is created or amended.
- [x] Confirm table/catalog/namespace inheritance and that child policies cannot erase inherited parent grants.
- [x] Resolve the stable credential RPC name and distinguish its audit-catalog omission from the explicit v1alpha/v1beta no-audit entries.
- [x] Split SQL DDL job telemetry from table-creation Activity and direct `tables.insert` telemetry.
- [x] Recheck credential-vending, commit, classic-table, and downstream Storage impact bounds.

## Safe future tests

- [ ] In a disposable project/catalog, call stable v1 `/credentials` with a read-only table binding; inspect `biglake.googleapis.com` logs and downstream Storage principal attribution. Delete the catalog, table, namespace, objects, bucket grants, and service identities that can be removed.
- [ ] Repeat with custom roles that isolate `biglake.tables.getData` and `biglake.tables.updateData`; record the exact error/authorization boundary without broad roles.
- [ ] Capture a supported Spark/Iceberg client transaction and compare read-only credential vending, staged object writes, and the final `UpdateIcebergTable` commit audit event.
- [ ] Verify whether a no-op or metadata-only CommitTable requires only `biglake.tables.update`, and which data-changing commits additionally require `biglake.tables.updateData`.
- [ ] In an isolated classic catalog, PATCH only `hiveOptions.storageDescriptor.locationUri` using a custom role with `biglake.tables.update`; verify `etag`, cache timing, exact audit payload, and the consuming identity's bucket requirement. Restore the original URI before deleting all test resources.
- [ ] Test BigQuery `tables.insert` versus SQL DDL creation of a connection-backed external table, confirming the raw absence/presence of `bigquery.jobs.create` and the Admin Activity/Data Access event split. Delete the table and all temporary data immediately.

## Guardrails

- [ ] Do not enable the API or create a catalog merely to resolve a documentation ambiguity unless a fully removable, no-residue plan is approved first; per-catalog managed identities may outlive the visible resource.
- [ ] Never print, persist, or commit a returned `gcs.oauth2.token`; if a future test stores a response temporarily, restrict permissions and securely remove it as soon as evidence is saved.
- [ ] Never point a production classic table at a test bucket or commit a snapshot to a real table.
- [ ] Keep credential-vending read access, writable vended credentials, and catalog commit authority as separate observations in future telemetry work.
