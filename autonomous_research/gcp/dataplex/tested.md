# Dataplex privilege-escalation research ledger

## 2026-09-29 — Data Lineage graph reconnaissance and MCP boundary

- Added the previously missing Data Lineage surface to Dataplex/Knowledge Catalog enumeration. The direct `SearchLinks` method returns adjacent entity links, while the Preview `search_lineage` MCP tool performs multi-root breadth-first upstream/downstream searches with column-level and process expansion. This maps provenance and downstream blast radius but does not read the referenced data.
- Unauthenticated `tools/list` exposed only the single static tool schema. A disposable principal held `datalineage.locations.searchLinks`, `datalineage.events.get`, `datalineage.events.getFields`, `datalineage.processes.get`, and `serviceusage.services.use`, but not `mcp.tools.call`. After IAM propagation, direct REST returned an empty success for a nonexistent owned FQN while MCP was denied on `mcp.googleapis.com/tools.call`; the owner positive control executed the same MCP request.
- The global MCP endpoint rejected a regional parent and required `locations/global`; regional REST remained valid. Documentation was bounded to endpoint/parent location parity rather than claiming that all global and regional lineage data are interchangeable.
- Recorded exact `DATA_READ` methods `SearchLinks` and `SearchLineageStreaming`; both are off-by-default Data Access. The wrapper is separately documented as service-specific MCP Data Access under `datalineage.googleapis.com/mcp`, enabled through the `mcp.googleapis.com` audit configuration.
- Removed the project binding, user-managed key, service account, custom role and isolated local credentials, then disabled Data Lineage to its baseline. Final checks found no residual asset.

## 2026-09-28 — Data Product principal replacement revalidates backing-resource IAM

- Live-tested an existing Data Product whose `readers` access group mapped a producer service account to `roles/bigquery.dataViewer` on a synthetic table. Before the update, the legitimate producer could list the harmless marker row (HTTP 200), the attacker-controlled producer could not (HTTP 403), and the table policy contained only the legitimate producer binding.
- The isolated updater held project `roles/dataplex.dataProductsEditor` and Service Usage Consumer. Its BigQuery `testIamPermissions` response for `tables.get`, `tables.getData`, `tables.getIamPolicy`, and `tables.setIamPolicy` was empty, and direct table metadata access returned HTTP 403. Its principal-only `PATCH` with `updateMask=accessGroups` was initially accepted as an LRO (HTTP 200), but LRO completion failed with code 7 because the caller lacked `bigquery.tables.getIamPolicy`. No attacker table binding or data access resulted.
- The Admin Activity start record showed `dataplex.dataProducts.update` granted to the isolated caller. The completion record carried the exact backing-table `getIamPolicy` denial. The initial asset grant and later revocation produced BigQuery `google.iam.v1.IAMPolicy.SetIamPolicy` records attributed to the DataAsset creator/deleter, not the Dataplex service agent. A successful marker read appeared as BigQuery `TableDataService.List` Data Access under the legitimate producer.
- Operational nuance: after the failed LRO, `GetDataProduct` still displayed the replacement service-account principal even though backing IAM remained on the legitimate producer. This partial metadata commit did not grant backing access and is not a useful offensive technique or security vulnerability on the tested path. An owner restored the legitimate principal before deletion. Retest only if a future access-request flow can turn failed-operation metadata into a privilege-bearing grant.
- Three bounded credential/setup attempts were cleaned. Final authoritative inventory found zero test service accounts, project IAM references, datasets, tables, Data Products, DataAssets, Dataplex service agent, local keys, isolated configurations, or harness processes. Baseline Dataplex and BigQuery API state was preserved.

## 2026-09-28 — Data Product `CreateDataAsset` validation enforces backing-resource access

- Live-tested `CreateDataAsset` with `validateOnly=true` against an empty synthetic BigQuery table. The isolated caller held `roles/dataplex.dataProductsEditor`, including `dataplex.dataAssets.create`, but its authoritative BigQuery `testIamPermissions` response was empty. The request returned HTTP 403 on `bigquery.datasets.get`; it did not create a DataAsset or change the table IAM policy.
- As the positive control, project Metadata Viewer supplied dataset/table metadata access and a table-level BigQuery Data Owner grant supplied the documented table IAM permissions. The otherwise identical request returned HTTP 200 as an already-complete validation operation. DataAsset list remained empty and the table's directly attached IAM policy stayed byte-for-byte equivalent.
- The tested deputy hypothesis is therefore closed as secure at the first backing-resource boundary. `dataplex.dataAssets.create` alone cannot use validation to package or grant access to a BigQuery table that the caller cannot inspect. This is not a book technique or vulnerability report.
- Admin Activity method `google.cloud.dataplex.v1.DataProductService.CreateDataAsset` recorded the full resource, access-group role and `validate_only=true`. Both evaluated calls showed `dataplex.dataAssets.create` granted; the negative status named `bigquery.datasets.get`, while the positive status was empty.
- Three bounded harness iterations were cleaned. Independent inventory found zero test service accounts, IAM references, datasets, tables, Data Products, DataAssets, cached configurations or Dataplex service agent. Dataplex and BigQuery APIs were enabled at baseline and preserved. Cloud Asset Search temporarily retains three deleted-key index records after authoritative IAM deletion.

## Historical authorized validation

The `dataplex.tasks.update` confused-deputy hypothesis was tested in the authorized lab and rejected. Updating either attacker-controlled execution fields or benign fields revalidated `iam.serviceAccounts.actAs` on the task's bound execution service account. The test infrastructure was removed. Do not restore an update-without-`actAs` technique unless the authorization contract changes.

## 2026-09-28 — current documentation and local CLI audit

This pass used current official Google Cloud REST, IAM, audit-logging, BigQuery, Cloud Storage, and Managed Service for Apache Spark documentation plus local Google Cloud SDK 586.0.0 help. It did not call cloud APIs or create, modify, or delete cloud resources.

### Retained privilege-escalation primitives

1. **Task create plus service-account attachment.** `dataplex.tasks.create` accepts attacker code and an execution service account, while `iam.serviceAccounts.actAs` authorizes attachment. The execution service account must also have a usable Spark runtime and payload access. Contrary to the old page, the execution project can differ from the lake project; the service account must belong to the selected execution project.
2. **Managed asset IAM self-grant.** A lake-, zone-, or asset-level policy administrator can grant a Dataplex data role to itself. Dataplex reconciles that role to the attached Cloud Storage bucket or BigQuery dataset. The impact is limited by the Dataplex scope, attached assets, security-policy state, access mode, and backing-service prerequisites.
3. **Policy-tag IAM self-grant.** `datacatalog.categories.setIamPolicy` can grant `roles/datacatalog.categoryFineGrainedReader` and satisfy the additional policy-tag check on protected BigQuery columns. It does not grant the ordinary dataset/table permissions or bypass independent row, masking, perimeter, or network controls.

### Removed or folded from the privilege-escalation page

- **`dataplex.datascans.getData`:** useful post-exploitation data disclosure. Existing profile scan results can contain top-N values without requiring a new read of the source table, but the permission reveals data rather than increasing cloud privileges.
- **Metadata-job EXPORT:** catalog reconnaissance/exfiltration, not privilege escalation. Its scope is bounded by `dataplex.entryGroups.export`; organization-level mode does not itself bypass that authorization.
- **Metadata-job IMPORT with FULL sync:** destructive catalog tampering and defense evasion, not privilege escalation. It was removed rather than presenting deletion as a privilege gain.
- **Catalog entry-group IAM self-grant:** generic metadata visibility, lower value than the retained backing-data and policy-tag boundaries.
- **Recurring tasks:** persistence is a consequence of the task primitive, not a separate privilege escalation heading.
- **Environment creation:** no execution-service-account selector comparable to tasks was found in the local CLI surface.

### Material corrections

- Removed the false same-project restriction and documented `--execution-project` accurately.
- Removed lake creation from the task PoC and minimums; a task needs an existing lake, not `dataplex.lakes.create`.
- Distinguished the caller's minimum permissions from runtime, payload, service-agent, networking, quota, and cross-project prerequisites.
- Distinguished raw `setIamPolicy` minimums from gcloud `add-iam-policy-binding`, which also reads the existing policy.
- Bounded policy-tag escalation to callers that already have ordinary BigQuery data access.
- Replaced permission-like strings with exact audit methods, identified Managed Service for Apache Spark `BatchController.CreateBatch`, and separated Cloud Storage from BigQuery Data Access defaults. BigQuery query and table-read records are Data Access, not Admin Activity.

### Telemetry conclusions

- `google.cloud.dataplex.v1.DataplexService.CreateTask` and Dataplex `SetIamPolicy` are Admin Activity and always recorded. `CreateTask` is an LRO; a downstream Dataproc `CreateBatch` record is expected only when execution reaches managed Spark batch creation.
- Policy-tag changes appear as Data Catalog `SetIamPolicy` Admin Activity and expose the caller, target, and changed bindings.
- Cloud Storage object Data Access is disabled by default. BigQuery Data Access audit logging cannot be disabled; the two backing services must not share one default-visibility claim.

### Independent review corrections

- Rechecked the three retained primitives against current official role, API, and audit contracts.
- Removed an unsupported claim that BigQuery emits a separate policy-tag data-read event associated with the triggering query. The policy IAM change and subsequent BigQuery query/read are the supported signals.
