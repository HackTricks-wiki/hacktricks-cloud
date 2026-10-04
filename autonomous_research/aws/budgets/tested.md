# AWS Budgets — tested & documented (NEW PAGE)

## budgets:CreateBudgetAction + iam:PassRole (+ExecuteBudgetAction) — self-attach admin policy / SCP / run SSM as passed role (SHIPPED)
- Gap: budget actions only appeared DEFENSIVELY on cost-explorer post-exploit page (delete action to evade containment). Offensive privesc direction undocumented. No budgets/cost privesc page existed.
- Mechanism: CreateBudgetAction ActionType APPLY_IAM_POLICY (attach managed policy to Users/Groups/Roles) | APPLY_SCP_POLICY (org SCP attach) | RUN_SSM_DOCUMENTS (cmd on instances), run as ExecutionRoleArn (budgets.amazonaws.com-trusting). iam:PassRole enforced on exec role at create.
- VERIFIED two-sided (lab 228478051196, us-east-1, global svc):
  - NEG (CreateBudgetAction APPLY_IAM_POLICY, NO iam:PassRole) -> AccessDeniedException iam:PassRole on ht-budget-exec.
  - POS (+ iam:PassRole on exec) -> SUCCEEDED, returned ActionId.
  - ExecuteBudgetAction(APPROVE) -> ResourceLockedException "not allowed during [ActionStatus: Standby]": new action starts Standby, moves Pending only when budget eval crosses threshold (timing/precondition, NOT authz). Set already-crossed threshold or AUTOMATIC approval for it to fire. Policy-attach effect is documented AWS behavior.
- Min perms: budgets:CreateBudgetAction + iam:PassRole (budgets-trusting exec role w/ iam:AttachUserPolicy etc.) + budgets:ExecuteBudgetAction (for manual approve).
- Teardown: deleted budget action, budget, ht-budget-exec, ht-budget-attacker, ht-budget-victim (never got policy attached). Verified no ht-* roles/users, budget None.
- Where: NEW page aws-privilege-escalation/aws-budgets-privesc/README.md; SUMMARY wired. Refs [1]-[4].
