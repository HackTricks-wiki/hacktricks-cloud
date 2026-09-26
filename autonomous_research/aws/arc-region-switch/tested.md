# arc-region-switch (AWS ARC Region Switch) — tested

## VERIFIED (lab 228478051196, 2026-09-25) — two-sided PassRole probe
- **CreatePlan + iam:PassRole(executionRole)**: WORKS.
  - NEG (CreatePlan only, no PassRole) -> `AccessDeniedException: not authorized to perform: iam:PassRole on resource: <exec-role>`.
  - POS (scoped iam:PassRole on exec-role) -> gate passes; call proceeds to `ValidationException` then, with primaryRegion set, full CreatePlan SUCCEEDS (returns plan ARN). DeletePlan removes it (clean teardown; only metadata, no running infra, no cost).
  - executionRole trust principal confirmed: `arc-region-switch.amazonaws.com` (accepted).
- Shipped to wiki: NEW PAGE aws-privilege-escalation/aws-region-switch-privesc/README.md (+ SUMMARY entry).

## Mechanism / why it matters
- Plan steps: customActionLambdaConfig (invoke arbitrary Lambda), rds promote-read-replica, global Aurora/DocumentDB failover, Route53 record/health-check flip, ASG/ECS/EKS scaling, arcRoutingControl. All run AS executionRole.
- Many resource configs take crossAccountRole + externalId -> cross-account pivot when the execution
  role can assume the target role and its trust accepts the execution-role principal/account plus the
  external ID.
- StartPlanExecution needs NO PassRole (plan already carries executionRole) -> availability/traffic-redirect primitive on an existing plan.

## NOT live-fired (documented high-confidence)
- Actual StartPlanExecution of a real failover (needs real multi-region app / Aurora global cluster; expensive + destructive). Doc-grounded in the page's post-exploitation section.
- Cross-account crossAccountRole pivot (needs a second-account role assumable by the execution role
  with the matching external ID).

## Official-contract reconciliation (2026-09-26)

- Corrected the earlier shorthand above: the target `crossAccountRole` does **not** directly trust ARC.
  ARC assumes the plan's `executionRole`, and that role then calls `sts:AssumeRole` on the target role.
  The target trust permits the execution-role account/principal and checks the plan's `externalId`.
- `associatedAlarms` can label alarms as `applicationHealth` or `trigger`; the separate `triggers`
  array selects alarm conditions, target Region, action, and a minimum delay between executions.
  AWS documents that a trigger automatically starts the plan when the alarm transitions into the
  configured condition. An alarm already in that state when attached does not immediately execute.
- This means a plan writer with the already-verified CreatePlan/UpdatePlan + execution-role PassRole
  boundary can install delayed/autonomous execution without retaining `StartPlanExecution`. No
  failover or alarm transition was fired because that would be destructive and adds no IAM-boundary
  evidence beyond the current official contract.

## UpdatePlan step-injection (VERIFIED two-sided, 2026-09-25)
- executionRole is REQUIRED on UpdatePlan -> PassRole-gated in EVERY call (even when role unchanged).
  - NEG (UpdatePlan only) with valid step -> AccessDeniedException iam:PassRole on exec-role.
  - POS (scoped iam:PassRole) -> injection ACCEPTED, reaches functional validation ("Custom action Lambda step: Region mismatch, missing [us-west-2]" -> needs a lambda per region). Gate passed.
- GOTCHA: schema ValidationException fires BEFORE the iam:PassRole authz check. A malformed request (e.g. bad regionToRun enum) returns ValidationException and can look like "no PassRole required" — it isn't. Always use a schema-valid request to observe the real gate. (Cost me one wrong read this session; corrected.)
- Net: UpdatePlan == same PassRole gate as CreatePlan but stealthier (rides an existing trusted plan). NOT a PassRole-free step-injection.
