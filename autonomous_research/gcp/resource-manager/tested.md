# Resource Manager — tested

Resource Manager (Projects/Folders/Orgs, Tags, Org Policy). Covered (Tag IAM-condition privesc,
deleteTagBinding evasion, LogSink DENY anti-forensics, project/folder.move guardrail-escape, PAB
PolicyBinding restriction escape).

## 2026-09-28 — privilege-escalation page audit

- Consolidated organization/folder/project `setIamPolicy` into one hierarchy-scoped primitive and
  distinguished a destructive one-permission replacement from a condition-safe version 3/`etag`
  read-modify-write.
- Corrected Resource Manager audit method names to the current v3 catalog and moved IAM binding
  deltas to `protoPayload.serviceData.policyDelta.bindingDeltas`.
- Consolidated create/delete TagBinding around the actual condition-flipping boundary. Exact custom
  permissions require the target resource's service-specific `createTagBinding`/`deleteTagBinding`
  and `resourcemanager.tagValueBindings.create`/`.delete` on the tag value; Tag User on both sides is
  the documented predefined-role form.
- Folded tag-key/value creation into the binding technique. Creation alone is not escalation; it
  matters only for a compatible key-level condition and when the caller can also use the value and
  attach it to the target.
- Retained tag-value/tag-key IAM self-grant as a separate chain because it converts tag-policy
  authority into use of a privileged value.
- Added the IAM v3 PolicyBinding restriction-escape chain: deleting the last applicable
  project-principal-set PAB binding, or conditionally excluding a controlled principal from every
  applicable binding, can restore eligibility to resources already allowed by IAM. This is bounded
  to eligibility only; it neither grants a role nor overrides deny, and other applicable PABs still
  participate. Exact project/PAB permissions and v3 Admin Activity LRO methods are documented.
- Bounded project/folder reparenting to inherited IAM and Organization Policy effects and removed
  the unsupported implication that PAB bindings are simply inherited from the resource parent.
  Corrected the stable/beta command split and same-organization minimum permissions; cross-org
  migration has additional requirements and is not represented by the short chain.
- Result: eight mixed headings became five genuine privilege-escalation primitives, all with exact
  prerequisites, bounded impact, categorical stealth and expandable telemetry.

That documentation pass did not access or change cloud state; it used current official documentation,
installed gcloud role/help output and static page checks. The separate bounded live validation below
then exercised only disposable tag resources.

## 2026-09-28 — live project-tag telemetry validation

- Created one project-scoped disposable tag key/value, granted the active test principal Tag User
  only on that value, attached it to the project without any policy condition, and then deleted the
  binding, value and key.
- The runtime IAM method contradicted the summary catalog label: the value write emitted
  `google.cloud.resourcemanager.v3.TagValues.SetIamPolicy`, authorized by
  `resourcemanager.tagValues.setIamPolicy`, not a `setIamPermissions` method.
- The SetIamPolicy request identified only the TagValue and omitted the added member/role; there was
  no `serviceData.policyDelta`. The page now requires a state diff or policy read to identify the
  exact self-grant.
- Existing same-day project-policy records used runtime `methodName="SetIamPolicy"` with
  `resourcemanager.projects.setIamPolicy`, rather than the scope-qualified operation label shown in
  the catalog summary. The page now filters the emitted method and uses permission/resource fields
  to distinguish hierarchy scope.
- Each TagBinding create/delete emitted two Admin Activity entries with the same method: one for
  `resourcemanager.tagValueBindings.create/delete` on the value and one for
  `resourcemanager.hierarchyNodes.createTagBinding/deleteTagBinding` on the project. The paired
  request/resource fields exposed both sides of the binding.
- Direct tag listing and Cloud Asset/IAM searches confirmed no matching binding, key, value or IAM
  policy remained after deletion. No API was enabled and no unrelated project IAM changed.

## Corrections applied (do NOT regress)
- Custom-constraint methodTypes are CREATE/UPDATE ONLY, never DELETE (page was wrong).
- `resourcemanager.tagValues.use` does NOT exist — real gate is dual-scoped `tagUser`.
- A user cannot be granted project Owner directly through `setIamPolicy`; the example uses a
  controlled service account. Condition-safe tag IAM helpers also require the matching
  `getIamPolicy` permission.
- Folder moves authorize `resourcemanager.folders.move` on the current and destination parents.
  Google's project-move guide and v3 method reference describe different project-side permission
  checks, so the page preserves both contracts instead of silently treating either as exhaustive.

## 2026-09-28 — IAM v3 PAB PolicyBinding documentation validation

- Official removal documentation requires `resourcemanager.projects.deletePolicyBinding` on the
  project-principal-set binding parent and `iam.principalaccessboundarypolicies.unbind` on the PAB's
  organization. The update variant requires `resourcemanager.projects.updatePolicyBinding` plus
  `iam.principalaccessboundarypolicies.bind`; `iam.operations.get` is only for polling the LRO.
- PolicyBinding conditions can reference `principal.subject`; a false condition makes the binding's
  PAB inapplicable to that principal. The safe command preserves the current `etag` and warns to
  combine, rather than erase, an existing expression.
- The IAM audit catalog classifies
  `google.iam.v3.PolicyBindings.DeletePolicyBinding` and
  `google.iam.v3.PolicyBindings.UpdatePolicyBinding` as always-on Admin Activity long-running
  operations. No live mutation was performed for this documentation validation.

## Audit classification — VERIFIED
- The current official audit-method tables classify Org Policy v2 `CreatePolicy`, `UpdatePolicy`,
  `DeletePolicy`, `CreateCustomConstraint`, and `UpdateCustomConstraint` as always-on Admin Activity.
- Legacy v1 `setOrgPolicy` is hosted and logged under `cloudresourcemanager.googleapis.com`; v2 uses
  `orgpolicy.googleapis.com`. The old book text incorrectly assigned the legacy write to the v2
  service name. All four Org Policy techniques now have exact minimum permissions, expandable log
  tables, and stealth ratings.
