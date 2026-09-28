# API Gateway — tested and verified

Last checked: 2026-09-28

## 2026-09-28 — MCP anonymous tool-discovery default live validation

- Enabled API Gateway, Service Management and Service Control from their initially disabled state
  and deployed one OpenAPI 3.x gateway with MCP globally enabled using
  `x-google-api-management.mcp: true`. The root-base-path fixture exposed one unauthenticated `GET`
  to `https://example.com` through `/mcp`; its referenced backend set `disableAuth: true`, so the
  fixture could not mint or forward a service-account identity token.
- Anonymous `initialize` and `tools/list` requests returned HTTP 200. `tools/list` disclosed the
  exact synthetic tool name, description and empty-object input schema. An anonymous `tools/call`
  reached the public operation, confirming invocation inherited that operation's deliberately empty
  authentication policy rather than bypassing a protected route.
- API Gateway automatically wrote platform request logs. The capture contained the outer `POST
  /mcp` request and a derived `GET /discovery/v1/service/.../mcptools` entry with
  `jsonPayload.apiMethod="google.api.discovery.v1.McpDiscoveryService.ListMcpTools"`; it identified
  the unauthenticated consumer as `jsonPayload.consumerNumber="0"`. The outer `/mcp` entry had no
  `apiMethod` and did not expose the JSON-RPC body. Treat the derived entry as observed Preview
  behavior, not a documented logging contract.
- Cross-review removed Certificate Transparency as a source of concrete default gateway hostnames:
  the managed certificates expose regional `*.gateway.dev` wildcard names, not individual random
  gateway hostnames. Passive DNS/URL scans and public client artifacts remain viable hostname
  sources; the gateway ID alone does not provide the generated hostname hash.
- Deleted the gateway, API config and API and verified that the generated hostname returned 404.
  Restored API Gateway, Service Management and Service Control to their initial disabled state,
  removed the local capture directory, and confirmed Cloud Asset Inventory plus project IAM
  searches returned no `ht-mcp-*` resource, identity or binding.

## Configuration update boundary — CORRECTED

- Official API Gateway documentation states that API configs are immutable except for display name
  and labels. A new definition creates a new config, and a gateway must then be explicitly updated
  to deploy it.
- The direct Service Management config-rollout auto-pull claim was therefore removed from API
  Gateway coverage. The existing API Gateway auth-bypass technique correctly uses
  `apigateway.apiconfigs.create` + `apigateway.gateways.update`.
- Added explicit minimum permissions and categorical stealth ratings to both API Gateway
  post-exploitation techniques.
- Removed the inference that `roles/apigateway.serviceAgent` containing `getAccessToken` means the
  gateway can disclose an OAuth access token. Official behavior and the verified primitive use an
  audience-bound ID token; the PoC now separates attacker destination from victim token audience.
- Corrected the blanket assumption that the Compute Engine default SA is always an Editor. Its
  actual roles must be enumerated; automatic grants are disabled by default in newer organizations.
- No lab resources were created or modified; no teardown was necessary.
