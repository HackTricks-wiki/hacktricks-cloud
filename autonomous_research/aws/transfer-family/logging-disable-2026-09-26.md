# Transfer Family logging-disable audit — 2026-09-26

## Outcome

Verified useful expected defense-evasion behavior: `transfer:UpdateServer` on one exact server is
sufficient to clear both logging mechanisms while the server remains ONLINE. No caller
`logs:DeleteLogDelivery`, other `logs:*`, or `iam:PassRole` permission was needed.

Published as Transfer Family post-exploitation, not persistence. It suppresses future Transfer server
telemetry but does not maintain access, erase historical events, hide the mutation, or disable S3 data
events.

## Minimum-permission fixture

- Disposable public SFTP server with both `LoggingRole` and one structured CloudWatch Logs destination.
- Restricted caller: only `transfer:UpdateServer` on the exact server ARN.
- Explicit Deny on `logs:*`, `iam:PassRole`, and `transfer:DescribeServer`.
- Server remained ONLINE throughout every mutation.

## Live matrix

| Case | Result |
| --- | --- |
| Restricted `DescribeServer` | `AccessDeniedException` |
| Clear only `LoggingRole:""` | Succeeded; structured destination remained |
| Admin restore legacy role | Succeeded |
| Clear only `StructuredLogDestinations:[]` | Succeeded despite `logs:*` deny; legacy role remained |
| Combined empty role + empty destinations from a fresh both-enabled server | Succeeded in one call |
| Admin describe after combined clear | Both fields empty; server still ONLINE |
| Immediate structured re-enable after a clear | `ConflictException: Conflicting update for log destination` for at least 150 seconds |

The re-enable conflict is operationally important: disabling is fast, while rollback can lag behind the
delivery deletion. It does not change the minimum attack permission.

## Telemetry

- `UpdateServer` is a default Transfer management/write event.
- After propagation, the restricted caller's event had `readOnly:false`, `managementEvent:true`, and
  retained exact `requestParameters.loggingRole:""` plus `structuredLogDestinations:[]`. It also
  contained the normal redacted `hostKey` placeholder even though no host key was submitted.
- There is no standalone PassRole event and no PassRole operation occurred.
- The caller's explicit `logs:*` deny proves no CloudWatch Logs authorization was evaluated against the
  attacker for either individual or combined clear.
- No separate caller-attributed `DeleteDelivery` event for the server/destination appeared in Event
  History after propagation.
- Future Transfer protocol events are absent once both logging fields are empty. Historical log groups,
  CloudTrail management events, and optional S3 data events remain.

## Cleanup

Three disposable server cycles isolated individual fields, observed the asynchronous restore conflict,
and verified the direct combined payload. Every server was deleted (never merely stopped) in `finally`.
All structured/legacy test log groups, CloudWatch deliveries, IAM inline policies, and roles were absent
in independent inventory. Total endpoint time remained far below the authorized cost ceiling.
