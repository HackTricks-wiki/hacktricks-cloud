# AppStream UpdateStack transfer-control weakening — 2026-09-30

## Outcome

Verified that `appstream:UpdateStack` scoped to one exact stack ARN can enable clipboard transfer in
both directions, file upload/download, and printing to the local device. The restricted caller had
no Describe, fleet, streaming-session, or PassRole permission.

Expected AWS functionality only. No AWS defect or private report.

## Security model and impact

- The controls are stack-level user settings applied to streaming sessions.
- Clipboard copy can be enabled independently in each direction. The tested maximum was the
  documented 20 MiB limit (`20971520`).
- Enabling both upload and download permits file-system redirection between the local device and
  the session. Local printing renders and downloads a PDF to the client.
- The useful attacker outcome is an ingress/exfiltration path for data reachable in an existing or
  future session. The write does not mint a session, grant an application, or defeat independent
  endpoint, network, EDR, or DLP enforcement.
- AWS describes these settings as ways to reduce data-leakage risk but warns that they do not
  replace a comprehensive DLP solution.

## Live exact-resource proof

Authorized account `228478051196`, Region `us-east-1`. A disposable stack named
`ht-user-settings-stack-20260930` was created with clipboard copy in both directions, upload,
download, and local printing disabled.

An STS session policy then allowed only `appstream:UpdateStack` on the exact stack ARN. That caller
successfully enabled all five channels and set each clipboard direction to 20 MiB. It could not
call `DescribeStacks`, and the same request authorized only against a different stack ARN was
denied. No fleet, application, session, streaming URL, IAM role, S3 object, or network resource was
needed or created for the proof.

## Telemetry

After normal propagation delay, CloudTrail Event History contained the successful `UpdateStack`
default management event. `requestParameters.userSettings` retained all five actions, permissions,
and both `maximumLength` values. `responseElements.stack.userSettings` returned the complete
resulting configuration. The event also included the exact stack name, caller, source IP, user
agent, and event ID.

Clipboard/file/print content movement is streaming-channel activity rather than a separate
AppStream management API request. Defenders should alert on disabled-to-enabled transitions and
unusually large clipboard limits, then correlate session, endpoint, proxy/network, and DLP
telemetry where available.

## Cleanup evidence

The disposable stack was deleted by the test trap. An independent final `DescribeStacks` inventory
found zero stacks with the test prefix. No other service resource was created.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateStack.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/data-loss-prevention.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/getting-started.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/how-to-enable-file-system-redirection.html
