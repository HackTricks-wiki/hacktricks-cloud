# AWS audit — status

Last updated: 2026-09-26

## Active 2026-09-26 checkpoint

Research remains active. The September 24 saturation table below records that specific sweep, not completion of AWS research. Recent changes pushed to PR #413 include Account Access Manager role entitlement assignment, Sign-In account and organization console-denial paths, Lambda full-resource-policy code-update escalation, RAM share retention on organization departure, current Organizations departure controls, and stealth/CloudTrail corrections across IAM, Identity Center, Lambda, and Organizations pages. Each tested service has a per-service ledger with prerequisites, negative branches, and cleanup results.

Current next checks: Sign-In network enforcement only in a disposable account; Identity Center applications-only instance effects; resource-share acceptance and retention without moving a production account; broader 2026 IAM/service action coverage. Do not publish unexpected security-impact candidates until separately validated and written in the local private AWS report folder.

## 2026-09-24 sweep checkpoint (historical)

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

## cont.80 (2026-09-25)
- Saturation re-confirmed: EventBridge family, SSM CreateActivation (ssm+ecs pages), DataSync/Transfer/FIS/IoT/GameLift privesc, Kendra CreateDataSource+PassRole — all covered.
- SHIPPED #55: AWS AppFlow CreateFlow attacker-defined transfer (aws-appflow-enum.md). Verified live S3->S3 exfil end-to-end; UpdateFlow endpoint-immutability verified; SaaS-connector-profile source doc-grounded. No PassRole (service-linked + connector authority). Residue zero.
- Lens-sweep log cont.76-79 written (parked: s3control MRAP policy, signer AddProfilePermission, finspace-data/emr-containers cred-vends).

## 2026-09-26 Lambda full-policy follow-up
- VERIFIED end-to-end with a least-privilege disposable IAM user: the documented three
  policy-management permissions work when scoped to one exact function ARN; a PutResourcePolicy
  attempt against a different ARN was denied.
- The same user was denied Invoke before the full policy and received a successful `200` invocation
  after the resource policy granted `lambda:InvokeFunction`, despite never having an identity-based
  invoke allow.
- Teardown verified: function, execution role, IAM user, inline policy, access key, and temporary SDK
  environment are absent. Zero persistent residue.

## 2026-09-26 S3 Access Grants canonicalization test
- NEGATIVE / secure behavior: a 24-case `GetDataAccess` matrix did not escape an `allowed/*` grant
  into a sibling `denied/*` object. Accepted dot/encoding strings were scoped literally under
  `Minimal`; `Default` stayed at the matching `allowed/*` grant. Other variants were denied or
  rejected as invalid.
- This is research-ledger-only, not public-book content. Full result:
  `s3/access-grants-canonicalization-2026-09-26.md`.
- Two test cycles fully torn down; Access Grants instance, bucket, objects, IAM user/key/policy, and
  location role/policy all verified absent.

## Saturation update (cont.81) — AgentCore Harness direct shell
- SHIPPED #56 (VERIFIED end to end, two-sided): `CreateHarness` + exact-role `iam:PassRole` +
  `InvokeAgentRuntimeCommand` produced UID 0 and the target execution-role STS ARN. The no-PassRole
  principal was explicitly denied. Added enumeration, impact, working boto3 call, logs table, and
  stealth rating to the AgentCore privesc page; also filled the missing stealth ratings on its four
  existing techniques.
- Composite-create dependency discovery recorded extra live gates (`CreateAgentRuntimeEndpoint`,
  `CreateWorkloadIdentity`, `GetAgentRuntime`) and the first-use Runtime Identity service-linked role.
  Full harness ARN is the working command target; generated runtime ARN and short harness ID are not.
- CloudTrail Event History verified `CreateHarness` request/response logging and exact PassRole denial.
  Runtime command telemetry attempted `logs:PutLogEvents` under the execution role; without that
  permission the command still succeeded while CloudWatch export failed.
- Teardown verified: harness, generated managed resources, both IAM users/keys/policies, execution
  role, and Runtime Identity service-linked role all absent; deletion task `SUCCEEDED`.

## Saturation update (cont.82) — CloudWatch Logs scheduled queries
- SHIPPED #57 (VERIFIED end to end, both role gates isolated): `logs:CreateScheduledQuery` plus
  `iam:PassRole` on a query execution role and a separate S3 delivery role repeatedly queries log
  groups the creator cannot read and exports selected rows to S3. No-PassRole denied on the delivery
  role first; delivery-only PassRole then denied on the execution role; both exact roles with
  `iam:PassedToService=logs.amazonaws.com` succeeded.
- One synthetic marker was delivered as JSON at the next minute boundary. Added the detailed technique
  to `aws-cloudwatch-enum.md` and a verified row to the analytics/data-access PassRole matrix.
- CloudTrail verified `CreateScheduledQuery`, automatic `StartQuery`, and automatic `GetQueryResults`
  as default management events. Creation logs the full query, groups, schedule, bucket URI/owner, and
  both roles; executions are attributed to `assumed-role/<execution-role>/Logs` with
  `invokedBy=logs.amazonaws.com`.
- Teardown verified zero scheduled queries, bucket/object, log group, IAM users/keys/policies, or roles.

## cont.83 (2026-09-26) — Step Functions callback-token boundary audit
- NEGATIVE / secure boundary: two isolated Activity cycles verified that callback tokens stayed bound to
  their original execution and Region; mutation, terminal replay, and expired-token use did not alter a
  live or closed execution. Exact matrix: `step-functions/callback-token-binding-2026-09-26.md`.
- Two non-security quirks retained for regression: immediate post-success heartbeat replay briefly returned
  HTTP 200 before converging to `TaskTimedOut`; a one-character token mutation consistently returned
  `InternalFailure` and generated SDK retries instead of the documented `InvalidToken`. Neither crossed a
  boundary or changed state, so no AWS vulnerability report and no standalone public attack technique.
- Minimum IAM clarification queued in the public callback technique: `SendTask*` has no resource type and
  therefore needs `Resource: "*"`; only `GetActivityTask` can be scoped to the Activity ARN.
- Both test cycles torn down. Independent checks found zero matching Activities and IAM roles; deleted state
  machines entered the service's asynchronous `DELETING` state.

## cont.84 (2026-09-26) — Step Functions dynamic HTTP Task credential capture
- SHIPPED #58 (VERIFIED end to end): `states:StartExecution` alone redirected a fixed EventBridge
  Connection's API-key header to an account-owned HTTPS collector because the existing workflow sourced
  `ApiEndpoint` from execution input. The restricted caller's `DescribeStateMachine` was denied and it had
  no EventBridge, Secrets Manager, update, or PassRole access.
- The execution role needed `states:InvokeHTTPEndpoint` on the exact state-machine ARN,
  `events:RetrieveConnectionCredentials` on the connection, and Get/Describe on its managed secret. A
  twenty-second IAM propagation wait was needed; early five-second attempts failed closed.
- CloudTrail showed `StartExecution` with redacted input and a service-driven `GetSecretValue` under the
  execution role naming the connection secret. The attacker endpoint remained absent without optional
  `InvokeHTTPEndpoint` state-machine data events or endpoint-side logs.
- Public StartExecution coverage now includes this high-value sink, minimum roles, impact, explicit stealth,
  logs, and the `states:HTTPEndpoint`/`states:HTTPMethod` mitigations.
- Five disposable cycles fully torn down; final inventory showed no matching state machine, Connection or
  generated secret, Lambda/Function URL, log group, or IAM role.

## cont.85 (2026-09-26) — TestState HTTP Connection oracle
- SHIPPED #59 (VERIFIED two-sided): `states:TestState` plus exact-role `iam:PassRole` executed an arbitrary
  HTTP Task and delivered an EventBridge Connection API key to the account-owned collector even with
  `inspectionLevel=INFO` and `revealSecrets=false`.
- `TestState` alone was denied specifically on PassRole. The positive caller had no `states:RevealSecrets`,
  EventBridge, Secrets Manager, Lambda, logs, or state-machine CRUD permission. The passed role's endpoint
  action was conditioned to the exact collector URL/method.
- Added the Connection-specific path, minimum caller/passed-role permissions, impact, stealth, and expanded
  logging table to the existing Step Functions TestState+PassRole privesc technique.
- Combined fixture torn down and independently verified absent: state machine/execution, Connection/generated
  secret, Lambda/Function URL, log group, all four roles, and policies.

## cont.86 (2026-09-26) — S3 Tables replication
- SHIPPED #60 (VERIFIED end to end, two-sided): `s3tables:PutTableBucketReplication` plus exact-role
  `iam:PassRole` configured continuous bucket-level table replication. Put without PassRole was denied on
  the exact role; initial Put with PassRole succeeded without Get and returned the version token.
- Bucket-level behavior was confirmed across destination replacement: an existing table was created in the
  new destination while its old replica remained, and a later source table appeared only in the active
  destination. Deleting the configuration likewise retained both destinations' replicas.
- Existing-rule replacement and deletion failed closed without the current version token. A caller that
  retained the token from its own previous write needed no Get permission. Empty/no-snapshot tables remained
  `pending`, so committed data-copy fidelity is explicitly doc-grounded rather than overclaimed as live-tested.
- CloudTrail recorded replication APIs as default management events, but successful Put omitted the entire
  configuration, replication-role ARN, and destination ARN. Service-driven `CreateNamespace`/`CreateTable`
  events exposed destination identifiers under the replication role.
- Four disposable cycles were cleaned; final inventory found no matching table bucket or IAM role. Cross-account
  policy setup is documented but was not live-tested without a second explicitly authorized account.

## cont.87 (2026-09-26) — Transfer Family custom IdP takeover and password exposure
- SHIPPED #61 (VERIFIED two independent end-to-end paths): exact-server `transfer:UpdateServer` alone
  repointed a Lambda custom IdP, and exact-function `lambda:UpdateFunctionCode` alone poisoned the
  already-wired IdP. Each accepted an attacker login and a real SFTP session read both protected marker
  prefixes through the high S3 role returned at authentication. Neither restricted caller had PassRole,
  Lambda Invoke, direct S3, or logs-read permission; the updater could not even DescribeServer.
- SHIPPED #62 (VERIFIED exact synthetic canary): the Lambda IdP received the SFTP password in plaintext;
  after the handler intentionally logged its event, `logs:FilterLogEvents` recovered the exact value.
  Added a dedicated Transfer Family post-exploitation page and SUMMARY entry.
- Filled all four existing Transfer privesc techniques' missing explicit stealth ratings and added the
  omitted `UpdateAccess` role-choice variant.
- The `PUBLIC_KEY_AND_PASSWORD` matrix enforced both factors and IAM intersection. AWS uses the password
  response's role/policy/home when factor responses differ; malformed nonempty policies failed closed,
  password-response PublicKeys were rejected, and empty/omitted Policy intentionally used the base role.
  Because the trusted IdP already controls authorization, no independent security boundary was crossed;
  the result stays in the research ledger and no AWS vulnerability report was created.
- Five short endpoint cycles were deleted immediately, never merely stopped. Final independent inventory
  was empty for matching Transfer servers, Lambdas, IAM roles, S3 buckets, and log groups.

## cont.88 (2026-09-26) — API Gateway custom IdP takeover and test oracle
- SHIPPED #63 (VERIFIED end to end): exact-resource `apigateway:PATCH` on the Transfer IdP's GET/200
  integration response plus `apigateway:POST` on that REST API's deployment collection replaced the
  response template with an attacker-selected role/home. After deployment, a real password SFTP login
  read the protected S3 marker through that role. The caller had an explicit `iam:PassRole` deny and
  could not read the integration response.
- SHIPPED #64 (VERIFIED exact-user scope): `transfer:TestIdentityProvider` on one exact user ARN, with
  `DescribeServer` denied, disclosed the IdP-selected role, home, and API URL. Its caller-controlled
  `SourceIp` satisfied an IdP allow rule even though a real SFTP login from the actual IP failed; the
  action creates no session and is documented as post-exploitation recon/password-oracle behavior.
- CloudTrail later confirmed `UpdateIntegrationResponse` records the complete malicious template;
  `CreateDeployment` records API/stage/deployment; and `TestIdentityProvider` redacts the password but
  records the chosen source IP plus full IdP response. The latter appeared as `readOnly:false`.
- Two API Gateway test cycles were fully deleted in `finally`, including both Transfer servers, REST
  APIs, roles/policies, bucket/objects, and access credentials. Combined Transfer custom-IdP inventory
  remained empty; no server was left stopped or billable.

## cont.89 (2026-09-26) — S3 Express session boundary audit
- SHIPPED #65 (VERIFIED expected data-access behavior): expanded the existing S3 Express
  `s3express:CreateSession` broker coverage with exact-bucket/minimum IAM, `ReadOnly`/`ReadWrite`
  impact, High stealth, and an expandable CloudTrail table. Session issuance and object calls are
  optional S3 Express data events, not default Event History management events.
- NEGATIVE / secure boundary: an exact-bucket-A, `SessionMode=ReadOnly` caller read/listed A but
  could not write/delete, mint ReadWrite, mint for bucket B, or use its A tuple against B. Omitted
  mode fell back to ReadOnly as documented.
- Session credential fields were indivisible: mutation, cross-bucket splices, same-bucket ReadOnly /
  privileged-ReadWrite token splices, and even a splice between two same-scope ReadOnly sessions all
  failed closed. An intact tuple replayed before expiry; a freshly signed request after its returned
  five-minute expiration was denied.
- Raw REST required `x-amz-content-sha256` on the empty CreateSession GET. A session-authenticated
  HEAD against its own Zonal bucket returned 200 despite documentation preferring IAM credentials;
  the same tuple against bucket B returned 403, so this remains a compatibility note without security
  impact and no AWS vulnerability report.
- Three complete two-bucket cycles and two preliminary header-diagnostic cycles ran through `finally`.
  Every object, directory bucket, inline policy, and test role was deleted; independent inventory for
  the `ht-s3e-` prefix was empty.
