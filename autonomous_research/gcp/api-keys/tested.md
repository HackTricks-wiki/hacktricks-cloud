# API Keys — tested and reviewed

## 2026-09-28 — release/catalog delta and remote MCP review

This was a documentation and read-only API-surface review. No API was enabled, no IAM or API Key resource was changed, and no cleanup obligation was created.

### Delta result

- A fresh read-only `gcloud iam list-testable-permissions` pull returned exactly **13,701** unique project-testable permissions, unchanged from the 2026-09-25 ledger baseline.
- The official IAM permissions change log still ends at the week of 2026-09-22 and was last updated 2026-09-25. The aggregate 2026-09-26/27 release-note entries are Google SecOps SOAR rollout and internal/customer-fix announcements, not new GCP IAM or attack primitives.
- The only security-relevant boundary-day item was the 2026-09-25 Preview release of the API Keys remote MCP server. It exposes existing API methods as MCP tools and adds `mcp.tools.call`; it adds no new `apikeys.keys.*` permission.

### Exact authorization surface

Google documents that an MCP call requires `mcp.tools.call` on the project plus the underlying service permission. `roles/mcp.toolUser` contains `mcp.tools.call` and `resourcemanager.projects.get/list`.

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

The live unauthenticated `tools/list` method returned public schemas for all eight tools. This is documented discovery behavior and reveals no victim resource, so it is not an unauthenticated-access technique. The API Keys IAM table currently appears to typo `keys.lookupKey` as requiring `apikeys.keys.undelete`; the method reference says `apikeys.keys.lookup`, consistent with the live permission catalog and existing wiki. Treat this as a parity test case, not evidence of a bypass.

### Candidate assessment

1. **Possible 0-day — authorization parity:** test whether the MCP wrapper ever omits either the `mcp.tools.call` or underlying `apikeys.keys.*` check. This is the highest-priority candidate.
2. **Possible 0-day — IAM condition/project binding:** test `tool.name`, `resource.service`, `tool.isReadOnly`, parser ambiguity and cross-project resource selection. Only an actual policy bypass is reportable.
3. **Possible product-safety issue — risk hint:** `apikeys_update_key` publishes `destructiveHint:false` although updating `restrictions` can broaden a key. MCP annotations are advisory/untrusted, so this is low value unless a Google client relies on it to omit confirmation.
4. **Expected behavior, fold-only:** prompt injection into an agent holding `mcp.tools.call` plus API Key read/write permissions can call `getKeyString`, remove restrictions, create, or undelete keys. These are alternate transports for techniques already documented in the API Keys pages; do not add duplicate techniques. A future verified note may record the MCP requirement and the distinct `protoPayload.serviceName="apikeys.googleapis.com/mcp"` detection path.

### No-garbage closures

- Public `tools/list` metadata is intentional discovery, not victim recon.
- Google documents `mcp.tools.call` alone as granting no underlying API Key access; the open parity test above exists to verify that contract on the new wrapper.
- The retired `serviceusage.mcppolicy.*` family is not persistence: Google shut down MCP endpoint enablement/policy management on 2026-07-30; enabling the underlying service is now sufficient.
- API Keys MCP does not justify a standalone book technique unless a parity, conditional-IAM, or project-binding failure is live-confirmed.

## 2026-09-28 — live MCP authorization-parity probe

The `apikeys_list_keys` wrapper enforced both authorization layers in a minimum-permission live matrix. The API Keys API was already enabled; the test created no API key and read no key string.

- A disposable service account with `roles/mcp.toolUser`, `roles/serviceusage.serviceUsageConsumer`, and a custom role containing only `apikeys.keys.list` reached the wrapper and returned HTTP 200 successfully.
- An otherwise identical service account without `apikeys.keys.list` reached the wrapper but returned a tool error naming the missing `apikeys.keys.list` permission.
- A separate underlying-only case without a usable MCP grant was denied at the `mcp.googleapis.com/tools.call` gate. Project `testIamPermissions` reports the allow-policy name as `mcp.tools.call`, while the denial message uses its deny-policy/full-service spelling `mcp.googleapis.com/tools.call`; these are two forms of the same documented gate, not two independently grantable permissions.
- MCP's authorization cache lagged the Resource Manager `testIamPermissions` result: both grants were already visible through IAM before the MCP endpoint accepted them. The valid principal succeeded after roughly 30 seconds; the negative principal did not reach the underlying API Keys check until roughly 90 seconds. Short, immediate probes can therefore produce false conclusions.
- The successful read and denied read produced zero `protoPayload.serviceName="apikeys.googleapis.com/mcp"` entries under the project's default audit configuration, consistent with MCP Data Access logging being disabled by default.

Result: **no authorization bypass** for `apikeys_list_keys`. All disposable custom roles, service accounts, keys, IAM bindings and isolated local configurations were deleted; a final independent inventory check found no `ht-mcp-*` identity, binding, live custom role or temp directory.

## 2026-09-28 — conditional `tool.name` and duplicate-field desync probe

A second live matrix bound `roles/mcp.toolUser` only when both `resource.service == 'apikeys.googleapis.com'` and the MCP `tool.name` attribute equalled `apikeys_list_keys`. The test principal separately held both `apikeys.keys.list` and `apikeys.keys.get`, so an attempted `apikeys_get_key` could not be confused with a missing underlying service permission.

- The allowed list call succeeded after approximately 90 seconds of endpoint-specific IAM propagation.
- A normal `apikeys_get_key` call was denied at `mcp.googleapis.com/tools.call`, proving the condition—not the underlying API Keys permission—blocked it.
- A raw request with duplicate `params.name` fields ordered as allowed-list then denied-get was denied at the MCP gate. Reversing the fields executed the final list value successfully. The authorization and dispatcher therefore used the same last-wins interpretation; no duplicate-key parser desynchronization was found.
- Both the successful and denied calls again produced no MCP audit entry under the default Data Access configuration. The probe used a deliberately nonexistent key name, returned no key metadata or key string, and created no API Key resource.

The conditional binding, custom API-read role, service account, key, IAM bindings and isolated configuration were deleted, and cleanup independently verified no residue.

## 2026-09-28 — `tool.isReadOnly` deny-policy constraint

- Official MCP IAM guidance distinguishes the attributes: `resource.service` and `tool.name` are supported in allow bindings, while `tool.isReadOnly` is enforced through IAM deny policies. The earlier checklist wording that grouped all three under one conditional allow binding was wrong.
- A disposable principal holding MCP tool use plus exactly `apikeys.keys.list` and `apikeys.keys.update` reached the expected baseline after endpoint propagation: list succeeded and an update request against a deliberately nonexistent key passed both authorization layers before returning not found. No API Key resource was created or changed.
- Creating the narrowly scoped deny policy for that service-account unique ID was then rejected:
  the configured project Owner lacks `iam.googleapis.com/denypolicies.create`. No deny policy came into existence, so live `tool.isReadOnly` enforcement remains unverified in this lab rather than a failed boundary.
- The service account, key, API custom role, three project bindings and isolated configuration were deleted and independently verified absent. A final deny-policy listing found no matching policy.

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

## 2026-09-28 — privilege-escalation taxonomy and authorization-key review

Documentation, local role-description, local gcloud-help, and installed gcloud-source review only. No key, IAM binding, API state, or organization policy was changed.

- Retained one genuine privilege transition: creating an **authorization key** bound to a more-privileged service account. Unlike a standard key, Google processes it as the bound service account, but only for APIs supporting authorization keys and within its restrictions.
- Removed standard-key creation, `getKeyString`, and restriction broadening as privesc H3s. They are useful credential-access/persistence or billing/API abuse, but a standard key does not authenticate an IAM principal.
- The enforced authorization-key boundaries are `apikeys.keys.create` on the key project plus `iam.serviceAccounts.actAs` and `iam.serviceAccountApiKeyBindings.create` on the target service account. The synchronous CLI flow also needs `serviceusage.operations.get` to poll the create LRO and recover its completed response. Google additionally documents API Keys Admin + Service Usage Viewer as the role-based key creation prerequisite; the local CLI sends `serviceAccountEmail` in the same `CreateKey` request.
- The default managed constraint blocks service-account API-key bindings except allowed services; projects without an organization are unsupported. Gemini is allowed by the default constraint.
- Corrected telemetry: `CreateKey` is an Admin Activity LRO; `GetKeyString` is `ADMIN_READ` Data Access (off by default), not `DATA_READ`; `ListKeys` is explicitly in the no-audit-method list. Current public API Keys and IAM audit catalogs do not expose a second binding-specific method.
- Authorization-key use is not recorded in service-account usage metrics and obscures the end user's identity. Downstream audit coverage is entirely the target API's contract.

Official sources:

- https://docs.cloud.google.com/docs/authentication/api-keys
- https://docs.cloud.google.com/docs/authentication/api-keys-best-practices
- https://docs.cloud.google.com/api-keys/docs/access-control
- https://docs.cloud.google.com/api-keys/docs/audit-logging
