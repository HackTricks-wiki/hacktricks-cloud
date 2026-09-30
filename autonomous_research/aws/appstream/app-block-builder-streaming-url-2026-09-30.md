# AppStream existing app-block-builder streaming URL — 2026-09-30

## Outcome

Verified and documented `appstream:CreateAppBlockBuilderStreamingURL` as a standalone access path
to an existing app-package builder. The action does not require Describe, builder/app-block
mutation, association, or caller-side PassRole permissions.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- The API accepts an app-block-builder name and optional validity from 1 to 604800 seconds.
- The builder must be running. Starting a stopped builder separately requires it to be associated
  with an app block.
- The builder provides a Windows administrative desktop intended to install applications, record
  the installation, package a VHD, upload it to S3, and activate the associated app block.
- App block builders use Windows Server 2019 and do not support Active Directory domain join.
- If the existing builder has `IamRoleArn`, WorkSpaces Applications publishes its rotating
  credentials in the `appstream_machine_role` profile. The URL caller does not pass or modify it.
- Each streaming session uses a new ephemeral instance and local changes do not persist after
  termination. Finishing the associated APPSTREAM2 packaging workflow is the durable branch: the
  package is uploaded to S3 and the app block becomes active for possible Elastic-fleet use.
- Configured AppStream streaming access endpoints restrict where administrators can connect.

## Exact-resource authorization proof

Authorized account `228478051196`, Region `us-east-1`. An inline STS session policy allowed only
`appstream:CreateAppBlockBuilderStreamingURL` on:

```text
arn:aws:appstream:us-east-1:228478051196:app-block-builder/ht-appstream-nonexistent-app-block-builder
```

The exact resource reached `ResourceNotFoundException`, another builder name was denied on its
different ARN, and `DescribeAppBlockBuilders` was denied. The session had no create/update,
association, start, or `iam:PassRole` permission.

## Safe live success proof

A disposable `stream.standard.small` builder and inactive APPSTREAM2 app block were created and
associated in the default VPC. Once the builder reached `RUNNING`, the URL API returned HTTP 200
and a 60-second bearer URL. Only its length and expiry were inspected; the URL was never printed,
saved, or redeemed. No desktop session, application install, VHD, or package upload occurred.

This proves the successful control-plane path and its prerequisites. The administrative packaging
and machine-role impacts are documented service behavior; the fixture deliberately had no machine
role and the URL was not opened, so no inside-session behavior is presented as live proof.

## Telemetry

CloudTrail recorded the successful `CreateAppBlockBuilderStreamingURL` request as a default
management write (`readOnly:false`). It retained the builder name and `validity:60`, and replaced
`responseElements.streamingURL` with `HIDDEN_DUE_TO_SECURITY_REASONS`. Failed exact-resource and
denied-resource attempts were also present after propagation; the service represented the
builder-not-found response as generic `UnknownError`.

Package completion can additionally create S3 object activity, but CloudTrail S3 data-event
logging is optional. Local installer/filesystem activity is not an AppStream API event. Detect the
URL call and correlate it with builder session state, app-block activation, destination-bucket
writes, and later calls by the builder machine role.

## Cleanup evidence

The builder was stopped, disassociated, and deleted. The app block, empty packaging bucket, and
temporary AppStream service role were deleted. Independent final checks returned zero matching
builders, app blocks, associations, and AppStream network interfaces; the exact bucket and role
were absent. The expired URL was never redeemed. No image, fleet, stack, application, VHD, EC2
instance, or other persistent resource was created.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateAppBlockBuilderStreamingURL.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/app-block-builder.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/app-block-builder-actions.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/appstream-app-blocks-create.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateAppBlockBuilder.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/connect-app-block-builder.html
