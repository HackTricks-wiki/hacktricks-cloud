# Discovery Engine / Gemini Enterprise — open leads

- [ ] Live-test a periodic BigQuery connector with two synthetic principals: a source-table reader
  that creates the connector and a Gemini Enterprise app user explicitly denied direct BigQuery
  data access. Capture Discovery Engine, connector and BigQuery audit events, then delete the app,
  engine, connector, data stores, dataset and all IAM bindings.
- [ ] Compare one-time `aclEnabled=true` imports with periodic imports containing synthetic document
  ACL fields. Verify fail-closed behavior for malformed, absent and stale identity mappings.
- [ ] Test whether project-level `roles/discoveryengine.agentspaceUser` overrides intended app-level
  isolation exactly as documented, and determine which enumeration calls reveal otherwise hidden
  apps/data stores to a project-level user.
- [x] Closed `SearchLite` as a periodic-BigQuery lead from current documentation. Although
  `SearchLite` is listed among methods that produce no audit logs, Google documents its API-key path
  for **public website data**. Do not generalize that unauthenticated/public-site mechanism to a
  private periodic BigQuery corpus without contrary reproducible evidence.
