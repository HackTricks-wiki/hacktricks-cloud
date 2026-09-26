# Network Services (Service Extensions) — tested

## 2026-09-26 — full service-enumeration coverage

- Added `gcp-network-services-enum.md` covering mesh routes and endpoint policies, Service
  Extensions, the newer Agent Gateway/connectivity-template and extension-binding resources, and
  allowlist-gated Cloud Multicast.
- Validated current stable `gcloud network-services` and `gcloud service-extensions` list/describe
  groups and the v1/v1alpha1 discovery resource surface. The authorized lab project's Network
  Services API is disabled; read-only list requests returned `PERMISSION_DENIED`, so no API was
  enabled and no resource was created.
- Agent Gateway and multicast additions were recorded as inventory and research leads, not promoted
  into attacks without a distinct verified security impact.
- Rechecked the current predefined roles: both Network Services Editor and Admin now include
  `agentGateways.*` and `wasmPlugins.use`; only Admin adds `httpfilters.setIamPolicy`. Updated the
  role summary and added explicit stealth ratings to all six retained attack sections.

## `networkservices.authzExtensions.*` authorization-callout hijack — SHIPPED (gap found via ground-truth diff)

Found by the permission-surface diff: the existing Service Extensions technique in
`gcp-networkservices-privesc.md` covered `lbTrafficExtensions`/`lbRouteExtensions`/`wasmPlugins` only.
`authzExtensions`, `lbEdgeExtensions`, `swpSecurityExtensions` had ZERO wiki mention (grep-confirmed).

- `authzExtensions` = ext_authz decision callout on an ALB: per-request ALLOW/DENY from an
  attacker-nameable external service that also receives request headers. Distinct wins: auth bypass
  (always-ALLOW), per-request credential/context exfil, DoS (always-DENY).
- Perms `networkservices.authzExtensions.create/update/use` in `roles/networkservices.editor`/`admin`
  and `roles/editor`/`owner` (verified via role describe). Insertion/attach mechanism identical to the
  already-verified `lbTrafficExtensions` MITM; only callout semantics differ.
- NOT live-fired: a full ALB + ext_authz backend + traffic is disproportionate (multiple billable
  resources, slow teardown) and the attach mechanism is the verified one. Documented from the API/
  gcloud surface + shared mechanism — no false "verified end-to-end" claim in the page.
- Also noted `lbEdgeExtensions` (Media CDN edge) and `swpSecurityExtensions` (Secure Web Proxy) as
  sibling attach points.

**SHIPPED** → `gcp-networkservices-privesc.md` new section
"`networkservices.authzExtensions.*` — Service Extensions authorization-callout hijack".

## PSC producer-authz — FOLD note (2026-09-25)

`networkconnectivity.pscAuthorizationPolicies.create` / `serviceConnectionMaps.create`
(+`serviceClasses.use`) is a **parallel producer-side authz surface** to the already-documented
Private Service Connect service-attachment consumer-accept-list. Not a new primitive class: same
"widen reach / DoS via a different permission family" outcome, gated by `roles/networkconnectivity.admin`.
`AUTHORIZATION_MODE_TRANSITIVE_TO_SERVICE_ATTACHMENT` broadens which consumers connect. Admin Activity
logs the policy write; the data-plane connection itself is **not** audit-logged.
- Action: added as a **FOLD note bullet** to `gcp-vpc-and-networking.md` (after the DoS bullet, before
  the PSC role-map NOTE) rather than a standalone technique — it augments the existing PSC section.
- Not live-fired: producer service-attachment + consumer endpoint across projects is disproportionate;
  the authz-write mechanism is understood from the API surface.

## Multicloud data-transfer — REJECTED (2026-09-25)

Storage Transfer / BigQuery multicloud "transfer from another cloud" configs examined as a possible
exfil/confused-deputy lever. **REJECTED, not a real useful attack:** these are billing/ingest configs
that pull INTO the project (require the attacker to already control the source or its creds); no
outbound exfil primitive beyond the already-documented Storage Transfer confused-deputy. No ship.
