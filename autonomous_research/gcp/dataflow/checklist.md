# Dataflow research checklist

## Completed in the 2026-09-28 documentation pass

- [x] Reconcile worker identity, caller `actAs`, Dataflow service-agent, and Compute service-agent
      boundaries.
- [x] Verify regional job/Flex Template launch permissions and local gcloud YAML flags.
- [x] Verify Cloud Storage overwrite permissions and distinguish content replacement from metadata
      update.
- [x] Reconcile Dataflow, Cloud Storage, Resource Manager, and Compute audit defaults.
- [x] Check whether `dataflow.jobs.updateContents` can replace pipeline code; reject that claim.
- [x] Consolidate inline YAML execution into the job-create run-as primitive.
- [x] Independently re-open the official Flex Template, worker/service-agent, cross-project,
      poisoning, and audit contracts after the first-pass rewrite.
- [x] Remove the duplicate post-exploitation export H3 and centralize the job-create plus `actAs`
      boundary in the privilege-escalation page.

## Safe future authorized tests

- [ ] In a disposable project, grant a caller only the documented regional Flex Template minimum
      and determine which principal performs each staging/temp object operation. Capture the exact
      `dataflow.jobs.create` request and any denied `actAs` record, then cancel the batch job and
      delete every test object and job artifact.
- [ ] Repeat with a cross-project worker service account to validate the exact Dataflow and Compute
      service-agent grants and the `iam.disableCrossProjectServiceAccountUsage` failure mode. Revoke
      all temporary IAM bindings afterward.
- [ ] Use a synthetic non-sensitive streaming pipeline to measure when a modified, unpinned UDF or
      staged dependency is fetched by an autoscaled worker. Compare object-generation pinning,
      versioning, and retention; restore/delete every test generation and tear down the job.
- [ ] Capture the exact object read/write principals and method names for the public YAML Flex
      Template launcher, staging path, and worker runtime. Do not generalize across runner versions
      without evidence.
- [ ] Test whether every supported replacement-job surface revalidates `iam.serviceAccounts.actAs`
      on the bound worker account. Do not publish an update-based bypass without a reproducible
      current control-plane result.
- [ ] Check Dataflow Prime and Runner v2 worker lifecycle telemetry separately; retain a technique
      only if it crosses a distinct authorization boundary rather than changing implementation
      details.
