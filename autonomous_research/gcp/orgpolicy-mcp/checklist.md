# Organization Policy remote MCP — open leads

- [x] Map anonymous tool discovery and all 12 tool schemas.
- [x] Compare direct and MCP read behavior without modifying any policy.
- [x] Map read/write permissions, scope, impact, and wrapper-versus-underlying telemetry.
- [x] Distinguish policy target scope from the organization-only administrator-role grant point.
- [ ] In a dedicated disposable organization, exercise every create/update/delete tool with the
      minimum role at the correct scope, verify full-overwrite behavior, and remove every policy and
      custom constraint immediately afterward.
- [ ] In a dedicated hierarchy, compare explicit versus effective-policy visibility at project,
      folder, and organization scope with controlled inheritance fixtures.
- [ ] With MCP and Organization Policy Data Access logging explicitly enabled, capture exact
      wrapper and underlying read entries without changing a shared hierarchy's audit policy.
