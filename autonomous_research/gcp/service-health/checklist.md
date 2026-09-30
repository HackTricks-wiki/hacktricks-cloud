# Personalized Service Health research checklist

- [x] Inventory unauthenticated MCP schemas and annotations.
- [x] Validate direct and MCP list with only `servicehealth.events.list`.
- [x] Confirm `EVENT_VIEW_FULL` returns update history under list-only authority.
- [x] Confirm direct and MCP get remain gated by `servicehealth.events.get`.
- [x] Validate the outer `mcp.tools.call` gate and anonymous boundary.
- [x] Reconcile direct/MCP logging with the official audit matrices.
- [x] Add one bounded post-exploitation technique with impact, scope, stealth and logs.
- [x] Remove all disposable IAM, credentials, configuration, local artifacts and API enablement.
- [ ] In an owned organization fixture, compare project events with organization events/impacts and
      test whether relevance leaks any child project outside the caller's authorized scope.
- [ ] Recheck the MCP setup guide; remove the documented-permission discrepancy note if Google adds
      the underlying Service Health permissions.
