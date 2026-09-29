# Cloud Run — open leads

## Custom URLs (Preview, announced 2026-09-28)
- [x] Verify create/delete/reclaim behavior, short propagation, service-deletion retention, public
      reachability, cleanup, and the documented cross-project domain-sniping boundary. Shipped as an
      unauthenticated Cloud Run technique.
- [ ] With a second disposable project, measure the release-to-cross-project-claim race and whether
      an organization policy, abuse reservation, or cooldown changes behavior for brand-like names.
      Release only a random test name and reclaim or delete it immediately; never snipe a third-party
      name.
- [ ] Capture the live `CreateDomainMapping`/`DeleteDomainMapping` Admin Activity payload after log
      indexing, including authorizationInfo, resource type, request redaction and system-event legs.
      Reconcile the current role-catalog lag: docs require `roles/run.admin` and audit docs name
      `run.domainmappings.*`, while the local predefined-role listing omits those permissions.
- [ ] Test whether custom audiences, Invoker IAM, disabled default URLs, ingress settings, IAP and
      VPC-SC behave identically on `*.cloud.run`. Keep any authentication or ingress discrepancy
      private-first and delete the mapping/service after every case.

## Documentation and audit drift
- [x] Reconcile Cloud Run get/list and `RunJob` logging against the current audit reference instead
      of treating an older missing-log capture as an immutable platform contract.
- [ ] In a future disposable job test, enable the exact `ADMIN_READ` and `DATA_WRITE` audit config,
      invoke through both v1 and v2, and determine whether current successful `RunJob` calls emit an
      attributed Data Access entry in addition to `/Jobs.RunJob`. Remove the job immediately.
- [ ] Capture the exact custom-role permission checks for attaching a pre-existing connector via a
      raw v2 service patch. Current documentation and role definitions identify
      `vpcaccess.connectors.get` plus `compute.networks.access`; do not create a connector solely for
      this check.

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
