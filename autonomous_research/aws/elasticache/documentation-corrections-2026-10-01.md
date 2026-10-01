# ElastiCache documentation corrections — 2026-10-01

## Snapshot export authorization correction

The existing post-exploitation page overclaimed the node-based snapshot export path in three ways:

1. `elasticache:CopySnapshot` alone is not the documented minimum. The current export guide requires
   caller-side S3 bucket/object permissions and wildcard `s3:ListAllMyBuckets`, separately from the
   bucket policy that grants the regional ElastiCache snapshot service access.
2. The `CopySnapshot` API troubleshooting contract explicitly says the destination bucket must be
   owned by the authenticated user. Therefore an arbitrary attacker-owned bucket in another account
   is not a supported direct destination.
3. `AWSServiceRoleForElastiCache` is an explicit serverless-export dependency; it was incorrectly
   presented as a node-based `CopySnapshot` prerequisite.

The public page now limits node-based export to a same-Region, same-account bucket the attacker can
use; lists the current S3 caller permissions; and retains the high-value control-plane exfiltration
impact without claiming a direct cross-account route. Serverless export wording is deliberately
conservative because the current guide's caller-policy example names `CopySnapshot`, while the
serverless API separately exposes `ServiceLinkedRoleNotFoundFault`. A future live test should settle
the exact caller-side S3 authorization matrix before further narrowing it.

## Enumeration freshness

The service page now includes:

- `DescribeServerlessCaches` and `DescribeServerlessCacheSnapshots`;
- `DescribeGlobalReplicationGroups --show-member-info`;
- serverless endpoint/authentication/network fields;
- Valkey 9+ public serverless endpoints, TLS 1.3, and IAM-only attached users; and
- the correct snapshot boundary: serverless Memcached supports snapshot creation, while node-based
  Memcached does not.

AWS's current export guide says serverless Memcached backup export is available, while the
`ExportServerlessCacheSnapshot` API description says the operation is available only for Valkey and
Redis OSS. The public attack section follows the narrower API contract and does not advertise a
Memcached export until a live test or documentation resolution establishes it.

## Validation and cleanup

All cited AWS documentation URLs returned HTTP 200 on 2026-10-01. This was a read-only documentation
correction; it created or changed no AWS resource and has no cleanup debt.
