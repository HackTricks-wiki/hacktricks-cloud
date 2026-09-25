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
