# Google Cloud Observability security research checklist

## Completed — 2026-09-29

- [x] Map the stable v1 discovery resource graph, fields, methods and locations.
- [x] Map Observability, scope, analytics, view-access and service-agent predefined roles.
- [x] Separate direct view access, legacy Trace reads, trace scopes and BigQuery links.
- [x] Verify official audit classes for link/scope/resource reads and legacy Trace reads.
- [x] Establish the current system-managed bucket/dataset/view lifecycle limitation.
- [x] Perform a no-storage eligibility/inventory probe and restore API, service-agent, IAM and local
      state to the disabled/absent baseline.

## Safe live-validation frontier

- [ ] In a disposable project that already contains synthetic `_Trace/Spans` data, give an isolated
      caller only `observability.links.create`, BigQuery Data Viewer and query-job authority. Prove
      direct `observability.views.access` denial, create the link, query a non-secret marker through
      `_AllSpans`, then delete the link and verify the BigQuery dataset disappears.
- [ ] Capture the successful Link LRO request/completion, service-agent IAM changes and BigQuery
      `JobInsertion`/`TableDataRead` principals. Subtract CLI helper get/list/operation reads by
      repeating the create through raw REST.
- [ ] With an existing synthetic trace view, compare Observability Analytics and legacy
      `GetTrace`/`ListTraces` audit behavior under default and temporarily enabled Data Access.
      Restore the exact prior audit policy and do not record sensitive span values.
- [ ] Test conditional `roles/observability.viewAccessor` grants on one view and confirm that
      analytics views cannot widen access to another source view.
- [ ] Inspect analytics-view SQL returned by get/list for stored literals, source view names and
      detection logic. Publish only if it exposes consequential information beyond ordinary view
      metadata.
- [ ] Recheck the callable API when bucket/dataset/view delete/undelete methods reach public v1.
      Do not create storage merely to test permission names before immediate teardown is supported.
- [ ] Review the adjacent Telemetry API (`telemetry.consumers.*`, `telemetry.*.write`) for
      cross-project ingestion, consumer-IAM and spoofing boundaries using only synthetic spans.

## Do not publish without stronger evidence

- [ ] No trace-scope cross-project read without source authorization.
- [ ] No link-only data read without BigQuery data and job permissions.
- [ ] No arbitrary cross-project link destination under the current Link schema.
- [ ] No unverified claim that Observability Analytics queries are permanently unlogged.
