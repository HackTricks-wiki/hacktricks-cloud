# Bedrock AgentCore — tested & documented (NEW PAGE)

Service: bedrock-agentcore (data plane) / bedrock-agentcore-control (control). IAM prefix bedrock-agentcore:. Brand-new GA service, ZERO prior wiki coverage.

## VERIFIED (lab 228478051196, us-east-1)
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

## Credential vend (data plane; documented from model, sensitive:true outputs)
- Chain: GetWorkloadAccessToken(workloadName) -> workloadIdentityToken -> GetResourceApiKey(token,provider) => plaintext apiKey (sensitive:true). Also GetResourceOauth2Token -> accessToken, GetResourcePaymentToken.
- GetWorkloadAccessTokenForJWT/ForUserId mint tokens on behalf of a user (impersonation of a workload identity).
- Control-plane Get*CredentialProvider returns only apiKeySecretArn/clientSecretArn (Secrets Manager ARN, NOT plaintext) -> confirms calibration; enum-to-secret pointer. Data plane returns plaintext.

## Teardown
Deleted ht-ac-attacker, ht-ac-target roles; deleted code interpreter; no agent runtimes created (both errored pre-create). Verified: no ht-* roles, no code-interpreters, no agent-runtimes.

## Where
NEW page aws-privilege-escalation/aws-bedrock-agentcore-privesc/README.md; SUMMARY wired after Bedrock Privesc. Refs [1][2][3][4].
