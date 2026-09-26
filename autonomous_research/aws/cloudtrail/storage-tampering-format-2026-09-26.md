# CloudTrail storage and Lake tampering accuracy audit — 2026-09-26

## Result

Completed minimum-permission, prerequisite, stealth, and recovery metadata for the remaining
CloudTrail storage tampering techniques: S3 lifecycle expiry, Event Data Store retention/deletion,
destination-bucket disruption, and S3/KMS log ransomware.

Important corrections retained in the public page:

- S3 lifecycle expiration is asynchronous; a versioned bucket's current-version expiration creates a
  delete marker unless noncurrent versions are also expired, and Object Lock still protects retained
  versions.
- The valid nondestructive Lake collection stop is `StopEventDataStoreIngestion`; an empty advanced
  selector is not the equivalent.
- Lake deletion can require clearing termination protection, disabling federation, or deleting an
  integration channel, and has an exact seven-day `PENDING_DELETION` restore window. Retention shrink
  removes aged-out events without a restore path.
- Bucket deletion requires removal of objects, versions, and delete markers and remains bounded by
  governance/compliance retention and legal holds.
- Changing a trail/bucket KMS configuration is not retroactive. Historical ciphertext is affected
  only if it already uses the targeted CMK or is separately copied/re-encrypted. `DisableKey` is
  reversible; scheduled deletion is cancellable for 7–30 days and cancellation leaves the key
  disabled until `EnableKey` is called.

No AWS calls or mutations were performed in this pass; it was a contract/accuracy review over the
existing techniques and recorded live authorization results.

## Sources

- <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/query-eds-disable-termination.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_StopEventDataStoreIngestion.html>
- <https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-kms-key-policy-for-cloudtrail.html>
