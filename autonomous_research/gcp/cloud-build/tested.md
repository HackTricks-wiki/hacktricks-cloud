# Cloud Build — tested

Cloud Build. Fully covered (build-step RCE, `connections.setIamPolicy`→SCM token, workerpools egress).

## Standing UNVERIFIED candidate — GAP A
- `cloudbuild.repositories.create` shadow-repo: hypothesis that creating a repository resource under
  an existing 2nd-gen connection could redirect/point a trigger at attacker source. Flagged repeatedly
  as **"would be garbage if it silently fails"** — never live-fired. See checklist.

## 2026-09-28 — Official-documentation privilege-escalation audit

Documentation-only review; no Cloud Build jobs, repositories, connections, worker pools, IAM policies, or other cloud resources were created or changed.

### Retained escalation chains

1. `cloudbuild.builds.create` executes attacker-controlled build steps as the effective build service account. It bypasses `iam.serviceAccounts.actAs` only when the project retained the legacy Google-owned Cloud Build default identity; current Compute Engine defaults and user-managed service accounts require `actAs`.
2. `cloudbuild.repositories.accessReadWriteToken` can poison source consumed by an existing privileged trigger. The GCP escalation is conditional on the trigger accepting attacker-controlled input and is bounded by its pinned service account.
3. `cloudbuild.connections.setIamPolicy` can self-grant `roles/cloudbuild.tokenAccessor`, after which the same conditional repository-to-trigger chain applies.

### Removed or folded from the privilege-escalation page

* Trigger creation/run was folded into `cloudbuild.builds.create`: the trigger IAM operations use that same permission and do not create a distinct privilege boundary.
* `cloudbuild.builds.approve` was removed as a standalone primitive: approval only changes the decision on an already-created pending build and does not itself let the approver author code or select a service account. It can complete a compound chain when the attacker separately controls accepted build input, but that approval-gate case already belongs in post-exploitation/approval-workflow coverage.
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
