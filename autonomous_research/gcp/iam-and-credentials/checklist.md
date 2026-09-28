# Iam And Credentials — open ideas

Open ideas — IAM / credentials / federation.

Coverage is exhausted across three closure passes. No open actionable candidate at this time.

Generate-more triggers (only if a new IAM surface ships):
- [ ] Re-diff `gcloud iam list-testable-permissions //cloudresourcemanager.googleapis.com/projects/<p>`
  against the wiki when GCP adds new `iam.*` / `iamcredentials.*` permissions.
- [ ] Watch for new Workforce/Workload federation subresources (managedIdentities, scim*) gaining
  `setIamPolicy`-free membership levers.

## Open validation after the 2026-09-28 page audit

- [ ] Capture current `iamcredentials.googleapis.com` `GenerateAccessToken`, `GenerateIdToken`,
      `SignBlob`, and `SignJwt` entries with IAM Data Access logging both disabled and enabled; do not
      retain tokens and restore the logging policy exactly. Capture organization-, folder-, project-,
      and `allServices` audit configuration so the retracted historical "logged by default" observation
      cannot be confused with inherited or cross-service Data Access configuration.
- [ ] Validate the version-3 service-account policy merge against disposable conditional and
      unconditional Token Creator bindings, including an intentional stale-`etag` conflict; restore the
      original policy byte-for-byte.
- [ ] Confirm the current maximum lifetime behavior for a disposable service account included in
      `constraints/iam.allowServiceAccountCredentialLifetimeExtension`, then remove the exception and
      discard the token.
- [ ] With a disposable service account, validate a `signJwt` OAuth bearer assertion that omits `sub`;
      separately distinguish Google's direct self-signed-JWT example from Workspace domain-wide
      delegation, discard every token, and remove all grants.
- [ ] Re-test generated versus uploaded service-account keys under the independent
      `disableServiceAccountKeyCreation`, `disableServiceAccountKeyUpload`, and key-expiry constraints;
      immediately delete every temporary key and local private-key file.
- [ ] In a disposable project where service-account lifecycle permissions are already effective,
      validate whether a user-managed key that was not separately deleted becomes usable again after
      deleting and undeleting the original service-account UID. Do not publish either outcome until
      the key is deleted, the restored account is deleted, all bindings are removed, and zero active
      test resources are independently confirmed.

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
