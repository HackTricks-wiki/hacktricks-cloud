# App Service Domains — Tests Done

Wiki: `az-app-services-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Reader / `domains/read` can retrieve a transfer-out EPP code | `Microsoft.DomainRegistration/domains/read` | **REFUTED 2026-09-26** — ARM requires hidden `domains/transferOut/write` |
| 2 | A wildcard custom role can match the hidden transfer-out operation | `Microsoft.DomainRegistration/domains/*` with published mutations excluded | **WORKS (authorization) / DOC-ONLY (real-domain response) 2026-09-26** |

**Lab record (2026-09-26 — safe nonexistent-domain authorization differential):** The subscription
started with `Microsoft.DomainRegistration` unregistered and contained no domain resources. Registered
the provider temporarily; created tagged RG `htrc-domainauth-26926`, UAMI `htrc-domain-mi-26926`, and a
no-ingress ACI running `probe-nonexistent-domain.sh`. The test name
`nonexistent-domain-26926.com` was only an Azure resource name; no domain was purchased or transferred.

Phase 1 assigned only `Microsoft.DomainRegistration/domains/read` at the test RG. The UAMI's ARM-token
results were:

- list domains: 200 with an empty list (positive token/scope/propagation control);
- get the nonexistent domain: provider 404;
- `PUT .../transferOut` with `Content-Length: 0`: ARM 403 naming the required action
  `Microsoft.DomainRegistration/domains/transferOut/write`;
- normal domain PUT: ARM 403 naming `domains/write`;
- renew: ARM 403 naming `domains/renew/action`.

The live provider catalog nevertheless has three duplicate `domains/Read` entries, one described as
“Transfer Out Domain.” The hidden action disclosed by ARM is not in that catalog. Creating a custom role
with exact `domains/transferOut/write` failed with `InvalidActionOrNotAction` because it matches no
published provider operation.

Phase 2 assigned `Microsoft.DomainRegistration/domains/*` but placed every published domain mutation in
`NotActions` (`write`, `delete`, renew/redeem/verification/contact actions, change-of-registrant delete,
and ownership-identifier writes/deletes). Results:

- `transferOut` reached the provider and returned the same 404 as GET for the nonexistent domain,
  proving that the wildcard matched the hidden action;
- ordinary domain PUT and renew remained 403, proving that the `NotActions` controls applied;
- official SDK/OpenAPI contracts state that the same PUT on a real domain returns the Domain model,
  whose `properties.authCode` is the EPP transfer credential. No real-domain call was made.

**Conclusion:** no Reader authorization bug and no MSRC report. This is an expected wildcard-permission
attack plus a provider-catalog blind spot useful for role review. The technique is public-book worthy
because transfer-code disclosure can enable registrar/domain takeover, while the misleading catalog can
cause defenders to miss it.

**Teardown:** removed both role assignments, both custom roles (the exact-action role never created),
ACI, UAMI, and RG. Final inventories showed no `26926` resource, custom role, or UAMI assignment. Because
the provider was initially unregistered and the subscription had zero domain resources, unregistered it
again and confirmed state `Unregistered`.
