# Firebase privilege-escalation checklist

## Completed 2026-09-28

- [x] Inventory every original H3 and separate privilege escalation from unauthenticated access,
      persistence, credential access, content tampering, direct post-exploitation, and DoS.
- [x] Give every retained technique exact minimum permissions/prerequisites, bounded impact, a
      categorical Stealth rating, and an expandable Logs generated table.
- [x] Reconcile Identity Platform user/config/tenant methods with the current official audit catalog.
- [x] Correct service-account custom-token signing and token-exchange prerequisites and telemetry.
- [x] Correct existing-release versus new-release Firebase Rules permissions and REST semantics.
- [x] Bound downstream Firestore and Cloud Storage Data Access visibility.
- [x] Use official Google/Firebase primary documentation only and avoid cloud resource access.

## Open leads / future safe validation

- [ ] In a disposable Identity Platform project, compare project-pool and tenant-pool
      `accounts:update` audit entries with Data Access logging enabled, then restore the account and
      remove every test user.
- [ ] Verify whether a service account from a different project can ever sign an accepted Firebase
      custom token when `aud`, `iss`, and project configuration are manipulated. Current official
      guidance scopes signers to the Firebase project; do not promote a cross-project claim without
      evidence.
- [ ] Capture both IAM Credentials API and legacy IAM `SignBlob` method names with Data Access
      logging enabled; delete any temporary key immediately and prefer keyless signing.
- [ ] Validate the `iam.serviceAccounts.signJwt` Firebase custom-token path and capture both the
      IAM Credentials API and legacy IAM `SignJwt` audit method names with Data Access logging
      enabled.
- [ ] Validate the exact URI/project restrictions applied when PATCHing an Identity Platform
      blocking-function trigger, including a cross-project but authorized Cloud Run function.
- [ ] Confirm that tenant-scoped `roles/identityplatform.admin` grants only the tenant API methods
      documented by Identity Platform access control and cannot affect the parent/default pool.
- [ ] Exercise the version-3 tenant-policy merge against disposable conditional and unconditional
      bindings, verify the `etag` conflict behavior, and restore the original policy exactly.
- [ ] In disposable Firestore and Firebase Storage resources, capture client-plane audit behavior
      after an allow-all rules release with Data Access logging both disabled and enabled. Restore
      the original release immediately and delete the test ruleset when it is no longer referenced.
- [ ] Revisit conditional OIDC/SAML provider abuse only with a concrete application authorization
      premise, such as verified-domain or email-based administrator bootstrap.
