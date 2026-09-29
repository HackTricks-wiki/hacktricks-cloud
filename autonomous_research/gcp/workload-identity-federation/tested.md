# Workload Identity Federation research ledger

## Scope and evidence

- Audited workload pools/providers, workforce pools/providers, workforce OAuth clients, managed
  workload identities, STS exchange, IAM Credentials impersonation, and their current IAM audit
  catalog against official Google Cloud documentation on 2026-09-28.
- Rechecked current predefined roles with local `gcloud iam roles describe`; this was read-only.
- Rechecked relevant local `gcloud` command help. No cloud resource or IAM state was changed during
  this audit.

## Previously validated expected behavior

The prior page recorded disposable-lab validation on 2026-09-08 with cleanup after each test:

- A principal holding only `iam.googleapis.com/workloadIdentityPoolProviders.create` added a SAML
  provider to a pool with a pool-wide Viewer binding; an attacker-signed assertion then exchanged at
  STS and read the project.
- A principal holding only `iam.googleapis.com/workloadIdentityPoolProviders.update` retained the
  current valid SAML certificate, added a controlled certificate, and made the controlled assertion
  usable. Google currently documents the signing-certificate overlap requirement.
- Provider undelete, pool re-enable, and pool undelete each restored an otherwise complete trust
  path when exercised through a single-purpose custom role containing the relevant permission.
- The control plane accepted an attestation-rule add from a custom role with the managed-identity
  attestation-rule write while project IAM policy access was denied. Downstream X.509 certificate
  issuance was not reproduced.
- Workforce OAuth client and credential creation were previously exercised, and credential describe
  returned the secret. End-to-end user authorization/refresh-token acquisition was not exercised.
- Deleted WIF resources were inert but remained soft-deleted tombstones during the documented
  recovery period; their identifiers were not immediately reusable.

## Retained privilege-escalation primitives

1. Create a controlled provider inside an existing workload pool whose admitted identities already
   match a privileged IAM binding.
2. Update a bound provider's trust/mapping controls. OIDC uploaded JWKS fully replaces fetched keys;
   SAML metadata must preserve at least one valid old signing certificate.
3. Restore a disabled/deleted pool or deleted provider when controlled trust and residual bindings
   remain. These were consolidated because they have the same security outcome.
4. Create/update a provider inside an already-authorized workforce pool, or restore a disabled or
   soft-deleted residual trust path. Uploaded OIDC JWKS is programmatic-only and cannot be used for
   federated Console sign-in.
5. Add an attestation rule to an existing managed workload identity, bounded to X.509/SPIFFE
   credentials and services/relying workloads that trust that identity.
6. Use a compromised Workforce SCIM tenant token to add an already accepted subject to a privileged
   group, or in Looker's users-and-groups mode modify a mapped custom claim. This is limited to the
   currently supported Gemini Enterprise and Looker integrations, not arbitrary GCP services.

## Retained persistence primitives

1. Create a workload pool/provider and add its principal set to a service account. This needs pool
   create, provider create, and service-account `setIamPolicy`; pool administration alone is not
   sufficient.
2. Create a workforce pool/provider and a target resource binding. Workforce principals are bound
   directly; no service-account hop is inherent.

## Rejected or folded hypotheses

- **SCIM group injection into arbitrary GCP IAM-bound workforce groups:** still rejected as an
  organization-wide claim. The 2026-09-25 documentation now supports SCIM as the authorization and
  OAuth claim source for Gemini Enterprise and Looker (Preview), so the supported-product path is
  retained separately. Ordinary federation outside those integrations still uses its configured
  assertion/token group source.
- **Managed identity attestation rule as a second persistence heading:** folded into privilege
  escalation. The described action hijacks an existing authorized identity and duplicated the same
  primitive.
- **Managed identity rule yields an STS/OAuth service-account token:** rejected. Managed workload
  identity issues X.509/SPIFFE credentials for mTLS; impact must be bounded accordingly.
- **`oauthClientCredentials.get` alone hijacks a legitimate OAuth application:** rejected as a
  general persistence claim. A client secret does not by itself control the registered redirect URI
  or produce a user's authorization code/refresh token.
- **Create a Workforce OAuth client with an attacker redirect and capture a refresh token:** removed
  from the book after independent review. Google documents this application-integration surface as
  IAP-only; the supported Workforce/IAP callback is
  `https://iap.googleapis.com/v1/oauth/clientIds/CLIENT_ID:handleRedirect`. Creating a client and
  secret does not configure an IAP resource, and knowing the client secret does not deliver IAP's
  authorization code to the caller. OAuth client/credential inventory remains security-sensitive,
  but it is not a standalone persistence primitive.
- **Provider SAML assertion-encryption key creation as escalation:** rejected. Google holds the
  private decryption key, and the provider still accepts plaintext assertions; creating an encryption
  key does not expand who can authenticate.
- **Pool `setIamPolicy` grants identities in that pool resource access:** rejected. That policy
  delegates administration of the pool; external principals need bindings on target resources or
  service accounts.

## Telemetry corrections

- Exact workload config-write methods use `google.iam.v1.WorkloadIdentityPools.*`; workforce writes
  use `google.iam.admin.v1.WorkforcePools.*`. These are always-on Admin Activity, and the documented
  create/update/undelete and attestation methods are LROs.
- STS `google.identity.sts.v1.SecurityTokenService.ExchangeToken` is Data Access with permission type
  `ADMIN_READ`, not `DATA_READ`, and is off by default. Some client-caused exchange failures are not
  logged.
- IAM Credentials `GenerateAccessToken` is separate Data Access (`ADMIN_READ`) and off by default.
- `google.longrunning.Operations.GetOperation` can appear when helpers poll; it is not an additional
  permission required by raw create/update/undelete calls and is off by default under IAM logging.

## Independent cross-review (2026-09-28)

- Rechecked the five privilege-escalation and two retained persistence boundaries against the
  current GA IAM/STS REST schemas, IAM and CA Service audit catalogs, local stable `gcloud` help, and
  current predefined roles. No project resources or policies were read or changed.
- Confirmed that the service-qualified `iam.googleapis.com/...` permission strings used by current
  predefined WIF/workforce/OAuth roles are intentional; they must not be confused with the
  `iam.googleapis.com` audit service name or the mostly unqualified permission spellings displayed
  by the IAM audit catalog.
- Corrected residual-token semantics: disabling a pool blocks new exchanges and active pool tokens,
  whereas disabling a provider blocks new exchanges but leaves already-issued tokens valid. Pool
  restoration can reactivate a still-valid token; provider restoration primarily restores exchange.
- Added the `iam.operations.get` boundary for helper polling while preserving the mutation-only raw
  REST minimum, organization-policy prerequisites for provider create/update, cross-project Cloud
  Asset search scope, exact enumeration reads, and conditional CA Service issuance telemetry for a
  customer-managed CA pool.
- Removed OAuth-client creation as a standalone persistence technique. Official guidance makes the
  application integration IAP-only and the supported IAP setup uses IAP's generated
  `:handleRedirect` callback. The management API does accept another `allowedRedirectUris` value,
  but that control-plane acceptance alone neither configures an IAP resource nor establishes a
  supported code-delivery path; secret possession likewise does not deliver IAP's authorization
  code or refresh token to the caller. Keep client/credential enumeration because
  `GetOauthClientCredential` returns the secret and is off-by-default Admin Read Data Access, but do
  not claim an independent token backdoor without separately evidenced IAP control/code delivery.

## 2026-09-29 SCIM / Looker release-delta review

- Reconciled the September 21/25 documentation change that adds
  `enabled-for-users-groups` for Looker. In that mode SCIM users, groups and mapped custom claims
  feed IAM authorization and Looker OAuth; `enabled-for-groups` remains the Gemini Enterprise mode.
- Retained a bounded privilege-escalation technique for a compromised tenant provisioning token.
  The token is attached to the tenant service agent; `roles/iam.scimSyncer` supplies the exact SCIM
  user/group permissions. `PatchGroup`, `CreateUser`, and `PatchUser` are always-on Admin Activity
  under `iamscim.googleapis.com`, but attribution is to the shared service agent.
- The project-only lab identity has no organization visibility or workforce-pool permissions, so no
  tenant was created and no IdP sign-in was attempted. Read-only organization discovery was denied;
  one create request against an intentionally nonexistent pool returned `NOT_FOUND` and created no
  resource. The technique rests on the explicit current service contract and standard SCIM PATCH
  semantics.
