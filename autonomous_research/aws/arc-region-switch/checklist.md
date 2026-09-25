# arc-region-switch — checklist (potential, not yet done)
- [x] UpdatePlan step-injection: RESOLVED -> executionRole is REQUIRED so PassRole IS enforced every call (verified two-sided). NOT PassRole-free. Documented on wiki.
- [ ] crossAccountRole + externalId: does ARC require the target-account role to trust arc-region-switch with a specific externalId? Map the confused-deputy conditions.
- [ ] StartPlanExecution authorization: any resource-policy / tag condition, or is action-only enough on any plan in the account?
- [ ] associatedAlarms/triggers: can an attacker set a CloudWatch alarm trigger so the malicious plan self-executes on an attacker-forced alarm state (autonomous trigger, no StartPlanExecution call)?
- [ ] reportConfiguration.s3Configuration bucketOwner/bucketPath: execution report written to attacker S3? minor exfil/where-am-I signal.
