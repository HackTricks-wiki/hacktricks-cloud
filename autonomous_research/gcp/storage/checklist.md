# Cloud Storage — open ideas

- [ ] In a disposable bucket where detailed audit logging mode is already approved, compare request
  fields for IAM/ACL, IP-filter, retention, versioning and lifecycle changes. Do not claim the default
  `request=null` shape is universal.
- [ ] Recheck whether Storage Batch Operations transformation logs are enabled by default for any
  future job type and whether they preserve the initiating principal across per-object actions.
- [ ] In a project whose target bucket was already enrolled in Storage Intelligence, create an
  isolated caller with Batch Operations Admin and zero Storage permissions. Give the job-project
  service agent Object Admin only on a synthetic bucket containing known-size prefix markers; run
  `dryRun=true` and determine whether counters expose their count/bytes. Use caller Object Viewer or
  Object Admin only as positive controls, then remove all grants and delete the job/LRO and bucket.
  Never activate a one-time trial solely for this test; keep a real authorization gap private-first.
- [ ] Repeat the prepared-fixture matrix with an enrolled bucket in a second authorized project and
  separately with project-source/CEL selection. The former exercises the job-project service agent;
  current troubleshooting says the latter uses caller credentials.
- [ ] Monitor signed-URL and soft-delete changes for any new cross-project or restoration boundary;
  avoid duplicating ordinary object read/write techniques.
