# Cloud Sql — tested

Cloud SQL. Covered (clone/replica copy, flag anti-forensics, SSL downgrade;
persistence: sslCerts.create, contained-DB user, pg_cron / event_scheduler scheduled-task).

## SQL Server `sp_help_revlogin` hash export live verification (2026-09-28)

- Created two sequential bounded zonal `SQLSERVER_2022_EXPRESS` fixtures with two vCPUs, 3.75 GiB
  memory, 10 GiB storage, one-runner `/32` public allowlists, and backups, retained/final backups, HA
  and deletion protection disabled. The first isolated a harness error; it was deleted before the
  corrected verification fixture was launched. SQL Admin was already enabled and remained enabled.
- Patched `cloud sql enable sp_help_revlogin=on`; the flag transition required no restart. Connected
  as the default `sqlserver` login and created one synthetic login with no restricted server role.
- `EXEC msdb.dbo.sp_help_revlogin @login_name='<synthetic>'` returned a `CREATE LOGIN` statement
  containing that login's password hash and SID. A full-output exclusion check did not expose the
  default `sqlserver` administrator. No raw password, hash or SID was retained in test output.
- Disabled the flag and confirmed the procedure was immediately absent. The first harness attempt
  had failed before export because it unnecessarily tried to create a database user in `master`; its
  cleanup completed before the corrected minimal `CREATE LOGIN` fixture was launched.
- Live audit capture showed start/completion `cloudsql.instances.update` Admin Activity entries with
  `cloudsql.instances.update` granted for the flag transitions, but `protoPayload.request` was null.
  The direct SQL procedure call produced no Cloud Audit Log; SQL Server Audit/trace is conditional.
- Cleanup deleted both bounded instances and the pulled SQL client image. Independent inventory
  found zero matching active instances, retained/final backups, containers or images, and preserved
  the pre-existing API state. Cloud Asset Search temporarily retained a stale `RUNNABLE` index entry
  for the deleted second instance; the authoritative SQL Admin inventory was empty.

## Workforce Identity database-user namespace research (2026-09-28)

- Current MySQL and PostgreSQL Workforce Identity documentation explicitly warns that Cloud SQL
  cannot distinguish equal mapped `google.subject`/user IDs from different pools or providers. This
  is an expected identity-namespace footgun, not a zero-day: the second pool-qualified principal
  must still have `cloudsql.instances.login`, reach the instance, and match an existing database
  user whose database grants bound the impact.
- Same-subject crossover is documented, while case folding, MySQL domain stripping, native
  32/63-byte truncation, Unicode normalization and delimiter decoding are not. Preserve those as
  private-first two-principal tests; a reportable boundary failure requires two genuinely different
  mapped subjects and a lower-privileged token receiving the first user's database grants.
- SQL Server is excluded because it does not support IAM authentication for database operations.

## Independent post-exploitation cross-review (2026-09-28)

- Split Data API prerequisites by authentication mode. `cloudsql.instances.executeSql` is common;
  IAM database authentication additionally needs `cloudsql.instances.login` and an IAM database
  mapping, while built-in-password mode instead needs `secretmanager.versions.access` on a
  same-region regional secret and a database user with grants. Added the conditional, off-by-default
  `AccessSecretVersion` Data Access record.
- Corrected clone scope: the simple command is same-project, but the current Admin API and newer
  gcloud releases support cross-project clones with both destination project and destination network.
  No source-only cross-project claim was made because destination resource/network/policy
  prerequisites still apply.
- Tightened restore semantics: databases, users, and settings are copied, but an existing target
  retains its database flags and backup settings return to defaults; restore-over-target disconnects
  clients, restarts, and overwrites data. Cross-project restore requires target-project
  `cloudsql.instances.create` even when the target instance already exists.
- Bounded the TLS downgrade to direct clients. Auth Proxy and Language Connectors remain encrypted
  and verify identities regardless of `sslMode`.
- Fixed a broken destructive command: `gcloud sql instances delete` has opt-in
  `--enable-final-backup`, not `--no-enable-final-backup`. Disable an enabled instance setting with
  `instances patch --no-final-backup`, then omit the opt-in deletion flag. Organization policy can
  still require a final backup. Documented the current four-day Customer Care recovery window.
- Replaced the nonexistent `gcloud sql instances stop-replica` command with the current
  `instances patch --no-enable-database-replication` form, while retaining the documented narrower
  raw `instances.stopReplica` API path and its distinct minimum permission/audit event.
- Revalidated all nine retained H3s and their Cloud SQL, Cloud Storage, Secret Manager, IAM
  Credentials, database, and observability telemetry against current official documentation. No
  cloud resources were used.

## Post-exploitation page rewrite (2026-09-28)

- Re-audited every former technique against the current official Cloud SQL PostgreSQL audit,
  permissions, Data API, backup/restore, clone, replica, import/export, flags, TLS, Auth Proxy, and
  lifecycle documentation. No cloud resources were used.
- Consolidated the former 17 H3 sections into nine end-to-end primitives with explicit minimum
  permissions, prerequisites, bounded impact, categorical stealth, and per-operation telemetry.
- **Moved out persistence duplicates:** authorized-network/public-IP exposure and database-user
  creation/password rotation are already covered by the Cloud SQL persistence page. User listing
  alone was dropped as low-value recon rather than retained as a standalone post-exploitation
  technique.
- **Bounded copy claims:** clone, replica, and restore operations copy data but do not grant a
  database session. End-to-end access still needs a usable database identity/grants and connection
  path. The simple clone form is same-project, while current API/newer CLI surfaces also support
  cross-project cloning with destination-side prerequisites; restore-over-target is disruptive.
- **Bounded import/export claims:** export uses the instance service account to write a supported
  export to Cloud Storage. Import is not a generic object-read oracle; the source must be a
  supported, parseable dump or data file. The export CLI needs `instances.get` plus `export`.
  Import itself needs `instances.import`; `instances.get` is conditional for the documented custom
  role/discovery workflow. Both require the corresponding bucket permission on the instance service
  account.
- **Corrected anti-forensics:** database flags can suppress PostgreSQL/pgAudit evidence but cannot
  disable Cloud Audit Logs and do not necessarily disable Query Insights. `--database-flags`
  replaces the complete flag set, so omitted flags reset to defaults; some changes restart the
  instance.
- **Corrected TLS claim:** `ALLOW_UNENCRYPTED_AND_ENCRYPTED` permits plaintext but does not force a
  downgrade. Interception needs a plaintext-capable client and an on-path attacker. Resetting SSL
  config deletes client certificates and rotates the server certificate, making it principally a
  disruption primitive.
- **Corrected proxy minimum:** the Auth Proxy path needs `cloudsql.instances.get` and
  `cloudsql.instances.connect`; automatic IAM DB auth also needs `cloudsql.instances.login`, an IAM
  DB mapping, and database grants. Authorized networks are unnecessary only for the public-IP
  connector path; private IP still requires network reachability.
- **Corrected destructive commands and recovery scope:** removed the nonexistent
  `gcloud sql instances delete --no-final-backup` form. Deletion protection and retained-backup
  behavior are patched first, and any enabled final-backup instance setting is disabled with
  `instances patch --no-final-backup`; deletion then omits the opt-in `--enable-final-backup` flag.
  Backup deletion affects only the selected Cloud SQL backup and does not imply removal of enhanced
  Backup and DR, PITR, external, or provider-held recovery paths.
- Rejected unsupported/low-value page material: direct GCS use of `backupRuns.export`, theoretical
  instance/database `setIamPolicy`, generic arbitrary-file import, generic CMEK repointing, and a
  broad "no SQL Server RCE" non-technique. These remain research notes or open questions rather
  than book claims.

## Audit/reference correction (2026-09-26)
- Compared the post-exploitation and persistence pages with the [official PostgreSQL audit method
  table](https://docs.cloud.google.com/sql/docs/postgres/audit-logging). `users.create/update` and
  `databases.delete` are `DATA_WRITE`, export is `DATA_READ`, import and executeSql are `DATA_WRITE`;
  these are Data Access methods and are off by default. The existing pages had labeled several as
  always-on Admin Activity. Also corrected `users.insert` to `users.create` and
  `backupRuns.restore` to `instances.restoreBackup`. Added explicit stealth ratings throughout
  the post-exploitation page. Proxy `instances.connect` is classified Admin Activity.
- **Retracted unsupported backup-to-GCS claim.** `cloudsql.backupRuns.export` exists as an IAM
  permission, but the [documented use](https://docs.cloud.google.com/alloydb/docs/migrate-cloud-sql-to-alloydb)
  is copying a PostgreSQL backup into an AlloyDB cluster, requiring AlloyDB privileges/resources.
  The Cloud SQL audit reference does not list a standalone method or a direct GCS export endpoint.
  Removed this as a book technique rather than presenting an unverified direct exfiltration path.
- The [Cloud SQL role list](https://docs.cloud.google.com/sql/docs/postgres/iam-roles) names
  `instances.setIamPolicy` and `databases.setIamPolicy`, so the earlier blanket claim that
  `cloudsql.*.setIamPolicy` does not exist was removed. Neither v1 nor v1beta4 SQL Admin
  discovery exposes an IAM policy method for instances or databases; no self-grant claimed.
- **Retracted unsupported CMEK repoint claim.** [Cloud SQL CMEK guidance](https://docs.cloud.google.com/sql/docs/postgres/configure-cmek)
  documents re-encryption with the latest version of the *existing* key, not changing an
  existing instance to an attacker-owned key. Key disable/destroy requires separate KMS control,
  so the prior `cloudsql.instances.manageEncryption` ransom entry had no demonstrated primitive.
- Clarified that clone/replica operations alone do not provide a database session: the published
  password reset requires `cloudsql.users.update`, and network changes require
  `cloudsql.instances.update`. These were missing from the stated end-to-end minimum permissions.

## Live-verified
- **pg_cron in-engine scheduled-task persistence — CONFIRMED (2026-09-25).** Stood up a throwaway
  POSTGRES_15 `db-f1-micro` (us-central1), set `cloudsql.enable_pg_cron=on` (`cloudsql.instances.update`,
  triggers a restart), `CREATE EXTENSION pg_cron`, `cron.schedule('* * * * *', ...)`. The job **fired every
  minute via the pg_cron background worker with no client session held** (verified rows + `cron.job_run_details`
  `succeeded`). Lives in the DB (`cron.job`), not IAM → **survives IAM revocation and instance restart**;
  removal needs superuser SQL (`DROP EXTENSION` / `cron.unschedule`), not an IAM change.
  - Min-perms: `cloudsql.instances.update` (flag) + a `cloudsqlsuperuser`-group DB login (built-in
    `postgres`/`root`). DB reach = built-in password auth (**no `cloudsql.instances.connect` needed**) or IAM
    DB auth (`cloudsql.instances.connect`+`get`); `cloudsql.users.update` resets the postgres password.
  - Logs: only `cloudsql.instances.update` hits Admin Activity (always-on). The DB login + every recurring
    execution are engine-internal → **no Cloud Audit Log entry** even with Data Access logging; visible only in
    `cron.job`/`cron.job_run_details` or `postgres.log` w/ pgAudit.
  - Wiki: upgraded `gcp-cloud-sql-persistence.md` from "not live-verified" to confirmed; sharpened min-perms.
  - Teardown: instance deleted, `sql instances list` empty, no SAs/keys. MySQL `event_scheduler` analogue
    left doc-grounded (not separately fired — same in-DB persistence class).
