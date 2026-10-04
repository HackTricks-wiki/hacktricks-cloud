# Certificate Authority Service research ledger

## 2026-09-28 — documentation and local-source audit

### Scope and evidence

- Reviewed the CA Service privilege-escalation, enumeration and persistence pages; there is no dedicated CA Service post-exploitation page.
- Checked the current official CA Service access-control table, v1 REST surface, policy-control, issuance-policy, template, tier, subordinate-CA, signing-key and audit-logging documentation.
- Checked the current Cloud KMS and Service Usage audit catalogs.
- Inspected installed `gcloud` help and the installed `gcloud privateca` implementation for certificate issuance, pool/template updates, subordinate creation, IAM preflights and operation polling.
- No cloud resource was created, modified or deleted. Findings below are documentation/source-validated, not a live minimum-role or telemetry capture.

### Retained high-value techniques

1. **Chosen-identity certificate issuance** with `privateca.certificates.create`.
   - This is a real boundary crossing only when the effective pool/template/name constraints allow the requested identity and a reachable relying party grants that identity more privilege.
   - Raw API minimum is `privateca.certificates.create`; add `privateca.certificateTemplates.use` only when naming a template.
   - `privateca.caPools.get` was removed from the issuance minimum. It is needed for pool discovery/trust-chain fetching, not `CreateCertificate`.
   - `CreateCertificate` is non-LRO Data Access `DATA_WRITE`, disabled by default. Enterprise retains the certificate resource; DevOps does not retain or revoke individual certificates.

2. **CA-pool IAM self-grant** with `privateca.caPools.setIamPolicy`.
   - The primitive can grant `roles/privateca.certificateRequester` on that pool.
   - Raw write minimum is `setIamPolicy`; the condition-safe `gcloud ... add-iam-policy-binding` helper also reads the policy and needs `privateca.caPools.getIamPolicy`.
   - `SetIamPolicy` is non-LRO Admin Activity and enabled by default.

3. **Relax pool or template constraints, then issue**.
   - Pool branch: `privateca.caPools.update` plus issuance.
   - Template branch: `privateca.certificateTemplates.update`, issuance, and template use; relevant where a conditional binding makes that template the remaining restriction.
   - The installed update helpers first `Get` the resource and poll the LRO, adding the relevant `.get` and `privateca.operations.get` to their raw patch minimum.
   - Pool constraints still apply to template-backed requests. `privateca.certificateAuthorities.update` does not widen issuance policy and was removed from this technique.

4. **Attacker-controlled subordinate CA signing key** as persistence.
   - A customer-managed `ASYMMETRIC_SIGN` key is Enterprise-only, must be enabled and location-compatible, and can reside in the attacker's KMS project.
   - Raw victim sequence: create CA, fetch its CSR, issue its subordinate certificate from the trusted pool, activate, and enable. This maps to `privateca.certificateAuthorities.create`, `.get`, `.update`, plus `privateca.certificates.create` on the issuer.
   - Installed `gcloud privateca subordinates create` additionally lists issuer CAs, polls CA operations, calls `GenerateServiceIdentity`, and reads/updates the supplied KMS key policy to grant the victim CA Service service agent `roles/cloudkms.signerVerifier` and `roles/viewer`.
   - Offline use is bounded by X.509 constraints and downstream trust. Deleting the CA Service object does not invalidate an already issued CA certificate; containment depends on trust removal and effective revocation checking.
   - Corrected Cloud KMS `AsymmetricSign` from `DATA_WRITE` to `DATA_READ`, disabled by default. Corrected the example to sign the TBSCertificate input once rather than pre-hashing and asking `gcloud` to hash it again; `gcloud` emits base64-encoded signature output.

### Rejected or folded hypotheses

- **Revoke certificates, patch CRLs, disable/delete a CA:** availability or integrity operations, not privilege escalation. Removed from the privesc page; retain as research context only.
- **`privateca.certificates.createForSelf` as arbitrary identity forgery:** rejected. It is the constrained workload self-enrolment path and is not equivalent to `privateca.certificates.create`.
- **`privateca.certificateAuthorities.update` as policy relaxation:** rejected. It changes CA lifecycle/configuration, not the pool/template certificate constraints that govern this path.
- **Google-managed subordinate key as an offline attacker key:** rejected. A Google-managed CA signing key is not handed to the caller. Offline post-IAM signing requires retained control of the customer-managed KMS key or another independent key compromise.
- **Describing every certificate as accepted by every root-trusting application:** rejected. Path validation, key usage, name constraints, application identity mapping, and revocation behavior all bound the result.
- **Certificate-template `setIamPolicy` as a standalone H3:** not independently useful. It can grant template use, but still needs certificate issuance and a useful template/conditional path. It remains a narrow prerequisite/lead, not a separate escalation primitive.
- **CRL `setIamPolicy` as privesc:** rejected; it concerns revocation-list access, not acquisition of a new identity or authority.
- **CA/certificate `setIamPolicy` claims from predefined-role permission lists:** the current v1 REST surface has no IAM methods on those resources. Permission presence in role metadata alone was not treated as an actionable technique.

### Telemetry notes

- Current exact CA Service write methods use the `google.cloud.security.privateca.v1.CertificateAuthorityService.*` names, except IAM `SetIamPolicy` and long-running `google.longrunning.Operations.GetOperation`.
- CA create/activate/enable and pool/template updates are LRO Admin Activity. CLI polling is Data Access and off by default; `WaitOperation` has no audit event.
- `CreateCertificate`, including the subordinate-certificate issuance inside the helper, is non-LRO Data Access and off by default.
- `FetchCertificateAuthorityCsr` and CLI issuer validation (`ListCertificateAuthorities`) are Data Access and off by default.
- KMS key creation and `SetIamPolicy` are Admin Activity; KMS `GetIamPolicy` and `AsymmetricSign` are Data Access and off by default.
- The current Service Usage audit catalog explicitly excludes `google.api.serviceusage.v1beta1.ServiceUsage.GenerateServiceIdentity` from audit logging.

### Open evidence questions

- The v1 API and current `gcloud` expose IAM on certificate templates, while the current CA Service audit catalog's `SetIamPolicy` entry lists only `privateca.caPools.setIamPolicy`. A controlled telemetry test is needed before publishing a categorical template-IAM log method claim.
- Capture an Enterprise-pool cross-project signing-key creation to confirm the complete sequence of secondary KMS calls performed by CA Service itself (for example, public-key reads/signing during provisioning) and their caller identities.
- Validate downstream rejection/acceptance with a purpose-built mTLS verifier that exercises CA name constraints and CRL enforcement; do not infer authorization from chain validity alone.

### Independent cross-review

- Rechecked the three privilege-escalation and one persistence boundaries against the current CA Service REST/audit catalogs, template/pool policy intersection and Cloud KMS logging. The official catalog confirms `UpdateCaPool` and `UpdateCertificateTemplate` are Admin Activity LROs and `CreateCertificate` is non-LRO `DATA_WRITE`; no correction was required.
- Rechecked the offline-signing example's single-hash and base64-output semantics, the separation of caller versus CA Service service-agent KMS permissions, and the downstream trust/name-constraint bounds. The retained claims remain appropriately conditional.
