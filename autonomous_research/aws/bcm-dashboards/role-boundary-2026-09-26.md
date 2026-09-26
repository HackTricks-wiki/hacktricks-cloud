# BCM Dashboards update role boundary — reasoned exclusion 2026-09-26

## Decision

Do not publish `bcm-dashboards:UpdateDashboard` or
`bcm-dashboards:UpdateScheduledReport` as a role-escalation technique. `UpdateDashboard` has no role
input. `UpdateScheduledReport` can replace a scheduled report's execution role, but AWS Billing and
Cost Management Dashboards uses that role only to run a fixed dashboard-report workflow. The APIs do
not expose credentials, a command or code surface, an arbitrary destination, or report contents to
the caller.

There is a narrower integrity risk: someone allowed to update an owned dashboard can change the cost
queries and filters shown in that dashboard and in later scheduled snapshots. Someone allowed to
update a scheduled report can repoint it to another eligible dashboard, change its schedule/widget
selection, or disable it. Those are direct consequences of the named write permissions, not a role
boundary bypass, and are not a distinct book-worthy post-exploitation technique without a concrete
downstream process that trusts the dashboard.

## Current API boundary

The AWS CLI 2.34.45 service model was inspected on 2026-09-26:

- `UpdateDashboard` accepts `arn`, `name`, `description`, and `widgets`. Widget query parameters are
  typed cost-management queries; there is no execution-role, output-destination, recipient, code, or
  command member.
- `UpdateScheduledReport` accepts the report ARN and optional name, description, dashboard ARN,
  `scheduledReportExecutionRoleArn`, schedule configuration, widget IDs, and a widget date-range
  override. It has no recipient, S3 destination, output URL, code, command, or generic API-action
  member.
- `CreateScheduledReport` has the same execution-role field in its required report configuration.
  `ExecuteScheduledReport` takes only the report ARN, an optional idempotency token, and `dryRun`.

The Service Authorization Reference lists `iam:PassRole` as a dependent action for both create and
update, with `iam:PassedToService = bcm-dashboards.amazonaws.com`. `UpdateDashboard` has no dependent
PassRole action. IAM permits a role to be passed only to a service in the same AWS account, so the role
field is not a direct cross-account role-assumption primitive.

## What the execution role can do

AWS's prescribed trust policy permits `bcm-dashboards.amazonaws.com` to assume the role and constrains
it with the report owner's `aws:SourceAccount` and BCM Dashboards `aws:SourceArn`. The documented
permissions policy contains `bcm-dashboards:GetDashboard` plus a fixed set of read calls for Cost
Explorer, Savings Plans/Reservations, Budgets, Cost Optimization Hub, and Billing Views. The role is
used to retrieve the data needed to render the selected dashboard widgets.

Giving this service an overprivileged role is still poor IAM hygiene, but the documented and modeled
workflow provides no way for the updater to ask the service to invoke unrelated permissions. Neither
the role session nor raw API results are returned to the updater. This is therefore unlike a compute
or workflow service that executes caller-controlled code as the passed role.

## Delivery and cross-account analysis

Scheduled reports are password-protected PDFs stored in AWS-managed S3 buckets and delivered through
AWS User Notifications. The download link and password are available in the corresponding User
Notifications event. The BCM Dashboards create/update report APIs do not select recipients; recipient
configuration is a separate User Notifications setup, and a first-time email recipient must verify
the address. Thus changing only the BCM execution-role field does not redirect the report to an
attacker-controlled bucket, account, or email address.

AWS documents an independent exposure condition: a principal with
`notifications:ListNotificationEvents` and `notifications:GetNotificationEvent` can retrieve a
report's download link and password even without Cost Management permissions. That is a direct User
Notifications authorization issue, not a consequence of `UpdateScheduledReport` or its passed role.

Dashboard sharing also does not turn the role into cross-account cost-data exfiltration. AWS states
that only dashboard configuration is shared; a recipient sees data according to permissions in the
recipient account, and each recipient manages its own scheduled-report configuration independently.

## Read-only lab check and residue

Profile `ht-admin` resolved to account `228478051196`. In `us-east-1`:

- `ListDashboards` returned five `AWS_MANAGED` dashboards and no custom dashboard. AWS documents
  managed dashboards as read-only and ineligible for direct scheduled-report creation.
- `ListScheduledReports` returned an empty list.

No create, update, execute, IAM, User Notifications, or delivery operation was performed. A final
`ListScheduledReports` check remained empty, so there was no fixture or residue to delete.

## Revisit condition

Revisit only if AWS adds a caller-controlled output destination, recipient, arbitrary action/code
surface, or a way for the caller to receive the assumed-role session. Separately, a real environment
may warrant documenting dashboard/report tampering if an automated financial control makes security
decisions from these dashboards without validating the underlying source data.

## Official sources

- <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_bcmDashboards_UpdateDashboard.html>
- <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_bcmDashboards_UpdateScheduledReport.html>
- <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_bcmDashboards_ExecuteScheduledReport.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_bcm-dashboards.html>
- <https://docs.aws.amazon.com/cost-management/latest/userguide/schedule-dashboard-reports-permissions.html>
- <https://docs.aws.amazon.com/cost-management/latest/userguide/schedule-dashboard-reports-create.html>
- <https://docs.aws.amazon.com/cost-management/latest/userguide/schedule-dashboard-reports-emails.html>
- <https://docs.aws.amazon.com/cost-management/latest/userguide/share-dashboards.html>
- <https://docs.aws.amazon.com/cost-management/latest/userguide/managed-dashboards-limitations.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html>
