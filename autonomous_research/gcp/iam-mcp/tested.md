# IAM remote MCP — tested

## 2026-09-29 — role/deny surface, authorization layers, and tool conditions

- Anonymous discovery returned 12 static tools: six for custom-role list/get/create/update/delete/
  undelete and six for project deny-policy list/get/create/update/delete/operation status. Mutating
  schemas were not exposed to victim data without invocation.
- A disposable principal with `iam.roles.list` and `serviceusage.services.use`, but no
  `mcp.tools.call`, listed its project custom role directly and was denied at the MCP wrapper on
  `mcp.googleapis.com/tools.call`. An unauthenticated tool call returned HTTP 401. No outer-gate
  bypass was found.
- An Owner positive control needed `X-Goog-User-Project` set explicitly; otherwise the wrapper used
  the credential's unrelated quota project and reported that IAM was disabled there. With the
  header, `list_roles` succeeded and `update_role` changed only the disposable role title. The
  underlying write emitted always-on `google.iam.admin.v1.UpdateRole`; no
  `iam.googleapis.com/mcp` entry appeared because MCP Data Access was disabled.
- Verified a fine-grained `roles/mcp.toolUser` allow binding. After the service-wide control grant
  was removed and IAM propagation settled, a condition allowing only `list_roles` admitted that
  tool and denied `update_role`, while the same identity's direct title-only role patch succeeded.
  Stateless requests needed `Mcp-Method: tools/call` for the `mcp.googleapis.com/tool.name`
  attribute to evaluate; omitting it failed closed. A briefly successful write during grant
  replacement disappeared after cache propagation and was not an authorization bypass.
- The current Owner role now includes `iam.denypolicies.get` and `iam.denypolicies.list`; an Owner
  MCP `list_deny_policies` call returned an empty project list. Owner still lacks create/update/
  delete, so the existing org-level `roles/iam.denyAdmin` write prerequisite remains unchanged.
- Removed both IAM bindings, the key, service account, custom role, and isolated credential tree.
  IAM stayed enabled at its baseline; the temporary role is only in GCP's expected soft-deleted
  state, with no active principal or binding.
