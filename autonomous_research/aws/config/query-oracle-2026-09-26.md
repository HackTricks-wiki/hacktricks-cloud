# AWS Config current/historical query oracle — 2026-09-26

## Result

AWS Config's read plane is a high-value cross-service configuration oracle:

- `config:SelectResourceConfig` alone returned current/stale IAM resource names, ARNs, trust policies, and managed-policy attachments while native IAM enumeration was denied.
- `config:GetResourceConfigHistory` alone returned a deleted IAM role's complete trust and inline policy while `iam:GetRole` was denied.
- `config:SelectAggregateResourceConfig` extends the same query model across every account and Region collected by a central aggregator; none existed in the lab, so the exact aggregator authorization is published from the current API/IAM contract.
- No Config recorder or aggregator was created or modified. Only one disposable IAM role was used and deleted.
- This is intended Config authorization behavior, not an AWS vulnerability.

## Initial state

- Authorized account: `228478051196`
- Region: `us-east-1`
- Assumed role: `arn:aws:iam::228478051196:role/ChackBotAdministratorRole`
- Customer-managed configuration recorders: `0`
- Configuration aggregators: `0`
- Config still held 28 `AWS::IAM::Role` configuration items captured by an earlier, now-removed recorder

No Config resource was created. The retained CIs made it possible to test read authorization without re-enabling recording.

## Experiment A — `SelectResourceConfig` only

Created temporary role `HtConfigReadAudit-20260926` with only:

```json
{
  "Effect": "Allow",
  "Action": "config:SelectResourceConfig",
  "Resource": "*"
}
```

Results:

- `iam:ListRoles` was denied.
- The Config query successfully returned role names, ARNs, URL-encoded `assumeRolePolicyDocument` values, and attached managed policies.
- One returned role, `ht-audit-cfg-rem-17105`, had already been deleted; administrator `iam:GetRole` returned `NoSuchEntity`. Its last recorded CI remained queryable because recording had stopped before the deletion was captured.
- `config:GetResourceConfigHistory` was independently denied.

Useful tested expression:

```sql
SELECT resourceName, arn,
       configuration.assumeRolePolicyDocument,
       configuration.attachedManagedPolicies
WHERE resourceType = 'AWS::IAM::Role'
```

An administrator query also proved that nested fields can return `rolePolicyList`; `SELECT *` returned only the documented top-level scalar fields.

## Experiment B — `GetResourceConfigHistory` only

Replaced the role policy with only:

```json
{
  "Effect": "Allow",
  "Action": "config:GetResourceConfigHistory",
  "Resource": "*"
}
```

For the deleted role ID `AROATKMS2MN6BQHAOOFCY`, the response returned:

- role name and ARN;
- recorded creation/capture metadata;
- trust policy for `ssm.amazonaws.com`;
- full inline policy `p`, including wildcard-resource `iam:AttachRolePolicy` and `iam:ListAttachedRolePolicies`;
- attachments, permissions boundary, tags, instance profiles, and last-used fields.

`iam:GetRole` and `SelectResourceConfig` were independently denied. This proves the history action is sufficient for a known resource ID and is not merely a helper for the advanced-query permission.

## Aggregator analysis

Current official contracts establish:

- `SelectAggregateResourceConfig` accepts an aggregator name and SQL expression and queries source accounts/Regions.
- IAM supports exact `ConfigurationAggregator` ARN scope and `aws:ResourceTag` conditions.
- `GetAggregateResourceConfig` and `BatchGetAggregateResourceConfig` are separate permissions for complete known resource keys.
- No target-account IAM/service read permission is listed; the aggregator's collected data is the deliberate authorization boundary.

Because the account had zero aggregators and is not the Organizations management account, no aggregator was created merely to duplicate the already verified local query mechanism.

## Telemetry

Expected and current official behavior:

| Event | Security value |
| --- | --- |
| `SelectResourceConfig` | Read-only Config management event; expression identifies the query; returned configurations are not useful in the response field |
| `GetResourceConfigHistory` | Read-only management event; resource type/ID and time window identify the target; returned history is omitted |
| `SelectAggregateResourceConfig` | Read-only management event in the aggregator account; aggregator name/expression identify organization-wide enumeration |

The events do not generate native IAM/EC2/S3/etc. read events because AWS Config serves its stored configuration items.

## Candidate matrix

| Candidate | Result / disposition |
| --- | --- |
| Current cross-service configuration through `SelectResourceConfig` | Verified and published |
| Deleted/previous state recovery through `GetResourceConfigHistory` | Verified and published |
| Multi-account/Region query through aggregator | Current official contract; published as bounded variant |
| `SELECT *` yields every nested configuration property | Rejected; it yields only top-level scalar fields, so nested fields must be explicit |
| Advanced query returns deleted resources | Rejected by product contract; observed stale result existed because deletion was never recorded |
| Native service read permissions are also required | Rejected live for IAM roles |
| Config query grants control of returned resources | Rejected; disclosure only |

## Cleanup

- Deleted inline policy `ConfigQueryOnly`.
- Deleted role `HtConfigReadAudit-20260926`.
- `GetRole` returned `NoSuchEntity` afterward.
- Final Config recorder count: `0`.
- Final Config aggregator count: `0`.

No Config state, S3 delivery resource, target service resource, or retained test role was created.

## Future tests

- In an existing central Config account, validate exact aggregator-ARN scoping, CloudTrail response omission, tag-based authorization on aggregators, and complete `GetAggregateResourceConfig` fields.
- Build a safe data-classification matrix for Config schemas that can carry sensitive application configuration, without assuming secret fields that native APIs redact.
- Test record/delete convergence and retained-history lookup for non-IAM types under each retention setting.
- Compare Config, Resource Explorer, and Tagging API coverage and fields so defenders understand that denying one inventory plane does not block the others.

## References

- https://docs.aws.amazon.com/config/latest/developerguide/querying-AWS-resources.html
- https://docs.aws.amazon.com/config/latest/APIReference/API_SelectResourceConfig.html
- https://docs.aws.amazon.com/config/latest/APIReference/API_SelectAggregateResourceConfig.html
- https://docs.aws.amazon.com/config/latest/APIReference/API_GetResourceConfigHistory.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_config.html
