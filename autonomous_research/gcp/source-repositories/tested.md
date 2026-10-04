# Cloud Source Repositories privilege-escalation audit

## 2026-09-28 - official-documentation and local CLI review

No repository, trigger, IAM policy, service, or other cloud resource was created or changed. The review used current official Cloud Source Repositories, IAM, Cloud Build, and Cloud Audit Logs documentation plus local `gcloud` help and predefined-role metadata.

### Retained techniques

1. `source.repos.update` can poison source consumed by an existing Cloud Build trigger and thereby execute as the service account already pinned to that trigger. This is conditional on matching event/ref/file filters, controllable content, no unmet approval, and a build identity with access beyond the caller. A repository-event push does not require the writer to hold `cloudbuild.builds.create` or `iam.serviceAccounts.actAs`.
2. `source.repos.setIamPolicy` can self-grant `roles/source.writer` on one repository and reach the first chain. `source.repos.getIamPolicy` is required for the safe etag-preserving workflow, not for the raw blind replacement authorization.

### Material corrections

- Cloud Source Repositories is unavailable to new customers under the June 17, 2024 end-of-sale rule; official material does not say all existing eligible use has been shut down.
- `source.repos.update` is the Git push permission and cannot be added to custom roles. The current predefined-role index also includes basic Editor and `roles/source.editor`, so the old role list was incomplete.
- `source.repos.setIamPolicy` is not limited to Owner and Source Repository Administrator. The current predefined-role index also includes Security Admin and other broad roles. The Security Admin boundary makes self-granting repository write access a meaningful least-privilege chain.
- A triggered build uses the service account configured on the trigger. A `serviceAccount` field in a repository build configuration is ignored for triggered builds, so a source writer cannot select a different identity through that field.
- An automatic repository event must not be labeled as the manual `google.devtools.cloudbuild.v1.CloudBuild.RunBuildTrigger` API. The resulting build record and configured build logs are downstream signals; no caller-attributed automatic-invocation audit method was claimed without direct evidence.
- Git clone/fetch uses `GitProtocol.UploadPack` / `LsRemote` (`DATA_READ`) and push uses `GitProtocol.ReceivePack` (`DATA_WRITE`). These are non-LRO Data Access events and are off by default. `SourceRepo.SetIamPolicy` is a non-LRO, always-on Admin Activity method.
- The former notification claim conflated source writes and repository configuration. The RPC and access-control contract uses `source.repos.updateRepoConfig` for `UpdateRepo`; notification setup additionally needs `iam.serviceAccounts.actAs`, a same-project publishing service account, and that service account's `pubsub.topics.publish` access to the topic.

### Rejected or relocated claims

- `source.repos.get` and cloning can expose source or hardcoded credentials, but that is post-exploitation/data access, not a direct authorization increase.
- Per-repository and project-wide Pub/Sub notification changes are monitoring/exfiltration or persistence surfaces, not privilege escalation. Naming a publishing service account does not let the caller execute arbitrary actions as it.
- `source.repos.updateProjectConfig` can change push-block and project notification configuration; this is defense evasion/configuration tampering, not a privilege gain.
- SSH keys and manually generated Git credentials configure authentication for the same user's existing repository permissions. They do not create new cloud authority.
- Secret Manager access belongs to the Secret Manager pages. Repository create/delete and public sharing claims were removed: create/delete are resource administration/availability, and the service rejects `allUsers` and `allAuthenticatedUsers` policies.

### Read-only role and CLI findings

- `roles/source.writer` is GA and currently contains `source.repos.get`, `.list`, and `.update`.
- `roles/source.admin` is GA and contains repository IAM, Git read/write, repository configuration, and project configuration permissions.
- Local `gcloud source repos update --help` states that notification configuration requires `iam.serviceAccounts.actAs`, defaults to the Compute Engine default service account if none is supplied, and accepts a topic project; official documentation bounds the publishing service account to the repository project and separately requires topic publish access.

### Telemetry result

The retained H3s distinguish the off-default Git data plane from always-on repository IAM writes. They also separate a manual Cloud Build trigger-run LRO from the build record and configuration-dependent logs produced when a repository event is processed internally.

## 2026-09-28 - independent cross-review

- Re-opened the current official access-control, release-note, trigger-identity, trigger-management, Source Repositories audit and Cloud Build audit contracts. The two retained chains and their permission, identity, end-of-sale and telemetry boundaries stand.
- Corrected the IAM helper to merge only an existing **unconditional** `roles/source.writer` binding. Conditional writer bindings are now preserved unchanged; treating one as an unconditional grant could otherwise leave the attacker subject to a condition or modify unrelated access.
- Reconfirmed that Git `ReceivePack` is off-default `DATA_WRITE`, fetch/list negotiation uses `UploadPack`/`LsRemote` as off-default `DATA_READ`, and `SourceRepo.SetIamPolicy` is always-on Admin Activity. None of these methods is an LRO.
- No cloud API was called and no repository, trigger, IAM policy, identity or local credential was created during the independent review.

## 2026-09-28 - post-exploitation taxonomy decision

- Promoted authorized cloning to a dedicated post-exploitation page rather than leaving it only as an enumeration command. The useful outcome is bulk disclosure of private source and all reachable Git history, which can include deleted hardcoded credentials, IaC, deployment logic and internal service details. That is a distinct high-value data-access primitive even though it is not a direct IAM privilege escalation.
- Kept exactly one bounded technique. A known repository needs `source.repos.get`; discovering names adds project-level `source.repos.list`, and list access alone cannot clone repository contents.
- Bounded downstream impact: a recovered credential yields only its own still-valid permissions. Source access by itself grants no additional Google Cloud role, and the page does not claim every repository contains secrets.
- Reconciled the stable gcloud helper with local source: `gcloud source repos clone` calls `GetRepo` to obtain the URL before invoking Git. A direct authenticated Git URL can omit `GetRepo`, but clone still requires `source.repos.get` and produces Git protocol reads.
- Recorded exact telemetry: optional `SourceRepo.ListRepos` and helper `SourceRepo.GetRepo` are `ADMIN_READ`; `GitProtocol.LsRemote` and `GitProtocol.UploadPack` are `DATA_READ`. All are non-LRO Data Access events disabled by default. No live repository or cloud API was used.
