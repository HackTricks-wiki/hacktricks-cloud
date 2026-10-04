# Unified Maintenance security research

## 2026-09-29 — cross-service maintenance reconnaissance and remote MCP surface

- Mapped the three read-only tools at `https://maintenance.googleapis.com/mcp`: list, get and summary. Unauthenticated `tools/list` returned the schemas; anonymous invocation returned 401.
- Retained one post-exploitation technique because maintenance records can disclose full consumer resource names, types, locations, schedules, actual timing, state, labels/annotations and the available product-specific controls through one cross-service permission.
- A narrow custom caller with only `maintenance.resourceMaintenances.list`, quota/project context and `mcp.tools.call` succeeded through direct REST and MCP. The project had no current records, so response-shape impact remains source-grounded; no maintenance or product resource was created.
- The same settled caller was denied `maintenance.resourceMaintenances.get`, proving the list/get split. Returned control metadata does not authorize apply, policy management or rescheduling; those actions remain in producer APIs.
- Default audit settings produced no caller entry, consistent with documented off-default Data Access for the direct `ADMIN_READ` methods and MCP wrapper.
- Deleted the disposable identity, key, custom role, all bindings, local gcloud configuration and response artifacts; restored the Maintenance API to its disabled baseline. Exact residue checks found no active test principal, binding, config, API or local credential.
