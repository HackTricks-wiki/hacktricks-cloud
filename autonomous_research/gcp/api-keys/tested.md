# API Keys — tested and reviewed

## 2026-09-28 — release/catalog delta and remote MCP review

This was a documentation and read-only API-surface review. No API was enabled, no IAM or API Key
resource was changed, and no cleanup obligation was created.

### Delta result

- A fresh read-only `gcloud iam list-testable-permissions` pull returned exactly **13,701** unique
  project-testable permissions, unchanged from the 2026-09-25 ledger baseline.
- The official IAM permissions change log still ends at the week of 2026-09-22 and was last updated
  2026-09-25. The aggregate 2026-09-26/27 release-note entries are Google SecOps SOAR rollout and
  internal/customer-fix announcements, not new GCP IAM or attack primitives.
- The only security-relevant boundary-day item was the 2026-09-25 Preview release of the API Keys
  remote MCP server. It exposes existing API methods as MCP tools and adds `mcp.tools.call`; it adds
  no new `apikeys.keys.*` permission.

### Exact authorization surface

Google documents that an MCP call requires `mcp.tools.call` on the project plus the underlying
service permission. `roles/mcp.toolUser` contains `mcp.tools.call` and
`resourcemanager.projects.get/list`.

| MCP tool | Underlying permission |
|---|---|
| `apikeys_list_keys` | `apikeys.keys.list` |
| `apikeys_get_key` | `apikeys.keys.get` |
| `apikeys_get_key_string` | `apikeys.keys.getKeyString` |
| `apikeys_create_key` | `apikeys.keys.create` |
| `apikeys_update_key` | `apikeys.keys.update` |
| `apikeys_delete_key` | `apikeys.keys.delete` |
| `apikeys_undelete_key` | `apikeys.keys.undelete` |
| `apikeys_lookup_key` | `apikeys.keys.lookup` |

The live unauthenticated `tools/list` method returned public schemas for all eight tools. This is
documented discovery behavior and reveals no victim resource, so it is not an unauthenticated-access
technique. The API Keys IAM table currently appears to typo `keys.lookupKey` as requiring
`apikeys.keys.undelete`; the method reference says `apikeys.keys.lookup`, consistent with the live
permission catalog and existing wiki. Treat this as a parity test case, not evidence of a bypass.

### Candidate assessment

1. **Possible 0-day — authorization parity:** test whether the MCP wrapper ever omits either the
   `mcp.tools.call` or underlying `apikeys.keys.*` check. This is the highest-priority candidate.
2. **Possible 0-day — IAM condition/project binding:** test `tool.name`, `resource.service`,
   `tool.isReadOnly`, parser ambiguity and cross-project resource selection. Only an actual policy
   bypass is reportable.
3. **Possible product-safety issue — risk hint:** `apikeys_update_key` publishes
   `destructiveHint:false` although updating `restrictions` can broaden a key. MCP annotations are
   advisory/untrusted, so this is low value unless a Google client relies on it to omit confirmation.
4. **Expected behavior, fold-only:** prompt injection into an agent holding `mcp.tools.call` plus
   API Key read/write permissions can call `getKeyString`, remove restrictions, create, or undelete
   keys. These are alternate transports for techniques already documented in the API Keys pages;
   do not add duplicate techniques. A future verified note may record the MCP requirement and the
   distinct `protoPayload.serviceName="apikeys.googleapis.com/mcp"` detection path.

### No-garbage closures

- Public `tools/list` metadata is intentional discovery, not victim recon.
- Google documents `mcp.tools.call` alone as granting no underlying API Key access; the open parity
  test above exists to verify that contract on the new wrapper.
- The retired `serviceusage.mcppolicy.*` family is not persistence: Google shut down MCP endpoint
  enablement/policy management on 2026-07-30; enabling the underlying service is now sufficient.
- API Keys MCP does not justify a standalone book technique unless a parity, conditional-IAM, or
  project-binding failure is live-confirmed.

### Official sources

- https://docs.cloud.google.com/release-notes#September_25_2026
- https://docs.cloud.google.com/api-keys/docs/reference/mcp
- https://docs.cloud.google.com/api-keys/docs/access-control
- https://docs.cloud.google.com/mcp/control-mcp-use-iam
- https://docs.cloud.google.com/mcp/prevent-read-write-tool-use
- https://docs.cloud.google.com/mcp/audit-logging
- https://docs.cloud.google.com/api-keys/docs/reference/mcp/tools_list/apikeys_update_key
- https://docs.cloud.google.com/service-usage/docs/deprecations
- https://docs.cloud.google.com/iam/docs/permissions-change-log#2026-09-22
