# API Keys — open leads

Last researched: 2026-09-28

The 2026-09-25 API Keys remote MCP server Preview adds a new authorization and audit wrapper around
the existing API Keys API. It adds no new `apikeys.keys.*` capability, so do not author a book
technique unless testing proves a distinct security boundary failure.

## Possible vulnerabilities — keep internal until verified

- [ ] **MCP authorization parity.** The read-only `apikeys_list_keys` case is complete: a principal
      with `roles/mcp.toolUser` plus `apikeys.keys.list` succeeded, while removing the underlying
      permission produced an explicit denial and an underlying-only case failed at the MCP gate.
      Repeat the pair/half matrix for `.get`, `.getKeyString`, `.create`, `.update`, `.delete`,
      `.undelete`, and `.lookup` only when a no-residue fixture exists. A tool succeeding with only
      one half is reportable; normal two-layer enforcement is not a book technique. Allow at least
      two minutes for endpoint-specific IAM propagation before interpreting a denial.
- [ ] **Conditional-IAM binding and project selection.** Exact `tool.name` enforcement and the
      duplicate-JSON-field desync case are complete: the allowed list tool succeeded, get was denied,
      and both duplicate-field orders consistently authorized the last parsed tool name. Unlike
      `tool.name`, `tool.isReadOnly` is a deny-policy attribute; its narrowly scoped live test is
      blocked because the lab Owner lacks `iam.googleapis.com/denypolicies.create`. Retest only with
      explicit deny-policy administration. Still test case/Unicode variants, conflicting MCP
      metadata, and cross-project resource names. If a second controlled project is available, ensure
      its MCP policy cannot be bypassed by selecting a caller/quota project where `mcp.tools.call` is
      allowed. Allow at least two minutes for MCP-specific IAM propagation before interpreting a denial.
- [ ] **Risk-hint accuracy in a Google-controlled client.** The live `tools/list` result marks
      `apikeys_update_key` as `readOnlyHint:false` but `destructiveHint:false`, even though it can
      remove restrictions and make a scoped key unrestricted. This is only reportable if a
      Google-controlled client treats the hint as a meaningful confirmation/safety boundary and
      performs restriction removal without the expected warning.
- [ ] **Audit parity.** The allowed and denied `apikeys_list_keys` calls produced no MCP audit entry
      under default logging, as expected for Data Access. For one reversible update, determine
      whether MCP emits only `SERVICE_NAME/mcp`, both MCP and underlying API entries, or another
      shape, and confirm that the update is attributable Admin Activity.

## Test constraints

- Prefer an existing disposable lab key. A newly created API key remains soft-deleted for 30 days
  after deletion and therefore cannot satisfy immediate hard cleanup.
- Restore an existing key's exact original restrictions immediately after an update test.
- Remove all temporary IAM bindings, custom roles, deny policies, and local credentials.
- Do not re-test `serviceusage.mcppolicy.get/update` or `serviceusage.effectivemcppolicy.get` as an
  enablement control: MCP policy management was shut down on 2026-07-30 and these permissions are
  deprecated catalog residue.

## Authorization-key follow-ups

- [ ] In an organization-owned disposable project whose managed constraint already permits a test
      API, verify the minimum custom-permission matrix for authorization-key creation. Do not loosen
      organization policy merely for this test.
- [ ] Capture one authorization-key `CreateKey` LRO and confirm whether any non-public,
      binding-specific audit entry accompanies the catalogued API Keys entry. Treat absence from the
      public catalog as a documented detection boundary, not proof that no internal or future entry
      can appear.
- [ ] Maintain a current allow-list of APIs that actually support authorization keys. Do not infer
      that an authorization key is a universal service-account credential from the service account's
      broader IAM grants.
- [ ] Verify whether a key project can bind a service account from a different project before
      documenting any cross-project boundary. Current public creation examples use a service-account
      email but do not state a supported cross-project contract.
- [ ] Avoid new-key probes in environments requiring immediate hard cleanup: API keys remain
      recoverable for 30 days after deletion.
