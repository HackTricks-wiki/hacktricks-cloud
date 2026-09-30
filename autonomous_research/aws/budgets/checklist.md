# AWS Budgets checklist
- [ ] Full execution proof: create budget whose ACTUAL spend already exceeds an absolute threshold, AUTOMATIC approval, wait for budget eval (hours) -> confirm AdministratorAccess/ReadOnlyAccess attached to victim. (Create+PassRole already verified; execution timing-gated.)
- [ ] APPLY_SCP_POLICY from the org management account -> attach/detach an SCP (org-wide guardrail manipulation). Needs mgmt account.
- [ ] RUN_SSM_DOCUMENTS budget action -> code exec on chosen instances via a budgets-trusting SSM role.
