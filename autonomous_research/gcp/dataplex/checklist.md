# Dataplex privilege-escalation research checklist

## Completed documentation and local checks — 2026-09-28

- [x] Live-test Data Product `CreateDataAsset` with `validateOnly=true`: a caller with
      `dataplex.dataAssets.create` and zero BigQuery permissions was denied on
      `bigquery.datasets.get`; the metadata plus table-IAM positive control succeeded without
      creating an asset or changing table IAM.
- [x] Classify every original heading as privilege escalation, post-exploitation, reconnaissance, destructive defense evasion, duplicate, or unsupported.
- [x] Verify task create request semantics, ON_DEMAND behavior, execution-project selection, service account attachment, runtime prerequisites, and exact CreateTask audit method.
- [x] Preserve the historical negative result that task update revalidates `actAs`.
- [x] Verify lake/zone/asset IAM permissions, data-role scope, asset access-mode semantics, and Dataplex SetIamPolicy/GetIamPolicy audit classes.
- [x] Verify policy-tag IAM permissions, fine-grained-reader effect, ordinary BigQuery access boundary, safe gcloud helper, and policy-tag audit evidence.
- [x] Separate Cloud Storage and BigQuery Data Access logging defaults.
- [x] Check Google Cloud SDK 586.0.0 help for task, asset IAM, policy-tag IAM, and metadata-job flags.
- [x] Add exact minimums, bounded impact, categorical stealth, and expandable telemetry to every
      retained H3.
- [x] Independent cross-review bounded the downstream Dataproc batch event to executions that reach
      that stage, marked `CreateTask` as an LRO, and removed an unsupported separate policy-tag
      data-read audit claim.
- [x] Map Data Lineage direct and remote-MCP graph search, validate the global parent requirement,
      confirm the extra `mcp.tools.call` gate with an underlying-only identity, and record the exact
      off-by-default `SearchLinks` / `SearchLineageStreaming` telemetry.

## Safe future validation leads

- [x] On a synthetic Data Product and packaged BigQuery table, an isolated Data Products Editor
      with an empty BigQuery permission set could start a principal-only update, but LRO completion
      failed on `bigquery.tables.getIamPolicy`; the backing grant did not move. The failed LRO left
      replacement-principal metadata visible until an owner restored it, but conferred no access.
- [ ] If an already-available predefined role can supply only BigQuery `getIamPolicy` without
      `setIamPolicy`, repeat the principal swap to identify the next enforcement point without
      creating a soft-deleted custom role. Do not weaken the tested caller boundary merely to force
      a success.
- [ ] In an authorized disposable environment, create one ON_DEMAND task whose lake and execution projects differ; capture both projects' CreateTask, Dataproc batch, and service-agent audit entries, then delete the task and payload immediately.
- [ ] On a disposable DIRECT Cloud Storage asset, add and remove a data-reader binding while recording the exact downstream bucket-IAM method and principal used by reconciliation.
- [ ] Repeat managed-access reconciliation against a disposable BigQuery dataset and record the exact dataset IAM method, propagation delay, and removal behavior.
- [ ] Capture policy-tag GetIamPolicy/SetIamPolicy and the subsequent protected-column query to confirm the documented separation between the tag check and originating query.

## Do not restore without stronger evidence

- [ ] Do not describe DataScan result reads or metadata EXPORT as privilege escalation; route them to post-exploitation if a dedicated page is created.
- [ ] Do not describe FULL-sync metadata IMPORT as privilege escalation; it is destructive catalog tampering/defense evasion.
- [ ] Do not claim task update bypasses `iam.serviceAccounts.actAs`.
- [ ] Do not claim execution service accounts must belong to the lake project when `--execution-project` selects another project.
- [ ] Do not claim all backing-service Data Access logs share the same default visibility.
