# Bedrock AgentCore — attack ideas queue

## To verify (needs more setup / real integrations)
- [ ] End-to-end InvokeCodeInterpreter/InvokeAgentRuntime confirming code runs as the role (fetch 169.254 creds / boto3 sts get-caller-identity in the sandbox). PassRole gate already proven; runtime exec left doc-grounded.
- [ ] GetResourceApiKey full chain against a real api-key credential provider (create provider -> workload identity -> vend plaintext). Needs a provider + workload.
- [ ] GetWorkloadAccessTokenForUserId impersonation: mint a token for another user's workload identity.
- [ ] CreateGatewayTarget / interceptor abuse: register an attacker MCP tool target on an existing gateway (tool-poisoning of an agent).
- [ ] SetTokenVaultCMK / GetTokenVault: repoint token-vault KMS key (persistence/defense-evasion on stored secrets).
- [ ] CreateApiKeyCredentialProvider persistence: plant an attacker credential provider agents will use.

## Notes
- authorizerConfiguration.customJWTAuthorizer on CreateAgentRuntime/CreateGateway = the runtime trusts a JWT issuer -> rogue-issuer angle analogous to Identity Center TTI (see identity-center/tested.md). Potential IdP-backdoor lens on AgentCore.
