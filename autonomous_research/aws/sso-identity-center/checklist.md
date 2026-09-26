# SSO / Identity Center — open ideas

Has an unauthenticated-enum page. Persistence/privesc angle not yet its own page.

- [ ] **Permission-set privesc** — `sso-admin:PutInlinePolicyToPermissionSet` /
  `AttachManagedPolicyToPermissionSet` + `ProvisionPermissionSet`: widen a permission set the
  attacker's assignment uses → escalate in every account it's provisioned to. Verify min-perms and
  whether it needs `CreateAccountAssignment` too.
- [ ] **Rogue assignment persistence** — `sso-admin:CreateAccountAssignment` to bind an
  attacker principal/permission-set to target accounts; durable cross-account access surviving
  local IAM cleanup. Stealth rating needed.
- [ ] **Identity-store user/group persistence** — `identitystore:CreateUser` / `CreateGroupMembership`
  to add a backdoor SSO user into a privileged group. Confirm it's callable and durable.
- [ ] **External-IdP trust tamper** — swap/add a SAML/OIDC IdP so attacker-asserted identities
  federate in. High impact; check feasibility + logging.
