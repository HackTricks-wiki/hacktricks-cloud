# AppStream image export to EC2 AMI — 2026-09-30

## Outcome

Documented `appstream:CreateExportImageTask` plus `iam:PassRole` as a private-image extraction path.
The task materializes an owned WorkSpaces Applications image as an EC2 AMI in the same account,
making the golden image consumable through normal EC2 launch/copy/share workflows.

Expected AWS functionality only. No AWS defect or private report.

## Current product boundaries

- The image must be owned by the caller's account, available, and Microsoft Windows Server 2022 or
  2025. Shared images cannot be exported directly.
- Export removes the WorkSpaces Applications agent and Microsoft license-included applications.
- The AMI stays private, in the same account and Region. Separate EC2 permissions are required to
  launch, inspect, copy, or share it.
- `IamRoleArn` is mandatory. The role trusts `appstream.amazonaws.com` and needs
  `ec2:CopyImage`, `ec2:DescribeImages`, and `ec2:CreateTags`.
- The caller needs `iam:PassRole` on that role. PassRole does not grant the role credentials to the
  caller; AppStream uses the role to produce the AMI.

## Safe live authorization proof

Authorized account `228478051196`, Region `us-east-1`. Preflight and final inventory both contained:

- zero private AppStream images;
- zero AppStream export-image tasks;
- zero self-owned EC2 AMIs with the `ht-appstream-*` prefix.

All calls used the impossible image `ht-appstream-nonexistent-export-image`, AMI name
`ht-appstream-nonexistent-export-ami`, and nonexistent role
`arn:aws:iam::228478051196:role/ht-appstream-nonexistent-export-role`.

Inline STS-policy results:

1. `CreateExportImageTask` alone reached an explicit `iam:PassRole` AccessDenied.
2. Adding exact-role PassRole with `iam:PassedToService=appstream.amazonaws.com` reached
   `ResourceNotFoundException` for the image, proving both IAM gates passed.
3. The same session remained denied for `ListExportImageTasks`, so task enumeration is not an
   implicit dependency.
4. Scoping `CreateExportImageTask` to the exact synthetic image ARN was denied. The error named
   `arn:aws:appstream:us-east-1:228478051196:image/*` as the authorization resource.
5. Replacing the exact ARN with that Region/account `image/*` wildcard reached image-not-found.
6. A separate list-only STS policy successfully returned zero tasks, confirming
   `ListExportImageTasks` is independently authorized and not a create dependency.

The Service Authorization Reference currently shows no resource type for `CreateExportImageTask`
while listing `aws:ResourceTag` as a condition. The live result indicates a wildcard image
pseudo-resource is accepted but per-image ARN scoping is not. This is an IAM/documentation nuance,
not treated as a security vulnerability; tag-condition behavior remains untested because no image
fixture exists.

No IAM role, image, task, AMI, snapshot, instance, or tag was created. Cleanup was vacuous.

## Impact boundaries

The exported AMI can expose proprietary applications, internal configuration, cached data, and
credentials mistakenly baked into the golden image. The action is valuable when the attacker also
has EC2 consumption/sharing permissions or can hand the AMI to another compromised principal. It is
post-exploitation/data disclosure, not automatic IAM privilege escalation.

## Telemetry

CloudTrail Event History recorded `CreateExportImageTask` as a management event with
`readOnly:false`.

- The no-PassRole denial had `requestParameters:null` and an `AccessDenied` message naming the
  missing role authorization.
- The service-authorized image-not-found event retained `imageName`, `amiName`, and `iamRoleArn` in
  `requestParameters`, but represented the service failure as generic `UnknownError`.
- Successful `ListExportImageTasks` appeared as a management read with `readOnly:true`, retained
  `maxResults`, and omitted its empty response (`responseElements:null`).
- `iam:PassRole` produced no standalone event.

A successful export should be correlated with the AppStream event, service use of the passed role,
EC2 `CopyImage`/`CreateTags`, export-task inventory, and the new AMI. Successful downstream telemetry
was not claimed because no eligible image existed.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateExportImageTask.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/export-image.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
