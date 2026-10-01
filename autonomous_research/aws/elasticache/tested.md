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
