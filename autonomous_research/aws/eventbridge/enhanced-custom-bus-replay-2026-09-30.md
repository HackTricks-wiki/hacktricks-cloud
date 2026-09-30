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
- Test `UpdateSubscriber` filter, run-state and mutable delivery settings separately. Target ARN and starting position are create-only, so replacement behavior must be treated separately.
- Validate whether `PutEvents` and `PutRawEvents` for `event-busv2` use a newly selectable CloudTrail data resource type once current CloudTrail selector documentation exposes it.
- Test resource-policy conditions `events:ContentFilterPresent` and `events:Metadata/*` against filter omission, multiple scopes and JSONata transforms.
- Test KMS decrypt/encryption behavior for cross-account subscribers and vended log payloads using a controlled customer-managed key.

## Universal-target role execution follow-up

A second live fixture closed the universal-target hypothesis. One enhanced bus, one S3 bucket/object path and one delivery role were created. The role trusted `events.amazonaws.com` and had only `s3:PutObject` on the exact synthetic object.

A restricted session had only:

- `events:CreateSubscriber` on the exact bus and one future subscriber name pattern; and
- `iam:PassRole` on that exact role with `iam:PassedToService=events.amazonaws.com`.

It had no S3 action, EventBridge publish/read/update/delete permission, or permission to assume the role. The session created a `LATEST`, `RUNNING` subscriber with target `arn:aws:events:::aws-sdk:s3:putObject`, static API input and a one-event batch. A matching event published separately caused EventBridge to create the exact object through the role; the recovered body was the controlled synthetic marker.

Two validation failures established required syntax without mutation: double-encoded `Input` was rejected for missing `Bucket`/`Key`, and omitting `BatchConfiguration` was rejected because universal targets require valid batch size/window values. Both failed fixture cycles ran through cleanup before the successful cycle.

CloudTrail recorded the successful `CreateSubscriber` as a default `eventsv2.amazonaws.com` management write with both resource ARNs, the role, universal target ARN, `LATEST`, `RUNNING`, and the one-event batch. It replaced the entire universal API input and filter pattern with `HIDDEN_DUE_TO_SECURITY_REASONS`. The separate `PutEvents` trigger again remained absent from default Event History.

Final independent inventory found zero matching enhanced buses, subscribers, IAM roles, S3 buckets and SQS queues. The three universal-target cycles and the second retained-event replay cycle were completely deleted. Expected service-role delegation; no AWS vulnerability report.

## Lossy resume / defense-evasion follow-up

An additional exact-subscriber test confirmed that `events:UpdateSubscriber` alone can deliberately create a delivery gap:

1. An ordinary `LATEST` subscriber delivered matching events to SQS through its existing role.
2. A restricted STS session whose only action was `events:UpdateSubscriber` on the exact subscriber changed `State` to `STOPPED`. It had no PassRole, bus, publish, subscriber-read, queue or role permission.
3. An administrator published a synthetic `lost-*` event while delivery was stopped; EventBridge accepted it into the retained bus.
4. A second equally restricted session updated the same subscriber to `RUNNING` with `ResumePosition=LATEST`.
5. A `live-*` event published after the resume reached SQS. Repeated receives returned only that live marker; the retained paused marker was skipped as documented.

The first fixture proved both update calls but its local queue parser failed on an empty CLI response; its EXIT trap fully cleaned the resources. The second fixture used an empty-response-safe parser and proved the end-to-end delivery gap. Both cycles ended with no matching bus, subscriber, role or queue.

CloudTrail recorded both updates as `readOnly:false` management events under `eventsv2.amazonaws.com`. Requests contained the exact subscriber ARN plus `state`; the resume also contained `resumePosition: LATEST`. Responses returned bus/subscriber identity, fixed starting position, final state and last-modified time. This is expected documented behavior and a useful narrow defense-evasion technique, not an AWS vulnerability.

## Filter clearing and delivery-log suppression follow-up

The mutable subscriber configuration produced a second, distinct `UpdateSubscriber` primitive:

1. Created a `RUNNING`, `LATEST` subscriber whose `DATA` filter matched only `detail.classification=public`, whose log level was `INFO/FULL`, and whose unchanged SQS delivery role had only `sqs:SendMessage` to the exact queue.
2. Published a synthetic `classification=secret` control event. The correctly shaped filter stored by `DescribeSubscriber` rejected it and the queue remained empty.
3. Assumed an STS session with only `events:UpdateSubscriber` on the exact subscriber **and exact bus** ARNs. It had no PassRole, EventBridge read/publish, IAM, SQS or target action.
4. Sent `FilterConfiguration:{}` and `LogConfiguration:{Level:OFF,IncludePayload:ON_ERROR_ONLY}` in one update. The target and role were omitted and remained unchanged.
5. `DescribeSubscriber` then omitted `FilterConfiguration`, returned `LogConfiguration.Level=OFF`, and kept the subscriber `RUNNING`.
6. Published an otherwise-identical `classification=secret` event. It reached the unchanged SQS queue; the earlier filtered event never did.

The authorization boundary differs from state-only updates. A preliminary restricted session with `UpdateSubscriber` on only the exact subscriber ARN was denied on the bus resource. Adding only the exact `event-busv2` ARN succeeded. No `iam:PassRole` check occurred because the invoke configuration was untouched.

Negative and diagnostic controls:

- `IncludePayload=NEVER` was rejected; the valid enum remains `ON_ERROR_ONLY|FULL`, even when the level is `OFF`.
- The first filter control incorrectly asserted on the AWS CLI's empty output for an empty `ReceiveMessage` result; an isolated diagnostic confirmed the stored `detail.classification` pattern and zero delivery. The final fixture used an empty-response-safe parser.
- An early publish attempt used the Classic per-entry bus shape and was rejected locally by the enhanced CLI, which requires top-level `--event-bus-arn`; no event was accepted in that cycle.

CloudTrail recorded the successful update as `readOnly:false` under `eventsv2.amazonaws.com`. The request retained the exact subscriber ARN, literal empty `filterConfiguration`, and `level:OFF`/`includePayload:ON_ERROR_ONLY`; `resources` named both `AWS::EventsV2::Subscriber` and `AWS::EventsV2::EventBus`. The response did not echo the filter/log objects, but returned the unchanged bus/subscriber identity and `RUNNING` state. The subscriber's mandatory `AWS/EventsV2` metrics remain available even after vended delivery logs are disabled.

All diagnostic, denied and successful cycles ran through exact cleanup traps. Final independent inventory found zero matching enhanced buses, subscribers, IAM roles and SQS queues. This is documented service behavior and a public post-exploitation/defense-evasion technique, not an AWS vulnerability.

## Resource-policy persistence follow-up

The enhanced bus's customer-managed `default` policy was validated as a distinct cross-account persistence surface:

- A restricted owner-account session with only `events:PutResourcePolicy` on one exact synthetic bus successfully installed a named grant for `arn:aws:iam::418720621023:user/chack-bot` to call `events:PutEvents`. It had no policy read/list/delete, bus update/delete, publish, subscriber or RAM permission.
- `ExpectedRevisionId=NO_POLICY` safely constrained the test to first-policy creation. `GetResourcePolicy` from the administrator returned the exact document and generated revision; cleanup deleted that same policy before deleting the bus.
- CloudTrail recorded the successful write as a default `eventsv2.amazonaws.com` management event. `requestParameters` contained the complete JSON document, exact external principal/action/bus, `policyName:default`, and `expectedRevisionId:NO_POLICY`; the response returned the revision. `DeleteResourcePolicy` recorded the removed revision.

The available external identity deliberately lacked its own `events:PutEvents` identity allow. Its call was denied both before and after the victim-side grant, confirming the documented two-sided cross-account requirement rather than an authorization bypass. No changes were made in account `418720621023`.

A same-account control created a disposable IAM user with no policies and tried to name it in the enhanced-bus policy. EventBridge rejected the document as invalid, consistent with this policy system being the cross-account side of authorization. An attempted disposable-role control could not begin because the existing administrator role cannot role-chain to arbitrary roles. Neither negative produced usable access.

The public technique is therefore bounded to a named foreign principal that already has the corresponding identity-side action. `PutEvents`/`PutRawEvents` enables durable injection; `CreateSubscriber` can enable retained/live data export but additionally requires the consumer's future-subscriber permission, same-account target/delivery role and PassRole. Public policies are rejected, the `AWS_RAM` document is not writable by the bus owner, and owner-only bus-management actions cannot be delegated.

All three fixture cycles cleaned in traps. Final inventories contained zero matching enhanced buses, IAM users and IAM roles, and no access key survived. Expected cross-account resource-policy functionality; no AWS vulnerability report.

Expected functionality only; no private AWS vulnerability report.
