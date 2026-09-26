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

## Custom Lambda IdP takeover and password capture — VERIFIED (cont.87)

- **`transfer:UpdateServer` path:** a restricted role with only `UpdateServer` on one exact server
  could not `DescribeServer`, had no PassRole/Lambda/S3 access, and repointed the server to an
  already server-authorized Lambda. A real password-authenticated SFTP session read both marker
  prefixes through the high Transfer role returned by that Lambda.
- **`lambda:UpdateFunctionCode` path:** a separate role with only that action on the configured IdP
  function replaced its logic. It had no Transfer, Invoke, PassRole, logs-read, or S3 permission;
  a real SFTP login again read both markers through the role returned at authentication time.
- **Credential capture:** the IdP Lambda received the exact plaintext synthetic SFTP password. When
  the handler printed its input, `logs:FilterLogEvents` recovered the exact canary value.
- **Boundary:** the returned role yields only S3/EFS operations Transfer performs; no STS credentials
  or unrelated IAM permissions are exposed. Omitted/empty session Policy means the base role;
  supplied Policy intersects with it.
- **CloudTrail:** `UpdateServer` recorded the replacement function ARN under the restricted updater.
  Lambda code replacement was `UpdateFunctionCode20150331v2` under the restricted coder. PassRole
  emitted no event because it was never performed. Lambda Invoke and S3 object access need optional
  data-event logging; protocol sessions need configured Transfer logging.
- **Cleanup:** five short public-SFTP fixture cycles were deleted, not stopped. Final independent
  inventory was empty for matching servers, functions, roles, buckets, and log groups.

## PUBLIC_KEY_AND_PASSWORD response-binding matrix — VERIFIED, no AWS report (cont.87)

- Correct RSA key + correct password succeeded; wrong password and wrong key both failed.
- Complete identical low-role/restrictive-policy responses allowed only `allowed/`.
- High role + restrictive session policy stayed restricted; low role + permissive session policy
  stayed low, confirming normal IAM intersection.
- If key and password responses differed, the password response deterministically supplied the
  effective role, Policy, and home: low/restrictive -> high/omitted became full high-role access;
  the reverse stayed low/restricted; restrictive -> permissive became permissive; the reverse stayed
  restrictive. A different password-response home became the session home.
- Returning `PublicKeys` in the password response failed authentication, as documented.
- Malformed nonempty Policy values (`{not-json`, truncated JSON) failed authentication. A duplicate
  top-level `Statement` connected but all file operations failed with `Unable to AssumeRole for user`.
  No malformed policy produced base-role access. Empty and omitted Policy both intentionally used the
  base role.
- Interpretation: the custom IdP is the trusted authentication and authorization decision point and
  can already return the high role directly. Response precedence did not cross another tenant,
  principal, or authorization boundary, so it is retained as a regression/implementation note rather
  than an AWS vulnerability report or standalone public attack.
