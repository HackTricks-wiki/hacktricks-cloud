# SQS CloudTrail data-event audit — 2026-09-26

Scope: SQS privilege escalation, post-exploitation, and persistence logging guidance. This pass checked AWS documentation only; it did not create queues, trails, or other resources.

| Claim checked | Result | Evidence |
| --- | --- | --- |
| SQS message operations cannot be logged by CloudTrail | Rejected. AWS lists `SendMessage`, `ReceiveMessage`, `DeleteMessage`, `ChangeMessageVisibility`, `GetQueueAttributes`, and related APIs as SQS data events. They are off by default and require advanced event selectors for `AWS::SQS::Queue`. Corrected the affected book pages and conditional stealth ratings. | [SQS CloudTrail logging](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/logging-using-cloudtrail.html) |
| No message events appeared in the earlier live test | Consistent with default CloudTrail settings; it does not establish that logging is impossible. | [CloudTrail data-event defaults](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html) |
| Internal service-side DLQ redrive produces per-message data events | Open. AWS documents direct SQS API data events, but this audit did not establish whether the managed move emits events for each internal transfer. The book now avoids either absolute claim. | [SQS CloudTrail logging](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/logging-using-cloudtrail.html) |
| FIFO deduplication-ID suppression requires `ContentBasedDeduplication` to be disabled | Rejected as an absolute condition. An explicit `MessageDeduplicationId` overrides a content-generated ID even when that queue setting is enabled. The existing verified scenario used explicit IDs; the wider setting condition is documented by AWS but was not retested here. | [SendMessage API](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessage.html) |

No new attack technique or AWS service defect was established. No infrastructure was launched; cleanup is not applicable.
