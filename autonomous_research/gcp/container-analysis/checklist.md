# Container Analysis / Artifact Analysis — research checklist

## Minimum-role and telemetry fixture

- [ ] In a disposable already-enabled project, create one synthetic ATTESTATION note and occurrence.
      Use separate principals for `occurrences.create` and `notes.attachOccurrence` to confirm both
      v1 checks and capture the denied side of each boundary.
- [ ] Enable Artifact Analysis Data Access only for the fixture window. Capture the exact v1 method
      names and authorization info for list/get/create/update/delete, then restore the original audit
      config.
- [ ] Repeat note `GetIamPolicy`/`SetIamPolicy` with a conditional version-3 policy and confirm etag
      conflict behavior. Restore the exact policy before deleting the note.
- [ ] Re-test the currently documented occurrence `getIamPolicy`/`setIamPolicy` endpoints. Older live
      work observed a 404 despite cataloged permissions; determine whether the current v1 global or
      regional resource now supports an effective occurrence-level binding. An effective
      resource-level self-grant is expected functionality, not a zero-day.

## Attestation boundary

- [ ] With a disposable local key and attestor, store an invalid-signature occurrence, call
      `ValidateAttestationOccurrence`, and prove validation rejection without deploying a workload.
- [ ] Store a correctly signed occurrence and validate it. Split occurrence-project create,
      note-resource attach and `binaryauthorization.attestors.verifyImageAttested` across minimum
      custom roles; capture all audit methods.
- [ ] If a no-cost synthetic deployment target already exists, compare successful, denied and
      `DRYRUN_AUDIT_LOG_ONLY` evidence. Do not provision a paid GKE cluster merely for this test.
- [ ] Test the documented digest-only reuse property using identical synthetic image digests in two
      repository locations; remove every image, occurrence and registry fixture.
- [ ] In a disposable multi-project fixture, separately remove the deployer service agent's
      `roles/binaryauthorization.attestorsVerifier` attestor binding and each attestor/deployer
      service agent's `roles/containeranalysis.notes.occurrences.viewer` note binding. Capture which
      lookup fails, then restore and delete every binding and fixture.
- [ ] Under a minimum custom role containing only `binaryauthorization.policy.update`, call stable
      v1 `UpdatePolicy` with and without attestor references. Reconcile the permission reference
      (only `policy.update`) with the audit catalog's additional `attestors.get/list` authorization
      metadata; capture denied `authorizationInfo` if either extra permission is truly enforced.

## New-surface monitoring

- [ ] Review new Grafeas occurrence kinds (DSSE/SLSA, compliance, secret and SBOM references) for
      downstream consumers that trust fields without independent signature/ownership validation.
- [ ] Revisit regional occurrence/note behavior. Binary Authorization currently requires the global
      endpoint; treat any cross-region or global/regional identity mix-up as a private potential
      platform issue until verified and reported.
- [ ] Check future changes to output-only vulnerability/VEX fields and provider-note ownership. Do
      not restore vulnerability-suppression claims without a minimum-role live success against a
      disposable scanner-owned finding.

## Cleanup invariant

- [ ] Delete every synthetic occurrence, attestor and note; restore complete note IAM and Binary
      Authorization policy documents; delete local/KMS key fixtures and temporary bindings; restore
      audit configs and API enablement to their exact starting state; confirm list and Cloud Asset/IAM
      searches find no fixture residue.
