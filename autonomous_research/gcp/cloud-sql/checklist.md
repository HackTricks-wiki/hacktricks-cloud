# Cloud Sql — open ideas

Open ideas — Cloud SQL.

- [ ] **Live-confirm pg_cron / event_scheduler persistence (cost-gated).** If a small disposable Cloud
  SQL instance can be stood up within the cost/time budget, confirm end-to-end that `enable_pg_cron`
  (Postgres) or `event_scheduler=ON` (MySQL) + a superuser-scheduled job re-executes attacker SQL on a
  timer and survives IAM changes. Tear down the instance immediately (deletion is fast). Otherwise keep
  as doc-grounded.
