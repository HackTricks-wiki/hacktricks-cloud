# Eventarc research ledger

Last reviewed: 2026-09-28

## Scope and method

- Re-audited the Eventarc Standard trigger and Eventarc Advanced bus/enrollment/pipeline surfaces against the current official REST resources, IAM role catalog, audit catalogs, gcloud 586.0.0 help/source behavior, and existing historical lab notes.
- Queried current predefined role definitions read-only for `roles/eventarc.developer`, `roles/eventarc.admin`, the three focused publisher roles, `roles/eventarc.eventReceiver`, `roles/eventarc.serviceAgent`, and `roles/editor`.
- Confirmed read-only that `eventarc.googleapis.com` and `eventarcpublishing.googleapis.com` are disabled in `gcp-labs-eqd4ny8d`. They were not enabled: this audit created no service agent, resource, IAM binding, billable workload, or cleanup debt.

## Retained expected techniques

1. **Standard trigger payload copy.** `eventarc.triggers.create` plus permission to attach the effective trigger identity and a readable destination can route future matching CloudEvents to an attacker sink. Provider/destination runtime prerequisites remain mandatory.
2. **Standard destination hijack.** `eventarc.triggers.update` can redirect a live trigger. The method is `DATA_WRITE` Data Access and therefore absent by default, although resource state and downstream delivery remain visible.
3. **Advanced OAuth-token delivery.** A pipeline can attach an OAuth access token, default `cloud-platform` scope, for a selected service account to a reachable HTTPS request. This requires `pipelines.create`, `actAs`, a live bus/enrollment route, an event, and functional Eventarc token creation. Pipeline/enrollment creation are always-on Admin Activity.
4. **Event injection.** Message-bus publish is `Publisher.Publish`, disabled-by-default Data Access. The current Eventarc Publishing audit catalog explicitly says `PublishEvents` and `PublishChannelConnectionEvents` produce no Cloud Audit Log.
5. **Advanced enrollment hijack.** `eventarc.enrollments.update` can replace the destination pipeline and broaden `celMatch`; it is always-on Admin Activity.
6. **Durable credential persistence.** An enrolled token-delivery pipeline can continue exporting fresh short-lived OAuth credentials after the creator loses interactive access, until the identity, service-agent authority, enrollment/pipeline, route, or destination is disabled.

## Corrections and rejected standalone ideas

- Removed the claim that `--service-account` is mandatory on Standard triggers. Current official target-role documentation states that omission selects the default Compute Engine service account. The creator still needs permission to attach the effective identity; omission is not an identity-free or no-`actAs` path.
- Removed Standard-trigger OIDC capture as a standalone privilege escalation. A token captured at an attacker sink is audience-bound to that destination and does not grant general Google API access. Retain it only as delivery-auth context; a real escalation would require a separate audience-validation flaw.
- Folded the separate audit-log watcher into trigger payload interception. It is the same primitive with a useful source type, and it only sees audit entries actually emitted.
- Removed unsupported wording that every publish method merely "should" be `DATA_WRITE`; the new service-specific publishing audit catalog gives exact behavior for all three methods.
- Did not publish Google-channel CMEK clearing/repointing as a standalone attack. It is primarily an availability/configuration mutation and does not expose plaintext or attacker-held key material by itself.
- Did not claim that `eventarc.pipelines.update` can redirect an existing token-authenticated pipeline without a fresh `actAs` check. The current update schema permits destination replacement, but the identity revalidation boundary needs a controlled live test before publication.
- Removed Standard trigger creation and route hijacking as standalone persistence. The trigger service account authenticates the delivery request; it does not become the Cloud Run, GKE, or Workflow runtime identity. Trigger/enrollment redirection remains useful post-exploitation.
- Kept the OAuth-token pipeline in privilege escalation and persistence, but removed its duplicate H3 from post-exploitation because obtaining a portable service-account credential is a direct escalation primitive.
- Corrected CLI-helper boundaries: current gcloud 586.0.0 reads a trigger/enrollment before an update, so those commands need `.get` even with `--async`; a direct PATCH only needs `.update`.
- Added the downstream `iamcredentials.googleapis.com` `GenerateAccessToken` Data Access signal. It is off by default and is enabled through IAM Data Access logging. Eventarc Advanced platform telemetry is separately controlled by `loggingConfig`, whose resource-creation default is `NONE`.
- Tightened Advanced topology: enrollment, pipeline, and bus must be in the same region; enrollment and pipeline must also be in the same project, while the bus can be cross-project.
- Clarified service-agent authorization: authenticated pipeline delivery needs the pipeline project's Eventarc service agent to have `iam.serviceAccounts.getAccessToken` on the selected account. The normal service-agent grant covers same-project accounts; cross-project identities need equivalent access on the service account.

## Telemetry ground truth

| Primitive | Exact Eventarc method | Current class/default |
| --- | --- | --- |
| Create/update Standard trigger | `Eventarc.CreateTrigger` / `Eventarc.UpdateTrigger` | Data Access `DATA_WRITE`; off by default |
| Create Advanced pipeline/enrollment | `Eventarc.CreatePipeline` / `Eventarc.CreateEnrollment` | Admin Activity `ADMIN_WRITE`; on |
| Update enrollment | `Eventarc.UpdateEnrollment` | Admin Activity `ADMIN_WRITE`; on |
| Poll Eventarc LRO | `google.longrunning.Operations.GetOperation` | Data Access `DATA_READ`; off by default |
| Publish to message bus | `google.cloud.eventarc.publishing.v1.Publisher.Publish` | Data Access `DATA_WRITE`; off by default |
| Publish to channel / channel connection | `Publisher.PublishEvents` / `Publisher.PublishChannelConnectionEvents` | Explicit no-log methods |
| Mint a pipeline OAuth token | `GenerateAccessToken` on `iamcredentials.googleapis.com` | Data Access `ADMIN_READ`; off by default and controlled through IAM Data Access logging |
| Process an Advanced event | Resource platform telemetry controlled by `loggingConfig` | Default `NONE` means no platform logs |

Long-running methods can produce start and completion audit entries. Deliveries and attacker code also create destination, network, application, and target-service telemetry independent of the Eventarc control-plane method.
