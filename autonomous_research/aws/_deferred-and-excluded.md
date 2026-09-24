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
- **iotfleetwise**, **iot-managed-integrations** — inconclusive: account not enabled / no endpoint.
  Documented as a *pattern* NOT claimed verified. Revisit if the account is enabled.

## No distinct primitive (verified-none — do not manufacture a page)

- **appsync CreateResolver/UpdateResolver**, **cloudfront CreateFunction/UpdateFunction** — run in a
  SANDBOXED engine (VTL/JS) with NO AWS role/credentials. Not a role-hijack primitive.
- **quicksight/connect/backup `*definition` / `*template`** members = DATA/report definitions, not
  executable code (regex `definition$` noise).
- **glacier SetVaultAccessPolicy** — legacy; reinstated to the cross-account matrix with an explicit
  "existing vaults only" caveat (not a new-account vector).
- **iotthingsgraph** deprecated; **machinelearning / marketplacecommerceanalytics** deprecated/legacy.
- Governance/finance/collab tail (wellarchitected/resiliencehub/auditmanager/etc.) — no distinct
  privesc/postexploit/persistence primitive beyond what the resource-policy matrix already covers.

## Honest niche exclusions (real primitive, low value / untestable)

- **signin `CreateOAuth2Token`** — returns creds but `signin` is an internal console-federation
  service, not a normal IAM-callable API. Unverifiable.
- **pca-connector-scep `GetChallengePassword`** — SCEP enrollment challenge password; very niche
  Private-CA device onboarding.
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
  `GetConnectorDestination.SecretsManager`) — preview / account-not-enabled / no endpoint (cont.41).
  Real device-provisioning-key primitive if enabled; revisit when GA + onboardable.
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
