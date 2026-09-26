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
- [ ] **API Gateway custom IdP takeover** — test integration-response/deployment mutation without
  PassRole and the documented password-header logging exposure.
- [ ] **Secrets Manager / DynamoDB IdP-record poisoning** — change role/policy/key/password/home without
  Lambda or Transfer mutation permissions, following the AWS templates/toolkit.
- [ ] **UpdateServer --logging-role** repoint or disable to blind access logging (anti-forensics).
- [ ] **TestIdentityProvider oracle** — isolate exact minimum read permission, caller-controlled
  `SourceIp`, password redaction in CloudTrail, and usefulness beyond raw role/policy/home recon.
- [ ] **DescribeUser/ListUsers** recon of which roles are bound to which users (target selection).
