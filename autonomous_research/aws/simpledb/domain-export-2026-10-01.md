# SimpleDB v2 domain-export audit — 2026-10-01

## Result

AWS added `StartDomainExport`, `GetExport` and `ListExports` in March 2026 through a new `simpledbv2` client. This invalidates the older repository exclusion that no export API existed.

Published `sdb:StartDomainExport` as a post-exploitation full-domain export primitive. It asynchronously writes standard JSON to S3 without requiring SimpleDB item-read actions. No unexpected AWS defect was found and no private report was created.

## Current contract

- CLI/SDK client: `simpledbv2`; IAM prefix and CloudTrail source remain `sdb` / `sdb.amazonaws.com`.
- `StartDomainExport` authorizes the exact `arn:aws:sdb:<region>:<account>:domain/<name>`.
- Destination accepts a bucket name, optional prefix, bucket-owner account ID, AES256/KMS selection and optional KMS key ID.
- Cross-account buckets are explicitly supported; `s3BucketOwner` is required for them.
- Export writes `_started`, JSON data partitions and two manifest files. It is one-way, background processing with no cancel/delete API. Partial files remain after failure.
- `GetExport` exposes bucket/owner/prefix, encryption/key, item count, cutoff, manifest and failures. `ListExports` returns the previous three months.
- The export quota is 25 starts per rolling 24 hours. SimpleDB charges no export fee, but S3 requests/storage and cross-Region transfer can cost money.

## Safe live authorization result

The lab had no domains or exports. A disposable IAM role had:

- `sdb:StartDomainExport` on only `arn:aws:sdb:us-east-1:228478051196:domain/ht-export-allowed-<id>`;
- explicit denies for `sdb:Select`, `sdb:GetAttributes`, `sdb:ListDomains` and `s3:*`.

Calling the allowed synthetic domain reached `NoSuchDomainException`, while a different domain failed IAM on its exact ARN. `ListExports` was empty before and after. This proves exact domain scoping and that item-read actions are not dependencies for the SimpleDB authorization stage.

An end-to-end export was deliberately not started: exports have no delete API and remain in inventory for three months, violating the test cleanup requirement. The JSON/file-layout/background/cross-account behavior and S3 prerequisites are explicit in current AWS documentation.

## Destination-permission caveat

AWS documents S3 permissions in the initiating identity, but its example uses `s3:ListObjects` and `s3:HeadBucket`, which are API labels rather than valid IAM action names. Public coverage avoids presenting those strings as a tested minimum and maps them to the valid S3 authorizations normally used by those APIs (`s3:ListBucket` and `s3:PutObject`), while warning that the exact destination/KMS boundary was not live exercised.

## Telemetry

AWS documents all three export APIs as CloudTrail management events. Its `StartDomainExport` example uses `eventSource: sdb.amazonaws.com`, records domain/bucket and the generated export ARN, and marks the call `readOnly:false`. Object writes need S3 data-event configuration for object-level CloudTrail visibility.

Both safe failed calls subsequently reached Event History as management writes with `readOnly:false`:

- the authorized request that returned `NoSuchDomainException` recorded `domainName`, `s3Bucket`, `s3BucketOwner`, the exact domain ARN and the S3 bucket ARN;
- the IAM-denied request recorded `requestParameters:null`, but retained the attempted domain ARN under `resources` and the exact ARN in `errorMessage`.

This verifies that failures remain useful telemetry and that defenders should inspect the resource list when IAM denial redacts request parameters. No live successful-export telemetry claim is made beyond AWS's explicit example.

## Cleanup

The disposable role and inline policy were deleted. Final matching-role inventory, classic SimpleDB domain inventory and `ListExports` were empty. No domain, item, bucket, object, key or export record was created.
