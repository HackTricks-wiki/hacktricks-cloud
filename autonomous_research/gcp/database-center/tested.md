# Database Center security research

## 2026-09-29 — cross-product fleet reconnaissance and remote MCP surface

- Mapped the global REST API and six read-only tools at `https://databasecenter.googleapis.com/mcp`. Unauthenticated `tools/list` returned the complete live schemas, including `list_fleet_query_stats`, which was absent from the static MCP overview.
- Retained one post-exploitation technique because Database Center centralizes materially useful attack-path data across database products: exact resources, engines/versions/locations, sizing/maintenance/backup metadata, tags/labels, detailed security and resilience findings, and normalized query workload statistics.
- Verified `v1beta:aggregateFleet` with a disposable caller containing only `databasecenter.fleetStats.list`, `resourcemanager.projects.get` and `serviceusage.services.use`. After removing the broad predefined viewer role, it returned the same two-product aggregate as the privileged control. No database resource was created or changed.
- Used existing accessible resources only to validate detailed resource-group and issue output. Confirmed that the API returned concrete configuration, capacity, maintenance, protection and weakness signals. Kept those pre-existing resource identifiers and values out of the book.
- Verified that MCP invocation checks the separate `mcp.tools.call` gate before the underlying Database Center permission. Anonymous invocation was rejected. The public technique follows the documented two-layer permission model.
- The current Google Cloud audit-service catalog does not list Database Center. Default audit settings produced no test-caller entry for direct reads. The book records direct visibility as undocumented and the MCP wrapper as off-default Data Access configured through `mcp.googleapis.com`.
- Deleted the disposable identity, key, custom role, all bindings, local gcloud configuration and response artifacts; restored the Database Center API to its disabled baseline. Exact residue checks found no active test principal, binding, config, API or local credential.
