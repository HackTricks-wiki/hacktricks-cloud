# BigQuery — open leads

## Job metadata and audit boundaries

- [x] With a non-secret marker query parameter, confirmed that full-projection `jobs.list` and
  `jobs.get` expose `queryParameters.parameterValue` to a separate `jobs.listAll` principal even
  though the value is absent from BigQuery audit logs. The job metadata and every test identity were
  deleted and verified absent.
- [ ] Recheck the documented no-log method list after major BigQuery audit schema releases,
  especially `GetJob`, `ListJobs`, and table/model metadata. `DeleteJob` is Data Access audited; keep
  deletion telemetry separate from the no-log reads.
- [ ] Validate which successful and failed query paths omit `JobChange`, `TableDataRead` or
  `TableDataChange`; use harmless marker tables and compare Cloud Audit Logs with
  `INFORMATION_SCHEMA.JOBS*`.

## Least privilege and downstream evidence

- [x] Raw REST `tabledata.list` with only `bigquery.tables.getData` is complete for ordinary tables,
  row policies, column policy tags, and an observed fine-grained-DML discrepancy. Ordinary and
  `TRUE`-filter access succeeded; a partial row filter returned 403. An untagged-column projection
  succeeded while tagged/all-column reads returned 403 until Fine-Grained Reader was granted. In a
  same-age two-table control, an enabled table remained readable until mutation while its unmutated
  control remained readable. The official contract says any enabled table is incompatible, so
  monitor/retest rather than treating mutation as a supported lifecycle rule. All disposable tables,
  policies, IAM material, and temporarily enabled API state were deleted and verified absent.
- [ ] Compare DML audit `deletedRowsCount`/`insertedRowsCount`/`truncated` with job `dmlStats` for
  `UPDATE`, `DELETE`, `MERGE` and `TRUNCATE`; document whether updates are represented as paired
  delete/insert counts or only in job statistics.
- [ ] Compare dataset-default CMEK patch telemetry with project `ALTER PROJECT` telemetry, including
  `PROJECT_OPTIONS_CHANGES`, then restore the original defaults and destroy every disposable key and
  table. Do not test key denial on data without an independent recovery copy.
- [ ] Recheck whether current capacity-commitment CLI syntax or available editions add a billing
  confirmation/control that materially changes the financial-DoS technique. Never purchase a real
  paid commitment merely to validate syntax.
