# NetApp Volumes — tested

## 2026-09-26 — post-exploitation permission and audit review
- Corrected the export-policy technique to NFS only. An NFS export can be opened to an
  attacker-reachable CIDR, but changing the export policy does not remove Active Directory
  authentication from SMB.
- Corrected recovery-point cloning to use `netapp.volumes.create` with `sourceSnapshot` or
  `sourceBackup`. The backup path also uses `netapp.backups.useReadOnly`; creating a new recovery
  point first needs `netapp.snapshots.create` or `netapp.backups.create`. The separate
  `netapp.volumes.restore` method performs file restore into a volume and is not the clone method.
- Corrected the audit classification of destructive calls. `DeleteVolume`, `DeleteSnapshot` and
  `DeleteBackup` are Data Access `DATA_WRITE` and disabled by default; `DeleteBackupVault` is
  always-on Admin Activity.
- Narrowed the ONTAP-mode technique to Google's documented filtered proxy. It has ONTAP
  administrator privilege for allowed command families, but it is not unrestricted cluster
  ownership and the documented allowlist does not establish that local ONTAP administrators can be
  created. Google says every proxy call is logged, while the public audit-method matrix does not
  yet publish an `ExecuteOntap*` method/category mapping.
- Removed the unverified claim that `activeDirectories.get/list` disclose the stored domain-join
  password. The API schema accepting a password on writes does not prove that reads return it, so
  this remains a private validation lead rather than a book technique.
- Read-only role inspection confirmed that `roles/netapp.admin` and basic Editor include the NetApp
  write permissions and `netapp.ontap.*`. `roles/netapp.viewer` and the misleadingly named
  `roles/netapp.editor` are read-only and include only `netapp.ontap.get`. The basic Viewer role,
  unlike `roles/netapp.viewer`, includes `netapp.backups.useReadOnly`.
- The NetApp API is disabled in the authorized lab. A read-only list request returned
  `SERVICE_DISABLED`; the API was not enabled and no storage pool, volume, backup or other resource
  was created.
