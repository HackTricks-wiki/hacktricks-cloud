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
