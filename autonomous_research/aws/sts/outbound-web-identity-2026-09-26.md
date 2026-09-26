# STS outbound web-identity token boundary — deferred 2026-09-26

## Candidate and security value

`sts:GetWebIdentityToken` returns an AWS-signed JWT representing the calling AWS identity. An external
service that trusts the account-specific issuer can exchange or directly authorize that token, so the
permission is a potential cross-cloud/SaaS credential-minting primitive. The caller chooses one to ten
audiences, a 60-to-3600-second lifetime, the signing algorithm, and up to 50 custom tags. AWS documents
separate `sts:TagGetWebIdentityToken` authorization for supplying tags.

This is not automatically privilege escalation: impact depends on which external services trust the
account issuer, their audience and subject validation, and how they map AWS identity/session/tag claims.
A useful public technique requires an enabled account plus a controlled external relying party proving
that a restricted AWS principal obtains additional external access.

## Live preflight result

The authorized account `228478051196` is not enabled. The following read-only calls were repeated in
`us-east-1` under `ChackBotAdministratorRole`:

```text
GetOutboundWebIdentityFederationInfo:
FeatureDisabled: Outbound identity federation is disabled for account 228478051196

GetWebIdentityToken(audience=https://example.invalid, duration=60, algorithm=ES384):
OutboundWebIdentityFederationDisabledException: OutboundWebIdentityFederation is disabled.
```

AWS says the feature must first be enabled with the account-level
`iam:EnableOutboundWebIdentityFederation` operation and that token generation is unavailable on the
global STS endpoint. Enabling the feature would be a persistent account-security configuration change,
not a disposable resource needed merely for a canary, so it was deliberately not performed.

## Future minimum-permission matrix

When an explicitly enabled disposable account and controlled relying party are available:

| Case | Minimum caller authorization | Expected secure result |
| --- | --- | --- |
| Fixed audience and short lifetime | `sts:GetWebIdentityToken` on `*`, restricted by `sts:IdentityTokenAudience` and `sts:DurationSeconds` | JWT contains the authorized audience and expires at the policy-bound lifetime |
| Caller-supplied tags | Previous permission plus `sts:TagGetWebIdentityToken` | Tags appear only when both authorizations permit them |
| Unauthorized audience/lifetime | Same constrained policy | IAM denial before a token is minted |
| Global endpoint request | Otherwise valid policy | Rejected; regional endpoint required |
| AWS inbound replay | Valid outbound JWT | `AssumeRoleWithWebIdentity` must not accept it for federation back into AWS |

The relying party must validate issuer, audience, expiration, and subject; otherwise the bug belongs to
that relying party's trust configuration rather than STS. Also test whether principal tags and request
tags can be confused, whether multiple audiences widen trust unexpectedly, and whether role-session
identity is consistently bound across fresh STS sessions.

## Logging expectations

Do not publish telemetry claims until live validation is possible. The future test must check CloudTrail
for `GetWebIdentityToken`, determine whether it is a default management event, and record whether the
audience, duration, algorithm, and tag keys/values are logged. Never place the returned JWT in the
research repository or a command transcript.

## Cleanup

No AWS resources or persistent settings were created. The two preflight operations were read-only. No
token was minted.

## Sources

- <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_getting_started.html>
- <https://docs.aws.amazon.com/cli/latest/reference/sts/get-web-identity-token.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssecuritytokenservice.html>
