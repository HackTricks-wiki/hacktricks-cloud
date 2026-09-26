# Cloud Sql — tested

Cloud SQL. Covered (clone/replica copy, flag anti-forensics, SSL downgrade;
persistence: sslCerts.create, contained-DB user, pg_cron / event_scheduler scheduled-task).

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
