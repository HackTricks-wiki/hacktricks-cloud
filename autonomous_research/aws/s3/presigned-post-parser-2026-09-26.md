# S3 SigV4 presigned POST multipart parser and revocation — 2026-09-26

## Result

**NEGATIVE / secure behavior.** A 34-case raw multipart/form-data matrix found no way to make an S3 SigV4 browser POST policy restricted to `allowed/` create an object outside that byte prefix. Duplicate/conflicting policy, signature, temporary-credential, key, content-type, encryption, filename, and file parts either failed or produced an allowed-prefix object consistent with the signed policy.

Two already-issued forms and a newly generated form also honored a later explicit IAM `Deny` after normal propagation. No AWS vulnerability report or public-book technique was created from this negative result.

## Fixture and signed boundary

- Region: `us-east-1`
- Private general-purpose bucket: `ht-post-3fc249393923`
- Versioning: never enabled
- Object Lock: never enabled
- Block Public Access: all four settings enabled
- Signer role: `ht-post-3fc249393923-signer`
- Signer permission: only `s3:PutObject` on the disposable bucket's objects
- Two separate assumed-role sessions generated independent forms
- Form lifetime: 300 seconds

The role intentionally had broad object permission within the disposable bucket. The boundary under test was the more restrictive signed POST policy. Before any HTTP request, the harness decoded and asserted that every SDK-generated policy contained:

```json
{
  "conditions": [
    {"bucket": "ht-post-3fc249393923"},
    ["starts-with", "$key", "allowed/"],
    {"x-amz-server-side-encryption": "AES256"},
    {"success_action_status": "201"},
    ["content-length-range", 1, 16]
  ]
}
```

The actual policy also contained exact SigV4 algorithm, credential, date, and temporary-session-token conditions. The key field was `allowed/${filename}`.

Raw HTTPS bodies preserved duplicate field names and ordering. After every request, an administrator listed the **entire bucket** and called `HeadObject` for every new key. Any stored key not byte-prefixed `allowed/` was the failure oracle.

## Verified matrix

| Cases | Result |
| --- | --- |
| Normal 8-byte baseline | HTTP 201; `allowed/base.txt`, length 8, SSE-S3 `AES256` |
| Duplicate `key`: allowed→denied, denied→allowed, allowed→denied→allowed, denied→allowed→denied | All HTTP 400 `InvalidArgument`; no object |
| `Key`, `KEY`, `key `, and RFC 5987 `name*=UTF-8''key` variants | HTTP 400 `InvalidArgument`; no object |
| Filename `../../denied/traversal` | HTTP 201; basename only at `allowed/traversal` |
| Filename `..\\..\\denied\\backslash` | HTTP 201; basename only at `allowed/backslash` |
| Filename `%2e%2e%2fdenied%2fencoded` | HTTP 201; encoded text stored literally under `allowed/` |
| Filename `allowed/../denied/literal` | HTTP 201; basename only at `allowed/literal` |
| Repeated slash and Unicode division-slash filenames | HTTP 201; basename/literal value remained under `allowed/` |
| Empty filename | HTTP 201 at literal key `allowed/` |
| Conflicting `filename` + traversal-shaped `filename*` | HTTP 201; basename `allowed/conflict` |
| File part before fields plus trailing denied key | HTTP 400 `InvalidArgument`; no object |
| Two file parts, small→17 bytes and 17 bytes→small | HTTP 400 (`InvalidArgument` / `EntityTooLarge`); no object |
| File lengths 1 and 16 | HTTP 201, exact stored lengths |
| File lengths 0 and 17 | HTTP 400 `EntityTooSmall` / `EntityTooLarge`; no object |
| Duplicate SSE `AES256`/`aws:kms` in both orders | HTTP 403 `AccessDenied`; no object |
| Duplicate signed content types `image/png`/`text/html` in both orders | HTTP 403 `AccessDenied`; no object |
| Valid + mutated policy in both orders | HTTP 403; no object |
| Duplicate credential/token/signature tuples from two signer sessions in both orders | HTTP 400 `InvalidArgument`; no object |
| Session-1 policy/signature with session-2 credential/token, and inverse | HTTP 403 `SignatureDoesNotMatch`; no object |

Canonicalization-shaped filenames that succeeded were not escapes. S3 object keys are not filesystem paths; the exact resulting keys still began with `allowed/`.

## Live IAM revocation

Fresh forms from signer sessions S1 and S2 first created unique 8-byte objects with HTTP 201. The role's inline policy was then updated with an explicit `Deny` for `s3:PutObject` on every object in the disposable bucket. Each poll checked:

- IAM `SimulatePrincipalPolicy`;
- reuse of both already-issued forms;
- a form generated locally after the deny from still-valid S1 credentials; and
- a direct administrator `PutObject` health control.

| Elapsed after deny | Simulation | Old S1 form | Old S2 form | Newly generated form | Admin health |
| --- | --- | --- | --- | --- | --- |
| 1.5 seconds | `explicitDeny` | 201 | 201 | 201 | 200 |
| 8.4 seconds | `explicitDeny` | 201 | 403 | 403 | 200 |
| 15.1 seconds | `explicitDeny` | 403 | 403 | 403 | 200 |

This demonstrates ordinary asynchronous propagation across independently assumed sessions, not a stable permission snapshot. Both old forms and a locally generated new form were revoked within 15.1 seconds.

## Logging

Presign generation is local and creates no AWS API event. A browser POST is an S3 `PutObject` **data event**, which is not present in default Event History unless an S3 object data-event selector is enabled. AWS identifies this authentication method as `HtmlForm` in CloudTrail. The role-policy update is a default IAM `PutRolePolicy` management event.

No paid trail or data-event selector was created solely for this negative test; HTTP responses plus full-bucket inventory were the decisive oracle.

## Cleanup

Browser POST is one atomic `PutObject`, not S3 Multipart Upload. Cleanup nevertheless called `ListMultipartUploads` and confirmed **zero** uploads. Final inventory contained 15 objects, all under `allowed/`; the harness deleted all 15, confirmed versioning remained unset, then deleted the bucket, inline role policy, and signer role.

Independent post-test inventory returned no bucket or IAM role starting with `ht-post-`.

## References

- https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html
- https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html
- https://docs.aws.amazon.com/botocore/latest/reference/services/s3/client/generate_presigned_post.html
- https://docs.aws.amazon.com/prescriptive-guidance/latest/presigned-url-best-practices/overview.html
- https://docs.aws.amazon.com/prescriptive-guidance/latest/presigned-url-best-practices/faq.html
- https://docs.aws.amazon.com/prescriptive-guidance/latest/presigned-url-best-practices/identifying-requests.html

