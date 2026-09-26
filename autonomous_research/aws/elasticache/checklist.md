# ElastiCache — open ideas (service has persistence page only)

- [ ] **Enum page** — `DescribeCacheClusters` / `DescribeReplicationGroups` /
  `DescribeCacheSubnetGroups` recon: endpoints, node types, engine version, `AuthTokenEnabled`,
  `TransitEncryptionEnabled`, whether RBAC or legacy AUTH-token, publicly-resolvable endpoints.
- [ ] **Privesc / lateral via RBAC** — `elasticache:ModifyUser` on an existing user to add
  `on ~* +@all` (mirror of the persistence primitive but framed as data-plane privesc to reach all
  keyspaces). Confirm min-perms and whether it needs the AWSServiceRoleForElastiCache SLR.
- [ ] **Post-exploitation** — `ModifyReplicationGroup --auth-token`/rotate to a known token, or
  `TestFailover` / `ModifyCacheCluster` to disrupt; snapshot exfil via `CopySnapshot
  --target-bucket` to an attacker S3 bucket (needs bucket policy granting the ElastiCache service
  principal — verify the cross-account copy path like the RDS/Redshift snapshot-share class).
- [ ] **Serverless caches** — check `CreateServerlessCacheSnapshot` / `ExportServerlessCacheSnapshot`
  for an exfil path analogous to the RDS snapshot-share technique.
