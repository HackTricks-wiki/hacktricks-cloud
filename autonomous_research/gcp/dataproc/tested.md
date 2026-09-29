# Dataproc — tested

## 2026-09-29 — live 16-tool MCP surface and Viewer-level batch diagnostics

- Both global and `us-central1` regional live MCP schemas exposed 16 tools: 15 documented cluster/job/batch/session/operation tools plus the additional `analyze_batch_service` tool.
- The additional tool maps to `dataproc.batches.analyze`, is marked non-read-only, starts an `AnalyzeBatch` LRO and is `ADMIN_WRITE`. Current predefined-role metadata nevertheless includes the permission in Dataproc Viewer as well as editor/admin roles.
- Created one disposable Serverless PySpark batch that failed with a synthetic canary. A reduced Dataproc Viewer with no Logging or Storage role was denied both driver-output object access and Cloud Logging queries, but ordinary batch get exposed the canary in `stateMessage` together with the runtime SA, script/output URIs and properties. This validates workload-definition/error harvesting as a distinct post-exploitation read surface.
- The reduced caller's MCP `analyze_batch_service` call completed and returned only generic unavailable-insight/support guidance; it did not disclose the synthetic canary or driver logs. No transitive Logging/Storage disclosure was found.
- Deleted the batch, both test LRO records, dedicated bucket, exact default-staging prefix, runtime and Viewer identities, all IAM grants, key, configuration and local files. Dataproc remained enabled at baseline; an unrelated older failed batch was not changed.

## 2026-09-28 — privilege-escalation visibility and correctness audit

- Rated all 11 retained privilege-escalation techniques against the current Managed Service for Apache Spark audit matrix and the platform's driver, gateway, guest and downstream-service logs.
- Corrected exact RPC names and long-running-operation behavior. `GetCluster`/`ListClusters` are Data Access `ADMIN_READ`, while create/submit/instantiate operations are always-on Admin Activity.
- Narrowed resource-IAM self-grant: cluster-level Editor/`clusters.use` does not supply the project-level `dataproc.jobs.create` permission. A binding on an existing job cannot authorize a new job.
- Removed the unsupported assertion that a custom image's Docker `ENTRYPOINT` executes. Retained the useful supply-chain primitive only through documented dependency/environment hooks consumed by a later Spark workload.
- Corrected Component Gateway (`clusters.use`), OS Login sudo, Serverless runtime-role, staged-object overwrite and logging-suppression prerequisites. No cloud resource was created.
