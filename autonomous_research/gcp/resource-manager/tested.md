# Resource Manager — tested

Resource Manager (Projects/Folders/Orgs, Tags, Org Policy). Covered (Tag IAM-condition privesc,
deleteTagBinding evasion, LogSink DENY anti-forensics, project/folder.move guardrail-escape).

## Corrections applied (do NOT regress)
- Custom-constraint methodTypes are CREATE/UPDATE ONLY, never DELETE (page was wrong).
- `resourcemanager.tagValues.use` does NOT exist — real gate is dual-scoped `tagUser`.

## Standing UNVERIFIED candidate
- Org Policy v2 `CreatePolicy` / `UpdatePolicy` audit classification (ADMIN_WRITE?) is unconfirmed.
