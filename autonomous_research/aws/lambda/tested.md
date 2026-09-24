# Lambda — tested

## VERIFIED (authz, two-sided) — `UpdateFunctionConfiguration --role` execution-role repoint privesc
- **Idea:** `lambda:UpdateFunctionConfiguration` + `iam:PassRole` + `lambda:InvokeFunction` on an
  EXISTING function → swap its `Role` onto a chosen, more-privileged `lambda.amazonaws.com`-trusting
  role, then run code as it. Distinct from the page's CreateFunction+PassRole (stands up a NEW fn) and
  from the exec-wrapper/layer UpdateFunctionConfiguration techniques (run as the EXISTING role, no
  PassRole). Stealthier: reuses a trusted fn, works when CreateFunction is denied.
- **Result (2026-09-25, acct 228478051196):**
  - NEGATIVE (PassRole scoped to WRONG arn): `AccessDeniedException ... not authorized to perform:
    iam:PassRole on resource: arn:aws:iam::228478051196:role/ht-lamx-target because no identity-based
    policy allows the iam:PassRole action` → IAM gate enforced on the swap.
  - POSITIVE (PassRole allowed on target, bogus fn name): reached the service → `ResourceNotFoundException`
    (`Type: User` = function-not-found, NOT AccessDenied) → gate passed.
- **Min perms:** `lambda:UpdateFunctionConfiguration`, `iam:PassRole` (on the target role, scoped to
  `lambda.amazonaws.com`), `lambda:InvokeFunction`. Target role must trust `lambda.amazonaws.com`.
- **Detection:** `UpdateFunctionConfiguration20150331v2` mgmt event; `requestParameters.role` names the
  attached role. Invoke is a data event (off by default). AssumeRole invokedBy lambda.amazonaws.com.
- **Status:** SHIPPED to wiki (aws-lambda-privesc/README.md), PR #413. Test roles ht-lamx-target /
  ht-lamx-att torn down, both verified NoSuchEntity.

## Pre-existing (already documented, not re-tested)
- CreateFunction + PassRole + Invoke (multiple variants incl. AddPermission, EventSourceMapping).
- UpdateFunctionConfiguration exec-wrapper (`AWS_LAMBDA_EXEC_WRAPPER`) / layer / UpdateFunctionCode —
  run as the function's existing role (no PassRole).
- Code-signing bypass/removal, provisioned-concurrency, container-image tag mutability.
