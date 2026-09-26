
## S3 Access Grants — marginal Update-variant (not shipped)
- `s3control:UpdateAccessGrantsLocation --iam-role-arn` + PassRole repoints an EXISTING Access Grants
  location's role; GetDataAccess for grants on that location then vends the NEW role's creds. This is the
  Update analog of the DOCUMENTED CreateAccessGrantsLocation+PassRole+CreateAccessGrant+GetDataAccess
  privesc (aws-s3-privesc). Same outcome; only value is when Create is denied but Update allowed. Marginal
novelty — NOT shipped to avoid duplicating the existing technique. Revisit only if a distinct angle emerges.

## Completed negative security test

- [x] `GetDataAccess` target canonicalization escape across an `allowed/*` grant. Dot segments,
  repeated/encoded separators, double encoding, backslashes, Unicode slash variants, and wildcard
  forms did not produce credentials usable against a sibling `denied/*` object. See
  `access-grants-canonicalization-2026-09-26.md`.
- [x] S3 Express `CreateSession` bucket/mode/credential binding. Exact-bucket `ReadOnly` sessions
  could not write, cross to a sibling bucket, or gain rights by mixing/mutating tuple fields. Omitted
  mode fell back to the maximum allowed (`ReadOnly`). See `s3express-session-binding-2026-09-26.md`.
