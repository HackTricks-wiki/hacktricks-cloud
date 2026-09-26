# API Gateway — tested and verified

Last checked: 2026-09-26

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
