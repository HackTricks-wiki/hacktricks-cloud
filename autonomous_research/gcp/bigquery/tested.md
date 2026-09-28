# BigQuery — tested

## 2026-09-28 — post-exploitation stealth, permissions and telemetry audit

- Reviewed all 11 retained BigQuery post-exploitation techniques against current official BigQuery,
  Data Transfer Service, Reservation API and Cloud KMS documentation. Added categorical stealth
  ratings that include durable state, downstream jobs and application failures rather than only the
  initiating API method. This pass was documentation-only; no cloud resource was touched.
- Confirmed the unusual metadata blind spot: `JobService.ListJobs` and `GetJob` are documented
  no-log methods even though project-wide job history can contain SQL and is retained for six months.
  `roles/bigquery.resourceViewer` is broader than the three sensitive job permissions.
- Corrected audit boundaries: query SQL is limited to 50K in `BigQueryAuditMetadata`, log entries are
  capped at 100K, BigQuery does not promise every completion/read/change entry for every failed or
  disrupted job, and DML `TableDataChange` can include deleted/inserted row counts and truncation.
- Corrected least privilege and feature limits for `tabledata.list`, exports, table expiration,
  deletion, DML/`CREATE OR REPLACE`, scheduled-transfer changes and BQML model inspection. Notable
  restrictions include row-policy TRUE-filter access, fine-grained-DML incompatibility with
  `tabledata.list`, extra overwrite/export permissions, and `ML.WEIGHTS` model-family limits.
- Corrected recovery and workload behavior: recursive dataset deletion has one dataset event rather
  than per-table events; customer time travel is 2–7 days and fail-safe is not self-service;
  deleting an assignment falls through to another assignment or on-demand, while deleting a
  reservation can fail in-flight jobs.
- Corrected CMEK semantics: a changed default applies only to newly created resources, never
  re-encrypts existing tables or their later partitions/writes, and attacker key control alone does
  not grant plaintext. The technique is availability/ransom and possible data loss. Dataset changes
  are Admin Activity; project defaults set with `ALTER PROJECT` are logged query jobs and also remain
  in `PROJECT_OPTIONS_CHANGES`.

## 2026-09-28 — cross-principal query-parameter exposure

- Live-tested with a zero-data synthetic `SELECT @marker` job created by a principal holding exactly
  `bigquery.jobs.create` (plus quota-project use), and a separate reader holding exactly
  `bigquery.jobs.listAll`, `bigquery.jobs.list` and `bigquery.jobs.get` (plus quota-project use).
- `jobs.list?allUsers=true&projection=full` found the other principal's job and returned the named
  parameter value. `jobs.get` returned the same value. The synthetic marker was absent from the
  BigQuery audit entry, confirming that parameterization redacts values from logs but not from job
  metadata visible to project-wide job readers.
- This is expected authorization under the documented full job projection, not a boundary bypass.
  It materially expands the established silent job-history technique: parameter values can contain
  secrets even when the SQL text contains only placeholders.
- The completed job metadata was deleted with `jobs.delete` (HTTP 200 and subsequent GET 404). Both
  service accounts, keys, custom roles, bindings and isolated configurations were deleted and
  independently verified absent.

## 2026-09-28 — exact `tabledata.list` and row-policy matrix

- A disposable principal holding exactly `bigquery.tables.getData` plus quota-project use—and no
  table/dataset metadata permission or `bigquery.jobs.create`—read both rows of a known synthetic
  table through raw `tabledata.list`.
- Adding a row access policy that granted the principal only `id = 1` changed the call to HTTP 403;
  it did not return the allowed subset. Dropping that policy and granting a `TRUE` filter restored
  HTTP 200 and both rows. This live-confirms the documented TRUE-filter requirement.
- In the live capture, each successful read page emitted two BigQuery Data Access entries: legacy
  `tabledataservice.list` and canonical `google.cloud.bigquery.v2.TableDataService.List` with
  `TABLEDATA_LIST_REQUEST`. Google documents legacy/current formats but does not guarantee a pair per
  request. The partial-policy denial emitted neither within the same observation window; this is not
  enough to claim a guaranteed audit blind spot for denied calls.
- The dataset/table and all row-policy DDL job metadata were deleted. The service account, key,
  custom role, binding and isolated configuration were also deleted and independently verified
  absent.

## 2026-09-28 — fine-grained DML live discrepancy and controlled follow-up

- Created a synthetic table with `enable_fine_grained_mutations = TRUE` in the `CREATE TABLE`
  statement and confirmed `INFORMATION_SCHEMA.TABLES.is_fine_grained_mutations_enabled = YES`.
- Before any mutating DML, the isolated caller holding exactly `bigquery.tables.getData` plus
  quota-project use still received HTTP 200 and both rows through `tabledata.list`. After a successful
  `UPDATE` changed one row, the same caller received HTTP 400 `INVALID_ARGUMENT` and no rows.
- A second run eliminated elapsed propagation as the explanation: two same-age tables both reported
  the flag as `YES` and returned rows; after mutating only one, the mutated table returned 400 while
  the untouched control continued to return 200. This contradicts the official categorical statement
  that any enabled table cannot use `tabledata.list`. It remains an undocumented live discrepancy,
  not a settled lifecycle contract. No row/column authorization was bypassed, so the observed behavior
  alone does not meet the security-vulnerability report bar.
- All three controlled attempts deleted their datasets/tables, explicit job metadata, service
  accounts, keys, custom roles, project bindings and isolated configurations. The first attempt that
  stopped during key activation was also cleaned and independently verified absent.

## 2026-09-28 — column-policy `selectedFields` matrix

- Attached a disposable Data Catalog policy tag to a synthetic `secret` column. The isolated reader
  held only `bigquery.tables.getData` on the target project plus quota-project use, with no BigQuery
  metadata permission or query-job permission.
- Without Fine-Grained Reader on the tag, `tabledata.list?selectedFields=id` returned HTTP 200 and
  both untagged values. Selecting only `secret`, or omitting `selectedFields` and thereby requesting
  all columns, returned HTTP 403 and no rows. Granting
  `roles/datacatalog.categoryFineGrainedReader` directly on the tag restored an HTTP 200 all-column
  response with both synthetic rows. No masking substitution or partial all-column response occurred.
- The audit capture contained the canonical and legacy BigQuery Data Access entries for each of the
  two successful pages. Neither of the two policy-denied requests appeared in that observation
  window; as with the row-policy case, this remains an observation rather than a guaranteed no-log
  contract.
- The first taxonomy cleanup call used an invalid parent-force assumption; the independent verifier
  caught the residue. The child policy tag was then deleted before its taxonomy, both resources were
  verified 404 while the API was live, and Data Catalog was returned to its original disabled state.
  The dataset/table, service account, key, role, binding and local configuration were also verified
  absent.
