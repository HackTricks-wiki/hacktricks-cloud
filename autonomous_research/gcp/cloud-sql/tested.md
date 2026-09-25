# Cloud Sql — tested

Cloud SQL. Covered (clone/replica exfil, flag anti-forensics, SSL downgrade, CMEK ransom, backup export;
persistence: sslCerts.create, contained-DB user, pg_cron / event_scheduler scheduled-task).

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
