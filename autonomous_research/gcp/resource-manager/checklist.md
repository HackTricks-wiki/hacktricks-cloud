# Resource Manager — open ideas

Open ideas — Resource Manager / Org Policy.

## 2026-09-28 verified privilege-escalation contracts

- [x] Hierarchy-node `setIamPolicy` scope, condition-safe `etag` handling, current audit methods and
  policy-delta field.
- [x] Dual-sided tag binding permissions, inheritance/propagation, tag-condition impact and exact
  create/delete audit methods.
- [x] Tag-key/value IAM self-grant boundary and live runtime `TagValues.SetIamPolicy` method,
  including the catalog-label mismatch and omitted member/role fields.
- [x] Live paired TagBinding create/delete records for value-side and target-side authorization,
  followed by verified binding/value/key teardown.
- [x] Same-organization project/folder move commands, minimum permissions, inherited-policy bounds
  and Admin Activity telemetry.
- [x] IAM v3 project-principal-set PAB PolicyBinding delete/update restriction escape, exact
  dual-resource permissions, `etag`/condition handling, eligibility-only impact and Admin Activity
  LRO telemetry.
- [x] Removed standalone tag-definition creation and folded it into the only useful conditional chain.

## Open bounded validation

- [ ] In an organization-scoped disposable hierarchy, capture exact `authorizationInfo.resource`
  values for project/folder moves and tag bindings and verify operation start/completion placement.
- [ ] Measure tag-condition propagation across IAM allow, IAM deny and Organization Policy without
  weakening any production guardrail; delete every binding and value after the fixture.
- [ ] In an organization-scoped disposable fixture, verify whether project-parented
  `DeletePolicyBinding`/`UpdatePolicyBinding` emits one or multiple Admin Activity records across the
  project and PAB-owning organization, and capture the exact LRO start/completion resource fields.

- (deferred, verification-only) Org Policy v2 `CreatePolicy`/`UpdatePolicy` audit-class confirmation.
  The privesc technique AND its detection are already documented (`gcp-orgpolicy-privesc.md`, detection
  section). This is a log-class double-check that does not gate a wiki change unless the stealth story
  flips; low priority, no new technique expected.
