# CloudWatch Logs S3 Tables integration role-mediated delivery — 2026-09-26

## Result

Verified end to end with a disposable fixture in an authorized lab:

- The setup caller could create an Observability Admin S3 Tables integration and pass a CloudWatch Logs integration role while holding no CloudWatch Logs read/query permissions.
- Immediately after `CreateS3TableIntegration`, `ListSourcesForS3TableIntegration` returned an empty source list. The API does not create the console's checked-by-default all-source association.
- An explicit `{ "name": "*", "type": "*" }` association became `ACTIVE`.
- One synthetic event, ingested into a uniquely named custom-source log group only after association, created the expected Iceberg table in the managed `aws-cloudwatch` bucket's `logs` namespace. The table appeared in about 80 seconds and identified `logs.amazonaws.com` as its managing service.
- The setup caller remained denied `logs:GetLogEvents`, `logs:FilterLogEvents`, `logs:StartQuery`, `s3tables:ListTables`, and `s3tables:GetTableMetadataLocation`. Delivery therefore used the passed role rather than the caller's source permissions.

This is expected AWS functionality, not a vulnerability. Its security significance is the separation between permission to configure delivery and permission to read the source.

## Exact caller boundary

Integration creation succeeded with:

- `observabilityadmin:CreateS3TableIntegration` on the account/Region integration ARN pattern
- `s3tables:CreateTableBucket`
- `s3tables:PutTableBucketEncryption`
- `s3tables:PutTableBucketPolicy`
- `iam:PassRole` on the exact integration role, restricted with `iam:PassedToService` to `logs.amazonaws.com` / `test.logs.amazonaws.com`

Source association exposed an additional dependency:

1. `logs:AssociateSourceToS3TableIntegration` alone returned `AccessDeniedException` with “Access denied to ObservabilityAdmin service.”
2. Adding only `observabilityadmin:GetS3TableIntegration` on the selected integration ARN made the identical association succeed.

The documented CloudWatch guide lists the create and associate actions, but currently does not call out this cross-service Get dependency.

## Passed-role boundary

The service role trusted `logs.amazonaws.com`, constrained by:

- `aws:SourceAccount` equal to the owning account
- `aws:SourceArn` equal to the disposable log-group ARN

Its identity policy allowed only `logs:integrateWithS3Table` on that same log-group ARN with `aws:ResourceAccount` constrained to the owning account. A wildcard data-source association did not bypass this resource boundary.

## Result-read boundary

The integration/setup policy did not confer result access.

- Direct Iceberg access requires `s3tables:GetTableMetadataLocation` plus the permission-only `s3tables:GetTableData` action on the resulting table. Table-bucket, namespace, and table list/get actions are discovery conveniences.
- Athena/Redshift access requires enabling the S3 Tables analytics/Glue integration, Lake Formation `DESCRIBE` and `SELECT`, IAM `lakeformation:GetDataAccess`, the appropriate catalog/query actions, and query-result S3/KMS access.

The lab did not enable the account-level Glue/Lake Formation integration because direct table creation plus explicit read denials were enough to establish the role-mediated delivery boundary without leaving service-linked integration state.

## Data and API behavior

- Only events received after association are delivered; existing retained log events are not backfilled.
- Custom-source categorization worked through the documented `cw:datasource:name` and `cw:datasource:type` log-group tags.
- The managed table name used the normalized `<source-name>__<source-type>` form in the `logs` namespace.
- `CreateS3TableIntegration` created the AWS-managed `aws-cloudwatch` table bucket and its system policy.

## CloudTrail evidence

- `CreateS3TableIntegration` was a default management write under `observabilityadmin.amazonaws.com`; its request contained encryption and the passed role ARN, and its response contained the integration ARN.
- Both the denied and successful `AssociateSourceToS3TableIntegration` calls were default management writes under `logs.amazonaws.com`; the successful request recorded the wildcard name/type.
- `CreateTableBucket` and `PutTableBucketPolicy` appeared as default S3 Tables management events attributed to the restricted setup caller.
- S3 Tables object operations are data events and require explicit data-event selectors.
- `iam:PassRole` generated no standalone event.

## Cleanup and residue check

Cleanup order and observed behavior:

1. Disassociated the wildcard source and waited until the association and generated table disappeared.
2. Deleted the integration and waited until the integration inventory was empty.
3. The managed `aws-cloudwatch` bucket remained because the now-empty `logs` namespace persisted. An initial table-bucket deletion correctly failed as non-empty.
4. After confirming the namespace was fixture-created and contained no tables, deleted the empty namespace and then the managed bucket.
5. Deleted the log group, both inline policies, the setup role, and the integration role.

Final independent checks returned empty integration, table-bucket, log-group, and fixture-role inventories; direct role lookups returned `NoSuchEntity`. No unique fixture prefix or managed table-bucket residue remained.

## Checklist

- [x] Pre-inventory existing integrations, S3 table buckets, relevant roles, and target log groups.
- [x] Prove the setup caller cannot read/query the source.
- [x] Establish create-stage minimum permissions and exact PassRole scope.
- [x] Check the source list immediately after the create API.
- [x] Establish the hidden `GetS3TableIntegration` association dependency.
- [x] Associate an explicit wildcard and record its inventory representation.
- [x] Deliver only a synthetic, post-association canary.
- [x] Confirm a managed table appears while the setup caller remains unable to read source or result.
- [x] Document the independent direct and Lake Formation/Athena read gates.
- [x] Capture default-management versus optional-data-event boundaries.
- [x] Disassociate before deleting the integration and verify associated data removal.
- [x] Handle the empty namespace before deleting the fixture-created managed bucket.
- [x] Verify zero unique-prefix residue.

## References

- <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/s3-tables-integration.html>
- <https://docs.aws.amazon.com/cloudwatch/latest/observabilityadmin/API_CreateS3TableIntegration.html>
- <https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_AssociateSourceToS3TableIntegration.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_observabilityadmin.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_logs.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_s3tables.html>
- <https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integrating-open-source.html>
- <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/data-source-discovery-management.html>
