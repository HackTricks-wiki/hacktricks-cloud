# Optional Identity Center account access, 2026-09-26

AWS [announced](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-identity-center-accounts-optional/) that new organization Identity Center instances can be applications-only, without AWS account access. [DescribeInstance](https://docs.aws.amazon.com/singlesignon/latest/APIReference/API_DescribeInstance.html) exposes `PermissionSetsEnabled`; [UpdateInstance](https://docs.aws.amazon.com/singlesignon/latest/APIReference/API_UpdateInstance.html) can set it to true, but cannot revert it. This is a prerequisite for permission-set and account-assignment attack paths, not a distinct privilege escalation by itself.

Read-only checks in the lab found one ACTIVE organization instance in `eu-west-1`, owner `418720621023`, with `PermissionSetsEnabled=true` using current Boto3 1.43.103. The installed older AWS CLI omitted the new response field; the current SDK exposed it. No instance configuration was changed, and the temporary SDK directory was removed.

An audit of the existing Identity Center privilege-escalation page found fourteen technique sections with impacts and expandable log tables but no explicit stealth rating. Added one to each, grounded in their logged control-plane actions and visible assignments/policies. No live assignment or policy mutation was performed.
