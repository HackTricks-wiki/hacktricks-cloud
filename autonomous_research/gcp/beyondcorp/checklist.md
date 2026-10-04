# BeyondCorp / Chrome Enterprise Premium research checklist

## Completed documentation checks

- [x] Separate the configuration caller, gateway delegating service account, end-user policy, Chrome client, and upstream application identities.
- [x] Verify current Admin/Editor/Viewer and empty-permission data-plane role contents.
- [x] Verify stable Security Gateway application create/update/list/describe and IAM command shapes against local CLI help/source.
- [x] Verify current v1 CRUD audit methods, classes, defaults, and LRO behavior.
- [x] Verify optional `AuthorizeUser` Data Access and Security Gateway connection-log configuration.
- [x] Bound private access to supported web routing and reject generic TCP and metadata-server claims.
- [x] Remove destructive DoS, automatic MITM, anonymous bypass, and retired connector creation claims from active technique coverage.
- [x] Independently validate the nested application-upstream parser, update-helper preflight GET and LRO poll permissions, and IAM helper policy-version/condition/etag preservation.
- [x] Inspect standalone current-resource IAM reads and replace condition-loss-prone CLI reads with explicit v1 REST `requestedPolicyVersion=3` enumeration.

## Safe future validation

- [ ] On an already-existing disposable licensed gateway, capture application and gateway `GetIamPolicy`/`SetIamPolicy` entries. Record exact `protoPayload.methodName`, log name/class, monitored resource, and default visibility; immediately restore the exact etag-protected policies.
- [ ] With an existing synthetic private HTTPS application, verify the minimum data-plane combination: application `sgApplicationUser`, gateway `serviceDiscoveryUser`, managed Chrome configuration, and no additional configuration-plane permission.
- [ ] Temporarily change a disposable application's endpoint matcher within the same already-authorized VPC and capture the `UpdateApplication` LRO start/completion pair, route propagation delay, `AuthorizeUser`, connection log, and target access log. Restore the exact original application immediately.
- [ ] Separately test whether the current service accepts `upstreams` in an application update mask. The stable CLI serializes the nested field, but current management guidance only documents changing endpoint matchers; do not claim cross-VPC repointing until server behavior is captured.
- [ ] Verify whether a principal with application access but no gateway service-discovery binding can use a legacy PAC-configured gateway, and clearly separate legacy/current client behavior.
- [ ] Test whether public principals are rejected or simply unusable at authorization time; do not describe `allUsers` as unauthenticated access unless the full client/data-plane path is demonstrated.
- [ ] Confirm that secure-gateway connection logging is disabled on a new gateway by default if a cost-approved disposable licensed environment becomes available.

## Legacy/open leads

- [ ] Inventory any pre-retirement `appConnectors`, `appConnections`, and `appGateways` in an authorized existing tenant. Do not create new resources; support ended in July 2026.
- [ ] Compare legacy connector IAM audit methods with actual behavior only if such resources remain operational.
- [ ] Assess proxy-protocol contextual or metadata header configuration for a distinct trust-boundary issue; do not claim header spoofing without an upstream application that trusts the injected fields incorrectly.
- [ ] Review organization policies, IAM deny policies, and principal-access-boundary support for limiting current Security Gateway policy grants.

## Cleanup guardrails

- [ ] Never create a paid gateway, hub, license assignment, connector VM, VPN, or Interconnect solely for documentation validation.
- [ ] For any approved test, save exact original gateway/application JSON and etag-bearing IAM policies before changes.
- [ ] Restore application routing first, then IAM policies, logging settings, browser policy, target firewall/DNS, and any temporary test principal.
- [ ] Confirm no LRO, application, binding, log setting, browser policy, firewall rule, DNS record, or synthetic upstream remains.
