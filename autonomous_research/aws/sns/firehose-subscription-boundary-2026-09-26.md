# SNS to Firehose subscription boundary — 2026-09-26

## Result

Verified the SNS Firehose subscription technique end to end with synthetic data and isolated,
least-privilege resources. The useful minimum boundary is:

```text
sns:Subscribe on the target topic
+ iam:PassRole on the SNS subscription role
  with iam:PassedToService = firehose.amazonaws.com
```

The condition value is noteworthy: `sns.amazonaws.com` did not satisfy the PassRole check even though
the supplied role trusts SNS and SNS assumes it for delivery. `firehose.amazonaws.com` did satisfy it.

## Authorized live test

Account `228478051196`, `us-east-1`, profile `ht-admin`:

- Created one synthetic standard SNS topic.
- Created one DirectPut Firehose stream with a dedicated S3 destination bucket and a one-minute
  buffer.
- Created one Firehose delivery role scoped to that bucket and one SNS subscription role scoped to
  the exact stream.
- Created a caller role with only `sns:Subscribe` on the exact topic.

The first subscription attempt passed the SNS action check but failed with
`AuthorizationError` naming `iam:PassRole` on the exact subscription role. Adding exact-role
PassRole with `iam:PassedToService=sns.amazonaws.com` still failed the same check. Replacing that
condition value with `firehose.amazonaws.com` succeeded and returned a confirmed subscription ARN.

An administrator published one harmless JSON notification. Firehose delivered one object under the
dedicated prefix. Its parsed SNS envelope contained the exact test topic ARN and the synthetic message,
proving the subscription was functional rather than merely accepted by the control plane.

Event History later contained both denied and successful `Subscribe` management events. The successful
event recorded `protocol=firehose`, the exact endpoint ARN, `SubscriptionRoleArn`, and the returned
subscription ARN; there was no standalone PassRole event.

No sensitive or third-party topic data was used.

## Scope and cross-account caveat

The live test was same-account. The public `Subscribe` API contract says that when the endpoint and
topic are not in the same account, the endpoint owner must confirm the subscription. Until that
confirmation, it remains pending. A topic resource policy must also authorize an external subscriber.
The page now separates this from the same-account path rather than implying that a cross-account sink
becomes active from `sns:Subscribe` alone.

Creating the S3/Firehose/IAM sink is not part of the minimum victim-topic permission boundary when an
eligible sink already exists. Conversely, a fully self-contained deployment needs the ordinary create,
configure, and Firehose-delivery-role PassRole permissions in the sink account.

## Cleanup and independent verification

Deleted the subscription and topic, force-deleted the Firehose stream, deleted the single delivered
object and bucket, removed all three inline policies and roles, and then checked the unique prefix
independently:

- SNS topic list: zero matches;
- Firehose stream list: initially showed asynchronous deletion, then zero matches;
- all three IAM roles: `NoSuchEntity`;
- S3 bucket: absent.

No test resource remains.

## Official sources

- <https://docs.aws.amazon.com/sns/latest/dg/prereqs-kinesis-data-firehose.html>
- <https://docs.aws.amazon.com/sns/latest/dg/sns-firehose-as-subscriber.html>
- <https://docs.aws.amazon.com/sns/latest/api/API_Subscribe.html>
- <https://docs.aws.amazon.com/sns/latest/dg/sns-using-identity-based-policies.html>
- <https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html>
