# Bigtable research checklist

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

- [ ] In a disposable Bigtable lab, capture the exact `authorizationInfo.resource` values for authorized-view, logical-view, and materialized-view reads.
- [ ] Confirm whether each current language client emits both `PrepareQuery` and `ExecuteQuery` for logical/materialized-view SQL and compare their permission-denied behavior.
- [ ] Capture cross-project `RestoreTable` audit entries in both source and destination projects to verify placement and any secondary service-generated record.
- [ ] Compare `DropRowRange` Data Access records, Monitoring metric deltas, and pre-enabled change-stream records for full-table versus prefix deletion.
- [ ] Confirm audit-field redaction across point reads, range reads, filters, and SQL; official documentation states that cell values are not audited.
- [ ] Recheck these permission and audit-method mappings after future Bigtable SQL/view GA changes.
