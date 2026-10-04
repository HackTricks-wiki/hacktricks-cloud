# Cloud Domains research log

## 2026-09-28 — official-contract audit

Scope was documentation, local Google Cloud CLI help, and public API/audit contracts only. No Cloud Domains API was called and no registration, IAM policy, or other cloud resource was changed.

### Retained or reclassified

- Retained authoritative-name-server replacement as post-exploitation. The exact minimum write permission is `domains.registrations.configureDns`; `ConfigureDnsSettings` is an Admin Activity LRO. The impact is bounded by DNSSEC, caches, reachability, and higher-layer authentication.
- Retained authorization-code disclosure/transfer as post-exploitation. Contrary to the old page, `RetrieveAuthorizationCode` is `ADMIN_WRITE` Admin Activity, is not an LRO, and requires `domains.registrations.configureManagement`. Unlock uses `ConfigureManagementSettings` (LRO), while push transfer uses `InitiatePushTransfer` (LRO). Authorization-code retrieval has a 60-day-after-registration gate.
- Retained contact privacy/contact replacement with bounded impact. `domains.registrations.configureContact` is the exact permission; `ConfigureContactSettings` is an Admin Activity LRO. Some contact changes require email confirmation and privacy changes can expose the previously effective contacts before replacement contacts publish.
- Moved `list`/`get` to a dedicated enum page. `GetRegistration` and `ListRegistrations` are `ADMIN_READ` Data Access and off by default.
- Moved registration `SetIamPolicy` to service-level persistence. `SetIamPolicy` is Admin Activity; `GetIamPolicy` is Data Access. The example requests policy version 3 and preserves the policy `etag` and conditions.

### Rejected or folded

- Rejected deletion/expiry/renewal-disable headings: they are destructive or availability-only and do not meet the post-exploitation sensitive-data/foothold bar.
- Rejected deprecated Google Domains export/import flows as current attack primitives. Current transfer-out behavior is covered through the authorization-code and supported push-transfer paths.
- Rejected an unauthenticated Cloud Domains page: registration control-plane operations require authenticated IAM authorization; public DNS/RDAP information is not a Cloud Domains authorization bypass.
- Did not claim an authorization code alone transfers a domain. Eligibility, lock state, receiving registrar, TLD/registry rules, and sometimes confirmation remain necessary.

### Primary evidence used

- Cloud Domains audit logging catalog and v1 REST reference.
- Current Cloud Domains role catalog.
- Current transfer-out, authorization-code, registration-settings, feature-deprecation, and Google Cloud CLI reference/help pages.

### Live-test status

Not tested live: the authorized project had no disposable domain in scope, and registration/transfer testing has external ownership, cost, and cleanup implications. All conclusions above are official-contract findings.

### Independent reciprocal review

- Corrected the enum field list: current `Registration` responses expose DNS/contact/management, supported-privacy, lifecycle, label and failure fields, but not `domainProperties` or a registrar field. Those properties belong to separate registration/transfer-parameter responses.
- Confirmed command syntax, permission boundaries, LRO classifications and policy-preserving IAM merge behavior; linked every telemetry/default-visibility statement to the audit catalog.
