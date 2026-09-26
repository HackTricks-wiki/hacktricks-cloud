# Cloud Workstations — tested and verified

Last checked: 2026-09-26

## Service enumeration surface — DOCUMENTED (read-only/docs-grounded)

- Confirmed from the installed stable CLI that cluster, configuration and workstation list commands
  can aggregate across all regions when parent flags are omitted.
- Confirmed the installed CLI exposes workstation `list-usable`, config/workstation describe and
  config/workstation `get-iam-policy`; clusters have no resource-level IAM command.
- Confirmed from the current v1 REST reference that configurations expose the runtime service
  account/scopes, image/container settings, host startup script and metadata, public-IP/SSH/TCP
  controls, network/resource tags, persistent storage, audit agent and creator policy-admin grant.
- Confirmed from the current audit table that ordinary list/get/getIamPolicy and
  `GenerateAccessToken` are Data Access (`ADMIN_READ`), mutations are always-on Admin Activity, and
  both `ListUsableWorkstationConfigs` and `ListUsableWorkstations` never produce audit logs.
- The authorized lab project `gcp-labs-eqd4ny8d` has `workstations.googleapis.com` disabled. Sent a
  read-only cluster list request, received `SERVICE_DISABLED`, and did not enable the API.
- No resource was created, changed or left behind; no teardown was necessary.

## Existing attack-page correction — SHIPPED

- Corrected the log description that conflated an unlogged IMDS token read with the audited
  `GenerateAccessToken` API. The latter is a Data Access event and is not logged by default.
- Added categorical stealth ratings to all three retained Cloud Workstations techniques.
