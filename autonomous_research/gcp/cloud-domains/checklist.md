# Cloud Domains research checklist

## Covered

- [x] Registrar DNS delegation replacement and DNSSEC boundary.
- [x] Transfer lock, authorization-code retrieval, and push-transfer variants.
- [x] Contact privacy disclosure and confirmation/non-atomic update boundary.
- [x] Registration get/list recon and audit defaults.
- [x] Registration-scoped IAM persistence with policy preservation.
- [x] Exact v1 audit methods, categories, LRO status, and default visibility.
- [x] Current Google Cloud CLI syntax.
- [x] Deprecated Google Domains import/export surfaces and no-garbage classification.
- [x] Unauthenticated-surface assessment.

## Safe future validation

- [ ] If a purpose-bought disposable domain is explicitly authorized, validate `ConfigureDnsSettings`, `ConfigureContactSettings`, and `ConfigureManagementSettings` start/completion audit pairs, then restore every setting immediately.
- [ ] On that disposable registration, validate registration-level grantability of `roles/domains.editor`, exact `SetIamPolicy` payload fields, and `GetIamPolicy` policy-version behavior; remove the test binding immediately.
- [ ] Confirm the exact registrar-side emails and state transitions for a supported transfer without completing a transfer to an external registrar.
- [ ] Compare DNS delegation visibility and DNSSEC failure behavior at multiple resolvers after a safely reversed change.

## Guardrails

- Do not register, unlock, transfer, publish contact data, or alter delegation on a real domain without explicit ownership and rollback authorization.
- Do not proceed with an external registrar transfer merely to validate the primitive.
- Preserve IAM policy version, conditions, and `etag`; remove any test binding during the same test window.
