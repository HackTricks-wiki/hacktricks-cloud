# VPC Service Controls — tested

## 2026-09-28 — post-exploitation taxonomy and telemetry audit

Official documentation, public audit catalogs, local page comparison, and read-only CLI help only. No access policy, perimeter, access level, ingress/egress rule, dry-run configuration, IAM policy, project, or protected resource was created or changed.

No standalone VPC-SC post-exploitation technique remains after applying the no-garbage taxonomy:

- Access policy, access level, perimeter, `spec`/`status`, ingress/egress, `restrictedServices`, resources, and `vpcAccessibleServices` reads are enumeration and already belong on the enum page.
- Perimeter/access-level/bridge/ingress/egress/dry-run/enforcement/`vpcAccessibleServices` changes weaken an authorization or network boundary and belong on the Access Context Manager privilege-escalation page.
- Standing permissive context or ingress/egress rules are persistence and already belong on the persistence page.
- Actual data access through a pre-existing allowed route is a Storage, BigQuery, KMS, or other protected-service technique. VPC-SC checks the call but does not grant the underlying data permission.
- Destructive perimeter deletion is a noisy control-destruction/availability action and was not retained independently.

Telemetry corrections:

- `GetServicePerimeter`, `ListServicePerimeters`, and `ListAccessLevels` require `ADMIN_READ` permissions and generate off-by-default Data Access logs. The old post page incorrectly labeled them `DATA_READ`.
- VPC-SC denials generate Policy Denied logs whose generation cannot be disabled, not ordinary Data Access logs. These entries can still be excluded from the `_Default` sink, or that sink can be disabled, so durable routing and retention are separate controls.
- Dry-run violations are still logged, with `metadata.dryRun=true`; dry run only logs differences relative to enforced policy. Therefore moving policy into dry run does not “kill the violation signal.”
- `UpdateServicePerimeter` is an `ADMIN_WRITE` long-running operation in always-on Admin Activity at the access-policy/organization resource.
- A successfully allowed request produces no VPC-SC violation because there is no denial, but its underlying service telemetry still follows that service's audit contract. This is not anti-forensics by itself.

Official sources:

- https://docs.cloud.google.com/access-context-manager/docs/audit-logging
- https://docs.cloud.google.com/vpc-service-controls/docs/audit-logging
- https://docs.cloud.google.com/vpc-service-controls/docs/dry-run-mode

## 2026-09-28 — reciprocal review

Independently rechecked the zero-technique taxonomy and telemetry statements against the current Access Context Manager and VPC Service Controls audit documentation. No cloud API was invoked and no resource was changed.

- Retained zero post-exploitation H3s: reads remain enumeration, boundary mutations remain privilege escalation, standing permissive paths remain persistence, and successful data access belongs to the protected service.
- Corrected “non-disableable Policy Denied log” to the exact boundary: generation cannot be disabled, but entries can be excluded from the `_Default` sink and that sink can be disabled. The book and durable ledger now distinguish generation from routing/retention.
- Reconfirmed `GetServicePerimeter`, `ListServicePerimeters`, and `ListAccessLevels` as `ADMIN_READ` Data Access methods (off by default), and `UpdateServicePerimeter` as an `ADMIN_WRITE` Admin Activity long-running operation.
- Reconfirmed that `metadata.dryRun=true` applies to dry-run-only violations and that calls already denied by the enforced perimeter are not separately reported as dry-run differences.
