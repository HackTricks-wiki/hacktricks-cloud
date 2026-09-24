# Cloud Sql — tested

Cloud SQL. Covered (clone/replica exfil, flag anti-forensics, SSL downgrade, CMEK ransom, backup export;
persistence: sslCerts.create, contained-DB user, pg_cron / event_scheduler scheduled-task).

## Not-live-verified (documented from docs, honest)
- pg_cron / MySQL event_scheduler in-engine persistence — `cloudsql.enable_pg_cron` /
  `event_scheduler` via `instances.update` + superuser `cron.schedule` / `CREATE EVENT`. Labeled
  reasoned/from-docs — "no Cloud SQL instance in lab" at the time.
