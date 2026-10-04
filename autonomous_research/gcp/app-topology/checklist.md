# App Topology — open leads

- [x] Map GA domains, schema, graph-query syntax, role exposure, MCP tools and wrapper authorization.
- [x] Correct the live `GraphPattern` nesting and reject the stale flat CLI example.
- [ ] In a disposable project with actual App Hub, telemetry, IAM-key, vulnerability and agent
      relationships, capture representative `IAM/IMPERSONATES`, `SENDS_TRAFFIC`, vulnerability and
      agent-to-MCP graph output. Do not add resources solely to populate topology.
- [ ] With direct App Topology Data Access logging explicitly enabled in a disposable project,
      capture exact `ListDomains`, `GetSchema` and `GenerateDiscoveredResourcesTopology` audit method
      names. Restore the original audit configuration.
- [ ] Test folder/application-boundary graph scope only in an owned multi-project fixture. Treat any
      cross-boundary node/edge disclosure beyond the caller's underlying visibility as private-first.
