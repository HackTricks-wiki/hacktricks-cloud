# Glue Spark Connect endpoint-token boundary — 2026-09-26

## Result

Verified expected post-exploitation path: `glue:GetSessionEndpoint` on one exact Glue session ARN returned the `sc://` Spark Connect URL, an auth token and its expiration for a live `SPARK_CONNECT` interactive session. The caller had no session discovery, metadata, lifecycle, statement-execution, PassRole or direct S3 permission.

AWS documents Spark Connect as a remote interface to the existing session. Consequently this Read-classified permission is an interactive Spark code/data-access capability under the session execution role, not harmless endpoint discovery. The endpoint was deliberately not opened during the issuance-boundary test.

## Cost and fixture

The current official pricing page states that interactive sessions are billed per second with a one-minute minimum; they require at least two DPUs, and the published example price is $0.44 per DPU-hour. The fixture used two `G.1X` workers and a one-minute idle timeout, so it was far below the $10/30-minute research limit.

The disposable session used:

- ID `ht-glue-e63138e94d`;
- Glue version 5.1;
- `SessionType=SPARK_CONNECT`;
- two `G.1X` workers;
- one-minute idle timeout and five-minute overall timeout;
- a dedicated Glue-trusted execution role with no attached/inline data permissions.

No data source, Glue connection, VPC attachment, S3 object or Catalog object was created.

## Least-privilege proof

The caller allowed only:

```json
{
  "Effect": "Allow",
  "Action": "glue:GetSessionEndpoint",
  "Resource": "arn:aws:glue:us-east-1:228478051196:session/ht-glue-e63138e94d"
}
```

It explicitly denied:

- `glue:GetSession`
- `glue:ListSessions`
- `glue:CreateSession`
- `glue:RunStatement`
- `glue:DeleteSession`
- `iam:PassRole`
- `s3:*`

Both exercised discovery negatives returned explicit-deny `AccessDeniedException`. The endpoint request then succeeded and returned a non-empty `sc://` URL, non-empty token, and expiration. The token was hashed in memory and not printed or stored. The observed expiration was approximately 30 minutes after issuance, longer than the five-minute value previously assumed during hypothesis triage.

The exact session ARN therefore works for resource scoping; `Resource: "*"` is unnecessary when the session ID is known.

## Impact boundary

The token is not AWS STS credentials. Its value is access to the existing Spark Connect runtime: code submitted through that runtime executes in the session and can use whatever AWS/data permissions, network reachability and configured connections the execution role/session already has. A role with no useful permissions yields little impact; a broad analytics role can turn this one Read action into substantial data access or privilege escalation.

The test proved credential issuance under the minimal IAM policy but deliberately did not establish a Spark connection or execute code. The code-execution semantics are the documented purpose of the endpoint.

## Logging and stealth

The successful call appeared in CloudTrail Event History with `eventSource=glue.amazonaws.com`, `eventName=GetSessionEndpoint`, `readOnly=true`, `managementEvent=true`, `eventCategory=Management`, the session ID in `requestParameters`, and `responseElements=null`. Treat that as the high-fidelity issuance event and separately retain interactive-session/runtime logs; do not assume each gRPC Spark operation becomes its own CloudTrail event. Downstream AWS calls remain subject to the target service's logging and appear under the session execution role.

Stealth rating: **Medium**. The issuance read is logged and relatively uncommon, while the subsequent Spark command channel has different observability.

## Cleanup verification

Immediately after the endpoint response the harness called `DeleteSession`, waited for a terminal `STOPPED` state, then deleted the caller and execution roles. Independent inventory returned no matching live sessions and no matching roles. The token was never used and expired naturally.

## References

- https://aws.amazon.com/glue/pricing/
- https://docs.aws.amazon.com/glue/latest/dg/interactive-sessions-spark-connect-configuring.html
- https://docs.aws.amazon.com/glue/latest/dg/interactive-sessions-spark-connect-api.html
- https://docs.aws.amazon.com/glue/latest/webapi/API_GetSessionEndpoint.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsglue.html
- https://docs.aws.amazon.com/glue/latest/dg/monitor-cloudtrail.html
