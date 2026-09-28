# Google SecOps post-exploitation research checklist

## Completed documentation and local checks — 2026-09-28

- [x] Classify every original H3 as supported, duplicate/destructive, or unverifiable.
- [x] Verify v1 UDM search and v1alpha raw-log search HTTP methods, request shapes, permissions, and
  data-access-scope boundary.
- [x] Verify RuleDeployment `enabled`, `alerting`, and `archived` semantics and update-mask behavior.
- [x] Verify rule PATCH permission, full-text revision behavior, optional etag, and revision evidence.
- [x] Verify reference-list entry replacement and data-table row creation permissions/schemas.
- [x] Verify dedicated feed-disable semantics, `ARCHIVED` state, and future-ingestion boundary.
- [x] Verify case bulk-close permission, migration prerequisite, numeric IDs, reason enum, and retained
  evidence/reopen boundary.
- [x] Correct Cloud Audit classes/defaults and distinguish search-event logging from query-text
  population.
- [x] Check local Google Cloud SDK 586.0.0 for a Chronicle command surface; none is installed.
- [x] Add exact minimums, bounded impact, categorical stealth, and expandable telemetry to every H3.
- [x] Independently cross-check public RPC spelling, empty-body requirements, non-atomic deployment
  updates, and case-closure request/resource fields.

## Safe future validation leads

- [ ] In an authorized IAM-migrated test tenant, capture `protoPayload.methodName` for each retained
  public v1/v1alpha operation and record whether it uses the public or internal `v1main` namespace.
- [ ] Compare UDM/raw-search audit entries before and after enabling all Chronicle API audit permission
  types, specifically separating method attribution from query-text population.
- [ ] With synthetic data, test whether a reference-list update and one-column data-table row change
  take effect immediately or after propagation, then restore the original content.
- [ ] Disable and immediately re-enable a synthetic feed while measuring feed state, freshness, and
  ingestion-health signals; do not use a production source.
- [ ] Close and reopen a synthetic SOAR case to capture Cloud Audit Logs and case-wall history without
  affecting a real investigation.

## Do not restore without stronger official evidence

- [ ] Do not claim a public retention or bulk-deletion primitive without an exact current API method,
  permission, request, and recovery boundary.
- [ ] Do not claim generic playbook disabling through `chronicle.soar*` without a documented public
  method and permission.
- [ ] Do not describe all SecOps Data Access operations as absent by default.
- [ ] Do not assume every reference list or data table is an allowlist; verify consuming rule logic.
- [ ] Do not use destructive rule/feed deletion when a narrower reversible primitive establishes the
  same offensive impact.
