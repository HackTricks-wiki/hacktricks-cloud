# BigQuery privilege-escalation checklist

## Completed 2026-09-28

- [x] Inventory every original level-three heading and separate escalation from direct
      post-exploitation.
- [x] Give every retained technique explicit minimum permissions/prerequisites, Potential Impact,
      categorical Stealth, and an expandable Logs generated table.
- [x] Reconcile dataset ACL changes with fine-grained dataset ACL enforcement.
- [x] Reconcile table IAM and row access policy permission/log boundaries.
- [x] Bound authorized-view, authorized-dataset, and authorized-routine behavior.
- [x] Reconcile scheduled-query run-as and service-agent prerequisites.
- [x] Reconcile connection creation/use/IAM methods and Connection API audit defaults.
- [x] Reconcile Data Catalog policy-tag and BigQuery Data Policy raw/masked access paths.
- [x] Reconcile Spark procedure and remote-function delegate/use boundaries.
- [x] Branch dataset ACL, authorized-resource, and routine permissions by fine-grained enforcement
      and REST/CLI mutation mode.
- [x] Separate modern and legacy BigQuery audit names, Connection API v1 and v1beta1 audit
      behavior, SQL routine DDL and direct API writes, and Spark downstream telemetry.
- [x] Reject generic connection-identity plus unrestricted target-IAM write as redundant.
- [x] Use official Google Cloud primary documentation only; no cloud resources touched.
- [x] Reclassify Cloud SQL `EXTERNAL_QUERY` as post-exploitation and remove its stale escalation
      count without discarding the earlier permission research.
- [x] Reconcile persistence and cross-account sharing with the current 150-day continuous-query
      limit and the dataset ACL's authenticated-only broad member.

## Open leads / future safe validation

- [ ] In a disposable project with fine-grained dataset ACL enforcement enabled, capture the exact
      permission checks and audit methods for DCL `GRANT`, `UPDATE_ACL`, and `UPDATE_FULL` side by
      side, then remove all test bindings and datasets.
- [ ] Confirm whether current `bq add-iam-policy-binding --table=true` performs a separately logged
      `GetIamPolicy` when BigQuery Admin Read logging is explicitly enabled.
- [ ] Capture the exact current BigQueryAuditMetadata fields for authorized-dataset and
      authorized-routine access entries and for their downstream query lineage.
- [ ] Reconcile the current view-management guide's authorization-preservation statement with the
      DatasetAccessEntry REST field's reauthorization statement in a disposable authorized view.
- [ ] In a disposable Cloud SQL database, capture the exact connection-use authorization entries,
      foreign SQL retained in BigQuery job metadata, and database-side principal attribution; keep
      the test read-only and destroy the database and connection afterward.
- [ ] Validate Data Policy v2 `AddGrantees` and SQL `GRANT FINE_GRAINED_READ` against a
      `RAW_DATA_ACCESS_POLICY`, including exact audit service/method/version and propagation delay.
- [ ] Validate the full delete-data-policies then clear-`activatedPolicyTypes` chain, including the
      intermediate query behavior and exact rollback sequence. Do not leave enforcement disabled.
- [ ] Capture Spark procedure runtime identity and workload logs without attempting token export;
      delete the procedure, connection, and all generated staging resources immediately afterward.
- [ ] Verify whether Cloud Run request logging exposes or redacts the remote-function
      `Authorization` header and confirm the exact OIDC audience; never publish a live token.
- [ ] Test whether a real IAM condition, deny policy, principal-type restriction, or delegated
      binding system can allow granting a target role to a BigQuery connection-managed service
      account while preventing the same caller from granting equivalent access to itself. Keep
      `CLOUD_RESOURCE` connection bridging out of the book unless this restricted-binding premise
      is demonstrated; delete the connection and all test bindings after validation.
- [ ] Recheck Connection API v1 and v1beta1 audit catalogs after API deprecation changes.
- [ ] Validate direct Routines API versus SQL DDL audit differences without invoking external
      workloads.
- [ ] Validate scheduled-query service-account attribution in same-project and cross-project
      configurations using synthetic data and complete cleanup.
