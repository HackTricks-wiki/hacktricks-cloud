# CodeArtifact authorization-token repository scope and IAM revocation — 2026-09-26

## Result

**NEGATIVE / secure behavior.** CodeArtifact bearer tokens remained bounded by the caller role's live effective `ReadFromRepository` permissions:

1. Tokens authorized for one repository could not ping a sibling repository in the same domain.
2. An explicit IAM deny revoked both already-issued tokens and newly minted tokens after a short propagation interval.
3. The repository remained healthy for an administrator token throughout the deny test.

This result does not add a public technique and does not warrant a private AWS vulnerability report.

## Why this was tested

CodeArtifact `GetAuthorizationToken` returns a bearer credential valid for 15 minutes to 12 hours. AWS states that repository access remains controlled by the caller's effective CodeArtifact permissions and specifically documents revoking tokens created from temporary credentials by adding an IAM deny. A token that crossed repository scope or survived a fully propagated explicit deny would have been a meaningful authorization failure.

## Fixture

- Region: `us-east-1`
- Disposable domain: `ht-ca-f817b64d70a6`
- Empty npm repositories: `allow` and `deny`
- No upstreams, external connections, packages, or package assets
- Restricted assumed role: `ht-ca-f817b64d70a6-reader/codeartifact-reader`
- Token lifetime: 900 seconds (the minimum nonzero value)

The restricted role had:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "codeartifact:GetAuthorizationToken",
      "Resource": "arn:aws:codeartifact:us-east-1:228478051196:domain/ht-ca-f817b64d70a6"
    },
    {
      "Effect": "Allow",
      "Action": "codeartifact:ReadFromRepository",
      "Resource": "arn:aws:codeartifact:us-east-1:228478051196:repository/ht-ca-f817b64d70a6/allow"
    },
    {
      "Effect": "Allow",
      "Action": "sts:GetServiceBearerToken",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "sts:AWSServiceName": "codeartifact.amazonaws.com"
        },
        "NumericLessThanEquals": {
          "sts:DurationSeconds": "900"
        }
      }
    }
  ]
}
```

Repository endpoints were resolved by the administrator before assuming this role, so `GetRepositoryEndpoint` was not part of the attacker permissions.

## Repository-scope matrix

The test sent the same HTTP request used by `npm ping` (`GET /-/ping?write=true`) with a bearer token. An empty repository is sufficient because AWS documents `npm ping` as verifying both authentication and `ReadFromRepository` authorization.

| Credential and target | Result |
| --- | --- |
| No token → `allow` | HTTP 401 |
| One-character-mutated restricted token → `allow` | HTTP 401 |
| Restricted token 1 → `allow` | HTTP 200 |
| Restricted token 1 → `deny` | HTTP 403 |
| Restricted token 2 → `allow` | HTTP 200 |
| Restricted token 2 → `deny` | HTTP 403 |
| Administrator token → `allow` | HTTP 200 |
| Administrator token → `deny` | HTTP 200 |

Token SHA-256 prefixes and mint request IDs, with no raw tokens retained:

| Token | SHA-256 prefix | `GetAuthorizationToken` request ID |
| --- | --- | --- |
| Administrator health token | `7a145d582505ef06` | `143e632e-7340-471b-a41e-58c71f14a49f` |
| Restricted pre-deny token 1 | `489116b5aaeabf04` | `a6f3f647-1859-4104-8a7d-fb2dd5232106` |
| Restricted pre-deny token 2 | `58342886bfacb4df` | `05d43e6c-e2c8-4fb2-916c-130f0b9db31f` |

## Live IAM-revocation matrix

The role's same inline policy was updated with:

```json
{
  "Effect": "Deny",
  "Action": "codeartifact:ReadFromRepository",
  "Resource": "arn:aws:codeartifact:us-east-1:228478051196:repository/ht-ca-f817b64d70a6/allow"
}
```

Every poll checked IAM simulation, both old tokens, a newly minted token, and the administrator health token:

| Elapsed after policy write | IAM simulation | Old token 1 | Old token 2 | New token | Admin health |
| --- | --- | --- | --- | --- | --- |
| 0.7 seconds | `explicitDeny` | 200 | 200 | 200 | 200 |
| 7.6 seconds | `explicitDeny` | 403 | 403 | 403 | 200 |

The first post-deny mint request ID was `06a385de-b5c8-46d6-9275-74500e0393c1`; the settled-deny mint request ID was `341e01e4-af65-441f-b35c-d292654a163e`.

Interpretation: IAM simulation reflected the policy before all CodeArtifact authorization paths had converged, but existing bearer tokens did not retain a permission snapshot. All old and new tokens honored the deny within 7.6 seconds, which is normal propagation behavior rather than a security issue.

## Logs and stealth notes

CloudTrail Event History confirmed that CodeArtifact recorded every package-manager ping as `ReadFromRepository`, including successes and failures:

| Event | Information |
| --- | --- |
| `GetAuthorizationToken` | Caller, domain, duration; token response is not logged |
| `ReadFromRepository` | Domain/repository, `httpMethod: GET`, and `requestUri: /npm/-/ping`; failed authorization includes `errorCode: AccessDenied` |
| `PutRolePolicy` | The explicit deny and policy update |
| `CreateDomain`, `CreateRepository`, `DeleteRepository`, `DeleteDomain` | Disposable fixture lifecycle |

This test is deliberately noisy because every package-manager request can become a `ReadFromRepository` event.

Examples from the settled-deny poll were success event `d3153e63-acc6-4eb4-9254-172ab7daa79b` for the administrator health token and denied event `caaec24d-2193-43bf-8d51-1647a7981130` for a restricted token. Invalid/no-token requests appeared with identity type `Unknown`; valid bearer tokens appeared as `AssumedRole` for the role that minted them.

## Cleanup

Cleanup order was both repositories, domain, inline role policy, and role. Independent post-test inventory confirmed:

- no domain whose name starts with `ht-ca-`;
- no IAM role whose name starts with `ht-ca-`.

The repositories were empty, so no stored package assets existed. Deleting the repositories/domain also made the still-unexpired test tokens unusable.

## References

- https://docs.aws.amazon.com/codeartifact/latest/ug/tokens-authentication.html
- https://docs.aws.amazon.com/codeartifact/latest/ug/npm-auth.html
- https://docs.aws.amazon.com/codeartifact/latest/ug/codeartifact-information-in-cloudtrail.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_codeartifact.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_bearer.html
