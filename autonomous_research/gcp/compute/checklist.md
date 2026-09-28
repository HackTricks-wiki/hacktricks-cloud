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

All future live tests must use minimum permissions, stay within the cost limit, record cleanup, and
delete every created asset immediately after the test.
