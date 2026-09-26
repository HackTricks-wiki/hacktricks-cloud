# IAM CloudTrail documentation audit — 2026-09-26

Scope: IAM privilege escalation, persistence, and post-exploitation pages. This was a documentation check; no AWS resources or test API calls were made.

| Claim checked | Result | Evidence |
| --- | --- | --- |
| CloudTrail Event History cannot be exported | Rejected in 32 IAM technique entries. AWS supports CSV/JSON download and programmatic `LookupEvents`; Event History is still limited to 90 days and is not a durable alerting pipeline. | [Working with Event History](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html), [downloading events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events-console.html) |
| `CreatePolicyVersion --set-as-default` also generates a `SetDefaultPolicyVersion` event | Not supported by the API model. `SetAsDefault` is a parameter on `CreatePolicyVersion`; `SetDefaultPolicyVersion` is a separate operation for activating an existing version. Corrected the event table to avoid requiring a second event for this path. This CloudTrail detail is inferred from AWS's API definitions, not tested live. | [CreatePolicyVersion](https://docs.aws.amazon.com/IAM/latest/APIReference/API_CreatePolicyVersion.html), [SetDefaultPolicyVersion](https://docs.aws.amazon.com/IAM/latest/APIReference/API_SetDefaultPolicyVersion.html) |

No new technique or AWS service defect was established. No infrastructure was launched; cleanup is not applicable.
