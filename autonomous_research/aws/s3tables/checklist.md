# S3 Tables research checklist

## Tested

- [x] Table/table-bucket policy self-grant and external-principal validation
- [x] Access Grants canonicalization against an `allowed/*` prefix (secure negative)
- [x] Bucket-level replication PassRole gate with minimum caller permissions
- [x] Replication create, destination replacement, future-table coverage, and delete behavior
- [x] Replication optimistic-concurrency token enforcement
- [x] Default CloudTrail management-event visibility and hidden configuration fields
- [x] Cleanup inventory after all live tests

## Documented, not live-tested

- [ ] Cross-account replication destination table-bucket policy (needs an explicitly authorized second account)
- [ ] Table-level `PutTableReplication`, precedence over bucket-level rules, and its own token semantics
- [ ] Non-empty committed Iceberg snapshots and snapshot-history fidelity
- [ ] KMS-encrypted table data and cross-account key-policy failure modes

## Future security hypotheses

- [ ] Try stale/current tokens across concurrent table- and bucket-level writers; expect strict optimistic concurrency and no lost update.
- [ ] Test whether a destination-policy change during transfer can result in partial metadata/data publication; expect atomic or recoverable failure.
- [ ] Test malicious namespace/table names and source metadata locations for destination-path confusion; expect canonicalized service-owned locations.
- [ ] Test destination deletion/recreation and bucket-name reuse for any stale replication binding; expect ARN/resource identity protection.
- [ ] Test role replacement and trust-policy revocation during transfer for cached authorization beyond normal STS-session lifetime.
- [ ] Compare default CloudTrail and optional data events for enough evidence to reconstruct hidden destinations.
