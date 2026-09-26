# Amazon Connect authorization-code session boundary — 2026-09-26

## Disposition

`CreateAuthCode` is a high-impact **candidate** because its documented response is a reusable
authorization code and its optional maximum duration defaults to 400 days. However, no code was
issued in the live matrix: every fully associated, IAM-authorized request returned HTTP 500. Do not
publish this as a working attack and do not report the 500 as a security zero-day; no security impact
was demonstrated.

The run did establish undocumented IAM-resource behavior for this API and verified both new IAM
action names. Retain those results so the session-minting path can be retested after the service or
documentation changes.

## Fixture

Each full run used only synthetic resources in `us-east-1`:

- a disposable SAML-backed Connect instance with inbound/outbound calls disabled;
- a Customer Profiles domain using the AWS-managed default encryption key and one synthetic profile;
- a `profile:PutIntegration` association whose URI was the Connect instance ARN and whose standard
  object type was `CTR`;
- the built-in Connect `Admin` security profile;
- in the final run, a custom security profile containing only `CustomerProfiles.View`,
  `CustomerProfiles.Edit`, and `CustomerProfiles.Create`;
- a disposable IAM role used only for the exact-boundary tests.

Although the Customer Profiles `CreateDomain` reference says instance association is console-only,
AWS's current re:Post guidance documents the API route: call `PutIntegration` with the domain name and
Connect instance ARN as `Uri`. The current service additionally rejected an omitted object type, so
the fixture supplied the standard `CTR` object type.

## IAM action and resource results

The current Service Authorization Reference does not list `CreateAuthCode` or `DeleteSession`, but
both hypothesized action names are active:

- a role allowing only `connect:CreateAuthCode` reached request validation and received
  `InvalidRequestException`, not IAM denial, when `DomainName` was omitted;
- a role allowing only `connect:DeleteSession` reached the service and received
  `ResourceNotFoundException: Instance not found` for a synthetic instance/session pair.

`CreateAuthCode` has a mandatory multi-resource authorization boundary when
`SecurityProfileIds` is supplied:

| Allowed resource | Result |
| --- | --- |
| Exact Connect instance ARN only | Denied on the selected `.../security-profile/<id>` ARN |
| Exact selected security-profile ARN only | Denied on the `.../instance/<id>` ARN |
| Both exact instance and selected security-profile ARNs | Passed IAM and reached the service |
| `Resource: "*"` plus exact `connect:InstanceId` | Passed IAM and reached the service |

This is important future least-privilege guidance: granting the action on an instance alone is not
enough, and granting it on a powerful security profile alone is not enough. Every selected security
profile should be treated as a privilege-bearing resource.

The restricted caller had no Connect list, describe, user-management, Customer Profiles, or other
Connect permissions. `ListInstances` was explicitly exercised and remained denied.

## Service behavior matrix

All calls explicitly set both maximum and inactivity duration to the 1,440-minute documented
minimum. The dangerous documented 400-day default was never exercised.

| Request state | Caller/scope | Result |
| --- | --- | --- |
| Domain exists but is not associated | restricted wildcard + exact instance condition; built-in Admin profile and no-profile variants | `InvalidRequestException: Scope is invalid.` |
| Domain associated; synthetic profile exists | restricted wildcard + condition; built-in Admin and no-profile variants | HTTP 500 |
| Domain associated for more than 75 seconds | administrator; built-in Admin profile + exact entity | HTTP 500 |
| Same fully settled fixture | administrator; custom Customer Profiles View/Edit/Create profile + exact entity | HTTP 500 |
| Same fully settled fixture | restricted role; exact instance + built-in Admin security-profile ARNs + exact entity | HTTP 500 |

Botocore retried the 500 responses automatically, producing several identical attempts. Neither an
`AuthCode` nor a `SessionId` was returned in any run. Therefore code lifetime, redemption endpoint,
replay behavior, effective session permissions, response redaction, and `DeleteSession` revocation
remain unverified.

## Logging

`CreateAuthCode` appeared in CloudTrail Event History as a default management **write** event from
`connect.amazonaws.com` with `readOnly: false`. The request logged the instance ID, domain name,
entity ID, selected security-profile IDs, maximum duration, and inactivity duration. Failed calls
recorded `AccessDenied`, `InvalidRequestException`, or `InternalServerErrorException` and the error
message in `responseElements`.

Do not infer successful-event redaction from this evidence because no successful response occurred.
If the API later succeeds, verify specifically that `AuthCode` and `SessionId` are absent/redacted
before assigning a stealth rating. Automatic SDK retries also mean a service-side 500 can create a
short burst of identical management events.

## Safe retest gate

Revisit only when AWS publishes the missing workflow/redemption documentation or the same complete
fixture stops returning 500. Keep `MaxSessionDurationMinutes=1440`, hash rather than print the code,
never redeem it outside the synthetic domain, and call `DeleteSession` immediately by administrator
using the returned session ID. Then test the two exact resource ARNs again because the Service
Authorization Reference may have caught up.

## Cleanup verification

Every iteration deleted its IAM role, synthetic profile, Connect security profile, Customer Profiles
integration and domain, then deleted the Connect instance and waited for `DescribeInstance` to return
not found. Independent final inventories returned no matching roles, domains, instances, or unrevoked
sessions. No calls, telephony resources, real customer data, or long-lived session were created.

## References

- https://docs.aws.amazon.com/connect/latest/APIReference/API_CreateAuthCode.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_DeleteSession.html
- https://docs.aws.amazon.com/cli/latest/reference/connect/create-auth-code.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-customer-profiles_PutIntegration.html
- https://repost.aws/articles/ARe8Bdet5HTCOYZvomFk_M6A/integrating-an-amazon-connect-customer-profiles-domain-with-amazon-connect-by-api
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_connect.html
