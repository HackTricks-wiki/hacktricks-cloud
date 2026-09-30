# AppStream UpdateApplication launch poisoning — 2026-09-30

## Outcome

Verified that exact-application `appstream:UpdateApplication` can replace an enabled Elastic
application's executable path and launch arguments with a Windows system interpreter. The launch
fields do not require app-block permission, Describe access, S3 access, fleet mutation, or
caller-side PassRole.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- An application stores the executable path, working directory, launch arguments, icon, display
  metadata, supported platforms/families, and app-block association used by Elastic fleets.
- `UpdateApplication` directly changes the path and arguments. The API documents the path as an
  executable on the streaming instance; it is not constrained to the mounted app-block path.
- When a user selects an application, the Elastic fleet mounts its app block and executes the
  stored launch definition. The mutation therefore persists until another update restores it.
- Code runs as the streaming user. It can access that session's mapped data and network placement;
  applications can also use an existing fleet `appstream_machine_role` profile.
- The mutation needs a later application launch. A separate `CreateStreamingURL` permission lets an
  attacker self-trigger; otherwise an entitled user must launch the poisoned catalog entry.

## Live exact-resource proof

Authorized account `228478051196`, Region `us-east-1`. Two disposable CUSTOM app blocks and enabled
Windows Server 2019 applications were created without a fleet or streaming session. An inline STS
session policy allowed only `appstream:UpdateApplication` on the exact application ARN.

The restricted principal successfully changed:

```text
LaunchPath:       C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
LaunchParameters: -NoProfile -Command Write-Output-HT-AppStream-Probe
```

The API returned the changed, enabled application. Under that same session:

- `DescribeApplications` was denied;
- the exact app-block ARN alone could not update the application;
- a different application ARN could not update it; and
- specifying `AppBlockArn`, even without changing its value, was denied until both the exact
  application and exact app-block ARNs were allowed.

Thus launch-path/argument poisoning needs only the application resource. App-block authorization is
a dependent resource check only when the update request supplies `AppBlockArn`.

No fleet was launched, so this test proves the accepted persistent launch definition and exact IAM
boundary rather than claiming a live desktop command execution. AWS documentation establishes that
Elastic fleets execute the stored path when users launch the application.

## Telemetry

CloudTrail recorded successful `UpdateApplication` calls as default management writes. The request
retained the full PowerShell path and launch arguments. The response recorded the resulting enabled
application, app-block ARN, platform, instance family, icon bucket/key, and the same launch fields.

This is high-fidelity prevention/detection data: alert on interpreter paths and encoded, download,
or network-oriented arguments. Subsequent local execution is not a CloudTrail API event, while AWS
calls made with the fleet machine role are attributed to that role rather than to the application
editor.

## Cleanup evidence

Both applications and app blocks were deleted. Their six harmless test objects and both exact S3
buckets were deleted. Independent final checks returned zero matching applications and app blocks,
and both bucket names were absent. No fleet, stack, URL, session, machine role, instance, or network
resource was created.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateApplication.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/applications-elastic.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/fleet-type.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/using-iam-roles-to-grant-permissions-to-applications-scripts-streaming-instances.html
