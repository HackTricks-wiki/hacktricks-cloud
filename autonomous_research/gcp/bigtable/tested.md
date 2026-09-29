# Bigtable research tested

## 2026-09-28 privilege-escalation documentation audit

This pass used current official documentation, local Google Cloud CLI help, and read-only predefined-role inspection only. It created or changed no Google Cloud resource, IAM policy, API, or service configuration.

### Retained primitives

- Instance IAM self-grant, bounded to one instance and its descendants.
- Table IAM self-grant, bounded to one table and applicable child resources.
- Backup IAM self-grant followed by restore to an authorized existing destination instance.
- Authorized/continuous-materialized-view IAM self-grant, bounded to the view definition.
- Authorized-view definition widening by a principal that can already use and update that view.

### Material corrections

- Split raw `setIamPolicy` minimums from additive gcloud helpers: the API write permission can replace a known complete policy, while a preservation-safe read/merge/write also needs `getIamPolicy`.
- Corrected backup exploitation to require source `bigtable.backups.restore`, destination `bigtable.tables.create`, destination row-read access, an existing destination instance, and CMEK compatibility when applicable. The restored table does not inherit the live table IAM policy.
- Bounded table- and view-level grants to the resource where the policy is attached; they do not confer sibling-table or instance administration.
- Distinguished the gcloud/API authorized-view PATCH from the console's **Save as view** workflow; the current guide warns that the latter overwrites previous view access unless it is reconfigured.
- Retained authorized and continuous materialized view `setIamPolicy` using the documented resource-level IAM boundary. Although logical views expose IAM REST methods, their current access guide prescribes a project-level conditional grant, so direct logical-view self-grant remains a validation lead rather than a book claim.
- Corrected telemetry: policy writes are always-on `ADMIN_WRITE`; `RestoreTable` and `UpdateAuthorizedView` are LROs; later Data API reads/writes are off-by-default Data Access.
- Removed logical/materialized-view creation as a speculative read escalation. Both current creation guides require `bigtable.tables.readRows` on the source table.
- Did not retain schema-bundle self-grant because it provides only narrow schema metadata and is below the book's technique-value threshold.

## 2026-09-28 privilege-escalation independent cross-review

This independent pass used current official Bigtable IAM, backup/CMEK, REST, audit-logging, and gcloud documentation plus local read-only gcloud source/help. It made no cloud calls or changes.

- Confirmed the resource-scoped `setIamPolicy` permissions, predefined/custom-role grantability for instance, table, backup, authorized view, and continuous materialized view, and the two generic Admin Activity method names. The IAM writes are not LROs.
- Removed logical-view direct self-grant from the retained combined technique. The REST surface and permission exist, but the current logical-view guide documents a project-level conditional role grant instead of a logical-view policy grant; downstream enforcement therefore remains unproven.
- Corrected cross-project restore detection: `RestoreTable` is documented against the destination table parent. A second source-project restore audit record is not a published contract; the prior source-backup IAM write remains independently visible there.
- Tightened CMEK restore prerequisites: the pinned source key version must remain enabled and accessible to the source Bigtable service agent; the destination must be CMEK-protected but need not use the same configuration, and its service agent needs `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the destination keys.
- Verified that `gcloud bigtable authorized-views update --definition-file ... --no-interactive` patches without a preliminary get. Interactive diff mode additionally needs `bigtable.authorizedViews.get`; omitting an etag leaves the update without concurrency protection.
- Added `bigtable.instances.get` as a helper-side prerequisite when the shown restore and authorized-view update commands wait for their LROs; `--async` avoids polling.
- Rechecked the shown instance/table/backup IAM, restore, authorized-view IAM, and authorized-view update command shapes against current gcloud help/source.

## 2026-09-28 documentation audit

Scope was documentation and local CLI-help review only. No Google Cloud resource was created, changed, or deleted.

### Retained and consolidated techniques

- Base-table row reads through `ReadRows` or GoogleSQL.
- Scoped-view reads for authorized, logical, and continuous materialized views.
- Table/view mutations and `DropRowRange` row destruction.
- Backup restoration into a new table, including an authorized cross-project destination.
- Undelete of a recently deleted non-CMEK table.

### Material corrections

- Removed the claim that GoogleSQL `ExecuteQuery` independently bypasses `bigtable.tables.readRows` for a base table. The current audit authorization table lists both `bigtable.instances.executeQuery` and `bigtable.tables.readRows`, and documents `PrepareQuery` separately.
- Bounded view exposure to each view definition and separated logical-view definer rights (`bigtable.logicalViews.readRows` without source-table row access) from ordinary base-table access.
- Classified `google.bigtable.admin.v2.BigtableTableAdmin.DropRowRange` as Data Access `DATA_WRITE`, despite its Admin API method name. It is disabled by default and uses `bigtable.tables.mutateRows`.
- Corrected the current restore command to `gcloud bigtable tables restore` and documented source/destination permissions separately.
- Removed the implication that a restore creator automatically owns or can read the new table. Reading still requires destination `bigtable.tables.readRows` or equivalent inherited access.
- Added the approximately seven-day undelete limit, CMEK exclusion, automatic deletion protection, and the fact that fine-grained table IAM bindings are not recovered.
- Distinguished always-on Admin Activity for restore/undelete from off-by-default Data Access records for row reads/writes.
- Added bounded downstream detection through standard Bigtable metrics and pre-existing change streams; metrics do not identify callers.
- Clarified that `ReadModifyWriteRow` is the dual-permission exception: it requires both row read and row mutation access, including both corresponding authorized-view permissions when the view is the target.
- Removed an unsupported implication that Admin API `DropRowRange` necessarily increments the Data API `server/modified_rows_count` metric. A pre-enabled change stream explicitly records `DropRowRange`, while application failures and storage/serving changes remain separate downstream signals.
- Clarified that change-stream deletion records are evidence, not a backup of old cell values; recovery requires a usable backup, application copy, or a downstream copy already maintained by a consumer.

### Removed or folded headings

- Dataflow export/import examples: generic cross-service pipelines with materially broader permissions and cost, redundant with direct read/mutation primitives.
- Resource IAM self-grant: privilege escalation, already belongs on the Bigtable privilege-escalation page rather than post-exploitation.
- Generic delete-operation list: mostly destructive administration/denial of service rather than distinct Bigtable data post-exploitation; the unusually important `DropRowRange` row wipe remains under data tampering.
- Separate authorized/logical/materialized-view headings: consolidated around the actual scoped-read security boundary.
- Separate SQL heading: folded into base-table/view reads after correcting its authorization semantics.

### Official sources reviewed

- Bigtable cbt reference and local gcloud 586.0.0 command help.
- Bigtable IAM access-control documentation.
- Bigtable Data API and Admin API audit-logging references.
- Bigtable audit-field and Monitoring metric references.
- Logical, authorized, and materialized view documentation.
- Backup, restore, table management/undelete, and change-stream documentation.
