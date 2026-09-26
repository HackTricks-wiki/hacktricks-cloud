# Network Services — open ideas

Open ideas — Network Services / Service Extensions.

- [ ] On an existing disposable Agent Gateway, test whether `networkservices.agentGateways.update`
  alone can swap `registries`, `selfManaged.resourceUri(s)`, the governed access path or the
  connectivity template without separate `use`/authorization-policy permissions. Determine whether
  any accepted change bypasses policy, exposes decrypted connector credentials or only causes DoS.
- [ ] Test the newly exposed `extensionBindings` target scope and `failOpen` boundary with a
  synthetic Agent Gateway/inference endpoint. Do not publish an attack unless it grants a capability
  beyond ordinary ownership of the target policy.
- [ ] If an allowlisted disposable Cloud Multicast environment becomes available, verify whether an
  empty consumer accept list plus `requireExplicitAccept=false` permits an otherwise unauthorized
  project to activate as documented, and record exact audit and membership-log behavior.
- authzExtensions/lbEdgeExtensions/swpSecurityExtensions gap shipped; traffic/route/WASM extensions
  were already documented. Avoid duplicating those primitives.
