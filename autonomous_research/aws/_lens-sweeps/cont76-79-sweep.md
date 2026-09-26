# Lens sweeps — cont.76–79 (2026-09-25)

## SHIPPED this arc
- #51 Batch RegisterJobDefinition + iam:PassRole (verified) — batch-privesc.
- #52 Bedrock AgentCore NEW PAGE (CreateAgentRuntime/CreateCodeInterpreter+PassRole verified; vend chain + repoint doc) — bedrock-agentcore-privesc.
- #53 SES PutIdentityPolicy cross-account sending-auth (doc+partial-verify) — ses-post-exploitation.
- #54 Budgets CreateBudgetAction + iam:PassRole NEW PAGE (PassRole gate verified two-sided) — budgets-privesc.

## Comprehensive sweeps run (methods reusable)
1. All-services credential-vend op sweep (Get*Credential/*Token/vend) vs wiki -> surfaced Bedrock AgentCore (shipped). Others: finspace-data GetProgrammaticAccessCredentials, emr-containers GetManagedEndpointSessionCredentials (parked), codecatalyst/route53globalresolver CreateAccessToken (niche PAT), workmail PATs (niche).
2. All-services resource-policy setter sweep (Put*Policy/Add*Permission) vs cross-account matrix -> SES PutIdentityPolicy (shipped). Parked: s3control:PutMultiRegionAccessPointPolicy (MRAP cross-account), signer:AddProfilePermission (code-signing cross-account supply-chain), waf*/PutPermissionPolicy (rulegroup share, low), mediastore PutContainerPolicy (EOL).
3. All-services Create*/Update*/Run*/Start*/Register* role-field sweep vs wiki -> Budgets CreateBudgetAction (shipped). Filtered variant-op noise: sagemaker(21 ops, canonical covered), comprehend/transcribe/comprehendmedical (covered by aws-ml-dataaccess-passrole-privesc), glue/eks/dms/ecs (covered). 

## Parked genuine candidates (verify/ship in a future cycle)
- kendra: post-exploit page only, NO privesc page. CreateIndex/CreateDataSource + RoleArn (Kendra reads data sources as passed role). Niche service, moderate value.
- ecs: CreateExpressGatewayService / RegisterDaemonTaskDefinition (new ECS ops, executionRole/taskRole/infrastructureRole) — ECS task-role PassRole covered by concept; confirm these variants mentioned.
- guardduty: CreateMalwareProtectionPlan + Role — passes a role for S3 malware scanning; low privesc value.
- amplify: CreateBranch computeRoleArn (SSR compute role) / CreateDomainAssociation autoSubDomainIAMRole — Amplify hosting; check if amplify privesc exists.
- proton: CreateEnvironmentAccountConnection cross-account roles — Proton is EOL-announced; skip.
- neptunedata: CreateMLEndpoint (sagemaker+neptune roles) — niche.

## Saturated lenses (confirmed, do not re-tread)
- Repoint (Update*+PassRole): Lambda, EKS, Glue, CodeBuild, Step Functions, CodePipeline, MWAA, AgentCore.
- Compute-exec+PassRole: Lambda, ECS, Batch, Glue, SageMaker(ML), MWAA(serverless+classic), Bedrock AgentCore, Step Functions, CodeBuild, EMR(+serverless/on-EKS).
- EventBridge family: Scheduler, Pipes, EventBridge (rules/targets) — privesc+persistence+post-exploit+enum all present.
- Snapshot/backup cross-account exfil; IAM cred-generation; sts:AssumeRoot/root-cred-mgmt; identity-provider backdoors (IAM SAML/OIDC, Cognito IdP, Identity Center TTI).
- Credential-disclosure calibration: control-plane Describe/Get REDACT secrets (return Secrets Manager ARNs); only purpose-built data-plane vend APIs return plaintext (confirmed again on AgentCore).

## cont.80 addendum — arc results + definitive catalogs (2026-09-25)
SHIPPED this arc:
- #55 AppFlow CreateFlow attacker-defined transfer (aws-appflow-enum.md) — VERIFIED live S3->S3 exfil.
- Signer AddProfilePermission — cross-account matrix row 53 upgraded to Verified (real external acct accepted; StartSigningJob --profile-owner signs under victim trusted profile).
- EMR on EKS GetManagedEndpointSessionCredentials + PassRole (aws-emr-serverless-privesc) — interactive-endpoint session as execution role (doc-grounded; PassRole class already verified).

DEFINITIVE CATALOGS (do NOT re-vet these service sets in future cycles):
- aws-ml-dataaccess-passrole-privesc/README.md = ~40-service PassRole confused-deputy catalog. Two tables: ML/data-access-role jobs (Comprehend/Transcribe/Translate/Textract/HealthLake/Personalize/Omics/Neptune/DataBrew/QBusiness/CleanRoomsML...) + execution-role long tail (Braket/Deadline/MSKConnect/m2/Panorama/SimSpaceWeaver/DeviceFarm/OSIS/EntityResolution/Timestream/BackupSearch/DAX/Grafana/PCS/AIOps/Chime/MediaPackageVOD). High-value standalone compute has dedicated pages (EMR/SageMaker/Glue/Bedrock/Batch/AppRunner/CodeBuild/Pipes/Proton/CloudControl/AgentCore/Budgets).
- resource-policy-and-shared-resource-attacks.md = ~65-row cross-account resource-policy/share matrix (most rows Verified). Covers every Put*Policy/Add*Permission/Share* class swept.

Remaining parked (all marginal / covered-by-generic-table): ecs CreateExpressGatewayService (ECS task/exec-role PassRole already generic), guardduty CreateMalwareProtectionPlan (low value), amplify computeRoleArn (hosting SSR, low), s3control MRAP policy (MRAP policy alone != data access; both MRAP+bucket policy required -> weak), finspace-data GetProgrammaticAccessCredentials (niche service).

VERDICT: AWS privesc/post-expl/persistence + cross-account lenses are at deep saturation. Net-new frontier now requires either brand-new AWS services at GA or novel mechanism classes; continue monitoring new service launches (AgentCore/AppFlow-class discoveries) rather than re-vetting the covered surface.
