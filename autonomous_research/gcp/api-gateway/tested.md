# API Gateway — tested and verified

Last checked: 2026-09-28

## 2026-09-28 — model-router arbitrary-backend credential boundary

- Deployed a bounded OpenAPI 3.x model router whose default model targeted a disposable public
  Cloud Run capture service rather than a Google model endpoint. API-config validation accepted the
  arbitrary HTTPS backend, consistent with the Preview documentation's warning that backend-domain
  allowlisting is not enforced.
- The capture service returned only credential shape and selected decoded claims; it never returned
  or logged the token. Two anonymous requests reached the selected backend with `Authorization:
  Bearer` and HTTP 200.
- The forwarded credential was a three-segment Google-signed JWT, not an opaque OAuth access token:
  issuer `https://accounts.google.com`, audience exactly equal to the configured backend URL, the
  configured backend service-account email, and a 3,600-second lifetime. This closes the reusable
  OAuth-token exfiltration hypothesis. A malicious configured backend can receive its own
  audience-bound identity token, which is expected backend-auth behavior and still reinforces that
  model-router configuration is a high-trust control plane.
- API Gateway wrote the ordinary platform request entry under
  `apigateway.googleapis.com/requests`; `jsonPayload.apiMethod` resolved to the generated
  `BoundedModelRoute` operation and anonymous `jsonPayload.consumerNumber` was `0`. The backend
  request appeared separately in `run.googleapis.com/requests`.
- Deleted the gateway, successful API config and API, Cloud Run service, source-build Artifact
  Registry repository, bucket and dedicated service account; the earlier rejected config never
  created a resource. Restored API Gateway,
  Service Management and Service Control to their initially disabled state, removed the temporary
  sources/responses, and confirmed Cloud Asset and IAM searches contained no `ht-mr` residue.

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
