# Glue CloudTrail and PassRole audit — 2026-09-26

## Findings

The [AWS CloudTrail supported data-event resource catalog](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html) lists `AWS::Glue::Table` for activity on Glue tables created by Lake Formation. Thus the book's blanket assertion that Glue emits management events only was too broad. The specific session, job, blueprint, and connection API calls documented on the affected pages remain management events in the prior tests. Exact Lake Formation table data-event API mapping was not established in this audit; do not reclassify those tested calls without evidence.

The [IAM PassRole guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html) explicitly states that `iam:PassRole` is a permission, not an API call, and generates no separate CloudTrail event. Inspect the service resource creation or update event to find the role that was passed. Removed `PassRole` rows from the Glue privilege escalation logging tables and clarified where the `roleArn` is recorded.

## Book corrections

- Replaced blanket no-data-events claims in Glue privilege escalation and post exploitation with scope-specific statements.
- Removed standalone `PassRole` rows from Glue technique tables; retained the minimum permission requirement in attack descriptions.

## Candidates

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| Lake Formation-created Glue table data-event monitoring | Expected | Supported resource type documented | Find exact API/event mapping or use an isolated table/trail test |
| PassRole recorded as a separate IAM event | Negative | AWS says it does not exist | Sweep remaining book tables for false standalone `PassRole` event rows |
| Cross-account Glue table access attribution | Expected | [AWS Glue guide](https://docs.aws.amazon.com/glue/latest/dg/cross-account-access.html) says access event copies to owner | Compare owner/recipient visibility and opt-in principal ARN behavior for a future attack/detection technique |

No AWS resources were created or left running in this audit. No zero-day claim.
