# SNS child-technique accuracy audit — 2026-09-26

## Scope and method

- Audited `aws-sns-data-protection-bypass.md` and `aws-sns-fifo-replay-exfil.md` against the current SNS API Reference, Developer Guide, Service Authorization Reference, SNS CloudTrail documentation, and SQS CloudTrail documentation.
- No AWS resources were created or changed. Current official contracts resolved the permission, lifecycle, and logging boundaries, so rerunning the existing techniques would add cost and mutation without resolving a material ambiguity.

## Message Data Protection downgrade

- Current lifecycle: as of April 30, 2026, SNS Message Data Protection is unavailable to new customers. Accounts that already had policies configured may continue to use it, with security updates but no planned feature enhancements.
- Exact minimum mutation is `sns:PutDataProtectionPolicy` on the topic. `sns:GetDataProtectionPolicy` is optional if the original document is already known, but is operationally important for exact restoration.
- `sns:Subscribe` is not intrinsic to the policy downgrade. It is needed only when the attacker must add an endpoint; an existing attacker-readable endpoint is sufficient.
- For SQS delivery, the queue resource policy—not the caller's identity policy—must allow the SNS service principal `sqs:SendMessage`, normally constrained by `aws:SourceArn`. The reader separately needs `sqs:ReceiveMessage`.
- A valid Audit statement requires a findings or no-findings destination and additional log-delivery/destination permissions. The exact low-permission downgrade is therefore the documented empty-string removal rather than a fabricated empty Audit destination.
- Impact was bounded to messages delivered after the change, data identifiers/principals previously covered by removed Outbound controls, and endpoints the attacker can actually read. No historical recovery is implied.
- Cleanup now distinguishes restoring the exact original policy on an existing target from deleting the wholly synthetic lab topic, queue, subscription, and local policy files.

## FIFO archive replay

- `ReplayPolicy` is accepted by both `Subscribe` and `SetSubscriptionAttributes`. The exact minimum paths are alternatives:
  - `sns:Subscribe` alone can create a subscription and initiate replay in one request when endpoint and timestamp are known.
  - `sns:SetSubscriptionAttributes` alone can initiate replay on a caller-owned existing subscription.
- `sns:GetTopicAttributes` is optional discovery for `BeginningArchiveTime`, not a required replay action when a valid in-retention timestamp is already known.
- Archive/replay applies only to A2A FIFO topics. Archive retention is 1–365 days and begins only once `ArchivePolicy` is active. Replay cannot recover pre-archive or expired messages.
- SNS FIFO topics may deliver to SQS standard or FIFO queues. The FIFO queue used by the lab is not an exfiltration prerequisite; it preserves ordering and deduplication.
- A queue-owner-created subscription is automatically confirmed. If the creator does not own the cross-account endpoint, the endpoint owner must confirm it.
- Encrypted archives require the SNS service principal to have `kms:Decrypt` and `kms:GenerateDataKey` in the customer managed key policy. This is a resource prerequisite, not an additional replay caller permission when already configured.
- Without `EndingPoint`, replay catches up and the subscription continues receiving new publications. With `EndingPoint`, it stops there and pauses subsequent delivery until a new policy resumes it. Filter policies apply during replay.
- An active archive prevents topic deletion. Lab cleanup must first set `ArchivePolicy` to `{}`, which deletes the archive, then delete the topic. Existing target cleanup must never disable the victim archive merely to remove an attacker subscription.

## Logging findings

- `PutDataProtectionPolicy`, `Subscribe`, `SetSubscriptionAttributes`, `GetTopicAttributes`, `Unsubscribe`, `SetTopicAttributes`, and deletion APIs are default CloudTrail management events.
- SNS topic `Publish` is a data event and is not logged by default.
- SQS `GetQueueAttributes`, `SendMessage`, and `ReceiveMessage` are data events and are not logged by default. Even when `SendMessage` is enabled, CloudTrail hides the message body.
- Replay has no distinct per-message SNS CloudTrail API event. `NumberOfReplayedNotificationsDelivered` and `NumberOfReplayedNotificationsFailed` provide one-minute aggregate CloudWatch evidence.
- The strongest replay detections are `Subscribe` carrying `ReplayPolicy` or `SetSubscriptionAttributes` setting it, correlated with an unfamiliar SQS endpoint and replay metrics.

## Primary official sources

- https://docs.aws.amazon.com/sns/latest/dg/sns-message-data-protection-availability-change.html
- https://docs.aws.amazon.com/sns/latest/api/API_PutDataProtectionPolicy.html
- https://docs.aws.amazon.com/sns/latest/dg/sns-message-data-protection-policies.html
- https://docs.aws.amazon.com/sns/latest/dg/sns-message-data-protection-operations.html
- https://docs.aws.amazon.com/sns/latest/dg/message-archiving-and-replay-topic-owner.html
- https://docs.aws.amazon.com/sns/latest/dg/message-archiving-and-replay-subscriber.html
- https://docs.aws.amazon.com/sns/latest/api/API_Subscribe.html
- https://docs.aws.amazon.com/sns/latest/api/API_SetSubscriptionAttributes.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_sns.html
- https://docs.aws.amazon.com/sns/latest/dg/logging-using-cloudtrail.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/logging-using-cloudtrail.html
