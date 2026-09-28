# Dataform — open research

## 2026-09-28 verified documentation contracts

- [x] Strict `iam.serviceAccounts.actAs` checks for repository create/update and workflow invocation,
  including an invocation-level `serviceAccount` override.
- [x] Effective service-account resolution and Dataform service-agent Token Creator prerequisite;
  scheduled workflow configurations additionally require service-agent `actAs`.
- [x] `setAuthenticatedUserAdmin=true` creator grant and location-level `CreatorRoleConfig` caveat.
- [x] Stable v1 workspace write, compilation-result creation, workflow-invocation creation, and
  direct repository commit request schemas.
- [x] `repositories.commit` internal-repository-only restriction and optional HEAD precondition.
- [x] Strict-mode prohibition on cron-scheduled releases for repositories not connected to a
  third-party repository; this invalidates the proposed automatic internal commit-poisoning chain.
- [x] Exact v1 Dataform audit methods/classes, automatic invocation completion signal, strict-act-as
  log, IAM Credentials token telemetry, and default-on BigQuery Data Access telemetry.
- [x] Removed or folded persistence, post-exploitation, recon, duplicate, and strict-mode-invalid
  material from the privilege-escalation page.

## Open bounded validation

- [ ] In a disposable project, verify the automatic creator binding with default, replaced, and
  disabled `CreatorRoleConfig`; delete all workspaces and repositories immediately afterward.
- [ ] Capture successful and denied strict-act-as platform logs under enforced mode and record the
  exact caller, effective-service-account, context, and method fields.
- [ ] Periodically re-check whether either strict-mode scheduled-release restrictions or the
  internal-only `repositories.commit` contract changes; do not promote the commit-poisoning chain
  unless an automatic compilation path exists without restoring caller `actAs`.
- [ ] Capture service-agent `GenerateAccessToken` and BigQuery `InsertJob` records to determine whether
  delegation metadata consistently exposes the Dataform service agent in addition to the effective
  service-account principal.
- [ ] Test whether an eligible service-account caller receives the same automatic creator binding as
  an end-user caller when `setAuthenticatedUserAdmin=true`; keep the book wording user-scoped until
  confirmed.
