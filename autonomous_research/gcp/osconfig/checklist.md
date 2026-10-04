# OS Config research checklist

## Completed

- [x] Compare current GA/Beta CLI surfaces with v1, v1beta, and v2 REST resources.
- [x] Verify narrow predefined roles and create-versus-update splits.
- [x] Separate control-plane caller identity, OS Config managed identities, attached VM service account, and in-guest OS identity.
- [x] Bound patch script injection by Cloud Storage generation, VM-SA object read, and OAuth scope.
- [x] Bound one-shot patch jobs to same-project active targets and the documented 500-VM limit.
- [x] Bound GA OS policy assignments to one zone and legacy guest policies to one project.
- [x] Verify `exec` and legacy recipe inline-script semantics and exit codes.
- [x] Verify policy-orchestrator numeric selector syntax, six-hour reconciliation, quota-project requirement, and service-agent prerequisites.
- [x] Verify exact audit methods, Data Access defaults, LRO status, and explicitly unaudited agent methods.
- [x] Correct guest/platform logging claims and preserve downstream service telemetry.
- [x] Review enum and absence of separate post-exploitation/persistence pages.
- [x] Perform no cloud mutation.

## Safe future validation

- [ ] On one disposable Linux VM with a custom-role caller containing only `osconfig.patchJobs.exec`, compare a private GCS step denied to the VM SA, a private step granted `storage.objects.get`, and a deliberately public test object. Capture access-scope effects and exact Storage/OS Config/agent logs.
- [ ] Repeat the patch-step test on one disposable Windows VM to confirm the observed service token is LocalSystem on the current image family.
- [ ] With a custom role containing only `osconfig.osPolicyAssignments.create`, submit an inline `exec` assignment using `--async`; verify whether any undocumented prerequisite permission is checked and capture both LRO audit entries with Data Access enabled.
- [ ] Grant only OSPolicyAssignment Editor on a disposable existing assignment and verify a known-name full update succeeds without create permission, preserving/restoring the original revision afterward.
- [ ] Repeat the legacy guest-policy create/update split with a uniquely named harmless recipe and record exact rerun behavior after version/name changes.
- [ ] In a disposable hierarchy already configured for orchestrators, test PolicyOrchestrator Admin plus `serviceusage.services.use` without child-project roles. Record managed-identity principals on child create/update logs and exact Cloud Logging names.
- [ ] Determine whether `osconfig.patchDeployments.execute` has any supported private/internal caller path before ever promoting it to a technique; do not infer usability from predefined-role membership.
- [ ] Test custom agent service identities to document how Linux `User=` or Windows service-account changes alter the impact ceiling.
- [ ] Re-check policy-orchestrator Beta roles, methods, and prerequisite service agents after GA changes.

## Cleanup requirements for any future live test

- Delete test patch deployments, patch jobs where deletion is supported, GA assignments, legacy guest policies, policy orchestrators, generated assignments, and test source objects/buckets.
- Restore any updated assignment/policy content and wait for cleanup rollouts to finish.
- Remove all temporary IAM grants from callers, VM service accounts, quota projects, buckets, and hierarchy service agents.
- Remove labels/metadata used for targeting or debug logging and restore prior VM Manager feature settings.
- Delete disposable VMs/disks and revoke or remove any temporary workload credentials or external sinks.
- Restore Data Access audit settings and APIs only if the test changed them, after preserving authorized evidence.
