# Historical cross-project and cross-tenant vulnerabilities — research checklist

Use only owned or explicitly authorized tenants. Treat the named bulletins as patched; test for
variations in current surfaces, not reproduction against third-party tenants.

- [ ] For every create/import/attach API that accepts a project or tenant in the body, independently
  authorize the target parent and every cross-project identity reference. Vary project ID versus
  number, regional parent, alternate resource name and long-running-operation resume paths.
- [ ] For every managed service that retrieves a caller-selected secret, require both the calling
  principal and the runtime P4SA to access that exact secret/version. Repeat across source-control,
  connector and deployment products that share the same backend pattern.
- [ ] Fuzz managed JDBC/ODBC/connector configuration at the parser boundary: duplicate parameters,
  URL and property-map disagreement, nested drivers, alternate schemes and runtime-specific
  options. Keep payloads benign until authorization and isolation are proven.
- [ ] Confirm gateways strip or overwrite internal identity, role, tenant and authorization headers
  across HTTP/1.1, HTTP/2, WebSocket, duplicate/case variants and direct backend routes.
- [ ] Exercise cross-tenant resource identifiers in console-only/private aggregation endpoints with
  harmless objects and strict positive/negative controls; include numeric IDs, aliases, pagination
  tokens and cached responses.
- [ ] Probe sandbox reachability to link-local, metadata and service-agent endpoints with a harmless
  identity request only. Escalate no further unless the boundary failure is confirmed and privately
  documented.
- [ ] After deletion or migration of globally named destinations, verify the service binds to owner
  identity rather than name alone. Cover log sinks, staging/import buckets, Pub/Sub destinations and
  callback endpoints.
- [ ] Capture caller-side and managed-service audit events in every involved project. Explicitly
  distinguish absence under default logging from a method documented as not logged.
- [ ] Delete every disposable resource and verify absence by exact resource name before ending a
  live test.
