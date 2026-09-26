# PassRole CloudTrail sweep — 2026-09-26

## Confirmed AWS contract

The [IAM PassRole guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html) states that `iam:PassRole` is a permission checked during another service's API call, **not** an API call itself. It generates no standalone `PassRole` CloudTrail event. To identify a passed role, inspect the service creation/update request containing the role ARN.

## Book sweep

Updated false standalone-event rows in EMR, GameLift, Step Functions, EventBridge Scheduler, API Gateway, CloudFront, S3, and IoT Core, plus Glue in the preceding audit. Corrected prose that pointed to a nonexistent event in EMR, Step Functions, CloudFront, S3, and FIS. Kept rows that already correctly say "no standalone event." Role passing remains a minimum IAM permission where required; this audit only changes logging guidance.

## Research queue

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| IAM `PassRole` CloudTrail event | Negative | AWS explicitly says none | Search any remaining book prose claiming a distinct event |
| Service request omits a passed role ARN despite a successful `iam:PassRole` check | Potential unexpected | No evidence | Scope to a specific service and compare its documented CloudTrail request fields in a controlled test |
| Detect PassRole misuse via role fields in service management events | Expected | General technique documented by AWS | Build service-specific detector guidance for high-value role-bearing APIs |

No AWS resources were created or left running. No zero-day claim.

The EKS Pod Identity tables had grouped `iam:GetRole` with `iam:PassRole` as though neither were an API. In that technique, `iam:GetRole` is a required permission checked by EKS, and no separate caller `GetRole` event was observed; a direct IAM `GetRole` API request is a management event. The book now distinguishes those cases.
