# Amazon S3 Files (s3files) — tested

## VERIFIED (authz, two-sided) — `s3files:CreateFileSystem` + `iam:PassRole` data-access privesc
- **Service:** S3 Files (API 2025-05-05, IAM prefix `s3files:`) = EFS-backed file-system view of an S3
  bucket, reached via VPC mount targets. CreateFileSystem takes `bucket` + `roleArn`; the FS accesses
  the bucket AS the passed role. GA and ACCESSIBLE in lab (us-east-1) — `list-file-systems` returns [].
- **Result (2026-09-25, acct 228478051196, us-east-1):**
  - NEGATIVE (only s3files:CreateFileSystem, no PassRole): `AccessDeniedException ... not authorized to
    perform: iam:PassRole on the specified resource`.
  - NEGATIVE2 (PassRole scoped to wrong arn): same iam:PassRole denial.
  - POSITIVE (PassRole allowed on target role): `ResourceNotFoundException: The bucket you specified
    does not exist` => BOTH s3files:CreateFileSystem and iam:PassRole passed; only the bogus bucket
    stopped it. Any bucket ARN accepted. Target role must trust s3files.amazonaws.com.
  - No file system created (bogus bucket). Roles ht-s3f-target/ht-s3f-att torn down (NoSuchEntity); no
    stray file systems.
- **Attack:** CreateFileSystem over any bucket with a privileged role + CreateMountTarget in a reachable
  subnet + mount (NFS) -> read/write that bucket's data as the role, bypassing the bucket's own policy.
- **Min perms:** `s3files:CreateFileSystem`, `iam:PassRole` (on an s3files-trusting role), `s3files:CreateMountTarget`
  (+ network foothold in the VPC to mount). Data-access privesc / exfil.
- **Status:** SHIPPED — aws-services/aws-s3-files-enum.md (new page), SUMMARY wired, PR #413.

## Doc-grounded (not live-tested; would need a real file system => cost/VPC)
- `s3files:PutFileSystemPolicy`/`DeleteFileSystemPolicy` — file-system resource policy => cross-account
  data exposure (same class as S3/EFS resource policies). Add to cross-account resource-policy matrix.
- `s3files:CreateMountTarget`/`UpdateMountTarget` — security-group/subnet control => network exposure of
  the NFS data plane (lateral movement).
