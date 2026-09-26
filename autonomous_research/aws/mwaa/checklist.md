# AWS MWAA (airflow) — open ideas

- [x] Classic CreateWebLoginToken/CreateCliToken -> DAG exec as execution role — DONE (token gate
  verified; DAG-exec from-confidence). See tested.md.
- [ ] **airflow:PublishMetrics** / worker impersonation — check whether it enables anything beyond
  metrics (likely not; low value).
- [ ] **UpdateEnvironment --airflow-configuration-options** — inject Airflow config (e.g. change
  webserver/authbackend, core.dags_folder, or add a malicious plugin path via requirements/plugins S3
  keys) as a persistence/backdoor vector on an existing env. Needs an env to test.
- [x] **UpdateEnvironment --execution-role-arn** — DONE. Authz gate VERIFIED (airflow:UpdateEnvironment
  + iam:PassRole -> ResourceNotFoundException on bogus env, NOT AccessDenied; note IAM prefix is
  `airflow:` not `mwaa:`). Documented on the MWAA post-ex page ("Repoint the execution role"). Repoint
  onto any airflow.amazonaws.com-trusting role, then CreateCliToken to run as it. End-to-end trigger
  needs a live env (MWAA ~$0.49/hr min + async ~30min apply) -> cost/time deferred, gate proven.
