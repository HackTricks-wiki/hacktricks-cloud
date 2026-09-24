# AWS Bedrock AgentCore — coverage review (2026-09-24)

Reviewed the full bedrock-agentcore + bedrock-agentcore-control models against the book.
**Result: already comprehensively covered — no net-new page made (no-duplicate bar).**

Already documented (verified present):
- AgentCore Identity token vending: `GetWorkloadAccessToken` -> `GetResourceApiKey` (stored 3rd-party
  API key) and `GetResourceOauth2Token` (stored OAuth access token) — aws-bedrock-enum.md.
- `CreateAgentRuntime` (+ endpoint, iam:PassRole) execution-role pivot — aws-bedrock-privesc.
- `StartCodeInterpreterSession`+`InvokeCodeInterpreter` execution-role pivot — aws-bedrock-privesc.
- AgentCore Sandbox Escape (Runtime SSRF->MMDS creds, DNS tunneling) — aws-bedrock-post-exploitation.
- `PutResourcePolicy` — resource-policy principal-validation matrix.

Not separately documented, but assessed near-duplicate of the CreateAgentRuntime pivot (SAME
PassRole-execution-role pattern) -> intentionally NOT manufactured:
`CreateGateway/UpdateGateway roleArn`, `CreateBrowser/CreateHarness executionRoleArn`,
`CreateMemory memoryExecutionRoleArn`, `CreateOnlineEvaluationConfig evaluationExecutionRoleArn`.
