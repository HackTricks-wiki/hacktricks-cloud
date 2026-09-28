# Certificate Authority Service future-test checklist

All tests must use disposable names, short certificate lifetimes, an isolated relying party, and immediate cleanup. CA pools and key rings have non-reusable or non-deletable lifecycle properties; prefer a disposable project scheduled for deletion rather than polluting a shared project.

## Minimum-permission matrix

- [ ] With a custom role containing only `privateca.certificates.create`, issue from a known pool by raw REST and by `gcloud privateca certificates create`; confirm no hidden read permission is necessary.
- [ ] Repeat with a named template and prove that `privateca.certificateTemplates.use` is the only added authorization check.
- [ ] Confirm that `privateca.certificates.createForSelf` cannot request an unrelated Subject/SAN through both CSR and structured-config request forms.
- [ ] Patch an issuance policy by raw REST with only `privateca.caPools.update`; then run the current CLI with/without `privateca.caPools.get` and `privateca.operations.get` to confirm helper-only extras.
- [ ] Repeat the raw/CLI split for `privateca.certificateTemplates.update`, `.get`, and `privateca.operations.get`.
- [ ] Confirm CA-pool IAM raw `setIamPolicy` authorization separately from the condition-safe CLI helper's `getIamPolicy` requirement.

## Telemetry matrix

- [ ] Capture `CreateCertificate` with CA Service Data Access disabled and with `DATA_WRITE` enabled; record exact resource and principal fields.
- [ ] Capture `UpdateCaPool`, `UpdateCertificateTemplate` and each LRO completion entry; distinguish primary method entries from CLI `GetOperation` polls.
- [ ] Capture condition-safe pool IAM binding and verify `SetIamPolicy`; determine whether the helper's pool `GetIamPolicy` emits any event despite its omission from the current CA Service audit catalog.
- [ ] In a disposable template, capture `certificateTemplates.getIamPolicy/setIamPolicy` and resolve the mismatch between the v1 endpoint and the audit catalog.
- [ ] Capture the subordinate helper sequence: IAM test calls, issuer list, create CA, fetch CSR, create subordinate certificate, activate, enable, operation polling and service-identity generation.
- [ ] In the attacker KMS project, capture `GetIamPolicy`, `SetIamPolicy`, `GetPublicKey` and `AsymmetricSign`; verify which calls are made by the attacker versus the victim CA Service service agent.

## Boundary validation

- [ ] Use an isolated mTLS server to show that certificate chain validity alone is insufficient and that privilege changes only when the application maps the forged SAN/Subject to authorization.
- [ ] Test pool policy + template intersection, including a template that attempts to permit a field forbidden by the pool.
- [ ] Test CA-certificate permitted/excluded name constraints against leaf issuance and relying-party validation.
- [ ] Test Enterprise certificate inventory/revocation and DevOps non-retention/non-revocation with short-lived leaves.
- [ ] Test a cross-project, same-location customer-managed subordinate key in an Enterprise pool; then remove victim-project grants and prove only the independently retained KMS permission remains relevant.
- [ ] Verify containment outcomes separately: CA resource disable/delete, subordinate-certificate CRL publication, a CRL-checking client, a non-checking client, and root/trust-anchor removal.

## Cleanup order for any authorized live test

- [ ] Stop the isolated relying service and remove its test trust anchor.
- [ ] Revoke the issued leaf/subordinate where supported and publish/verify the updated CRL.
- [ ] Disable and delete the disposable CA using the documented grace-period rules; delete the pool if eligible.
- [ ] Remove the victim CA Service service-agent bindings from the attacker KMS key.
- [ ] Disable and schedule destruction of disposable KMS key versions. Remember that key rings cannot be deleted.
- [ ] Delete the disposable project when project-level cleanup was chosen, and verify there are no billable CAs remaining.
