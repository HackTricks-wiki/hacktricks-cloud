# Lens sweep — cont.75 (2026-09-25)

Systematic sweeps run this cycle and their verdicts (avoid re-treading).

## SHIPPED
- `sso-admin:CreateTrustedTokenIssuer` rogue TTI (identity-provider/IdP-backdoor lens) → see identity-center/tested.md. Commit c8980fe16.

## Confirmed already-covered (no action)
- Identity-provider backdoors: IAM SAML/OIDC create+update (iam-privesc/persistence), Cognito CreateIdentityProvider (cognito-privesc/persistence). Only TTI was the gap.
- S3 Access Grants (`s3control:CreateAccessGrant`/`GetDataAccess`) — aws-s3-privesc. VPC Lattice `PutAuthPolicy` — covered.
- Snapshot/backup cross-account exfil: EBS ModifySnapshotAttribute, AMI ModifyImageAttribute, RDS ModifyDBSnapshotAttribute + ModifyDBClusterSnapshotAttribute, DLM, DRS, Redshift, backup-vault PutBackupVaultAccessPolicy — all covered across post-exploitation + cross-account matrix.
- IAM credential-generation persistence: CreateServiceSpecificCredential / ResetServiceSpecificCredential / UploadSSHPublicKey / UploadSigningCertificate — iam-privesc + iam-post-exploitation + codestar.
- `sts:AssumeRoot` + EnableOrganizationsRootCredentialsManagement (centralized root; S3UnlockBucketPolicy/SQSUnlockQueuePolicy task policies) — sts-privesc, sts-persistence, organizations-privesc, basic-info. Current.

## Considered and REJECTED (below no-garbage bar / already-reasoned)
- `backup:StartCopyJob` cross-account copy — the aws-backup-post-exploitation page already reasons that cross-account is gated to `CopyIntoBackupVault` with org/vault/role/encryption prerequisites; not a clean external exfil. A dedicated section adds no distinct value.

## Parked NICHE candidates (low prevalence; verify only if a target uses the service)
- `finspace-data:GetProgrammaticAccessCredentials` — cred-vend to a FinSpace data environment (needs existing env+user). No wiki page for finspace. Low prevalence (financial kdb+ shops); expensive to lab.
- `finspace:CreateKxCluster` + iam:PassRole — pass a role to a kdb+ cluster; expensive.
- `cleanroomsml:CreateConfiguredModelAlgorithm`/`CreateTrainingDataset` + PassRole — run attacker container/algorithm as a passed role (code-exec+PassRole on Clean Rooms ML). Niche.
- `ssm-quicksetup:UpdateConfigurationDefinition` + role — Quick Setup deploys StackSets org-wide via a role; potential org-wide deployment privesc. Complex precondition (Quick Setup enabled).
- `iot:CreateAuthorizer` / `apigateway:CreateAuthorizer` — custom-authorizer auth bypass; app-scoped (not IAM privesc). Possible enum-page mention only.

## Botocore gap-analysis snapshot
- 423 botocore services; 123 with no token match in aws-security wiki (mostly billing/marketplace/geo/deprecated). Of those, only the niche parked set above have PassRole/cred-vend signal. No high-prevalence structural gap remains.
