# Backup and DR post-exploitation audit

## 2026-10-04 - Preview auto-protection policy authorization

### Live result

- Created an empty one-day backup vault and two compatible one-day Compute Disk backup plans in
  `us-central1`. The policy used the deliberately absent label `htautoprot=nevermatch1004`; no
  Compute fixture was created, no resource matched, and no backup-plan association, data source or
  recovery point was produced.
- A reduced service account successfully created the policy with exactly
  `backupdr.autoProtectionPolicies.create`, `backupdr.backupPlans.useForComputeDisk`, and Service
  Usage Consumer. The active policy referenced the expected plan and label selector.
- With `backupdr.autoProtectionBindings.create` but without
  `backupdr.appliedAutoProtectionPolicies.authorize`, binding creation failed on the latter
  permission in the workload project. Adding that one permission and waiting for Backup and DR's
  authorization cache made the identical request succeed. The applied-policy view became `ACTIVE`
  while matching-resource and association inventories remained empty.
- Changed the caller to hold `backupdr.autoProtectionPolicies.update` but not
  `backupdr.backupPlans.useForComputeDisk`. A `backupPlanDetails` PATCH targeting the second plan
  failed on the missing `useForComputeDisk` permission. Restoring that permission made the same
  PATCH succeed after propagation. This rejects both private-first missing-authorization leads.
- Deleting the disposable caller after policy creation did not remove the policy or binding. This
  confirms the useful expected behavior: the service-managed policy is not tied to the creator's
  continuing credentials. It does not prove data disclosure by itself; listing/restoring completed
  backups and all vault, encryption and restore-target boundaries remain separate prerequisites.

### Permission and documentation correction

- The live API, generated audit catalog and current predefined roles use
  `backupdr.autoProtectionBindings.create|delete|get|list`. The auto-protection tutorial currently
  prints the stale `backupdr.autoProtectionPolicyBindings.*` spelling in its granular-permission
  table. Book examples and minimum-permission statements use the live permission names.
- `roles/backupdr.editor`, `roles/backupdr.admin`, and basic `roles/editor` currently include policy
  create/update/delete, binding create/delete, workload authorization and both Compute resource
  `useFor...` permissions. `roles/backupdr.viewer` contains only the relevant read permissions.
- Cross-project protection is still bounded by the foreign backup-vault service agent's documented
  `roles/backupdr.computeEngineOperator` or `roles/backupdr.diskOperator` grant in the workload
  project. The same-project control did not attempt to generalize around this prerequisite.

### Telemetry

- Successful policy creation emitted always-on Admin Activity under
  `google.cloud.backupdr.v1beta.BackupDR.CreateAutoProtectionPolicy`, with authorization rows for
  both policy create and `backupdr.backupPlans.useForComputeDisk`. The LRO produced start and
  completion records.
- Binding denial and success emitted the documented v1beta method plus an additional
  `google.cloud.backupdr.v1.BackupDR.CreateAutoProtectionPolicyBinding` authorization entry. The
  denial isolated `backupdr.appliedAutoProtectionPolicies.authorize`; the successful front-end entry
  recorded both binding create and workload authorization.
- The rejected and accepted plan-target changes used
  `google.cloud.backupdr.v1beta.BackupDR.UpdateAutoProtectionPolicy`. The denied record explicitly
  showed `autoProtectionPolicies.update` granted and `backupPlans.useForComputeDisk` denied on the
  new plan.
- Policy, binding, matching-resource and applied-policy reads are Data Access `ADMIN_READ` and off
  by default. Downstream resource enrollment would create an Admin Activity
  `CreateBackupPlanAssociation` LRO, but the guaranteed no-match fixture generated none.

### Teardown state

- Issued the supported binding delete and observed both the source binding and applied policy move
  through `DELETION_INITIATED` before returning `404`. Google documents removal as normally taking
  up to two hours and sometimes eight hours; this no-match fixture cleared in about 17 minutes.
- After that dependency cleared, deleted the policy, both plans and empty vault. Removed the caller
  key/account, every test binding, both active custom roles, the generated Backup and DR
  service-agent project grant and the isolated local configuration. Disabled Backup and DR back to
  its original state. Final API, IAM, service-account, Cloud Asset, config and named-resource checks
  found no active test residue; Compute remained at its enabled baseline.

## 2026-09-28 - documentation, CLI, schema, role, and taxonomy review

No cloud resource, IAM policy, backup, restore, VM, cluster, or directory object was created or changed. The audit used current official documentation, generated audit-method tables, Google Cloud IAM role descriptions, and local Google Cloud CLI 586.0.0 help. No cleanup was required.

### Retained techniques

- **Vaulted Compute restore:** retained as a bounded data-recovery/exfiltration primitive. The caller needs `backupdr.bvbackups.restore` on the backup and `backupdr.compute.restoreFromBackupVault` on the target. The target must be allowed by the vault's permanent access restriction, and the vault service agent needs its documented target-project operator/network/KMS grants. Impact is limited to the selected recovery point and data available in the resulting VM/disks.
- **Backup for GKE Secrets/PV restore:** retained because `--include-secrets` lets the service agent capture Secret objects without the caller holding source-cluster Kubernetes RBAC, then restore them into an attacker-accessible cluster. The caller needs both the backup and restore permission halves and separate target-cluster access. PV contents additionally require `--volume-data-restore-policy=restore-volume-data-from-backup`; the CLI default would provision or bind volumes without restoring their backed-up contents. Cross-project use requires preconfigured channels and reciprocal service-agent grants.

### Removed or folded claims

- Backup/vault/plan/association deletion and CMEK destruction are destructive-only anti-recovery; they are not post-exploitation credential/data access techniques.
- The earlier claim that a vault's access restriction could be loosened before restore was false. Current documentation says the access-restriction choice is permanent.
- Backup-plan association ingest into an attacker vault was removed as a standalone `backupUser` exfiltration claim. Cross-project backup also requires the foreign vault service agent to hold the workload-specific operator role in the victim project; a caller with only `roles/backupdr.backupUser` cannot install that grant. In same-project scenarios the ability to create/own a vault and plan already implies broader authority, so the prior presentation materially understated prerequisites.
- `roles/backupdr.computeEngineOperator` contains the generic create-VM/attach-SA permission combination already documented in the Compute privilege-escalation page. It was removed here rather than duplicated. No service-specific confused-deputy invocation that lets an ordinary caller arbitrarily exercise every service-agent permission was established.
- Backup for GKE delete operations are destructive-only. Plan-resource IAM writes are generic persistence/privesc, not part of the retained Secret/PV recovery chain.

### Telemetry corrections

- `google.cloud.backupdr.v1.BackupDR.RestoreBackup` is an Admin Activity `ADMIN_WRITE` LRO and is on by default. `ListBackups` is Data Access `ADMIN_READ` and is off by default.
- Backup for GKE `CreateBackupPlan`, `CreateBackup`, `CreateRestorePlan`, and `CreateRestore` are Admin Activity `ADMIN_WRITE` LROs and are on by default. `Operations.GetOperation` is Data Access `ADMIN_READ` and is off by default. The CLI's `--wait-for-completion` loops also call `GetBackup` and `GetRestore`, which are Data Access `ADMIN_READ` and off by default.
- The book no longer claims that service-agent Secret extraction has no telemetry. Source/target cluster audit and platform logs are configuration-dependent and separate from the exact Backup for GKE control-plane audit methods listed in the table.

### Local verification

- Confirmed the required `--name`, `--backup-vault`, `--data-source`, `--target-project`, and `--target-zone` arguments for `gcloud backup-dr backups restore compute`.
- Confirmed Backup for GKE plan, backup, restore-plan, and restore command syntax with local beta help. Confirmed that the restore-plan default is `no-volume-data-restoration`, and added the explicit restore-from-backup policy required by the documented PV-content impact.
- Confirmed from the generated audit-method table and local CLI polling source that `CreateRestore` evaluates `gkebackup.backups.get` as well as `gkebackup.restores.create`, and that the shown waiting commands require `gkebackup.operations.get`, `gkebackup.backups.get`, and `gkebackup.restores.get` as applicable.
- Confirmed current role contents using `gcloud iam roles describe` for Backup and DR restore/admin roles, Backup for GKE backup/restore/admin roles, and basic Editor.
