# CloudTrail configuration-tampering metadata audit — 2026-09-26

Reviewed the five existing, live-verified single-permission trail-tampering techniques:

- `DeleteTrail`
- `StopLogging`
- `UpdateTrail` to remove multi-Region/global coverage
- `PutEventSelectors` to suppress write, KMS/RDS Data API, or data events
- `PutInsightSelectors` to disable Insights

Each write supports authorization on the exact trail ARN and can be performed blind when the trail
name and home Region are known; the associated describe/get actions are optional. The public page now
states those minimum permissions/prerequisites and differentiates loud deletion/stopping from subtler
healthy-looking selector and scope reductions. Existing impact and event-specific evidence were
preserved.

No AWS call or resource mutation was made during this pass. It was a metadata/contract review over
the page's previously recorded live single-permission tests.

## Sources

- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudtrail.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_DeleteTrail.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_StopLogging.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_UpdateTrail.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_PutEventSelectors.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_PutInsightSelectors.html>
