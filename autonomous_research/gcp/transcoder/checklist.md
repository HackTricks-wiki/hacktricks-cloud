# Transcoder — open validation leads

- [ ] With one harmless synthetic media object, validate the exact source/destination Cloud Storage
  permissions and audit principals under a minimum `transcoder.jobs.create` custom role.
- [ ] Compare default-template output against a custom spritesheet-only job to determine the least
  lossy useful disclosure path and document size/format limits.
- [ ] Verify whether CMEK-protected input/output adds any Cloud KMS permissions or audit events that
  materially change the caller or service-agent boundary.

Any live validation must use disposable buckets and non-sensitive generated media, avoid deletion
features, and remove jobs, objects, buckets, and IAM grants immediately afterward.
