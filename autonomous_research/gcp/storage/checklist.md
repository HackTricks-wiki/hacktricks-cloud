# Cloud Storage — open ideas

- [ ] In a disposable bucket where detailed audit logging mode is already approved, compare request
  fields for IAM/ACL, IP-filter, retention, versioning and lifecycle changes. Do not claim the default
  `request=null` shape is universal.
- [ ] Recheck whether Storage Batch Operations transformation logs are enabled by default for any
  future job type and whether they preserve the initiating principal across per-object actions.
- [ ] Monitor signed-URL and soft-delete changes for any new cross-project or restoration boundary;
  avoid duplicating ordinary object read/write techniques.
