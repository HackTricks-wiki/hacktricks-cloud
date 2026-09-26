# STS outbound web-identity token boundary — live verified 2026-09-26

## Result

`sts:GetWebIdentityToken` is a real external/SaaS credential-minting primitive when account-level
outbound identity federation is enabled and an external relying party already trusts the account's
OIDC issuer. It is not native AWS privilege escalation: AWS rejects an outbound token passed to
`AssumeRoleWithWebIdentity`.

The authorized lab account `228478051196` was enabled briefly in `us-east-1`. An isolated role minted
only 60-second synthetic-canary tokens. No JWT was printed, transmitted to a third party, or stored.
The feature was disabled and the role was deleted after testing.

## Verified token and endpoint behavior

- The operation worked only through a regional STS endpoint, not the global endpoint.
- The representative response contained a 1,239-character JWT and a separate expiration field.
- Local decoding, without recording the token, showed an `RS256` header and the expected issuer,
  audience, IAM role subject, issued-at time, and expiration exactly 60 seconds later.
- The `sub` claim was the underlying `arn:aws:iam::228478051196:role/...` role ARN, not the assumed-role
  session ARN. Relying parties that authorize only on `sub` therefore collapse distinct sessions of
  the same role and should inspect appropriate AWS-namespaced session/source-context claims too.
- OIDC discovery returned the same issuer as the token, and exactly one published JWKS key matched the
  JWT `kid`.
- The API accepts one to ten audiences, a 60-to-3,600-second lifetime (300 seconds by default), and
  `RS256` or `ES384`. Optional request tags become custom claims only with the additional dependent
  authorization action.

## Exact tested minimum authorization

This policy succeeded for the isolated principal:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:GetWebIdentityToken",
    "Resource": "arn:aws:sts::228478051196:self",
    "Condition": {
      "ForAllValues:StringEquals": {
        "sts:IdentityTokenAudience": "urn:hacktricks:test:228478051196"
      },
      "NumericLessThanEquals": {
        "sts:DurationSeconds": "60"
      },
      "StringEquals": {
        "sts:SigningAlgorithm": "RS256"
      }
    }
  }]
}
```

Despite examples using `"Resource": "*"`, the exact pseudo-resource
`arn:aws:sts::<account-id>:self` worked and also appeared in authorization errors. Negative tests
confirmed that a different audience and a 61-second lifetime were denied.

A request containing a tag was denied until the caller also had `sts:TagGetWebIdentityToken` on the
same `self` resource. This is a dependent permission for the `GetWebIdentityToken` request, not a
separate API call. Production grants should additionally constrain `aws:TagKeys` and
`aws:RequestTag/<key>`.

## CloudTrail

Event History recorded successful issuance as:

```text
eventSource: sts.amazonaws.com
eventName: GetWebIdentityToken
eventType: AwsApiCall
eventCategory: Management
managementEvent: true
readOnly: false
```

The request recorded audience, duration, and signing algorithm. The successful response recorded only
`webIdentityTokenId` (a UUID) and expiration, not the JWT. Denied policy tests were also management
events. Tagged calls still generate `GetWebIdentityToken`; there is no separate
`TagGetWebIdentityToken` CloudTrail event. Feature enablement was recorded as
`iam.amazonaws.com` / `EnableOutboundWebIdentityFederation`, and disabling produces the corresponding
IAM management event. Subsequent use of a JWT at the relying party is outside AWS CloudTrail.

## Security interpretation

The external service must already trust the account-specific issuer and authorize the token's subject,
audience, and claims. Depending on that mapping, the token may directly grant external access or may be
exchanged for a service-specific credential. A relying party must validate signature/JWKS, exact
issuer and audience, expiration, expected subject, and—where distinct sessions matter—the appropriate
session/source-context claims. Caller-controlled request tags must not be trusted as authoritative
tenant or privilege assertions.

Defenders should keep the account feature disabled if unused; restrict the action to the exact `self`
ARN; allow-list audiences; cap lifetime; pin the signing algorithm; separately restrict or omit tag
authorization; and alert on enable/disable plus unexpected issuance events.

## Cleanup and residual public metadata

- `GetOutboundWebIdentityFederationInfo` returned `FeatureDisabled` after cleanup.
- A fresh token request returned `OutboundWebIdentityFederationDisabledException`.
- The disposable IAM role returned `NoSuchEntity`, and a name-filtered inventory found no role,
  inline policy, or other test fixture.
- The last token expired at `2026-09-26T17:44:48Z`; cleanup verification occurred after
  `2026-09-26T17:45:12Z`.
- OIDC discovery and JWKS URLs continued to return HTTP 200 after disable. They expose public metadata
  and verification keys, not credentials. AWS provides no separate metadata-delete operation, and
  keeping keys available allows validation of tokens that were issued before disable.

AWS documents that disabling prevents new token issuance but does not revoke already-issued tokens.
Defenders must therefore wait for the maximum allowed token lifetime after disabling.

## Sources

- <https://docs.aws.amazon.com/STS/latest/APIReference/API_GetWebIdentityToken.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_getting_started.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_token_claims.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_sts.html>
- <https://aws.amazon.com/about-aws/whats-new/2025/11/aws-iam-identity-federation-external-services-jwts/>
- <https://aws.amazon.com/blogs/aws/simplify-access-to-external-services-using-aws-iam-outbound-identity-federation/>
