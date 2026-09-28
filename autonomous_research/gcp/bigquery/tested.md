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
