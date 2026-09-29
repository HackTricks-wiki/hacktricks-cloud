# Resource Manager remote MCP — tested

## 2026-09-29 — project discovery and intentional Tool User exception

- Anonymous `tools/list` exposed one static read-only schema, `search_projects`; unauthenticated
  invocation returned HTTP 401.
- The current guide explicitly says Resource Manager is an exception: MCP-specific IAM attributes
  and `roles/mcp.toolUser`/`mcp.tools.call` cannot restrict this server. A disposable identity had
  `roles/browser` plus a narrow service-usage/get role and no `mcp.tools.call`; project
  `testIamPermissions` confirmed the outer permission was absent.
- An initial get-only probe returned no result during IAM propagation. A fresh isolated retest with
  only `resourcemanager.projects.get` plus `serviceusage.services.use` returned the same single
  visible project through direct v3 and MCP search after about one minute; Browser was not needed.
  The MCP result exposed only the normal project fields: name/number, project ID, display name,
  parent, state, create time, and etag. No visibility expansion was found.
- Direct and MCP searches each produced a Resource Manager `SearchProjects` Data Access entry in
  this hierarchy. The project-local audit configuration was empty, so the logs were likely enabled
  by an inaccessible ancestor policy; no `cloudresourcemanager.googleapis.com/mcp` wrapper entry
  was present. Public documentation correctly treats Resource Manager Data Access as off by
  default and inheritable.
- Removed all project bindings, both user-managed keys and service accounts, the custom role, and
  both isolated credential directories. Resource Manager remained enabled at baseline; the
  temporary role is only soft-deleted and no active principal or binding remains.
