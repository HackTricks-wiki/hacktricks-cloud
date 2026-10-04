# BeyondCorp / Chrome Enterprise Premium research log

## 2026-09-28 — documentation and local-source audit

No cloud resources or policies were created, updated, or deleted. The review used current official documentation, the current public REST and audit catalogs, installed `gcloud` help/source, and read-only predefined-role descriptions.

### Evidence checked

- Current private-web and SaaS Security Gateway setup guides, including client prerequisites, gateway `delegatingServiceAccount`, `roles/beyondcorp.upstreamAccess`, application/gateway access policies, VPC routing, DNS, and firewall boundaries.
- Current v1 REST schemas for `SecurityGateway`, `Application`, endpoint matchers, network/external upstreams, IAM methods, and LRO CRUD methods.
- Current Chrome Enterprise Premium IAM roles and live read-only role descriptions for Admin, Editor, Viewer, `sgApplicationUser`, `serviceDiscoveryUser`, and `upstreamAccess`. The official permission index also confirms current-resource `setIamPolicy` in BeyondCorp Admin, IAM Security Admin, `roles/admin`, and Owner, but not BeyondCorp Editor or basic Editor.
- Current service audit-method catalog, secure-gateway troubleshooting/access-log guide, connection-logging setup, and generic Cloud Audit Logs LRO behavior.
- Installed stable `gcloud beyondcorp security-gateways applications` create/update/IAM help and implementation. The add-binding helpers perform GetIamPolicy followed by SetIamPolicy and preserve the returned policy/etag.

### Retained boundaries

1. **Application IAM self-grant.** `beyondcorp.sgApplications.setIamPolicy` can add `roles/beyondcorp.sgApplicationUser`. Current service discovery also requires an existing gateway `serviceDiscoveryUser` binding or control of the gateway policy. This grants access only through a licensed/configured Chrome client and does not bypass upstream authentication.
2. **Repoint an application the caller can already use.** `beyondcorp.sgApplications.update` can change endpoint matchers while retaining the application's IAM policy. Direct privilege gain requires the caller already be a data-plane user and the target hostname already be reachable through the application's configured upstream/VPC.
3. **Configuration disclosure.** Current gateway/application reads disclose private web hostnames, VPC resource names, gateway identities, egress settings, authorized principals, and access conditions without touching upstream applications.
4. **Service-level persistence.** Durable gateway/application user bindings can outlive loss of the original configuration role, but not loss of the controlled Chrome identity/client setup or deletion of the resources.

### Corrected or rejected claims

- **Corrected:** Security Gateway protects SaaS and private web applications; it is not a generic arbitrary-TCP/DB/SSH tunnel. The endpoint matcher selects a hostname/port and the VPC upstream selects the network used to resolve/reach it.
- **Rejected:** `roles/beyondcorp.upstreamAccess` as an end-user accessor role. It is granted to the gateway's `delegatingServiceAccount` on the target VPC project.
- **Corrected:** current end-user access normally needs application-level `roles/beyondcorp.sgApplicationUser` and gateway-level `roles/beyondcorp.serviceDiscoveryUser`, plus Chrome Enterprise Premium licensing/client configuration. An application with no access policy denies access by default.
- **Rejected:** application IAM self-grant as equivalent to an unauthenticated IAP `allUsers` bypass. No official evidence shows anonymous secure-gateway use; the documented path authenticates a Chrome user and evaluates context.
- **Rejected:** publishing `169.254.169.254` as a generic metadata-SSRF path. The Compute metadata server is not an ordinary VPC-routable target, and Security Gateway documentation supports web application routing rather than arbitrary TCP proxying.
- **Rejected:** endpoint update as automatic credential/session interception. HTTPS certificate validation and upstream authentication remain; redirection can cause route tampering or denial of service, but credential capture additionally requires an accepted certificate/protocol/application condition.
- **Removed as low-value/destructive:** gateway/application deletion and `beyondcorp.subscriptions.terminate`. These are denial of service, not post-exploitation or privilege escalation.
- **Retired from active techniques:** regional App Connector creation. Google stopped new connector creation in May 2026 and documented support ending in July 2026. Old resources remain relevant only to legacy inventory.
- **Corrected CLI:** nested `--upstreams` requires `network=name=projects/.../global/networks/...`; external targets require the nested `external.endpoints[]` shape. The previous `external=host:port` and flat `network=...` examples did not match the current schema. This validates client-side serialization, not server-side mutability of an existing application's upstream.

### Telemetry findings

- `ListSecurityGateways`, `GetSecurityGateway`, `ListApplications`, and `GetApplication` are exact v1 `ADMIN_READ` Data Access methods, non-LRO, disabled by default.
- `CreateApplication`, `UpdateApplication`, and `DeleteApplication` are exact v1 `ADMIN_WRITE` Admin Activity LROs, logged by default. LROs normally have start and completion entries.
- The current generated service catalog's generic IAM methods enumerate legacy connector permissions but omit `securityGateways.{get,set}IamPolicy` and `sgApplications.{get,set}IamPolicy`. The REST methods and permissions are current, but exact emitted method/default visibility for those resources is an explicit capture gap. The book labels the expected classes rather than inventing an exact method.
- End-user authorization is available as Data Access with `resource.labels.method="AuthorizeUser"` after BeyondCorp Data Access logging is enabled.
- Connection logs use `resource.type="beyondcorp.googleapis.com/SecurityGateway"` only after gateway logging is enabled. Target-side web/load-balancer/WAF/authentication logs remain separate downstream signals.

## 2026-09-28 — independent reciprocal cross-review

- Rechecked the current private-web/SaaS guides, App Connector retirement notice, v1 REST and audit catalogs, live predefined-role descriptions, and installed stable CLI implementation without changing cloud state.
- Confirmed the documented `--upstreams=network=name=projects/.../global/networks/...` shorthand:
  local parser inspection produced the nested request object `{"network":{"name":"projects/.../global/networks/..."}}`. The endpoint matcher likewise produced a numeric port list. Current management guidance documents endpoint-matcher updates but not upstream replacement, so the active technique now keeps the existing upstream/VPC; accepting the CLI flag is not treated as proof that the backend accepts that update mask.
- Corrected the application-update helper boundary. Stable `gcloud ... applications update` first calls `GetApplication` to merge the selected fields, then calls `UpdateApplication`; synchronous use polls `GetOperation`. The helper therefore needs `beyondcorp.sgApplications.get`, `.update`, and `beyondcorp.operations.get`. A raw PATCH needs only `.update`, and `--async` avoids only the poll.
- Confirmed both add-binding implementations request IAM policy version 3 and send the returned policy object, including existing conditional bindings, version, and etag. Their documented `getIamPolicy` plus `setIamPolicy` minimum is correct.
- Found that the installed standalone GA/Beta declarative `get-iam-policy` commands omit `options.requestedPolicyVersion=3` (GA currently addresses the v1alpha endpoint; Beta addresses v1). Enumeration now uses the documented v1 REST GET with an explicit version-3 option so access conditions are returned instead of `_withcond_...` role hashes. This does not affect the custom add-binding helpers, which explicitly request version 3.
- Kept the route-update impact bounded to browser-mediated web access. Although the generic CLI schema accepts numeric ports, the current product guides document SaaS/private web applications and browser proxying; that is not evidence of a general SSH/database/arbitrary-TCP tunnel.
- Removed the active-page suggestion that the gateway discovery binding could be omitted for a legacy PAC configuration. The current official guides explicitly require the gateway-level `serviceDiscoveryUser` binding; any legacy exception remains an unverified research lead only.
- Confirmed the audit gap remains real as of the current generated catalog: current Security Gateway CRUD methods and their LRO classes are listed, while generic IAM method entries enumerate only legacy connector-resource permissions, not current `securityGateways`/`sgApplications` IAM permissions.
