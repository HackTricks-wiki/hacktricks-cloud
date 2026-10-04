# EventBridge PutEvents CloudTrail audit — 2026-09-26

## Verified from AWS documentation

The [current EventBridge CloudTrail guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/logging-using-cloudtrail.html) lists `PutEvents` as an optional data event for `AWS::Events::EventBus` and, for global endpoints, `AWS::Events::Endpoint`. Event History never displays data events. Prior live observations of no `PutEvents` record used default CloudTrail settings; those observations do not establish that the API cannot be logged. Event `detail` is redacted in the CloudTrail data event.

The data event is delivered **only to the API caller's account**. For a cross-account publisher sending to a victim-owned bus, the victim account does not receive the `PutEvents` CloudTrail data event even if it owns the bus. This is documented expected behavior and is security-relevant for owner-side monitoring. Same-Region bus-to-bus forwarding does not generate an additional data event; cross-Region forwarding can generate one in the rule owner's account.

## Book corrections

- Updated `PutEvents` logging rows and explanations in EventBridge privilege escalation, persistence, and post exploitation pages.
- Separated management records for rule/target/policy changes from optional publisher-side data records.
- Removed the misleading `PutEvents` row from the `StartReplay` technique because the call is not part of that technique; separate replay data-event behavior remains unverified.

## Attack and research candidates

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| Publish to cross-account bus while owner relies on its own CloudTrail | Expected | Documented by AWS; corrected book | Test with two isolated accounts only if a concrete detection recipe needs validation |
| Use `PutPermission` plus `PutEvents` to drive existing rules | Expected | Previously live verified; book covers | Check selector and caller account in any later live logging test |
| Bypass of caller-side `AWS::Events::EventBus` data selector | Potential unexpected | No evidence; do not report | Only investigate with a correctly configured isolated trail and clean up all fixtures |
| Replay deliveries emitting a separate `PutEvents` data event | Unknown | Not tested | Compare a replay with caller-side data-event logs before asserting yes or no |

No AWS resources were created or left running in this documentation audit. No zero-day claim.
