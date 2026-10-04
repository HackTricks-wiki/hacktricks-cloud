# AppStream UpdateFleet image replacement with role inheritance — 2026-09-30

## Outcome

Verified that exact-fleet `appstream:UpdateFleet` can replace an On-Demand fleet's AWS-owned image
while preserving its existing `IamRoleArn`, without Describe or caller-side PassRole permissions.
Documented the attacker-controlled private/shared image branch as conditional on image availability
and authorization.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- Always-On and On-Demand fleets launch instances from an AppStream image. Elastic fleets use app
  blocks/applications and are outside this path.
- A same-operating-system image can replace the image on a running fleet. Existing sessions remain
  on old instances, while new/replacement instances use the new image. Cross-OS replacement needs a
  stopped fleet.
- `UpdateFleet` does not require the request to repeat `IamRoleArn`. Omitting it preserves the
  existing machine role and does not perform a new caller-side PassRole check.
- Security impact requires an attacker-controlled image available to the fleet. A same-account
  private image works; a foreign owner can share a private image with `AllowFleet=true`.
- The malicious image can contain modified applications or image-baked session scripts, including
  SYSTEM-context hooks, which then execute on instances that inherit the fleet role.

## Live exact-fleet proof

Authorized account `228478051196`, Region `us-east-1`. A disposable stopped On-Demand fleet used
`stream.standard.small`, desired capacity zero, an AWS-owned Windows Server 2022 image, and a
harmless machine role.

An inline STS session policy containing only `appstream:UpdateFleet` on the exact fleet ARN changed
the fleet to a second AWS-owned Windows Server 2022 image. The response retained the original
machine-role ARN. `DescribeFleets` was denied and the session policy contained no `iam:PassRole`,
fleet start, image-builder, sharing, or session permission.

A second exact fleet+public-image policy produced the same successful result. Public AWS image ARNs
have an empty account field, and the first success proves that this public-image case did not need a
separate image statement. The service-authorization table lists `image` as an additional
`UpdateFleet` resource; the public technique conservatively requires exact-image authorization for
customer-owned/shared targets because that branch was not available for live testing.

No fleet instance or session was started. This proves the image mutation, role retention, and
public-image IAM minimum. The attacker-code branch follows the documented fleet image lifecycle but
remains explicitly conditional on a usable malicious private/shared image.

## Telemetry

CloudTrail recorded successful `UpdateFleet` as a default management event. It retained fleet name
and the full AWS-owned target image ARN. The response recorded the resulting image name/ARN,
unchanged role ARN, fleet type/state, capacity, instance type, and stream view. The observed event
omitted the optional `readOnly` field.

Detect any image change outside the approved release pipeline, validate target ownership/sharing,
and correlate replacement instances with first-seen calls by the fleet role.

## Cleanup evidence

The zero-capacity fleet was deleted without starting it. Its harmless machine role and the
temporary AppStream service role were deleted. Independent final checks returned zero matching
fleets and AppStream ENIs, and both roles were absent. No bucket, image, image builder, stack, URL,
session, or streaming instance was created.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateFleet.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/update-fleets-new-image.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateImagePermissions.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/use-session-scripts.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/using-iam-roles-to-grant-permissions-to-applications-scripts-streaming-instances.html
