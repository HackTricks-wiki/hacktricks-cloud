# Database Center research checklist

- [x] Inventory unauthenticated MCP schemas, annotations and the static-reference delta.
- [x] Map all six tools to the underlying Database Center permissions.
- [x] Validate `aggregateFleet` with a narrow custom role after removing the predefined viewer.
- [x] Validate detailed inventory and issue results against existing accessible resources only.
- [x] Test the independent `mcp.tools.call` gate and anonymous invocation.
- [x] Reconcile default live visibility with the audit-service and MCP logging catalogs.
- [x] Add one bounded post-exploitation technique with impact, scope, stealth and logs.
- [x] Remove every disposable identity, binding, credential, role, configuration and local artifact,
      and return the API to its disabled baseline.
- [ ] In an owned multi-project organization fixture, measure project/folder/organization parent
      filtering and partial-access behavior. Treat any inaccessible-resource disclosure as
      private-first.
- [ ] Capture representative normalized query statistics only when synthetic database traffic is
      already available; do not provision a database solely for the read-path test.
- [ ] Test tag/label filtering, baseline deltas, unreachable-region reporting and pagination using
      synthetic resources in an owned hierarchy.
- [ ] Recheck the audit-service catalog as the API matures and replace the undocumented direct-read
      wording if Google publishes a Database Center audit matrix.
