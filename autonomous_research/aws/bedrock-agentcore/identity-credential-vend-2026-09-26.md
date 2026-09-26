# AgentCore Identity API-key credential vend — verified 2026-09-26

## Result

Verified end to end in account `228478051196`, `us-east-1`: a restricted role minted a workload access
token for a manually created workload identity and exchanged it for the exact 40-character synthetic
canary stored by an API-key credential provider. `GetResourceApiKey` returned the key in plaintext. This
is expected credential-provider functionality, not an AWS vulnerability.

The caller did not invoke Secrets Manager directly. AgentCore made a backing `GetSecretValue` request
under the caller's identity, making access to the managed secret an additional authorization boundary.

## Minimum-permission and resource-omission matrix

`bedrock-agentcore:GetWorkloadAccessToken` required both resources:

1. `arn:aws:bedrock-agentcore:us-east-1:228478051196:workload-identity-directory/default`
2. the exact child `.../workload-identity/<name>` ARN

`bedrock-agentcore:GetResourceApiKey` required all four resources:

1. `arn:aws:bedrock-agentcore:us-east-1:228478051196:token-vault/default`
2. the exact `.../apikeycredentialprovider/<name>` ARN
3. the default workload-identity-directory ARN
4. the exact workload-identity ARN

Each resource was removed from an otherwise working restricted policy one at a time. Every omission
failed with `AccessDenied` naming the missing ARN. The caller additionally required
`secretsmanager:GetSecretValue` on the exact `apiKeySecretArn.secretArn` returned by the provider's
control-plane response. Removing only this statement allowed workload-token minting but made
`GetResourceApiKey` fail on the managed secret ARN.

No list/get-provider permission, direct client-side Secrets Manager operation, runtime, gateway, or
`iam:PassRole` was required. The provider secret name contains generated components, so defenders should
obtain its exact ARN from the provider metadata or use a carefully bounded provider-name prefix.

## CloudTrail

Both successful AgentCore calls appeared in default Event History:

| Event | Classification | Sensitive-field handling |
| --- | --- | --- |
| `GetWorkloadAccessToken` | `AwsApiCall`, Management, `managementEvent:true`, `readOnly:false` | response token was `HIDDEN_DUE_TO_SECURITY_REASONS` |
| `GetResourceApiKey` | `AwsApiCall`, Management, `managementEvent:true`, `readOnly:false` | request workload token and response API key were hidden; provider name remained visible |
| backing `GetSecretValue` | Secrets Manager Management, `readOnly:true` | attributed to the restricted caller; response omitted |

Provider creation logged the submitted key as `***` and exposed only the managed secret ARN/source in
its response. A failed vend lacking Secrets Manager permission placed the secret ARN in the AgentCore
event's error message but did not reveal the secret value.

## Cleanup

The API-key provider, workload identity, restricted role policy, and restricted IAM role were deleted.
Independent verification found:

- provider `Get` -> `ResourceNotFound` and provider list empty;
- workload `Get` -> `ResourceNotFound` and exact list matches zero;
- IAM role -> `NoSuchEntity`;
- managed secret -> `ResourceNotFound`, with no exact match even when listing planned deletions.

CloudTrail showed the service-owned cleanup calling `DeleteSecret` with
`forceDeleteWithoutRecovery:true`; no recovery-window secret remained. No runtime, gateway, compute,
external credential, or persistent account setting was created.

## Sources

- <https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_GetWorkloadAccessToken.html>
- <https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_GetResourceApiKey.html>
- <https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/scope-credential-provider-access.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_bedrock-agentcore.html>
