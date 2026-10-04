# Organization Policy remote MCP — tested

## 2026-09-29 — tool catalog, read behavior, and cleanup

- Anonymous `tools/list` exposed 12 static schemas: six read tools for constraints, policies, and custom constraints, plus six create/update/delete tools. Unauthenticated invocation returned HTTP 401.
- Read-only positive controls exercised `ListConstraints` and `ListPolicies`. Constraint discovery returned the normal project-applicable catalog; the lab project had no explicit v2 policies.
- Mapped the documented two-layer permission model: `mcp.tools.call` plus the relevant `orgpolicy.*` permission. The public page records this expected contract and routes write impact to the existing Organization Policy privilege-escalation coverage.
- Corrected a material scope ambiguity in that existing coverage: the policy resource can be project/folder-scoped, but `roles/orgpolicy.policyAdmin` is organization-grantable only and its write authority reaches descendants through inheritance or a tag-conditioned organization binding. The live project grantable-role catalog excluded the administrator role, and a project custom role rejected a v2 policy-write permission.
- No policy or custom constraint was created, updated, or deleted. Write permissions could not be safely exercised at the shared project's resource scope and are not supported in project custom roles.
- No matching Organization Policy or MCP audit event appeared under the project's default audit configuration, consistent with reads and wrapper calls being off-default Data Access. Mutations remain always-on Admin Activity.
- Removed every temporary binding, both service accounts and user-managed keys, the custom role, and isolated local credentials. Organization Policy remained enabled at its pre-test baseline.
