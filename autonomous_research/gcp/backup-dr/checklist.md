# Backup and DR - open research checklist

- [x] Live-test Preview auto-protection policy creation, binding authorization and policy-update
      plan-use checks with minimum custom roles. All three boundaries enforced correctly. The
      guaranteed no-match fixture produced an applied policy but no association or backup; see
      `tested.md`.
- [ ] With two same-organization disposable projects, verify cross-project auto-protection under
      only the documented workload authorization and foreign vault-service-agent Disk/Compute
      operator grant. Capture both projects' attribution, then wait for binding removal before
      deleting the policy, plan, vault, service-agent grant and APIs.
- [ ] Private-first: after a workload administrator authorizes a deliberately narrow cross-project
      binding, remove the policy editor's workload-project access and test whether policy-only
      `update` plus the new plan's `useFor...` can broaden the label selector or redirect future
      backups without renewed `appliedAutoProtectionPolicies.authorize`. If this is the intended
      mutable-policy delegation, document the trust boundary; if workload reauthorization is
      promised but absent, keep the finding private. Restore the benign revision before teardown.
- [ ] Test the label-only enrollment boundary: after an administrator creates a no-sensitive-data
      policy, give a second identity only `compute.disks.setLabels` or
      `compute.instances.setLabels` and determine whether adding the selector causes service-managed
      enrollment without any Backup and DR permission. Use a blank workload, and remove its label,
      association, binding, policy, plan, vault and every grant after all LROs settle.
- [ ] With explicit approval for a live test, verify whether a restored Compute VM request that supplies instance metadata or a service account performs any additional caller-side authorization checks beyond the two permissions documented for CLI/API restore.
- [ ] With explicit approval and disposable clusters, capture the exact GKE/Kubernetes audit events emitted when the Backup for GKE agent reads Secret objects and when it writes them during restore.
- [ ] Revisit cross-project GKE backup/restore after the standard backup-plan guide removes its stale same-project-only sentence; the dedicated cross-project guides and release notes describe the GA channel workflow.
- [ ] Monitor new Backup and DR workload types for restore methods that expose credentials or data through a stronger service identity.
