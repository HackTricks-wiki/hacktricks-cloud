# ECS CloudTrail data-event audit — 2026-09-26

Scope: ECS enum, privilege escalation, post-exploitation, and persistence logging text. This was a documentation check only; no AWS resources or test API calls were made.

| Claim checked | Result | Evidence |
| --- | --- | --- |
| ECS has no CloudTrail data events and every ECS API call is a management event | Rejected. AWS supports optional data events for container-instance agent `Poll`, `StartTelemetrySession`, and `PutSystemLogEvents`. The attack-related control-plane operations in the audited pages remain management events. Replaced the repeated absolute claim and added an enum-page logging note. | [Amazon ECS CloudTrail logging](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/logging-using-cloudtrail.html) |

No new attack technique or AWS service defect was established. No infrastructure was launched; cleanup is not applicable.
