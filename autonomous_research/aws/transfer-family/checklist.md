# AWS Transfer Family — open ideas

- [x] CreateUser/UpdateUser/CreateAccess + PassRole role-choice privesc — DONE, authz VERIFIED. tested.md.
- [x] ImportSshPublicKey user impersonation — already documented on the wiki page (pre-existing).
- [x] **Custom Lambda IdP takeover** — VERIFIED end to end. Exact-function `lambda:UpdateFunctionCode`
  alone can accept an attacker login, return a Transfer-trusting role without PassRole, capture the
  plaintext password, and read role-authorized S3 data over SFTP. Exact-server `transfer:UpdateServer`
  alone can repoint to an already server-authorized Lambda with the same result.
- [x] **PUBLIC_KEY_AND_PASSWORD response binding / malformed Policy** — VERIFIED. Both factors enforced;
  the password response supplies the effective role/policy/home when responses differ. Malformed
  nonempty policies failed closed at authentication or role use; empty/omitted policy intentionally
  gives the base role; IAM intersection held. No independent boundary crossing, so no AWS report.
- [x] **Plaintext password in Lambda custom-IdP logs** — exact synthetic canary recovered with
  `logs:FilterLogEvents`; published as Transfer Family post-exploitation.
- [x] **API Gateway custom IdP takeover** — VERIFIED. Exact integration-response PATCH plus production
  deployment accepted an attacker password and selected a Transfer role without PassRole.
- [x] **Secrets Manager legacy IdP-record poisoning** — VERIFIED end to end. Exact-secret
  `PutSecretValue` installed an attacker password and selected a high Transfer role without Get,
  PassRole, Transfer/Lambda/API Gateway, or direct S3 access.
- [ ] **DynamoDB toolkit IdP-record poisoning** — change the newer toolkit's role/policy/home record
  without Lambda or Transfer mutation permissions; keep distinct from its Secrets Manager credential.
- [x] **UpdateServer logging disable** — VERIFIED. Exact-server UpdateServer alone, with explicit
  `logs:*` and PassRole denies, cleared legacy and structured logging separately and together ONLINE.
- [x] **TestIdentityProvider oracle** — VERIFIED exact-user scope, caller-controlled `SourceIp`,
  password redaction, full response logging, and no protocol session/role assumption.
- [ ] **DescribeUser/ListUsers** recon of which roles are bound to which users (target selection).
