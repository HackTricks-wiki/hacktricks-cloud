# Service Directory research log

## 2026-09-28 — official-contract audit

Scope was documentation, local Google Cloud CLI help, and public API/audit contracts only. No Service Directory, Cloud DNS, IAM, network, or other cloud resource was changed.

### Retained or reclassified

- Retained endpoint creation/update as one post-exploitation service-discovery poisoning primitive. The exact API permissions are `servicedirectory.endpoints.create` or `servicedirectory.endpoints.update`. A non-empty endpoint `network` also checks `servicedirectory.networks.attach` on the referenced network project; the network resource uses the project number.
- Bounded the effect: `ResolveService` returns a set and can filter/cap endpoints, so adding one endpoint does not force every client to use it. Updating an already selected endpoint is stronger. Reachability, TLS/mTLS, application authentication, VPC policy, and client logic remain prerequisites or controls.
- Corrected telemetry: `CreateEndpoint` and `UpdateEndpoint` are `DATA_WRITE` Data Access and off by default, not Admin Activity. `ResolveService` is `DATA_READ` Data Access and off by default. None is an LRO.
- Kept DNS integration conditional on an already-associated Service Directory private zone in the same project as the namespace. DNS visibility is network-based; Cloud DNS query logs are optional and cached answers may not log.
- Moved namespace/service `SetIamPolicy` to service-level persistence. It is always-on Admin Activity; `GetIamPolicy` is off-by-default Data Access. Public v1 IAM methods exist at namespace and service scope, not endpoint scope, despite endpoint IAM permission names in the role catalog.
- Expanded the enum page with exact list/resolve permissions and Data Access methods.

### Rejected or folded

- Removed namespace/service/endpoint deletion as destructive availability-only behavior.
- Removed the resource-IAM self-grant from post-exploitation; a durable service-level binding is persistence, not sensitive-data access.
- Folded service-annotation changes out of the main technique. They matter only when a particular client trusts attacker-controlled annotation keys and are not a general traffic-redirection guarantee.
- Rejected the claim that one rogue endpoint redirects every client. Endpoint selection is client-dependent.
- Rejected a new unauthenticated page: API resolution and control-plane operations require IAM; DNS visibility is intentionally network-scoped through a configured private zone, not unauthenticated internet exposure.
- Rejected endpoint-level IAM instructions because the public v1 endpoint REST collection has no `getIamPolicy` or `setIamPolicy` method.

### Primary evidence used

- Service Directory v1 REST/RPC resource and audit-logging catalogs.
- Current Service Directory access-control/role catalog.
- Current Service Directory configuration, private-network-access, DNS-zone, and Cloud DNS monitoring documentation.
- Local `gcloud service-directory` help.

### Live-test status

Not tested live. The task prohibited cloud mutation, and official method/permission/audit contracts were sufficient to correct the pages.

### Independent reciprocal review

Confirmed the endpoint network immutability/attach boundary, client-dependent endpoint selection, namespace/service IAM inheritance, command syntax, audit classes/defaults, and policy-preserving IAM helpers. Every telemetry statement now cites its official audit or downstream logging contract.
