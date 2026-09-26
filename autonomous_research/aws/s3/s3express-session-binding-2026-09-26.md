# S3 Express `CreateSession` binding audit — 2026-09-26

## Outcome

Negative / secure boundary result. S3 Express session credentials stayed bound to the exact directory
bucket, requested/authorized mode, and complete returned credential tuple. No cross-bucket read,
ReadOnly-to-ReadWrite escalation, token mutation, or credential-field splice succeeded. This is
expected behavior, so no AWS vulnerability report was created.

The useful expected behavior was added to the existing S3 Express enumeration section: exact minimum
IAM, mode fallback, credential handling, impact, stealth, and CloudTrail data-event requirements.

## Fixture and minimum IAM

- Region/AZ: `us-east-1`, `use1-az6`.
- Two disposable S3 Express One Zone directory buckets in the same AZ, each containing one synthetic
  marker.
- Restricted role had only `s3express:CreateSession` on bucket A's exact
  `arn:aws:s3express:...:bucket/...` ARN, conditioned on
  `s3express:SessionMode = ReadOnly`.
- No bucket-B permission and no `s3:GetObject`, `s3:PutObject`, or other object-action grants.
- Requests used raw SigV4 with signing name `s3express`; SDK automatic session refresh was bypassed.
- The session tuple used `x-amz-s3session-token`, while the caller's assumed-role credential used the
  normal `x-amz-security-token` for `CreateSession`.

## Verified matrix

| Case | Result |
| --- | --- |
| Bucket A explicit `ReadOnly` issuance | HTTP 200 |
| Bucket A omitted mode | HTTP 200; subsequent PUT denied, proving fallback to allowed ReadOnly |
| Bucket A explicit `ReadWrite` issuance | `AccessDenied` |
| Bucket B explicit `ReadOnly` issuance | `AccessDenied` |
| ReadOnly GET/list A | HTTP 200; exact marker recovered |
| ReadOnly PUT/delete A | `AccessDenied` |
| Complete A tuple used against B | `AccessDenied` |
| Replay unchanged A tuple before expiration | HTTP 200; expected |
| Freshly signed GET with same tuple after its returned expiration + 10 seconds | `AccessDenied` |
| One-character session-token mutation | Rejected (`InvalidRequest`) |
| A key/secret + B token | Rejected (`InvalidAccessKeyId`) |
| B key/secret + A token | Rejected (`InvalidAccessKeyId`) |
| A ReadOnly key/secret + same-bucket admin ReadWrite token | Rejected (`InvalidAccessKeyId`) |
| A admin ReadWrite key/secret + ReadOnly token | Rejected (`InvalidAccessKeyId`) |
| A ReadOnly key/secret + a second A ReadOnly token | Rejected (`InvalidAccessKeyId`) |
| A session credentials HEAD A at Zonal endpoint | HTTP 200 |
| Same A session credentials HEAD B | HTTP 403 |

The same-bucket privileged-token splice is the decisive mode-boundary result: privilege is not carried
solely in a swappable token, and the three returned fields cannot be recombined across sessions.

## REST and documentation notes

- Raw `CreateSession` required `x-amz-content-sha256` even for the empty GET request. Omitting it
  returned `InvalidRequest: Missing header: x-amz-content-sha256`.
- Directory-bucket endpoint form was
  `BUCKET.s3express-ZONE_ID.REGION.amazonaws.com`; path-style requests were not used.
- Two preliminary cycles that found the missing raw header deleted both buckets in `finally` and were
  fixture corrections, not security results.
- AWS documentation says `HeadBucket` should use IAM credentials rather than session credentials, but
  a correctly signed session request to A's Zonal endpoint returned 200 while the same tuple against B
  returned 403. This did not cross the bucket or mode boundary and is retained as a documentation/
  compatibility regression case, not a vulnerability.

## CloudTrail

- `CreateBucket` and `DeleteBucket` are default management events from `s3express.amazonaws.com`.
- `CreateSession`, `GetObject`, `ListObjectsV2`, `PutObject`, `DeleteObject`, and `HeadBucket` are data
  events and are not recorded by default.
- Directory-bucket object activity requires an advanced event selector for resource type
  `AWS::S3Express::Object`; default Event History therefore cannot verify these session/data calls.
- No temporary trail or paid data-event selector was created solely for this negative test.

## Cleanup

Every cycle used `finally` cleanup. Fresh admin ReadWrite sessions listed and removed the synthetic
objects, both directory buckets were deleted, and the inline policy/test role were removed. Independent
inventory was empty for directory buckets and IAM roles matching the `ht-s3e-` prefix after the final
expiration check.
