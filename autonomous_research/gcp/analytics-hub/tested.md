# Analytics Hub privilege-escalation research

## 2026-09-28 — official documentation and local role audit

No cloud resource was created, changed, or deleted. The review used current BigQuery sharing, Analytics Hub REST/audit, BigQuery audit, Pub/Sub audit, and IAM-role documentation plus read-only local `gcloud iam roles describe` output.

### Retained primitives

- `analyticshub.listings.subscribe` crosses from listing access into the resource intentionally published by that listing. It can create either a read-only linked BigQuery dataset or a linked Pub/Sub subscription without source dataset/topic IAM.
- `analyticshub.dataExchanges.subscribe` is a distinct data-clean-room LRO. It requires source `dataExchanges.subscribe` and destination `subscriptions.create`, and creates linked datasets for the exchange's eligible listings. Its impact remains bounded by analysis rules.
- Listing or exchange `setIamPolicy` can grant `roles/analyticshub.subscriber`; an exchange binding is inherited by child listings. This is genuine policy-to-data escalation when destination-side creation/query or consume permissions also exist.

### Material corrections

- Corrected current v1 audit behavior: `SubscribeListing` is a non-LRO **Data Access** event even though the catalog labels its permission `ADMIN_WRITE`. Analytics Hub Data Access is disabled by default. `SubscribeDataExchange` is an **Admin Activity LRO** associated with destination `analyticshub.subscriptions.create` and is logged by default.
- Rejected the previous claim that linked-dataset reads are invisible to the publisher. BigQuery query jobs are logged by default, and `INFORMATION_SCHEMA.SHARED_DATASET_USAGE` gives the provider near-real-time consuming project, listing, object, rows, and bytes. Subscriber principal identity is populated only when subscriber email logging is enabled and accepted; that flag defaults false.
- Added Pub/Sub sharing. Linked subscription creation is durable/Admin Activity, while Pub/Sub does not audit Pull, StreamingPull, Acknowledge, or ModifyAckDeadline message operations.
- Reconciled a shared-topic documentation ambiguity. The audit contract identifies only `analyticshub.listings.subscribe` for `SubscribeListing`; the stream-sharing workflow also grants `roles/analyticshub.subscriptionOwner` on the specific listing, but does not establish `analyticshub.subscriptions.create` as a direct method check. The page therefore distinguishes the documented API permission from the broader role-based management workflow.
- Corrected minimum query permissions to include `bigquery.jobs.create` and `bigquery.tables.getData` through the linked dataset. Added clean-room `analyticshub.subscriptions.create` and bounded the result to analysis-rule-enforced views.
- Replaced the destructive blind IAM-policy example with a policy-version-3, `etag`-preserving read-modify-write command. The safe sequence needs the target's `getIamPolicy` in addition to `setIamPolicy`.

### Removed or reclassified material

- Removed exchange/listing creation and publishing from privilege escalation. Creating a listing requires `analyticshub.listings.create` plus `bigquery.datasets.get` and `bigquery.datasets.update` on the source; the caller already controls and can read that dataset. It can be an explicit ongoing sharing/exfiltration channel, but it does not acquire new source privileges and did not meet the privesc no-garbage bar.
- Removed subscription list/get/delete/update as an H3. List/get is enumeration, while delete/revoke is denial of service rather than privilege escalation. Subscription lifecycle remains useful for defenders but does not cross an access boundary for the caller.
- Did not rely on the older claim that `roles/analyticshub.publisher` itself includes listing update/delete/set-IAM permissions. The current authoritative permission table and live predefined role metadata contain `listings.create` but not those three permissions; Listing Admin carries update/delete/set-IAM. The prose role guide is internally inconsistent and is not used for the minimum-permission claims.

### Evidence limits

- No subscription, linked dataset, Pub/Sub subscription, IAM mutation, or API enablement was performed. API prerequisites and audit placement are based on current official contracts.
- The downstream linked-dataset `InsertDataset` and linked Pub/Sub `CreateSubscription` methods are documented audit methods for the resource types created by subscription, but the Analytics Hub contract does not guarantee a separate entry for service-created linked resources. The book labels them conditional downstream signals. A future disposable test should confirm emission and exact principal attribution.

## 2026-09-28 — independent cross-review

- Corrected both enumeration `getIamPolicy` examples to use the documented POST transport and a policy-v3 request body; the previous GET examples were not valid REST calls and could also omit conditional bindings from a policy review.
- Corrected clean-room cardinality: an exchange subscription creates one linked dataset containing the resources represented by all listings, not one linked dataset per listing.
- Removed the absolute clean-room claim that raw access is impossible. Official limitations state that directly shared tables, materialized views, and views without analysis rules expose raw data, and that analysis rules alone are not guaranteed to stop every extraction query.
- Confirmed that listing subscription is a synchronous `SubscribeListing` response, whereas clean-room `SubscribeDataExchange` is an LRO; the request paths and JSON shapes in the page match the current REST schemas.
- Confirmed the condition-safe IAM sequence: both IAM methods are POST, requested policy version 3 and the returned `etag` are retained, and `bindings,etag` is the documented default update mask.
- Kept the shared-topic custom-role minimum deliberately bounded. Current official documentation names `analyticshub.listings.subscribe` for the API method and separately documents a role-based workflow that grants Subscriber plus Subscription Owner; it does not resolve whether `analyticshub.subscriptions.create` is an additional direct check for `SubscribeListing`.
- The generated audit page remains internally inconsistent for v1 `SubscribeListing`: its method detail labels the event Data Access, while the permission-type table and general rule place its `ADMIN_WRITE` permission in Admin Activity. With no mutation performed, the book retains the method-detail classification and the checklist keeps a live audit check open.
