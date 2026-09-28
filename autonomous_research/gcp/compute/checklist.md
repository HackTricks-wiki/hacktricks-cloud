# GCP Compute research checklist

## Completed

- [x] Audit every Compute privilege-escalation technique for an explicit categorical stealth rating.
- [x] Validate Compute, OS Login, VM Manager, service-account attachment, storage, Windows, and MIG
  claims against current official Google Cloud documentation.
- [x] Remove the non-technique access-scope placeholder and retain its useful defensive context.
- [x] Correct the project-metadata command and the existing-MIG template reconstruction command.
- [x] Document configuration-dependent permissions instead of presenting optional VM permissions as
  unconditional minima.
- [x] Correct OS Login and OS Config audit categories and default-log availability.
- [x] Correct machine-image, snapshot, and disk IAM semantics and required follow-on operations.
- [x] Record this pass without touching GCP resources.
- [x] Audit Compute enum, privilege-escalation, post-exploitation and persistence coverage as one
  caller/service-agent/guest identity model.
- [x] Add explicit minimum permissions/prerequisites to all 15 retained Compute privesc H3s.
- [x] Rebuild Compute persistence around four recurring/self-healing mechanisms and remove the
  duplicate plain-VM run-as-SA claim.
- [x] Apply the no-garbage bar to Compute post-exploitation by removing three destructive-only or
  availability-only headings while preserving their negative results in `tested.md`.
- [x] Correct enum disk location, image-type/export duplication and Data Access visibility.
- [x] Preserve condition/version/etag state in the instance-IAM self-grant example.
- [x] Apply reciprocal review corrections for project-versus-instance metadata `actAs`, unclassified
  OS Login monitoring signals, regional-disk IAM REST, helper reads, and complete command examples.
- [x] Rebuild the dedicated custom-SSH-metadata page into one instance and one project primitive,
  with exact CLI helper reads/operation waits, prerequisites, bounded impact, categorical stealth,
  and current audit defaults; no cloud mutation was performed.
- [x] Independently reciprocal-review the dedicated SSH-metadata page against current REST IAM
  requirements and Google Cloud CLI 586.0.0 source; no further page fix was required.

## Follow-up validation ideas

- [ ] Re-test current OS Login data-plane `CheckPolicy`, `StartSession`, and `ContinueSession` record
  availability under default and explicitly enabled Data Access configurations.
- [ ] Capture the separate IAM `iam.serviceAccounts.actAs` audit record for direct VM creation,
  `setServiceAccount`, and a MIG-created VM; verify the principal attributed on each path.
- [ ] Test a least-privilege new-MIG matrix to separate caller permissions from Google APIs Service
  Agent permissions for SA, image, disk, network, and subnet references.
- [ ] Test a least-privilege existing-MIG template swap for both zonal and regional MIGs and record
  exact `setInstanceTemplate`, patch, and apply-update methods.
- [ ] Test resource-level grants on machine images, snapshots, and disks with a principal that has
  only the minimum target-project creation permissions; document role grantability and failures.
- [ ] Test Windows password generation with `disable-account-manager=true` and record the guest and
  control-plane failure signals.
- [ ] Verify OS Config agent log destinations on current Google-provided images with and without Ops
  Agent installed.
- [ ] Capture one recurring patch deployment run with VM Manager Data Access enabled and determine
  whether the service-triggered execution emits `ExecutePatchJob`, another service-principal audit
  record, or only patch-job/agent state.
- [ ] Validate whether `gcloud compute project-info add-metadata` and instance `add-metadata` perform
  any additional authorization beyond the locally confirmed resource-get and operation-wait helper
  calls under minimum custom roles, separating raw REST minima from CLI minima.
- [ ] Validate image-family resolution and exact `images.insert` request/audit fields with a stopped
  disposable source disk; delete the image and disk immediately after the test.
- [ ] Capture zonal and regional MIG template changes to confirm the exact regional method-name
  variants and service-agent attribution for scale-out versus explicit recreation.

All future live tests must use minimum permissions, stay within the cost limit, record cleanup, and
delete every created asset immediately after the test.
