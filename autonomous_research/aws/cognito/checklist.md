# Cognito — open ideas

- [ ] **Authenticator-enrollment persistence (WebAuthn/passkey)** — enroll an attacker-controlled
  passkey on a victim user pool user for durable MFA-backed access. DEFERRED: needs a WebAuthn
  attestation library to mint a valid attestation object; not trivial to script. Revisit with a
  helper lib. TOTP-only variant is weak (still requires knowing/resetting the secret) — low value.
- [ ] **Identity-pool role-mapping abuse** — `cognito-identity:SetIdentityPoolRoles` /
  ambiguous role-resolution + `GetCredentialsForIdentity`: can a low-priv authenticated identity
  be mapped to a higher-priv role via a permissive `RoleMappings` rule? Check against the existing
  cognito privesc page to avoid duplicating.
- [ ] **User-pool client secret / callback-URL tamper** as a phishing/token-theft persistence: add
  an attacker callback URL to an app client (`UpdateUserPoolClient`) to capture auth codes. Verify
  it's not already covered by the cognito persistence page.
