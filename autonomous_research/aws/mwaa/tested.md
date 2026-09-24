# AWS MWAA (airflow) — tested

## Classic MWAA CreateWebLoginToken/CreateCliToken -> RCE-as-execution-role — token gate VERIFIED

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1/eu-west-1. No MWAA envs present.
- **Authz VERIFIED (least-priv):** role granted ONLY airflow:CreateWebLoginToken + airflow:CreateCliToken,
  assumed, both called against a bogus env name -> ResourceNotFoundException (NOT AccessDenied) on BOTH
  => IAM gates pass independently; each token op alone reaches the service. Role torn down (NoSuchEntity).
- **Not run end-to-end:** classic MWAA env = ~25-min VPC-scaffolded provision; disproportionate for a
  canonical technique whose execution-role model is already confirmed on the same page by the Serverless
  CreateWorkflow coverage (verified there). Documented from-confidence for the DAG-exec chain.
- **Technique:** CreateWebLoginToken -> Airflow UI (env RBAC role, often Admin); CreateCliToken ->
  Airflow CLI-over-REST (POST https://<host>/aws_mwaa/cli, Bearer token). Trigger/upload a DAG ->
  Python runs on MWAA workers AS the environment EXECUTION ROLE -> escalate to that role. No PassRole,
  no DAG-bucket write needed to trigger existing DAGs (bucket write enables self-contained new-DAG RCE).
- **Disposition:** NEW section on aws-mwaa-post-exploitation/README.md (classic, distinct from the
  Serverless airflow-serverless:CreateWorkflow section already there). Refs [14][15][16]. Impact + Logs.
  This fills the "classic MWAA DAG-replacement below" forward-reference that had no section.
