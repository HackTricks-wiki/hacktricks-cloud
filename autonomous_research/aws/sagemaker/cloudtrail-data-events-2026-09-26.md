# SageMaker CloudTrail data-event audit — 2026-09-26

Scope: SageMaker enum and post-exploitation pages. This pass checked AWS documentation only; no endpoint, feature group, trail, or other resource was created.

| Claim checked | Result | Evidence |
| --- | --- | --- |
| `InvokeEndpoint` and `InvokeEndpointAsync` cannot be logged even when data events are enabled | Rejected by the current SageMaker CloudTrail guide. Both are listed as opt-in `AWS::SageMaker::Endpoint` data events. Request parameters are omitted for these APIs. The prior live observation may reflect older support or selector configuration; it was not retested here. | [SageMaker CloudTrail logging](https://docs.aws.amazon.com/sagemaker/latest/dg/logging-using-cloudtrail.html) |
| Feature Store `PutRecord`, `GetRecord`, and `BatchGetRecord` cannot be logged | Rejected. AWS lists these as opt-in Feature Store data events and publishes a sample `PutRecord` event. Corrected the main page and the feature-store-poisoning page. | [Feature Store CloudTrail logging](https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store-logging-using-cloudtrail.html) |
| AWS documentation is internally consistent on endpoint logging | Rejected. The current dedicated CloudTrail guide lists endpoint data events, while an older incident-response page still says CloudTrail does not monitor `runtime_InvokeEndpoint`. The book follows the dedicated logging guide and notes default-off behavior. | [Current logging guide](https://docs.aws.amazon.com/sagemaker/latest/dg/logging-using-cloudtrail.html), [incident-response page](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-incident-response.html) |

No new attack technique or AWS service defect was established. No infrastructure was launched; cleanup is not applicable.
