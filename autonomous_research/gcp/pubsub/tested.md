# Pub/Sub privilege escalation — documentation-audited findings

## 2026-09-28 — full page audit

This pass used current official Google Cloud documentation and local Google Cloud CLI help only. No Pub/Sub, IAM, Logging, BigQuery, Cloud Storage, or other cloud resource was read or changed.

### Retained high-value escalation primitives

1. **Topic/subscription `SetIamPolicy` self-grant.** A principal with the resource's `setIamPolicy` permission can grant a controlled identity any Pub/Sub role applicable to that same resource. The page now distinguishes a blind policy write from the safe gcloud read-modify-write, which additionally requires `getIamPolicy`, and bounds the result to the policy-bearing topic or subscription.
2. **Authenticated-push OIDC token oracle.** `CreateSubscription`, `UpdateSubscription`, or `ModifyPushConfig` requires `iam.serviceAccounts.actAs` when a push-auth service account is selected. If the subscription project's Pub/Sub service agent already has `iam.serviceAccounts.getOpenIdToken` on that service account, Pub/Sub sends a Google-signed identity token to the configured public HTTPS receiver. An audience override can identify a different relying service, but the token is not an OAuth access token and cannot call arbitrary Google APIs.
3. **Export write through a more privileged identity.** A BigQuery or Cloud Storage export subscription writes as the default Pub/Sub service agent or as a selected user-managed service account. The default branch requires no caller `actAs`; the custom branch requires caller `actAs` and Pub/Sub service-agent `getAccessToken`. This is a destination-bounded write primitive, not portable service-account impersonation.

### Exact permission and prerequisite corrections

- New subscription creation requires `pubsub.subscriptions.create` on the subscription project and `pubsub.topics.attachSubscription` on the source topic. Cross-project attachment therefore evaluates permissions on two resources.
- Direct push modification and subscription patch both require `pubsub.subscriptions.update` on the subscription. No `pubsub.subscriptions.get` permission is part of the direct API minimum.
- Authenticated push additionally requires caller `iam.serviceAccounts.actAs`, a selected user-managed service account in the same project as the subscription, and pre-existing Pub/Sub service-agent `iam.serviceAccounts.getOpenIdToken` on that account.
- BigQuery delivery needs `bigquery.tables.get` and `bigquery.tables.updateData` on the existing compatible destination table.
- Google's documented Cloud Storage delivery role combination is `roles/storage.objectCreator` and `roles/storage.legacyBucketReader` on the destination, and the bucket must exist with Requester Pays disabled.
- A custom export account additionally requires caller `iam.serviceAccounts.actAs`, Pub/Sub service-agent `iam.serviceAccounts.getAccessToken`, and the destination permissions on that custom account.
- `pubsub.topics.publish` is needed only to force delivery or inject attacker-chosen content; naturally arriving topic traffic can exercise push/export delivery without it.

### Telemetry corrections

- `google.iam.v1.IAMPolicy.SetIamPolicy`, `google.pubsub.v1.Subscriber.CreateSubscription`, `google.pubsub.v1.Subscriber.UpdateSubscription`, and `google.pubsub.v1.Subscriber.ModifyPushConfig` are Admin Activity and always logged.
- The official catalog also retains legacy `tech.pubsub.SubscriberService.CreateSubscription` and `tech.pubsub.SubscriberService.ModifyPushConfig` method names for detection coverage.
- `GetIamPolicy` is Data Access `ADMIN_READ` and off under the default Pub/Sub audit configuration.
- Pub/Sub explicitly excludes message operations including `Publish`, `Pull`, `StreamingPull`, `Acknowledge`, and `ModifyAckDeadline` from Cloud Audit Logs.
- The official authenticated-push contract does not promise a separate Service Account Credentials `GenerateIdToken` entry for Pub/Sub's internal signer. The page no longer invents one.
- Cloud Storage object creation is Data Access `DATA_WRITE`, disabled by default. BigQuery Storage API `AppendRows` is a BigQuery Data Access method; BigQuery Data Access is enabled by default. Storage Write API appends do not produce `BigQueryAuditMetadata.TableDataChange`, so detection must not depend only on that metadata event.
- Removed the prior unqualified claim that subscription creation always creates two audit entries. The official audit contract guarantees `CreateSubscription` with both create and attach permissions; cross-project activity can be logged in the topic project, but entry cardinality is not a stable published guarantee.
- Removed empirical claims that every request body is complete. Audit request fields can be useful, but the current product contract does not promise that all subscription configuration fields are always present and unredacted.

### Folded or rejected as non-privesc

- `pubsub.subscriptions.consume`: direct data access and possible destructive acknowledgement; post-exploitation.
- `Seek` to a timestamp or snapshot: replay or purge of an already controlled subscription; data access/availability rather than a new authorization boundary. `Seek` is auditable as Data Access `ADMIN_READ`, off by default.
- `pubsub.snapshots.create`: freezes/replays accessible backlog but needs consume on the source subscription; useful post-exploitation, not privilege escalation.
- Snapshot/schema `SetIamPolicy`: valid resource-local APIs, but low-value standalone grants that do not remove independent consume/create permissions. Folded into the general resource-scope explanation rather than retained as headings.
- New unauthenticated push/export subscription used only to copy topic messages: high-value exfiltration but post-exploitation unless it uses a more privileged destination identity.
- Existing unauthenticated push redirect: exfiltration and outage, not privilege escalation.
- Dead-letter redirection, retention reduction, detachment, expiration manipulation, and deletes: persistence, data loss, or availability actions.
- Speculative SSRF against RFC1918, metadata, or internal HTTPS names: the official push contract requires a publicly accessible HTTPS endpoint with a CA-signed certificate. A VPC-SC perimeter further limits new push endpoints and prohibits updating existing push subscriptions. Mere configuration acceptance is not evidence of backend reachability.
- Generic “publish triggers privileged application” chains: application-specific business-logic abuse, not a platform-level Pub/Sub privilege-escalation primitive without a concrete vulnerable consumer contract.

### Material impact bounds

- Topic/subscription IAM grants do not create project-level permissions or affect unrelated Pub/Sub resources.
- Captured push credentials are audience-bound OIDC identity tokens, not access tokens.
- Export delivery emits only messages present on the selected topic and is constrained by destination schema, IAM, retention, and organization controls. It does not reveal a portable token.
- Destination logs correctly attribute writes to the configured delivery identity; they do not inherently identify the human or workload that configured the subscription, so defenders should correlate them with the always-on subscription control-plane event.

## 2026-09-28 — independent cross-review

An independent official-documentation and local-CLI review confirmed all three retained primitives
and made two final bounds explicit:

- The authenticated-push path correctly requires subscription create or update, caller
  `iam.serviceAccounts.actAs`, a user-managed service account in the subscription project, and
  Pub/Sub service-agent `iam.serviceAccounts.getOpenIdToken`. The audience is attacker-selectable
  but the resulting credential remains an audience-bound OIDC identity token. Under VPC Service
  Controls, a new push endpoint is limited to a Cloud Run default `run.app` URL; a Workflows target
  is allowed only through Eventarc and its push-auth service account must be included in the
  perimeter, the topic/subscription perimeter boundary must be allowed, and an existing push
  subscription cannot be updated. The page now states that these constraints
  normally block the public capture endpoint used by the technique.
- The export REST schemas make caller `actAs` conditional on setting `serviceAccountEmail` and do
  not currently document the authenticated-push same-project rule for custom export identities.
  The book example therefore uses a same-project custom account and does not claim cross-project
  custom-account support. Cross-project destination buckets and tables remain supported when the
  selected delivery identity has the documented destination permissions.

The review also reconfirmed that `ModifyPushConfig` and patch both require only
`pubsub.subscriptions.update` at the Pub/Sub resource layer; creation requires
`pubsub.subscriptions.create` on the subscription project plus
`pubsub.topics.attachSubscription` on the topic; the current gcloud flags in all examples are GA;
and the Pub/Sub audit catalog/default visibility and BigQuery/Cloud Storage downstream caveats are
accurate. No cloud resources, APIs, subscriptions, topics, service accounts, policies, or data were
read or changed.
