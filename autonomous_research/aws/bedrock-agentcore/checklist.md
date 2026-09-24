# AWS Bedrock AgentCore — open ideas (compute/GA-gated; non-duplicate)

- [ ] **SetTokenVaultCMK re-key** — point the AgentCore Identity token vault at an attacker-influenced
  KMS key, or a key later denied/deleted, to lock out / control access to all stored OAuth tokens &
  API keys (DoS/persistence over the identity plane). Verify it's a real access-control pivot vs pure
  DoS before documenting. Needs AgentCore Identity onboarded.
- [ ] **AgentCore Payments** (`CreatePaymentCredentialProvider`, `CreatePaymentConnector`,
  `GetResourcePaymentToken`, `GetPaymentInstrumentBalance`) — brand-new payment credential plane;
  investigate whether GetResourcePaymentToken vends a usable payment token to any authorized caller
  (secret-exfil parallel to GetResourceOauth2Token). Revisit when public docs/GA exist.
- [ ] **CreateApiKeyCredentialProvider / CreateOauth2CredentialProvider persistence** — plant an
  attacker credential provider so agents authenticate outbound with attacker-controlled creds, or
  read clientSecretArn/apiKeySecretArn (points at Secrets Manager) — check if distinct from the
  existing GetResource* vend coverage.
