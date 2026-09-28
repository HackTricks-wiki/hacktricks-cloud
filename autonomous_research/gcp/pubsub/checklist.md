# Pub/Sub privilege-escalation research checklist

## Completed documentation checks — 2026-09-28

- [x] Enumerate all original H3 claims and classify each as privilege escalation, post-exploitation, persistence, destructive availability, or unsupported speculation.
- [x] Verify topic, subscription, snapshot, and schema IAM permission/resource boundaries.
- [x] Verify exact create, patch, and `ModifyPushConfig` Pub/Sub permissions.
- [x] Verify authenticated-push same-project service account, `actAs`, service-agent `getOpenIdToken`, OIDC audience, public HTTPS receiver, and VPC-SC prerequisites.
- [x] Verify default and custom export identity branches for Cloud Storage and BigQuery.
- [x] Verify BigQuery destination minimum permissions and Cloud Storage documented destination roles/prerequisites.
- [x] Verify current Pub/Sub audit classes, modern and legacy method names, and explicitly unlogged message operations.
- [x] Verify destination-side Cloud Storage and BigQuery visibility/defaults.
- [x] Check local gcloud create/update/modify-push flags and use supported syntax.
- [x] Remove unsupported audit-entry cardinality, complete-request-body, internal-SSRF, and service-account-token-log guarantees.
- [x] Add explicit minimum permissions/prerequisites, bounded impact, categorical stealth, and expandable log table to every retained H3.

## Future safe validation leads

- [ ] With a dedicated no-cost test project, determine whether a custom BigQuery or Cloud Storage export service account can be cross-project from the subscription. The current REST contract does not state a same-project restriction; do not assert one without a current product result.
- [ ] Capture the exact Admin Activity request/response field shapes for create, patch, and `ModifyPushConfig` across REST and gcloud, treating results as dated observations rather than API guarantees.
- [ ] Confirm whether authenticated push performed by Pub/Sub's internal signer produces any IAM Credentials or service-agent delegation audit entry under explicitly enabled Data Access logging. The current official contract does not promise one.
- [ ] Confirm the precise BigQuery Storage Write audit entries and principal identity produced by a Pub/Sub BigQuery subscription. The official docs support `AppendRows` telemetry and explicitly exclude `TableDataChange` for Storage Write API appends, but do not document Pub/Sub-specific entry shape.
- [ ] Confirm Cloud Storage export's exact object-create method name and principal identity with Data Write logging enabled.
- [ ] Revisit Bigtable export subscriptions when stable gcloud and product documentation exposes their custom-identity setup and audit behavior; the REST resource contains `bigtableConfig`, but the current stable local create/update CLI does not expose it.

## Rejected unless new evidence changes the classification

- [ ] Do not restore pull, seek, snapshot replay, unauthenticated siphon, or redirect-only headings to the privilege-escalation page; place them in Pub/Sub post-exploitation if that page is audited.
- [ ] Do not claim internal-network SSRF from a stored `pushEndpoint` without successful delivery to a security-relevant internal target and a documented/verified reachability boundary.
- [ ] Do not claim that subscription creation always emits two audit entries or that its complete request body is guaranteed.
- [ ] Do not describe destination writes as anonymous or inherently attacker-attributed; they execute under the configured service identity.
- [ ] Do not describe authenticated-push tokens as Google API access tokens.
