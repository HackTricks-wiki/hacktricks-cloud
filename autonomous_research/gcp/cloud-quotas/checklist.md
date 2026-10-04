# Cloud Quotas — open ideas

## Current public coverage

- [x] Map all five live MCP schemas and direct REST equivalents.
- [x] Verify the separate `mcp.tools.call` gate with a reduced Viewer caller.
- [x] Retain quota-info/preference/adjuster reconnaissance with exact impact and audit classes.
- [x] Keep quota and adjuster writes classified as capacity/availability effects rather than IAM
      privilege escalation.
- [x] Remove every disposable IAM, credential, configuration and API change and verify effective
      quota at baseline.

## Open bounded leads

- [ ] In an owned hierarchy with existing synthetic preferences, compare project, folder and
      organization partial visibility, inheritance, filters and service-project boundaries.
- [ ] Test quota-adjuster get/update only in an eligible disposable hierarchy. Preserve etags,
      change only a no-impact synthetic setting and restore exact inheritance immediately.
- [ ] Diff effective/default/future values and rollout metadata for existing synthetic quota
      transitions; do not request capacity solely to populate a fixture.
- [ ] Confirm Data Access method names and payload reduction with explicitly enabled logs, then
      remove the temporary audit configuration.
- [ ] Re-diff MCP schemas for delete/cancel support, newly exposed services, tool annotations and
      any permission split beyond the current coarse `cloudquotas.quotas.get/update` pair.
