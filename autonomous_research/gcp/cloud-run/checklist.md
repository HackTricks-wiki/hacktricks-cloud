# Cloud Run — open leads

## Image export
- [x] Test whether `run.locations.exportImage` is custom-role grantable and whether it exports a private revision image without source Artifact Registry access. Confirmed: the permission alone is sufficient when the source project's Cloud Run service agent can write to the destination package path; caller registry access is unnecessary. See `tested.md` and the Cloud Run post-exploitation page.
- [ ] If a second disposable project becomes available, repeat with a physically cross-project destination and confirm whether organisation policies or VPC Service Controls add any boundary beyond destination-repository IAM.

## Worker Pools
- [x] Verify whether `run.workerpools.update` can alter code/config on an existing pool without `iam.serviceAccounts.actAs` on the unchanged identity. It cannot: a container-only patch was denied on the pinned default service account. Captured the dedicated audit resource type and `allowMissing` CLI-create behavior; see `tested.md`.

## Cloud Run instances (Preview, announced 2026-08-25)
- [x] Check whether `run.instances.update` accepts changes to an existing privileged instance's container image, command, or environment without `iam.serviceAccounts.actAs` on its unchanged service identity. It does not: a caller with only `run.instances.update` received `403` with an explicit `actAs` denial for a benign environment-variable patch. See `tested.md`.
- [ ] Check whether `run.instances.start` after a stopped-instance configuration change creates a separate authorization boundary, and record actual Admin Activity/System Event and container logs. Delete every instance immediately after testing; [the preview resource](https://docs.cloud.google.com/run/docs/instances/create-and-manage-instances) bills for dedicated compute and is unavailable in `us-central1`.

The ordinary `run.instances.create` + `iam.serviceAccounts.actAs` path is the same service-account execution family as Cloud Run services/jobs, so it is not a separate book technique without a distinct boundary. The current wiki already mentions `run.instances.sshRead`/`sshRoot` as a direct path into an existing instance. API permission reference: https://docs.cloud.google.com/run/docs/reference/iam/permissions.

## System-managed Agent Identity (Preview, announced 2026-09-01)
- [x] Test whether a caller holding only `run.services.update` (no service-account `actAs`) can change code or environment on an existing Cloud Run agent using `--identity-type=agent-identity`. The v2 update was denied because the caller lacked `actAs` on the underlying Compute Engine default service account; see `tested.md`. This does not yield a one-permission run-as-agent-identity technique.
- [x] If creation/registration is unavailable in the lab, record the exact blocking control. Creation worked after disabling the preview workload certificate; the first attempt failed at certificate mount and was cleaned up.

## Delayed jobs (Preview, announced 2026-09-08)
- [x] Reviewed the [delayed-execution feature](https://docs.cloud.google.com/run/docs/delayed-jobs): `--delay-execution` defers provisioning for up to 12 hours, but uses the existing job execution and override permissions and creates an ordinary execution resource. It does not establish a distinct escalation or durable persistence primitive beyond the documented `run.jobs.run` family. No delayed job was launched, so no long-lived execution or cleanup obligation was created.
