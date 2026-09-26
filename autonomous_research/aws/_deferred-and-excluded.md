# Deferred & reasoned-exclusion register (AWS)

Services/techniques deliberately NOT documented, with the concrete reason. Future agents: do not
re-test these blindly — revisit only when the stated blocker changes (docs published, account
enabled, cost model changes, or a helper library becomes available).

## Cost / not-onboarded blocked (revisit if budget or onboarding changes)

- **finspace-kx** `UpdateKxClusterCodeConfiguration` — inject kdb+ q-code onto a managed-kdb cluster
  whose executionRole is S3-scoped. Conceptually the generic ml-dataaccess-passrole pattern. Blocked:
  finspace-kx exceeds $5/30min budget and isn't onboarded in the lab account; q-code's ability to
  call arbitrary AWS APIs as the role (vs. only kdb/S3 ops) is unverifiable here. Reasoned exclusion,
  NOT a manufactured page. See `finspace-kx/checklist.md`.

## Preview / under-documented (revisit when public docs exist)

- **securityagent** — `CreatePentest`/`StartPentestJob`/`UpdateFinding`/`StartCodeRemediation`. LIVE
  in us-east-1 (authz probed OK) but preview with under-documented semantics. Deferred.
- **devops-agent / aidevops** — `UpdateOperatorAppIdpConfig` (rogue-IdP shape). No in-region
  endpoint / preview. Page correctly labeled "documented from public docs" where mentioned.
- **iotfleetwise** — inconclusive: account not enabled / no endpoint. Documented as a *pattern* NOT
  claimed verified. Revisit if the account is enabled.

## No distinct primitive (verified-none — do not manufacture a page)

- **appsync CreateResolver/UpdateResolver**, **cloudfront CreateFunction/UpdateFunction** — run in a
  SANDBOXED engine (VTL/JS) with NO AWS role/credentials. Not a role-hijack primitive.
- **WAFv2 `GetDecryptedAPIKey`** — misleading operation name, but the response schema returns only
  `CreationTimestamp` and `TokenDomains`; it does not return a decrypted/plaintext key. The caller must
  already supply the encrypted API key, which is intentionally embedded in browser JavaScript for the
  CAPTCHA integration. No credential-disclosure technique. See
  `waf/decrypted-api-key-name-false-positive-2026-09-26.md`.
- **quicksight/connect/backup `*definition` / `*template`** members = DATA/report definitions, not
  executable code (regex `definition$` noise).
- **glacier SetVaultAccessPolicy** — legacy; reinstated to the cross-account matrix with an explicit
  "existing vaults only" caveat (not a new-account vector).
- **iotthingsgraph** deprecated; **machinelearning / marketplacecommerceanalytics** deprecated/legacy.
- Governance/finance/collab tail (wellarchitected/resiliencehub/auditmanager/etc.) — no distinct
  privesc/postexploit/persistence primitive beyond what the resource-policy matrix already covers.

## Honest niche exclusions (real primitive, low value / untestable)

- **pca-connector-scep live challenge/enrollment proof** — the permission boundary is documented in
  the book, but a complete disposable connector could not be created in this lab. Two attempts
  established additional prerequisites (a root CA certificate with at least one full year remaining,
  then an AWS RAM share to the SCEP service principal); the share is restricted to the AWS
  Organization and organization sharing is not enabled for this account. Changing that persistent
  organization setting was out of scope for a fixture-only test. Revisit in an organization-enabled
  account. See `pca-connector-scep/challenge-live-boundary-2026-09-26.md`.
- **Audit Manager live evidence/report fixture** — `GetAccountStatus` returned `INACTIVE`. Audit
  Manager is closed to new customers, so the lab cannot safely create the prerequisite assessment
  data. Existing IAM-authorization-only documentation remains; do not claim a live artifact read.
- **ACM ACME endpoint token paths** — `ListAcmeEndpoints` returned no endpoints in `us-east-1` and
  `us-west-2`; there was no existing safe fixture to probe.
- **Route 53 Global Resolver `GetAccessToken`** — the service requires `us-east-2`, where the lab SCP
  (`p-oat9rg2i`) explicitly denies `ListGlobalResolvers`. No resource was created and no token path
  was tested. Current review additionally confirmed that the AWS-managed
  `AmazonRoute53GlobalResolverReadOnlyAccess` policy grants the secret-returning action on `*`, making
  the documented technique particularly relevant to read-only-role compromise. Revisit live only in an
  account/OU that permits the service.
- **Amazon Connect `CreateAuthCode` session minting** — IAM authorization and exact multi-resource
  behavior were verified, but every fully associated Customer Profiles request returned a service
  HTTP 500, including administrator calls. No authorization code was issued, so this is neither a
  public technique nor a security-impact bug report yet. See
  `connect/auth-code-session-boundary-2026-09-26.md` and revisit after AWS documents the remaining
  prerequisite or fixes the new API.
- **AWS Support App `CreateSlackChannelConfiguration` / `UpdateSlackChannelConfiguration` role
  binding** — this can conditionally expose support cases and future case notifications to every user
  in a configured Slack channel, but it is not generic execution as the passed role. The documented
  Slack interface is limited to Support and Service Quotas workflows. The lab has no authorized Slack
  workspace/channel, no role trusting `supportapp.amazonaws.com`, and no premium Support entitlement;
  creating the fixture would require third-party Slack OAuth/app installation. No state was changed.
  Revisit only with an existing test-owned authorized workspace and synthetic support case. See
  `support-app/slack-channel-role-2026-09-26.md`.
- **Backup Gateway `PutHypervisorPropertyMappings(IamRoleArn)`** — this stores VMware-to-AWS tag
  mappings; the passed role is used only to list/tag/untag Backup Gateway `vm/*` resources during a
  separate metadata sync. It does not vend credentials, access VM disks, or provide arbitrary role
  execution. The only conditional effect is tag manipulation that might influence tag-based backup
  selection or unusual ABAC. The lab has no gateway, hypervisor, VM, trusted role, or managed-policy
  attachment. A nonexistent-resource put failed at the gateway-version readiness check and created no
  state. A real fixture requires external VMware/vCenter plus a deployed gateway, and mappings have no
  dedicated delete API. Reasoned exclusion; see `backup-gateway/checklist.md`.
- **STS `GetDelegatedAccessToken` as a standalone technique** — a real credential exchange, but only
  for AWS Partner temporary delegation. IAM permission alone is insufficient: the caller must be an onboarded/registered partner
  and hold a trade-in token delivered after a customer associates and approves a delegation request.
  The resulting permissions are the intersection of the approved principal and a pre-registered
  session-policy template. The lab has no delegation requests or delivery SNS topic; a synthetic token
  returned `ValidationError: Invalid trade-in token` and created no state. This is not a general STS
  privilege-escalation primitive and no disposable fixture exists without partner onboarding plus a
  second-party approval workflow. The distinct customer-side risk of accepting a malicious delegation
  request is already documented on the IAM privesc page. See
  `sts/delegated-access-token-2026-09-26.md`.
- **License Manager `CreateToken` / `GetAccessToken`** — a real long-lived external credential
  primitive for seller-issued licenses, but not a broadly useful AWS-account persistence technique.
  The refresh token can repeatedly obtain one-hour OIDC tokens and reach only a preconfigured role
  trusting `openid-license-manager.amazonaws.com`; AWS's standard consumption role is limited to
  license-consumption operations. The lab is not onboarded, has no seller licenses or compatible
  role, and a complete fixture would leave License Manager onboarding state plus KMS key-deletion
  residue. Revisit only in an existing ISV seller-license deployment, especially when a custom
  trusting role has broader permissions or weak issuer conditions. See
  `license-manager/external-consumption-token-2026-09-26.md`.
- **s3files** (EFS-analog, has PutFileSystemPolicy/CreateMountTarget/CreateAccessPoint) — no
  confident public product name/citation, so NOT asserted. Candidate only.

## Scanner-tail deferrals (cont.58, 2026-09-24 — real secret-out/role-in but blocked)

- **codecatalyst `CreateAccessToken.secret`** — mints a CodeCatalyst PAT (persistence). Blocked:
  CodeCatalyst identity is AWS Builder ID / Identity Center space membership, a **separate identity
  plane** from the IAM account role — not cleanly reachable/testable via the lab account role. Niche.
- **finspace-data** (`GetProgrammaticAccessCredentials.credentials`,
  `GetExternalDataViewAccessDetails.credentials`, `ResetUserPassword.temporaryPassword`) — real
  credential-returning ops, but FinSpace is niche + not onboarded + cost-blocked (see finspace-kx).
- **qapps `CreatePresignedUrl`** — needs a Q Business subscription (same gate as QApps generally).
- **iot-managed-integrations** (`CreateProvisioningProfile.ClaimCertificatePrivateKey`,
  `CreateDestination.RoleArn`, `GetConnectorDestination.SecretsManager`) — the service is GA and the
  lab can reach it in `eu-west-1`, but every meaningful fixture requires the account to first call
  `RegisterCustomEndpoint`. AWS exposes no deregister/delete operation, so that onboarding would leave
  irreversible account-level state. The unonboarded lab safely confirmed the prerequisite error and
  currently has no custom endpoint. Revisit in an already-onboarded account; do not register the lab
  merely to test these candidates. See `iot-managed-integrations/checklist.md`.
- **security-ir** — NOT deferred: documented from model (see security-ir/tested.md).

## cont.61 (2026-09-24) — zero-coverage sweep tail (133 services cross-referenced)

- **payment-cryptography / payment-cryptography-data** — real crypto primitives but excluded as
  niche/covered-by-permission: `ExportKey` is HSM-wrapped (TR-31/TR-34/RSA, needs a KEK the service
  trusts — NO plaintext key exfil, like KMS); `DecryptData`->PlainText, `GeneratePinData`/
  `TranslatePinData`->PIN blocks are "the permission does what it says" on a PCI-PIN service used by
  a tiny population. `payment-cryptography:PutResourcePolicy` (cross-account key share) is the only
  structural vector — candidate matrix row if ever a customer uses the service. Not a page.
- **Remaining zero-coverage set** = runtime/data-plane variants (lex-runtime, personalize-runtime,
  *-data), deprecated (machinelearning, iotthingsgraph, mturk, swf, simpledbv2, importexport,
  marketplacecommerceanalytics), no-primitive read/catalog (controlcatalog, service-quotas,
  compute-optimizer, resource-explorer-2, geo-*, polly), or already deferred (finspace-data,
  codecatalyst, iot-managed-integrations, qapps, s3files). No further net-new privesc/persist/post
  primitive found in the tail beyond ssm-incidents (documented).
