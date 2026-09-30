# AppStream private-image sharing — 2026-09-30

## Outcome

Documented `appstream:UpdateImagePermissions` as a cross-account golden-image disclosure and durable
copy primitive. `allowFleet` grants runtime fleet use; `allowImageBuilder` lets the recipient create
image builders and independent images that survive later revocation.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- Images are Regional and may be shared only for use in the same Region.
- The owner selects `allowFleet`, `allowImageBuilder`, or both for a 12-digit recipient account.
- Fleet-only access stops producing new instances after revocation; AWS sets affected desired
  capacity to zero while existing sessions finish.
- Image-builder access is intentionally durable: recipient-created builders/images remain after the
  owner removes the share. A builder session gives local administrator access on Windows and
  `ImageBuilderAdmin`/root privileges on Linux.
- The owner-side minimum is `appstream:UpdateImagePermissions` on the exact image ARN. The Service
  Authorization Reference supports image resource scoping and `aws:ResourceTag` conditions.
- The share does not itself grant an owner-account IAM identity or role. Recipient-side builder/fleet
  actions and prerequisites remain separate.

## Safe live authorization proof

Authorized account `228478051196`, Region `us-east-1`.

Preflight returned zero owned private images and zero images shared with the account. An inline STS
session policy then allowed only `appstream:UpdateImagePermissions` on:

```text
arn:aws:appstream:us-east-1:228478051196:image/ht-appstream-nonexistent-share-probe
```

Results:

- the exact image name and syntactically valid foreign account reached
  `ResourceNotFoundException`, proving the image-scoped authorization passed;
- a different image name returned `AccessDeniedException` on its distinct image ARN;
- `DescribeImages` returned `AccessDeniedException`, proving enumeration was not inherited;
- the exact image with the owner account as recipient passed IAM and reached the service's explicit
  same-account validation error.

Only impossible synthetic image names were used. No image, share, builder, fleet, IAM role, or other
resource was created, and cleanup was vacuous.

## Impact boundaries

The security impact is conditional on image content. A golden image can hold proprietary software,
internal configuration, cached data, or credentials mistakenly baked into the filesystem. With
builder permission, the foreign account can inspect it with administrative privileges and retain a
derived copy. Fleet-only permission is useful for running the image but is less durable.

## Telemetry

CloudTrail Event History recorded both service-authorized failed probes as
`UpdateImagePermissions` management events with `readOnly:false`. `requestParameters` retained:

- `name`;
- `sharedAccountId`;
- `imagePermissions.allowFleet`;
- `imagePermissions.allowImageBuilder`.

The service surfaced the tested validation/not-found failures in CloudTrail as generic
`errorCode: UnknownError` / `errorMessage: An unknown error occurred`, so detection should key on the
event and request parameters instead of relying on precise failure codes. Successful response-body
logging was not tested because no real image existed. Recipient-side builder/fleet/session events
occur in the recipient account and are not present in the owner's trail.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateImagePermissions.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/share-image-with-another-account.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/managing-image-builders-connect-console.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/service-name-info-in-cloudtrail.html
