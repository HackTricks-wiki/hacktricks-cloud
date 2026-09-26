# Datastream — checked

## 2026-09-26 — service enumeration and BigQuery-source correction

- Added `gcp-datastream-enum.md` covering regional/static-IP discovery, connection profiles,
  streams/objects/backfills, private connections/routes and audit visibility.
- The API is already enabled in the authorized lab. Read-only list operations in `us-central1` and
  `europe-west1` returned no profiles, streams or private connections; the documented
  `locations fetch-static-ips` command returned the current `us-central1` service IPs. No resource
  was created and no teardown was required.
- Rechecked the current v1 discovery schema, official source list and stable CLI. BigQuery is only a
  destination: `SourceConfig` has no `bigquerySourceConfig`, and `streams create` has no
  `--bigquery-source-config`. Corrected the prior zero-credential "Spanner / BigQuery sources"
  technique to Spanner only across privesc and persistence.
- Tightened the general confused-deputy prerequisite: a conventional source requires an existing
  stored profile or a valid credential plus network reach. The caller does not recover that stored
  secret; Spanner is the credential-free native exception.
- Added explicit stealth ratings to all four retained Datastream attack sections.
