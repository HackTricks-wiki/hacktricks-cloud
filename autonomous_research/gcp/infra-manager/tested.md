# Infrastructure Manager — tested

## 2026-09-28 privilege-escalation audit

Documentation/local-CLI audit; no deployment, build, bucket, IAM policy, or state was accessed or changed.

- Retained the documented selected-service-account Terraform execution boundary: `config.deployments.create` plus `iam.serviceAccounts.actAs`.
- Verified current `gcloud infra-manager deployments apply` Git-source and service-account flags and current predefined-role contents.
- Added the run-as account's `roles/config.agent`, downstream permission, and cross-project prerequisites.
- Removed unrelated state disclosure, import-state poisoning, lock/DoS, and deployment-policy self-grant material.
- Corrected the false claim that Terraform actions have no Cloud Audit event; target services log calls under their own audit contracts.
