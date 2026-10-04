# Unified Maintenance research checklist

- [x] Inventory unauthenticated MCP schemas and annotations.
- [x] Map list/get/summary to exact underlying permissions.
- [x] Validate direct and MCP list with only `maintenance.resourceMaintenances.list`.
- [x] Confirm get remains independently gated by `maintenance.resourceMaintenances.get`.
- [x] Validate the outer MCP gate and anonymous boundary.
- [x] Reconcile default visibility with the Unified Maintenance and MCP audit matrices.
- [x] Add one bounded post-exploitation technique with impact, scope, stealth and logs.
- [x] Remove all disposable IAM, credentials, configuration, local artifacts and API enablement.
- [ ] In a project with pre-existing synthetic maintenance records, capture representative resource,
      label/annotation, timing, state and control output without creating infrastructure solely for
      the read-path test.
- [ ] Test pagination, filters, summaries, regional versus `-` scope and unreachable locations with
      pre-existing disposable resources.
