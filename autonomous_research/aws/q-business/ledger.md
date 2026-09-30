# Amazon Q Business research ledger

## Scope and environment

- Date: 2026-09-26
- Authorized account: `228478051196`
- Bootstrap profile: `hacktricks-training`
- Assumed role: `arn:aws:iam::228478051196:role/ChackBotAdministratorRole`
- Region/output: `AWS_REGION=us-east-1`, `AWS_DEFAULT_REGION=us-east-1`, `AWS_DEFAULT_OUTPUT=json`
- Starting state: `ListApplications` returned zero applications.
- Cost policy: no index, LLM call, subscription, connector sync, or other billable workload was started.

## Live evidence

| Probe | Result | Security conclusion |
|---|---|---|
| `sts:GetCallerIdentity` after role assumption | Account `228478051196`, assumed role `ChackBotAdministratorRole` | Correct authorized boundary. |
| Admin `qbusiness:ListApplications` | `applications: []` | No pre-existing Q Business resources to touch. |
| `CreateApplication` for a tagged anonymous fixture | `NotAuthorizedException: Amazon Q Business is no longer accepting new customers` | Full live resource testing is impossible in this unenrolled account after July 31, 2026. |
| Cleanup after failed creation | `applications=0`, matching IAM roles `0`, tagged Q resources `0` | Zero residue independently verified. |
| Role with only `qbusiness:ListApplications` | List succeeded with `0`; `GetApplication` returned IAM `AccessDeniedException` | Basic least-privilege/resource authorization works. Probe role deleted. |
| Unsigned `ListApplications`, `CreateAnonymousWebExperienceUrl`, `ListPluginTypeMetadata` | `MissingAuthenticationTokenException` | “Anonymous application” does not make the AWS control plane unsigned/public. |
| `ListPluginTypeMetadata` | 11 live built-in types | Current types: Asana, Confluence, Google Calendar, Jira, Exchange, Teams, PagerDuty, Salesforce, ServiceNow, Smartsheet, Zendesk. |
| `ListPluginTypeActions` | Destructive/write actions returned | Examples: delete Jira issue/sprint, delete Salesforce case/opportunity, delete ServiceNow incident/change request, send Teams messages. |
| `UpdatePlugin` with `qbusiness:UpdatePlugin` but no `iam:PassRole` | Explicit `AccessDeniedException` for `iam:PassRole` on target role | No PassRole bypass despite missing dependent action in current Service Authorization Reference. |
| Same constrained-role test for `UpdateApplication`, `UpdateDataSource`, `UpdateRetriever`, `UpdateWebExperience`, `BatchPutDocument` | Each explicitly denied `iam:PassRole` before resource lookup | Runtime consistently protects stored role changes. Probe role deleted. |
| `AssociatePermission` with only `qbusiness:AssociatePermission` | Explicit `AccessDeniedException` for `qbusiness:PutResourcePolicy` | Both actions are required. Probe role deleted. |

## Accepted/documented techniques

| ID | Technique | Confidence | Publication decision |
|---|---|---|---|
| QB-01 | `BatchPutDocument` with no ACL creates public retrievable content; use for durable knowledge/prompt poisoning or accidental sensitive-data publication. | High: API makes `accessConfiguration` optional and AWS states documents without ACLs are public. Live ingestion blocked by account enrollment. | Included with qualification and cleanup guidance. |
| QB-02 | `CreateDataSource` plus permission-only `DisableAclOnDataSource` creates a connector that indexes source content as public. | High: official IAM and connector documentation. | Included. |
| QB-03 | `ListDocuments` + `CheckDocumentAccess` maps actual ACLs, aliases, groups, and access decisions; authorized `GetDocumentContent` returns a 5-minute raw/extracted download URL. | High: explicit API response/authorization documentation. | Included; explicitly not called an ACL bypass. |
| QB-04 | `UpdatePlugin` changes endpoint/schema/auth/state, enabling hijack of the plugin's authenticated third-party action authority. | High for configuration/action control; raw credential forwarding after endpoint-only change remains unverified. | Included without claiming raw secret theft. |
| QB-05 | Data accessor + application resource policy + IDC assignment provides durable registered-ISV cross-account `SearchRelevantContent` access. | High but conditional on supported ISV principal/tenant and end-user ACL. | Included with conditional prerequisites and complete cleanup. |
| QB-06 | `CreateAnonymousWebExperienceUrl` can mint billable public sessions. | High: documented one-use/5-minute redemption and 15–60 minute session. | Included as a bounded abuse path, not authentication bypass. |

## Rejected or bounded candidates

| Candidate | Disposition | Evidence/reason |
|---|---|---|
| Spoof `ChatSync.userId`/`userGroups` using ordinary IAM credentials | Rejected as a general authenticated-app bypass | AWS requires identity-aware SigV4 credentials and trusted identity propagation for the chat/conversation/search subset. |
| Call the Q Business control plane unsigned because the app is anonymous | Rejected | Three live unsigned probes returned `MissingAuthenticationTokenException`. |
| Use `GetDocumentContent` as an admin-only ACL bypass | Rejected | API explicitly validates user authorization against document ACL before returning the URL. Anonymous apps cannot call it. |
| Read chat attachments/media from anonymous apps | Rejected | Anonymous applications do not support attachments, history, `GetMedia`, or direct document download. |
| Change connector endpoint and reuse an unrelated stored secret to make Q disclose it | Rejected as a simple confused-deputy chain | AWS documents an endpoint-in-secret versus connector-configuration equality check; a changed endpoint requires a new secret. |
| Change any Q Business service role through an update API without `iam:PassRole` because the authorization table omits it | Rejected by live test | `UpdateApplication`, `UpdateDataSource`, `UpdateRetriever`, `UpdatePlugin`, and `UpdateWebExperience` all returned explicit `iam:PassRole` denial under a constrained role. |
| Create an arbitrary cross-account data accessor for an attacker role | Rejected as documented/general behavior | AWS documents that only registered supported ISVs can be data accessors. Resource policy alone does not supply end-user identity/consent. |

## Future tests requiring an enrolled account with disposable fixtures

1. Verify direct inline `BatchPutDocument` without `accessConfiguration` is queryable by two unrelated test users and produces the expected public-document ACL.
2. Verify whether `CheckDocumentAccess` can enumerate arbitrary user aliases/groups with only its IAM action or requires an additional identity context in each identity mode.
3. Test conversation, attachment, `GetMedia`, and `GetDocumentContent` isolation with two distinct Identity Center users.
4. Test direct `ChatSync.actionExecution` against a benign custom plugin and determine whether an action-review token/state is enforced server-side.
5. Test endpoint-only `UpdatePlugin` while retaining Basic/OAuth configuration. Determine whether old credentials are ever sent to the new origin. Do not publish or use real credentials.
6. Test data-accessor provider allowlisting, external-ID validation, assignment-required behavior, and removal order with a cooperative registered ISV sandbox.
7. Capture representative CloudTrail events for `CheckDocumentAccess`, `GetDocumentContent`, `SearchRelevantContent`, data accessor changes, anonymous URL issuance, and plugin action execution to confirm management/data classification.
8. Confirm whether partial update calls preserve omitted `authConfiguration`/`roleArn` fields for plugins and web experiences.

## Zero-day candidates

No confirmed AWS security malfunction was found.

- **Closed QB-Z01 — missing documented PassRole dependency on update APIs.** The Service Authorization Reference omits `iam:PassRole` for several update operations whose request bodies accept `roleArn`. Live least-privilege probes proved runtime enforcement on all tested operations. This is a documentation defect, not an exploitable bypass.
- **Open QB-Z02 — endpoint-only plugin update with retained stored credentials.** The API documents optional `serverUrl` and optional `authConfiguration`, but the account could not host a disposable application. Keep private/unpublished until an enrolled sandbox proves whether endpoint changes preserve authentication and whether the service prevents credential forwarding to a new origin.
- **Open QB-Z03 — `CheckDocumentAccess` identity graph exposure.** The documented response returns the actual ACL plus resolved aliases/groups for a supplied user ID. Determine in an enrolled account whether `qbusiness:CheckDocumentAccess` alone exposes this graph across arbitrary users. Keep the possible over-broad disclosure claim unpublished until verified.

## Cleanup and final residue verification

Every IAM probe role used a unique `ht-qbusiness-audit-probe-qbaudit260926*` name and was deleted with its inline policy. The one application-role fixture was deleted immediately after `CreateApplication` failed.

Final checks to repeat at handoff:

```bash
aws qbusiness list-applications --max-results 100 \
  --query 'length(applications)' --output text
aws iam list-roles \
  --query "length(Roles[?contains(RoleName, 'ht-qbusiness-audit-')])" \
  --output text
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=HackTricksAudit \
  --query 'length(ResourceTagMappingList)' --output text
```

Expected and observed after the failed fixture plus each role probe: `0`, `0`, `0`.

## Official sources used

- https://docs.aws.amazon.com/service-authorization/latest/reference/list_qbusiness.html
- https://docs.aws.amazon.com/amazonq/latest/api-reference/Welcome.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/making-sigv4-authenticated-api-calls-iam.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/create-anonymous-application.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/supported-exp-actions-anonymous.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/connector-concepts.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/custom-plugin.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/plugins-api-schema.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/data-accessors.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/data-accessors-granting-permissions.html
- https://docs.aws.amazon.com/amazonq/latest/api-reference/API_CheckDocumentAccess.html
- https://docs.aws.amazon.com/amazonq/latest/api-reference/API_GetDocumentContent.html
- https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/logging-using-cloudtrail.html
