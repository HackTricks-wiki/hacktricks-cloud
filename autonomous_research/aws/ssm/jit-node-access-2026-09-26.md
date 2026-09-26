# Systems Manager Just-in-time Node Access credential vending — 2026-09-26

## Result

High-confidence expected technique added to the public SSM privilege-escalation page from current AWS documentation and API/service-authorization models. Not fired live because JIT is an account/organization-level feature that is not configured in this shared test account; enabling it would create cross-account setup state and future per-node billing.

This is not an AWS vulnerability or approval bypass. Its offensive value is permission equivalence: `ssm:StartAccessRequest` plus `ssm:GetAccessToken` can become an interactive shell after approval even when the requester has no `ssm:StartSession` or `iam:PassRole` permission.

## Read-only account preflight

In `us-east-1`:

- `AWSServiceRoleForSystemsManagerJustInTimeAccess`: `NoSuchEntity`.
- Auto-approval policy documents: none.
- Manual-approval policy documents: none.
- Managed-node inventory: empty.
- SSM Quick Setup configuration managers: none (`null`).

No configuration was changed and no cloud resource was created.

## Required boundary

The minimum known-target API path is:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ssm:StartAccessRequest",
      "Resource": "arn:aws:ec2:<region>:<account>:instance/<instance-id>"
    },
    {
      "Effect": "Allow",
      "Action": "ssm:GetAccessToken",
      "Resource": "*"
    }
  ]
}
```

The service authorization reference supports EC2 instance and SSM managed-instance resources for `StartAccessRequest`, lists no resource type for `GetAccessToken`, and lists no dependent action for the former. Optional tags add `ssm:AddTagsToResource`; discovery/console/OpsItem permissions in AWS examples are not intrinsically required for the two API calls.

## Preconditions and limits

- Unified Systems Manager console and JIT must already be enabled.
- Only STS `AssumeRole` temporary credentials are supported for requesters.
- An auto-approval policy must match, or all manual approvals must complete.
- Deny-access policies take precedence.
- Requester and node must be in the same account and Region.
- Auto-approved access lasts exactly one hour; manual policies allow 1–336 hours.
- An approved user may start multiple sessions during the window.
- Existing sessions are not automatically terminated when the approval window ends.
- Access-request records are retained for one year.

## Deferred live fixture

Use a dedicated account/Region already onboarded to the unified SSM console, one private Amazon Linux managed node, and an exact-requester/exact-node auto-approval policy. Give the requester only the two actions above and explicitly deny direct `StartSession`. After approval, handle all three `GetAccessToken` credential fields only in memory, start a session, run a harmless identity/canary read, terminate the session, and inspect CloudTrail.

Do not enable JIT in a populated shared account for testing because pricing applies to managed nodes after the trial and setup can use delegated-administrator/Quick Setup/StackSet resources.

## References

- https://aws.amazon.com/blogs/mt/introducing-just-in-time-node-access-using-aws-systems-manager/
- https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-just-in-time-node-access.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-just-in-time-node-access-start-session.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-just-in-time-node-access-setting-up.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-just-in-time-node-access-approval-policies.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_ssm.html
- https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_StartAccessRequest.html
- https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_GetAccessToken.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSSystemsManagerJustInTimeAccessTokenPolicy.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/monitoring-cloudtrail-logs.html
- https://aws.amazon.com/systems-manager/pricing/

