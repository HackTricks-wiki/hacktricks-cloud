# Amazon S3 Files (s3files) — checklist

- [ ] Live-verify PutFileSystemPolicy cross-account: create a small FS over a throwaway bucket, put a
      resource policy naming an external account, confirm cross-account mount/access. Cost: FS is
      EFS-backed (hourly) — do in a compute-authorized run; tear down FS + mount targets + bucket.
- [ ] Confirm whether CreateFileSystem's roleArn trust must be exactly s3files.amazonaws.com or accepts
      a broader principal; test acceptBucketWarning bypass of bucket-config warnings.
- [ ] GetSynchronizationConfiguration / PutSynchronizationConfiguration — does changing sync direction
      enable overwriting bucket objects from the file side (integrity attack)?
- [ ] Access point posixUser/rootDirectory — privilege boundary bypass across tenants on a shared FS.
