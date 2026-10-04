# CloudWatch Omni audit — 2026-10-01

## Outcome

CloudWatch Omni was absent from the public book despite reaching general availability on 2026-09-23. Added service enumeration and four high-value expected attack paths:

1. Direct IAM telemetry queries through the implicit `dataset/default`.
2. One-time deep-link conversion of IAM credentials into a domain browser session.
3. Persistent `SPACE_ADMIN` access grants for an existing principal.
4. Organization management/delegated-admin vending of one-hour member-space AWS credentials.

No unexpected behavior is claimed. The separate no-grant management-account credential-vending hypothesis remains unverified because the authorized account is an ordinary organization member, not the management account or a delegated administrator.

## Environment and starting inventory

- Account: `228478051196`
- Organization: `o-bsfj09ozhf`
- Management account: `418720621023`
- Region used for controls: `us-east-1`
- `ListDomains`: empty
- `ListSpaces`: empty
- `ListSpacesForOrganization`: `AccessDenied`, consistent with the member-account prerequisite
- Unsigned `ListDomains`: `MissingAuthenticationTokenException`

The service uses CLI client `cloudwatchomni`, IAM/signing prefix `cloudwatch`, and CloudTrail source `cloudwatch.amazonaws.com`.

## Managed-policy observations

Live IAM policy retrieval showed:

- `CloudWatchReadOnlyAccess` default version v25, created 2026-09-22, includes `cloudwatch:Get*`, `cloudwatch:List*`, and an explicit `cloudwatch:CreateOneTimeDeepLinkCode` allow on `*`.
- The `Get*` wildcard includes `cloudwatch:GetSpaceCredentialsForOrganization`, an API that returns a full one-hour AWS credential tuple.
- v24 already contained `cloudwatch:Get*`; v25 added the explicit deep-link action.
- `CloudWatchOmniSpaceAccessPolicy` v1 allows Omni space actions on `*` only when `cloudwatch:HasAccessGrant=true`. It also contains account-wide IAM role/user metadata reads, Secrets Manager metadata listing, constrained secret management, KMS operations, Config service-linked recorder management, evaluator operations, Lambda invocation for named evaluator functions, and same-account PassRole paths.
- `CloudWatchOmniDomainAccessPolicy` applies `cloudwatch:HasAccessGrant=true` to organization domain grant operations.

## Direct telemetry-query controls

### Authorization

A restricted session with only:

- `cloudwatch:StartTelemetryQuerySession`
- `cloudwatch:StopTelemetryQuerySession`

on `Resource: "*"` created a session. The same action on a fabricated space ARN was denied on `resource: *`. The successful session was immediately stopped.

Adding `StartTelemetryQuery`, `GetTelemetryQueryResults`, and `StopTelemetryQuery` but omitting `GetRecords` caused `StartTelemetryQuery` to fail on:

`arn:aws:cloudwatch:us-east-1:228478051196:dataset/default`

Adding only `cloudwatch:GetRecords` on that exact Dataset ARN passed the dependency. This is a useful current minimum that is not obvious from the top-level query API.

### Successful bounded query

The query used a five-minute time window, selected only `@timestamp`, and limited results to one row. The API required explicit compatible timestamp expressions; `to_timestamp('<UTC timestamp>')` succeeded. The query completed immediately with:

- status: `Complete`
- rows: `0`
- bytes scanned: `0`
- records scanned/matched: `0`
- partial results: `false`

No domain, space, access grant, operator role, or forwarded Dataset record existed. This proves the direct SigV4 IAM path and minimum actions, not data exposure in the empty account. AWS explicitly documents that direct IAM callers are controlled by their identity policy and a missing grant does not deny unless the policy requires `cloudwatch:HasAccessGrant=true`.

Every created session was stopped successfully. No active reusable session or query remains.

### Telemetry

CloudTrail indexed the query workflow as default management events with `readOnly: true`:

- `StartTelemetryQuerySession`: session name retained.
- `StartTelemetryQuery`: session ID retained; query text replaced by `HIDDEN_DUE_TO_SECURITY_REASONS`; successful and validation-failed calls both appeared.
- `GetTelemetryQueryResults`: query ID retained; result rows absent from response elements.
- `StopTelemetryQuerySession`: session ID retained.

The no-`GetRecords` IAM denial omitted request parameters and named the exact Dataset ARN in the error.

## One-time deep-link controls

Restricted sessions called `CreateOneTimeDeepLinkCode` for synthetic domain `d-aaaaaaaaaa` with a 600-second TTL:

- Admin baseline: `ResourceNotFoundException: Domain not found`.
- Only `cloudwatch:CreateOneTimeDeepLinkCode` on `*`: same service result.
- Same action on fabricated domain/space ARNs: IAM denial on `resource: *`.

This confirms the action-only wildcard minimum and no list/get dependency for a known domain ID. No real code or browser session was created.

CloudTrail recorded a write management event. Authorized failures retained `domainId` and `ttlSeconds`; IAM denial parameters were null. The service model marks both returned code and URL sensitive and says they are redacted from request logs and CloudTrail.

## Access-grant persistence controls

Restricted `CreateAccessGrant` requests used a nonexistent domain/space, `SPACE_ADMIN`, and an existing same-account role principal. Results:

- `Resource: "*"`: passed IAM, `Domain not found`.
- `arn:aws:cloudwatch:us-east-1:228478051196:access-grant/*`: passed IAM, `Domain not found`.
- Fabricated space ARN only: denied on a generated access-grant ARN.
- Wrong-account access-grant prefix: denied on the actual-account generated ARN.
- No action: denied on the generated ARN.

Current live authorization therefore evaluates `CreateAccessGrant` on:

`arn:aws:cloudwatch:<region>:<account>:access-grant/<service-generated-uuid>`

This is narrower than `*` but cannot be limited to one predictable future UUID or one target space, because the target IDs are not encoded in the evaluated ARN. The current public Service Authorization Reference lists no resource type for the action.

CloudTrail authorized failures retained domain ID, space ID, name, principal type/ARN, `SPACE_ADMIN`, and generated client token. IAM denials had null request parameters. No grant was created.

## Organization space-credential broker

`GetSpaceCredentialsForOrganization` controls used synthetic domain/target-account context:

- Admin baseline: `AccessDenied`.
- Only the action on `*`: `AccessDenied`.
- Fabricated resource-scoped statement: `AccessDenied`.

The service intentionally returned the same terse result at the organization gate, so the member account cannot distinguish every internal IAM/resource check. The Service Authorization Reference and IAM model expose no resource type, so the expected policy remains `Resource: "*"`.

Official sources establish that the API returns an access key, secret key, session token, and expiration valid for one hour; the caller must be the management account or delegated admin with target-space access; and the member-account data-access/operator role is assumed to issue space credentials. No credentials were returned in this lab.

CloudTrail recorded the denials as read-only management events with null request/response parameters. The management-account/no-grant test remains the highest-priority future fixture. Do not conflate the public expected technique with the private bypass hypothesis.

## Not shipped / future tests

- **Potential security-impact candidate:** management-account or delegated-admin caller with only `CloudWatchReadOnlyAccess` and no target-space grant. Secure outcome is denial. A success would vend write-capable member-space credentials from a nominally read-only policy and should be privately reported.
- Test a properly granted credential vend in a disposable management/member pair; record returned caller ARN, session policy/tags/context, operator-role ceiling, target-account CloudTrail, revocation behavior, and optional custom role policies.
- Test `CreateDomainAccessGrantForOrganization` persistence separately in an authorized management-account fixture.
- Test access-grant data scopes against metrics, dataset export, AI summaries and prompt playground. AWS already documents the exclusions; only unexpected scope escape should become a private report.
- Test integration credential reads/updates with disposable Slack/API-key fixtures. `GetIntegration` exposes credential and role ARNs but not stored secret values.
- Deep-link redirect handling is not presently an attack: the caller already owns the one-time code, and no victim-secret transfer has been demonstrated.

## Cleanup

- All query sessions created during authorization/syntax testing were stopped, including the successful bounded query session.
- No domain, space, access grant, access profile, integration, dashboard, alert, view, IAM role, secret, KMS key, Dataset forwarding rule, or organization state was created.
- Final `ListDomains` and `ListSpaces` remain empty.
- Only expiring restricted STS sessions and CloudTrail audit records remain.

## References

- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch-omni.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-identity-and-access-management-for-cloudwatch-omni.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-security-best-practices-for-cloudwatch-omni.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-control-access-to-your-space.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-sql-query-reference.html
- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_CreateOneTimeDeepLinkCode.html
- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_CreateAccessGrant.html
- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_GetSpaceCredentialsForOrganization.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_cloudwatch.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/CloudWatchReadOnlyAccess.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/CloudWatchOmniSpaceAccessPolicy.html
