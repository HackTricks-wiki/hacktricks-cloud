# Account Access Manager (`account-access`) — research, 2026-09-26

## High-value expected behavior

- AWS [launched Account Access Manager on 2026-08-10](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-iam-aam/). Its [CreateEntitlement API](https://docs.aws.amazon.com/IAM/latest/UserGuide/aam-assign-remove-access.html) maps an Identity Center user/group ID to an existing IAM role ARN in any organization account. A controlled user can then reach that role from the Account Access Manager portal.
- [Service Authorization Reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_account-access.html) maps the operation to `account-access:CreateEntitlement` on the application ARN, with no `iam:PassRole` dependent action. [AWS's assignment-only policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/aam-security.html) likewise includes the Account Access Manager action and separate discovery/console dependencies, not `iam:PassRole`.
- The target role must already trust `account-access.amazonaws.com` for `sts:AssumeRole` and `sts:SetContext`, constrained by the target account and application ARN. [AWS trust-policy guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/aam-prepare-roles.html). This prerequisite limits the technique to roles an organization deliberately prepared for AAM. Assigning an unprepared role should not grant access.
- [AWS documents CloudTrail logging](https://docs.aws.amazon.com/IAM/latest/UserGuide/aam-security.html) for the `account-access` namespace. The new public book section supplies impact, persistence scope, stealth, and an expandable log table.

## Lab boundary and cleanup

The available lab account is an organization **member** without an organization Identity Center instance/Account Access Manager application. It cannot satisfy the service's management-account onboarding prerequisite without privileges absent from this test role. The installed AWS CLI 2.34.45 also lacks the `account-access` command namespace; current AWS CLI documentation describes it. The finding is grounded in AWS's explicit assignment and trust-policy documentation, with no live assignment attempted. No AWS resources were created, so no teardown was required.

## Distinct negative / limits

- `CreateEntitlement` does not rewrite target-role trust or grant access to arbitrary IAM roles. The role must already trust the specific Account Access Manager application.
- `CreateApplication` is not an ordinary member-account setup path; AWS requires the organization's management account, an organization Identity Center instance, and trusted AWS service access. Do not treat a member account's `account-access:CreateApplication` as a standalone escalation.
- The privilege is meaningful when a controlled Identity Center identity exists and a target trusting role is more privileged than the caller's current access. Otherwise it is just assignment administration.
