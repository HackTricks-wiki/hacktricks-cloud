# API Keys — open leads

Last researched: 2026-09-28

The 2026-09-25 API Keys remote MCP server Preview adds a new authorization and audit wrapper around
the existing API Keys API. It adds no new `apikeys.keys.*` capability, so do not author a book
technique unless testing proves a distinct security boundary failure.

## Possible vulnerabilities — keep internal until verified

- [ ] **MCP authorization parity.** With minimum-permission test principals, verify that every tool
      requires both `mcp.tools.call` and its underlying permission: `apikeys.keys.list`, `.get`,
      `.getKeyString`, `.create`, `.update`, `.delete`, `.undelete`, or `.lookup`. Test each half
      independently as well as the valid pair. A tool succeeding with only one half is reportable;
      normal two-layer enforcement is not a book technique.
- [ ] **Conditional-IAM binding and project selection.** Bind `roles/mcp.toolUser` to one exact
      `tool.name`, deny non-read-only tools with `tool.isReadOnly`, and try other tool names, duplicate
      JSON fields, case/Unicode variants, conflicting MCP metadata, and cross-project resource names.
      If a second controlled project is available, ensure its MCP deny policy cannot be bypassed by
      selecting a caller/quota project where `mcp.tools.call` is allowed.
- [ ] **Risk-hint accuracy in a Google-controlled client.** The live `tools/list` result marks
      `apikeys_update_key` as `readOnlyHint:false` but `destructiveHint:false`, even though it can
      remove restrictions and make a scoped key unrestricted. This is only reportable if a
      Google-controlled client treats the hint as a meaningful confirmation/safety boundary and
      performs restriction removal without the expected warning.
- [ ] **Audit parity.** For one allowed read and one reversible update, determine whether MCP emits
      only `SERVICE_NAME/mcp`, both MCP and underlying API entries, or another shape. Confirm that
      `DATA_READ` is absent with default logging and that the update is attributable Admin Activity.

## Test constraints

- Prefer an existing disposable lab key. A newly created API key remains soft-deleted for 30 days
  after deletion and therefore cannot satisfy immediate hard cleanup.
- Restore an existing key's exact original restrictions immediately after an update test.
- Remove all temporary IAM bindings, custom roles, deny policies, and local credentials.
- Do not re-test `serviceusage.mcppolicy.get/update` or `serviceusage.effectivemcppolicy.get` as an
  enablement control: MCP policy management was shut down on 2026-07-30 and these permissions are
  deprecated catalog residue.
