# Iam And Credentials — open ideas

Open ideas — IAM / credentials / federation.

Coverage is exhausted across three closure passes. No open actionable candidate at this time.

Generate-more triggers (only if a new IAM surface ships):
- [ ] Re-diff `gcloud iam list-testable-permissions //cloudresourcemanager.googleapis.com/projects/<p>`
  against the wiki when GCP adds new `iam.*` / `iamcredentials.*` permissions.
- [ ] Watch for new Workforce/Workload federation subresources (managedIdentities, scim*) gaining
  `setIamPolicy`-free membership levers.

## Resolved — Managed Workload Identity attestation-rule persistence — SHIPPED (2026-09-25)
- [x] **`workloadIdentityPoolManagedIdentities.setAttestationRules`** (correct string; the guessed
  `managedIdentities.addAttestationRule` was wrong). Live-verified control plane: a principal with ONLY
  a custom role holding the attestation-rule write (no `setIamPolicy` anywhere) added a rule enrolling
  an attacker workload into a privileged managed identity; membership is INVISIBLE to `getIamPolicy`
  (managed-identities/namespaces have no get-iam-policy surface). `roles/iam.workloadIdentityPoolAdmin`
  grants it without broad IAM. Rule write IS logged (`AddAttestationRule`, Admin Activity); resulting
  membership + token mint are not. SHIPPED → `gcp-workload-identity-federation-persistence.md`. See tested.md.

## Assessed this iteration — NOT primitives (2026-09-25)
- WIF **`providerKeys`** = SAML-response encryption keys only (decrypt inbound SAML); not a
  credential-mint or membership lever. Non-primitive.
- WIF **`namespaces`** = a separate managed-identity grouping construct; membership is governed by the
  attestation-rule model above, not by namespaces themselves. The lever is the attestation rule.
