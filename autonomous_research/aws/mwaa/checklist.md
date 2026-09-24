# AWS MWAA (airflow) — open ideas

- [x] Classic CreateWebLoginToken/CreateCliToken -> DAG exec as execution role — DONE (token gate
  verified; DAG-exec from-confidence). See tested.md.
- [ ] **airflow:PublishMetrics** / worker impersonation — check whether it enables anything beyond
  metrics (likely not; low value).
- [ ] **UpdateEnvironment --airflow-configuration-options** — inject Airflow config (e.g. change
  webserver/authbackend, core.dags_folder, or add a malicious plugin path via requirements/plugins S3
  keys) as a persistence/backdoor vector on an existing env. Needs an env to test.
- [ ] **UpdateEnvironment --execution-role-arn** — repoint an env at a more-privileged execution role
  (privesc parallel to the Deadline pattern) + then CreateCliToken to run as it. iam:PassRole gated.
  Needs an env to test; likely high-value — verify whether UpdateEnvironment enforces PassRole.
