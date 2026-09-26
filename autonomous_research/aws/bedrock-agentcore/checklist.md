# Bedrock AgentCore — attack ideas queue

## To verify (needs more setup / real integrations)
- [x] End-to-end Harness `InvokeAgentRuntimeCommand`: verified UID 0 and `sts:GetCallerIdentity` as the passed execution role. Full harness ARN—not its generated runtime ARN or short ID—is the working SDK target. Separate CodeInterpreter/ordinary Runtime invocation remains untested.
- [x] GetResourceApiKey full chain against a real API-key provider and manually created workload
  identity: plaintext vend, exact multi-resource IAM boundary, backing Secrets Manager dependency,
  CloudTrail redaction, and cleanup verified. See `identity-credential-vend-2026-09-26.md`.
- [ ] GetWorkloadAccessTokenForUserId impersonation: mint a token for another user's workload identity.
- [ ] CreateGatewayTarget / interceptor abuse: register an attacker MCP tool target on an existing gateway (tool-poisoning of an agent).
- [ ] SetTokenVaultCMK / GetTokenVault: repoint token-vault KMS key (persistence/defense-evasion on stored secrets).
- [ ] CreateApiKeyCredentialProvider persistence: plant an attacker credential provider agents will use.

## Notes
- authorizerConfiguration.customJWTAuthorizer on CreateAgentRuntime/CreateGateway = the runtime trusts a JWT issuer -> rogue-issuer angle analogous to Identity Center TTI (see identity-center/tested.md). Potential IdP-backdoor lens on AgentCore.
