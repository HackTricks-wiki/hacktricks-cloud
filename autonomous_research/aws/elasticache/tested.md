# ElastiCache — tested

- **RBAC persistence** — VERIFIED. `elasticache:CreateUser` + `ModifyUser` planting an `on ~* +@all` RBAC user for durable Redis access. Documented:
  `aws-persistence/aws-elasticache-persistence`. Needs the ElastiCache SLR (mirror of MemoryDB).

- **Exact-user RBAC privilege escalation** — VERIFIED 2026-10-01. A user with only
  `elasticache:ModifyUser` on one exact ElastiCache user ARN, and no Describe permission,
  replaced both its password and a narrow/off access string with `on ~* +@all`. Admin inventory
  observed the active unrestricted ACL and password-authentication mode. No cache, group, SLR
  mutation, PassRole, secret/KMS permission, or paid data-plane fixture was involved. Published in
  `aws-privilege-escalation/aws-elasticache-privesc`; full evidence and cleanup are in
  `modify-user-rbac-escalation-2026-10-01.md`.

Further enum and post-exploitation ideas remain in `checklist.md`.

- **Legacy AUTH token addition** — VERIFIED end to end 2026-10-01. A caller with only
  `elasticache:ModifyReplicationGroup` on one exact replication-group ARN and no Describe permission
  applied `ROTATE` with a caller-chosen token. After convergence, isolated in-VPC TLS probes proved
  that both the original and new tokens completed `AUTH` and `PING`. No application data existed.
  The node, group, function/role/ENIs, IAM identity and fixture-created ElastiCache SLR were removed;
  see `modify-replication-group-auth-rotation-2026-10-01.md`.

- **Authentication invariants** — CLOSED SAFE 2026-10-01. Exact-user `ModifyUser` calls could not
  carry `no-password-required` from Redis into Valkey (engine-only or explicitly repeated auth mode),
  and could not change a mismatched `UserId`/`UserName` pair to IAM authentication. All three calls
  returned `InvalidParameterCombinationException`; administrator inventory stayed unchanged. See
  `authentication-invariants-2026-10-01.md`.

- **User-group secondary-resource authorization** — VERIFIED 2026-10-01. `ModifyUserGroup` on only
  the exact group failed on the added user ARN. Granting the action on the group, added user, and
  removed user succeeded; a different ungranted user failed on its own ARN. The existing persistence
  page now states the exact minimum. See `modify-user-group-authorization-2026-10-01.md`.

- **Exact-resource Describe isolation** — CLOSED SAFE 2026-10-01. `DescribeUsers` and
  `DescribeUserGroups` with exact A ARNs plus exact A filters returned only A. Filtered B requests
  were denied on B's ARN; unfiltered requests were denied on `user:*`/`usergroup:*`. No unrelated
  metadata leaked. See `describe-resource-isolation-2026-10-01.md`.

- **Prospective `CreateUserGroup` authorization** — VERIFIED 2026-10-01. Permission on only the
  future group ARN failed on the initial `default` user ARN. Exact future group plus every initial
  user succeeded; a second prospective group with an ungranted member failed on that member ARN.
  Updated the existing persistence page; see `create-user-group-authorization-2026-10-01.md`.

- **Failed AUTH-token CloudTrail redaction** — CLOSED SAFE 2026-10-01. An exact synthetic-group
  `ModifyReplicationGroup` carrying a unique marker passed IAM and stopped at the absent SLR. The
  default write event had null request/response/resources and did not contain the marker. See
  `failed-auth-token-redaction-2026-10-01.md`.
