# Cloud Build — tested

Current retained boundaries are build-step execution, repository-source poisoning, connection-IAM
self-grant into source poisoning, and stored-output recovery. Network-positioning and egress through
private pools remain useful behavior but are not independently a Cloud IAM privilege escalation.

## Closed legacy candidate — repository shadowing

`cloudbuild.repositories.create` under an existing second-generation connection does not retarget a
trigger, which binds a specific repository resource. Without separate trigger/build execution or
writable source that the trigger accepts, repository creation executes nothing. The idea is closed
under the no-garbage rule; see the checklist.

## 2026-09-28 — Official-documentation privilege-escalation audit

Documentation-only review; no Cloud Build jobs, repositories, connections, worker pools, IAM policies, or other cloud resources were created or changed.

### Retained escalation chains

1. `cloudbuild.builds.create` executes attacker-controlled build steps as the effective build service account. It bypasses `iam.serviceAccounts.actAs` only when the project retained the legacy Google-owned Cloud Build default identity; current Compute Engine defaults and user-managed service accounts require `actAs`.
2. `cloudbuild.repositories.accessReadWriteToken` can poison source consumed by an existing privileged trigger. The GCP escalation is conditional on the trigger accepting attacker-controlled input and is bounded by its pinned service account.
3. `cloudbuild.connections.setIamPolicy` can self-grant `roles/cloudbuild.tokenAccessor`, after which the same conditional repository-to-trigger chain applies.

### Removed or folded from the privilege-escalation page

* Trigger creation/run was folded into `cloudbuild.builds.create`: the trigger IAM operations use that same permission and do not create a distinct privilege boundary.
* `cloudbuild.builds.approve` was removed as a standalone primitive: approval only changes the decision on an already-created pending build and does not itself let the approver author code or select a service account. It can complete a compound chain when the attacker separately controls accepted build input, so that boundary is folded into the retained source-poisoning/build-execution chain.
* `cloudbuild.builds.get` / `cloudbuild.builds.list` was removed: build-history and log discovery is post-exploitation, not escalation.
* `cloudbuild.repositories.accessReadToken` was removed: source disclosure is post-exploitation unless another independent exploit converts it into privileges.
* `cloudbuild.connections.fetchLinkableRepositories` was removed: it is reconnaissance.
* `cloudbuild.connections.get` plus Secret Manager access was removed: credential theft is post-exploitation, and the Secret Manager permission is the controlling privilege.
* Worker-pool creation/use/update was removed: network positioning, egress, and denial of service are valuable offensive actions but not an inherent Cloud IAM escalation.

### Material corrections

* Distinguished the Cloud Build service agent from runtime build identities.
* Removed the stale assumption that the legacy Cloud Build service account is the default or that the Compute Engine default service account necessarily has Editor.
* Corrected `accessReadWriteToken` to its sole RPC permission and removed universal provider/scope/one-hour-expiry claims; the documented expiry can be absent.
* Replaced payload-level audit assertions not guaranteed by the audit-log reference with exact method, audit class, and default-visibility statements.
* Recorded that `logging: NONE` does not remove Admin Activity or the Cloud Build history record.
* Cross-review added the off-default `GetBuild` calls made by synchronous CLI polling, the always-on trigger update/delete methods, and the off-default `GetIamPolicy` read performed by the additive connection IAM helper.
* Tightened the repository-poisoning prerequisite: an accepted writable ref is insufficient when a manual approval or trusted `/gcbrun` comment gate remains unsatisfied.

## 2026-09-28 — post-exploitation taxonomy and current-contract audit

Documentation, local CLI help, prior authorized-test records, and public audit/API contracts only.
No build, trigger, service account, role, logging setting, bucket, or other cloud state was changed.

- Retained one post-exploitation primitive: reading build output that was actually retained in Cloud
  Logging or Cloud Storage. Split the exact authorization boundaries for project/container Logging
  queries, named log views, user-owned Storage buckets, and Google's default log bucket. A successful
  build can have no stored output, and secret references or KMS ciphertext are not plaintext secrets.
- Removed trigger mutation/approval-gate removal from post-exploitation because attacker-controlled
  build execution as the pinned service account is already covered by the Cloud Build privilege-
  escalation page. Removed build cancellation because it is availability-only.
- Removed `ApproveBuild` as a standalone H3. The current REST method, predefined Approver role,
  approval guide, and earlier contained test establish `cloudbuild.builds.approve` as the caller
  boundary. The audit catalog additionally lists `.create` for the method, but the predefined role
  omits it and it is not a documented caller prerequisite. Approval still cannot author or change a
  build: it matters only when an already-pending build is attacker-useful or the caller separately
  controls accepted input, so it is folded into the existing source-poisoning/build-execution chain
  rather than presented independently.
- Corrected telemetry: `ApproveBuild` is an Admin Activity LRO under the current catalog; Cloud
  Logging `ListLogEntries` and Storage object get/list are off-by-default Data Access. Cloud Build
  `GetBuild`/`ListBuilds` are optional discovery reads, not prerequisites when the destination and
  object/log query are known.
- Corrected the Google-owned default-bucket path: `gcloud builds log` first performs the off-default
  `GetBuild`, then reads an object from Google's bucket project. The customer cannot enable or query
  the bucket project's Storage Data Access log.

Official sources:

- https://docs.cloud.google.com/build/docs/api/reference/rest/v1/projects.locations.builds/approve
- https://docs.cloud.google.com/build/docs/securing-builds/audit-logs
- https://docs.cloud.google.com/build/docs/securing-builds/store-manage-build-logs
- https://docs.cloud.google.com/logging/docs/access-control
- https://docs.cloud.google.com/logging/docs/audit-logging
- https://docs.cloud.google.com/storage/docs/audit-logging
