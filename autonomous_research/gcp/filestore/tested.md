# Filestore post-exploitation audit

## 2026-09-28 - official documentation and local CLI/source review

Scope: every H3 in `gcp-post-exploitation/gcp-filestore-post-exploitation.md`. The review used
current official Filestore access-control, mount, backup/restore, IAM-role, REST, and audit-method
documentation plus local Google Cloud CLI 586.0.0 help/source.

No Filestore instance, backup, snapshot, network, mount, IAM policy, or other cloud resource was
created, changed, mounted, or deleted. No cleanup was necessary. A read-only
`gcloud iam roles describe roles/file.editor` call confirmed the current predefined-role permission
set; it made no mutation.

### Retained results

- **Mount a reachable share:** no Filestore IAM check exists on NFS I/O. The boundary is client mount
  privilege, route/firewall, export source range, security flavor, and POSIX identity/permissions.
  Filestore publishes no data-plane audit methods, so this is High stealth unless optional network
  or endpoint telemetry exists.
- **Widen NFS exports:** raw `UpdateInstance` needs `file.instances.update`. Current GA `gcloud`
  first calls `GetInstance`, and synchronous mode polls with `file.operations.get`; `--async` avoids
  polling but not the helper read. The write is a default-on Admin Activity LRO, so stealth is Low.
- **Clone through a standard backup:** `file.backups.create`, `file.backups.useReadOnly`, and
  `file.instances.create` produce a separate, mountable point-in-time copy without overwriting the
  live share. `file.operations.get` is needed only for synchronous CLI polling. Both create methods
  are default-on Admin Activity LROs; clone reads have no Filestore data-plane audit.

### Corrected or removed claims

- Folded "restore a backup" and "create a backup and restore it" into the same clone primitive.
  The supported non-destructive command is `instances create` with `source-backup`; the prior
  `instances restore` command targets an existing share and overwrites it.
- Removed the DoS/anti-recovery H3. In-place restore, revert, protection disablement, and deletion are
  destructive availability/recovery actions and fail the no-garbage bar for this post-exploitation
  page even though their Admin Activity methods are real.
- Removed the published cross-project exfil assertion. The current role catalog contains
  `file.instances.createCrossProjectBackup` and current instance-create help exposes
  `source-backup-project`, but the standard backup command constructs the source instance in its
  configured project and official public guidance does not establish the claimed end-to-end attack
  or its exact secondary checks. This remains a live-validation candidate, not a book claim.
- Removed `anon_uid` / `anon_gid` from `NO_ROOT_SQUASH`; current CLI help and API schema allow those
  fields only with `ROOT_SQUASH`.
- Bounded mount/update impact by NFS export, security flavor, UID/GID, POSIX, network, and share
  scope instead of claiming unconditional access to all data.

### Audit classifications retained

- `GetInstance` and `google.longrunning.Operations.GetOperation`: Data Access `ADMIN_READ`, disabled
  by default.
- `UpdateInstance`, `CreateBackup`, and `CreateInstance`: Admin Activity `ADMIN_WRITE`, enabled by
  default; all are LROs and usually emit start/completion records.
- NFS mount and file I/O: no Filestore data-plane Cloud Audit method.

## 2026-09-28 reciprocal review

- Corrected the mount prerequisites and examples to distinguish NFSv3 RPC/NLM ports and
  `showmount` from the NFSv4.1 TCP/2049, FQDN, version, and security-flavor path.
- Corrected the clone sequencing: an asynchronous backup cannot immediately seed a clone, and an
  asynchronous clone cannot immediately be mounted. The working example now waits for both LROs,
  records `file.operations.get`, and uses `file.instances.get` to discover the completed clone IP.
- Added explicit source-location flag and same-protocol restoration boundaries. Review remained
  documentation/local-CLI only; no resource or API was accessed or changed.
