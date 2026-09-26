# Cloud Run — open leads

## Cloud Run instances (Preview, announced 2026-08-25)
- [ ] Check whether `run.instances.update` accepts changes to an existing privileged instance's container image, command, or environment without `iam.serviceAccounts.actAs` on its unchanged service identity. The [instance identity guide](https://docs.cloud.google.com/run/docs/configuring/instances/service-identity) says create/update needs `actAs`; verify the actual enforcement with a minimum-permission caller before claiming a distinct privilege escalation.
- [ ] Check whether `run.instances.start` after a stopped-instance configuration change creates a separate authorization boundary, and record actual Admin Activity/System Event and container logs. Delete every instance immediately after testing; [the preview resource](https://docs.cloud.google.com/run/docs/instances/create-and-manage-instances) bills for dedicated compute and is unavailable in `us-central1`.

The ordinary `run.instances.create` + `iam.serviceAccounts.actAs` path is the same service-account execution family as Cloud Run services/jobs, so it is not a separate book technique without a distinct boundary. The current wiki already mentions `run.instances.sshRead`/`sshRoot` as a direct path into an existing instance. API permission reference: https://docs.cloud.google.com/run/docs/reference/iam/permissions.
