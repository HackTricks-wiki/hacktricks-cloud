# Cognito M2M client-secret creation — 2026-09-26

## Result

Verified expected post-exploitation path: a principal with only `cognito-idp:AddUserPoolClientSecret` on one user-pool ARN can create and retrieve a new app-client secret. For a pre-existing M2M client, that secret can immediately call the public `GetClientToken` operation and obtain a bearer JWT with the client's configured custom scopes. `GetClientToken` does not evaluate IAM.

This is documented product behavior, not an AWS vulnerability. It is security-sensitive because an apparently narrow secret-rotation action is sufficient to impersonate the machine client without `DescribeUserPoolClient`, `ListUserPoolClientSecrets`, or an IAM permission for the token exchange.

## Fixture

A disposable `us-east-1` user pool contained:

- resource server `https://ht-m2m-98ee2073e4.invalid`;
- custom scope `canary.read`;
- one confidential app client whose only explicit flow was `ALLOW_CLIENT_TOKEN_AUTH`;
- a five-minute access-token lifetime;
- one initial generated secret.

The narrow caller allowed only:

```json
{
  "Effect": "Allow",
  "Action": "cognito-idp:AddUserPoolClientSecret",
  "Resource": "arn:aws:cognito-idp:us-east-1:228478051196:userpool/us-east-1_Lz6tsISUV"
}
```

It explicitly denied `ListUserPoolClientSecrets`, `DescribeUserPoolClient`, `UpdateUserPoolClient`, and `DeleteUserPoolClientSecret`. The list negative control returned `AccessDeniedException` before the successful add.

## Proof

Before the attack the client had one active secret. Calling `AddUserPoolClientSecret` without supplying a value returned both a new `ClientSecretId` and generated `ClientSecretValue`; afterwards the client had two active secrets. An administrator's `ListUserPoolClientSecrets` response contained metadata for both but did not expose either value.

An unsigned/public `GetClientToken` call with a deliberately wrong secret returned `NotAuthorizedException: Invalid client or secret`. The same call with the newly generated value returned:

- a non-empty bearer access JWT;
- `expires_in=300`;
- the exact expected app-client ID in the token;
- `token_use=access`;
- exact scope `https://ht-m2m-98ee2073e4.invalid/canary.read`;
- an observed `exp-iat` lifetime of 300 seconds.

Only SHA-256 digests were retained. No secret or JWT value was written to the repository or opened against a downstream API.

## Boundaries and useful negatives

- The add action does not change the app client's enabled authentication flows or scopes. A client must already permit `ALLOW_CLIENT_TOKEN_AUTH` for `GetClientToken` to work.
- M2M access is whatever downstream resource servers grant to the configured scopes; the JWT is not an AWS access-key credential.
- A user-pool client supports at most two active secrets. An already-full client rejects another add.
- `ListUserPoolClientSecrets` is not required and does not reveal secret values.
- `DeleteUserPoolClientSecret` is a separate permission; an attacker need not possess it to use the secret they just created.

## Detection

Historical and current `AddUserPoolClientSecret` events appeared as default CloudTrail management writes. Observed successful event structure included the pool ID and client ID in `requestParameters`, the new secret ID in `responseElements`, and the literal redaction `HIDDEN_DUE_TO_SECURITY_REASONS` instead of the value. Secret deletion is also a management write keyed by the secret ID.

At the time of the test, CloudTrail Event History returned no `GetClientToken` event. Treat that public token operation as potentially visible through Cognito/resource-server application telemetry rather than relying on Event History. The high-fidelity detection point is the uncommon secret-add management event. Overall stealth: **Low**.

## Cleanup verification

The harness deleted the newly added secret explicitly before deleting the app client, resource server, and user pool. It then deleted the narrow IAM role and independently listed matching pools and roles. Both inventories were empty. No users or real resource server existed.

## References

- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AddUserPoolClientSecret.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DeleteUserPoolClientSecret.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_ListUserPoolClientSecrets.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_GetClientToken.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-define-resource-servers.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncognitouserpools.html
