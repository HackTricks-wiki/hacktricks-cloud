# ElastiCache — tested

- **RBAC persistence** — VERIFIED. `elasticache:CreateUser` + `ModifyUser` planting an
  `on ~* +@all` RBAC user for durable Redis access. Documented:
  `aws-persistence/aws-elasticache-persistence`. Needs the ElastiCache SLR (mirror of MemoryDB).

Enum / privesc / post pages still missing — see checklist.md.
