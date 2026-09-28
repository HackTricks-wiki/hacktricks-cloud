# Dataproc — tested

## 2026-09-28 — privilege-escalation visibility and correctness audit

- Rated all 11 retained privilege-escalation techniques against the current Managed Service for
  Apache Spark audit matrix and the platform's driver, gateway, guest and downstream-service logs.
- Corrected exact RPC names and long-running-operation behavior. `GetCluster`/`ListClusters` are
  Data Access `ADMIN_READ`, while create/submit/instantiate operations are always-on Admin Activity.
- Narrowed resource-IAM self-grant: cluster-level Editor/`clusters.use` does not supply the
  project-level `dataproc.jobs.create` permission. A binding on an existing job cannot authorize a
  new job.
- Removed the unsupported assertion that a custom image's Docker `ENTRYPOINT` executes. Retained the
  useful supply-chain primitive only through documented dependency/environment hooks consumed by a
  later Spark workload.
- Corrected Component Gateway (`clusters.use`), OS Login sudo, Serverless runtime-role, staged-object
  overwrite and logging-suppression prerequisites. No cloud resource was created.
