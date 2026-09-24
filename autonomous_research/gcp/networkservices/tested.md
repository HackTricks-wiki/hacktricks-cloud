# Network Services (Service Extensions) — tested

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
