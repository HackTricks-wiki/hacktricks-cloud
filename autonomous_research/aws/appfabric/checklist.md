# AppFabric — open ideas

- [x] GetAppAuthorization credential leak — DISPROVEN (input-only credential); see tested.md.
- [x] CreateIngestionDestination log-redirect exfil — VERIFIED authz; page created.
- [ ] **StartUserAccessTasks abuse** — triggers AppFabric to query a connected SaaS for the list of
  users who can access it (returns a task; results via BatchGetUserAccessTasks). Assess whether a
  low-priv principal can enumerate SaaS-tenant users (recon of the org's SaaS user base) with only
  `appfabric:StartUserAccessTasks` + `BatchGetUserAccessTasks`. Needs an existing app authorization.
- [ ] **UpdateAppAuthorization credential swap persistence** — replace a tenant's stored OAuth token
  with an attacker-issued one (if it accepts it) to keep AppFabric pulling under attacker control,
  or point it at attacker OAuth. Low confidence (likely validated against the SaaS); needs a real
  SaaS connection to test.
