# BigQuery privilege escalation — tested and reviewed

## 2026-09-28 — end-to-end documentation audit

- Documentation-only review against the current BigQuery, BigQuery Connection API, BigQuery Data
  Transfer Service, Data Policy, Data Catalog, IAM, and audit-log references. No cloud resource was
  created or changed.
- Retained 12 distinct privilege-boundary techniques: dataset/table/connection IAM self-grants;
  policy-tag and masking-policy weakening; complete column-enforcement disablement; Spark-procedure
  and remote-function execution; authorized routines and authorized views/datasets; row-policy
  widening; and scheduled queries bound to a service account.
- Moved `bigquery.connections.use` with Cloud SQL `EXTERNAL_QUERY` to post-exploitation. It consumes
  an already-authorized stored database credential and does not grant new GCP permissions.
- Confirmed that BigQuery Data Access logging is always on only for `bigquery.googleapis.com`.
  Connection API, Data Transfer Service, Data Catalog, Cloud Run, and destination-service audit
  defaults must be evaluated independently.
- Kept current/legacy BigQuery audit method names as alternatives. Documentation does not promise a
  duplicate pair of entries for every request.
- Kept authorized-view/dataset and authorized-routine paths bounded: source-data access is required
  when creating/changing the object. The current view-management guide says a view update preserves
  its authorization; authorized-routine updates instead require reauthorization. Neither is a
  source-IAM bypass after the editor's source access is revoked.

## Rejected or recategorized hypotheses

- `bigquery.connections.create` alone is not durable escalation or persistence. A newly created
  Cloud Resource connection identity starts without target-resource privileges, and deleting the
  connection deletes its credential; a recreated identity is distinct and must not be described as
  inheriting stale grants.
- The documented BigQuery dataset ACL broad member is `allAuthenticatedUsers`; current dataset ACL
  docs do not document a tokenless `allUsers` read path, and the API requires authentication.
- Transfer-config `iam.serviceAccounts.actAs` is an authorization check on configuration creation or
  update; it must not be presented as a guaranteed separate IAM Credentials audit method.

## Earlier detailed permissions and telemetry review (preserved)

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
  for `EXTERNAL_QUERY`; impact is limited by the stored database user's privileges. The current
  review preserves this finding on the post-exploitation page rather than as escalation.
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

## Current retained privilege-escalation inventory

1. Dataset ACL/IAM self-grant.
2. Connection resource IAM self-grant.
3. Data Catalog Fine-Grained Reader self-grant.
4. Data Policy v2 raw grantee or masking-rule update.
5. Data-policy deletion plus taxonomy enforcement disablement.
6. Spark procedure execution through a privileged connection.
7. Remote-function invocation through a privileged connection.
8. Authorized routine indirect access.
9. Table IAM self-grant.
10. Row access policy widening/removal.
11. Authorized view/dataset indirect access.
12. Scheduled SQL as an `actAs`-authorized service account.

The earlier inventory counted Cloud SQL stored-credential use as a thirteenth technique. The
end-to-end audit above recategorizes that operation as post-exploitation while preserving the
original permission and telemetry research.
