# Pub Sub — open ideas

Open ideas — Pub/Sub.

- [ ] **GCS import-topic persistence (UNVERIFIED).** Configure a topic's
  `ingestionDataSourceSettings.cloudStorage` (GCS import) via `topics.update` and verify whether it
  creates a durable ingestion pipeline that keeps pulling from an attacker-influenced GCS bucket after
  the attacker's project IAM is revoked. Confirm the ingestion SA identity + min-perm; ship only if it
  is genuinely a standing/persistence primitive distinct from the documented export-sink.
