# EMR Serverless Spark Connect session-endpoint takeover — 2026-09-26

## Result

**VERIFIED end to end.** A principal different from the session creator, holding only `emr-serverless:GetSessionEndpoint` on one exact existing session ARN, retrieved a portable Spark Connect bearer token and used the target session to read an S3 object available only to its execution role.

This is expected AWS functionality with important privilege-escalation impact, not an AWS vulnerability. It is public-book quality because it crosses from a narrow read action into interactive use of an already-bound role and requires neither `iam:PassRole` nor `StartSession`.

## Hypothesis and boundary

`GetSessionEndpoint` returns an endpoint and one-hour `authToken` for EMR Serverless `7.13.0+` Spark Connect sessions. The hypothesis was that the token is not bound to `session.createdBy` or to the IAM credentials that retrieved it, and therefore an unrelated exact-session reader can operate the existing Spark session under its `executionRoleArn`.

Required fixture:

- EMR Serverless Spark application, release `emr-7.13.0`, `sessionEnabled=true`.
- One active session created by the administrator under a narrow execution role.
- One private S3 canary object readable only by that execution role.
- A different attacker role with an allow for only `emr-serverless:GetSessionEndpoint` on the exact session ARN.

Explicit attacker-role denies covered:

- `emr-serverless:StartSession`
- `emr-serverless:GetSession`
- `emr-serverless:ListSessions`
- `emr-serverless:TerminateSession`
- `iam:PassRole`
- `s3:GetObject`
- `s3:ListBucket`

## Successful reproduction

Final disposable prefix: `ht-emr-session-e949dfaba1`.

- Application: `00g92n5o091bas09`
- Session: `00g92n5rakf6fi0a`
- Session creator: `ChackBotAdministratorRole` assumed-role session
- Attacker: `ht-emr-session-e949dfaba1-attacker/endpoint-only-attacker`
- Execution role: `ht-emr-session-e949dfaba1-execution`
- Runtime observed after connection: Spark `3.5.6-amzn-2`
- Endpoint token length: 2,594 bytes
- Endpoint token SHA-256 prefix: `9b374605a89e504e`
- Canary SHA-256 prefix: `2d4f9300a6b46068`
- Retrieved canary SHA-256 prefix: `2d4f9300a6b46068`
- `GetSessionEndpoint` request ID: `c599854a-b207-4b4d-a279-47f5a0e68763`

The attacker role received explicit-deny responses for all negative controls before the successful endpoint call:

| Control | Request ID | Result |
| --- | --- | --- |
| `GetSession` | `51d1a792-b98f-4ba1-88e6-e92fb42fcca7` | `AccessDeniedException`, explicit deny |
| `ListSessions` | `711ad839-a33b-4768-b1a0-873a66564a91` | `AccessDeniedException`, explicit deny |
| direct `s3:GetObject` | `DBABPXSBK8VVH77N` | `AccessDenied`, explicit deny |
| `TerminateSession` | `803213c0-707d-4450-9369-a879f5f0680c` | `AccessDeniedException`, explicit deny |

The only successful attacker control-plane action was:

```json
{
  "Effect": "Allow",
  "Action": "emr-serverless:GetSessionEndpoint",
  "Resource": "arn:aws:emr-serverless:us-east-1:228478051196:/applications/00g92n5o091bas09/sessions/00g92n5rakf6fi0a"
}
```

The returned endpoint and token were passed to an independently constructed PySpark client:

```text
sc://<returned-host>:443/;use_ssl=true;x-aws-proxy-auth=<returned-token>
```

`SparkSession.builder.remote(...).getOrCreate()` connected, and `spark.read.text("s3://<canary-bucket>/restricted/canary.txt").collect()` returned the exact canary. The PySpark process did not need the execution role's credentials; the remote driver performed the read under the role already attached to the target session.

No raw bearer token or canary value was retained.

## Failed setup iterations

These are fixture lessons, not service-security results:

1. Disabling both S3 logging and managed debugging caused `CreateApplication` to reject the interactive application with `ValidationException: Either S3 Logging or Managed Debugging must be enabled`. No application was created; the bucket and roles were removed.
2. A `2 vCPU / 10 GB / 40 GB` hard cap with explicit one-core/4-GB driver and executor settings created the application, but the session entered `FAILED` with only `Session failed.` as state detail. It was terminal before cleanup; the application and all other assets were removed.
3. The first successful 8-vCPU/32-GB session yielded the cross-principal token, but local PySpark failed before connecting because Python 3.12 lacked `distutils`. Installing current `setuptools` fixed the local-only dependency. That session and all assets were removed before the final run.

Reliable bounded fixture settings were:

- no pre-initialized capacity;
- maximum capacity `8 vCPU / 32 GB / 40 GB`;
- application auto-stop and session idle timeout of two minutes;
- AWS-managed persistence/debugging enabled, no customer S3 or CloudWatch log destination;
- explicit application start before `StartSession`;
- default session worker sizing.

## CloudTrail and stealth

- `GetSessionEndpoint` is a default management read event under `emr-serverless.amazonaws.com`.
- It identifies the attacker principal and exact application/session IDs.
- The successful call appeared as Event History event `faebdf8a-050a-4988-bcd6-5a1e001867a6`, `readOnly=true`, `managementEvent=true`, with the restricted assumed-role identity and exact application/session IDs. `responseElements` was `null`, so the bearer token and endpoint were not exposed.
- Spark Connect gRPC operations do not produce separate EMR Serverless management events.
- Downstream calls are made under the session execution role. S3 object-level visibility requires an S3 data-event trail.

Stealth rating: **Medium**. The endpoint read is a clear management event, but it is non-mutating and subsequent activity blends into the already-running session/execution role.

## Cleanup verification

Every attempted run used a unique `ht-emr-session-*` prefix. After each attempt:

1. The session was terminated or confirmed already terminal.
2. The application was stopped and deleted.
3. The canary object and bucket were deleted.
4. Both inline policies and IAM roles were deleted.
5. Independent list calls returned no matching EMR Serverless applications, S3 buckets, or IAM roles after every attempt.

The pre-existing service-linked role `AWSServiceRoleForAmazonEMRServerless` was created on 2026-09-23 and was intentionally untouched.

## References

- https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_GetSessionEndpoint.html
- https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/spark-connect.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonemrserverless.html
- https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/security-iam-runtime-role.html
- https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/logging-using-cloudtrail.html
- https://aws.amazon.com/emr/pricing/
