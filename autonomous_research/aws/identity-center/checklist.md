# Identity Center / SSO — attack ideas queue

## Parked (verify against an account with IdC enabled)
- [ ] CreateTrustedTokenIssuer end-to-end: register rogue OIDC TTI, mint JWT, CreateTokenWithIAM exchange, hit a Q Business app as impersonated user. Needs IdC instance + a TTP app. (Shipped doc-grounded; lab has no IdC instance.)
- [ ] UpdateTrustedTokenIssuer — repoint an EXISTING legit TTI's IssuerUrl/JwksRetrievalOption to attacker infra (stealthier than creating a new one; reuses trusted name). Repoint-lens applied to TTI.
- [ ] UpdateApplication / PutApplicationAuthenticationMethod — weaken an existing TTP app's auth to accept attacker tokens.
- [ ] sso-oidc dynamic client registration abuse (RegisterClient) as a foothold for token exchange.

## Dead / covered lenses (identity-provider axis)
- IAM SAML/OIDC provider create+update — covered (iam-privesc/iam-persistence).
- Cognito user-pool IdP — covered (cognito-privesc/persistence).
- iot:CreateAuthorizer / apigateway:CreateAuthorizer — custom-authorizer auth bypass: candidate, but value is app-specific (bypasses only that API/IoT domain's authz, not AWS IAM). Evaluate for a service-enum page rather than privesc; low IAM-privesc value.
