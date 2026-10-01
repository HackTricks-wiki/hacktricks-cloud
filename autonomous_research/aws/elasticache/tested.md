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
