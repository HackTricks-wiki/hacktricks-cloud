# Cloud DNS — open verification leads

## Open verification leads (2026-09-28)

- In a disposable VPC, capture the exact `protoPayload.methodName` emitted by each current gcloud wrapper (`record-sets create/update/delete`, `policies update`, `response-policies update`, and rule update) and confirm whether it uses the REST `patch`, `update`, or Changes surface documented in the audit catalog.
- Verify least-privilege custom roles independently for each network and GKE attachment gate, including cross-project consumer/producer networks for a peering zone. Official documentation is inconsistent about whether `dns.networks.bindPrivateDNSZone` is separately checked for every peering-zone consumer attachment.
- Measure query-log behavior for cached public and private responses and confirm the log-owning project for Shared VPC and cluster-scoped zones without changing production logging.
- Confirm whether the installed gcloud help omission for `dns policies update --no-enable-logging` is only a help-generation bug; the current official Cloud DNS monitoring guide documents the flag.
- Move the dangling Cloud DNS name-server-shard delegation hypothesis to the unauthenticated DNS research/page only after a disposable-domain test confirms authoritative takeover and cleanup behavior. Do not represent it as project post-exploitation.
- If a dedicated Cloud DNS privilege-escalation page is added, move the `dns.managedZones.setIamPolicy` policy-preserving self-grant analysis there and revalidate current predefined-role holders against the IAM role catalog.

## Cross-review confirmations (2026-09-28)

- [x] Replaced the disputed private query-logging disable CLI flag with the current `policies.patch` REST surface.
- [x] Added exact Cloud Logging `ListLogEntries` audit visibility for DNS-query surveillance.
- [x] Reconciled `dns.managedZones.setIamPolicy` holders with the current IAM role catalog.
