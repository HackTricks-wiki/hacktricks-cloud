
## S3 Access Grants — marginal Update-variant (not shipped)
- `s3control:UpdateAccessGrantsLocation --iam-role-arn` + PassRole repoints an EXISTING Access Grants
  location's role; GetDataAccess for grants on that location then vends the NEW role's creds. This is the
  Update analog of the DOCUMENTED CreateAccessGrantsLocation+PassRole+CreateAccessGrant+GetDataAccess
  privesc (aws-s3-privesc). Same outcome; only value is when Create is denied but Update allowed. Marginal
  novelty — NOT shipped to avoid duplicating the existing technique. Revisit only if a distinct angle emerges.
