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
- [ ] ssm-quicksetup UpdateConfigurationDefinition (LocalDeploymentAdministrationRoleArn/ExecutionRoleName): deploys via CloudFormation StackSets org-wide. LIKELY subsumed by aws-cloudformation-privesc StackSets coverage — QuickSetup is a wrapper. Check if it adds a distinct org-wide-deploy path (mgmt/delegated-admin gated) worth a note on the control-tower/cfn pages.
- [ ] snowball CreateJob/CreateCluster (RoleARN): EXPORT job reads S3 as role onto a PHYSICAL device shipped to an address -> slow physical exfil. Distinctive but device-gated.
- [ ] resource-groups StartTagSyncTask (RoleArn): tag-sync assumes a role to manage group membership by tag -> ABAC angle. Niche.
- [ ] observabilityadmin CreateS3TableIntegration (RoleArn): telemetry -> S3 tables as role. New/niche.
- [ ] iot-managed-integrations CreateDestination (RoleArn); backup-gateway PutHypervisorPropertyMappings (IamRoleArn); repostspace CreateSpace (roleArn); support-app CreateSlackChannelConfiguration (channelRoleArn); license-manager CreateToken (RoleArns); application-autoscaling RegisterScalableTarget (RoleARN, legacy custom-resource scaling); marketplacecommerceanalytics StartSupportDataExport (roleNameArn, seller-only export); bcm-dashboards UpdateScheduledReport (report export role); arc-region-switch associatedAlarms/triggers crossAccountRole (covered on the new page).
