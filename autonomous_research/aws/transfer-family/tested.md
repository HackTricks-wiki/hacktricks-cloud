# AWS Transfer Family — tested

## CreateUser/UpdateUser/CreateAccess + iam:PassRole role-choice privesc — authz VERIFIED (cont.66) [net-new]

- **Technique:** transfer:CreateUser / UpdateUser / CreateAccess let the caller CHOOSE the IAM `Role`
  an SFTP/FTPS identity assumes on login (unlike ImportSshPublicKey which reuses an existing user's
  role). Bind a more-privileged, transfer.amazonaws.com-trusting role to an attacker-controlled
  identity (own SSH key, or mapped AD group), authenticate, inherit the role over the file protocol.
- **Authz VERIFIED:** attacker role = transfer:CreateUser + iam:PassRole on target -> create-user on a
  bogus server returned ResourceNotFoundException (ResourceType: Server), NOT AccessDenied -> IAM gate
  passed; with a real server the user would be created. AWS docs: iam:PassRole required for Role param.
- **Not fully fired:** end-to-end SFTP login needs a live Transfer server (billable per-hour endpoint)
  -> cost exception; login flow is documented AWS behavior (Transfer assumes the user's Role).
- **Min perms:** transfer:CreateUser|UpdateUser|CreateAccess + iam:PassRole (role trusting
  transfer.amazonaws.com) + ability to auth as the identity (attacker SSH key / AD group membership).
- **Teardown:** all probe roles (target + attacker) deleted, verified NoSuchEntity. No infra left.
  Gotcha: UserName min length 3 (client-side ParamValidation); assume-role needs ~18s propagation +
  robust cred capture (retry loop var-scoping bug wasted two runs).
- **Wiki:** aws-transfer-family-privesc/README.md new section, refs [10][11][12].
