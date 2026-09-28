# Workload Identity Federation research checklist

## Completed

- [x] Inventory workload, workforce, OAuth-client, and managed-identity resource families.
- [x] Reconcile workload provider create/update/undelete and pool update/undelete contracts.
- [x] Reconcile SAML certificate overlap and OIDC uploaded-JWKS replacement behavior.
- [x] Bound workload/federated direct access versus service-account impersonation.
- [x] Bound workforce provider takeover, including the local-JWKS Console limitation.
- [x] Reconcile workforce pool/provider enablement and soft-delete restoration with residual access.
- [x] Check current pool-admin, workforce-editor, OAuth-client-admin, SCIM-syncer, and Editor roles.
- [x] Remove the false general-purpose SCIM group-injection escalation.
- [x] Correct managed identity from STS/OAuth language to X.509/SPIFFE semantics.
- [x] Consolidate disabled/deleted resource restoration into one residual-trust technique.
- [x] Remove duplicate managed-identity persistence coverage.
- [x] Correct exact audit method namespaces, LRO status, permission class, and default visibility.
- [x] Remove the unsupported OAuth-client-only refresh-token persistence claim; document the IAP-only
      redirect and configuration boundary.
- [x] Confirm no cloud mutation was performed in this audit.

## Safe future validation

- [ ] Capture a complete current workload OIDC static-JWKS takeover in a disposable project and
  verify the provider diff plus STS log fields. Account for the unavoidable 30-day deleted-resource
  tombstone before deciding whether the lab cleanup policy permits the test.
- [ ] Validate a workforce uploaded-JWKS programmatic exchange and confirm that the same provider
  cannot complete federated Console sign-in, using an authorized external IdP fixture.
- [ ] Validate managed workload identity certificate issuance from a matching Compute Engine
  attached-service-account UID rule and a controlled mTLS relying workload. Delete all VM and CA
  resources immediately; do not launch without an explicit cheap/no-residue plan.
- [ ] Capture `AddAttestationRule`, `SetAttestationRules`, and their LRO polling entries to confirm
  request/response placement in the current audit-log implementation.
- [ ] Test the distinct combined hypothesis requiring both OAuth-client administration and control
  of an IAP application's workforce settings/code-delivery path; do not restore an OAuth persistence
  heading unless an attacker-observable authorization code or refresh token is demonstrated.
- [ ] Verify whether the current helper commands ever add permissions beyond the raw REST permission
  when project/resource identifiers are fully supplied; retain raw REST as the minimum baseline.
