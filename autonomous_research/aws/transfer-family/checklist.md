# AWS Transfer Family — open ideas

- [x] CreateUser/UpdateUser/CreateAccess + PassRole role-choice privesc — DONE, authz VERIFIED. tested.md.
- [x] ImportSshPublicKey user impersonation — already documented on the wiki page (pre-existing).
- [ ] **CreateServer --identity-provider-type AWS_LAMBDA / API_GATEWAY** — a custom-IdP server delegates
  auth to an attacker-influenced Lambda that returns the Role+Policy per login. If the attacker controls
  that Lambda (lambda:UpdateFunctionCode) they mint arbitrary Role for any login -> privesc/persistence.
  Needs iam:PassRole on the returned role? Check whether the IdP Lambda response Role bypasses PassRole.
- [ ] **UpdateServer --logging-role** repoint or disable to blind access logging (anti-forensics).
- [ ] **DescribeUser/ListUsers** recon of which roles are bound to which users (target selection).
