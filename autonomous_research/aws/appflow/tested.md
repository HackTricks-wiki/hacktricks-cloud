# AppFlow — tested

## Verified live — lab account 228478051196, `us-east-1`

### 2026-09-25: S3-to-S3 transfer

- Created an S3-to-S3 flow with an attacker-chosen source bucket/prefix and destination bucket/prefix.
- `StartFlow` executed and transferred source CSV records to destination JSON.
- This proves the AppFlow transfer primitive, but the original conclusion that only `CreateFlow` + `StartFlow` were needed was incomplete; the 2026-09-26 minimum-permission retest below identified direct S3 validation and KMS-grant dependencies.
- S3 was in the same AWS account and Region. Official AppFlow documentation explicitly excludes cross-account S3.
- All test flows and buckets were removed.

### 2026-09-26: `UpdateFlow` S3 object immutability

- Created one disposable S3-to-S3 flow with four disposable buckets.
- A principal with `appflow:UpdateFlow` on the exact flow tried to replace the destination prefix and destination bucket. Both returned:

  `ValidationException: Destination object for the destination connector can not be updated`

- Replacing the source prefix and source bucket returned:

  `ValidationException: Do not update the object for the flow.`

- Conclusion: neither bucket nor prefix can be repointed in an existing S3 flow.

### 2026-09-26: `UpdateFlow` direct validation dependencies and task/trigger mutation

- `appflow:UpdateFlow` alone was rejected. The error requested S3 bucket-list/location/policy reads.
- The minimum successful test policy added:
  - `s3:ListAllMyBuckets` on `*`.
  - `s3:ListBucket`, `s3:GetBucketLocation`, and `s3:GetBucketPolicy` on both configured bucket ARNs.
- With those grants, changing the task configuration succeeded. A `Map_all` task was changed to exclude the `secret` field; `DescribeFlow` showed the generated mapping/filter task set and the flow remained `Active`.
- Changing `OnDemand` to `Scheduled` with `rate(1days)` succeeded but changed the flow to `Draft`. It did not become recurring until a separate `StartFlow` activation; this bounds the persistence claim.

### 2026-09-26: `CreateFlow` direct validation and KMS dependencies

- With only `appflow:CreateFlow` and a future exact-flow `appflow:StartFlow`, S3-to-S3 creation was rejected for missing S3 validation reads.
- After adding the S3 actions listed above, it was rejected for missing:
  - `kms:ListKeys`
  - `kms:DescribeKey`
  - `kms:ListAliases`
  - `kms:CreateGrant`
  - `kms:ListGrants`
- Creation succeeded after adding `ListKeys`/`ListAliases` on `*`, the key-scoped actions on the account `alias/aws/appflow` key, and `kms:ViaService` / `kms:GrantIsForAWSResource` restrictions.
- This occurred even though the request did not specify `kmsArn`; AppFlow used the default AppFlow KMS key.
- No `iam:PassRole` was needed for the plain S3-to-S3 shape. This does not imply that role-bearing Redshift or Glue configurations avoid `PassRole`.

### 2026-09-26: CloudTrail fields

- `CreateFlow`: `flowName` and trigger were visible; `sourceFlowConfig`, `destinationFlowConfigList`, and `tasks` were each recorded as `"***"`.
- `UpdateFlow`: the same configuration/task structures were redacted as `"***"`; error messages remained visible.
- `StartFlow`: the request included `flowName`, and the observed response included `executionId`, `flowStatus`, and `flowArn`.
- `DescribeConnectorProfiles`: the request had no identifying arguments and the response was not recorded.

## High-confidence, prerequisite-gated findings

- Reusing an existing connector profile requires `appflow:UseConnectorProfile` on the profile ARN. The profile credentials are not returned, but AppFlow can use them.
- A SaaS source profile can feed an attacker-readable allowed destination; a SaaS destination profile can receive attacker-controlled records. Live SaaS execution was not attempted because no disposable external tenant/credential existed.
- `UpdateConnectorProfile` accepts replacement connection properties and credentials. Replacing a source profile can poison later runs; replacing a destination profile can redirect later runs to an attacker SaaS tenant. The replacement connection is connector-validated.
- Redshift is destination-only and can involve roles passed to both AppFlow and Redshift plus an intermediate S3 bucket. Snowflake is destination-only and uses an intermediate S3 stage.
- AppFlow EventBridge destination support is partner-event-specific, not a general arbitrary cross-account event bus target.

## Cleanup verification

After the 2026-09-26 tests, independent prefix inventories returned:

- AppFlow flows: `[]`
- Connector profiles: `[]`
- S3 buckets: `[]`
- IAM roles: `[]`

The complete 2026-09-26 audit and candidate matrix are in `audit-2026-09-26.md`.
