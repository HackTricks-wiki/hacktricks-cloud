# BigQuery — open leads

## Persistence and public-access boundaries

- [ ] With an empty disposable dataset, validate whether `allAuthenticatedUsers` can call
  `tabledata.list` and query through an unrelated billing project with only its documented dataset
  role; confirm victim-data-project versus execution-project log routing. Remove the ACL, table,
  dataset, test identities, bindings, and job metadata immediately.
- [ ] Capture a short synthetic continuous query under a service account and verify initial job,
  cancellation/completion, and destination publish telemetry. Do not infer periodic or per-row
  BigQuery audit entries when the service does not promise them.
- [x] Reconcile the current view-management guide (updates preserve authorized-view status) with the
  DatasetAccessEntry REST field description. A live individual-view matrix showed that an update
  checks source `tables.getData` and source `datasets.update`, then preserves authorization after
  those direct permissions are revoked; the same principal's direct source read was denied.
- [x] Validate authorized-dataset future-view behavior separately with non-sensitive rows. A writer
  of the authorized view dataset still needed direct source `bigquery.tables.getData` to create a
  future view; dataset-level authorization did not make source-blind view creation succeed.
- [ ] Recheck BigQuery's dataset ACL schema for any future addition of tokenless `allUsers`; current
  documentation lists only `allAuthenticatedUsers` among public-like special groups.

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

## Data agents and Gemini Enterprise publication

- [x] Triage the September 2026 BigQuery data-agent publication workflow. Default Google-managed
  credentials are managed OAuth client credentials, not a privileged runtime identity: the end user
  completes a one-time BigQuery OAuth sign-in, and Google documents that the agent acts with that
  user's permissions. Do not present this feature alone as a confused-deputy escalation.
- [ ] With two synthetic users and non-sensitive tables, test same-project Agent Registry and
  cross-project A2A-card publication for identity/token mix-ups. Confirm that the low-privilege user
  cannot inherit the publisher's or Gemini Enterprise administrator's BigQuery access.
- [ ] Test whether an agent editor can change instructions or knowledge sources so a later privileged
  user's conversation discloses query results to other agent users, shared conversation history, or
  an attacker-controlled sink. Keep all data synthetic and remove the agent, registry entry, gateway
  binding and app configuration after each run.
- [ ] Check A2A card and Agent Registry import authorization for endpoint/card substitution across
  projects, regions and deleted/recreated agent identifiers. Treat an attacker-controlled endpoint
  accepted by an authorized administrator as expected social/configuration risk unless a trust or
  ownership check is bypassed.
