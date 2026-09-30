# Service Usage privilege-escalation audit

## 2026-09-28 - documentation and read-only role audit

No project, service, quota, API key, IAM policy, or organization policy was changed. The review used current official Service Usage, Cloud Quotas, API Keys, IAM role, and Cloud Audit Logs documentation, local read-only role inspection, and three authenticated read-only policy GETs.

### Result

No direct Service Usage privilege-escalation primitive remains. The five former headings were removed or redirected because they represented credential handling in another service, an enabling prerequisite, quota/billing consumption, defense evasion, or denial of service rather than an increase in the caller's authorization.

### Corrections

- `serviceusage.services.enable` enables a service but does not grant that service's permissions. It remains a supporting prerequisite where a separate attack requires a disabled API.
- `serviceusage.services.use` authorizes consumption of a project's quota and billing. It does not authenticate the caller as that project or bypass the called service's IAM checks.
- `serviceusage.services.disable` and quota-override writes can be damaging, but are availability, cost, or defense-evasion operations rather than privilege escalation.
- Preview `serviceusage.consumerpolicy.update` enables services through inherited hierarchy rules; the default gcloud update helper also calls Analyze and needs `serviceusage.consumerpolicy.analyze`, while `--bypass-dependency-check` skips that call. The raw update permission remains `.update`. Neither path grants data-plane permissions. The older MCP enablement policy was an additional server-enablement gate, but never supplied an underlying API permission; it is now deprecated.
- The v2beta discovery schema still exposes `contentSecurityPolicies.patch` and names Model Armor as its provider, but an authorized `contentSecurityPolicies/default` GET now returns HTTP 400, `FAILED_PRECONDITION`, reason `SU_MCP_DEPRECATED`, and explicitly says the policy has no effect. The MCP policy GET returns the same result. Neither stale discovery surface was promoted.
- Standard API keys do not authenticate an IAM principal. API key creation/exfiltration/restriction changes already have a dedicated API Keys page and should not be duplicated under Service Usage.
- Authorization keys do act as a bound service account, but current documentation requires the API key roles plus Service Account User, Service Account API Key Binding Admin, and an organization- policy state under `constraints/iam.managed.disableServiceAccountApiKeyCreation` that allows the target service (with the documented Gemini API default exception). Projects without an organization are unsupported. This is an API Keys/IAM attachment primitive, not a consequence of `serviceusage.services.enable` or `serviceusage.services.use` alone.

### Telemetry boundaries

- `EnableService` and `DisableService` are Admin Activity long-running operations and normally produce start and completion records.
- Service Usage consumer-override mutations are Admin Activity LROs.
- Cloud Quotas `CreateQuotaPreference` and `UpdateQuotaPreference` writes are always-on Admin Activity but are not LROs; they must not inherit the legacy Service Usage override classification.
- `UpdateConsumerPolicy`, `UpdateContentSecurityPolicy`, and the deprecated `UpdateMcpPolicy` are also documented as always-on Admin Activity LROs.
- `AnalyzeConsumerPolicy`, `GetConsumerPolicy`, `GetContentSecurityPolicy`, and `GetMcpPolicy` are explicitly listed as methods that don't produce audit logs. `GetOperation` polling is itself classified as Admin Activity by the current Service Usage catalog.
- The current API Keys audit catalog classifies `CreateKey` as Admin Activity and `GetKeyString` as `ADMIN_READ` Data Access. The old page's generic `DATA_READ` label for `GetKeyString` was stale.

### Read-only policy probe

- `GET v2beta/projects/gcp-labs-eqd4ny8d/contentSecurityPolicies/default`: HTTP 400, `SU_MCP_DEPRECATED`; no state change.
- `GET v2beta/projects/gcp-labs-eqd4ny8d/mcpPolicies/default`: HTTP 400, `SU_MCP_DEPRECATED`; no state change.
- `GET v2beta/projects/gcp-labs-eqd4ny8d/consumerPolicies/default`: HTTP 200 and returned the current hierarchical service-enable policy; no state change.

No response contained a credential or customer data, and no temporary asset or cleanup action was needed.

## 2026-09-28 - independent cross-review

The independent pass rechecked current official Service Usage, Cloud Quotas, API Keys, quota-project, hierarchical activation, deprecation, and audit documentation; local role/help metadata; the public v2beta discovery document; and the same three authenticated read-only GETs. It made no mutation.

- Confirmed that API enable/disable, quota-project use, both quota-management families, and consumer policy updates can alter availability, billing, quota, or prerequisites but cannot grant the caller an enabled service's IAM permissions. No direct privilege-escalation H3 should be restored.
- Added the private-service `servicemanagement.services.bind` boundary for service enablement.
- Split the raw consumer-policy update minimum (`serviceusage.consumerpolicy.update`) from the default gcloud helper, which also calls Analyze and needs `.analyze` unless `--bypass-dependency-check` is used. The analysis and policy GET methods produce no audit logs, while the update is an Admin Activity LRO.
- Split legacy Service Usage quota overrides (Admin Activity LROs) from current Cloud Quotas preference writes (Admin Activity, not LRO).
- Corrected the historical MCP wording: the deprecated policy was an extra server-enablement gate, not a source of a tool's underlying IAM permission.
- Reconfirmed authorization-key role and exact organization-policy boundaries, including the organization requirement and Gemini API default exception.
- Independently reproduced HTTP 400 `FAILED_PRECONDITION` with ErrorInfo reason `SU_MCP_DEPRECATED` and the explicit "deprecated and has no effect" message for content-security and MCP policy GETs. Consumer-policy GET remained HTTP 200 and returned the one current policy; only its name and enable-rule count were inspected, not policy contents.

### Role inspection

The current role index confirms that `roles/serviceusage.serviceUsageAdmin` includes enable, disable, quota/billing consumption and quota-policy administration, but none of those permissions grants a target service's data-plane authorization. API-key and service-account binding permissions are separately named and documented.
