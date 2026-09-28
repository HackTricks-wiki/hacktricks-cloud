# Cloud Scheduler — tested

## 2026-09-26 — post-exploitation permissions and logging review
- Corrected `GetJob` and `ListJobs` from Data Access `DATA_READ` to the current documented
  `ADMIN_READ` classification. They remain disabled by default. Full stored-request harvesting
  requires `cloudscheduler.jobs.fullView` together with get or list. Applied the same correction to
  the duplicate privilege-escalation section, which had incorrectly claimed that get/list alone
  returned stored secrets.
- Added minimum permissions and categorical stealth ratings to all four post-exploitation
  techniques. `RunJob`, pause and delete each require only their verb-specific permission when the
  job name is known; no get/list permission is inherent in those REST methods.
- Corrected the disruption log table so it no longer includes unrelated `UpdateJob`, and corrected
  the update technique's downstream logging: the target operation can be Admin Activity, Data
  Access or a platform log depending on the method, not unconditionally Data Access/off by default.
- Clarified the update boundary. A narrow URI/body/header patch preserves the existing
  authentication configuration. Supplying or replacing an OAuth/OIDC service account explicitly
  requires `iam.serviceAccounts.actAs`; for OIDC, a redirected endpoint must also accept the stored
  audience.

## 2026-09-26 — narrow authenticated-job update boundary attempt
- The lab Scheduler API was already enabled and contained no jobs. Created a paused annual HTTP job
  with an OIDC victim identity and attempted a raw `PATCH` limited to `http_target.uri` from a caller
  with no `iam.serviceAccounts.actAs`.
- Two fresh custom-role attempts and one predefined `roles/cloudscheduler.admin` attempt did not
  reach the service-account boundary: throughout the bounded propagation windows, Scheduler denied
  the caller on `cloudscheduler.jobs.update` itself. This is inconclusive about whether an unchanged
  token configuration causes `actAs` to be reevaluated.
- Deleted all three paused jobs, six temporary service accounts, project bindings, service-account
  keys and isolated gcloud configurations. Verified no matching job, account, binding, key file or
  configuration remains. The two deleted custom roles remain only as normal soft-deleted IAM
  tombstones (`htSchedulerUpdateBoundary` and `htSchedulerUpdateBoundary2`).

## 2026-09-28 — privilege-escalation page independent documentation audit

- Rebuilt the page around four distinct delivery-time boundaries: authenticated HTTP dispatch as
  an attached service account, forced execution of an existing privileged job, actAs-free App
  Engine handler invocation, and actAs-free same-project Pub/Sub publish via the Scheduler service
  agent.
- Bounded the HTTP primitive. OAuth is an in-band request credential and Scheduler does not return
  it or the downstream body to the caller. A captured OIDC token is audience-bound and is useful
  only where a relying party accepts that issuer/audience and authorizes the selected service
  account. Neither path is unrestricted service-account impersonation.
- Confirmed from the v1 REST and audit contracts that `CreateJob`, `UpdateJob`, and `RunJob` are
  non-LRO methods. Their permissions are respectively `cloudscheduler.jobs.create`, `.update`, and
  `.run`; the authentication attachment adds `iam.serviceAccounts.actAs`, while a known-name
  `RunJob` does not require get/list or actAs.
- Confirmed from installed gcloud command YAML/help that Scheduler update commands issue a direct
  v1 `jobs.patch` with a field mask. Supplying an explicit `--location` avoids location inference;
  `cloudscheduler.locations.list` is not part of the raw minimum for the documented commands.
- Corrected a material telemetry error: Pub/Sub currently produces **no Cloud Audit Log** for
  `google.pubsub.v1.Publisher.Publish`. This is not a disabled-by-default `DATA_WRITE` event.
  Scheduler `CreateJob`/`UpdateJob` and `AttemptStarted`/`AttemptFinished` still expose the control
  plane and each delivery attempt.
- Removed `jobs.get/list + fullView` from privilege escalation because it is read-only secret
  discovery already covered by the post-exploitation page. Removed the malformed generic service
  account key-upload recipe, speculative URL-acceptance-as-SSRF claim, destructive-only pause/delete
  material, generic role inventory, and the third-party historical reference.
- No cloud API was called and no resource or IAM state was created or changed during this review.

## 2026-09-28 — independent cross-review

- Re-opened the current official Scheduler access-control, job resource, create/patch/run,
  authenticated-HTTP, App Engine target, Scheduler audit, Pub/Sub audit and App Engine logging
  contracts. The four retained delivery boundaries and their minimum permissions stand.
- Reconfirmed that the service agent, rather than the caller, publishes to same-project Pub/Sub and
  mints an attached HTTP job's tokens; the caller needs `actAs` only for the selected same-project
  client service account. The official access-control page explicitly warns that `jobs.create` can
  target any same-project topic.
- Reconfirmed that App Engine targets can invoke same-project handlers protected by `login: admin`,
  require the app's region, and need the firewall to accept `0.1.0.2/32`. This is a handler-specific
  invocation path, not general App Engine IAM.
- Reconfirmed that a known-name `RunJob` requires only `cloudscheduler.jobs.run`, does not reattach
  the stored identity, and is a non-LRO Admin Activity method. Automatic execution/platform logs and
  the downstream operation remain separate from that caller-attributed control-plane record.
- Rechecked all command examples and the exact Scheduler/Pub/Sub logging boundaries. No additional
  correction, cloud call or mutation was required.
