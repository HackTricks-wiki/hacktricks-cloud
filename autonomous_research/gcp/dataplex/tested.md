# Dataplex privilege-escalation research ledger

## 2026-09-28 — Data Product `CreateDataAsset` validation enforces backing-resource access

- Live-tested `CreateDataAsset` with `validateOnly=true` against an empty synthetic BigQuery table.
  The isolated caller held `roles/dataplex.dataProductsEditor`, including
  `dataplex.dataAssets.create`, but its authoritative BigQuery `testIamPermissions` response was
  empty. The request returned HTTP 403 on `bigquery.datasets.get`; it did not create a DataAsset or
  change the table IAM policy.
- As the positive control, project Metadata Viewer supplied dataset/table metadata access and a
  table-level BigQuery Data Owner grant supplied the documented table IAM permissions. The otherwise
  identical request returned HTTP 200 as an already-complete validation operation. DataAsset list
  remained empty and the table's directly attached IAM policy stayed byte-for-byte equivalent.
- The tested deputy hypothesis is therefore closed as secure at the first backing-resource boundary.
  `dataplex.dataAssets.create` alone cannot use validation to package or grant access to a BigQuery
  table that the caller cannot inspect. This is not a book technique or vulnerability report.
- Admin Activity method `google.cloud.dataplex.v1.DataProductService.CreateDataAsset` recorded the
  full resource, access-group role and `validate_only=true`. Both evaluated calls showed
  `dataplex.dataAssets.create` granted; the negative status named `bigquery.datasets.get`, while the
  positive status was empty.
- Three bounded harness iterations were cleaned. Independent inventory found zero test service
  accounts, IAM references, datasets, tables, Data Products, DataAssets, cached configurations or
  Dataplex service agent. Dataplex and BigQuery APIs were enabled at baseline and preserved. Cloud
  Asset Search temporarily retains three deleted-key index records after authoritative IAM deletion.

## Historical authorized validation

The `dataplex.tasks.update` confused-deputy hypothesis was tested in the authorized lab and rejected.
Updating either attacker-controlled execution fields or benign fields revalidated
`iam.serviceAccounts.actAs` on the task's bound execution service account. The test infrastructure
was removed. Do not restore an update-without-`actAs` technique unless the authorization contract
changes.

## 2026-09-28 — current documentation and local CLI audit

This pass used current official Google Cloud REST, IAM, audit-logging, BigQuery, Cloud Storage, and
Managed Service for Apache Spark documentation plus local Google Cloud SDK 586.0.0 help. It did not
call cloud APIs or create, modify, or delete cloud resources.

### Retained privilege-escalation primitives

1. **Task create plus service-account attachment.** `dataplex.tasks.create` accepts attacker code and
   an execution service account, while `iam.serviceAccounts.actAs` authorizes attachment. The
   execution service account must also have a usable Spark runtime and payload access. Contrary to
   the old page, the execution project can differ from the lake project; the service account must
   belong to the selected execution project.
2. **Managed asset IAM self-grant.** A lake-, zone-, or asset-level policy administrator can grant a
   Dataplex data role to itself. Dataplex reconciles that role to the attached Cloud Storage bucket
   or BigQuery dataset. The impact is limited by the Dataplex scope, attached assets, security-policy
   state, access mode, and backing-service prerequisites.
3. **Policy-tag IAM self-grant.** `datacatalog.categories.setIamPolicy` can grant
   `roles/datacatalog.categoryFineGrainedReader` and satisfy the additional policy-tag check on
   protected BigQuery columns. It does not grant the ordinary dataset/table permissions or bypass
   independent row, masking, perimeter, or network controls.

### Removed or folded from the privilege-escalation page

- **`dataplex.datascans.getData`:** useful post-exploitation data disclosure. Existing profile scan
  results can contain top-N values without requiring a new read of the source table, but the
  permission reveals data rather than increasing cloud privileges.
- **Metadata-job EXPORT:** catalog reconnaissance/exfiltration, not privilege escalation. Its scope
  is bounded by `dataplex.entryGroups.export`; organization-level mode does not itself bypass that
  authorization.
- **Metadata-job IMPORT with FULL sync:** destructive catalog tampering and defense evasion, not
  privilege escalation. It was removed rather than presenting deletion as a privilege gain.
- **Catalog entry-group IAM self-grant:** generic metadata visibility, lower value than the retained
  backing-data and policy-tag boundaries.
- **Recurring tasks:** persistence is a consequence of the task primitive, not a separate privilege
  escalation heading.
- **Environment creation:** no execution-service-account selector comparable to tasks was found in
  the local CLI surface.

### Material corrections

- Removed the false same-project restriction and documented `--execution-project` accurately.
- Removed lake creation from the task PoC and minimums; a task needs an existing lake, not
  `dataplex.lakes.create`.
- Distinguished the caller's minimum permissions from runtime, payload, service-agent, networking,
  quota, and cross-project prerequisites.
- Distinguished raw `setIamPolicy` minimums from gcloud `add-iam-policy-binding`, which also reads the
  existing policy.
- Bounded policy-tag escalation to callers that already have ordinary BigQuery data access.
- Replaced permission-like strings with exact audit methods, identified Managed Service for Apache
  Spark `BatchController.CreateBatch`, and separated Cloud Storage from BigQuery Data Access
  defaults. BigQuery query and table-read records are Data Access, not Admin Activity.

### Telemetry conclusions

- `google.cloud.dataplex.v1.DataplexService.CreateTask` and Dataplex `SetIamPolicy` are Admin
  Activity and always recorded. `CreateTask` is an LRO; a downstream Dataproc `CreateBatch` record
  is expected only when execution reaches managed Spark batch creation.
- Policy-tag changes appear as Data Catalog `SetIamPolicy` Admin Activity and expose the caller,
  target, and changed bindings.
- Cloud Storage object Data Access is disabled by default. BigQuery Data Access audit logging cannot
  be disabled; the two backing services must not share one default-visibility claim.

### Independent review corrections

- Rechecked the three retained primitives against current official role, API, and audit contracts.
- Removed an unsupported claim that BigQuery emits a separate policy-tag data-read event associated
  with the triggering query. The policy IAM change and subsequent BigQuery query/read are the
  supported signals.
