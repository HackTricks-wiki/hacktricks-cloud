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
