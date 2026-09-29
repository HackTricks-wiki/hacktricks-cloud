# Firebase privilege-escalation research ledger

## 2026-09-28 — documentation-only page audit

- Reviewed every level-three technique in `gcp-firebase-privesc.md` against current official Firebase, Identity Platform, IAM, Firestore, and Cloud Storage documentation. No cloud resources were accessed or changed.
- Reduced the page to five independent privilege-escalation primitives:
  1. `firebaseauth.users.update` for application-user takeover or privileged custom claims.
  2. Same-project service-account key/signing access for Firebase custom-token forgery.
  3. `firebaseauth.configs.update` for Identity Platform blocking-function claim injection.
  4. `identitytoolkit.tenants.setIamPolicy` for tenant-scoped IAM self-grant.
  5. Firebase Rules deployment for indirect Firestore or Cloud Storage data access.
- Corrected Identity Platform telemetry. `SetAccountInfo`, user lookup, user import, and session creation are Data Access methods, not always-on Admin Activity. Password and custom-token sign-in are explicitly listed as producing no Cloud Audit Log.
- Corrected Firebase custom-token prerequisites. A downloaded same-project service-account key signs locally; the keyless path needs `iam.serviceAccounts.signBlob`. `actAs` by itself is insufficient, the signer need not be the `firebase-adminsdk-*` account, and no project-wide Token Creator grant on that account is guaranteed.
- Bounded blocking-function abuse to Identity Platform-enabled projects and supported function trigger URIs. Anonymous and custom-token authentication do not invoke blocking functions; forwarded IdP credentials depend on the provider and authentication flow.
- Added the previously buried tenant IAM self-grant as its own technique. Its impact is restricted to the selected tenant and does not reach the parent project, other tenants, or the default pool.
- Corrected Firebase Rules minimum permissions: deploying to an existing release requires `firebaserules.rulesets.create` plus `firebaserules.releases.update`; `.releases.create` applies only when the release does not exist. Corrected the PATCH body/update mask and downstream audit boundaries.
- Rejected Realtime Database rule opening as a separate privilege escalation:
  `firebasedatabase.instances.update` already grants full RTDB data read/write as well as rule modification. It remains useful as an exposure or persistence action, but yields no new data privilege to that caller.

## Material excluded from the privilege-escalation page

- Public RTDB, Firestore, Storage, HTTP Functions, and weak-password Authentication attacks require no prior GCP permission and belong in unauthenticated-access coverage.
- Password-hash/config-secret reads, direct Firestore entity operations, export/import, backup, bulk-delete, and TTL actions are direct post-exploitation or availability operations.
- Firebase Hosting deployment, Remote Config poisoning, FCM sending, App Distribution releases, and Firebase Management API app creation are content/supply-chain tampering or persistence, not a grant of stronger cloud or application privileges to the caller.
- Firebase CLI token theft requires prior local host compromise and is credential-access material.
- App Check enforcement changes/debug tokens remove a client-attestation control or cause denial of service; they do not independently grant backend data access when Firebase Security Rules or IAM still deny the request.
- Creating a rogue Identity Platform tenant is persistence in a new isolated pool, not access to an existing tenant or the default pool. Tenant IAM self-grant is retained instead.
- Adding an attacker-controlled OIDC/SAML provider, changing authorized domains, or disabling email verification is not a generic account takeover. It becomes escalation only when application logic grants privilege to the resulting identity; the deterministic blocking-function claims path is retained instead.
- The prior Firestore export claim that an arbitrary attacker bucket needs no target-side grant was not retained. Cross-project export destinations require the Firestore service agent to have the documented bucket permissions, and export is data exfiltration rather than privilege escalation.

## 2026-09-28 — independent cross-review corrections

- Removed quota-project headers from the two minimum-permission Identity Platform examples. Such a header can add a separate `serviceusage.services.use` check on the quota project and was not needed for either API call. Added the tenant-scoped `accounts:update` endpoint explicitly and bounded password takeover to projects where email/password sign-in is usable.
- Tightened custom-token prerequisites to configured Firebase Authentication and a usable Firebase Web API key whose restrictions permit Identity Toolkit. Added the supported `signJwt` path and exact signing telemetry: current Service Account Credentials calls are Data Access (the signing permissions have type `ADMIN_READ`), while legacy IAM signing calls, local private-key signing, and custom-token exchange produce no Cloud Audit Log.
- Replaced the loose blocking-function URL prerequisite with an already deployed, attacker-controlled blocking Cloud Run function using a supported Auth blocking-event handler. Function deployment and runtime identity permissions remain separate prerequisites when that resource does not exist.
- Replaced the tenant IAM example that would have overwritten unrelated bindings. The corrected workflow requests policy version 3, reuses only an unconditional Identity Platform Admin binding (or appends one), and preserves conditional bindings, the policy version, and the `etag` during read-modify-write.
