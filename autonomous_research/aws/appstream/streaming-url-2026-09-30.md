# AppStream existing-fleet streaming URL — 2026-09-30

## Outcome

Documented `appstream:CreateStreamingURL` as a standalone existing-fleet access and conditional
machine-role escalation primitive. It creates a bearer URL for a caller-selected custom user without
user-pool or SAML setup, fleet mutation, or caller-side PassRole.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- The call requires a fleet associated with a stack, a caller-selected `UserId`, and optionally an
  application, session context, and validity from 1 to 604800 seconds (seven days).
- `CreateStreamingURL` exists specifically for sessions without normal user setup. The resulting
  URL authenticates the custom session.
- Authorization requires both the fleet and stack resources. Both support `aws:ResourceTag`
  conditions.
- A fleet machine role is already assumed by AppStream on its streaming instances. Applications and
  scripts can use its rotating credentials through the `appstream_machine_role` profile.
- The role path is conditional on the user gaining command execution through Desktop stream view, a
  provided shell/tool, or an exploitable allowed application. Application-only fleets can constrain
  this, although private-network/application access remains.

## Safe live authorization proof

Authorized account `228478051196`, Region `us-east-1`. The account contained zero fleets and zero
stacks, so an end-to-end session was neither possible nor created.

An inline STS session policy allowed only `appstream:CreateStreamingURL` on:

```text
arn:aws:appstream:us-east-1:228478051196:stack/ht-appstream-nonexistent-url-stack
arn:aws:appstream:us-east-1:228478051196:fleet/ht-appstream-nonexistent-url-fleet
```

The request used a synthetic custom user, `applicationId=Desktop`, and the maximum seven-day
validity.

- exact stack + exact fleet reached `ResourceNotFoundException`, proving the action passed IAM;
- alternate stack + allowed fleet was denied on the alternate stack ARN;
- allowed stack + alternate fleet was denied on the alternate fleet ARN;
- `DescribeStacks` was denied, proving discovery is not an implicit dependency;
- the session policy contained no `iam:PassRole` or user-management action.

No fleet, stack, user, streaming URL, session, IAM role, or other resource was created. Cleanup was
vacuous.

## Impact boundaries

A successful caller can enter the fleet's application/desktop environment and private network. If
the session allows command execution, it can use and exfiltrate the existing machine-role
credentials. This is up to role-level privilege escalation, but it is not automatic for a tightly
restricted application-only fleet with no usable execution path.

## Telemetry

CloudTrail recorded the service-authorized failed call as `CreateStreamingURL`, management,
`readOnly:false`. It retained:

- `fleetName` and `stackName`;
- `applicationId=Desktop`;
- `validity=604800`.

CloudTrail replaced `userId`, `sessionContext`, and the response's `streamingURL` with
`HIDDEN_DUE_TO_SECURITY_REASONS`. The resource-not-found service failure was represented as
generic `UnknownError`; IAM-denied calls used `AccessDenied` and `requestParameters:null`.

If usage reporting is enabled, the daily sessions report includes custom authentication type,
session/user IDs, stack/fleet, client IPs, instance, duration, connection state, and stream view.
AWS API calls from inside the session are logged under the fleet machine role rather than the URL
creator, so detection must correlate the management event, session report, and role activity.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateStreamingURL.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/how-to-use-iam-role-with-streaming-instances.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/usage-reports-fields-sessions-reports.html
