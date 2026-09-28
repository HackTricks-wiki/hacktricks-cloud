# Cloud Source Repositories research checklist

## Completed 2026-09-28

- [x] Apply the June 17, 2024 new-customer and organization eligibility boundary without claiming a
      full service shutdown.
- [x] Separate repository read/data exposure from genuine privilege escalation.
- [x] Bound the source-writer chain to an existing enabled Cloud Build trigger, matching filters,
      attacker-controlled executed content, approval state, and the trigger's pinned service account.
- [x] Confirm that repository-event invocation does not require the writer to hold
      `cloudbuild.builds.create` or `iam.serviceAccounts.actAs`.
- [x] Confirm that `source.repos.update` is not supported in custom roles and refresh its current
      predefined-role examples.
- [x] Bound repository IAM self-grant to the target repository and preserve policy bindings,
      version, and etag in the documented workflow.
- [x] Correct the notification boundary to repository/project configuration permission plus
      `iam.serviceAccounts.actAs`, same-project service account, and topic publish access.
- [x] Distinguish `GitProtocol.ReceivePack` / `UploadPack` / `LsRemote` Data Access visibility from
      `SourceRepo.SetIamPolicy` Admin Activity visibility and state the non-LRO boundary.
- [x] Avoid attributing an internally processed repository event to the manual Cloud Build
      `RunBuildTrigger` method without evidence.
- [x] Remove/fold credential setup, Secret Manager, push-block, notification, deletion, and public-
      repository claims that are not distinct privilege-escalation primitives.
- [x] Independently re-open the current official service, trigger and audit contracts and make the
      IAM merge condition-safe by leaving conditional writer bindings untouched.

## Safe future tests

- [ ] In an eligible disposable organization/project, create a minimal CSR repository and a
      no-privilege trigger, then capture the exact build/audit records for an automatic push. Remove
      the trigger and repository immediately; do not use a privileged runtime identity.
- [ ] With Data Access logging temporarily enabled in a disposable project, capture
      `GitProtocol.ReceivePack`, `UploadPack`, and `LsRemote` entries and confirm principal/ref fields;
      restore the prior logging policy after the test.
- [ ] Test the smallest repository-level policy containing only `source.repos.setIamPolicy` in a
      custom role, then self-grant writer on an empty disposable repository. Preserve/restore the
      original policy and delete all temporary identities and resources.
- [ ] Revisit mirrored-repository `SyncRepo` behavior only if it yields a distinct authorization
      path; do not duplicate ordinary push or external-SCM control.

## Post-exploitation taxonomy follow-up 2026-09-28

- [x] Decide that full private-source/history recovery is high-value post-exploitation, not merely
      enumeration or a privilege-escalation claim.
- [x] Separate the known-name minimum (`source.repos.get`) from optional project discovery
      (`source.repos.list`), and state that listing does not authorize cloning.
- [x] Verify stable gcloud clone behavior against local command source and official CLI help.
- [x] Add exact `SourceRepo.GetRepo` / `ListRepos` and `GitProtocol.LsRemote` / `UploadPack` audit
      classes, disabled-by-default visibility, and non-LRO boundaries.
- [x] Bound secret recovery to committed/reachable data and downstream credentials that remain valid.
- [ ] In an eligible disposable project, enable Source Repositories Data Access logging, clone an
      empty synthetic repository once through gcloud and once through a direct Git URL, compare the
      exact `GetRepo`, `LsRemote`, and `UploadPack` entries, then restore logging and delete the repo.
