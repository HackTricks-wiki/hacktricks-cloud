# WorkMail Message Flow audit — 2026-09-29

## Scope and account state

Reviewed the separate `workmailmessageflow` data plane for in-transit message disclosure and
tampering. The authorized account had zero WorkMail organizations in both `us-east-1` and
`eu-west-1`; no organization, directory, mailbox, rule, Lambda function, bucket or billable
subscription was created.

## Verified boundaries

| Hypothesis | Result | Disposition |
| --- | --- | --- |
| `GetRawMessageContent` reaches the service with only a message ID | A read-only fake-ID request reached the API and returned `ResourceNotFoundException: Unknown messageId`, rather than a local parsing or endpoint failure | Publish as time-limited post-exploitation, bounded by valid-ID possession and IAM |
| `PutRawMessageContent` works as a single-action primitive | An earlier disposable role allowing only `workmailmessageflow:PutRawMessageContent` on `*` reached the API and returned `ResourceNotFoundException` for a fake ID | Publish as message-integrity post-exploitation with the synchronous-rule/S3 prerequisites |
| Raw messages are resource-scopeable | Current Service Authorization Reference defines `RawMessage` as `message/${OrganizationId}/${Context}/${MessageId}` for both actions | Document exact account/org/incoming-or-outgoing scoping |
| Message ID enables mailbox-history access | Rejected: AWS limits Message Flow retrieval to in-transit mail within 24 hours, and the API has no list operation | Do not describe as general mailbox enumeration |
| `PutRawMessageContent` can rewrite already delivered mail | Rejected: AWS states that the call may update the retrievable representation but does not change a delivered/sent message | Require synchronous Run Lambda timing |
| Cross-account message-ID IDOR | Not tested and not assumed. The ARN contains the owning account and the service is IAM-authorized | Keep private-test candidate only if a second authorized WorkMail account becomes available |

## Minimum-permission and telemetry evidence

CloudTrail retained the complete lifecycle of the earlier disposable role
`ht-audit-sweep-workmailmessageflow`:

- inline policy: only `workmailmessageflow:PutRawMessageContent` on `*`;
- service response: `ResourceNotFoundException` for `htnonexistentzzz`;
- event source: `workmailmessageflow.amazonaws.com`;
- event classification: management event, `readOnly=false`;
- cleanup: `DeleteRolePolicy` and `DeleteRole` both succeeded immediately.

The 2026-09-29 `GetRawMessageContent` call used the administrator role and a deliberately nonexistent
ID. It created no output object and changed no service state. CloudTrail later recorded it under
`workmailmessageflow.amazonaws.com` as a management event with `readOnly=true`, the message ID in
`requestParameters`, and the expected `ResourceNotFoundException`. End-to-end body
retrieval/replacement was not attempted because creating a WorkMail organization and subscription
solely for this test would add billable, asynchronously provisioned infrastructure. The feature
contract and prior single-action authorization probe are sufficient to publish the expected
behavior with those limitations.

## Cleanup proof

- `ListOrganizations=[]` in `us-east-1` and `eu-west-1` before and after the read-only probe.
- The prior disposable test roles are absent; their successful deletion is retained in CloudTrail.
- No local output file, AWS resource or paid WorkMail state was created in this cycle.

## Sources

- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_workmailmessageflow.html>
- <https://docs.aws.amazon.com/workmail/latest/adminguide/lambda-content.html>
- <https://docs.aws.amazon.com/workmail/latest/adminguide/lambda-content-access.html>
- <https://docs.aws.amazon.com/workmail/latest/adminguide/update-with-lambda.html>
- <https://docs.aws.amazon.com/workmail/latest/APIReference/API_messageflow_GetRawMessageContent.html>
- <https://docs.aws.amazon.com/workmail/latest/APIReference/API_messageflow_PutRawMessageContent.html>
