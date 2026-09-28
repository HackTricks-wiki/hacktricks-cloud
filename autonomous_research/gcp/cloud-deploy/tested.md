# Cloud Deploy privilege-escalation research

## 2026-09-28 — official documentation and local CLI audit

No Cloud Deploy, Cloud Build, Cloud Storage, GKE, or Cloud Run resources were accessed or changed. Current official service-account, execution-environment, task/hook, configuration-schema, IAM, deployment, and audit-logging contracts were reviewed. Local Google Cloud CLI 586.0.0 help and current predefined role permission lists were also checked.

### Retained boundaries

- Pipeline/target control plus release/rollout creation and service-account attachment can execute an attacker-defined predeploy task in a Cloud Build execution environment as the selected execution account.
- Release and rollout authority on an existing pipeline can push attacker-controlled source, image substitutions, or manifests to trusted targets. This can become execution under an application runtime identity, but only within the target, runtime, and admission boundaries.
- Resource-level `setIamPolicy` on delivery pipelines, targets, custom target types, or deploy policies is a scoped self-grant primitive. It does not itself supply service-account `actAs`, storage access, or runtime deployment rights.

### Material corrections

- Removed the claim that an existing-pipeline release/rollout works without `iam.serviceAccounts.actAs`. Official documentation explicitly requires `actAs` on the render execution account for release creation and on the deployment execution account for rollout creation/promotion.
- Removed the proposed no-`actAs` default-account bypass. An omitted service account selects the default Compute Engine service account, but the caller attachment check still applies. The default account is also not guaranteed to retain `roles/editor` because automatic grants can be disabled or remediated.
- Replaced the obsolete claim of three independent execution-account fields with the current direct `executionConfigs.serviceAccount` schema. The older nested `defaultPool.serviceAccount` and `privatePool.serviceAccount` syntax remains supported as an alternative syntax, not additional simultaneous identities.
- Separated caller permissions from execution-account prerequisites. `roles/clouddeploy.jobRunner`, artifact access, and runtime deployment permissions belong to the execution account; `roles/clouddeploy.releaser` grants release/rollout permissions to the caller but not `actAs`.
- Distinguished raw API minima from CLI conveniences. Current `gcloud deploy apply` uses `PATCH` with `allowMissing=true` without a preliminary read, but it does poll the returned operation; local release source staging requires an object write; `GetOperation` and Cloud Deploy `GetIamPolicy` are disabled-by-default Data Access events.
- Added exact Cloud Deploy v1 method names, generic IAM method names, Cloud Build `CreateBuild`, Cloud Storage source/artifact activity, Cloud Run v1 create/replace methods, GKE Kubernetes audit boundaries, and conditional application signals.

### Folded or rejected headings

- `RollbackTarget` is a lower-input variant of deploying an existing release, not a new privilege boundary. It was folded into the existing-pipeline deployment surface and the persistence page remains the appropriate place for re-arm framing.
- Automation creation is persistence/operations automation, not arbitrary execution as the automation account. That account performs Cloud Deploy operations and must itself be able to act as the applicable execution account.
- `rollouts.approve` and `deployPolicies.override` bypass configured gates but do not create a release, create a rollout, choose an artifact, or supply `actAs`; they remain conditional prerequisites rather than standalone privilege escalation.
- Custom target render/deploy tasks, verification, analysis, and postdeploy tasks are alternate attacker-controlled task sinks under the same execution-environment boundary and were consolidated instead of repeated.
- Resource deletion, cancellation, job retry/ignore, and release abandonment are destructive availability actions, not privilege escalation.

## 2026-09-28 — independent cross-review

No cloud resources or APIs were touched. The rewritten page was independently checked against the current Cloud Deploy REST schema and audit catalog, Cloud Deploy service-account/IAM/task documentation, Cloud Build/Cloud Run/Storage/GKE audit documentation, IAM policy versioning, and local Google Cloud CLI 586.0.0 source/help.

- Corrected the hook YAML: each entry under `predeploy.tasks` must contain a nested `task` object.
- Corrected the shown `gcloud deploy apply` minimum and telemetry. It sends PATCH with `allowMissing=true`, so `.update` is sufficient even when the resource is absent and the audit methods are `UpdateDeliveryPipeline` / `UpdateTarget`; direct Create calls remain `.create` / `Create*`. Custom-target execution conditionally adds CustomTargetType create/update.
- Completed current CLI helper requirements: pipeline/release/rollout reads, rollout listing, operation polling, staging-bucket get/create, source-object read when copying a `gs://` source, and staged-object creation. Added the omitted `GetRollout` signal.
- Distinguished the Cloud Deploy caller's release/rollout plus `actAs` checks from the execution account's Job Runner, artifact, worker-pool, and runtime permissions. Cloud Run runtime-service-account `actAs` belongs to the deploy execution account; GKE workload identity remains bounded by Kubernetes RBAC/admission and an existing Workload Identity binding.
- Made resource IAM mutation condition-safe: the helper example now explicitly requests an unconditional binding, while raw read/modify/write requires policy version 3 plus the returned `etag` and preservation of all conditions.
- Rechecked all three retained H3s for bounded impact, categorical stealth, exact Cloud Deploy/Cloud Build method names, log class/default visibility, and conditional downstream signals. No additional standalone high-value primitive survived the no-duplication bar.
