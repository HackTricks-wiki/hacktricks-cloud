# Analytics Hub privilege-escalation checklist

## Completed

- [x] Separate listing subscription, data-clean-room exchange subscription, and IAM self-grant.
- [x] Cover linked BigQuery datasets and linked Pub/Sub subscriptions.
- [x] Verify current predefined role contents with local role metadata.
- [x] Reconcile v1 exact audit methods, permission types, LRO status, and default visibility.
- [x] Add BigQuery job, shared-dataset-usage, Pub/Sub creation, and message-method telemetry.
- [x] Bound restricted export, clean-room analysis rules, commercial approval, regional, and VPC-SC prerequisites.
- [x] Remove publish, enumeration, subscription administration, and denial-of-service headings from the privilege-escalation page.
- [x] Validate IAM policy mutation as version-3 and `etag` preserving.
- [x] Independently verify REST transports, request shapes, linked-resource identities, IAM policy preservation, clean-room cardinality, and clean-room privacy bounds.

## Safe future validation

- [ ] In disposable publisher/subscriber projects, subscribe a least-privileged custom principal to a synthetic BigQuery listing and capture Analytics Hub plus BigQuery dataset/job audit entries. Delete the linked dataset and all publisher-side test resources immediately.
- [ ] Repeat with a synthetic shared Pub/Sub topic and a pull-only linked subscription. Confirm the API's exact custom-role minimum, whether `analyticshub.subscriptions.create` is checked despite being absent from the `SubscribeListing` audit contract, the consume check, exact creation-log principal, and absence of Pull/Acknowledge audit entries; delete both sides immediately.
- [ ] Create a synthetic data clean room with an aggregation-threshold view and verify that exchange subscription cannot bypass the analysis rule. Capture both LRO entries, then delete the linked datasets, subscription, listing, exchange, and source dataset.
- [ ] Compare `INFORMATION_SCHEMA.SHARED_DATASET_USAGE` with subscriber email logging disabled and enabled, using only synthetic identities and rows.
- [ ] Resolve the official prose-versus-permission-table inconsistency for `roles/analyticshub.publisher`; do not claim update/delete/set-IAM until role metadata or a live least-privilege test supports it.
- [ ] Resolve the current audit-page inconsistency for v1 `SubscribeListing`: method detail says Data Access, while the `ADMIN_WRITE` permission table and the page's classification rule imply Admin Activity. Capture the actual log name in the disposable listing test above before changing the default-visibility claim.
