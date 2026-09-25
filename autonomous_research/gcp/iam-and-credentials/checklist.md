# Iam And Credentials — open ideas

Open ideas — IAM / credentials / federation.

Coverage is exhausted across three closure passes. No open actionable candidate at this time.

Generate-more triggers (only if a new IAM surface ships):
- [ ] Re-diff `gcloud iam list-testable-permissions //cloudresourcemanager.googleapis.com/projects/<p>`
  against the wiki when GCP adds new `iam.*` / `iamcredentials.*` permissions.
- [ ] Watch for new Workforce/Workload federation subresources (managedIdentities, scim*) gaining
  `setIamPolicy`-free membership levers.

## Open lead — Managed Workload Identity attestation-rule persistence (2026-09-25)
- [ ] **`managedIdentities.addAttestationRule` / `setAttestationRules`** (Managed Workload Identity, the
  newer WIF managed-identity model — distinct from the classic pool/provider). An attestation rule
  names *who* (which workload attributes) may assume a managed identity; adding a rule for an
  attacker-controlled workload is a candidate `setIamPolicy`-free membership backdoor analogous to the
  shipped `iam.oauthClients` workforce backdoor. Needs live confirmation that a rule grants token
  minting without touching the project allow policy, + the min-perm role. Cost-light (no compute) —
  prioritize next infra-standable iteration.

## Assessed this iteration — NOT primitives (2026-09-25)
- WIF **`providerKeys`** = SAML-response encryption keys only (decrypt inbound SAML); not a
  credential-mint or membership lever. Non-primitive.
- WIF **`namespaces`** = a separate managed-identity grouping construct; membership is governed by the
  attestation-rule model above, not by namespaces themselves. The lever is the attestation rule.
