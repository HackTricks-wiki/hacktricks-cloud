# Cognito provisioned-limit cost-abuse audit — 2026-09-30

## Result

Shipped a conditional post-exploitation technique for the new `GetProvisionedLimit` and `UpdateProvisionedLimit` APIs. A caller with `cognito-idp:UpdateProvisionedLimit` on `Resource: "*"` can immediately activate any already-approved paid API-category capacity in one Region. The write is account-level and needs no user-pool permission, Service Quotas write, PassRole, or prior read. It is expected functionality, not an AWS vulnerability.

The boundary is important: a requested value must be at least the category's free limit and no greater than the existing regional Service Quotas ceiling. This cannot reduce capacity below the free default or create capacity that AWS has not approved. It is therefore billing abuse only when an account already has paid headroom. AWS documents regional scope, no cross-account management, per-category billing above the default, and a one-day minimum duration on the current pricing page.

## Live authorization and boundary tests

The account's six adjustable API-rate categories in `us-east-1` all began at their free values, with no paid headroom:

| Category | Provisioned/free/ceiling RPS |
| --- | ---: |
| `UserToken` | 120 / 120 / 120 |
| `UserFederation` | 25 / 25 / 25 |
| `UserResourceRead` | 50 / 50 / 50 |
| `UserAuthentication` | 120 / 120 / 120 |
| `UserRead` | 120 / 120 / 120 |
| `UserCreation` | 50 / 50 / 50 |

A restricted STS session with only `cognito-idp:UpdateProvisionedLimit` on `Resource: "*"` successfully wrote `UserCreation=50` and received the complete limit object. This was deliberately a no-op at the free value, so it created no incremental capacity or charge. An otherwise identical session policy scoped to `arn:aws:cognito-idp:us-east-1:228478051196:userpool/*` was denied and reported authorization against resource `*`.

Two signed negative writes established both guardrails:

- `UserCreation=49` returned `InvalidParameterException: Requested value 49 is below the free limit of 50`.
- `UserCreation=51` returned `ServiceQuotaExceededException: Requested value 51 exceeds Service Quota ceiling of 50`.

The final read remained 50/50. A separate restricted session with only `cognito-idp:GetProvisionedLimit` on `Resource: "*"` successfully returned the `eu-west-1` `UserAuthentication` value (120/120), confirming independent regional reads.

## Telemetry

Event History indexed both APIs as management events under `cognito-idp.amazonaws.com`. `GetProvisionedLimit` was `readOnly:true`, retained the complete limit definition, and had a null response even on success. `UpdateProvisionedLimit` was `readOnly:false`; the successful no-op retained the definition and requested value, then returned the complete resulting definition plus provisioned/free values. The above-ceiling failure retained the request and exact `ServiceQuotaExceededException`. The resource-scoped IAM denial instead had null request/response fields and identified resource `*` in the authorization error.

Overall stealth: **Low**. The write is uncommon and logged, while billing signals arrive later.

## Cleanup

No persistent resource was created. Only expiring restricted STS sessions, read calls, one free-value no-op write and two rejected writes were used. Final `UserCreation` capacity was 50 RPS, equal to its free value and original state. User-pool inventories remained empty in both allowed Regions.

## Sources

- https://docs.aws.amazon.com/cognito/latest/developerguide/quotas.html#managing-provisioned-limits
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GetProvisionedLimit.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_UpdateProvisionedLimit.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncognitouserpools.html
- https://aws.amazon.com/cognito/pricing/#API_quotas
