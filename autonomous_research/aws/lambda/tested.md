# Lambda — tested

## VERIFIED (end-to-end, least privilege) — durable execution history and callback authorization
- **Idea:** determine whether retained durable-execution history exposes useful workflow data and whether
  a callback ID can be completed with permission on a different execution or replayed after use.
- **Result (2026-09-29, acct 228478051196):** a disposable Python 3.14 durable function created two
  simultaneous callback-waiting executions. History with execution data returned both callback IDs.
  A test role allowed `lambda:SendDurableExecutionCallbackSuccess` only on execution B. It was denied
  when it supplied execution A's callback ID, while A remained `RUNNING`; the same role completed B
  with an attacker-chosen JSON result and B reached `SUCCEEDED`. Replaying B's consumed callback ID
  returned `CallbackTimeoutException`.
- **Authorization boundary:** callback IDs are bound to their owning execution ARN. The usable attack
  is a known live callback ID plus the matching send-success or send-failure permission, not a
  cross-execution or replay bypass. `GetDurableExecutionHistory --include-execution-data` is a
  separate sensitive-data read and can disclose callback IDs and payloads.
- **Telemetry:** `GetDurableExecution` and `GetDurableExecutionHistory` appeared as read-only Lambda
  management events in default Event History. Callback send and stop calls did not appear there;
  record that as observed behavior, not proof that no configurable data-event trail can capture them.
- **Cleanup:** execution A was stopped; B was terminal. The function, execution role, restricted test
  role, CloudWatch log group, deployment archive, and local source fixture were deleted and absence
  verified. Durable history has a minimum one-day retention and no per-execution delete API, so only
  the AWS-managed terminal records remain until expiry. No compute or other infrastructure remains.
- **Status:** expected history-disclosure and callback-injection techniques shipped to the wiki. The
  cross-execution authorization and callback-replay 0-day hypotheses were falsified; no private
  vulnerability report created.

## VERIFIED (end-to-end, least privilege) — full resource-policy direct invoke and ARN scoping
- **Idea:** use `lambda:PutResourcePolicy` with its two dependent permission-only actions to grant
  `lambda:InvokeFunction` through the function policy, without an identity-based invoke allow.
- **Result (2026-09-26, acct 228478051196):** a disposable IAM user with only
  `lambda:PutResourcePolicy`, `lambda:AddPermission`, and `lambda:RemovePermission`, all scoped to one
  exact function ARN, was denied Invoke before the policy, denied PutResourcePolicy against a
  different function ARN, then successfully replaced the exact function's policy and invoked it
  (`200`, expected payload). The user's identity policy never allowed Invoke.
- **Minimum permissions:** the three policy-management actions above on the target function ARN. The
  full policy itself must grant `lambda:InvokeFunction` to the caller principal. No identity-based
  `lambda:InvokeFunction` allow is required for a same-account IAM user.
- **Cleanup:** test function, execution role, IAM user, inline policy, access key, and isolated SDK
  environment all deleted; absence verified with `ResourceNotFoundException` / `NoSuchEntity`.
- **Status:** strengthens the already-shipped full-policy technique; public wording updated.

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
