# Google Cloud Observability security research ledger

## 2026-09-29 — Error Reporting remote MCP and stack-trace harvesting

- Mapped the new global `https://clouderrorreporting.googleapis.com/mcp` endpoint. It exposes one
  read-only tool, `list_group_stats`, backed by `errorreporting.groups.list`. Its result includes
  group status/counts, affected services/users, time bounds and a representative event with the
  error message, stack trace and request/source context; individual sampled events remain available
  only through the direct `projects.events.list` API.
- An isolated caller with only `errorreporting.groups.list`, project read and quota-use permission
  returned the same existing representative group through direct REST but was denied by MCP on
  `mcp.googleapis.com/tools.call`. An unconditional `roles/mcp.toolUser` grant enabled the MCP call,
  while an anonymous tool call returned HTTP 401. This confirms the documented two-layer boundary;
  no authorization bypass or unexpected vulnerability was found.
- Tool-name-only and service-plus-tool conditional grants did not authorize during a bounded
  propagation window, while the unconditional grant worked quickly. This was fail-closed and had
  no security impact. Re-test before claiming that Error Reporting currently honors the documented
  MCP allow-policy attributes; the one-tool server does not need that condition for tool separation.
- Confirmed the visibility boundary: `ListGroupStats` and `ListEvents` are `DATA_READ` Data Access
  methods disabled by default, and the service-specific MCP wrapper is also off-default Data Access
  enabled through the `mcp.googleapis.com` audit configuration. No principal-attributed entry was
  present under the project's default settings.
- No error was injected, updated or deleted. Removed the disposable key, identity, both IAM grants,
  custom role and gcloud configuration, disabled Error Reporting back to its pre-test baseline, and
  verified zero active identity, binding, configuration, enabled API or local-artifact residue. The
  custom role remains only in Google's normal soft-deleted state.

## 2026-09-29 — new v1 storage, scope and BigQuery-link surface

- Reviewed public Observability v1 discovery revision `20260917`, Google Cloud SDK 586.0.0,
  current official storage/scope/query/access/audit documentation, and all seven predefined
  `roles/observability.*` roles. This is a separate API (`observability.googleapis.com`) from Cloud
  Logging's `logging.links.*` surface.
- Mapped buckets, datasets, views, links, analytics views, trace scopes, the project `_Default`
  observability scope and project/folder/organization default settings. Cloud Trace uses the
  system-managed `_Trace/Spans/_AllSpans` path. Each dataset supports at most one link, which creates
  a read-only linked BigQuery dataset in the same project.
- Retained two high-value expected post-exploitation paths. First, Trace/Observability view readers
  can mine span attributes and events for URLs, tokens, SQL, GenAI inputs/outputs, user data and
  internal topology. Second, `observability.links.create` expands an existing trace dataset to the
  BigQuery permission plane. Observability Editor contains link create but not
  `observability.views.access`; a principal with separate BigQuery Data Viewer and query-job
  authority can therefore create and query the bridge without View Accessor.
- Bounded the link technique to a same-project linked dataset, an existing `_Trace/Spans` dataset,
  no pre-existing link, BigQuery data read plus query-job permissions, billing/APIs and functional
  service agents. There is no destination-project parameter and no claim of direct cross-project
  exfiltration.
- Audit visibility is asymmetric. `CreateLink`/`DeleteLink` are always-on Admin Activity LROs and
  BigQuery queries are audited by default. Legacy `GetTrace`/`ListTraces` and Observability inventory
  are Data Access reads, off by default. The current Observability audit catalog lists no Analytics
  query-execution method, so runtime query attribution remains explicitly unverified.
- Trace/log scopes are read-time aggregators, not data grants. Official semantics say Trace and
  Logging recheck source-resource IAM; only Monitoring Metrics Scopes authorize reads at the
  scoping project. Scope updates were therefore not promoted as cross-project bypasses.
- The permission catalog contains bucket/dataset/view delete/undelete permissions ahead of the
  public callable surface. Current v1 discovery and CLI have no bucket/dataset/view delete methods,
  and official docs say those system-managed resources cannot be lifecycle-managed by customers.
  No destructive or speculative technique was published from permission names alone.
- Performed a bounded eligibility/inventory probe. `observability.googleapis.com` was disabled at
  baseline; exact enablement succeeded even though the normal available-services query did not
  return it. Enumerated all 46 supported locations with `showDeleted=true`: no bucket, dataset,
  view or link existed. Creating `_Trace` was intentionally skipped because current API/docs offer
  no clean bucket deletion path. Removed the auto-created Observability service-agent binding and
  account, disabled the API, deleted local discovery responses, and verified zero residue.

## Rejected or deferred claims

- Do not call a trace scope an authorization bypass; source-project view access is rechecked.
- Do not claim Link creation alone reads trace data. The caller still needs BigQuery Data Viewer on
  the project/linked dataset and query-job permission.
- Do not claim a cross-project link destination. The linked dataset is created in the source
  project and the request has no destination-project field.
- Do not claim Analytics queries are impossible to audit. The current control-plane catalog omits a
  query method, but runtime behavior needs a prepared trace fixture.
- Do not create a synthetic observability bucket in this lab until a supported immediate-delete
  path exists; current cleanup guarantees are insufficient.
