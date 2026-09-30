# Database Insights research checklist

- [x] Inventory the unauthenticated MCP tool schemas and annotations.
- [x] Map every tool to its service-specific permission and product prerequisite.
- [x] Validate `queryMetrics:fetch` with the narrow Database Insights and Monitoring permissions.
- [x] Validate a harmless direct/MCP positive control without creating a database fixture.
- [x] Check anonymous invocation and an ungranted-tool negative control.
- [x] Reconcile default live visibility with the current audit-service and MCP logging catalogs.
- [x] Add one bounded post-exploitation technique with impact, minimum permissions, stealth and a
      per-technique log table.
- [x] Remove every disposable identity, binding, credential, role, configuration and local artifact,
      and return the API to its disabled baseline.
- [ ] In a pre-existing disposable Cloud SQL/AlloyDB fixture, capture representative normalized SQL,
      tag/IP dimensions, advanced wait/query statistics and index recommendations. Do not provision
      a database solely for this read-path test.
- [ ] Measure cross-project `parent` versus PromQL `resource` authorization and regional behavior
      only with two owned projects and synthetic telemetry.
- [ ] Recheck the audit-service catalog as the Preview API matures and replace the current
      undocumented direct-read wording if Google publishes a Database Insights audit matrix.
