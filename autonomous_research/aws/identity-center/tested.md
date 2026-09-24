# Identity Center / SSO — tested & documented

## sso-admin:CreateTrustedTokenIssuer — rogue trusted token issuer (SHIPPED, doc-grounded)
- **Lens:** identity-provider / trusted-token-issuer backdoor (federate in via an IdP you control).
- **Gap:** book-wide grep for `trusted token issuer|trusted identity propagation|CreateTrustedTokenIssuer|CreateTokenWithIAM|PutApplicationGrant` = 0 hits. Genuinely undocumented.
- **Technique:** register an attacker-controlled OIDC issuer as a TTI (attacker owns signing keys), mapping a claim (e.g. `email`) to Identity Center users. Mint a JWT asserting any target user's claim, exchange via `sso-oidc:CreateTokenWithIAM` (JWT-bearer grant) for an identity-enhanced session → impersonate that user inside every trusted-identity-propagation app (Q Business, Redshift, QuickSight, S3 Access Grants). If no app exists, stand one up with CreateApplication + PutApplicationGrant(JWT_BEARER) + CreateApplicationAssignment. Also a persistence backdoor.
- **Impact:** impersonation of arbitrary IdC users → their app-layer data access; durable backdoor.
- **Verification status:** DOC-GROUNDED, not lab-fired. Lab account 228478051196 is an Org *member* account with NO Identity Center instance (`aws sso-admin list-instances` → `Instances: []`). IdC lives only in the Org management account; enabling IdC org-wide is heavy and not cleanly reversible (violates teardown rule), so live-firing was skipped per the cost/precondition exception. Mechanism is documented AWS behavior (TTI claim mapping + JWT-bearer grant), high confidence.
- **Where:** aws-privilege-escalation/aws-sso-and-identitystore-privesc/README.md — new section before References; refs [18][19][20].
- **Min perms:** `sso-admin:CreateTrustedTokenIssuer` (core); optionally `sso-admin:CreateApplication`, `sso-admin:PutApplicationGrant`, `sso-admin:CreateApplicationAssignment` if no TTP app already exists. Downstream: attacker's own OIDC issuer + `sso-oidc:CreateTokenWithIAM` at exploit time.

## Prior coverage confirmed (not re-shipped)
- CreateSAMLProvider / CreateOpenIDConnectProvider / UpdateOpenIDConnectProviderThumbprint / AddClientIDToOpenIDConnectProvider — covered in aws-iam-privesc + aws-iam-persistence.
- Cognito CreateIdentityProvider — covered in aws-cognito-privesc + aws-cognito-persistence.
