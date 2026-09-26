# cont.82 reliable role-bearing scan of the 130 true-gap services (rg-based) — 2026-09-25
Method: for each botocore service with ZERO rg match under aws-security/, scan Create/Start/Update/Put/Register
ops whose input has a *role*arn* member. Full output in session log.

## SHIPPED this cycle
- arc-region-switch CreatePlan/UpdatePlan+PassRole -> NEW PAGE aws-region-switch-privesc (VERIFIED two-sided).
- finspace CreateKxCluster (executionRole) + CreateKxUser (iamRole) -> ml-dataaccess table row (doc-grounded).

## Already covered (in ml-dataaccess table / cross-account matrix) — from the scan, do NOT re-add
- chime-sdk-media-pipelines, cleanroomsml(cleanrooms-ml), backupsearch(backup-search), timestream-query(timestream).

## Legacy / EOL — skip
- machinelearning (Amazon ML, no new customers), iotthingsgraph (EOL).

## Niche parked candidates (low prevalence; vet only if a distinct primitive emerges)
- [x] ssm-quicksetup UpdateConfigurationDefinition (LocalDeploymentAdministrationRoleArn/ExecutionRoleName): reviewed 2026-09-26. Fixed AWS-owned configuration types and an explicit `iam:PassRole` dependency make this a constrained CloudFormation/StackSets wrapper, not arbitrary-template execution. The one arbitrary-policy-looking type, SSM Change Manager, is closed to new customers and creates a job-function invocation role rather than granting the updater permission to use it. Lab has no configuration managers or local Quick Setup deployment roles; onboarding would create persistent service/StackSet state. Reasoned exclusion recorded in `ssm-quicksetup/update-definition-2026-09-26.md`.
- [ ] snowball CreateJob/CreateCluster (RoleARN): EXPORT job reads S3 as role onto a PHYSICAL device shipped to an address -> slow physical exfil. Distinctive but device-gated.
- [x] resource-groups StartTagSyncTask (RoleArn): reviewed 2026-09-26. The task can only maintain AppRegistry membership by applying/removing the service-defined `awsApplication` tag; it cannot choose an arbitrary output tag or execute as the role. `iam:PassRole` is enforced and the documented role is limited to grouping plus tag/untag. No distinct privesc/ABAC primitive. See `resource-groups/tag-sync-role-2026-09-26.md`.
- [ ] observabilityadmin CreateS3TableIntegration (RoleArn): telemetry -> S3 tables as role. New/niche.
- [ ] iot-managed-integrations CreateDestination (RoleArn); backup-gateway PutHypervisorPropertyMappings (IamRoleArn); repostspace CreateSpace (roleArn); support-app CreateSlackChannelConfiguration (channelRoleArn); license-manager CreateToken (RoleArns); application-autoscaling RegisterScalableTarget (RoleARN, legacy custom-resource scaling); marketplacecommerceanalytics StartSupportDataExport (roleNameArn, seller-only export); bcm-dashboards UpdateScheduledReport (report export role); arc-region-switch associatedAlarms/triggers crossAccountRole (covered on the new page).

## cont.82b — resource-policy & credential-vend lenses over the SAME 130 gap services
Genuine signals (rest were pagination nextToken/ChangeToken/PaginationToken noise):

### Resource-policy / cross-account setters (all niche or legacy — parked)
- [ ] refactor-spaces:PutResourcePolicy (Migration Hub Refactor Spaces env share) — niche.
- [ ] mediatailor:PutChannelPolicy (cross-account channel access) — niche.
- [ ] cleanrooms-ml:PutConfiguredAudienceModelPolicy (audience-model share) — niche; cleanrooms-ml already partly covered.
- waf-regional:PutPermissionPolicy — WAF CLASSIC (legacy, superseded by wafv2). skip.
- resiliencehub/application-autoscaling/wisdom/mturk "policy" hits = NOT IAM/resource policies (RTO config, scaling, content guardrails, review policies). noise.

### Credential / token vend (Get/Create returning secrets)
- [ ] finspace-data:GetProgrammaticAccessCredentials + GetExternalDataViewAccessDetails -> plaintext `credentials`. Legacy FinSpace (Hydra dataset mgmt, being DEPRECATED by AWS). Was parked cont76-79. Low value now.
- [ ] codecatalyst:CreateAccessToken -> `secret` (PAT, up to ~1y). Real DEV-persistence primitive (survives SSO/session revocation) BUT CodeCatalyst auth = AWS Builder ID / SSO, not IAM roles -> outside IAM-privesc model, not lab-testable here. Note-worthy only.
- [ ] license-manager:CreateToken -> `Token` (long-lived refresh) + GetAccessToken -> `AccessToken`. Niche (license entitlement OIDC tokens).
- license-manager-linux-subscriptions:GetRegisteredSubscriptionProvider -> SecretArn (REDACTED ARN, needs secretsmanager:GetSecretValue). iotmanagedintegrations Get* -> SecretsManager/CredentialLockerId (ARN/ID, redacted). Per calibration [[aws-technique-audit-progress]] control-plane returns ARN not plaintext -> NOT a direct vend.

## CONCLUSION
The 130 true-gap services are now swept across all THREE high-value lenses (PassRole exec-role,
resource-policy/cross-account, credential-vend). Net-new shippable: arc-region-switch (done),
finspace kx (done). Everything else in the tail is niche/legacy/non-IAM — parked, not garbage-shipped.
Next productive lens should target WIKI-PRESENT services (deeper per-service audit) rather than the gap tail.
