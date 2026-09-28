# Network Security privilege escalation - checklist

## Completed 2026-09-28

- [x] Distinguish modern targeted `AuthzPolicy` from legacy unattached `AuthorizationPolicy`.
- [x] Validate ALLOW/DENY/CUSTOM evaluation order and bound the bypass impact.
- [x] Validate direct REST and declarative-import permissions, helper reads, and LRO polling.
- [x] Validate `ServerTlsPolicy.allowOpen` applicability and attached-resource prerequisite.
- [x] Validate project and organization address-group membership methods, permissions, and propagation.
- [x] Review TLS inspection, client TLS, backend authentication, gateway rules, URL lists, security profiles, firewall endpoints, and DNS threat detection against the privilege-escalation bar.
- [x] Review Network Security Integration intercept and mirroring resource graphs, immutable fields, and producer/consumer trust boundaries.
- [x] Validate resource-level IAM targets and condition/etag-safe allow-policy mutation.
- [x] Validate every retained technique's audit method, class, default visibility, and conditional downstream signals.
- [x] Validate commands with Google Cloud CLI 586.0.0 help and source definitions.
- [x] Independently cross-review AuthzPolicy schema/evaluation, TLS field compatibility, address-group helper permissions, intercept forwarding-rule boundaries, resource-IAM mutation safety, and downstream product logs.

## Open validation leads

- [ ] In a disposable producer/consumer lab, live-validate the documented/current CLI behavior that an actor with only `networksecurity.interceptDeployments.create` can reference a known compatible existing forwarding rule without an additional forwarding-rule permission check. Do not test without a bounded cleanup plan.
- [ ] Capture whether a consumer endpoint group's inventory/state immediately exposes a newly added producer deployment location and whether any consumer-side system event is emitted.
- [ ] Recheck Secure Web Proxy and Agent Gateway request-log fields and defaults as those products' logging contracts evolve.
- [ ] Recheck the documentation inconsistency that names `roles/compute.securityAdmin` for address-group management while the current predefined role contains no `networksecurity.*` permissions.
- [ ] Consider moving conditional TLS/client/backend trust manipulation and filter-evasion ideas to the relevant post-exploitation page rather than reintroducing them here.
