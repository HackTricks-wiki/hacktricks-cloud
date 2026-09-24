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

## UpdateEnvironment execution-role repoint (privesc) — authz VERIFIED (cont.64)

- **What:** `aws mwaa update-environment --execution-role-arn <target>` swaps the env's execution
  role onto any `airflow.amazonaws.com`-trusting role; then a minted CLI/web token (or any DAG) runs
  as that role. Companion to the classic token technique.
- **Authz probe:** role trusted by ChackBotAdministratorRole, inline policy = ONLY
  `airflow:UpdateEnvironment` + `iam:PassRole` (Resource:*). Assumed it, called update-environment on a
  non-existent env -> **ResourceNotFoundException** (IAM gate PASSED). First probe used `mwaa:` prefix
  and got AccessDenied — the IAM action prefix for MWAA is **`airflow:`**, not `mwaa:` (CLI is `aws mwaa`).
- **Precondition:** target role trusts `airflow.amazonaws.com`; iam:PassRole permits it.
- **Not fully fired:** end-to-end trigger needs a live MWAA env (~$0.49/hr min, and UpdateEnvironment
  applies asynchronously over ~30 min, recycling workers) -> cost/time exception; gate proven, trigger
  path is the already-documented token/DAG exec.
- **Teardown:** probe role deleted, verified NoSuchEntity. No infra left.
- **Wiki:** MWAA post-exploitation README, section "Repoint the execution role:
  airflow:UpdateEnvironment + iam:PassRole" with per-technique impact + Logs generated block. Ref [17].
