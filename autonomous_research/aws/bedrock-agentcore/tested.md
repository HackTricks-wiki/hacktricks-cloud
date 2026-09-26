# Bedrock AgentCore — tested & documented (NEW PAGE)

Service: bedrock-agentcore (data plane) / bedrock-agentcore-control (control). IAM prefix bedrock-agentcore:. Brand-new GA service, ZERO prior wiki coverage.

## VERIFIED (lab 228478051196, us-east-1)
### CreateHarness + iam:PassRole + InvokeAgentRuntimeCommand -> root shell as executionRoleArn (SHIPPED)
- NEG (composite AgentCore create actions, no PassRole) -> explicit `AccessDeniedException` on `iam:PassRole` for the supplied role.
- POS (+ exact-role PassRole) -> harness reached `READY`; full harness ARN passed to `InvokeAgentRuntimeCommand` returned UID `0`, exit code `0`, and the STS assumed-role ARN for the supplied execution role.
- Live dependency discovery found composite gates beyond the short AWS permissions table: `CreateAgentRuntimeEndpoint`, `CreateWorkloadIdentity`, and `GetAgentRuntime`; final working set is recorded in `harness-command-privesc-2026-09-26.md`.
- CloudTrail Event History captured positive and negative `CreateHarness` events with `executionRoleArn`; command invocation is a data event and was absent with data-event logging disabled. Runtime CloudWatch export failed without `logs:PutLogEvents`, but the command succeeded.
- All disposable harness/IAM resources deleted; service-linked-role deletion polled separately because it is asynchronous.

### CreateCodeInterpreter + iam:PassRole -> code-exec sandbox as executionRoleArn (SHIPPED)
- NEG (CreateCodeInterpreter, executionRoleArn set, NO iam:PassRole) -> `AccessDeniedException ... iam:PassRole on resource: .../ht-ac-target because no identity-based policy allows the iam:PassRole action`.
- POS (+ iam:PassRole) -> SUCCEEDED, returned codeInterpreterId htAcProbe-... status READY with the passed executionRoleArn. Deleted (status DELETED).
- Min perms: bedrock-agentcore:CreateCodeInterpreter + iam:PassRole (bedrock-agentcore-trusting target) + bedrock-agentcore:InvokeCodeInterpreter to run.

### CreateAgentRuntime (+CreateAgentRuntimeEndpoint) + iam:PassRole -> run attacker container as roleArn (SHIPPED)
- roleArn REQUIRED. Creating a runtime also provisions its default endpoint -> needs CreateAgentRuntime + CreateAgentRuntimeEndpoint too.
- POS (has PassRole, bogus containerUri) -> passed iam:PassRole, advanced to next gate: AccessDenied on bedrock-agentcore:CreateAgentRuntimeEndpoint (proves PassRole passed + revealed the 2nd required action).
- NEG (endpoint action allowed, NO PassRole) -> AccessDenied on iam:PassRole on ht-ac-target. Two-sided isolated.
- Min perms: CreateAgentRuntime + CreateAgentRuntimeEndpoint + iam:PassRole; InvokeAgentRuntime to execute.

## DOC-GROUNDED (same PassRole class, not separately fired)
- CreateBrowser + executionRoleArn (same gate as CodeInterpreter).
- UpdateAgentRuntime/UpdateGateway + iam:PassRole repoint (same gate, reuses existing resource).
- CreateGateway (roleArn), CreateMemory (memoryExecutionRoleArn), etc.

## Credential vend (live API-key chain; OAuth/payment siblings documented from model)
- Chain: GetWorkloadAccessToken(workloadName) -> workloadIdentityToken -> GetResourceApiKey(token,provider) => plaintext apiKey (sensitive:true). Also GetResourceOauth2Token -> accessToken, GetResourcePaymentToken.
- GetWorkloadAccessTokenForJWT/ForUserId mint tokens on behalf of a user (impersonation of a workload identity).
- Control-plane Get*CredentialProvider returns only apiKeySecretArn/clientSecretArn (Secrets Manager ARN, NOT plaintext) -> confirms calibration; enum-to-secret pointer. Data plane returns plaintext.
- Live 2026-09-26: isolated role retrieved the exact synthetic canary. Both directory/workload ARNs were
  independently required for workload-token minting; vault/provider/directory/workload ARNs were each
  independently required for the API-key vend. `secretsmanager:GetSecretValue` on the exact managed
  secret was an additional mandatory permission because AgentCore reads it under the caller's identity.
  Both AgentCore calls were default management events with `readOnly:false`; secrets were hidden. Full
  evidence and cleanup are in `identity-credential-vend-2026-09-26.md`.

## Teardown
- Original Runtime/CodeInterpreter probe: deleted ht-ac-attacker and ht-ac-target roles and the code interpreter; no ordinary agent runtime was created (both calls errored pre-create).
- Harness probe: deleted every disposable harness, its managed Runtime/Memory, both IAM users/keys/policies, execution role, and the Runtime Identity service-linked role. Final independent list/get checks found no matching residue.

## Where
NEW page aws-privilege-escalation/aws-bedrock-agentcore-privesc/README.md; SUMMARY wired after Bedrock Privesc. Refs [1][2][3][4].
