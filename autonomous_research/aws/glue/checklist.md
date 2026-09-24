# Glue — open ideas

Glue already has privesc + post-exploitation coverage (catalog/job code-exec, DataAccessRole
confused-deputy). Missing a dedicated **enum** page under `aws-services/`.

- [ ] **Enum page** — `GetDatabases`/`GetTables`/`GetConnections`/`GetJobs`/`GetDevEndpoints`:
  recon of data-catalog schema, JDBC `Connections` (which may embed credentials in
  `ConnectionProperties` — check `GetConnection --hide-password false` behavior), job script S3
  locations (`Command.ScriptLocation` → read the script from S3 for secrets/logic).
- [ ] **Connection password disclosure** — verify whether `GetConnection` returns the password or
  only metadata by default, and whether `glue:GetConnection` alone (no `PASSWORD` decrypt perm)
  leaks reusable DB creds. If it does, that's a clean recon/creds technique.
- [ ] **Catalog resource-policy** — `glue:PutResourcePolicy` cross-account catalog share already in
  the resource-policy matrix; confirm no separate enum-side exposure (e.g. Lake Formation hybrid).
