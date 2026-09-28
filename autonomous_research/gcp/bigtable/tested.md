# Bigtable research tested

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
