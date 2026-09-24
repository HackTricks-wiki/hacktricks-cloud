# AppStream 2.0 — tested

## NEGATIVE — `appstream:DescribeDirectoryConfigs` does NOT disclose the service-account password
- **Hypothesis:** DescribeDirectoryConfigs returns `ServiceAccountCredentials {AccountName, AccountPassword}`
  (both `sensitive:true` in botocore) → thought it might leak the AD domain-join password in cleartext.
- **Tested live (2026-09-25, acct 228478051196, us-east-1):** created a directory config with a known
  service-account password, then DescribeDirectoryConfigs. Response returns **only `AccountName`**
  (`DOMAIN\username`) — the `AccountPassword` field is **redacted / omitted**. `grep` for the plaintext
  password across the full JSON = NO match. Directory config deleted, verified gone.
- **Conclusion:** NOT a credential-disclosure technique. Only value is minor recon — it reveals the AD
  domain name + the privileged domain-join service-account username (targeting info), not the password.
  Below the no-garbage bar; not shipped to the wiki.
- **Calibration:** botocore `sensitive:true` means "scrub from logs", NOT "returned in the response".
  AWS redacts stored passwords from Describe/List output. See STATUS.md dead-lens note. [[dms]]
