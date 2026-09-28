# Bigtable research checklist

## Privilege-escalation audit verified from current official documentation — 2026-09-28

- [x] Instance-, table-, backup-, authorized-view-, and continuous-materialized-view IAM policy
      surfaces and their inheritance bounds; logical-view direct IAM remains an open validation lead.
- [x] Read-only predefined-role inspection: `roles/bigtable.admin` contains all five retained
      `setIamPolicy` permissions; `roles/bigtable.editor` contains none of them while already carrying
      the documented data/view/create/restore capabilities.
- [x] Preservation-safe `getIamPolicy` plus `setIamPolicy` helper boundary versus a raw full-policy
      replacement with `setIamPolicy` alone.
- [x] Backup self-grant restore prerequisites across source backup, destination table creation,
      destination read access, and CMEK compatibility.
- [x] Authorized-view definition expansion using empty row and qualifier prefixes, bounded to named
      column families and an existing view read/mutate grant.
- [x] Generic `BigtableInstanceAdmin.SetIamPolicy` versus `BigtableTableAdmin.SetIamPolicy` resource
      disambiguation and the `UpdateAuthorizedView`/`RestoreTable` LRO records.
- [x] Rejected logical/materialized-view creation as a read escalation because current documentation
      requires `bigtable.tables.readRows` on the source table.
- [x] Rejected schema-bundle IAM as a low-impact metadata-only self-grant and did not duplicate it in
      the book.

## Verified from current official documentation

- [x] Base-table `ReadRows` permission, audit method, and default Data Access visibility.
- [x] GoogleSQL `PrepareQuery` / `ExecuteQuery` permission boundary for base tables.
- [x] Authorized, logical, and materialized-view read boundaries.
- [x] Mutation and `DropRowRange` permissions and audit classes.
- [x] `ReadModifyWriteRow` dual read/write permission requirement for table and authorized-view targets.
- [x] Standard Bigtable metrics and change-stream downstream signals.
- [x] Backup restore source/destination permissions and current gcloud syntax.
- [x] Undelete window, CMEK restriction, deletion protection, and IAM-policy behavior.

## Open bounded validation leads

- [ ] With a disposable logical view and policy, live-confirm role grantability and downstream
      authorization through the logical-view resource-level `setIamPolicy` endpoint; remove the
      binding and view immediately. Keep it out of the book until captured.
- [ ] Capture the exact `resourceName`, request policy redaction, and start/completion multiplicity
      for instance/table/backup/view IAM and authorized-view expansion under minimum custom roles.
- [ ] Verify the minimum permissions used by each additive gcloud IAM helper separately from direct
      full-policy REST replacement, including etag-conflict behavior.
- [ ] In a disposable Bigtable lab, capture the exact `authorizationInfo.resource` values for authorized-view, logical-view, and materialized-view reads.
- [ ] Confirm whether each current language client emits both `PrepareQuery` and `ExecuteQuery` for logical/materialized-view SQL and compare their permission-denied behavior.
- [ ] Capture cross-project `RestoreTable` audit entries in both source and destination projects to verify placement and any secondary service-generated record.
- [ ] Compare `DropRowRange` Data Access records, Monitoring metric deltas, and pre-enabled change-stream records for full-table versus prefix deletion.
- [ ] Confirm audit-field redaction across point reads, range reads, filters, and SQL; official documentation states that cell values are not audited.
- [ ] Recheck these permission and audit-method mappings after future Bigtable SQL/view GA changes.

## Privilege-escalation independent cross-review — 2026-09-28

- [x] Rechecked resource scope and predefined/custom-role grantability for each retained IAM
      self-grant against current Bigtable access-control documentation.
- [x] Verified IAM write audit methods are Admin Activity `ADMIN_WRITE` and not LROs; verified
      `RestoreTable` and `UpdateAuthorizedView` are Admin Activity LRO methods.
- [x] Removed the unproven logical-view direct-policy claim while preserving it as a bounded live
      validation lead.
- [x] Corrected restore audit placement so a second source-project restore record is not assumed.
- [x] Tightened source/destination CMEK and destination service-agent prerequisites.
- [x] Verified non-interactive authorized-view PATCH does not pre-read the view; documented the
      interactive `get` requirement and lack of etag concurrency protection in the shown command.
- [x] Split the LRO submission permissions from `bigtable.instances.get`, which the synchronous
      gcloud helpers need to poll; `--async` does not poll.
- [x] Revalidated command shapes, references, Markdown details/fences, and diff hygiene.
