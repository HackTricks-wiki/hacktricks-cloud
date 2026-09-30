# EventBridge enhanced Custom Event Bus retained-event replay — 2026-09-30

## Scope

- Audited the enhanced Custom Event Bus introduced on 2026-09-24 using AWS CLI 2.37.6 (`eventsv2`) and the current API, IAM and user-guide contracts.
- The API uses the `eventsv2` CLI/endpoint and `eventsv2.amazonaws.com` in CloudTrail, but IAM actions remain under `events:` and delivery roles trust `events.amazonaws.com`.
- Enhanced buses retain events for 1 day by default and 1-365 days when configured. Consumer-created subscribers can start at the latest event, the earliest retained event (`HORIZON`), or a retained timestamp.

## Live authorization and behavior

Account `228478051196`, `us-east-1`; one inert bus, one SQS queue, one role and one synthetic event.

1. Initial `ListEventBuses` and `ListEventSources` inventories were empty.
2. Created bus `ht-ebv2-replay-20260930`. The response defaulted retention to 1 day, returned a precise `RetentionWindowStartTime`, and transitioned from `CREATING` to `ACTIVE`.
3. Created an SQS queue and a delivery role trusted by `events.amazonaws.com`; the role had only `sqs:SendMessage` on that queue.
4. Published one inert `RetainedCanary` event before any subscriber existed. `PutEvents` returned `FailedEntryCount: 0`, one event ID and one sequence number.
5. Created an unfiltered `RUNNING` subscriber with `StartingPosition=POINT_IN_TIME`, `PointType=HORIZON`, and `Transformer.Type=WITH_METADATA`. It delivered the pre-existing event to SQS. The message carried the same EventBridge event ID and `SystemMetadata["aws:DeliveryType"]="REPLAY"`.
6. Deleted that subscriber and repeated creation under a restricted session with only:
   - `events:CreateSubscriber` on the exact bus ARN;
   - `events:CreateSubscriber` on `arn:aws:events:us-east-1:228478051196:subscriber/ht-ebv2-restricted-20260930/*`; and
   - `iam:PassRole` on the exact delivery role with `iam:PassedToService=events.amazonaws.com`.
7. The restricted session had no EventBridge list/describe/publish/update/delete permission and no SQS permission. It created the subscriber successfully, and the same retained event arrived a second time with `aws:DeliveryType=REPLAY`.

This verifies a post-exploitation data-export primitive: a narrowly scoped subscriber creator can drain the retained window to an attacker-readable same-account target and, without an end point, continue consuming live events. It does not remove history or affect existing subscribers.

## Authorization boundary

- `CreateSubscriber` performs separate `events:CreateSubscriber` checks against the bus and the future subscriber resource. Because the generated ID does not exist yet, the subscriber resource must end in a wildcard after the chosen name.
- The action also checks `iam:PassRole` against the role in `InvokeConfiguration.RoleArn`; tagged creates additionally require `events:TagResource`.
- The role and target must belong to the subscriber's account. The delivery role must trust `events.amazonaws.com` and have the target action, such as `sqs:SendMessage`.
- No filter means every event. `WITH_METADATA` includes the payload, producer metadata and EventBridge system metadata. `HORIZON` starts at the earliest event still retained.
- Retention bounds retrospective exposure. The default is one day and the configured maximum is 365 days.

## Telemetry

- `CreateEventBus` and both `CreateSubscriber` calls appeared as default CloudTrail management writes under `eventsv2.amazonaws.com`.
- `CreateSubscriber` named both `AWS::EventsV2::EventBus` and `AWS::EventsV2::Subscriber` in `resources`. The request retained the target and role ARNs, starting position, HORIZON configuration, transformer and state; the response retained the generated subscriber ARN.
- The restricted event was attributed to session `ht-ebv2-replay-minimum` and exposed the same complete configuration.
- The `PutEvents` call did not appear in default Event history. Enhanced buses always emit publish metrics in `AWS/EventsV2`; do not equate absent Event history with absent telemetry or with proof that a separately configured data-event trail cannot capture it.
- Subscriber delivery logs were deliberately left at their `OFF` default. AWS documents that records require both a non-OFF subscriber log level and a CloudWatch Logs vended-log delivery.
- The SQS message's sender was the assumed delivery role, and its metadata unambiguously labelled the delivery `REPLAY`.

## Cleanup

- Deleted both subscribers after their single delivery and confirmed the bus contained zero subscribers before bus deletion.
- Deleted the exact bus and independently confirmed no matching enhanced event bus or event source remained.
- Deleted the SQS queue, inline role policy and role; independent reads returned `NonExistentQueue` and `NoSuchEntity`.
- No Classic rule/bus, AWS RAM share, KMS key, log group/delivery, Lambda function, HTTP endpoint or external request was created.

## Follow-up hypotheses

- Test a shared bus with two controlled accounts: determine which account receives publish, subscriber and target telemetry, and validate revocation/reattachment behavior without overclaiming from the one-account fixture.
- Test `UpdateSubscriber` target-role changes and universal targets as separate exfiltration or execution primitives. Target ARN and starting position are create-only, so replacement behavior must be treated separately.
- Validate whether `PutEvents` and `PutRawEvents` for `event-busv2` use a newly selectable CloudTrail data resource type once current CloudTrail selector documentation exposes it.
- Test resource-policy conditions `events:ContentFilterPresent` and `events:Metadata/*` against filter omission, multiple scopes and JSONata transforms.
- Test KMS decrypt/encryption behavior for cross-account subscribers and vended log payloads using a controlled customer-managed key.

Expected functionality only; no private AWS vulnerability report.
