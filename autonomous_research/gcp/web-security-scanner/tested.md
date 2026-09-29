# Web Security Scanner research ledger

## 2026-09-28 — post-exploitation documentation audit

This pass used current official Web Security Scanner overview, custom-scan, REST schema, IAM and audit references. The API remained untouched: no scan, run, finding, app request, SCC setting, IAM policy or other cloud state was created, changed or deleted.

### Retained techniques

1. **Active project-app reconnaissance.** Create and run a custom scan, then read findings and crawled URLs. Impact is bounded to an eligible project-associated public target and configured application identity. The scan can change application data and is always noisy at both control and data planes.
2. **Passive stored-intelligence read.** Read existing scan configuration, findings and paths. A custom configuration can disclose its username and login URL, but password fields are explicitly input-only, encrypted and excluded from responses/audit logs.

### Corrections and removals

- Replaced reasoned telemetry with the current official method catalog. Create/start/update/delete/ stop are non-LRO `ADMIN_WRITE` Admin Activity. Scan/config get/list methods are `ADMIN_READ` Data Access; finding/path reads are `DATA_READ`; all reads are disabled by default.
- Added separate discovery permissions for unknown config/run IDs and active-scan polling.
- Added Security Command Center/service enablement, target ownership/static-IP validation, application authentication and potentially destructive crawler behavior as prerequisites.
- Removed scan deletion, schedule weakening and run stopping as destructive defense evasion/DoS, not sensitive-information post-exploitation.
- Reconfirmed there is no arbitrary-target SSRF path and no stored password read primitive.

## 2026-09-28 — reciprocal review

- Revalidated create/start/result method permissions, exact v1 method names, non-LRO boundaries, and Admin Activity versus disabled-by-default Data Access classifications against the current audit catalog and discovery schema.
- Corrected the generic REST example to send `targetPlatforms`. The raw API defaults an omitted field to `APP_ENGINE`; an eligible Compute, Cloud Run, or Cloud Run functions target must select its matching enum. The JSON body now uses `jq` rather than interpolating an unescaped URL.
- Reconfirmed project-target validation, public IPv4 and SCC prerequisites, active crawler side effects, input-only password behavior, and the passive-read impact boundary. No scan or other cloud state was created or changed.
