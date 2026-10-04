# Parallelstore research checklist

## Completed 2026-09-28

- [x] Separate get/list enumeration from privilege escalation.
- [x] Separate standalone export, attacker-controlled import, and instance deletion from privesc.
- [x] Retain only the two-transfer chain that exercises a stronger source-bucket grant held by the
      transfer service agent.
- [x] Bound impact to transferred Cloud Storage data; do not claim token or general SA takeover.
- [x] Correct ExportData to off-by-default Data Access and ImportData to always-on Admin Activity.
- [x] Verify current GA gcloud flags, LRO behavior, role permissions, and VPC-SC boundary.
- [x] Record the current English documentation redirects without inferring product retirement.

## Open bounded leads

- [ ] In a disposable no-sensitive-data project, test the exact caller authorization for a
      user-selected transfer service account, including cross-project acceptance and act-as checks.
- [ ] Test the least object-level permissions that work for import and export; the published
      Parallelstore guide currently prescribes broad bucket-scoped `roles/storage.admin`.
- [ ] Verify whether transfer-operation state or service-specific platform logs provide a default-on
      signal beyond the documented Admin Activity import record.
- [ ] Monitor Parallelstore documentation redirects and release notes for a formal lifecycle or
      migration announcement; do not infer deprecation from redirects alone.
