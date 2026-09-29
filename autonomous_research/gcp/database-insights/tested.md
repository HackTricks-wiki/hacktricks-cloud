# Database Insights security research

## 2026-09-29 — telemetry reconnaissance and remote MCP surface

- Mapped the seven read-only tools at `https://databaseinsights.googleapis.com/mcp`: standard query
  and system PromQL, four AlloyDB Advanced Query Insights statistics tools, and AlloyDB index
  recommendations. Unauthenticated `tools/list` returned the complete static schemas.
- Retained one post-exploitation technique because the surface exposes materially useful database
  and application intelligence: normalized SQL, users, client addresses, database/resource IDs,
  application tags/routes, execution and wait history, and exact index-advisor DDL with schema,
  table and column names. Literal SQL constants are normalized away, so the impact is bounded.
- Verified a harmless `queryMetrics:fetch` call with a deliberately nonexistent Cloud SQL instance
  selector. A minimum read identity required `databaseinsights.queryMetrics.fetch` plus
  `monitoring.timeSeries.list`; direct REST and authorized remote MCP both returned an empty object.
  Anonymous MCP invocation returned HTTP 401.
- Independently mapped the service-specific checks for the remaining tools:
  `databaseinsights.systemMetrics.fetch`, `queryStats.fetch`, `waitEventStats.fetch`,
  `queryTimeSeries.fetch`, `waitEventTimeSeries.fetch`, and `indexRecommendations.query`. Public
  guidance follows the documented MCP consumer-project requirement in addition to these underlying
  permissions.
- The current Google Cloud audit-service catalog does not list Database Insights. Default live
  validation produced no caller entry for the direct or wrapper reads. The book records direct
  visibility as undocumented, Cloud Monitoring reads as off-default Data Access, and the MCP
  wrapper as off-default Data Access enabled through `mcp.googleapis.com`.
- No database, instance, cluster, table, query, recommendation, metric or other data resource was
  created or changed. Deleted both disposable identities, keys, project bindings, gcloud
  configurations and local artifacts; soft-deleted the custom role; and restored the Database
  Insights API to its disabled baseline. Exact checks found no active principal, binding, config,
  API or local residue.
