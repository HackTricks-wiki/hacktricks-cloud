# Cloud Product Registry — tested

## 2026-09-29 — GA REST and remote MCP boundary

- Mapped the GA `cloudproductregistry.googleapis.com` surface: read-only Product Suite, Logical
  Product, Logical Product Variant, and name-lookup methods plus seven matching remote MCP tools.
  The discovery document declares no OAuth scopes and Google documents the catalog as public data
  requiring no additional project-level IAM permission.
- An unauthenticated REST list and unauthenticated MCP `tools/call` were both rejected as
  unregistered callers. Unauthenticated `tools/list` succeeded, but disclosed only the public tool
  names and schemas. This is the standard remote-MCP discovery behavior and not useful victim
  reconnaissance.
- Enabled the API temporarily and created a fresh service account with only Service Usage Consumer.
  `testIamPermissions` confirmed `serviceusage.services.use=true` and `mcp.tools.call=false`.
  A token was minted through the target project's pre-existing IAM Credentials API without a key.
- Both direct REST `productSuites.list` and the matching MCP tool returned generic
  `INVALID_ARGUMENT`, including with the owner caller. This prevented a meaningful outer-MCP-gate
  comparison. The behavior might be rollout, enrollment, consumer-registration, or backend state;
  it is not evidence of an authorization bypass.
- Classified the service as generic public catalog data with no current attacker benefit. Do not
  add a book technique unless a future response exposes non-public prelaunch metadata or an MCP
  discrepancy crosses an actual security boundary.
- Cleanup removed the project IAM binding, disposable service account and its resource policy,
  disabled Cloud Product Registry back to baseline, and deleted every local response file. Final
  API, live-account, and project-binding checks were empty.
