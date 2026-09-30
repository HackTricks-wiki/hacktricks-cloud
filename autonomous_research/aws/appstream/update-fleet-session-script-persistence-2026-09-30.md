# AppStream UpdateFleet session-script persistence — 2026-09-30

## Outcome

Verified that exact-fleet `appstream:UpdateFleet` plus exact-object `s3:GetObject` can set an
existing Elastic fleet's `SessionScriptS3Location` while retaining its pre-existing machine role.
The updater did not have `iam:PassRole`, Describe, fleet start, stack, or session permissions.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- An Elastic fleet can download a ZIP containing `config.json` and scripts from a same-account,
  same-Region S3 bucket for every new streaming instance.
- Configuration supports both session-start and session-termination hooks, with one `user` and one
  `system` context executable per event.
- PowerShell is supported by configuring the system PowerShell executable and passing the staged
  `.ps1` path in arguments.
- The hook persists at fleet level until the location or object is removed/replaced. A valid future
  session triggers it; the updater does not need session access if normal users later connect.
- Updating only the script location leaves `IamRoleArn` untouched. The script can use the existing
  `appstream_machine_role` profile without the updater passing that role.

## Live exact-resource proof

Authorized account `228478051196`, Region `us-east-1`. A disposable Windows Server 2019 Elastic
fleet was created in two default-VPC subnets with `stream.standard.small`, maximum concurrency one,
and a harmless machine role. No session was started, so it created no streaming instance.

A placeholder object was stored under an AppStream-readable bucket policy. This intentionally
tested control-plane validation only; no executable archive or payload was staged. Results:

- exact-fleet `UpdateFleet` without S3 permission reached the service but failed with the specific
  no-access-to-object error;
- exact-fleet `UpdateFleet` plus `s3:GetObject` on the exact object succeeded;
- the response retained the original `IamRoleArn` despite the session policy having no PassRole;
- `DescribeFleets` and an update authorized only for a different fleet ARN were denied; and
- the successful configuration persisted on the stopped fleet until deletion.

The service accepted the object reference without validating ZIP content at update time. A real
attack still requires a correctly structured archive and a later session; AWS documentation, not
this harmless fixture, establishes SYSTEM/user hook execution.

## Telemetry

CloudTrail recorded `UpdateFleet` as a default management event. The successful request retained
the fleet name and exact S3 bucket/key. Its response recorded the full resulting fleet, including
the script location, machine-role ARN, VPC placement, platform, type, instance size, state, stream
view, and capacity. The observed event omitted `readOnly`; the no-S3-permission failure appeared as
generic `UnknownError`, while the wrong fleet policy was `AccessDenied` with null request fields.

S3 `PutObject` and service `GetObject` visibility depends on optional bucket data events. Session
stdout/stderr logging is also optional and can be disabled in `config.json`. Later AWS calls are
attributed to the retained machine role.

## Cleanup evidence

The fleet was deleted directly without starting it. The placeholder object and exact bucket were
deleted, as were the disposable machine role and temporary AppStream service role. Independent
final checks returned zero matching fleets and AppStream ENIs; the bucket and both roles were
absent. No stack, application, app block, URL, session, streaming instance, or other resource was
created.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/developerguide/use-session-scripts.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/session-script-configuration-file.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/create-specify-session-scripts.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/using-powershell-files-with-session-scripts.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateFleet.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/example-elastic-fleets.html
