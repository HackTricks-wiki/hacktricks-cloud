# Cloud Monitoring post-exploitation research

## 2026-09-28 — documentation audit

No live cloud resources were created or modified during this pass. Findings were reconciled against current Google Cloud REST, IAM, audit-logging, and gcloud documentation.

- Confirmed that Monitoring configuration reads generate `ADMIN_READ` Data Access logs when enabled; they are not inherently unlogged. `ListTimeSeries` is `DATA_READ` and `CreateTimeSeries` is `DATA_WRITE`. Those Data Access categories are disabled by default.
- Confirmed exact fully qualified audit method names for alert policies, dashboards, notification channels, metrics, SLOs, and uptime checks.
- Corrected `consumed_api.credential_id`: it represents a client credential such as an API-key ID or OAuth client ID, not a service-account email or an authenticated-principal identity.
- Corrected custom-metric injection: every time series needs a fully specified monitored resource and all metric/resource labels. Only user-defined metrics are writable.
- Corrected descriptor deletion: built-in metrics are not deletable; log-based metrics belong to Cloud Logging; stored time-series data becomes inaccessible and expires rather than being immediately erased.
- Corrected SLO deletion scope and removed the claim that `services.delete` permanently cascades through SLOs; service deletion is documented as a soft delete.
- Corrected uptime-check deletion: Google rejects deletion while an alerting policy references the check. The useful bounded primitive is weakening content, path, or accepted-status validation through update.
- Folded snooze creation/update, attacker-controlled policy/channel beacons, and recurring uptime callbacks into the existing Monitoring persistence page instead of duplicating them as post-exploitation techniques.
- Kept notification-channel abuse bounded to documented disable/delete behavior. Destination-label behavior and verification depend on channel type; a standard PATCH cannot set `verificationStatus`.

## 2026-09-28 — independent cross-review

No live cloud resources were created or modified. The retained eight techniques were checked again against the current Monitoring REST, IAM, audit-logging, Metrics Scope, and gcloud references.

- Corrected Data Access visibility wording: an audit configuration can be inherited from an organization or folder, not only enabled directly on the project.
- Distinguished raw partial PATCH minimums from the shown read-modify-write CLI helpers. The policy and channel helpers require the corresponding `.get`; the uptime helper always GETs and then sends a full replacement.
- Clarified that `metricDescriptors.list` returns descriptors defined or available to the named project, not proof that every returned metric is actively used. `activeOnly=true` is required to constrain descriptors to recent data.
- Clarified Metrics Scope authorization: cross-project list results are authorized on the named scoping project and only cover projects in that Metrics Scope.
- Added the documented active-billing, enabled-API, and timestamp-window prerequisites for user-defined time-series writes.
- Revalidated all eight categorical stealth ratings and every listed audit method/class against the current Cloud Monitoring audit-logging matrix; no rating or method-name change was required.
- Expanded every paired GET/LIST log-table entry to show both fully qualified audit method names instead of abbreviating the LIST namespace.
- Revalidated the retained command and REST examples locally without making API calls. No duplicate or low-value retained technique was found.
