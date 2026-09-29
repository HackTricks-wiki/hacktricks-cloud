# Cloud Quotas — tested

## 2026-09-29 — five-tool MCP surface and capacity reconnaissance

- The unauthenticated live `https://cloudquotas.googleapis.com/mcp` schema exposed five tools:
  quota-info list, quota-preference list, adjuster-settings get/update and quota-increase request.
  Anonymous invocation returned HTTP 401.
- A disposable principal with Cloud Quotas Viewer and quota-project consumption authority listed
  project quota preferences and a bounded page of Compute Engine quota information directly. The
  result exposed exact quota IDs/metrics, values, regions, dimensions and increase eligibility.
- The same caller was rejected by the MCP wrapper without `mcp.tools.call`, then returned the same
  bounded quota-info result after MCP Tool User was added. The quota-project header was material:
  omitting `x-goog-user-project` produced misleading permission/service-consumer failures even
  though IAM analysis resolved the target grant.
- Cloud Quotas Data Access reads and the MCP wrapper produced no default caller log. Write attempts
  and denials used always-on `google.api.cloudquotas.v1.CloudQuotas.UpdateQuotaPreference` Admin
  Activity with the exact `cloudquotas.quotas.update` decision.
- The initial read found no pre-existing quota preferences. Quota-adjuster settings were unavailable to
  both Viewer and Owner behind the same Support/Sales feature gate, so no adjuster behavior is
  inferred from this environment.
- Removed every disposable role binding, key, service account and isolated gcloud configuration;
  restored the Cloud Quotas API to its disabled baseline. Independently verified the tested
  `us-central1` A2 CPU limit and zero usage at the original value 12 after cleanup.
