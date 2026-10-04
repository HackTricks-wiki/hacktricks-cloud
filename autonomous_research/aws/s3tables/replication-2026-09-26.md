# S3 Tables replication research — 2026-09-26

## Outcome

Verified the expected bucket-level replication attack end to end in `us-east-1`: a restricted caller with only `s3tables:PutTableBucketReplication` on one source bucket and exact-role `iam:PassRole` could configure a service role that copied source tables into another table bucket. This is useful public-book material, not an AWS vulnerability.

Cross-account replication is documented by AWS but was not exercised because no second account was explicitly authorized. The live test used two destination table buckets in account `228478051196`.

## Minimum-permission matrix

| Case | Caller permissions | Result |
| --- | --- | --- |
| Initial create without PassRole | `s3tables:PutTableBucketReplication` on exact source | Denied, naming `iam:PassRole` on the exact role |
| Initial create | Put on exact source + PassRole on exact role, conditioned to `replication.s3tables.amazonaws.com` | Succeeded; returned a version token without requiring Get |
| Replace existing rule without token | Same as above | `BadRequestException: A version token is not specified.` |
| Replace with current token | Same as above; no Get permission | Succeeded; returned a new token |
| Delete without token | `s3tables:DeleteTableBucketReplication` on exact source | Same `BadRequestException` |
| Delete with current token | Delete on exact source; no Get permission | Succeeded |

The replication role trusted `replication.s3tables.amazonaws.com` and had:

- source tables: `GetTable`, `GetTableMetadataLocation`, `GetTableMaintenanceConfiguration`, `GetTableData`;
- source bucket: `ListTables`;
- destination buckets: `CreateNamespace`, `CreateTable`;
- destination tables: `PutTableData`, `GetTableData`, `UpdateTableMetadataLocation`, `PutTableMaintenanceConfiguration`.

## Behavior

- A source table that existed before configuration appeared in destination 1.
- Replacing the rule with destination 2 caused that pre-existing table to appear there, while its destination-1 replica remained.
- A source table created after the replacement appeared only in destination 2, confirming that bucket-level replication follows future tables and the old destination stops receiving new ones.
- Deleting the rule left both destinations' replicas intact.
- `GetTableReplicationStatus` remained lowercase `pending` for the empty, no-snapshot source tables during the five-minute observation window, even though destination namespace/table creation had occurred. Therefore the test does not claim a committed data-snapshot copy. AWS documentation establishes replication of table data, metadata, schema, and snapshot history.
- The API returned lowercase `success` in the status response.
- Although the SDK shape allows an omitted version token, the live service requires it for replacement and deletion. This is secure optimistic-concurrency behavior.

## CloudTrail

Contrary to the incomplete operation list on the S3 Tables CloudTrail documentation page, the following were visible as default management events:

- `PutTableBucketReplication`
- `GetTableBucketReplication`
- `DeleteTableBucketReplication`
- `GetTableReplicationStatus`

A successful Put event recorded only the source `tableBucketARN` and, on updates, the supplied `versionToken`. It omitted the entire configuration—including the replication role and destination bucket. `responseElements` included the new version token. The denied no-PassRole event contained the exact missing role authorization. The no-token update recorded `BadRequest`.

Service-driven `CreateNamespace` and `CreateTable` events appeared under `assumed-role/<replication-role>/s3-tables-replication`, with `invokedBy=replication.s3tables.amazonaws.com`, and revealed destination bucket and table names. A `CreateNamespace` conflict is expected when the namespace already exists. Object/data-copy activity requires optional data-event logging.

## Security interpretation

This is an expected PassRole/data-exfiltration primitive. The high-value details are:

- bucket-level configuration gives continued access to future tables;
- old replicas survive destination changes and configuration deletion;
- configuration writes hide the role and destination in their default CloudTrail event;
- S3 Tables has no service-specific IAM condition key that limits the replication destination, making the passed role policy, PassRole scope, destination policy, and SCPs the practical controls;
- an attacker retaining the returned version token can later replace/delete the configuration without Get permission.

No malfunction crossed an authorization or isolation boundary, so no local AWS security report was created.

## Cleanup

Four disposable runs were cleaned. The final independent inventory showed zero table buckets and zero IAM roles matching the `ht-s3t-*` test prefix. No replication configuration or destination replica remains.
