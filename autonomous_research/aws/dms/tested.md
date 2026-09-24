# DMS — tested

## NEGATIVE — `dms:DescribeEndpoints` does NOT disclose stored endpoint passwords
- **Hypothesis (historical claim):** DescribeEndpoints leaks the endpoint DB `Password` in cleartext.
- **Tested live (2026-09-25, acct 228478051196, us-east-1):** created a mysql source endpoint with
  `--password`, then DescribeEndpoints. Response returns `Username`, `ServerName`, `Port`,
  `MySQLSettings.AuthenticationMethod=password` — but **no password value**. The top-level
  `Endpoint.Password` member has been **removed from the output shape entirely** (botocore: Endpoint
  output has `Username` but no `Password`); nested engine-settings passwords are likewise not returned.
  `grep` for the plaintext password = NO match. Endpoint deleted (async), verified deleting→gone.
- **Conclusion:** AWS has closed this historical disclosure. NOT a technique. The DMS enum page already
  covers the still-valid angle (endpoint-repoint / role abuse). Not shipped.
- **Calibration:** confirms the AppStream finding — the "Describe returns a stored password" lens is
  dead across AWS. [[appstream]]
