# Amazon EVS attack ideas

- [x] `GetEnvironment` plus exact Secrets Manager reads for VCF management and ESX root credentials.
- [x] `ListEnvironmentConnectors` plus exact Secrets Manager reads for appliance credentials.
- [ ] Connector credential relay: with a disposable environment, controlled same-domain DNS/TLS and canary secret, determine whether FQDN-only update sends Basic/session credentials to the new host.
- [ ] `GetDepotUrl`: re-check when the operation reaches the installed SDK/CLI model; determine URL lifetime, binding and whether it grants access to proprietary VCF add-on artifacts.
- [ ] Entitlement integrity: test whether create/delete entitlement can affect arbitrary VM IDs or is tightly bound to discovered VMs in the same environment.
