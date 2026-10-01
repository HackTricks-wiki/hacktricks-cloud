# ElastiCache — open ideas

- [ ] **Enum page** — `DescribeCacheClusters` / `DescribeReplicationGroups` / `DescribeCacheSubnetGroups` recon: endpoints, node types, engine version, `AuthTokenEnabled`, `TransitEncryptionEnabled`, whether RBAC or legacy AUTH-token, publicly-resolvable endpoints.
- [x] **Privesc / lateral via RBAC** — live exact-user test confirmed that `elasticache:ModifyUser` alone can simultaneously replace a restricted user's password and ACL with `on ~* +@all`, without Describe, group/cache, secret/KMS, PassRole, or SLR-management permission. Published on the privesc page; see `modify-user-rbac-escalation-2026-10-01.md`.
- [ ] **Post-exploitation** — `ModifyReplicationGroup --auth-token`/rotate to a known token, or `TestFailover` / `ModifyCacheCluster` to disrupt; snapshot exfil via `CopySnapshot --target-bucket` to an attacker S3 bucket (needs bucket policy granting the ElastiCache service principal — verify the cross-account copy path like the RDS/Redshift snapshot-share class).
- [ ] **Serverless caches** — check `CreateServerlessCacheSnapshot` / `ExportServerlessCacheSnapshot` for an exfil path analogous to the RDS snapshot-share technique.
