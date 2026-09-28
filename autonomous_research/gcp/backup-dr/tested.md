# Backup and DR post-exploitation audit

## 2026-09-28 - documentation, CLI, schema, role, and taxonomy review

No cloud resource, IAM policy, backup, restore, VM, cluster, or directory object was created or
changed. The audit used current official documentation, generated audit-method tables, Google Cloud
IAM role descriptions, and local Google Cloud CLI 586.0.0 help. No cleanup was required.

### Retained techniques

- **Vaulted Compute restore:** retained as a bounded data-recovery/exfiltration primitive. The
  caller needs `backupdr.bvbackups.restore` on the backup and
  `backupdr.compute.restoreFromBackupVault` on the target. The target must be allowed by the vault's
  permanent access restriction, and the vault service agent needs its documented target-project
  operator/network/KMS grants. Impact is limited to the selected recovery point and data available
  in the resulting VM/disks.
- **Backup for GKE Secrets/PV restore:** retained because `--include-secrets` lets the service agent
  capture Secret objects without the caller holding source-cluster Kubernetes RBAC, then restore
  them into an attacker-accessible cluster. The caller needs both the backup and restore permission
  halves and separate target-cluster access. PV contents additionally require
  `--volume-data-restore-policy=restore-volume-data-from-backup`; the CLI default would provision or
  bind volumes without restoring their backed-up contents. Cross-project use requires preconfigured
  channels and reciprocal service-agent grants.

### Removed or folded claims

- Backup/vault/plan/association deletion and CMEK destruction are destructive-only anti-recovery;
  they are not post-exploitation credential/data access techniques.
- The earlier claim that a vault's access restriction could be loosened before restore was false.
  Current documentation says the access-restriction choice is permanent.
- Backup-plan association ingest into an attacker vault was removed as a standalone
  `backupUser` exfiltration claim. Cross-project backup also requires the foreign vault service
  agent to hold the workload-specific operator role in the victim project; a caller with only
  `roles/backupdr.backupUser` cannot install that grant. In same-project scenarios the ability to
  create/own a vault and plan already implies broader authority, so the prior presentation
  materially understated prerequisites.
- `roles/backupdr.computeEngineOperator` contains the generic
  create-VM/attach-SA permission combination already documented in the Compute privilege-escalation
  page. It was removed here rather than duplicated. No service-specific confused-deputy invocation
  that lets an ordinary caller arbitrarily exercise every service-agent permission was established.
- Backup for GKE delete operations are destructive-only. Plan-resource IAM writes are generic
  persistence/privesc, not part of the retained Secret/PV recovery chain.

### Telemetry corrections

- `google.cloud.backupdr.v1.BackupDR.RestoreBackup` is an Admin Activity `ADMIN_WRITE` LRO and is on
  by default. `ListBackups` is Data Access `ADMIN_READ` and is off by default.
- Backup for GKE `CreateBackupPlan`, `CreateBackup`, `CreateRestorePlan`, and `CreateRestore` are
  Admin Activity `ADMIN_WRITE` LROs and are on by default. `Operations.GetOperation` is Data Access
  `ADMIN_READ` and is off by default. The CLI's `--wait-for-completion` loops also call `GetBackup`
  and `GetRestore`, which are Data Access `ADMIN_READ` and off by default.
- The book no longer claims that service-agent Secret extraction has no telemetry. Source/target
  cluster audit and platform logs are configuration-dependent and separate from the exact Backup
  for GKE control-plane audit methods listed in the table.

### Local verification

- Confirmed the required `--name`, `--backup-vault`, `--data-source`, `--target-project`, and
  `--target-zone` arguments for `gcloud backup-dr backups restore compute`.
- Confirmed Backup for GKE plan, backup, restore-plan, and restore command syntax with local beta
  help. Confirmed that the restore-plan default is `no-volume-data-restoration`, and added the
  explicit restore-from-backup policy required by the documented PV-content impact.
- Confirmed from the generated audit-method table and local CLI polling source that `CreateRestore`
  evaluates `gkebackup.backups.get` as well as `gkebackup.restores.create`, and that the shown
  waiting commands require `gkebackup.operations.get`, `gkebackup.backups.get`, and
  `gkebackup.restores.get` as applicable.
- Confirmed current role contents using `gcloud iam roles describe` for Backup and DR restore/admin
  roles, Backup for GKE backup/restore/admin roles, and basic Editor.
