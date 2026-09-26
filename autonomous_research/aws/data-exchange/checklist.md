# AWS Data Exchange autonomous research checklist

- [x] Revalidate the current `CreateDataGrant` and `PublishToDataGrant` authorization boundary.
- [x] Separate receiver acceptance from sender grant creation.
- [x] Document owned-data-set, finalized-revision, and license-distribution prerequisites.
- [x] Bound expiry, deletion/revocation, copy persistence, and sender billing.
- [x] Audit `EXPORT_ASSET_TO_SIGNED_URL`, `EXPORT_ASSETS_TO_S3`, and `EXPORT_REVISIONS_TO_S3` as
  direct-export alternatives.
- [x] Add local CloudTrail tables and exact useful request fields to every retained technique.
- [x] Inventory permitted lab Regions without creating a paid or externally addressed grant.
- [ ] On a future account with two explicitly controlled AWS accounts and an existing disposable file
  data set, re-run isolated sender and receiver policies and capture sanitized write events.
- [ ] Verify whether accepted-grant deletion is surfaced as `DeleteDataGrant` plus the documented Data
  Grant Revoked EventBridge event in both accounts; do not assume exported copies are recoverable.

Current detailed record: `post-exploitation-audit-2026-09-26.md`.
