
## batch:RegisterJobDefinition + iam:PassRole (+ SubmitJob) — run container as passed role (SHIPPED, VERIFIED)
- Gap: batch-privesc page only mentioned RegisterJobDefinition PassRole enforcement parenthetically; the primary register->pass-privileged-role->submit privesc had no section with impact+Logs.
- Two-sided authz probe (lab 228478051196, us-east-1):
  - NEG (batch:RegisterJobDefinition, NO iam:PassRole, jobRoleArn set) -> `AccessDeniedException ... not authorized to perform: iam:PassRole on resource: .../ht-batch-target because no identity-based policy allows the iam:PassRole action`.
  - POS (+ iam:PassRole on target) -> RegisterJobDefinition SUCCEEDED, registered ht-batch-probe-pos with privileged jobRoleArn baked in.
- Confirms iam:PassRole enforced on jobRoleArn/executionRoleArn at RegisterJobDefinition time. Complements existing SubmitJob-only technique (no PassRole at submit).
- Min perms: batch:RegisterJobDefinition + iam:PassRole (on ecs-tasks-trusting target) + batch:SubmitJob (to run). 
- Teardown: deregistered ALL revisions (pos:1, pos:2); deleted ht-batch-attacker/ht-batch-target roles; verified no ht-* roles, no ACTIVE ht-batch-probe defs. (Deregistered defs go INACTIVE/non-runnable; AWS has no hard-delete — page documents this.)
- Where: aws-batch-privesc/README.md new first section; refs [8][9]. Commit pending.
