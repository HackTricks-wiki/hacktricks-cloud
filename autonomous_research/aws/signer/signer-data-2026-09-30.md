# AWS Signer Data Plane revocation audit — 2026-09-30

## Result

Reasoned exclusion from the public attack book. The newly exposed `signer-data` client duplicates the existing `GetRevocationStatus` operation on a `data-signer` endpoint. It checks only identifiers already carried by a signed artifact and correctly requires authentication plus authorization to both the signing profile and signing job. Nonexistent identifiers return an empty revocation set rather than an existence signal.

## API and IAM model

- Client/service model: `signer-data` / `2017-08-25`; endpoint prefix `data-signer`; SigV4 signing name and IAM prefix remain `signer`.
- Required inputs are signature timestamp, platform ID, profile-version ARN, job ARN and one or more composite certificate hashes. The response contains only which supplied identifiers are revoked.
- The ordinary `signer` client and the separate `signer-data` client returned the same empty response for the same synthetic request.
- The documented permission is `signer:GetRevocationStatus`. Service Authorization lists both `signing-profile` and `signing-job` resource types.

## Live authorization matrix

Used syntactically valid but nonexistent same-account profile/job identifiers with the Notation platform and a synthetic certificate hash:

| Session policy | Result |
| --- | --- |
| No signature (`--no-sign-request`) | `MissingAuthenticationTokenException` |
| Exact synthetic job only | Denied on the profile ARN |
| Exact synthetic profile only | Denied on the job ARN |
| Both exact synthetic profile and job | Success, `revokedEntities: []` |
| Admin via legacy `signer` client | Success, `revokedEntities: []` |
| Admin via new `signer-data` client | Success, `revokedEntities: []` |

The dual-resource check therefore does not exhibit the common multi-resource authorization bypass where access to either side incorrectly authorizes the whole request. The empty response also does not distinguish nonexistent resources from existing non-revoked resources.

## Rejected attack ideas

| Idea | Result |
| --- | --- |
| Unauthenticated revocation oracle | Rejected before semantic validation |
| Profile/job existence oracle | Nonexistent identifiers returned the normal empty non-revoked result |
| Query a victim profile with permission only on an attacker job | Denied on the missing profile authorization |
| Query a victim job with permission only on an attacker profile | Denied on the missing job authorization |
| Cross-account reconnaissance | At most checks revocation of identifiers already present in a signed artifact and explicitly authorized in IAM; no names, job metadata, payload, signer identity expansion or certificate material are returned |
| Separate-client policy bypass | Both endpoints use the same `signer:GetRevocationStatus` permission and behavior |

`GetRevocationStatus` remained absent from Event History after the same delay that made adjacent Inspector Scan management events visible. Record this live absence, but do not claim that every trail configuration or future Signer implementation omits it solely from an Event History negative.

## Cleanup

No signing profile, job, payload, S3 object, key, certificate or other AWS resource was created or changed. The audit reused only synthetic identifiers and the already-canceled `ht_signer_test_23614` profile for read-only platform context. Restricted STS sessions expire after 15 minutes; there is nothing persistent to delete.
