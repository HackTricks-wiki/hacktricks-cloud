# AWS Support App Slack channel role binding — reasoned exclusion 2026-09-26

## Decision

Do not publish `supportapp:CreateSlackChannelConfiguration` or
`supportapp:UpdateSlackChannelConfiguration` as a generic `iam:PassRole` privilege-escalation
technique. The channel role is assumed by the AWS Support App and the documented Slack interface
exposes a fixed set of Support and Service Quotas workflows, not arbitrary AWS API execution.

There is a real but highly conditional **support-data exposure and support-case manipulation** path:
someone who controls a channel in an already-authorized Slack workspace and can bind a sufficiently
privileged channel role can let every member of that channel read or modify the account's support
cases. Notification settings can also send future case updates into the channel. This remains parked
until it can be validated in an existing, explicitly authorized disposable Slack/Support environment.

## Exact prerequisites

AWS documents all of the following prerequisites:

1. The AWS account has Business Support+, Enterprise Support, or Unified Operations.
2. A Slack workspace has already authorized the AWS Support App through Slack OAuth. This requires a
   Slack workspace administrator or someone permitted to add apps. For an Organizations member
   account, `RegisterSlackWorkspaceForOrganization` can reuse a workspace previously authorized by
   the management account.
3. The AWS Support App has been invited to the target public/private Slack channel. The caller knows
   its Slack `teamId` and `channelId`.
4. The channel role trusts the service principal `supportapp.amazonaws.com` and grants the Support /
   Service Quotas operations that the Slack users should receive.
5. The AWS caller can create or update the channel configuration and pass that exact role.

The Support App service has no resource types or service-specific IAM condition keys, so its own
create/update permissions require `Resource: "*"`. The minimum caller-side policy shape is:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "supportapp:CreateSlackChannelConfiguration",
        "supportapp:UpdateSlackChannelConfiguration"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::<account-id>:role/<channel-role>",
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "supportapp.amazonaws.com"
        }
      }
    }
  ]
}
```

Only the create action is needed for a new configuration; only the update action is needed to replace
the role on an existing configuration. `iam:ListRoles` is console convenience, not an API dependency.
The Service Authorization Reference lists `iam:PassRole` as a dependent action for both create and
update, with static `iam:PassedToService = supportapp.amazonaws.com`.

The channel role itself needs this trust relationship before the Support App can use it:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "supportapp.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

## What the passed role actually enables

AWS states that every user in the configured Slack channel receives the channel role's effective
Support App permissions, even if the Slack user has no AWS identity. The documented Slack commands and
buttons can create/search/resolve cases, add correspondence and attachments, start/end live chats, and
request Service Quotas increases.

The current `AWSSupportAppFullAccess` managed policy documents the intended action set:

- Support: `AddAttachmentsToSet`, `AddCommunicationToCase`, `CreateCase`, `DescribeCases`,
  `DescribeCommunications`, `DescribeSeverityLevels`, `InitiateChatForCase`, and `ResolveCase`.
- Service Quotas: read quotas and requests, and `RequestServiceQuotaIncrease`.
- IAM: only `CreateServiceLinkedRole`, constrained to
  `iam:AWSServiceName = servicequotas.amazonaws.com`.

`AWSSupportAppReadOnlyAccess` contains only `support:DescribeCases` and
`support:DescribeCommunications`. Support case data can include up to 24 months of case details,
correspondence, and Slack-originated chat history, so read-only role binding can still expose
sensitive operational data. The managed read-only policy does not include `DescribeAttachment`, so do
not claim that it permits downloading arbitrary existing attachment bodies.

There is no documented Slack command or Support App API that lets a channel user invoke arbitrary
actions from an overprivileged role. Therefore passing an `AdministratorAccess` role must not be
described as direct takeover of that role. The defensible impact is limited to the fixed workflows the
Support App actually invokes. Creating a case or chatting with Support is also not an AWS authorization
bypass: AWS documents that Support does not act in the account merely because a case exists and its
screen-sharing workflow is view-only and consent-based.

## Conditional attack shape

If all prerequisites already exist, an attacker with AWS configuration permission **and** access to a
Slack channel in the authorized workspace could:

1. Bind a role with `DescribeCases` / `DescribeCommunications` and enable all-case notifications.
2. Search existing cases and receive future case updates in Slack.
3. If the role has the write actions, create cases, add correspondence/attachments, initiate chats,
   resolve cases, or request quota increases.

This is distinct from the Amazon Q Developer in chat / former AWS Chatbot PassRole technique: that
product supports running AWS commands subject to a channel role and guardrails, while AWS Support App
documents only support-case and quota workflows.

## CloudTrail and other audit evidence

AWS documents all public Support App API calls as CloudTrail management events. Its example
`CreateSlackChannelConfiguration` event uses `eventSource: supportapp.amazonaws.com`,
`eventCategory: Management`, `managementEvent: true`, `readOnly: false`, and records `teamId`,
`channelId`, `channelRoleArn`, and notification flags in `requestParameters`.

The lab's earlier bounded nonexistent-ID update produced the same event shape in `us-east-1`:

```text
eventSource: supportapp.amazonaws.com
eventName: UpdateSlackChannelConfiguration
eventType: AwsApiCall
eventCategory: Management
managementEvent: true
readOnly: false
errorCode: ResourceNotFoundException
```

The request recorded the synthetic `teamId` and `channelId`. AWS also documents that all Support API
operations, including `CreateCase`, `DescribeCases`, and `ResolveCase`, are logged by CloudTrail under
`support.amazonaws.com`. Service Quotas operations are separately attributable to that service. Slack
origin is also visible in the case correspondence in Support Center, including the Slack-side update
history; do not assume CloudTrail alone preserves the individual Slack user's identity.

## Read-only lab preflight

Account `228478051196`, profile `ht-admin`, `us-east-1`:

- `ListSlackWorkspaceConfigurations` returned an empty list.
- `ListSlackChannelConfigurations` returned an empty list.
- IAM inventory found no current role trusting `supportapp.amazonaws.com`.
- `support:DescribeSeverityLevels` returned `SubscriptionRequiredException`, confirming the account
  lacks the premium Support API entitlement required by the Support App.
- CloudTrail contained one older, bounded `UpdateSlackChannelConfiguration` call against synthetic
  nonexistent identifiers. It returned `ResourceNotFoundException`; no configuration was created.

No create, update, OAuth, workspace registration, Slack, IAM, or support-case mutation was performed
in this review. There is no test residue to clean.

## Cleanup feasibility and revisit gate

A channel configuration is individually deletable with `DeleteSlackChannelConfiguration`; deleting it
does not delete the Slack channel. A workspace configuration is separately deletable, and deletion does
not delete the Slack workspace. IAM role/policy cleanup is conventional. However, building a complete
fixture here would also require a paid Support entitlement and external Slack OAuth/app installation,
which this test must not create or contact.

Revisit only in an account that already has a premium plan plus a test-owned, authorized Slack
workspace/channel. A safe live test must use synthetic support-case content, a minimal describe-only
channel role first, no real case attachments, and must delete the channel configuration and IAM role,
remove any test-only workspace authorization/app installation through its owning Slack administrator,
and verify both Support App inventories are empty.

## Book-worthiness

**Current verdict: reasoned exclusion / no public page.** This is not a general role takeover, and the
conditional support-case exfiltration path cannot be validated without an existing third-party Slack
fixture and premium Support subscription. Promote it only after end-to-end proof that an isolated AWS
principal can bind a controlled Slack channel and that a distinct Slack-only user can retrieve a
synthetic canary case or notification through the role.

## Official sources

- <https://docs.aws.amazon.com/awssupport/latest/user/prerequisites-support-app-for-slack.html>
- <https://docs.aws.amazon.com/awssupport/latest/user/authorize-slack-workspace.html>
- <https://docs.aws.amazon.com/awssupport/latest/user/add-your-slack-channel.html>
- <https://docs.aws.amazon.com/awssupport/latest/user/support-app-permissions.html>
- <https://docs.aws.amazon.com/awssupport/latest/user/support-app-commands.html>
- <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSSupportAppFullAccess.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_support-app.html>
- <https://docs.aws.amazon.com/supportapp/latest/APIReference/API_CreateSlackChannelConfiguration.html>
- <https://docs.aws.amazon.com/supportapp/latest/APIReference/API_UpdateSlackChannelConfiguration.html>
- <https://docs.aws.amazon.com/supportapp/latest/APIReference/API_DeleteSlackChannelConfiguration.html>
- <https://docs.aws.amazon.com/awssupport/latest/user/logging-using-cloudtrail-support-app.html>
- <https://docs.aws.amazon.com/awssupport/latest/user/logging-using-cloudtrail.html>
- <https://docs.aws.amazon.com/awssupport/latest/user/security-for-support-cases.html>
