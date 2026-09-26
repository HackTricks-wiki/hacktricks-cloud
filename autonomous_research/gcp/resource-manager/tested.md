# Resource Manager — tested

Resource Manager (Projects/Folders/Orgs, Tags, Org Policy). Covered (Tag IAM-condition privesc,
deleteTagBinding evasion, LogSink DENY anti-forensics, project/folder.move guardrail-escape).

## Corrections applied (do NOT regress)
- Custom-constraint methodTypes are CREATE/UPDATE ONLY, never DELETE (page was wrong).
- `resourcemanager.tagValues.use` does NOT exist — real gate is dual-scoped `tagUser`.

## Audit classification — VERIFIED
- The current official audit-method tables classify Org Policy v2 `CreatePolicy`, `UpdatePolicy`,
  `DeletePolicy`, `CreateCustomConstraint`, and `UpdateCustomConstraint` as always-on Admin Activity.
- Legacy v1 `setOrgPolicy` is hosted and logged under `cloudresourcemanager.googleapis.com`; v2 uses
  `orgpolicy.googleapis.com`. The old book text incorrectly assigned the legacy write to the v2
  service name. All four Org Policy techniques now have exact minimum permissions, expandable log
  tables, and stealth ratings.
