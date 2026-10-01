# CloudWatch Omni asynchronous access-profile and alert audit — 2026-10-01

## Outcome

Verified two expected, book-quality attack paths in a disposable account-level Omni domain and space:

1. `CreateAlert` plus exact-profile `AssumeAccessProfile` installs an autonomous scheduled telemetry query through an already-authorized access profile.
2. Exact-alert `UpdateAlert` plus exact-profile `AssumeAccessProfile` replaces an existing alert's query, thresholds, cadence and notification destination.

These are service-level persistence and monitoring/post-exploitation paths. They do not return access-profile credentials, exceed the profile/operator-role ceilings, or establish an AWS vulnerability.

## Fixture

- Account/Region: `228478051196`, `us-east-1`
- Disposable IAM-only account domain and one space
- Customer-supplied operator role carrying `CloudWatchOmniSpaceAccessPolicy`
- Customer-managed access profile with only the documented query/result/telemetry-read/notification grant
- `ALERT` principal ID `ALL` granted only `cloudwatch:AssumeAccessProfile` on that exact profile

Creating a space also created the service-managed `DefaultAccessProfileForAsyncWorkflows`, its agent-assumption grant, and a system-managed Space Admin grant for the creating role. These disappeared with the space.

## Minimum `CreateAlert` boundary

A restricted STS session contained only:

- `cloudwatch:CreateAlert` on `arn:aws:cloudwatch:us-east-1:228478051196:alert/*`
- `cloudwatch:AssumeAccessProfile` on the exact profile ARN

With the known space/profile IDs it created an alert without `ListAccessProfiles`, `GetAccessProfile`, alert list/get, telemetry reads, grant/profile administration, SNS, integration or PassRole permissions. The service generated a random 32-hex alert ID under the allowed prefix.

An enabled creation accepted `arn:aws:sns:us-east-1:999999999999:ht-attacker-topic` without checking that the foreign topic existed. Actual cross-account delivery was not attempted; it remains conditional on the foreign topic policy accepting CloudWatch Omni.

## Minimum `UpdateAlert` boundary

- Exact-alert `cloudwatch:UpdateAlert` alone changed the alert description.
- The same action alone could not replace notification configuration: `Not authorized to assume the access profile`.
- Adding `cloudwatch:AssumeAccessProfile` on the exact current profile ARN allowed notification replacement and full rule replacement.
- No telemetry read, SNS, grant/profile administration, integration or PassRole action was present in the restricted session.

The restricted update changed the query to `vector(1)`, set a zero critical threshold and 30-second cadence, enabled notifications, and stored the foreign SNS ARN. `GetAlert` later showed `CRITICAL` with one critical contributor, proving autonomous evaluation after the updater session ended.

## Important limits and negatives

- Access profiles cannot be Space Admins and cannot manage grants/profiles. Their grants and the space operator role are both ceilings.
- A new alert needs both caller-to-profile and alert-to-profile assumption authorization. In this fixture, `ALERT/ALL` supplied the second half.
- The notification target accepted a foreign ARN, but the lab did not own that account and did not claim successful delivery or raw-row exfiltration.
- An initial SQL alert query using `@timestamp` failed the alert parser, and a simple documented logs query failed telemetry-query validation in the empty fixture. Documented PromQL syntax and `vector()` controls were accepted.
- The `ALERT/ALL` principal ID is the case-sensitive reserved value. Its single CUSTOM action was `cloudwatch:AssumeAccessProfile`, scoped with resource type `AccessProfile`; `ACCESS_PROFILE` was rejected as a resource-type spelling.
- Creating an alert did not need the `ListAccessProfiles` action that the console workflow uses when the profile ID was already known.

## CloudTrail

All control-plane events used `eventSource: cloudwatch.amazonaws.com` and were default write management events.

| Event | Observed payload |
| --- | --- |
| `CreateAccessProfile` | Full space/name/description/tags/client token; response included the complete profile metadata and ID |
| `CreateAccessGrant` | Full principal, actions, exact profile ARN, tags and client token; response included the generated grant ID |
| `CreateAlert` | Full profile ID, query, thresholds, cadence, notification rules and client token; response included the generated alert ID/ARN and full stored rule |
| `UpdateAlert` | Full replacement query, thresholds, cadence and foreign SNS ARN; `responseElements` was null |
| IAM-denied `UpdateAlert` | Full attempted notification target remained visible with `AccessDenied` |

AWS documents that alert state changes, configuration changes and sent notifications are retained as telemetry inside the space for 90 days. No separate caller-attributed management call is required for each scheduled evaluation.

## Cleanup

- Deleted all three disposable alerts.
- Deleted both customer-managed grants and the customer-managed access profile.
- Deleted the space, then the domain.
- Detached/deleted the operator role and deleted the accidental restricted-role fixture.
- Final `ListDomains`, `ListSpaces`, `ListIntegrations` and matching IAM-role inventories were empty.
- Final Observability Admin Dataset-integration inventory was empty and CloudWatch OTel enrichment remained `Stopped`.
- No SNS topic, subscription, secret, KMS key, forwarding integration, log group, compute resource or third-party request was created.

## References

- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-access-profiles.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-alerts.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-custom-grant-actions.html
- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_CreateAlert.html
- https://docs.aws.amazon.com/cloudwatch-omni/latest/APIReference/API_UpdateAlert.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_cloudwatch.html
