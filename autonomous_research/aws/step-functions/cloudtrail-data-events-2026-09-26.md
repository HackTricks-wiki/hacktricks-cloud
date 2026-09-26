# Step Functions CloudTrail data-event audit — 2026-09-26

## Scope and result

A prior book entry said `GetActivityTask` could never be recorded by CloudTrail and another said Step Functions had no data events. Current AWS documentation lists three opt-in data APIs:

| API | `resources.type` for advanced selectors | Result |
| --- | --- | --- |
| `GetActivityTask` | `AWS::StepFunctions::Activity` | Loggable as a data event when selected; absent from Event History |
| `StartSyncExecution` | `AWS::StepFunctions::StateMachine` | Loggable as a data event when selected; absent from Event History |
| `InvokeHTTPEndpoint` | `AWS::StepFunctions::StateMachine` | Loggable as a data event when selected; absent from Event History |

Source: [AWS Step Functions CloudTrail guide](https://docs.aws.amazon.com/step-functions/latest/dg/procedure-cloud-trail.html). AWS states that data events are disabled by default and Event History does not contain them. The earlier live test saw no `GetActivityTask` entry in default Event History while `SendTaskSuccess` appeared; that test established the default behavior only. It did **not** test a trail with activity data-event selectors. Current API reference: [GetActivityTask](https://docs.aws.amazon.com/step-functions/latest/apireference/API_GetActivityTask.html).

## Book changes

- Corrected the activity task claim and table in post exploitation; retained the original test observation with its configuration limit.
- Corrected the blanket no-data-events statement in persistence.
- Added data-event setup and interpretation to service enumeration.
- Added the optional activity poll event to the combined callback technique's logging table.

## Attack candidates and next checks

| Candidate | Expected or unexpected | Status | Next check |
| --- | --- | --- | --- |
| Activity task claim plus callback using only `GetActivityTask` and `SendTaskSuccess` | Expected | Previously live verified; book already covers | Confirm defender correlation under opt-in activity data events when a suitable isolated test account is available |
| Synchronous Express execution abuse with `StartSyncExecution` | Expected | Logging documented; offensive value not established in this audit | Review existing post exploitation technique and minimum IAM permissions |
| Activity poll bypassing an enabled `AWS::StepFunctions::Activity` data selector | Potential unexpected | No evidence; do not report as a vulnerability | If tested, use an isolated activity and trail and compare records; remove both after test |

No AWS resources were created or left running in this audit. No zero-day claim.
