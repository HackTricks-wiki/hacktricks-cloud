# Lambda full JSON resource policy research, 2026-09-26

## Confirmed expected escalation

AWS [launched full Lambda resource policies](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-lambda-full-iam-resource-based-policies/) in August 2026. [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html) lists `UpdateFunctionCode` as a supported policy action and states that `PutResourcePolicy` replaces the old policy and requires `lambda:PutResourcePolicy`, `lambda:AddPermission`, and `lambda:RemovePermission`.

In account `228478051196`, a disposable IAM user with **no identity-based Lambda policy** successfully called `UpdateFunctionCode` on an active test function after an administrator used `PutResourcePolicy` to allow that user ARN to call `lambda:UpdateFunctionCode`. The function's code changed. This confirms that full policy control can lead to code execution under an existing function role, a privilege escalation when that role is stronger than the policy editor. No function execution was needed for the authorization test. CloudTrail Event History showed `PutResourcePolicy` and `UpdateFunctionCode20150331v2` as `lambda.amazonaws.com` management events in `us-east-1`.

A separate disposable user with only `lambda:PutResourcePolicy`, `lambda:AddPermission`, and `lambda:RemovePermission` on `*` successfully called `PutResourcePolicy` once. However, later attempts with the same action set on the exact function ARN, and then on `*`, returned `AccessDeniedException` despite IAM policy simulation returning `allowed`. The behavior was inconsistent across short-lived test users; do not infer an undocumented authorization bypass or assert exact resource-scoping behavior. The public entry follows AWS's stated action dependencies and the confirmed effect of the policy grant.

## Negative branch and cleanup

A user in a second authorized account was granted `UpdateFunctionCode` by the test function's policy but its call failed because that user lacked a caller-side identity-based `lambda:UpdateFunctionCode` allow. A separate attempt against a newly created function hit `ResourceConflictException` while its state was `Pending`; waiting until `Active` resolved that prerequisite in the final same-account test.

Each temporary Lambda function, execution role, IAM user, access key, and inline policy was deleted by the corresponding test script. No Lambda function was invoked; there were no compute charges from execution. The temporary local Boto3 installation is removed after documentation.

## Next checks

- [ ] Recheck exact-function ARN scoping after a longer IAM propagation interval using a single durable test user, then delete it.
- [ ] Test a cross-account code update using a caller with its own identity-based `UpdateFunctionCode` allow in a disposable second account.
- [ ] Confirm direct `Invoke` via the full policy with an IAM user lacking an identity allow.
- [ ] Check explicit deny, permissions boundary, and code-signing interactions in isolated functions.
