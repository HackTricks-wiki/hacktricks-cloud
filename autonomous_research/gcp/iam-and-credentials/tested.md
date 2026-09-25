# Iam And Credentials — tested

IAM, Service Accounts, IAM Credentials, Deny policies, WIF/Workforce federation. Fully covered in
the book; recorded here for the LIVE-FIRE facts that correct common assumptions.

## Self-impersonation token renewal is NOT stealthy — VERIFIED LIVE
- `iamcredentials.GenerateAccessToken` / `SignJwt` (self-impersonation) **are logged by default** in
  the `data_access` stream **even with Data Access logging OFF** — this impersonation stream is on by
  default and effectively cannot be disabled. Corrects the common "token self-renewal is silent" claim.

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
