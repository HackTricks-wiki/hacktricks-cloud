# Iam And Credentials — tested

IAM, Service Accounts, IAM Credentials, Deny policies, WIF/Workforce federation. Fully covered in
the book; recorded here for the LIVE-FIRE facts that correct common assumptions.

## Self-impersonation token visibility — PRIOR BASELINE CLAIM RETRACTED (2026-09-28)
- A prior live observation found `GenerateAccessToken` / `SignJwt` in `data_access` and incorrectly
  generalized that they are logged by default even with Data Access logging off. Current official
  IAM documentation explicitly says short-lived-credential audit entries require IAM Data Access
  logging; `iamcredentials.googleapis.com` cannot be configured independently and follows the
  `iam.googleapis.com` or `allServices` Data Access configuration. The old test did not establish the
  effective ancestor/`allServices` audit configuration, so it cannot prove a platform exception.
- Book baseline: current Credentials API `GenerateAccessToken`, `GenerateIdToken`, `SignBlob`, and
  `SignJwt` are Data Access and off by default. Legacy IAM API `SignBlob`/`SignJwt` produce no audit
  log. A future live retest must capture the complete effective audit configuration before and after.

## IAM Deny policies — VERIFIED LIVE (4 claims)
1. `roles/owner` does NOT include `denypolicies.create`.
2. `iam.denypolicies.create` is NOT allowed in custom roles (`INVALID_ARGUMENT`).
3. `roles/iam.denyAdmin` is not grantable at project level (org/folder-gated).
4. Deny policies do NOT appear in `projects get-iam-policy` (separate surface → stealthy).

## WIF / Workforce federation
- OIDC static-JWKS pin (`--jwk-json-path`/`oidc.jwksJson`) hijacks a bound provider without touching
  issuer-uri (stealthier than SAML). Workforce SCIM group-membership injection
  (`iam.workforcePoolProviderScimGroups.patch`, roles `iam.scimSyncer`+`workforcePoolAdmin`) inherits
  bindings without `setIamPolicy`. WIF managed-identity attestation hijack
  (`iam.workloadIdentityPoolManagedIdentities.setAttestationRules`).

## Negative results (rejected after verification — do NOT re-file)
- SCIM `scimTenants.tokens.create` persistence — **permission does not exist** in `iam.scimSyncer` /
  `workforcePoolAdmin`. Rejected.
- WIF X.509 / provider Keys / AWS provider / extra-attributes — saturated, rejected.

Three independent closure passes (service enum, permission-level, fan-out) converged on 0 gaps.

## Managed Workload Identity attestation-rule membership backdoor — SHIPPED (2026-09-25)
Live-verified (control plane, end-to-end on the membership grant). NOT a duplicate: the only WIF wiki
pages cover the classic pool+provider model; zero coverage of Managed Workload Identity / attestation
rules anywhere in `src/`.
- **Primitive:** Managed Workload Identity (pool `--mode=trust-domain`) hierarchy pool→namespace→
  managed-identity; an **attestation rule** names a `--google-cloud-resource` (e.g. GCE VM attached-SA
  uid) allowed to attest AS the managed identity and receive its SPIFFE/mTLS creds. Adding a rule is the
  SOLE membership mechanism and a separate API surface from the IAM allow policy.
- **Min-perm (proven):** custom role with only `workloadIdentityPoolManagedIdentities.{getAttestationRules,
  setAttestationRules,get}` + `namespaces.get` + `workloadIdentityPools.get` + `resourcemanager.projects.get`
  sufficed to add a rule while the same principal was DENIED project get/setIamPolicy. Predefined
  `roles/iam.workloadIdentityPoolAdmin` grants the write with NO project `setIamPolicy`.
  (Correct string: `iam.googleapis.com/workloadIdentityPoolManagedIdentities.setAttestationRules` —
  the guessed `iam.managedIdentities.addAttestationRule` was WRONG.)
- **Stealth (crux, confirmed):** managed-identities/namespaces have NO get-iam-policy command/perm;
  pool `get-iam-policy` returned `{}`. Membership invisible to allow-policy review — analogous to the
  shipped `iam.oauthClients` backdoor.
- **Logs:** `AddAttestationRule`/`SetAttestationRules` (`google.iam.v1.WorkloadIdentityPools`) = Admin
  Activity NOTICE, always-on, verified live with attacker principalEmail. `getAttestationRules` = Data
  Access (off). Downstream cert/token mint by the attested workload = separate data-plane event.
- **Live-fired vs doc:** control plane fully live-fired (pool/namespace/MI create; min-perm role + test
  SA added a 2nd rule; setIamPolicy denial; getIamPolicy invisibility; Admin Activity entry). NOT
  live-fired: final token/cert mint by an attested workload (needs a real GCE VM matching the rule uid —
  disproportionate); documented from Google docs, no false "end-to-end token mint" claim in the page.
- **Teardown:** MI, namespace, SA+key, custom role, project IAM binding all deleted; pool soft-deleted
  (tombstone, auto-purges); local key + isolated gcloud config removed. No ACTIVE test residue.
- **Wiki:** new section in `gcp-workload-identity-federation-persistence.md` (+ refs 5,6).

## Identity federation service-enumeration coverage — SHIPPED (2026-09-26)

- Added `gcp-identity-federation-enum.md` under GCP services. It inventories classic Workload Identity Federation, organization-scoped Workforce Identity Federation, project-scoped workforce OAuth clients/credentials, and managed workload identities/attestation rules in one place.
- Enumeration includes soft-deleted pools/providers/clients, provider trust and claim mappings, pool policies, Cloud Asset searches for external-principal bindings, service-account policies, workforce bindings, OAuth client secrets, and attestation-rule membership that is invisible to `getIamPolicy`.
- Live read-only validation against the lab confirmed classic pool/provider listing and pool IAM, soft-deleted OAuth-client listing, Cloud Asset IAM search syntax, and namespace enumeration. A deleted trust-domain pool cannot be traversed as an active parent, as expected. No resource or policy was changed.

## 2026-09-28 — IAM privilege-escalation page audit

- Rebuilt `gcp-iam-privesc.md` from current official IAM, Service Account Credentials, OAuth, and
  audit-logging documentation. No cloud resources or policies were accessed or changed.
- Retained seven genuine primitives: custom-role mutation, direct access-token minting, service-account
  key create/upload, implicit delegation, `signBlob`/`signJwt`, service-account-policy self-grant, and
  OIDC ID-token minting.
- Corrected the custom-role boundary: `iam.roles.update` can add any permission supported and applicable
  to that custom-role level; the caller does not need to already hold the permission. An existing binding
  to the attacker or a controlled principal is the actual escalation prerequisite.
- Corrected all Service Account Credentials telemetry. `GenerateAccessToken`, `GenerateIdToken`,
  `SignBlob`, and `SignJwt` are Data Access and are not written by default; enable IAM Data Access logging
  because the credentials service cannot be configured independently. Legacy IAM `SignBlob`/`SignJwt`
  explicitly produce no audit log.
- Corrected the signed OAuth assertion example: ordinary service-account JWT bearer assertions omit
  `sub`; that claim is reserved for separately authorized Google Workspace domain-wide delegation and
  identifies the user to impersonate.
- Preserved the key-upload variant under the same exact `iam.serviceAccountKeys.create` permission and
  distinguished `UploadServiceAccountKey` from `CreateServiceAccountKey`, `USER_PROVIDED` from
  `GOOGLE_PROVIDED`, and the separate key-creation/key-upload organization policy constraints.
- Replaced the destructive service-account policy overwrite with a version-3, `etag`-preserving merge
  that never reuses a conditional Token Creator binding.
- Removed `iam.roles.create` plus a bind permission as a standalone technique: role creation grants no
  access, `iam.serviceAccounts.setIamPolicy` can directly bind Token Creator without a custom role, and
  hierarchy policy setters can directly bind an existing privileged role.
- Folded `iam.serviceAccounts.actAs` into the existing miscellaneous/service-specific coverage because it
  is a prerequisite for a resource run-as chain, not a standalone identity-escalation action.
- Removed duplicated tag-condition material from the IAM page and linked the dedicated Resource Manager
  page. The deleted text also used the obsolete/nonexistent `resourcemanager.tagValues.use` model; current
  tag attachment requires `resourcemanager.tagValueBindings.create` on the tag value plus the target
  resource's type-specific `createTagBinding` permission.

## 2026-09-28 — Independent cross-review corrections

- Added the active-role-at-use and satisfied-binding-condition requirements to custom-role
  escalation (the same update permission can reactivate a disabled role) and corrected direct
  `roles.patch`: an `etag` is concurrency protection, not an authorization prerequisite, and a
  caller can overwrite `includedPermissions` without first reading the role.
- Distinguished the 12-hour general `signJwt` payload limit from the one-hour OAuth JWT-bearer
  assertion limit, and recorded the one-hour, non-revocable service-account ID-token lifetime.
- Made the service-account policy merge force policy version 3 while retaining the returned `etag`,
  conditions, unrelated bindings, and members; it only creates or reuses an unconditional Token
  Creator binding.
- Corrected OIDC audience guidance: Cloud Run normally expects its generated `run.app` service URL or
  an explicitly configured custom audience, whereas IAP OIDC uses the IAP OAuth client ID rather than
  the protected request URL.
- Added exact final-permission audit types for direct and delegated Credentials API requests and
  retained the official off-default Data Access baseline. Corrected the signing command boundary:
  current `gcloud iam service-accounts sign-blob` uses `iamcredentials.googleapis.com` and produces
  off-default Data Access; only callers of the deprecated IAM v1 methods receive no audit log.

## 2026-09-28 — IAM post-exploitation and persistence reclassification

- Removed the two short-lived-token self-renewal claims from the book. Current official IAM
  credential guidance explicitly prohibits self-impersonation: self-`generateAccessToken` returns
  `FAILED_PRECONDITION`, and output of self-`signBlob`/`signJwt` through the IAM APIs cannot be used
  against IAM, IAM Credentials, or OAuth 2.0 APIs. The old examples and their default-on telemetry
  claims were both invalid.
- Replaced the IAM post-exploitation page with a quality-bar boundary. Destructive delete/disable
  actions are noisy denial of service, not high-value credential discovery, persistence, or cloud
  privilege escalation, and are no longer promoted as techniques.
- Added a dedicated IAM persistence page with two retained primitives: durable allow-policy bindings
  at project/folder/organization scope, and service-account undelete restoring the original immutable
  identity and its residual roles. Both are low-stealth, always-on Admin Activity operations. The
  undelete entry explicitly requires a separate retained path to use the restored identity and does
  not claim that undelete reveals a private key or mints a credential.
- Official contract: a deleted service account can normally be restored for 30 days if no replacement
  uses the same name; the original identity retains its roles. A same-email recreation gets a new UID
  and does not inherit the original bindings.
- A contained retained-key validation was attempted, but project policy propagation prevented the
  add-binding stage, so no retained-key conclusion was drawn. Cleanup was verified: zero matching
  `ht-undel-*` accounts, no project role binding for the test identity, the local private-key file
  removed, and the temporary cleanup-only Service Account Admin grant removed.
- Added missing technique-level telemetry and stealth ratings across IAM service enumeration and
  unauthenticated principal/domain reconnaissance. Current official audit catalogs establish three
  materially different baselines: IAM and Cloud Asset reads are generally off-by-default Data Access;
  Recommender recommendation/insight list/get methods explicitly produce no audit logs; feed creation,
  API enablement, and allow-policy writes are always-on Admin Activity. Policy Analyzer activity reads
  are off-by-default Data Access, while Policy Troubleshooter's documented internal
  `GetEffectivePolicy` read is visible only when IAM `ADMIN_READ` logging is enabled.
- Independent review corrected four precision edges: the wrong-principal-type helper needs both
  project policy read/write permissions; its validation-failed `SetIamPolicy` emission is undocumented
  and must not be presented as guaranteed; `QueryGrantableRoles` is an `OTHER` catalog entry governed
  by Resource Manager `ADMIN_READ` logging; and API enablement is the exact, always-on
  `google.api.serviceusage.v1.ServiceUsage.EnableService` LRO, whose polling can add
  `google.longrunning.Operations.GetOperation` Admin Activity entries.
