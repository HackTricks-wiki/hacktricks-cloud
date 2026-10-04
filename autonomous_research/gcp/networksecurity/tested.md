# Network Security privilege escalation - tested research

## 2026-09-28 - documentation and local CLI/source audit

No cloud resources were created or mutated. Contracts were checked against the current Google Cloud REST references, audit-log catalog, IAM role definitions, Google Cloud CLI 586.0.0 help, declarative-import definitions, and v1 discovery document.

### Promoted

- **Modern `AuthzPolicy` create/update:** the policy embeds forwarding-rule or gateway targets, so an `ALLOW` policy can grant application/network access without a separate attachment permission. A matching `DENY` or rejecting `CUSTOM` policy still wins. Direct minimum is `networksecurity.authzPolicies.create` or `.update`; `networkservices.authzExtensions.use` is conditional on a referenced authorization extension. Declarative import additionally reads the resource and synchronous mode polls its LRO.
- **Legacy `AuthorizationPolicy` update:** only useful when an Endpoint Policy or other supported consumer already references it. Empty `rules` applies the selected action to every request. Direct PATCH needs `.update`; create by itself was rejected as non-impactful.
- **Legacy mesh `ServerTlsPolicy` update:** `allowOpen: true` permits plaintext for Traffic Director/Cloud Service Mesh and can coexist with `mtlsPolicy`, but it cannot coexist with `serverCertificate`. It is invalid as an Application Load Balancer downgrade and is useful only on an attached compatible policy.
- **Referenced address-group membership update:** `AddAddressGroupItems` requires `networksecurity.addressGroups.update`; updates automatically propagate to referencing Cloud NGFW and Cloud Armor rules. Create of an unreferenced group was rejected.
- **Intercept deployment injection:** `networksecurity.interceptDeployments.create` can add a producer appliance to an existing deployment group. This becomes a cross-project traffic-interception primitive only with an already connected consumer configuration and attacker control of a compatible same-network ILB and its backends.
- **Resource-level `setIamPolicy`:** supported on project address groups, authorization policies, authz policies, client TLS policies, and server TLS policies. The documented flow preserves version 3, conditions, and `etag`, and merges into an existing unconditional binding instead of creating a duplicate; impact remains scoped to the resource and requires a follow-on granted write.

### Corrected or rejected

- **TLS inspection is not a plaintext-capture API for the policy author.** `TlsInspectionPolicy` selects the CA pool that the Google-managed SWP/NGFW inspection path uses. Mutating it can disrupt or weaken inspection, but exposes no API or sink that returns decrypted payloads to the caller. It was removed from the privilege-escalation page. Its create/update/delete methods are `DATA_WRITE` Data Access events, disabled by default, not Admin Activity.
- **`ClientTlsPolicy` update does not reroute traffic.** It controls client-side TLS/SNI/trust for a global backend service and needs separate backend/routing control plus a suitable certificate/trust relationship for an impersonation chain. Removed as a standalone escalation primitive.
- **Gateway security policy/rule and URL-list changes** enable egress or weaken filtering but do not independently cross an authorization boundary in Google Cloud. Track as conditional post-exploitation/security-control tampering, not privilege escalation.
- **Security profile update, firewall endpoint detachment, and DNS threat-detector changes** are defense evasion or availability primitives unless followed by a separate exploit. Removed from this page.
- **Mirroring deployment injection** can copy packet data but does not grant privileges; it belongs in Network Security post-exploitation. The forwarding rule and deployment group references on both intercept and mirroring deployments are immutable, so `.update` cannot repoint an existing deployment to an attacker collector.
- **Backend authentication and client trust configuration** can support MITM only when combined with independent routing/backend and certificate control; not retained as standalone escalation.
- **Destructive `DENY` policies and resource deletion** were excluded as denial of service rather than escalation.

### Telemetry verified

- `CreateAuthzPolicy`, `UpdateAuthzPolicy`, `UpdateAuthorizationPolicy`, `UpdateServerTlsPolicy`, `AddAddressGroupItems`, `CreateInterceptDeployment`, and `SetIamPolicy` are Admin Activity / `ADMIN_WRITE` and always logged. The mutation methods except `SetIamPolicy` are LROs.
- Resource `Get*`, `GetIamPolicy`, and `google.longrunning.Operations.GetOperation` are Data Access / `ADMIN_READ`, disabled by default.
- Address-group project and organization calls use different method names: `AddressGroupService.AddAddressGroupItems` and `OrganizationAddressGroupService.AddAddressGroupItems`.
- Application Load Balancer request logs expose matching authorization-policy details only when backend-service logging is enabled; it is normally disabled and sampling applies. Firewall-policy connection/intercept logs require per-rule logging.
- Intercept deployment Admin Activity is written in the producer project; a different consumer project does not automatically receive that event.

### Independent cross-review corrections (2026-09-28)

- Removed a duplicate top-level `action` from the `AuthzPolicy` example and made the documented `CUSTOM` -> `DENY` -> `ALLOW` evaluation order explicit.
- Corrected the data-plane logging contract: Application Load Balancer entries use `jsonPayload.authzPolicyInfo`; Secure Web Proxy and Agent Gateway use `networkservices.googleapis.com/gateway_requests`.
- Removed unsupported `compute.regions.list` and `networksecurity.locations.list` helper-permission claims from address-group item updates. Current CLI source directly issues `AddAddressGroupItems` when location is explicit.
- Confirmed that Intercept Deployment create lists only `networksecurity.interceptDeployments.create`; the current API/CLI does not perform a separate forwarding-rule `.get` or `.use` check. Control or creation of the compatible ILB and backends remains a separate prerequisite.
- Bounded `allowOpen` to an attached Traffic Director-compatible policy without `serverCertificate` and hardened the IAM helper to preserve conditions/etag while merging members safely.
- The current audit catalog enumerates `GetIamPolicy` Data Access coverage for client/server TLS policy reads but not every other resource-level IAM target; the book's exact read row therefore describes the shown server TLS policy command rather than generalizing the catalog entry.

### Role observations

- Current predefined `roles/networksecurity.admin` and `roles/compute.networkAdmin` contain the relevant resource `setIamPolicy` permissions; `roles/networksecurity.editor` contains mutation and `getIamPolicy` but not `setIamPolicy`.
- The current live role definition for `roles/compute.securityAdmin` contains no `networksecurity.*` permissions, despite one address-group guide still naming that role. The book states exact permissions rather than repeating that inconsistent role claim.
