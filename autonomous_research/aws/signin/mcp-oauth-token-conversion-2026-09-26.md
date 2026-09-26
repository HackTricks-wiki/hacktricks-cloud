# Sign-In AWS MCP OAuth token conversion — 2026-09-26

## Result

Verified expected post-exploitation path: `signin:CreateOAuth2Token` on the exact AWS MCP service-principal ARN was sufficient to call `CreateOAuth2TokenWithIAM` and convert a short-lived IAM role session into a bearer JWT issued for the `aws-mcp.amazonaws.com` audience.

This is a credential-format converter, not AWS privilege escalation. Official AWS documentation states that AWS MCP retains the source identity, permissions and governance. It is still valuable to attackers because the portable bearer token can be handed to MCP-capable tooling without disclosing the original access-key secret and session token.

This result supersedes the old research-register entry that treated `signin:CreateOAuth2Token` as an internal/unverifiable operation; AWS published the non-interactive AWS MCP flow in 2026 and the API is live.

## Least-privilege proof

The disposable caller role allowed:

```json
{
  "Effect": "Allow",
  "Action": "signin:CreateOAuth2Token",
  "Resource": "arn:aws:signin:us-east-1:228478051196:service-principal/aws-mcp.amazonaws.com",
  "Condition": {
    "StringEquals": {
      "signin:OAuthGrantType": "client_credentials"
    }
  }
}
```

It explicitly denied `signin:IntrospectOAuth2Token`, `signin:RevokeOAuth2Token`, `sts:GetFederationToken`, and further `sts:AssumeRole` from inside the test session. Requesting `not-a-real-service.invalid` returned `AccessDeniedException`. Requesting `aws-mcp.amazonaws.com` succeeded.

## Credential result

The successful response contained:

- a non-empty OAuth access token;
- `tokenType=Bearer`;
- a JWT audience of exactly `aws-mcp.amazonaws.com`;
- `expiresIn=899`;
- an encoded `exp-iat` lifetime of 899 seconds.

The caller's STS session had 900 seconds remaining, proving the documented rule that non-interactive tokens expire at the shorter of one hour or the remaining source-session duration. No refresh token was returned.

Only a SHA-256 digest and selected nonsensitive claims were retained. The JWT was never submitted to AWS MCP or any other service.

## Boundaries

- The token does not grant permissions beyond the originating IAM principal.
- The `resource` request parameter is `aws-mcp.amazonaws.com`, while IAM authorization scopes the corresponding ARN in the account and Region.
- `signin:OAuthGrantType=client_credentials` prevents reuse of the grant for interactive authorization-code or refresh-token flows.
- Non-interactive issuance returns no refresh token. AWS states existing access tokens remain valid until they expire; revoking a refresh token cannot end one early.
- Immediate containment requires revoking/denying the underlying AWS/Sign-In session, including use of `aws:SignInSessionArn` where appropriate.

## Logging and stealth

The successful call appeared in CloudTrail with `eventSource=signin.amazonaws.com`, `eventName=CreateOAuth2Token`, `readOnly=true`, `managementEvent=true`, target `aws-mcp.amazonaws.com`, client ID `arn:aws:signin:::client-credentials/sigv4`, and the Sign-In session ARN plus `grant_type=client_credentials` in `additionalEventData`. `responseElements` was null, so the token itself was omitted. Overall stealth is **Medium**: the issuance read is visible, but it can resemble ordinary approved agent use.

## Cleanup verification

No persistent AWS application/service resource was created. The harness deleted the narrow caller's inline policy and IAM role and independently listed matching roles; final inventory was empty. The unexercised bearer token had no revocation mechanism and expired naturally after 899 seconds.

## References

- https://docs.aws.amazon.com/signin/latest/userguide/aws-mcp-server.html
- https://docs.aws.amazon.com/signin/latest/APIReference/API_dataplane-signin_CreateOAuth2TokenWithIAM.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_signin.html
