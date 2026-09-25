# cont.81 gap-analysis (botocore 423 services vs wiki) — 2026-09-25
Method: diff all botocore service dirs against lowercased AWS wiki corpus (see [[aws-wiki-gap-analysis-method]]).

## SHIPPED
- mediaconvert:CreateJob + iam:PassRole -> ml-dataaccess table (verified two-sided).

## Confirmed ZERO wiki mention — vet next cycles (real candidates)
- [ ] opensearchserverless: collections gated by DATA ACCESS POLICIES (not IAM resource policy) + network/encryption policies. aoss:CreateAccessPolicy / CreateSecurityPolicy could grant over-broad/attacker principal data access to collections (Serverless has its OWN authz model distinct from managed OpenSearch which IS covered). HIGH interest.
- [ ] eks-auth:AssumeRoleForPodIdentity — EKS Pod Identity credential vend: exchanges a pod's k8s SA token for the associated IAM role creds. Data-plane vend. Check if EKS pages cover pod-identity association abuse (CreatePodIdentityAssociation + PassRole) and this vend.
- [ ] bedrock-data-automation / bedrock-data-automation-runtime: processes docs/media via projects with a role; CreateDataAutomationProject role-passing? new service.
- [ ] groundstation: MissionProfile / DataflowEndpointGroup with roleArn; niche (satellite), low prevalence.
- [ ] mwaa-serverless: new serverless Airflow; MWAA classic exhaustively covered — check if serverless CreateEnvironment role-passing differs.

## False-positive / already-covered (no substring but covered by pattern/other name)
- kafkaconnect/osis/panorama/braket/mediapackage-vod/cleanroomsml/migration-hub-refactor-spaces -> in ml-dataaccess table or cross-account matrix already.
- cloud9 (deprecated, no new customers), outposts (hw), importexport/mturk/machinelearning (legacy), marketplace* (mostly read), *-data/*-runtime/*-query data-plane variants of covered services.
