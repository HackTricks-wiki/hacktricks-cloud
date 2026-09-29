# Dataform — tested and documented

## 2026-09-28 — privilege-escalation page audit

- Reduced the page to two useful boundaries: creator-admin repository bootstrap and invocation of an existing compilation result.
- Corrected the central identity contract. Strict act-as mode is globally enforced for repositories, and repository create/update and manual invocation require `iam.serviceAccounts.actAs` on the effective service account. The prior invocation-level arbitrary-SA/no-`actAs` implication is stale.
- Preserved `invocationConfig.serviceAccount` as a supported override, but bounded it by the same strict `actAs` check and Dataform service-agent token-creation prerequisite.
- Documented `setAuthenticatedUserAdmin=true` as the reason an eligible authenticated user with parent-level `dataform.repositories.create` can bootstrap repository admin in the user root, while respecting team-folder exclusion and location-level `CreatorRoleConfig` disablement or role replacement.
- Rejected the internal-repository commit-poisoning hypothesis after reconciling two current product constraints. `repositories.commit` only works when `gitRemoteSettings.url` is absent, while strict act-as mode prevents configuring cron-scheduled releases for repositories not connected to a third-party repository. A manual compilation/invocation would restore the caller's `actAs` check.
- Rejected the repository-IAM self-grant chain as a distinct escalation primitive because its only proposed downstream path was the invalid internal scheduled-commit chain. Repository IAM mutation remains a generic child-resource authorization change, not a complete privilege-escalation result.
- Removed standalone scheduling persistence, workspace-only overwrite, git-secret repointing, end-user OAuth, token-status recon, and deletion/cleanup claims from the privilege-escalation page. They were persistence, post-exploitation, incomplete without another permission, or not distinct escalation primitives.
- Corrected audit classes. `CreateRepository`, `CreateWorkspace`, and `SetIamPolicy` are Admin Activity. `WriteFile`, `CreateCompilationResult`, `CreateWorkflowInvocation`, and `CommitRepositoryChanges` are Data Access and off by default. `CommitRepositoryChanges` is not Admin Activity. The repository-policy read records are Data Access; Google's audit catalog lists both the Dataform v1 and generic IAM-policy `GetIamPolicy` method names for that permission.
- Added the always-generated workflow-invocation completion platform log, strict-act-as platform signal, optional IAM Credentials `GenerateAccessToken` audit record, and downstream BigQuery audit records. BigQuery Data Access is enabled by default, unlike ordinary Data Access audit logs.
- Local Cloud SDK 586.0.0 inspection confirmed that no `gcloud dataform` command group is available; all commands use the stable v1 REST API.

This pass used current official Google Cloud documentation and local CLI inspection only. It did not call Dataform, IAM, BigQuery, or any other cloud API and created no cloud resources.

## 2026-09-29 — user-credential GA and remote MCP boundary

- Reviewed the current stable discovery revision (`20260920`) and the GA user-credential execution contract. `InvocationConfig` is mutually selectable between `serviceAccount` and `endUserAuthConfig`; the latter exposes an output-only `userEmail` plus consented additional OAuth scopes, never an access or refresh token.
- Corrected the enumeration page's stale default-service-agent statement. Current workflows require a custom service account or a Google Account authorization; the default Dataform service agent cannot be the workflow execution identity.
- Folded the useful user-credential case into the existing invocation technique. A principal with `dataform.workflowInvocations.create` can reference a known workflow configuration whose owner already authorized BigQuery Pipelines. The caller can trigger only the saved release/action set; this does not expose the credential or permit SQL/configuration changes.
- Kept strict `iam.serviceAccounts.actAs` wording limited to service-account-backed invocations. A user-credential workflow has no attached service account, but depends on the consenting user's OAuth grant and downstream permissions remaining valid.
- Live-negative-tested the Dataform remote MCP wrapper with a fresh service account holding only `dataform.repositories.list`. Direct REST listing succeeded, while MCP `list_repositories` was denied specifically on `mcp.googleapis.com/tools.call`. No repository was created or read.
- Removed the disposable identity and project binding. Final inventory showed no test principal, IAM member, or Dataform repository. The API was already enabled and remained at baseline.

No interactive Google Account OAuth fixture exists in this lab, so retained-owner patch behavior is not claimed. The public technique is bounded to the documented create-invocation contract and saved workflow configuration.
