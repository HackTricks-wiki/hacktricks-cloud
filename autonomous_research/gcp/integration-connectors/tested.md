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
