# AWS audit — status

Last updated: 2026-09-24

## Completion state per axis

| Axis | State | Notes |
|---|---|---|
| Privesc (existing services) | ✅ complete | impact + "Logs generated" retrofit done across the 28-page privesc tail |
| Post-exploitation (existing) | ✅ complete | impact + logs retrofit done across the 17-page post-ex tail |
| Persistence (existing) | ✅ complete | + Stealth rating on every persistence technique |
| Privesc/post/persistence (net-new services) | ✅ saturated | 34 net-new pages/techniques; phase-2 zero-presence services swept |
| Unauth / recon (all 433) | ✅ complete | 7 new pages + 7 cross-account resource-policy matrix rows; 8-slice manual pass |
| Cross-account resource-policy matrix | ✅ complete | all 75 policy-setters across 433 enumerated; 65 matrix rows |
| autonomous_research folder | 🟡 in progress | this scaffold; per-service checklists being seeded |

**34 net-new pages/techniques + 27 format-fixed** cumulative. HEAD == origin `6f165c07e`.
PR #413 body updated through the full unauth sweep.

## The 7 convergent lenses

privesc-PassRole · unauth-authtype · recon-output-shape · persistence · hijack-no-PassRole ·
per-service-ledger (`master_ledger.csv`) · 8-slice manual review. All converge on "no further
clean net-new gap that clears the no-garbage bar." Remaining items are reasoned exclusions
(niche/preview/deprecated/cost-blocked) — see each `<service>/tested.md` and `checklist.md`.

## Standing irreversible residue (do NOT re-flag as a mistake)

- `ht-audit-objlock-1790090581` — S3 bucket, one 12-byte object `auto.txt` under COMPLIANCE
  retain-until **2126-08-29**. Undeletable by any principal incl. account root & AWS Support, by
  design. ~$0 cost. Verified empirically. Leave it.
- 2 customer KMS CMKs (`1bb73ce3…`, `acdd6d73…`) in PendingDeletion → self-delete 2026-09-29.
  **Reuse these for KMS tests** instead of creating new CMKs.

Everything else removable has been removed (residue sweep cont.53, 2026-09-24).

## Known content gaps still worth a page (tracked as per-service checklists)

- ~~ElastiCache — no enum/privesc/post~~ **STALE/WRONG**: `aws-services/aws-elasticache.md` exists
  with enum + 2 post-ex techniques (ModifyUser password reset, CopySnapshot→S3 exfil) + persistence
  page. Only a distinct *privesc* framing might be marginally addable (low value).
- MemoryDB — persistence only; no privesc/post.
- Glue — no dedicated `aws-services/` enum page (organizational only; GetConnection creds already
  documented in post-ex — verified 2026-09-24, see glue/).
- `aws-vpn-post-exploitation` — empty stub.
- ~~SSO / Identity Center — persistence angle not yet a page.~~ **STALE/WRONG**: verified cont.66 —
  `aws-privilege-escalation/aws-sso-and-identitystore-privesc/README.md` comprehensively covers the
  persistence-relevant primitives (CreatePermissionSet + policy inject + CreateAccountAssignment,
  identitystore/sso-directory CreateUser, CreateGroupMembership, GetRoleCredentials cache theft, plus
  Detach/Delete defense-evasion variants). No separate persistence page needed.
- Redshift — privesc+post exist; no persistence/enum-deepen.

## Net-new since the all-433 sweep

- **AppFabric** (`aws-services/aws-appfabric-enum.md`, 2026-09-24) — zero prior coverage. Enum +
  `appfabric:CreateIngestionDestination` SaaS-audit-log redirect/exfil + SOC-blinding (authz gate
  verified, end-to-end doc-scoped due to SaaS-OAuth precondition). Defensive negative: AppFabric
  does NOT leak stored SaaS credentials via API. See appfabric/.

## Open-idea backlog lives per service

See `<service>/checklist.md`. When an idea is tested it moves to `<service>/tested.md` with the
result, and — if it works and clears the no-garbage bar — into the public book.

## Saturation update (cont.61, 2026-09-24)
- Systematic zero-coverage sweep: ALL botocore services cross-referenced vs the whole book -> 133
  zero-coverage services; signal-scanned the tail; only ssm-incidents yielded a net-new page. Rest =
  runtime/data-plane variants, deprecated, no-primitive, or already-deferred.
- Newest 2024 services (bedrock-agentcore) confirmed ALREADY comprehensively covered (token-vault
  vending, execution-role pivots, sandbox escape, resource-policy) — no net-new.
- This continuation net-new: CloudTrail Lake EDS anti-forensics; Deadline queue-role privesc
  (VERIFIED live); Incident Manager counter-IR. Cumulative ~40 net-new + 27 format-fixed.
- Remaining threads are compute-gated (Deadline CreateJob->RCE, response-plan/replication-set
  end-to-end, AgentCore token-vault/payments) -> parked in per-service checklists for a
  compute-authorized run.

## Saturation update (cont.62-66, 2026-09-24)
- **Net-new this stretch (all pipelined to PR #413):**
  - #42 MWAA classic token->DAG exec-as-execution-role (`airflow:CreateWebLoginToken`/`CreateCliToken`).
  - #43 MWAA exec-role repoint (`airflow:UpdateEnvironment --execution-role-arn` + PassRole) — authz
    VERIFIED. GOTCHA: MWAA IAM prefix is `airflow:`, not `mwaa:`.
  - #44 IoT Core credential-provider role alias (`iot:CreateRoleAlias`/`UpdateRoleAlias` + PassRole ->
    vend any credentials.iot-trusting role via X.509 cert at the cred-provider endpoint) — VERIFIED
    END-TO-END, zero cost. Vend leaves NO CloudTrail event (stealth persistence).
  - #45 Transfer Family role-choice (`transfer:CreateUser`/`UpdateUser`/`CreateAccess` + PassRole binds
    a chosen role to an SFTP identity) — authz VERIFIED. Distinct from pre-existing ImportSshPublicKey.
  - Deadline fleet-role privesc (VERIFIED live, no-compute CMF worker), earlier in stretch.
- **Saturation CONFIRMED across the whole credential/role-vending seam:** Cognito identity pools
  (SetIdentityPoolRoles/unauth vend/RBAC), SSM CreateActivation, IAM Roles Anywhere
  (CreateTrustAnchor+Profile / UpdateTrustAnchor / STS privesc), App Runner (CreateService RCE +
  UpdateService + mutable-tag auto-deploy), Glue GetConnection creds, RDS IAM auth — ALL already
  documented. The generic PassRole-into-job family is exhaustively catalogued in
  aws-ml-dataaccess-passrole-privesc (MSK Connect, Braket, m2, Panorama, DAX, pcs, osis, timestream,
  chime, ... all listed). Net-new only comes from DISTINCT mechanisms the catalog doesn't model.
- **Cumulative: ~45 net-new + 27 format-fixed. All test infra torn down + verified each cycle.**
- **Primed threads for a compute-authorized run:** Transfer custom-IdP Lambda (attacker-controlled
  auth Lambda mints arbitrary Role/Policy per login); IoT provisioning-template role selection +
  UpdateCACertificate autoregistration persistence; MWAA end-to-end env exploitation; Deadline
  CreateJob->RCE-on-worker.

## Saturation update (cont.68-70, 2026-09-25)
- **#47 Lambda exec-role repoint** (`lambda:UpdateFunctionConfiguration --role` + PassRole + Invoke) —
  authz VERIFIED live (two-sided). Shipped: aws-lambda-privesc/README.md. PR #413. ~47 net-new.
- **Repoint/attach-role lens CONFIRMED SATURATED:** Redshift already covers BOTH `ModifyClusterIamRoles`
  and serverless `UpdateNamespace` with two-sided PassRole proof; Batch covers RegisterJobDefinition
  PassRole + SubmitJob (live); CodeBuild/CloudFormation/App Runner/Step Functions all covered. Lambda
  was the last clean gap in this family.
- **DEAD LENS — "Describe/List returns a stored password":** systematically scanned botocore for read-op
  output shapes with secret-like fields (password/secret/credential/token/privatekey). Empirically tested
  the two strongest candidates:
  - AppStream `DescribeDirectoryConfigs.ServiceAccountCredentials` → **AccountPassword REDACTED**, only
    `AccountName` (DOMAIN\user) returned. (appstream/tested.md)
  - DMS `DescribeEndpoints` → **Password removed from output shape**; no value returned. (dms/tested.md)
  - **Calibration:** botocore `sensitive:true` = scrub-from-logs, NOT returned-in-response. AWS redacts
    stored passwords from Describe/List. The ONLY reliable secret vends are purpose-built
    `Get*Credentials`/`GetSecretValue`/`GetAuthorizationToken`/`GetRoleCredentials`/`GetCredentialsForIdentity`/
    `DownloadDefaultKeyPair`/`GetInstanceAccessDetails`/`GetTemporary*Credentials`/`GetDataAccess` — ALL
    already documented (Lightsail, Lake Formation, S3 Access Grants, SSO, Cognito, ECR, CodeArtifact,
    STS, EMR GetClusterSessionCredentials, Redshift GetClusterCredentials, Glue GetConnection).
  - Remaining `sensitive` fields (EMR KerberosAttributes, RDS/docdb/neptune MasterUserPassword, storagegateway
    CHAP, ds SharedSecret, cloudhsmv2 PreCoPassword, wickr OIDC) are the same redacted-in-Describe class →
    not chased. If ever revisited, must be empirically re-tested, not assumed.
- **Cumulative: ~47 net-new + 27 format-fixed.** All test infra torn down + verified each cycle.

## Saturation update (cont.73-74, 2026-09-25)
- **Verified net-new shipped this session:** #47 Lambda UpdateFunctionConfiguration --role repoint; #48
  Amazon S3 Files (new page: CreateFileSystem+PassRole data-access + PutFileSystemPolicy cross-account
  matrix row [66] + mount-target exposure); #49 EKS UpdatePodIdentityAssociation repoint (role swap +
  target-role cross-account chaining + disable-session-tags ABAC bypass). All authz-verified two-sided.
- **Lenses confirmed saturated/dead this session:**
  - Update*+PassRole "repoint an existing resource's role": saturated after Lambda + EKS (Redshift both
    cluster+serverless, Batch, ECS exhaustive, CodeBuild, App Runner, Step Functions, MWAA, Transfer,
    Amplify all done). Remaining role-input Update ops = niche ML/legacy or no-vend-value (rds:ModifyDBProxy
    role doesn't change configured secret; batch serviceRole limited; s3control:UpdateAccessGrantsLocation
    = marginal Update of documented Create).
  - Code/script injection into an existing execution path: Glue EXHAUSTIVE (StartJobRun --scriptLocation,
    UpdateJob, s3:PutObject on script, workflow stored-authority, blueprints), CodeBuild/ECS/Lambda covered.
  - Describe/List secret-disclosure: DEAD (AppStream/DMS redact; sensitive:true = log-scrub only).
- **New-service frontier:** s3files shipped; iot-managed-integrations parked (irreversible RegisterCustomEndpoint
  onboarding gate); rest of 2024+ services = no security primitives.
- **Cumulative: ~49 net-new + 28 format/matrix.** All test infra torn down + verified each cycle.

## Saturation update (cont.75) — identity-provider / trusted-token-issuer lens
- SHIPPED (doc-grounded) #50: `sso-admin:CreateTrustedTokenIssuer` rogue TTI → impersonate any Identity Center user via JWT-bearer grant / CreateTokenWithIAM into trusted-identity-propagation apps (Q Business, Redshift, QuickSight, S3 Access Grants). Commit c8980fe16 on research/aws-technique-audit; PR #413 bullet added; autonomous_research/aws/identity-center/{tested,checklist}.md.
- Book-wide grep confirmed TTI/TTP was 0-hit (genuinely undocumented). Lab is Org MEMBER acct (no IdC instance) → doc-grounded per precondition exception; parked end-to-end verify for an IdC-enabled account.
- Identity-provider lens status: IAM SAML/OIDC + Cognito IdP = already covered; TTI = the net-new gap, now shipped. iot:CreateAuthorizer / apigateway:CreateAuthorizer = low IAM-privesc value (app-scoped auth bypass), parked in checklist for possible enum-page mention.

## Saturation update (cont.76) — Batch RegisterJobDefinition+PassRole
- SHIPPED #51 (VERIFIED two-sided): batch:RegisterJobDefinition + iam:PassRole (+ SubmitJob) run-container-as-passed-role, new first section on aws-batch-privesc/README.md. Complements existing SubmitJob-only technique. Commit 6693993d7; PR #413 bullet added.
- Repoint/compute-exec lens sweep: Glue UpdateJob/UpdateDevEndpoint, CodeBuild UpdateProject, Step Functions UpdateStateMachine, CodePipeline UpdatePipeline all covered. Batch's Register+PassRole was the one primary-path gap (only parenthetical before) - now closed.
- Teardown verified: no ht-* roles, no ACTIVE ht-batch-probe defs (INACTIVE remain, no hard-delete available).

## Saturation update (cont.77) — NEW SERVICE Bedrock AgentCore
- SHIPPED #52 (NEW PAGE, 2 techniques VERIFIED two-sided): aws-bedrock-agentcore-privesc/README.md. CreateCodeInterpreter+PassRole (POS created READY interpreter); CreateAgentRuntime(+CreateAgentRuntimeEndpoint)+PassRole (POS advanced past PassRole to endpoint gate, NEG PassRole AccessDenied). + Update-repoint (doc), + data-plane cred vend GetWorkloadAccessToken->GetResourceApiKey/Oauth2Token plaintext (doc, sensitive:true). SUMMARY wired. Commit 1b5051e17; PR #413 bullet.
- Found via comprehensive credential-vend sweep across all 423 botocore services (autonomous_research method). AgentCore = biggest net-new frontier surfaced.
- Calibration reconfirmed: control-plane Get*CredentialProvider returns only Secrets Manager ARN; data-plane GetResourceApiKey returns plaintext (sensitive:true).
- Teardown verified clean.

## Saturation update (cont.78) — SES sending-authorization backdoor
- SHIPPED #53 (doc+partial-verify): ses:PutIdentityPolicy / sesv2:PutEmailIdentityPolicy cross-account sending-authorization backdoor, new section on aws-ses-post-exploitation. Commit 1a0931630; PR #413 bullet.
- Found via all-services resource-policy-setter sweep (Put*Policy/Add*Permission vs cross-account matrix). SES identity policy was a proper-section gap (matrix had only 1 line). 
- Other sweep candidates parked/rejected: s3control PutMultiRegionAccessPointPolicy (MRAP cross-account - candidate), signer AddProfilePermission (code-signing cross-account - niche), waf*/PutPermissionPolicy (rulegroup share - low), mediastore PutContainerPolicy (service EOL). Scaling/read policies discarded.

## Saturation update (cont.79) — Budgets CreateBudgetAction privesc
- SHIPPED #54 (NEW PAGE, PassRole gate VERIFIED two-sided): aws-budgets-privesc/README.md. CreateBudgetAction APPLY_IAM_POLICY/APPLY_SCP_POLICY/RUN_SSM_DOCUMENTS + iam:PassRole -> self-attach admin / org SCP / SSM code-exec via ExecutionRoleArn. Execution timing-gated (Standby->Pending on budget eval). Commit 346ff079c; PR #413 bullet.
- Found via all-services Create*/Update* role-passing sweep. Filtered out variant-op noise (sagemaker 21 ops, comprehend/transcribe covered by aws-ml-dataaccess-passrole-privesc). Budgets = genuine net-new (only defensive coverage existed).
- Parked from same sweep for later: kendra (post-exploit only, CreateIndex+PassRole), amplify computeRoleArn, proton (EOL) cross-account connection, ecs ExpressGatewayService (new), guardduty CreateMalwareProtectionPlan.
