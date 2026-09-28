# Integration Connectors — checked

## 2026-09-26 — service-enumeration coverage

- Added a service-enumeration page covering cross-region connection discovery, `FULL` connection
  configuration, resource IAM, action/entity schemas, event subscriptions, per-user authentication,
  endpoint attachments, managed zones, custom connectors and provider versions.
- Confirmed from the current REST discovery documents that the v1 control-plane and v2 runtime
  endpoints are present. Confirmed locally that the installed Google Cloud CLI has no stable
  `gcloud connectors` command group, so the page uses REST examples.
- Sent read-only list requests to the authorized lab project. The Connectors API is disabled and all
  calls returned `SERVICE_DISABLED`; it was not enabled and no connection or other resource was
  created. The request paths are documentation/discovery-validated.
- Reconciled enumeration visibility with Google's current audit-method table: location list is not
  logged; administrative reads are Data Access and disabled by default; `ListenEvent` has no audit
  log; mutable control-plane operations are Admin Activity.

## Current lab constraint

Do not create a billable connection only to test enumeration. Re-run the minimum-permission and
exact response-field checks when an existing disposable connection is available, then delete any
purpose-built connection and wait for the delete operation to finish.

## 2026-09-28 — CVE-2026-4644 current-state correction

- Google's GCP-2026-059 bulletin states that unauthorized service-account attachment in the HTTP
  Connector affected versions before December 11, 2025 and was patched on that date. Removed the
  stale public claims that current `connectors.connections.create`/`update` provides an
  `actAs`-free service-account escalation path.
- Retained CVE-2026-4644 as a fixed entry on the historical-vulnerabilities page and as an explicit
  warning on the current privilege-escalation page, not as a live technique. The supported current
  primitives remain use of an existing connection by an authorized Invoker/Listener and
  connection-level `setIamPolicy` self-grant. Reclassified the former into a dedicated
  post-exploitation page because it exposes or changes backend data but does not itself increase
  GCP IAM; retained only the IAM self-grant as a current privilege-escalation technique.
- Corrected action/entity telemetry from "no Cloud Audit event" to Data Access, disabled by
  default; retained Google's explicit no-audit exception for `ListenEvent`. The current audit
  catalog does not list `ExecuteSqlQuery`, so its Cloud Audit visibility remains unknown pending a
  disposable-connection capture.
- This correction used first-party documentation only and created no cloud resource.
- Independent review against the v2 discovery document corrected the SQL request from the
  nonexistent `connectionSchemaMetadata:executeSqlQuery` route to
  `connections/{connection}:executeSqlQuery`. The audit catalog updated September 24, 2026 still
  neither lists this method nor places it in the explicit no-audit list, so visibility remains
  unknown rather than "not logged." Exact documented runtime audit method names and a single
  categorical Medium stealth rating were added to the post-exploitation technique.
