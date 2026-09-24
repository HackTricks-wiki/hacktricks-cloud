# AWS Deadline Cloud (deadline) — tested

## Queue-role privesc: CreateQueue/UpdateQueue + PassRole -> AssumeQueueRoleForUser — VERIFIED live

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1. Deadline IS available (list-farms works).
- **End-to-end test (all torn down):**
  1. `create-farm` (free, no compute) -> farmId.
  2. IAM role `ht-dlq-*` trusting `credentials.deadline.amazonaws.com` (sts:AssumeRole+TagSession),
     inline policy = ONLY `s3:ListAllMyBuckets`.
  3. `create-queue --role-arn <that role>` -> queue IDLE, roleArn attached.
  4. `assume-queue-role-for-user --farm-id --queue-id` -> temp creds.
  5. Creds' `get-caller-identity` = `assumed-role/ht-dlq-.../queue-...`; `s3api list-buckets` SUCCEEDED;
     `iam list-users` DENIED "no identity-based policy allows" => effective policy is the ROLE's own,
     NOT a Deadline-narrowed session. => AssumeQueueRoleForUser vends FULL role privileges.
  6. Teardown: delete-queue, delete-farm, delete-role -> farms=0, role NoSuchEntity. Verified clean.
- **Contrast:** `AssumeQueueRoleForRead` / `AssumeFleetRoleForRead` ARE session-narrowed to read-only
  (already documented). `-ForUser` is the un-narrowed one -> the privesc pivot.
- **Technique:** with `deadline:CreateQueue` (or `UpdateQueue` to repoint an existing queue) +
  `iam:PassRole` + `deadline:AssumeQueueRoleForUser`, set queue roleArn to a more-privileged role and
  vend its full creds. Precondition: target role trusts `credentials.deadline.amazonaws.com` and is
  PassRole-able => other queues' roles are the natural targets. UpdateQueue revertible (stealth).
- **Disposition:** NEW "## Privilege Escalation" section on aws-deadline-cloud-enum.md (refs [4][5][6]);
  also corrected the enum's "session policy Deadline applies" line (only -ForRead is narrowed).
  Impact + Logs block. Min-perms stated.
