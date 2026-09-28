# BigQuery privilege-escalation audit

## 2026-09-28 — documentation-only permissions and telemetry review

- Rebuilt the privilege-escalation page from current Google Cloud primary documentation. No cloud
  resources were read or changed.
- Removed `Read Table`, `Export data`, and `Insert data` as non-escalation techniques. They are
  direct data access/exfiltration/integrity operations and already belong in BigQuery
  post-exploitation coverage.
- Merged the duplicate dataset IAM/ACL primitives and documented the fine-grained dataset ACL
  transition. DCL, enforcement-disabled updates, REST PATCH `UPDATE_ACL`, REST PUT, and
  `UPDATE_FULL` do not have the same permission boundary. Applied the same branching to
  authorized routines, views, and datasets because each mutates the dataset `.access` field.
- Corrected dataset/table examples to grant resource-compatible roles such as
  `roles/bigquery.dataOwner` and `roles/bigquery.dataViewer`, rather than presenting
  `roles/bigquery.admin` as the least-privilege resource-level grant.
- Corrected row-level security telemetry. Create/update/delete have dedicated
  `RowAccessPolicyService` Admin Activity events in addition to query-job telemetry. A policy
  grantee still needs base `bigquery.tables.getData`; the policy alone grants no table read.
- Bounded authorized-view/dataset claims. Creating or updating a view in an authorized dataset
  requires source permissions; authorization is a concealed indirect path, not a way for an
  otherwise unprivileged view owner to widen SQL indefinitely.
- Corrected Data Transfer permissions to the current `bigquery.transfers.*` namespace and retained
  the `iam.serviceAccounts.actAs` and Data Transfer service-agent token-minting prerequisites.
  Documented the run identity's source-read, destination-dataset, destination-create/updateData,
  DDL/DML, and conditional CMEK permissions.
- Rejected generic `CLOUD_RESOURCE` connection creation plus unrestricted target IAM write as an
  independent escalation technique. Target IAM write ordinarily lets the caller grant its own
  identity access directly, so the connection service account is unnecessary indirection. The
  chain becomes distinct only if an IAM condition, deny rule, or member-type restriction permits a
  binding to the connection-managed identity while preventing a direct attacker binding.
- Corrected Cloud SQL connection use: `bigquery.connections.get` is reconnaissance, not required
  for `EXTERNAL_QUERY`; impact is limited by the stored database user's privileges.
- Corrected a high-value logging edge case: Connection API `SetIamPolicy` is documented as a Data
  Access `ADMIN_READ` method in v1, not Admin Activity, and is therefore not logged by default
  unless BigQuery Connection API Admin Read logging is enabled. The v1beta1 `SetIamPolicy` method
  is explicitly listed as producing no audit log.
- Removed connection credential repointing as a privilege-escalation H3. It is tampering,
  poisoning, or denial of service unless combined with a separate privileged consumer, and should
  remain in post-exploitation research rather than the escalation page.
- Corrected column-security paths. Policy-tag Fine-Grained Reader is the raw-access grant for
  Data Catalog column-level security. `roles/bigquerydatapolicy.maskedReader` returns masked data,
  and Data Policy IAM does not make that role a per-policy raw-data grant. Data Policy v2 grantees
  use IAM v2 principal syntax, not legacy `user:` member syntax.
- Replaced the false `datacatalog.taxonomies.update`-only mass-unmask claim. Current Google
  documentation requires deleting all associated data policies before disabling taxonomy
  enforcement, so the retained chain requires both `bigquery.dataPolicies.delete` and
  `datacatalog.taxonomies.update`.
- Corrected Spark procedure permissions to `connections.delegate` for creation and
  `connections.use` for invocation. A new Spark connection identity is not privileged by default.
  Added conditional target-service audit logs for Google API calls and configuration-dependent
  network/application logs for non-Google egress.
- Corrected remote-function scope. Endpoints are supported regional Cloud Run/Cloud Run functions,
  not arbitrary Internet collectors, and the endpoint identity token is audience-bound rather
  than a general Google API token.
- Corrected authorized routines: changing a routine invalidates its authorization, so later silent
  widening without reauthorization is not a valid persistence claim.
- Separated SQL routine DDL from direct Routines API writes: SQL needs `bigquery.jobs.create`,
  direct insert/update does not, and `CREATE OR REPLACE` adds `bigquery.routines.update`.
- Added modern and legacy BigQuery audit-method aliases to detection guidance. Legacy
  `datasetservice.*`, `tableservice.*`, and `jobservice.*` names remain relevant alongside current
  `BigQueryAuditMetadata` method names.

## Techniques retained

1. Dataset ACL/IAM self-grant.
2. Table IAM self-grant.
3. Row access policy widening/removal.
4. Authorized view/dataset indirect access.
5. Scheduled SQL as an `actAs`-authorized service account.
6. Cloud SQL stored-credential use through `EXTERNAL_QUERY`.
7. Connection resource IAM self-grant.
8. Data Catalog Fine-Grained Reader self-grant.
9. Data Policy v2 raw grantee or masking-rule update.
10. Data-policy deletion plus taxonomy enforcement disablement.
11. Spark procedure execution through a privileged connection.
12. Remote-function invocation through a privileged connection.
13. Authorized routine indirect access.
