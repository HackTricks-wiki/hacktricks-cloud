# CloudWatch Omni organization credential vending — 2026-09-26

## Status

**High-priority bypass hypothesis; not tested in the required account type.** A safe conclusive fixture requires an explicitly disposable AWS Organizations management account, a separate member account, an organization CloudWatch Omni domain, and a member space. The current authorized account is an ordinary member (`228478051196`, management account `418720621023`), so it cannot exercise the decisive boundary without Organizations-level and cross-account state changes.

The documented, properly authorized credential-broker operation is now covered publicly as expected cross-account functionality. Do **not** claim or report the no-target-grant bypass unless it succeeds in the management/delegated-admin fixture below.

## Why this is high priority

`cloudwatch:GetSpaceCredentialsForOrganization` returns a full one-hour AWS credential tuple for the target member account's `CloudWatchOmniOperatorRole`. The request selects either a `spaceId` or `domainId` plus `targetAccountId`.

The action has three unusual properties:

1. Service Authorization exposes no resource type or condition key, so IAM can only grant it on `Resource: "*"`.
2. It has no listed dependent action; no `iam:PassRole` is required at credential-vending time.
3. AWS-managed `CloudWatchReadOnlyAccess` current version 25 includes `cloudwatch:Get*` on `*`, automatically granting this new credential-vending API to a policy advertised as read-only. Version 25 also explicitly adds `cloudwatch:CreateOneTimeDeepLinkCode`; the credential action was already captured by the older `Get*` wildcard.

The operator role is not generic administrator, but the AWS-managed `CloudWatchOmniSpaceAccessPolicy` includes meaningful CloudWatch Omni writes, account-wide IAM role/user metadata reads, Secrets Manager metadata listing, tagged-secret management, Lambda invocation for evaluator functions, AWS Config recorder management, and constrained same-account `iam:PassRole` paths.

## Expected secure gate and zero-day hypothesis

Official API prose says the caller must be the Organizations management account or a delegated administrator **with access to the target space**. Other Omni guidance says programmatic callers are authorized by IAM and a missing access grant does not deny unless the identity policy itself requires `cloudwatch:HasAccessGrant=true`. This action exposes no such condition key.

The strongest test is:

- management-account role with only `cloudwatch:GetSpaceCredentialsForOrganization` (or only `CloudWatchReadOnlyAccess`);
- no domain/space access grant to that role;
- request credentials for an existing member-account space.

Secure outcome: access denied. Returning credentials would let a nominally read-only management-account principal obtain a write-capable member-account operator session and would merit private AWS reporting.

Secondary boundaries:

- grant on Space A, request Space B/member B;
- delegated admin without target-space grant;
- `domainId + targetAccountId` before a target space exists, resolving a documentation contradiction;
- revoke access grant or explicitly deny future vending, then measure already-issued credential lifetime;
- confirm caller-account vending event, target-account service `AssumeRole`, session tags/context, and response redaction.

## Member-account controls completed 2026-10-01

No AWS resource was created. Synthetic requests used the documented `domainId + targetAccountId` form:

- Administrator baseline: `AccessDenied`.
- Restricted session with only `cloudwatch:GetSpaceCredentialsForOrganization` on `Resource: "*"`: the same `AccessDenied`.
- Restricted statement on fabricated domain/space ARNs: the same `AccessDenied`.

This is the secure expected outcome for an ordinary member account and confirms that the organization-role prerequisite is enforced before the account can obtain credentials. The deliberately terse error cannot prove the target-space grant boundary or distinguish every internal IAM/resource check.

CloudTrail indexed all three as `readOnly: true` management events under `cloudwatch.amazonaws.com`; request parameters and response elements were null. No credential material was returned. `ListSpacesForOrganization` was independently denied, while local `ListDomains` and `ListSpaces` remained empty.

## Detection

Omni management APIs are expected CloudTrail management events with `eventSource: cloudwatch.amazonaws.com`. Detect `GetSpaceCredentialsForOrganization` in the management/delegated-admin account, service assumption of `CloudWatchOmniOperatorRole` in the member, and subsequent calls under that session. Expected stealth is **Low/Medium**: the vend is logged, but generic CloudWatch `Get*` policy reviews and monitoring may not treat it as credential issuance.

## Safe future fixture

Use only an empty disposable member account and Region. Enabling a space can backfill up to seven days of telemetry, so do not use a production member. Test the no-grant caller, explicit-deny control, properly granted control, cross-space boundary, pre-space selector, and post-revocation lifetime. Make one harmless reversible Omni write only after confirming the returned principal and policy.

Cleanup must delete every space first, wait until absent, delete the organization domain, and then inspect service-created roles/service-linked roles rather than assuming they were removed automatically.

## References

- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_GetSpaceCredentialsForOrganization.html
- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_SpaceCredentialRequestContext.html
- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_AwsCredentials.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_cloudwatch.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-identity-and-access-management-for-cloudwatch-omni.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-cross-service-confused-deputy-prevention.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/CloudWatchReadOnlyAccess.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/CloudWatchOmniSpaceAccessPolicy.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-security-best-practices-for-cloudwatch-omni.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-set-up-omni-for-your-organization.html
