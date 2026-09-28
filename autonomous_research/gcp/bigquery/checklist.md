# BigQuery — open leads

## Job metadata and audit boundaries

- [ ] With non-secret marker query parameters, determine whether `jobs.list`/`jobs.get` responses
  expose `queryParameters.parameterValue` to a `jobs.listAll` principal. Official documentation says
  parameter values are not logged, but does not clearly state the cross-principal Jobs API response.
- [ ] Recheck the documented no-log method list after major BigQuery audit schema releases,
  especially `GetJob`, `ListJobs`, table/model metadata and job deletion.
- [ ] Validate which successful and failed query paths omit `JobChange`, `TableDataRead` or
  `TableDataChange`; use harmless marker tables and compare Cloud Audit Logs with
  `INFORMATION_SCHEMA.JOBS*`.

## Least privilege and downstream evidence

- [ ] Test raw REST `tabledata.list` with only `bigquery.tables.getData` against an ordinary table,
  a row-policy table, a column-policy table and a fine-grained-DML table. Never use real sensitive
  data, and delete all disposable tables and policies after the matrix.
- [ ] Compare DML audit `deletedRowsCount`/`insertedRowsCount`/`truncated` with job `dmlStats` for
  `UPDATE`, `DELETE`, `MERGE` and `TRUNCATE`; document whether updates are represented as paired
  delete/insert counts or only in job statistics.
- [ ] Compare dataset-default CMEK patch telemetry with project `ALTER PROJECT` telemetry, including
  `PROJECT_OPTIONS_CHANGES`, then restore the original defaults and destroy every disposable key and
  table. Do not test key denial on data without an independent recovery copy.
- [ ] Recheck whether current capacity-commitment CLI syntax or available editions add a billing
  confirmation/control that materially changes the financial-DoS technique. Never purchase a real
  paid commitment merely to validate syntax.
